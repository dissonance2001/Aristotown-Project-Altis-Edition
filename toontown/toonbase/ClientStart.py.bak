#!/usr/bin/env python2
import __builtin__
import os
import sys

__builtin__.process = 'client'

# Temporary hack patch:
__builtin__.__dict__.update(__import__('pandac.PandaModules', fromlist = ['*']).__dict__)
from direct.extensions_native import HTTPChannel_extensions
from direct.extensions_native import Mat3_extensions
from direct.extensions_native import VBase3_extensions
from direct.extensions_native import VBase4_extensions
from direct.extensions_native import NodePath_extensions
from panda3d.core import *

loadPrcFile('dependencies/config/general.prc')
loadPrcFile('dependencies/config/release/dev.prc')
if sys.platform == 'darwin':
    loadPrcFile('dependencies/config/macos.prc')

import StringIO
vfs = VirtualFileSystem.getGlobalPtr()
import glob

# Mount content packs before importing OTP/Toontown modules or loading
# the default phase archives. Fonts and GUI assets can be cached very early.

from direct.directnotify.DirectNotifyGlobal import directNotify
from otp.settings.Settings import Settings

notify = directNotify.newCategory('AltisClient')
notify.setInfo(True)

preferencesFilename = ConfigVariableString(
    'preferences-filename', 'user/preferences.json').getValue()
notify.info('Reading %s...' % preferencesFilename)
__builtin__.settings = Settings(preferencesFilename)
from toontown.settings import ToontownSettings
__builtin__.ttsettings = ToontownSettings

hadDisplayMode = 'display-mode' in settings
for setting in ttsettings.DefaultSettings:
    if setting not in settings:
        settings[setting] = ttsettings.DefaultSettings[setting]

if not hadDisplayMode:
    settings['display-mode'] = 2 if settings.get('fullscreen', False) else 0

displayMode = int(settings.get('display-mode', 0))
settings['fullscreen'] = displayMode == 2
loadPrcFileData('Settings: res', 'win-size %d %d' % tuple(settings.get('res', (1280, 720))))
loadPrcFileData('Settings: fullscreen', 'fullscreen %s' % settings['fullscreen'])
loadPrcFileData('Settings: borderless', 'undecorated %s' % (displayMode == 1))
loadPrcFileData('Settings: music', 'audio-music-active %s' % settings['music'])
loadPrcFileData('Settings: sfx', 'audio-sfx-active %s' % settings['sfx'])
musicVol = float(settings.get('musicVol', 1.0))
sfxVol = float(settings.get('sfxVol', 1.0))
loadPrcFileData('Settings: musicVol', 'audio-master-music-volume %s' % musicVol)
loadPrcFileData('Settings: sfxVol', 'audio-master-sfx-volume %s' % sfxVol)
loadDisplay = settings.get('loadDisplay', 'pandagl')
if sys.platform == 'darwin':
    loadDisplay = 'pandagl'
loadPrcFileData('Settings: loadDisplay', 'load-display %s' % loadDisplay)
loadPrcFileData('Settings: toonChatSounds', 'toon-chat-sounds %s' % settings['toonChatSounds'])
anisoIndex = int(settings.get('anisotropic-filtering', 0))
if anisoIndex < 0 or anisoIndex >= len(ttsettings.AnistrophicOptions):
    anisoIndex = 0
    settings['anisotropic-filtering'] = anisoIndex
loadPrcFileData('', 'texture-anisotropic-degree %d' % ttsettings.AnistrophicOptions[anisoIndex])
loadPrcFileData('', 'framebuffer-multisample %s' % settings['anti-aliasing'])
loadPrcFileData('', 'multisamples %s' % (1 if settings['anti-aliasing'] else 0))
loadPrcFileData('', 'sync-video %s' % settings['vertical-sync'])

