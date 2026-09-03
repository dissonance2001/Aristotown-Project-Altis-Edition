from panda3d.core import *
from direct.interval.IntervalGlobal import *
from toontown.fishing import FishGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DirectRegion(NodePath):
    """
    DirectRegion(NodePath)

    :todo This should be separated out from this module and into toontown.gui because for some reason
    toontown.racing also imports this class...
    """

    def __init__(self, parent = aspect2d):
        NodePath.__init__(self)
        self.assign(parent.attachNewNode('DirectRegion'))

    def destroy(self):
        self.unload()

    def setBounds(self, *bounds):
        """
        :param bounds: floats: left, right, top, bottom
        """
        self.bounds = bounds

    def setColor(self, *colors):
        """
        :param colors: floats: red, green, blue, alpha
        """
        self.color = colors

    def show(self):
        pass

    def hide(self):
        pass

    def load(self):
        if not hasattr(self, 'cRender'):
            # Create a separate reality for the fish to swim in:
            self.cRender = NodePath('fishSwimRender')
            # It gets its own camera
            self.fishSwimCamera = self.cRender.attachNewNode('fishSwimCamera')
            self.cCamNode = Camera('fishSwimCam')
            self.cLens = PerspectiveLens()
            self.cLens.setFov(40, 40)
            self.cLens.setNear(0.1)
            self.cLens.setFar(100.0)
            self.cCamNode.setLens(self.cLens)
            self.cCamNode.setScene(self.cRender)
            self.fishSwimCam = self.fishSwimCamera.attachNewNode(self.cCamNode)

            cm = CardMaker('displayRegionCard')

            cm.setFrame(*self.bounds)

            self.card = card = self.attachNewNode(cm.generate())
            card.setColor(*self.color)

            newBounds = card.getTightBounds()
            ll = render2d.getRelativePoint(card, newBounds[0])
            ur = render2d.getRelativePoint(card, newBounds[1])
            newBounds = [ll.getX(), ur.getX(), ll.getZ(), ur.getZ()]
            # scale the -1.0..2.0 range to 0.0..1.0:
            newBounds = [max(0.0, min(1.0, (x + 1.0) / 2.0)) for x in newBounds]

            self.cDr = base.win.makeDisplayRegion(*newBounds)
            self.cDr.setSort(10)
            self.cDr.setClearColor(card.getColor())
            self.cDr.setClearDepthActive(1)
            self.cDr.setClearColorActive(1)
            self.cDr.setCamera(self.fishSwimCam)
        return self.cRender

    def unload(self):
        if hasattr(self, 'cRender'):
            base.win.removeDisplayRegion(self.cDr)
            del self.cRender
            del self.fishSwimCamera
            del self.cCamNode
            del self.cLens
            del self.fishSwimCam
            del self.cDr


@DirectNotifyCategory()
class FishPhoto(NodePath):
    """
    FishPhoto(NodePath)
    """

    # special methods
    def __init__(self, fish = None, parent = aspect2d):
        """
        :param fish: None
        :param parent: aspect2d
        """
        NodePath.__init__(self)
        self.assign(parent.attachNewNode('FishPhoto'))
        self.fish = fish
        self.actor = None
        self.sound = None
        self.soundTrack = None
        self.track = None
        self.fishFrame = None
        return

    def destroy(self):
        self.hide()
        if hasattr(self, 'background'):
            del self.background
        self.fish = None
        del self.soundTrack
        del self.track
        return

    def update(self, fish):
        self.fish = fish

    def setSwimBounds(self, *bounds):
        """
        :param bounds: floats: left, right, top, bottom
        """
        self.swimBounds = bounds

    def setSwimColor(self, *colors):
        """
        :param colors: floats: red, green, blue, alpha
        """
        self.swimColor = colors

    def load(self):
        pass

    def makeFishFrame(self, actor):
        # NOTE: this may need to go in FishBase eventually
        actor.setDepthTest(1)
        actor.setDepthWrite(1)

        # scale the actor to the frame
        if not hasattr(self, 'fishDisplayRegion'):
            self.fishDisplayRegion = DirectRegion(parent=self)
            self.fishDisplayRegion.setBounds(*self.swimBounds)
            self.fishDisplayRegion.setColor(*VBase4(1, 1, 1, 1))

        frame = self.fishDisplayRegion.load()
        pitch = frame.attachNewNode('pitch')
        rotate = pitch.attachNewNode('rotate')
        scale = rotate.attachNewNode('scale')
        actor.reparentTo(scale)

        # Translate actor to the center.
        bMin, bMax = actor.getTightBounds()
        center = (bMin + bMax) / 2.0
        actor.setPos(-center[0], -center[1], -center[2])
        genus = self.fish.getGenus()
        fishInfo = FishGlobals.FishFileDict.get(genus, FishGlobals.FishFileDict[-1])

        fishPos = fishInfo[5]
        if fishPos:
            actor.setPos(fishPos[0], fishPos[1], fishPos[2])
        scale.setScale(fishInfo[6])
        rotate.setH(fishInfo[7])
        pitch.setP(fishInfo[8])
        pitch.setY(2)

        return frame

    def show(self, showBackground = 0):
        # if we are browsing fish we must be awake
        messenger.send('wakeup')
        if self.fishFrame:
            self.actor.cleanup()
            if hasattr(self, 'fishDisplayRegion'):
                self.fishDisplayRegion.unload()
            self.hide()
        self.actor = self.fish.getActor()
        self.actor.setTwoSided(1)
        self.fishFrame = self.makeFishFrame(self.actor)

        if showBackground:
            if not hasattr(self, 'background'):
                background = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
                background = background.find('**/Fish_BG')
                self.background = background
            self.background.setPos(0, 15, 0)
            self.background.setScale(11)
            self.background.reparentTo(self.fishFrame)
        self.sound, loop, delay, playRate = self.fish.getSound()
        if playRate is not None:
            # make a track to play the anim and sound
            self.actor.setPlayRate(playRate, 'intro')
            self.actor.setPlayRate(playRate, 'swim')
        introDuration = self.actor.getDuration('intro')
        track = Parallel(
            Sequence(
                Func(self.actor.play, 'intro'),
                Wait(introDuration),
                Func(self.actor.loop, 'swim')
            )
        )

        # if we have a sound, make a track to loop it
        if self.sound:
            soundTrack = Sequence(Wait(delay), Func(self.sound.play))
            if loop:
                duration = max(introDuration, self.sound.length())
                soundTrack.append(Wait(duration - delay))
                track.append(Func(soundTrack.loop))
                self.soundTrack = soundTrack
            else:
                track.append(soundTrack)

        self.track = track
        self.track.start()
        return

    def hide(self):
        if hasattr(self, 'fishDisplayRegion'):
            self.fishDisplayRegion.unload()
        if self.actor:
            self.actor.stop()
        if self.sound:
            self.sound.stop()
            self.sound = None
        if self.soundTrack:
            self.soundTrack.pause()
            self.soundTrack = None
        if self.track:
            self.track.pause()
            self.track = None
        return
