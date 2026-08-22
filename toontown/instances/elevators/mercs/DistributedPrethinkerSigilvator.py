from toontown.instances.elevators.mercs.DistributedInstanceMercSigilvator import DistributedInstanceMercSigilvator
from direct.actor.Actor import Actor
from toontown.building.ElevatorConstants import *
from otp import *
from panda3d.core import *
from direct.interval.IntervalGlobal import *

from toontown.toonbase import ToontownGlobals
from toontown.utils import Nodes
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget


@DirectNotifyCategory()
class DistributedPrethinkerSigilvator(DistributedInstanceMercSigilvator):
    CellarDoorPath = 'phase_3.5/models/schoolhouse/schoolhouse_exterior_door'

    BoardH = 90 - 18.069
    JumpOutH = BoardH + 90

    relativeClock = False
    clockPos = Vec3(46.438, 164.5, 9.51)
    clockHpr = Vec3(78.415, 0, 0)

    relativeCamera = False
    cameraPos = Vec3(65.17, 152.13, 7.9)
    cameraHpr = Vec3(48, -2.4, 0.0)

    OriginName = 'sigilvator_origin'

    @InjectorTarget
    def __init__(self, cr):
        DistributedInstanceMercSigilvator.__init__(self, cr)

        self.door = Actor(
            '%s-zero' % self.CellarDoorPath,
            {
                'open': '%s-open' % self.CellarDoorPath,
                'close': '%s-close' % self.CellarDoorPath,
            }
        )
        self.door.setBlend(frameBlend=base.wantSmoothAnims)
        self.door.setPos(46.12, 163.3, 3.0)
        self.door.setHpr(80, 0, 0)
        self.door.setScale(1.75, 1.55, 1.75)
        self.door.reparentTo(render)

        # Door collision
        cn = CollisionNode('PrethinkerDoorCollision')
        cs = CollisionCapsule(0, 0, 0, 0, 0, 20, 3)
        cn.addSolid(cs)
        cn.setCollideMask(ToontownGlobals.WallBitmask)
        self.collisionNode = self.door.attachNewNode(cn)

        # Door sounds
        self.doorOpenSfx = loader.loadSfx(
            'phase_3.5/audio/sfx/schoolhouse_exterior_door-open.ogg')
        self.doorCloseSfx = loader.loadSfx(
            'phase_3.5/audio/sfx/schoolhouse_exterior_door-close.ogg')

    def setupElevator(self, task=None):
        print('[Prethinker] setupElevator called')

        origin = render.find('**/%s' % self.OriginName)
        if origin.isEmpty():
            origin = render.attachNewNode(self.OriginName)
            origin.setPos(46.12, 163.3, 3.0)   # tune these
            origin.setHpr(80, 0, 0)
            print('[Prethinker] Created sigilvator_origin at', origin.getPos(render))

        print('[Prethinker] origin found?', not origin.isEmpty(), origin)

        return DistributedInstanceMercSigilvator.setupElevator(self, task)

    def disable(self):
        DistributedInstanceMercSigilvator.disable(self)
        if self.collisionNode:
            self.collisionNode.removeNode()
            self.collisionNode = None
        if self.door:
            self.door.cleanup()
            self.door = None
        if self.doorOpenSfx:
            self.doorOpenSfx.stop()
            self.doorOpenSfx = None
        if self.doorCloseSfx:
            self.doorCloseSfx.stop()
            self.doorCloseSfx = None

    def getPortInterval(self):
        ival = Parallel()
        for startIndex, avId in self.getIndexToAvIdDict().items():
            av = base.cr.doId2do.get(avId)
            if not av:
                continue
            moveSequence = Sequence()
            for sigilIndex in range(startIndex, -1, -1):
                moveSequence.append(self.makeSigilStepSequence(av=av, index=sigilIndex))
            ival.append(moveSequence)
            ival.append(Func(av.loop, 'walk'))
        return Sequence(
            Parallel(
                Func(self.doorCloseSfx.stop),
                Func(base.playSfx, self.doorOpenSfx, node=self.door),
                Func(self.door.play, 'open'),
                Wait(1.0),
            ),
            ival,
        )

    def makeSigilStepSequence(self, av, index):
        retParallel = Parallel()
        startNode = self.sigils[index]
        moveTime = 0.8

        if index == 0:
            endNode = self.door
            moveTime = 1.0
            retParallel.append(
                Sequence(
                    Wait(0.3),
                    LerpColorScaleInterval(
                        nodePath=av.getGeomNode(),
                        duration=0.5,
                        colorScale=(1, 1, 1, 0),
                    ),
                    Func(av.hide),
                    Func(av.getGeomNode().setColorScale, 1, 1, 1, 1),
                    Func(av.setH, 0),
                )
            )
        else:
            endNode = self.sigils[index - 1]

        retParallel.append(
            LerpPosInterval(
                nodePath=av,
                duration=moveTime,
                pos=endNode.getPos(render),
                startPos=startNode.getPos(render),
            ),
        )
        retParallel.append(
            LerpHprInterval(
                nodePath=av,
                duration=0.1,
                hpr=(Nodes.findHeadingBetweenNodes(startNode, endNode), 0, 0),
                blendType='easeOut',
            ),
        )
        return retParallel

    def onDoorCloseFinish(self):
        DistributedInstanceMercSigilvator.onDoorCloseFinish(self)
        self.door.play('close')
        self.doorOpenSfx.stop()
        base.playSfx(self.doorCloseSfx, node=self.door)

    def sigilPlacementFailed(self):
        taskMgr.doMethodLater(
            0.1, self.setupElevator, 'setupSigilvatorDelay', extraArgs=[])

    @property
    def closeTime(self):
        return 6.0