from otp.ai.MagicWordGlobal import *
from pandac.PandaModules import Filename

try:
    import __builtin__ as _builtins
except ImportError:
    import builtins as _builtins
try:
    from pandac.PandaModules import PStatClient
except:
    PStatClient = None
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals


@magicWord(name='logout', category=CATEGORY_COMMUNITY_MANAGER, types=[])
def clashLogout():
    """Takes you back to the Pick-A-Toon screen."""
    if not getattr(base, 'cr', None):
        return 'The client repository is not available.'
    base.cr.gameFSM.request('closeShard')
    return 'Logging out.'


@magicWord(name='tp', category=CATEGORY_COMMUNITY_MANAGER, types=[int])
def clashTp(zoneId):
    """Teleports you to an Altis zone or playground ID."""
    place = base.cr.playGame.getPlace()
    if place is None:
        return 'You cannot teleport from here.'
    hoodId = ZoneUtil.getHoodId(zoneId)
    place.requestTeleport(hoodId, zoneId, base.localAvatar.currentShard, -1)
    return 'Teleporting to zone %d.' % zoneId


@magicWord(name='cs', category=CATEGORY_PROGRAMMER, types=[])
def clashChainsawLobby():
    place = base.cr.playGame.getPlace()
    if place is None or not hasattr(place, 'fsm'):
        return 'You cannot teleport from here.'
    place.fsm.request('teleportOut', [{
        'loader': ZoneUtil.getLoaderName(ToontownGlobals.OutdoorZone),
        'where': 'toonInterior',
        'how': 'teleportIn',
        'hoodId': ToontownGlobals.OutdoorZone,
        'zoneId': ToontownGlobals.ChainsawLobby,
        'shardId': None,
        'avId': -1,
        'battle': 1,
        'quick': 1,
    }])
    return 'Teleporting to the Chainsaw Consultant lobby.'


@magicWord(name='district', category=CATEGORY_COMMUNITY_MANAGER, types=[int])
def clashDistrict(shardId):
    """Switches to the selected district ID."""
    if shardId == base.localAvatar.currentShard:
        return 'You are already in that district.'
    place = base.cr.playGame.getPlace()
    if place is None:
        return 'You cannot switch districts from here.'
    zoneId = base.localAvatar.getZoneId()
    hoodId = ZoneUtil.getCanonicalHoodId(zoneId)
    place.requestTeleport(hoodId, hoodId, shardId, -1)
    return 'Switching to district %d.' % shardId


def _getSettingsStore():
    # Some Altis launch paths expose the preferences object through Python 2's
    # builtins, while others do not.  Fall back to a small session store so
    # audio commands always work instead of raising NameError.
    store = getattr(_builtins, 'settings', None)
    if store is None:
        store = getattr(base, 'settings', None)
    if store is None:
        store = getattr(base, '_clashMagicWordSettings', None)
        if store is None:
            store = {}
            base._clashMagicWordSettings = store
    return store


def _rememberVolume(name, volume):
    try:
        _getSettingsStore()[name] = volume
    except:
        pass


def _readVolume(name, manager, default=1.0):
    store = _getSettingsStore()
    try:
        if name in store:
            return float(store[name])
    except:
        try:
            value = store.get(name)
            if value is not None:
                return float(value)
        except:
            pass
    try:
        return float(manager.getVolume())
    except:
        return float(default)


def _setMusicVolume(value):
    value = max(0, min(100, int(value)))
    volume = value / 100.0
    base.musicManager.setVolume(volume)
    base.musicActive = volume > 0.0
    _rememberVolume('musicVol', volume)
    return value


def _setSfxVolume(value):
    value = max(0, min(100, int(value)))
    volume = value / 100.0
    for manager in base.sfxManagerList:
        manager.setVolume(volume)
    base.sfxActive = volume > 0.0
    _rememberVolume('sfxVol', volume)
    return value


@magicWord(name='music', category=CATEGORY_COMMUNITY_MANAGER, types=[int])
def clashMusic(volume):
    """Sets music volume from 0 to 100."""
    return 'Set music volume to %d%%.' % _setMusicVolume(volume)


@magicWord(name='sfx', category=CATEGORY_COMMUNITY_MANAGER, types=[int])
def clashSfx(volume):
    """Sets sound-effect volume from 0 to 100."""
    return 'Set sound-effect volume to %d%%.' % _setSfxVolume(volume)


