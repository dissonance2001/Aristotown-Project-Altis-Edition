import json
import os
import re
import shutil
import subprocess
import sys
import threading
import uuid
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

import builtins
from direct.gui.DirectGui import DirectButton, DirectEntry, DirectFrame, DirectLabel, DirectScrolledFrame, DirectSlider
from direct.showbase.DirectObject import DirectObject
from direct.task.TaskManagerGlobal import taskMgr
from direct.task.Task import Task
from panda3d.core import Filename, Geom, GeomNode, GeomTriangles, GeomVertexData, GeomVertexFormat, GeomVertexWriter, TextNode, TextureStage, Vec3

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class PacesetterTVPlayer(DirectObject):
    CACHE_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'ProjectAltis', 'PacesetterTV')
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    DENO_PATH = os.path.join(PROJECT_ROOT, 'dependencies', 'deno', 'deno.exe')

    def __init__(self, tv, getOffset, controller, pauseMusic=None, resumeMusic=None):
        super().__init__()
        self.tv = tv
        self.getOffset = getOffset
        self.controller = controller
        self.pauseMusicCallback = pauseMusic
        self.resumeMusicCallback = resumeMusic
        self.youtubeUrl = ''
        self.movie = None
        self.sound = None
        self.screen = None
        self.videoPath = None
        self.downloadThread = None
        self.downloadUrl = None
        self.downloadResult = None
        self.pendingPlay = False
        self.musicPaused = False
        self.pendingSelectedUrl = None
        self.browserProcess = None
        self.selectionPath = os.path.join(self.CACHE_DIR, 'selection-%s.json' % uuid.uuid4().hex)
        self.selectionTaskName = 'tv-browser-selection-%s' % uuid.uuid4().hex
        self.controlPanel = None
        self.urlEntry = None
        self.playlistFrame = None
        self.volumeSlider = None
        self.playlistWidgets = []
        self.playlist = []
        self.playlistTitles = {}
        self.titleLookups = set()
        self.titleResults = []
        self.currentPlaylistUrl = None
        self.volume = 1.0
        self.titleTaskName = 'tv-title-lookup-%s' % uuid.uuid4().hex
        self.downloadTaskName = 'tv-download-%s' % uuid.uuid4().hex
        self.finishedEvent = 'TV-videoFinished-%s' % uuid.uuid4().hex
        self._createScreen()
        self._createControlPanel()
        taskMgr.add(self._downloadTask, self.downloadTaskName)
        taskMgr.add(self._pollBrowserSelection, self.selectionTaskName)
        taskMgr.add(self._titleTask, self.titleTaskName)

    def _createScreen(self):
        points = (
            Vec3(0.0265609883, -0.198608026, 0.778891146),
            Vec3(-0.291178435, -0.092263222, 0.754392207),
            Vec3(-0.218811542, -0.116409376, 0.394155681),
            Vec3(0.0574991703, -0.208890334, 0.425090134),
        )
        normal = Vec3(-0.31728, -0.94833, 0)
        screenWidth = ((points[0] - points[1]).length() + (points[3] - points[2]).length()) * 0.5
        screenHeight = ((points[1] - points[2]).length() + (points[0] - points[3]).length()) * 0.5
        self.screenAspect = screenWidth / screenHeight if screenHeight else 1.0
        center = (points[0] + points[1] + points[2] + points[3]) * 0.25
        points = tuple(center + (point - center) * 1.06 + normal * 0.004 for point in points)

        vertexData = GeomVertexData('TVScreen', GeomVertexFormat.getV3t2(), Geom.UHStatic)
        vertexWriter = GeomVertexWriter(vertexData, 'vertex')
        texWriter = GeomVertexWriter(vertexData, 'texcoord')

        for point, uv in zip(points, ((1, 1), (0, 1), (0, 0), (1, 0))):
            vertexWriter.addData3f(point)
            texWriter.addData2f(*uv)

        triangles = GeomTriangles(Geom.UHStatic)
        triangles.addVertices(0, 1, 2)
        triangles.addVertices(0, 2, 3)
        triangles.closePrimitive()

        geom = Geom(vertexData)
        geom.addPrimitive(triangles)
        node = GeomNode('TV-Screen')
        node.addGeom(geom)
        self.screen = self.tv.attachNewNode(node)
        self.screen.setTwoSided(True)
        self.screen.setLightOff()
        self.screen.setDepthWrite(False)
        self.screen.setDepthOffset(2)
        self.screen.hide()

    def _createControlPanel(self):
        baseObject = getattr(builtins, 'base', None)
        parent = getattr(builtins, 'aspect2d', None)
        if parent is None and baseObject is not None:
            parent = getattr(baseObject, 'aspect2d', None)
        if parent is None or baseObject is None:
            return
        try:
            aspect = float(baseObject.getAspectRatio())
            self.controlPanel = DirectFrame(
                parent=parent,
                frameColor=(0.035, 0.045, 0.065, 0.96),
                frameSize=(-0.38, 0.38, -0.92, 0.92),
                pos=(aspect - 0.42, 0, 0),
                relief=1,
            )
            DirectLabel(
                parent=self.controlPanel,
                text='TV',
                text_scale=0.042,
                text_fg=(1, 1, 1, 1),
                frameColor=(0, 0, 0, 0),
                pos=(0, 0, 0.82),
            )
            DirectLabel(
                parent=self.controlPanel,
                text='YouTube URL',
                text_scale=0.026,
                text_fg=(0.82, 0.85, 0.9, 1),
                frameColor=(0, 0, 0, 0),
                pos=(-0.23, 0, 0.735),
            )
            self.urlEntry = DirectEntry(
                parent=self.controlPanel,
                initialText='',
                width=19,
                scale=0.029,
                pos=(-0.285, 0, 0.68),
                command=self._playEnteredURL,
                numLines=1,
                focus=0,
                frameColor=(0.92, 0.92, 0.94, 1),
                text_fg=(0.05, 0.05, 0.06, 1),
                entryFont=None,
            )
            DirectButton(
                parent=self.controlPanel,
                text='Play URL',
                scale=0.031,
                pos=(-0.17, 0, 0.55),
                command=self._playEnteredURL,
                frameColor=(0.12, 0.38, 0.62, 1),
                text_fg=(1, 1, 1, 1),
            )
            DirectButton(
                parent=self.controlPanel,
                text='Add to playlist',
                scale=0.031,
                pos=(0.16, 0, 0.55),
                command=self._queueEnteredURL,
                frameColor=(0.18, 0.34, 0.24, 1),
                text_fg=(1, 1, 1, 1),
            )
            DirectButton(
                parent=self.controlPanel,
                text='Browse YouTube',
                scale=0.031,
                pos=(0, 0, 0.43),
                command=self.openBrowser,
                frameColor=(0.26, 0.27, 0.31, 1),
                text_fg=(1, 1, 1, 1),
            )
            DirectLabel(
                parent=self.controlPanel,
                text='PLAYLIST',
                text_scale=0.033,
                text_fg=(0.88, 0.9, 0.95, 1),
                frameColor=(0, 0, 0, 0),
                pos=(0, 0, 0.29),
            )
            self.playlistFrame = DirectScrolledFrame(
                parent=self.controlPanel,
                frameSize=(-0.32, 0.32, -0.64, 0.16),
                canvasSize=(-0.30, 0.30, -0.1, 0),
                pos=(0, 0, -0.02),
                scrollBarWidth=0.035,
                frameColor=(0.055, 0.065, 0.085, 1),
                borderWidth=(0.005, 0.005),
            )
            DirectLabel(
                parent=self.controlPanel,
                text='Volume',
                text_scale=0.024,
                text_fg=(0.88, 0.9, 0.95, 1),
                frameColor=(0, 0, 0, 0),
                pos=(-0.29, 0, -0.70),
            )
            self.volumeSlider = DirectSlider(
                parent=self.controlPanel,
                range=(0, 1),
                value=self.volume,
                pageSize=0.1,
                scale=0.27,
                pos=(0.05, 0, -0.70),
                command=self._setVolume,
                thumb_frameColor=(0.85, 0.88, 0.94, 1),
                frameColor=(0.18, 0.2, 0.24, 1),
            )
            DirectButton(
                parent=self.controlPanel,
                text='Skip',
                scale=0.027,
                pos=(-0.23, 0, -0.83),
                command=self._skipNext,
                frameColor=(0.15, 0.35, 0.5, 1),
                text_fg=(1, 1, 1, 1),
            )
            DirectButton(
                parent=self.controlPanel,
                text='Stop TV',
                scale=0.027,
                pos=(0, 0, -0.83),
                command=self._stopFromPanel,
                frameColor=(0.5, 0.16, 0.15, 1),
                text_fg=(1, 1, 1, 1),
            )
            DirectButton(
                parent=self.controlPanel,
                text='Hide panel',
                scale=0.027,
                pos=(0.23, 0, -0.83),
                command=self._hideControlPanel,
                frameColor=(0.24, 0.25, 0.29, 1),
                text_fg=(1, 1, 1, 1),
            )
            self.controlPanel.hide()
            self.accept('f8', self._showControlPanel)
            self._refreshPlaylist()
        except Exception as exc:
            self.notify.warning('Unable to create TV controls: %s' % exc)
            if self.controlPanel:
                self.controlPanel.destroy()
            self.controlPanel = None
            self.urlEntry = None
            self.playlistFrame = None
            self.volumeSlider = None

    @staticmethod
    def _normalizeYouTubeURL(value):
        parsed = urlparse(str(value or '').strip())
        host = (parsed.hostname or '').lower()
        videoId = ''
        if host == 'youtu.be':
            videoId = parsed.path.strip('/').split('/')[0]
        elif host in ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'music.youtube.com'):
            if parsed.path == '/watch':
                videoId = parse_qs(parsed.query).get('v', [''])[0]
            elif parsed.path.startswith(('/shorts/', '/embed/', '/live/')):
                parts = parsed.path.strip('/').split('/')
                if len(parts) > 1:
                    videoId = parts[1]
        if not re.fullmatch(r'[A-Za-z0-9_-]{6,20}', videoId):
            return ''
        return 'https://www.youtube.com/watch?v=' + videoId

    def _showControlPanel(self):
        if self.controlPanel:
            self.controlPanel.show()

    def _hideControlPanel(self):
        if self.controlPanel:
            self.controlPanel.hide()

    def _videoId(self, url):
        parsed = urlparse(url)
        videoId = parse_qs(parsed.query).get('v', [''])[0]
        if not videoId and parsed.hostname == 'youtu.be':
            videoId = parsed.path.strip('/').split('/')[0]
        return videoId or url.rstrip('/').split('/')[-1]

    def _playlistLabel(self, url):
        title = self.playlistTitles.get(url, 'Loading video title…')
        if len(title) > 37:
            title = title[:34].rstrip() + '…'
        return title

    def _requestVideoTitle(self, url):
        if url in self.playlistTitles or url in self.titleLookups:
            return
        self.titleLookups.add(url)
        threading.Thread(
            target=self._fetchVideoTitle,
            args=(url,),
            name='TVTitleLookup',
            daemon=True,
        ).start()

    def _fetchVideoTitle(self, url):
        title = None
        try:
            query = urlencode({'url': url, 'format': 'json'})
            request = Request(
                'https://www.youtube.com/oembed?' + query,
                headers={'User-Agent': 'Mozilla/5.0'},
            )
            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
            title = str(data.get('title') or '').strip() or None
        except Exception:
            title = None
        if not title:
            title = 'Video %s' % self._videoId(url)
        self.titleResults.append((url, title))

    def _titleTask(self, task):
        if self.titleResults:
            results = self.titleResults[:]
            self.titleResults.clear()
            for url, title in results:
                self.playlistTitles[url] = title
                self.titleLookups.discard(url)
            self._refreshPlaylist()
        return Task.cont

    def _setVolume(self, value=None):
        if value is None and self.volumeSlider is not None:
            value = self.volumeSlider['value']
        try:
            self.volume = max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            self.volume = 1.0
        if self.sound:
            self.sound.setVolume(self.volume)

    def _skipNext(self):
        if not self.playlist:
            return
        currentUrl = self.currentPlaylistUrl or self.youtubeUrl
        try:
            currentIndex = self.playlist.index(currentUrl)
        except ValueError:
            currentIndex = -1
        nextIndex = currentIndex + 1
        if nextIndex >= len(self.playlist):
            self.notify.info('There are no more videos queued.')
            return
        self._requestPlay(self.playlist[nextIndex])

    def _refreshPlaylist(self):
        if not self.playlistFrame:
            return
        for widget in self.playlistWidgets:
            try:
                widget.destroy()
            except Exception:
                pass
        self.playlistWidgets = []
        canvas = self.playlistFrame.getCanvas()
        if not self.playlist:
            emptyLabel = DirectLabel(
                parent=canvas,
                text='Paste a URL or browse YouTube.',
                text_scale=0.027,
                text_fg=(0.78, 0.8, 0.84, 1),
                frameColor=(0, 0, 0, 0),
                pos=(0, 0, -0.05),
            )
            self.playlistWidgets.append(emptyLabel)
            self.playlistFrame['canvasSize'] = (-0.30, 0.30, -0.1, 0)
            return
        bottom = max(0.1, len(self.playlist) * 0.085 + 0.02)
        self.playlistFrame['canvasSize'] = (-0.30, 0.30, -bottom, 0)
        for index, url in enumerate(self.playlist):
            button = DirectButton(
                parent=canvas,
                text=self._playlistLabel(url),
                text_align=TextNode.ALeft,
                text_scale=0.85,
                text_pos=(-8.2, -0.25),
                text_fg=(1, 1, 1, 1),
                frameColor=(0.13, 0.15, 0.19, 1),
                frameSize=(-9.2, 9.2, -0.65, 0.65),
                scale=0.028,
                pos=(-0.01, 0, -0.045 - index * 0.085),
                command=self._playPlaylistItem,
                extraArgs=[url],
            )
            self.playlistWidgets.append(button)

    def _addPlaylistItem(self, url):
        if url not in self.playlist:
            self.playlist.append(url)
            self._refreshPlaylist()
        self._requestVideoTitle(url)

    def _enteredURL(self, value=None):
        if value is not None and isinstance(value, str) and value.strip():
            return value.strip()
        if self.urlEntry:
            return self.urlEntry.get().strip()
        return ''

    def _playEnteredURL(self, value=None):
        url = self._normalizeYouTubeURL(self._enteredURL(value))
        if not url:
            self.notify.warning('Enter a valid YouTube video URL.')
            return
        self._addPlaylistItem(url)
        self._showControlPanel()
        self._requestPlay(url)

    def _queueEnteredURL(self, value=None):
        url = self._normalizeYouTubeURL(self._enteredURL(value))
        if not url:
            self.notify.warning('Enter a valid YouTube video URL.')
            return
        self._addPlaylistItem(url)
        if self.urlEntry:
            self.urlEntry.enterText('')

    def _playPlaylistItem(self, url):
        self._showControlPanel()
        self._requestPlay(url)

    def _requestPlay(self, url):
        self.currentPlaylistUrl = url
        self._addPlaylistItem(url)
        if self.controller:
            try:
                self.controller.sendUpdate('requestPlayVideo', [url])
                return
            except Exception as exc:
                self.notify.warning('Unable to send YouTube selection to the TV server: %s' % exc)
        self.pendingSelectedUrl = url
        self.notify.warning('YouTube selection queued; waiting for the TV server object.')

    def _stopFromPanel(self):
        if self.controller:
            try:
                self.controller.sendUpdate('requestExit')
            except Exception as exc:
                self.notify.warning('Unable to stop TV: %s' % exc)
        self.stop()

    def setController(self, controller):
        self.controller = controller
        if self.pendingSelectedUrl:
            url = self.pendingSelectedUrl
            try:
                controller.sendUpdate('requestPlayVideo', [url])
                self.pendingSelectedUrl = None
                self.notify.info('Sent queued YouTube selection to the TV server.')
            except Exception as exc:
                self.notify.warning('Unable to send queued YouTube selection to the TV server: %s' % exc)

    def openBrowser(self):
        if self.browserProcess and self.browserProcess.poll() is None:
            return

        baseObject = getattr(builtins, 'base', None)
        if baseObject is None or baseObject.win is None:
            self.notify.warning('Unable to open TV browser: Panda3D window is unavailable.')
            return

        try:
            os.makedirs(self.CACHE_DIR, exist_ok=True)
            if os.path.exists(self.selectionPath):
                os.remove(self.selectionPath)
            windowHandle = baseObject.win.getWindowHandle()
            parentHandle = windowHandle.getIntHandle() if hasattr(windowHandle, 'getIntHandle') else int(windowHandle)
            browserScript = os.path.join(os.path.dirname(__file__), 'PacesetterTVBrowser.py')
            creationFlags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            if os.name == 'nt':
                pythonLauncher = shutil.which('py')
                if pythonLauncher:
                    browserCommand = [pythonLauncher, '-3.13', browserScript, str(parentHandle), self.selectionPath]
                else:
                    browserCommand = [sys.executable, browserScript, str(parentHandle), self.selectionPath]
            else:
                browserCommand = [sys.executable, browserScript, str(parentHandle), self.selectionPath]
            self.browserProcess = subprocess.Popen(
                browserCommand,
                creationflags=creationFlags,
            )
        except Exception as exc:
            self.notify.warning('Unable to open TV browser: %s' % exc)

    def _pollBrowserSelection(self, task):
        if os.path.exists(self.selectionPath):
            try:
                with open(self.selectionPath, 'r', encoding='utf-8') as selectionFile:
                    selection = json.load(selectionFile)
                os.remove(self.selectionPath)
                if selection.get('error'):
                    self.notify.warning('TV browser: %s' % selection['error'])
                elif selection.get('url'):
                    selectedUrl = selection['url']
                    self.notify.info('YouTube video selected: %s' % selectedUrl)
                    self._addPlaylistItem(selectedUrl)
                    self._showControlPanel()
                    self._requestPlay(selectedUrl)
                    if self.controller:
                        self.notify.info('Sent YouTube selection to the TV server.')
            except (OSError, ValueError, TypeError) as exc:
                self.notify.warning('Unable to read TV browser selection: %s' % exc)
        return Task.cont

    def setURL(self, url):
        if not url:
            return
        if url == self.youtubeUrl:
            self._showControlPanel()
            self._addPlaylistItem(url)
            self.currentPlaylistUrl = url
            if self.movie and self.sound:
                self.pendingPlay = True
                self._startPlayback()
            return
        self._pauseLobbyMusic()
        self._addPlaylistItem(url)
        self.currentPlaylistUrl = url
        self._showControlPanel()
        self.youtubeUrl = url
        self.videoPath = None
        self.pendingPlay = True
        if self.sound:
            self.sound.stop()
            self.sound = None
        if self.movie:
            self.movie.stop()
            try:
                self.movie.unsynchronize()
            except Exception:
                pass
            self.movie = None
        self.screen.hide()
        if self.downloadThread is None:
            self._startDownload()

    def _pauseLobbyMusic(self):
        if self.musicPaused:
            return
        try:
            if self.pauseMusicCallback:
                self.pauseMusicCallback()
            else:
                baseObject = getattr(builtins, 'base', None)
                musicMgr = getattr(baseObject, 'musicMgr', None) if baseObject else None
                if musicMgr:
                    musicMgr.stopMusic('pacesetter_lobby')
            self.musicPaused = True
        except Exception as exc:
            self.notify.warning('Unable to pause Pace Lobby music: %s' % exc)

    def _resumeLobbyMusic(self):
        if not self.musicPaused:
            return
        try:
            if self.resumeMusicCallback:
                self.resumeMusicCallback()
            else:
                baseObject = getattr(builtins, 'base', None)
                musicMgr = getattr(baseObject, 'musicMgr', None) if baseObject else None
                if musicMgr:
                    musicMgr.playMusic('pacesetter_lobby', looping=1, interrupt=0, musicCode='pacesetter_lobby')
        except Exception as exc:
            self.notify.warning('Unable to resume Pace Lobby music: %s' % exc)
        self.musicPaused = False

    def play(self):
        self.pendingPlay = True
        self._pauseLobbyMusic()
        if self.movie and self.sound and self.videoPath:
            self._startPlayback()
            return
        if self.downloadThread is None and self.youtubeUrl:
            self._startDownload()

    def stop(self):
        self.pendingPlay = False
        self._hideControlPanel()
        self._resumeLobbyMusic()
        if self.sound:
            self.sound.stop()
        if self.movie:
            self.movie.stop()
        if self.screen:
            self.screen.hide()

    def _startDownload(self):
        if not self.youtubeUrl:
            return
        try:
            os.makedirs(self.CACHE_DIR, exist_ok=True)
        except OSError as exc:
            self.notify.warning('Unable to create TV cache directory: %s' % exc)
            self.pendingPlay = False
            return

        self.downloadResult = None
        self.downloadUrl = self.youtubeUrl
        self.downloadThread = threading.Thread(
            target=self._downloadWorker,
            args=(self.downloadUrl,),
            name='TVDownload',
            daemon=True,
        )
        self.downloadThread.start()

    def _downloadWorker(self, videoUrl):
        try:
            import yt_dlp

            denoPath = self.DENO_PATH
            if not os.path.isfile(denoPath):
                userDenoPath = os.path.join(os.path.expanduser('~'), '.deno', 'bin', 'deno.exe')
                denoPath = userDenoPath if os.path.isfile(userDenoPath) else shutil.which('deno')
            if not denoPath:
                raise RuntimeError('Deno is missing. Run Install_Deno.bat from the Corporate Clash project root and try again.')

            failures = []
            filename = None
            videoId = videoUrl.split('v=')[-1].split('&')[0] if 'v=' in videoUrl else videoUrl.rstrip('/').split('/')[-1]
            for playerClient in ('android', 'android_vr', 'web_safari'):
                ydlOpts = {
                    'format': 'best[ext=mp4][height<=480]/best[height<=480]/best[ext=mp4]/best',
                    'noplaylist': True,
                    'quiet': True,
                    'no_warnings': False,
                    'remote_components': ['ejs:npm', 'ejs:github'],
                    'retries': 2,
                    'fragment_retries': 2,
                    'socket_timeout': 20,
                    'js_runtimes': {'deno': {'path': denoPath}},
                    'extractor_args': {'youtube': {'player_client': [playerClient]}},
                    'outtmpl': os.path.join(self.CACHE_DIR, '%(id)s.%(ext)s'),
                }
                try:
                    with yt_dlp.YoutubeDL(ydlOpts) as ydl:
                        info = ydl.extract_info(videoUrl, download=True)
                        candidate = ydl.prepare_filename(info)
                    if not os.path.isfile(candidate):
                        candidates = [
                            os.path.join(self.CACHE_DIR, name)
                            for name in os.listdir(self.CACHE_DIR)
                            if name.startswith(videoId + '.') and not name.endswith(('.part', '.ytdl', '.audio.wav', '.altis_tv.mp4'))
                        ]
                        if candidates:
                            candidate = max(candidates, key=os.path.getsize)
                    if os.path.isfile(candidate):
                        filename = candidate
                        break
                    failures.append('%s: yt-dlp finished but no downloaded video file was found' % playerClient)
                except Exception as exc:
                    failures.append('%s: %s' % (playerClient, exc))

            if not filename:
                raise RuntimeError('All YouTube extraction clients failed. ' + ' | '.join(failures))
            self.downloadResult = (videoUrl, filename)
        except Exception as exc:
            self.downloadResult = (videoUrl, exc)

    def _downloadTask(self, task):
        if self.downloadThread and not self.downloadThread.is_alive() and self.downloadResult is not None:
            completedUrl, result = self.downloadResult
            self.downloadThread = None
            self.downloadResult = None
            self.downloadUrl = None
            if completedUrl != self.youtubeUrl:
                if self.youtubeUrl:
                    self._startDownload()
            elif isinstance(result, Exception):
                self.notify.warning('Unable to load TV video: %s' % result)
                self.pendingPlay = False
                self._resumeLobbyMusic()
            else:
                self.videoPath = result
                if self.pendingPlay:
                    self._loadPlayback()
        return Task.cont

    def _loadPlayback(self):
        try:
            loader = builtins.loader
            pandaVideoPath = Filename.fromOsSpecific(os.path.abspath(self.videoPath))
            self.movie = loader.loadTexture(pandaVideoPath)
            self.sound = loader.loadSfx(pandaVideoPath)
            if self.sound:
                self.sound.setVolume(self.volume)
            if not self.movie or not self.sound or not hasattr(self.movie, 'synchronizeTo'):
                raise RuntimeError('Panda3D could not load the downloaded video.')
            self.movie.synchronizeTo(self.sound)
            self.sound.setFinishedEvent(self.finishedEvent)
            self.accept(self.finishedEvent, self._videoFinished)
            self.screen.setTexture(self.movie, 1000)
            self._fitVideoToScreen()
            self._startPlayback()
        except Exception as exc:
            self.notify.warning('Unable to initialize TV video: %s' % exc)
            self.pendingPlay = False
            self._resumeLobbyMusic()

    def _fitVideoToScreen(self):
        if not self.movie or not self.screen:
            return
        try:
            videoWidth = float(self.movie.getXSize())
            videoHeight = float(self.movie.getYSize())
            if videoWidth <= 0 or videoHeight <= 0 or self.screenAspect <= 0:
                return
            videoAspect = videoWidth / videoHeight
            stage = TextureStage.getDefault()
            if videoAspect > self.screenAspect:
                factor = self.screenAspect / videoAspect
                self.screen.setTexScale(stage, factor, 1.0)
                self.screen.setTexOffset(stage, (1.0 - factor) * 0.5, 0.0)
            elif videoAspect < self.screenAspect:
                factor = videoAspect / self.screenAspect
                self.screen.setTexScale(stage, 1.0, factor)
                self.screen.setTexOffset(stage, 0.0, (1.0 - factor) * 0.5)
            else:
                self.screen.setTexScale(stage, 1.0, 1.0)
                self.screen.setTexOffset(stage, 0.0, 0.0)
        except (AttributeError, TypeError, ValueError, ZeroDivisionError):
            pass

    def seekToOffset(self, offset):
        if not self.movie or not self.sound:
            return
        try:
            target = max(0.0, float(offset))
            duration = float(self.sound.length())
            if duration > 0:
                target = min(target, max(0.0, duration - 0.1))
            wasPlaying = self.sound.status() == self.sound.PLAYING and not self.pendingPlay
            self.sound.stop()
            self.sound.setTime(target)
            self.movie.synchronizeTo(self.sound)
            if wasPlaying:
                self.sound.play()
        except Exception as exc:
            self.notify.warning('Unable to synchronize TV playback: %s' % exc)

    def _startPlayback(self):
        if not self.movie or not self.sound:
            return

        offset = max(0.0, float(self.getOffset()))
        if self.sound.length() > 0 and offset >= self.sound.length():
            self.stop()
            return

        self.sound.stop()
        self.sound.setTime(offset)
        self.sound.play()
        self.screen.show()
        self._showControlPanel()
        self.pendingPlay = False

    def _videoFinished(self):
        if self.pendingPlay or not self.controller:
            return
        self.controller.sendUpdate('requestExit')

    def destroy(self):
        taskMgr.remove(self.downloadTaskName)
        taskMgr.remove(self.selectionTaskName)
        taskMgr.remove(self.titleTaskName)
        self.ignore(self.finishedEvent)
        self.ignore('f8')
        if self.browserProcess and self.browserProcess.poll() is None:
            self.browserProcess.terminate()
        if self.sound:
            self.sound.stop()
        if self.movie:
            self.movie.stop()
            try:
                self.movie.unsynchronize()
            except Exception:
                pass
        if self.screen:
            self.screen.removeNode()
        if self.controlPanel:
            self.controlPanel.destroy()
            self.controlPanel = None
        self.sound = None
        self.movie = None
        self.screen = None
