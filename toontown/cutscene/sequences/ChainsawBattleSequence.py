from __future__ import absolute_import
from toontown.cutscene.editor.CSEditorEnums import EventDefinitionEnum as EDE
from toontown.cutscene.CutsceneSequenceBase import cutsceneSequence, getUniqueCutsceneId
from toontown.cutscene.CutsceneSequenceHelpers import NodePathWithState
from direct.interval.IntervalGlobal import Func, LerpFunctionInterval, LerpHprInterval, LerpPosHprInterval, LerpPosInterval, Parallel, Sequence, SoundInterval, Wait
from panda3d.core import Point3, Vec3, NodePath


@cutsceneSequence(name='Cannon: Fake Control', enum=EDE.fakeCannonControl)
def seq_fakeCannonControl(nodeIndex=0, delay=0, posOffset=(0, 0, 0),
                          startHpr=(0, 0, 0), hpr=(0, 0, 0),
                          awakenTime=2.0, adjustTime=0.6, holdTime=2.0,
                          cogCannon=True, cutsceneDict=None):
    nodes = cutsceneDict.get('nodes', ())
    if nodeIndex < 0 or nodeIndex >= len(nodes):
        return Sequence()
    point = nodes[nodeIndex]
    if point is None:
        return Sequence()
    try:
        if point.isEmpty():
            return Sequence()
    except:
        pass

    if cogCannon:
        cannon = loader.loadModel('phase_5/models/props/cannon_cog')
    else:
        cannon = loader.loadModel('phase_4/models/minigames/toon_cannon')
    barrel = NodePathWithState(cannon.find('**/cannon'))
    referenceNode = render.attachNewNode('referenceNode-Cannon')
    referenceNode.hide()
    cannonHolder = NodePathWithState('CannonHolder')
    cannonHolder.reparentTo(referenceNode)
    cannon.reparentTo(cannonHolder)
    cannonAttachPoint = barrel.attachNewNode('CannonAttach')
    scaleFactor = 1.6
    barrel.setScale(scaleFactor, 1, scaleFactor)

    soundAdjust = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_adjust.ogg')
    playAdjust = SoundInterval(soundAdjust, duration=adjustTime, node=cannonHolder)

    def setupCannon():
        cannon.setPos(0, 0, -8.6)
        cannonHolder.setH(0)
        barrel.setHpr(0, 90, 0)
        referenceNode.setPos(point.getPos(render))
        referenceNode.setHpr(point.getHpr(render))
        cannonAttachPoint.setScale(1.0 / scaleFactor, 1, 1.0 / scaleFactor)
        cannonAttachPoint.setPos(0, 6.7, 0)

    eventId = getUniqueCutsceneId()
    holderAttr = 'turnToPoint-%s' % eventId
    barrelAttr = 'turnToPoint-%s' % eventId

    def updateStartHpr():
        setattr(cannonHolder, holderAttr, cannonHolder.getH())
        setattr(barrel, barrelAttr, barrel.getP())

    def updateHpr(t):
        endH, endP, unused = hpr
        endH -= referenceNode.getH()
        h1 = getattr(cannonHolder, holderAttr, cannonHolder.getH())
        p1 = getattr(barrel, barrelAttr, barrel.getP())
        cannonHolder.setH(((endH - h1) * t) + h1)
        barrel.setP(((endP - p1) * t) + p1)

    rotateTrack = Sequence(
        Func(updateStartHpr),
        LerpFunctionInterval(updateHpr, duration=adjustTime, blendType='easeIn'))

    react = Parallel(
        Func(setupCannon),
        Func(referenceNode.show),
        Sequence(
            LerpPosHprInterval(
                cannonHolder, awakenTime,
                Point3(0, 0, 7) + Point3(*posOffset), Vec3(*startHpr),
                startPos=Point3(*posOffset), blendType='easeInOut'),
            Parallel(rotateTrack, playAdjust),
            Wait(holdTime),
            Parallel(
                LerpHprInterval(barrel, adjustTime, Point3(0, 90, 0), blendType='easeOut'),
                playAdjust),
            LerpPosInterval(cannonHolder, 1.0, Point3(*posOffset), blendType='easeInOut')))

    def cleanup():
        for node in (referenceNode, cannonHolder, cannon, barrel, cannonAttachPoint):
            try:
                if isinstance(node, NodePath) and not node.isEmpty():
                    node.removeNode()
            except:
                pass

    return Sequence(Wait(delay), react, Func(cleanup))