vfs = VirtualFileSystem.getGlobalPtr()
DefaultPhases = (3, 3.5, 4, 5, 5.5, 6, 7, 8, 9, 10, 11, 12, 13)
import glob
notify.info("Loading Default Pack...")
__builtin__.defaultPhaseMultifiles = []
for file in glob.glob('resources/default/*.mf'):
    phaseName = os.path.splitext(os.path.basename(file))[0]
    if not phaseName.startswith('phase_'):
        continue
    try:
        phase = float(phaseName[len('phase_'):])
    except ValueError:
        continue
    if phase in DefaultPhases:
        mf = Multifile()
        phaseFilename = Filename.fromOsSpecific(os.path.abspath(file))
        if not mf.openRead(phaseFilename):
            notify.warning('Failed to open default phase: ' + file)
            continue
        if not vfs.mount(mf, Filename('/'), VirtualFileSystem.MFReadOnly):
            notify.warning('Failed to mount default phase: ' + file)
            mf.close()
            continue
        defaultPhaseMultifiles.append(mf)
        notify.info('Successfully Mounted:' + file)
notify.info("Default Pack Loaded!")
from toontown.toonbase.ContentPackManager import ContentPackManager
__builtin__.ContentPackMgr = ContentPackManager()
ContentPackMgr.loadAll()

loadPrcFileData('', 'load-display %s' % loadDisplay)

import os
import time
import sys
import random
import __builtin__

try:
    from toontown.launcher.TTALauncher import TTALauncher
    launcher = TTALauncher()
    __builtin__.launcher = launcher
except Exception as e:
    raise (e)

if launcher.isDummy():
    http = HTTPClient()
else:
    http = launcher.http

from toontown.toonbase import ToontownGlobals
tempLoader = Loader()

from direct.gui import DirectGuiGlobals
from direct.gui.DirectGui import *

from toontown.pgui import DirectGuiGlobals as PGUIGlobals

DirectGuiGlobals.setDefaultFontFunc(ToontownGlobals.getInterfaceFont)
PGUIGlobals.setDefaultFontFunc(ToontownGlobals.getInterfaceFont)
launcher.setPandaErrorCode(7)
notify.info('Loading AltisBase...')
from toontown.toonbase import ToonBase
ToonBase.ToonBase()
if base.win is None:
    notify.error('Unable to open window; aborting.')

launcher.setPandaErrorCode(0)
launcher.setPandaWindowOpen()
ConfigVariableDouble('decompressor-step-time').setValue(0.01)
ConfigVariableDouble('extractor-step-time').setValue(0.01)
backgroundNode = tempLoader.loadSync(Filename('phase_3/models/gui/loading-background'))
backgroundNodePath = aspect2d.attachNewNode(backgroundNode, 0)
backgroundNodePath.setPos(0.0, 0.0, 0.0)
backgroundNodePath.setScale(render2d, VBase3(1))
backgroundNodePath.find('**/fg').hide()
logo = OnscreenImage(
    image = 'phase_3/maps/toontown-logo.png',
    scale = (1 / (4.0 / 3.0), 1, 1 / (4.0 / 3.0)),
    pos = backgroundNodePath.find('**/fg').getPos())
logo.setTransparency(TransparencyAttrib.MAlpha)
logo.setBin('fixed', 20)
logo.reparentTo(backgroundNodePath)
backgroundNodePath.find('**/bg').setBin('fixed', 10)
base.graphicsEngine.renderFrame()
DirectGuiGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
DirectGuiGlobals.setDefaultClickSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
DirectGuiGlobals.setDefaultDialogGeom(loader.loadModel('phase_3/models/gui/dialog_box_gui'))
PGUIGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
PGUIGlobals.setDefaultClickSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
PGUIGlobals.setDefaultDialogGeom(loader.loadModel('phase_3/models/gui/dialog_box_gui'))
from toontown.toonbase import TTLocalizer
from otp.otpbase import OTPGlobals
OTPGlobals.setDefaultProductPrefix(TTLocalizer.ProductPrefix)