@magicWord(name='volume', category=CATEGORY_COMMUNITY_MANAGER, types=[int])
def clashVolume(volume):
    """Sets music and sound-effect volume from 0 to 100."""
    music = _setMusicVolume(volume)
    _setSfxVolume(volume)
    return 'Set master volume to %d%%.' % music


@magicWord(name='currentvolume', category=CATEGORY_COMMUNITY_MANAGER, types=[])
def clashCurrentVolume():
    """Shows the current music and sound-effect volumes."""
    musicVolume = _readVolume('musicVol', base.musicManager)
    sfxManagers = getattr(base, 'sfxManagerList', [])
    sfxManager = sfxManagers[0] if sfxManagers else None
    sfxVolume = _readVolume('sfxVol', sfxManager)
    return 'Music: %d%%, SFX: %d%%.' % (
        int(round(musicVolume * 100)),
        int(round(sfxVolume * 100)))


@magicWord(name='toggle', category=CATEGORY_COMMUNITY_MANAGER, types=[])
def clashCollisionToggle():
    """Toggles your Toon collisions."""
    enabled = getattr(base.localAvatar, '_clashShortcutCollisionsEnabled', True)
    if enabled:
        base.localAvatar.collisionsOff()
        base.localAvatar._clashShortcutCollisionsEnabled = False
        return 'Collisions have been disabled.'
    base.localAvatar.collisionsOn()
    base.localAvatar._clashShortcutCollisionsEnabled = True
    return 'Collisions have been enabled.'


@magicWord(name='surrounding', category=CATEGORY_PROGRAMMER, types=[])
def clashSurroundingCollisions():
    """Toggles collision traverser bounds."""
    visible = getattr(base, '_clashShortcutTraverserCollisions', False)
    if visible:
        try:
            base.cTrav.hideCollisions()
        except:
            pass
        try:
            base.shadowTrav.hideCollisions()
        except:
            pass
        base._clashShortcutTraverserCollisions = False
        return 'Collision traverser bounds hidden.'
    try:
        base.cTrav.showCollisions(render)
    except:
        pass
    try:
        base.shadowTrav.showCollisions(render)
    except:
        pass
    base._clashShortcutTraverserCollisions = True
    return 'Collision traverser bounds shown.'


@magicWord(name='render', category=CATEGORY_PROGRAMMER, types=[])
def clashRenderCollisions():
    """Toggles all rendered CollisionNode geometry."""
    nodes = render.findAllMatches('**/+CollisionNode')
    visible = getattr(base, '_clashShortcutRenderCollisions', False)
    if visible:
        nodes.hide()
        base._clashShortcutRenderCollisions = False
        return 'Rendered collision bounds hidden.'
    nodes.show()
    base._clashShortcutRenderCollisions = True
    return 'Rendered collision bounds shown.'


@magicWord(name='pstats', category=CATEGORY_PROGRAMMER, types=[])
def clashPstats():
    """Connects the client to Panda3D PStats."""
    if PStatClient is None:
        return 'PStats is unavailable in this Panda3D build.'
    if PStatClient.connect('127.0.0.1', 5185):
        return 'Opened a PStats connection.'
    return 'PStats connection failed.'


def _callBaseToggle(methodName, successText):
    method = getattr(base, methodName, None)
    if method is None:
        return '%s is unavailable in this Panda3D build.' % methodName
    method()
    return successText


@magicWord(name='texture', category=CATEGORY_PROGRAMMER, types=[])
def clashTexture():
    """Toggles texture rendering."""
    return _callBaseToggle('toggleTexture', 'Toggled textures.')


@magicWord(name='vertexcolors', category=CATEGORY_PROGRAMMER, types=[])
def clashVertexColors():
    """Toggles vertex-color rendering."""
    return _callBaseToggle('toggleVertexPainting', 'Toggled vertex colors.')


@magicWord(name='vertexdensity', category=CATEGORY_PROGRAMMER, types=[])
def clashVertexDensity():
    """Toggles vertex-density visualization."""
    return _callBaseToggle('toggleShowVertices', 'Toggled vertex density.')


@magicWord(name='bounds', category=CATEGORY_PROGRAMMER, types=[str])
def clashBounds(mode=''):
    """Toggles model bounds; use tight for tight bounds."""
    if mode.lower() == 'tight':
        return _callBaseToggle('toggleTightBounds', 'Toggled tight bounds.')
    return _callBaseToggle('toggleBounds', 'Toggled bounds.')


