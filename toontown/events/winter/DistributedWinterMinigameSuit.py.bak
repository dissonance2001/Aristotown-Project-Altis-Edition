from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM, State
from direct.interval.IntervalGlobal import Sequence, Parallel, ActorInterval, Wait, SoundInterval, ParticleInterval, Func, Track
from pandac.PandaModules import Point3

from toontown.battle import BattleParticles, MovieUtil
from toontown.suit import DistributedSuitBase
from toontown.toonbase import ToontownGlobals


class DistributedWinterMinigameSuit(DistributedSuitBase.DistributedSuitBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedWinterMinigameSuit')

    def __init__(self, cr):
        DistributedSuitBase.DistributedSuitBase.__init__(self, cr)
        self.flyTrack = None
        self.stealTrack = None
        self.explodeTrack = None
        self.exploding = False
        self.snowballHitPending = False
        self.fsm = ClassicFSM.ClassicFSM('DistributedWinterMinigameSuit', [
            State.State('Off', self.enterOff, self.exitOff, ['Neutral', 'Stealing', 'Explode']),
            State.State('Neutral', self.enterNeutral, self.exitNeutral, ['Stealing', 'Explode', 'Off']),
            State.State('Stealing', self.enterStealing, self.exitStealing, ['Neutral', 'Explode', 'Off']),
            State.State('Explode', self.enterExplode, self.exitExplode, ['Off'])
        ], 'Off', 'Off')
        self.fsm.enterInitialState()

    def generate(self):
        DistributedSuitBase.DistributedSuitBase.generate(self)

    def announceGenerate(self):
        DistributedSuitBase.DistributedSuitBase.announceGenerate(self)
        colNode = self.find('**/distAvatarCollNode*')
        if not colNode.isEmpty():
            colNode.setTag('pieCode', str(ToontownGlobals.PieCodeWinterMinigame))
            colNode.setTag('winterSuitId', str(self.doId))
        self.hideName()

    def disable(self):
        self._finishTracks()
        if self.fsm:
            self.fsm.request('Off')
        DistributedSuitBase.DistributedSuitBase.disable(self)

    def delete(self):
        self._finishTracks()
        if self.fsm:
            del self.fsm
            self.fsm = None
        DistributedSuitBase.DistributedSuitBase.delete(self)

    def request(self, state):
        if self.fsm:
            self.fsm.request(state)

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterNeutral(self):
        if not self.exploding:
            self.loop('neutral')

    def exitNeutral(self):
        pass

    def enterStealing(self):
        if self.exploding:
            return
        self.stealTrack = Sequence(
            ActorInterval(self, 'reach', startFrame=0, endFrame=50),
            ActorInterval(self, 'reach', startFrame=50, endFrame=0))
        self.stealTrack.loop()

    def exitStealing(self):
        if self.stealTrack:
            try:
                self.stealTrack.finish()
            except:
                pass
            self.stealTrack = None

    def explode(self):
        self.request('Explode')

    def enterExplode(self):
        if self.exploding:
            return
        self.exploding = True
        if self.flyTrack:
            try:
                self.flyTrack.finish()
            except:
                pass
            self.flyTrack = None
        if self.stealTrack:
            try:
                self.stealTrack.finish()
            except:
                pass
            self.stealTrack = None
        self.reparentTo(render)
        try:
            self.collNodePath.stash()
        except:
            pass
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
        try:
            deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        except:
            deathSound = spinningSound
        BattleParticles.loadParticles()
        smallGears = BattleParticles.createParticleEffect(file='gearExplosionSmall')
        singleGear = BattleParticles.createParticleEffect('GearExplosion', numParticles=1)
        smallGearExplosion = BattleParticles.createParticleEffect('GearExplosion', numParticles=10)
        bigGearExplosion = BattleParticles.createParticleEffect('BigGearExplosion', numParticles=30)
        for effect in (smallGears, singleGear, smallGearExplosion, bigGearExplosion):
            effect.setDepthWrite(False)
        explosionPoint = self.getPos(render) + Point3(0, 0, self.height / 2.0)
        kapowTrack = Sequence(Wait(5.4), MovieUtil.createKapowExplosionTrack(render, explosionPoint=explosionPoint))
        animTrack = Sequence(ActorInterval(self, 'lose', startFrame=0, endFrame=137), Func(self.hide))
        soundTrack = Sequence(Wait(0.6), SoundInterval(spinningSound, duration=1.2, startTime=1.5, volume=0.15, node=self),
                              SoundInterval(spinningSound, duration=3.0, startTime=0.6, volume=0.6, node=self),
                              SoundInterval(deathSound, volume=0.32, node=self))
        gears1Track = Sequence(Wait(2.0), ParticleInterval(smallGears, self, worldRelative=False, duration=4.3, cleanup=True))
        gears2Track = Track(
            (0.7, ParticleInterval(singleGear, self, worldRelative=False, duration=5.7, cleanup=True)),
            (5.2, ParticleInterval(smallGearExplosion, self, worldRelative=False, duration=1.2, cleanup=True)),
            (5.4, ParticleInterval(bigGearExplosion, self, worldRelative=False, duration=1.0, cleanup=True)))
        self.explodeTrack = Parallel(animTrack, soundTrack, kapowTrack, gears1Track, gears2Track)
        self.explodeTrack.start()

    def exitExplode(self):
        pass

    def flyIn(self, x, y, z):
        if self.exploding:
            return
        self.reparentTo(render)
        self.show()
        self.flyTrack = Sequence(
            self.beginSupaFlyMove(Point3(x, y, z), 1, 'fromSky', walkAfterLanding=False),
            Func(self._beginStealing))
        self.flyTrack.start()

    def _beginStealing(self):
        self.flyTrack = None
        if not self.exploding:
            self.request('Stealing')

    def _finishTracks(self):
        for name in ('flyTrack', 'stealTrack', 'explodeTrack'):
            track = getattr(self, name, None)
            if track:
                try:
                    track.finish()
                except:
                    pass
                setattr(self, name, None)