if base.musicManagerIsValid:
    music = base.loader.loadMusic('phase_3/audio/bgm/tt_theme.ogg')
    if music:
        music.setLoop(1)
        music.setVolume(0.9)
        music.play()
    notify.info('Loading the default GUI sounds...')
    DirectGuiGlobals.setDefaultRolloverSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_rollover.ogg'))
    DirectGuiGlobals.setDefaultClickSound(base.loader.loadSfx('phase_3/audio/sfx/GUI_create_toon_fwd.ogg'))
else:
    music = None
from toontown.toonbase import ToontownLoader
from direct.gui.DirectGui import *
serverVersion = base.config.GetString('server-version', 'no_version_set')

version = OnscreenText(serverVersion, pos = (-1.3, -0.975), scale = 0.06, fg = Vec4(0, 0, 0, 1), align = TextNode.ALeft)
version.setPos(0.03, 0.03)
version.reparentTo(base.a2dBottomLeft)
from toontown.suit import Suit
Suit.loadModels()
loader.beginBulkLoad('init', TTLocalizer.LoaderLabel, 138, 0, TTLocalizer.TIP_NONE, 0)
from toontown.toonbase.ToonBaseGlobal import *
from direct.showbase.MessengerGlobal import *
from toontown.distributed import ToontownClientRepository
cr = ToontownClientRepository.ToontownClientRepository(serverVersion, launcher)
cr.music = music
del music
base.initNametagGlobals()
base.cr = cr
loader.endBulkLoad('init')
from otp.friends import FriendManager
from otp.distributed.OtpDoGlobals import *
cr.generateGlobalObject(OTP_DO_ID_FRIEND_MANAGER, 'FriendManager')
if not launcher.isDummy():
    base.startShow(cr, launcher.getGameServer())
else:
    base.startShow(cr)
backgroundNodePath.reparentTo(hidden)
backgroundNodePath.removeNode()
del backgroundNodePath
del backgroundNode
del tempLoader
version.cleanup()
del version
base.loader = base.loader
__builtin__.loader = base.loader
autoRun = ConfigVariableBool('toontown-auto-run', 1)

def printCameraPos():
    print(camera.getPos())
    print(camera.getHpr())

# base.accept('[', printCameraPos)

def printOobePos():
    print(base.oobeCameraTrackball.getPos())
    print(base.oobeCameraTrackball.getHpr())
    print

# base.accept(']', printOobePos)

def printToonPos():
    print(camera.getPos())
    print(camera.getHpr())

# base.accept('[', printCameraPos)

# X movement
def cameraX():
    camera.setX(camera.getX() + 1)

#base.accept('f1', cameraX)

def cameraXDecrease():
    camera.setX(camera.getX() - 1)

#base.accept('f2', cameraXDecrease)#

# Y movement
def cameraY():
    camera.setY(camera.getY() + 1)

#base.accept('f3', cameraY)

def cameraYDecrease():
    camera.setY(camera.getY() - 1)

#base.accept('f4', cameraYDecrease)

# Z movement
def cameraZ():
    camera.setZ(camera.getZ() + 1)

#base.accept('f5', cameraZ)

def cameraZDecrease():
    camera.setZ(camera.getZ() - 1)

#base.accept('f6', cameraZDecrease)

# H rotation (Heading)
def cameraH():
    camera.setH(camera.getH() + 1)

#base.accept('f7', cameraH)

def cameraHDecrease():
    camera.setH(camera.getH() - 1)

#base.accept('f8', cameraHDecrease)

# P rotation (Pitch)
def cameraP():
    camera.setP(camera.getP() + 1)

#base.accept('f9', cameraP)

def cameraPDecrease():
    camera.setP(camera.getP() - 1)

#base.accept('f10', cameraPDecrease)

# R rotation (Roll)
def cameraR():
    camera.setR(camera.getR() + 1)

#base.accept('f11', cameraR)

def cameraRDecrease():
    camera.setR(camera.getR() - 1)

#base.accept('f12', cameraRDecrease)

if autoRun:
    try:
        base.run()
    except SystemExit:
        raise
    except:
        from toontown.toonbase import ToonPythonUtil as PythonUtil
        print PythonUtil.describeException()
        raise