@magicWord(name='inverted', category=CATEGORY_PROGRAMMER, types=[])
def clashInverted():
    """Toggles an upside-down camera view."""
    inverted = not getattr(base, '_clashShortcutInverted', False)
    if inverted:
        base._clashShortcutPreviousCameraR = base.cam.getR()
        base.cam.setR(180)
    else:
        base.cam.setR(getattr(base, '_clashShortcutPreviousCameraR', 0))
    base._clashShortcutInverted = inverted
    return 'Upside-down view %s.' % ('enabled' if inverted else 'disabled')


@magicWord(name='stereo', category=CATEGORY_PROGRAMMER, types=[])
def clashStereo():
    """Toggles Altis stereoscopic rendering."""
    base.toggleStereo()
    return 'Toggled stereoscopic rendering.'


@magicWord(name='reloadtextures', category=CATEGORY_PROGRAMMER, types=[])
def clashReloadTextures():
    """Releases prepared graphics objects so textures reload."""
    base.win.getGsg().getPreparedObjects().releaseAll()
    return 'Reloaded prepared textures and graphics objects.'


@magicWord(name='backfaceculling', category=CATEGORY_PROGRAMMER, types=[])
def clashBackfaceCulling():
    """Toggles backface culling."""
    return _callBaseToggle('toggleBackface', 'Toggled backface culling.')


@magicWord(name='frontfaceculling', category=CATEGORY_PROGRAMMER, types=[])
def clashFrontfaceCulling():
    """Toggles frontface culling."""
    return _callBaseToggle('toggleFrontface', 'Toggled frontface culling.')


@magicWord(name='fog', category=CATEGORY_PROGRAMMER, types=[])
def clashFog():
    """Toggles fog rendering."""
    return _callBaseToggle('toggleFog', 'Toggled fog.')


@magicWord(name='particles', category=CATEGORY_PROGRAMMER, types=[])
def clashParticles():
    """Toggles particle rendering."""
    return _callBaseToggle('toggleParticles', 'Toggled particles.')


@magicWord(name='ls', category=CATEGORY_PROGRAMMER, types=[int])
def clashSceneLs(includeRender2d=0):
    """Prints the scene graph tree to the client log."""
    print('--- RENDER ---')
    render.ls()
    if includeRender2d:
        print('--- RENDER2D ---')
        render2d.ls()
    return 'Printed the scene graph to the client log.'


@magicWord(name='analyze', category=CATEGORY_PROGRAMMER, types=[int])
def clashSceneAnalyze(includeRender2d=0):
    """Prints scene graph analysis to the client log."""
    print('--- RENDER ---')
    render.analyze()
    if includeRender2d:
        print('--- RENDER2D ---')
        render2d.analyze()
    return 'Printed scene analysis to the client log.'


@magicWord(name='tobamfile', category=CATEGORY_PROGRAMMER, types=[str])
def clashToBamFile(filename='scene_export'):
    """Exports the current render scene to a BAM file."""
    if not filename.lower().endswith('.bam'):
        filename += '.bam'
    try:
        render.writeBamFile(Filename.fromOsSpecific(filename))
        return 'Wrote %s.' % filename
    except:
        return 'Could not write %s.' % filename


@magicWord(name='loadmodel', category=CATEGORY_PROGRAMMER, types=[str])
def clashLoadModel(modelPath):
    """Loads a model at your Toon's current position."""
    try:
        model = loader.loadModel(modelPath)
    except:
        return 'Invalid model path: %s' % modelPath
    if model is None or model.isEmpty():
        return 'Invalid model path: %s' % modelPath
    parent = render.find('**/clashShortcutLoadedModels')
    if parent.isEmpty():
        parent = render.attachNewNode('clashShortcutLoadedModels')
    model.reparentTo(parent)
    model.setPos(base.localAvatar.getPos(render))
    return 'Loaded model: %s' % modelPath


@magicWord(name='spam', category=CATEGORY_PROGRAMMER, types=[])
def clashNotifySpam():
    """Enables verbose DirectNotify output."""
    from direct.directnotify import DirectNotifyGlobal
    DirectNotifyGlobal.directNotify.setVerbose()
    return 'Verbose notify output enabled.'
