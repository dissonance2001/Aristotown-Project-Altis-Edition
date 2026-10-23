import random
import re
from toontown.toonbase.ToonBaseGlobal import *
from pandac.PandaModules import *
from toontown.toonbase.ToontownGlobals import *
from direct.distributed import DistributedObject
from direct.distributed.ClockDelta import globalClockDelta
from toontown.toonbase import ToontownGlobals
from direct.task.Task import Task
from toontown.building.DistributedAnimatedProp import DistributedAnimatedProp
from toontown.building.interior.PacesetterTVPlayer import PacesetterTVPlayer
from direct.directnotify import DirectNotifyGlobal
from toontown.building import ToonInteriorColors
from toontown.building import DistributedToonInterior
from toontown.dna.DNAParser import DNADoor
from toontown.hood import ZoneUtil
from toontown.toon.DistributedNPCToonBase import DistributedNPCToonBase
from toontown.building.interior.props.LavaLamp import LavaLamp


class DistributedPaceLobbyInterior(DistributedToonInterior.DistributedToonInterior):

    def __init__(self, cr):
        DistributedToonInterior.DistributedToonInterior.__init__(self, cr)
        self.dnaStore = cr.playGame.dnaStore
        self.bellSound = None
        self.bellInside = False
        self.bellPosition = Point3(-29.851, 26.147, 4.043)
        self.bellEnterRadius = 2.0
        self.bellExitRadius = 2.75
        self.bellTaskName = 'paceLobbyBellTask-%s' % id(self)
        self.showerSound = None
        self.showerInside = False
        self.showerTaskName = 'paceLobbyShowerTask-%s' % id(self)
        self.positionPrinterEvent = 'f9'
        self.motoroomSigilvatorOrigin = None
        self.tv = None
        self.tvClick = None
        self.tvPlayer = None
        self.tvController = None
        self.tvControllerState = None
        self.tvControllerVideoUrl = None
        self.tvVideoTimestamp = None
        self.tvControllerTaskName = 'pacesetter-tv-controller-%s' % id(self)
        self.paceMusicRestoreTaskName = 'pace-lobby-music-restore-%s' % id(self)
        self.paceMusicPositionTaskName = 'pace-lobby-music-position-%s' % id(self)
        self.paceLobbyMusicTime = 0.0
        self.tvClickTraverser = None
        self.tvClickQueue = None
        self.tvClickRay = None
        self.tvClickRayNP = None

    def generate(self):
        DistributedToonInterior.DistributedToonInterior.generate(self)

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        self.setup()
        taskMgr.doMethodLater(0.1, self.doMusic, 'pacelobbyMusic')
        taskMgr.add(self.checkBell, self.bellTaskName)
        taskMgr.add(self.checkShower, self.showerTaskName)
        self.accept(self.positionPrinterEvent, self.printPaceLobbyPosition)
        print('[Pace Lobby Position] Press F9 to print your Toon position.')

    def printPaceLobbyPosition(self):
        if not hasattr(base, 'localAvatar') or not base.localAvatar:
            return
        pos = base.localAvatar.getPos(render)
        hpr = base.localAvatar.getHpr(render)
        print(('[Pace Lobby Position] (%.3f, %.3f, %.3f, %.3f)' %
              (pos.getX(), pos.getY(), pos.getZ(), hpr.getX())))

    def doMusic(self, task):
        if self.tvPlayer and getattr(self.tvPlayer, 'musicPaused', False):
            return task.done
        base.musicManager.stopAllSounds()
        self.pacelobbyMusicFile = loader.loadMusic('phase_9/audio/bgm/merc/instance_pacesetter_lobby.ogg')
        self.paceLobbyMusicTime = 0.0
        self.pacelobbyMusic = self.pacelobbyMusicFile
        base.playMusic(self.pacelobbyMusicFile, looping=1)
        taskMgr.remove(self.paceMusicPositionTaskName)
        taskMgr.doMethodLater(0.25, self._trackPaceLobbyMusicPosition, self.paceMusicPositionTaskName)
        return task.done

    def checkBell(self, task):
        if not hasattr(base, 'localAvatar') or not base.localAvatar:
            return task.cont

        toonPos = base.localAvatar.getPos(render)
        distanceSquared = (toonPos - self.bellPosition).lengthSquared()
        enterDistanceSquared = self.bellEnterRadius * self.bellEnterRadius
        exitDistanceSquared = self.bellExitRadius * self.bellExitRadius

        if self.bellInside:
            if distanceSquared >= exitDistanceSquared:
                self.bellInside = False
        elif distanceSquared <= enterDistanceSquared:
            self.bellInside = True
            if self.bellSound:
                self.bellSound.stop()
                self.bellSound.play()

        return task.cont

    def checkShower(self, task):
        if not hasattr(base, 'localAvatar') or not base.localAvatar:
            return task.cont

        pos = base.localAvatar.getPos(render)

        inside = (-6.5 <= pos.getX() <= 6.3 and
                  57.8 <= pos.getY() <= 60.2)

        if self.showerInside:
            if not inside:
                self.showerInside = False
        elif inside:
            self.showerInside = True
            if self.showerSound:
                self.showerSound.stop()
                self.showerSound.play()

        return task.cont

    def setZoneIdAndBlock(self, zoneId, block):
        self.zoneId = zoneId
        self.block = block

    def chooseDoor(self):
        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'
        door = self.dnaStore.findNode(doorModelName)
        return door

    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.interior = loader.loadModel('phase_8/models/areas/ttcc_int_psetter_lobby.bam')
        self.interior.reparentTo(render)
        self.bellSound = loader.loadSfx('phase_5/audio/sfx/ttcc_int_psetter_bell.ogg')
        self.showerSound = loader.loadSfx('phase_4/audio/sfx/MG_sfx_travel_game_bonus.ogg')
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        door = self.chooseDoor()
        doorOrigin = render.find('**/door_origin;+s')
        doorNP = door.copyTo(doorOrigin)
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.025, 0)
        doorColor = self.randomGenerator.choice(self.colors['TI_door'])
        DNADoor.setupDoor(doorNP, self.interior, doorOrigin, self.dnaStore, str(self.block), doorColor)
        doorFrame = doorNP.find('door_*_flat')
        doorFrame.wrtReparentTo(self.interior)
        del self.colors
        del self.dnaStore
        del self.randomGenerator
        self.lavaLamps = []
        lampData = [
            ((26.119, 16.110, 2.477), 0, 0),
            ((28.545, 87.109, -8.553), 1, 0),
            ((19.204, 96.448, -8.553), 2, 0),
            ((8.375, 79.841, -8.552), 3, 0),
            ((-7.447, 73.204, -8.552), 4, 0)
        ]
        for pos, colorIndex, h in lampData:
            lamp = LavaLamp(colorIndex)
            lamp.reparentTo(self.interior)
            lamp.setPos(pos)
            lamp.setH(h)
            self.lavaLamps.append(lamp)
        self.interior.flattenMedium()
        self._setupTV()
        self.motoroomSigilvatorOrigin = self.interior.attachNewNode(
            'major_player_sigilvator_origin_2')
        self.motoroomSigilvatorOrigin.setPos(
            render, -17.100, 91.284, -11.014)
        self.motoroomSigilvatorOrigin.setHpr(
            render, 91.530, 0, 0)
        for npcToon in self.cr.doFindAllInstances(DistributedNPCToonBase):
            npcToon.initToonState()

    def _setupTV(self):
        tv = loader.loadModel('props/general/models/cc_a_gen_prp_tv.bam')
        if tv.isEmpty():
            return
        tv.reparentTo(self.interior)
        tv.setScale(4)
        tv.setPos(-23.472, 36.342, 4.043)
        tv.setH(68.632)
        for geom in tv.findAllMatches('**/+GeomNode'):
            for stage in geom.findAllTextureStages():
                for texture in geom.findAllTextures(stage):
                    textureName = texture.getName().split('/')[-1]
                    textureName = re.sub(r'\.\d+$', '', textureName)
                    try:
                        replacement = loader.loadTexture('props/general/maps/' + textureName + '.png')
                        if replacement and replacement.getXSize() > 0:
                            geom.setTexture(stage, replacement, 100)
                    except Exception:
                        pass

        tvMin = Point3()
        tvMax = Point3()
        if not tv.calcTightBounds(tvMin, tvMax, tv):
            tvMin = Point3(-0.4, -0.35, 0.25)
            tvMax = Point3(0.2, 0.1, 0.95)

        wallCollision = CollisionNode('Pacesetter-TV-Collision')
        wallCollision.addSolid(CollisionBox(tvMin, tvMax))
        wallCollision.setIntoCollideMask(WallBitmask)
        wallCollision.setFromCollideMask(BitMask32.allOff())
        tv.attachNewNode(wallCollision)

        clickNode = CollisionNode('Pacesetter-TV-Click')
        clickNode.addSolid(CollisionBox(tvMin, tvMax))
        clickNode.setIntoCollideMask(BitMask32.bit(30))
        clickNode.setFromCollideMask(BitMask32.allOff())
        self.tvClick = tv.attachNewNode(clickNode)

        self.tv = tv
        self.tvPlayer = PacesetterTVPlayer(
            tv,
            self._getTVOffset,
            self.tvController,
            self._pauseTVMusic,
            self._resumeTVMusic,
        )
        self.tvClickTraverser = CollisionTraverser('Pacesetter-TV-Click-Traverser')
        self.tvClickQueue = CollisionHandlerQueue()
        self.tvClickRay = CollisionRay()
        rayNode = CollisionNode('Pacesetter-TV-Click-Ray')
        rayNode.addSolid(self.tvClickRay)
        rayNode.setFromCollideMask(BitMask32.bit(30))
        rayNode.setIntoCollideMask(BitMask32.allOff())
        self.tvClickRayNP = base.camera.attachNewNode(rayNode)
        self.tvClickTraverser.addCollider(self.tvClickRayNP, self.tvClickQueue)
        self.accept('mouse1', self._handleTVClick)
        self.accept('window-event', self._handlePaceLobbyWindowEvent)
        taskMgr.add(self._findTVController, self.tvControllerTaskName)

    def _findTVController(self, task):
        if self.tvController is None:
            for obj in self.cr.doId2do.values():
                if isinstance(obj, DistributedAnimatedProp) and getattr(obj, 'propId', None) == ToontownGlobals.PacesetterLobby:
                    self.tvController = obj
                    if self.tvPlayer:
                        self.tvPlayer.setController(obj)
                    break

        if not self.tvController or not self.tvPlayer:
            return task.cont

        videoUrl = getattr(self.tvController, 'videoUrl', '')
        videoTimestamp = getattr(self.tvController, 'videoTimestamp', 0)
        previousVideoUrl = self.tvControllerVideoUrl
        previousVideoTimestamp = self.tvVideoTimestamp
        if videoUrl and videoUrl != self.tvPlayer.youtubeUrl:
            self.tvPlayer.setURL(videoUrl)
        if (previousVideoTimestamp is not None and videoTimestamp and
                videoTimestamp != previousVideoTimestamp and
                videoUrl and videoUrl == previousVideoUrl == self.tvPlayer.youtubeUrl and
                self.tvPlayer.movie and self.tvPlayer.sound):
            self.tvPlayer.seekToOffset(globalClockDelta.localElapsedTime(videoTimestamp))
        self.tvControllerVideoUrl = videoUrl
        self.tvVideoTimestamp = videoTimestamp
        try:
            stateName = self.tvController.fsm.getCurrentState().getName()
        except Exception:
            stateName = 'off'
        if stateName != self.tvControllerState:
            self.tvControllerState = stateName
            if stateName == 'playing':
                self.tvPlayer.play()
            else:
                self.tvPlayer.stop()
        return task.cont

    def _getTVOffset(self):
        if not self.tvController:
            return 0.0
        timestamp = getattr(self.tvController, 'videoTimestamp', 0)
        return globalClockDelta.localElapsedTime(timestamp) if timestamp else 0.0

    def _handleTVClick(self):
        panel = getattr(self.tvPlayer, 'controlPanel', None) if self.tvPlayer else None
        if panel and not panel.isHidden():
            return
        if not base.mouseWatcherNode.hasMouse() or not self.tvClickTraverser:
            return
        mousePos = base.mouseWatcherNode.getMouse()
        self.tvClickRay.setFromLens(base.camNode, mousePos.getX(), mousePos.getY())
        self.tvClickQueue.clearEntries()
        self.tvClickTraverser.traverse(render)
        if self.tvClickQueue.getNumEntries():
            self.tvClickQueue.sortEntries()
            hit = self.tvClickQueue.getEntry(0).getIntoNodePath().getName() == 'Pacesetter-TV-Click'
            if hit and self.tvPlayer:
                self.tvPlayer.openBrowser()

    def _pauseTVMusic(self):
        self._savePaceLobbyMusicTime()
        music = getattr(self, 'pacelobbyMusic', None)
        if music:
            music.stop()
        elif getattr(base, 'musicManager', None):
            base.musicManager.stopAllSounds()

    def _resumeTVMusic(self):
        if not getattr(self, 'pacelobbyMusicFile', None):
            self.pacelobbyMusicFile = loader.loadMusic('phase_9/audio/bgm/merc/instance_pacesetter_lobby.ogg')
        self.pacelobbyMusic = self.pacelobbyMusicFile
        base.playMusic(
            self.pacelobbyMusicFile,
            looping=1,
            time=max(0.0, self.paceLobbyMusicTime),
        )
        taskMgr.remove(self.paceMusicPositionTaskName)
        taskMgr.doMethodLater(0.25, self._trackPaceLobbyMusicPosition, self.paceMusicPositionTaskName)

    def _handlePaceLobbyWindowEvent(self, window=None):
        if window is None:
            window = getattr(base, 'win', None)
        if not window:
            return
        try:
            foreground = window.getProperties().getForeground()
        except (AttributeError, TypeError):
            return
        if not foreground:
            self._savePaceLobbyMusicTime()
            taskMgr.remove(self.paceMusicRestoreTaskName)
            return
        taskMgr.remove(self.paceMusicRestoreTaskName)
        taskMgr.doMethodLater(0.25, self._restorePaceLobbyMusic, self.paceMusicRestoreTaskName)

    def _restorePaceLobbyMusic(self, task):
        if self.tvPlayer and getattr(self.tvPlayer, 'musicPaused', False):
            return task.done
        music = getattr(self, 'pacelobbyMusic', None)
        if music:
            try:
                status = music.status()
                current_time = max(0.0, float(music.getTime()))
            except (AttributeError, TypeError, ValueError):
                status = None
                current_time = None
            if status == music.PLAYING:
                if current_time is None or current_time >= self.paceLobbyMusicTime - 1.5:
                    if current_time is not None:
                        self.paceLobbyMusicTime = max(self.paceLobbyMusicTime, current_time)
                    return task.done
                try:
                    music.stop()
                except Exception:
                    pass
        if getattr(self, 'pacelobbyMusicFile', None):
            self.pacelobbyMusic = self.pacelobbyMusicFile
            base.playMusic(
                self.pacelobbyMusicFile,
                looping=1,
                time=max(0.0, self.paceLobbyMusicTime),
            )
            taskMgr.remove(self.paceMusicPositionTaskName)
            taskMgr.doMethodLater(0.25, self._trackPaceLobbyMusicPosition, self.paceMusicPositionTaskName)
        return task.done

    def _savePaceLobbyMusicTime(self):
        music = getattr(self, 'pacelobbyMusic', None)
        if not music:
            return
        try:
            if music.status() != music.PLAYING:
                return
            current_time = max(0.0, float(music.getTime()))
            saved_time = getattr(self, 'paceLobbyMusicTime', 0.0)
            if current_time + 1.5 >= saved_time:
                self.paceLobbyMusicTime = current_time
        except (AttributeError, TypeError, ValueError):
            pass

    def _trackPaceLobbyMusicPosition(self, task):
        if not (self.tvPlayer and getattr(self.tvPlayer, 'musicPaused', False)):
            window = getattr(base, 'win', None)
            try:
                foreground = window.getProperties().getForeground() if window else True
            except (AttributeError, TypeError):
                foreground = True
            if foreground:
                music = getattr(self, 'pacelobbyMusic', None)
                if music:
                    try:
                        if music.status() == music.PLAYING:
                            self.paceLobbyMusicTime = max(0.0, float(music.getTime()))
                    except (AttributeError, TypeError, ValueError):
                        pass
        return task.again

    def _cleanupTV(self):
        taskMgr.remove(self.tvControllerTaskName)
        taskMgr.remove(self.paceMusicRestoreTaskName)
        self.ignore('mouse1')
        self.ignore('window-event')
        if self.tvPlayer:
            self.tvPlayer.destroy()
            self.tvPlayer = None
        if self.tvClickTraverser and self.tvClickRayNP:
            try:
                self.tvClickTraverser.removeCollider(self.tvClickRayNP)
            except Exception:
                pass
        self.tvClickTraverser = None
        self.tvClickQueue = None
        self.tvClickRay = None
        if self.tvClickRayNP:
            self.tvClickRayNP.removeNode()
            self.tvClickRayNP = None
        if self.tv:
            self.tv.removeNode()
            self.tv = None
        self.tvClick = None
        self.tvController = None
        self.tvControllerState = None
        self.tvControllerVideoUrl = None
        self.tvVideoTimestamp = None

    def stopPaceLobbyMusic(self):
        taskMgr.remove(getattr(self, 'paceMusicPositionTaskName', ''))
        taskMgr.remove(getattr(self, 'paceMusicRestoreTaskName', ''))
        base.musicManager.stopAllSounds()
        if getattr(self, 'pacelobbyMusic', None):
            try:
                self.pacelobbyMusic.stop()
            except Exception:
                pass
            self.pacelobbyMusic = None
        if getattr(self, 'pacelobbyMusicFile', None):
            try:
                self.pacelobbyMusicFile.stop()
            except Exception:
                pass
            self.pacelobbyMusicFile = None
        self.paceLobbyMusicTime = 0.0

    def disable(self):
        self._cleanupTV()
        taskMgr.remove(self.bellTaskName)
        taskMgr.remove(self.showerTaskName)
        self.ignore(self.positionPrinterEvent)
        taskMgr.remove('pacelobbyMusic')
        self.bellInside = False
        self.stopPaceLobbyMusic()
        self.motoroomSigilvatorOrigin = None

        if self.bellSound:
            self.bellSound.stop()
            self.bellSound = None
        if self.showerSound:
            self.showerSound.stop()
            self.showerSound = None

        if hasattr(self, 'lavaLamps'):
            for lamp in self.lavaLamps:
                lamp.cleanup()
                lamp.removeNode()
            del self.lavaLamps

        DistributedToonInterior.DistributedToonInterior.disable(self)


    def delete(self):
        self._cleanupTV()
        taskMgr.remove(self.bellTaskName)
        taskMgr.remove(self.showerTaskName)
        self.ignore(self.positionPrinterEvent)
        taskMgr.remove('pacelobbyMusic')
        self.stopPaceLobbyMusic()
        self.motoroomSigilvatorOrigin = None
        if hasattr(self, 'lavaLamps'):
            for lamp in self.lavaLamps:
                lamp.cleanup()
                lamp.removeNode()
            del self.lavaLamps
        DistributedToonInterior.DistributedToonInterior.delete(self)

