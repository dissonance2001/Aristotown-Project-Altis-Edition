from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.directnotify import DirectNotifyGlobal
from toontown.battle.BattleProps import globalPropPool
from toontown.battle import BattleParticles
from toontown.building.DistributedSigilvator import DistributedSigilvator


class DistributedHighRollerSigilvator(DistributedSigilvator):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedHighRollerSigilvator')

    def getInstanceId(self):
        from toontown.building import MajorPlayerInstanceGlobals
        return MajorPlayerInstanceGlobals.HIGH_ROLLER

    def __init__(self, cr):
        DistributedSigilvator.__init__(self, cr)
        self.stageLightSfx = loader.loadSfx(
            'phase_11/audio/sfx/LB_camera_shutter_2.ogg')
        self.particleSfx = loader.loadSfx(
            'phase_12/audio/sfx/SA_scabbard.ogg')
        self.teleportingToons = []

    def getPortInterval(self):
        toons = []
        toonHideSequence = Parallel()
        for avId in list(self.boardedAvIds.keys()):
            av = base.cr.doId2do.get(avId)
            if av:
                toons.append(av)
                toonHideSequence.append(
                    Sequence(Func(self.hideStageLight, av), Func(av.hide)))

        self.teleportingToons = toons[:]
        teleportTrack = Parallel()
        for index, toon in enumerate(toons):
            stageTrack = self.applyStageLight(toon, index * 0.2)
            stageTrack.append(Func(toon.loop, 'neutral'))
            teleportTrack.append(stageTrack)
            teleportTrack.append(self.applyParticles(toon))

        return Sequence(
            Parallel(
                SoundInterval(self.particleSfx, startTime=1.5,
                              duration=4.0, volume=0.7),
                teleportTrack,
                Sequence(
                    Wait(2.5),
                    Parallel(
                        SoundInterval(self.stageLightSfx, volume=0.7),
                        toonHideSequence))))

    def applyStageLight(self, target, delay):
        if not target:
            return Sequence()
        self.hideStageLight(target)
        stagelight = globalPropPool.getProp('stagelight')
        setattr(target, 'lobbyStagelight', stagelight)
        stagelight.hide()
        node = stagelight.node()
        node.setBounds(OmniBoundingVolume())
        node.setFinal(1)
        stagelight.find('**/stagelight').hide()
        stagelight.reparentTo(target)
        stagelight.setPos(0, 0, 30)
        stagelight.setScale(1, 1, 2)
        stagelight.setColorScaleOff(1)
        stagelight.setColor(Vec4(0.996, 0.992, 0.659, 0.28))
        target.setColorScale(1, 1, 1, 1)
        return Sequence(
            Wait(delay),
            Func(stagelight.show),
            SoundInterval(self.stageLightSfx, volume=0.7))

    def hideStageLight(self, target):
        if hasattr(target, 'lobbyStagelight'):
            target.lobbyStagelight.removeNode()
            del target.lobbyStagelight

    def applyParticles(self, target):
        particleNode = render.attachNewNode(
            'DistHighRollerSigilvator-particleNode-%s' % target.doId)
        particleNode.setPos(target.getPos(render))
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.loadParticleFile(
            'highRollerTeleporter.ptf')
        fadeTracks = [
            LerpColorScaleInterval(
                target, 1.0, (1, 1, 1, 0), blendType='easeIn')]
        if hasattr(target, 'nametag3d') and target.nametag3d:
            fadeTracks.append(
                LerpColorScaleInterval(
                    target.nametag3d, 1.0, (1, 1, 1, 0),
                    blendType='easeIn'))
        return Sequence(
            Parallel(
                ParticleInterval(
                    particleEffect, particleNode, worldRelative=0,
                    duration=4.0, cleanup=True, softStopT=-1.5,
                    renderParent=render),
                Sequence(
                    Wait(0.5),
                    Func(target.setTransparency, 1),
                    Parallel(*fadeTracks))),
            Func(particleNode.removeNode))


    def restoreTeleportTargets(self):
        for target in self.teleportingToons:
            self.hideStageLight(target)
            try:
                target.show()
                target.clearTransparency()
                target.clearColorScale()
            except:
                pass
            if hasattr(target, 'nametag3d') and target.nametag3d:
                try:
                    target.nametag3d.clearColorScale()
                except:
                    pass
        self.teleportingToons = []

    def disable(self):
        DistributedSigilvator.disable(self)
        self.restoreTeleportTargets()

    @property
    def closeTime(self):
        return 6.0

    def delete(self):
        self.restoreTeleportTargets()
        if self.stageLightSfx:
            self.stageLightSfx.stop()
            self.stageLightSfx = None
        if self.particleSfx:
            self.particleSfx.stop()
            self.particleSfx = None
        DistributedSigilvator.delete(self)
