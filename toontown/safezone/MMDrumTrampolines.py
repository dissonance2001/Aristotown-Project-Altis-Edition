from __future__ import absolute_import
from direct.interval.IntervalGlobal import Func, LerpScaleInterval, Sequence
from direct.showbase import DirectObject

import random
import time
from six.moves import range


class MMDrumTrampolines(DirectObject.DirectObject):
    ModelPath = 'phase_6/models/props/cc_m_ara_mml_prp_drum_trampoline'
    SfxPaths = [
        'phase_6/audio/sfx/cc_s_sfx_ara_mml_prp_drum_trampoline_%s.ogg' % index
        for index in range(1, 6)
    ]

    DrumPositions = (
        (-16.05, 44.75, -14.6),
        (39.5, 44.75, -14.6),
        (-16.05, -86.0, -14.6),
        (39.5, -86.0, -14.6),
    )

    DrumScale = 0.7
    JumpForce = 55.0
    IgnoreStepTimeInterval = 0.5

    def __init__(self):
        DirectObject.DirectObject.__init__(self)
        self.drums = []
        self.sfxList = []
        self.jumpSequences = {}
        self.lastSteppedTimestamps = {}

    def load(self):
        self.sfxList = [loader.loadSfx(path) for path in self.SfxPaths]

        for drumIndex, position in enumerate(self.DrumPositions):
            drum = loader.loadModel(self.ModelPath)
            if drum is None or drum.isEmpty():
                continue

            drum.setPos(*position)
            drum.setScale(self.DrumScale)
            drum.reparentTo(render)

            shadow = drum.find('**/trampoline_shadow')
            if not shadow.isEmpty():
                shadow.setZ(shadow.getZ() + 0.1)

            collision = drum.find('**/trampoline_coll_top')
            if not collision.isEmpty():
                collisionName = 'MMDrum-%s-CollisionTop' % drumIndex
                collision.setName(collisionName)
                self.accept(
                    'enter' + collisionName,
                    self._steppedOnTrampoline,
                    [drumIndex],
                )

            self.drums.append(drum)
            self.lastSteppedTimestamps[drumIndex] = 0.0

    def unload(self):
        self.ignoreAll()

        for sequence in self.jumpSequences.values():
            if sequence:
                sequence.finish()
        self.jumpSequences = {}

        for sfx in self.sfxList:
            if sfx:
                sfx.stop()
        self.sfxList = []

        for drum in self.drums:
            if drum and not drum.isEmpty():
                drum.removeNode()
        self.drums = []
        self.lastSteppedTimestamps = {}

    def _steppedOnTrampoline(self, drumIndex, collisionEntry=None):
        now = time.time()
        lastStepped = self.lastSteppedTimestamps.get(drumIndex, 0.0)
        if now <= lastStepped + self.IgnoreStepTimeInterval:
            return

        localAvatar = getattr(base, 'localAvatar', None)
        if localAvatar is None:
            return

        physControls = getattr(localAvatar, 'physControls', None)
        lifter = getattr(physControls, 'lifter', None)
        if physControls is None or lifter is None:
            return

        self.lastSteppedTimestamps[drumIndex] = now

        lifter.setVelocity(self.JumpForce)
        physControls.isAirborne = 1
        messenger.send('jumpStart')

        self._playJumpAnimation(drumIndex)

    def _playJumpAnimation(self, drumIndex):
        if drumIndex < 0 or drumIndex >= len(self.drums):
            return

        drum = self.drums[drumIndex]
        oldSequence = self.jumpSequences.get(drumIndex)
        if oldSequence:
            oldSequence.finish()

        sequenceParts = []
        if self.sfxList:
            sequenceParts.append(
                Func(base.playSfx, random.choice(self.sfxList), node=drum)
            )

        sequenceParts.extend((
            LerpScaleInterval(
                drum,
                0.11,
                self.DrumScale * 1.125,
                blendType='easeOut',
            ),
            LerpScaleInterval(
                drum,
                0.11,
                self.DrumScale,
                blendType='easeIn',
            ),
        ))

        sequence = Sequence(*sequenceParts)
        self.jumpSequences[drumIndex] = sequence
        sequence.start()
