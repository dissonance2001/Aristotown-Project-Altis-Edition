from __future__ import absolute_import
from __future__ import print_function
from pandac.PandaModules import *
import six.moves.builtins
import json
import random
import six


class ContentPackCompatibility:
    _musicJsonCache = {}

    _hqLobbyMusicKeys = {
        'phase_9/audio/bgm/sb_boss_lobby.ogg': 'sellbot_lobby',
        'phase_10/audio/bgm/cb_boss_lobby.ogg': 'cashbot_lobby',
        'phase_11/audio/bgm/lb_boss_lobby.ogg': 'lawbot_lobby',
        'phase_12/audio/bgm/bb_boss_lobby.ogg': 'bossbot_lobby'
    }

    @staticmethod
    def getManager():
        try:
            return six.moves.builtins.ContentPackMgr
        except Exception:
            return None

    @staticmethod
    def resolveMountedFile(relativePath):
        manager = ContentPackCompatibility.getManager()
        if not manager:
            return None

        try:
            mountPoints = manager.mountPoints
        except Exception:
            return None

        relativePath = str(relativePath).replace('\\', '/').lstrip('/')
        vfs = VirtualFileSystem.getGlobalPtr()

        for mountPoint in reversed(mountPoints):
            candidate = Filename(
                '%s/%s' % (
                    str(mountPoint).rstrip('/'),
                    relativePath
                )
            )

            if vfs.exists(candidate):
                return str(candidate)

        return None

    @staticmethod
    def resolveFontPath(fontPath):
        requestedPath = str(fontPath).replace('\\', '/').lstrip('/')

        searchPaths = [requestedPath]

        altisFontPrefix = 'phase_3/models/fonts/'
        if requestedPath.startswith(altisFontPrefix):
            fontName = requestedPath[len(altisFontPrefix):]

            clashPath = 'phase_3/fonts/' + fontName
            searchPaths.insert(0, clashPath)

            if '.' not in fontName:
                searchPaths.insert(0, clashPath + '.ttf')

        for searchPath in searchPaths:
            resolvedPath = ContentPackCompatibility.resolveMountedFile(
                searchPath
            )

            if resolvedPath:
                print('CONTENT PACK: Resolved font %s to %s' % (
                    requestedPath,
                    resolvedPath
                ))
                return resolvedPath

        return fontPath

    @staticmethod
    def _getMountPoints():
        manager = ContentPackCompatibility.getManager()
        if not manager:
            return []

        try:
            return list(manager.mountPoints)
        except Exception:
            return []

    @staticmethod
    def _loadMusicJsonForMount(mountPoint):
        cacheKey = str(mountPoint)
        if cacheKey in ContentPackCompatibility._musicJsonCache:
            return ContentPackCompatibility._musicJsonCache[cacheKey]

        vfs = VirtualFileSystem.getGlobalPtr()
        musicData = None

        jsonPaths = (
            'audio/music.json',
            'phase_3/audio/music.json',
            'music.json'
        )

        for jsonPath in jsonPaths:
            candidate = Filename(
                '%s/%s' % (
                    str(mountPoint).rstrip('/'),
                    jsonPath
                )
            )

            if not vfs.exists(candidate):
                continue

            try:
                rawData = vfs.readFile(candidate, True)
                parsedData = json.loads(rawData)

                if isinstance(parsedData, dict):
                    musicData = parsedData
                    print('CONTENT PACK: Loaded music mappings from %s' % (
                        candidate
                    ))
                    break

                print('CONTENT PACK ERROR: %s is not a JSON object' % (
                    candidate
                ))
            except Exception as error:
                print('CONTENT PACK ERROR: Failed to read %s: %s' % (
                    candidate,
                    error
                ))

        ContentPackCompatibility._musicJsonCache[cacheKey] = musicData
        return musicData

    @staticmethod
    def _getActiveMusicSeasons():
        seasons = []

        try:
            season = str(base.currHoliday)
            if season and season != 'None':
                seasons.append(season)
        except Exception:
            pass

        if 'default' not in seasons:
            seasons.append('default')

        return seasons

    @staticmethod
    def _getMusicMappingValue(musicData, musicKey):
        if not isinstance(musicData, dict):
            return None

        for season in ContentPackCompatibility._getActiveMusicSeasons():
            seasonData = musicData.get(season)
            if isinstance(seasonData, dict) and musicKey in seasonData:
                return seasonData[musicKey]

        # Keep compatibility with older/simple packs that put keys at root.
        if musicKey in musicData:
            return musicData[musicKey]

        return None

    @staticmethod
    def _getPackLabel(mountPoint):
        manager = ContentPackCompatibility.getManager()
        if not manager:
            return str(mountPoint)

        try:
            index = list(manager.mountPoints).index(mountPoint)
        except Exception:
            return str(mountPoint)

        try:
            if index < len(manager.sort):
                return str(manager.sort[index])
        except Exception:
            pass

        return str(mountPoint)

    @staticmethod
    def _chooseMusicPath(value):
        if isinstance(value, six.string_types):
            return value

        if isinstance(value, (list, tuple)):
            choices = [
                item for item in value
                if isinstance(item, six.string_types) and item
            ]
            if choices:
                return random.choice(choices)
            return None

        # Some packs use a small object for a default/non-holiday track.
        if isinstance(value, dict):
            for key in ('default', 'normal', 'path', 'file', 'music'):
                if key in value:
                    return ContentPackCompatibility._chooseMusicPath(
                        value[key]
                    )

        return None

    @staticmethod
    def _resolvePathInsideMount(mountPoint, relativePath):
        requestedPath = str(relativePath).replace('\\', '/').lstrip('/')
        if requestedPath.startswith('./'):
            requestedPath = requestedPath[2:]

        searchPaths = [requestedPath]

        # A bare filename is treated as being next to audio/music.json.
        if '/' not in requestedPath:
            searchPaths.insert(0, 'audio/' + requestedPath)

        vfs = VirtualFileSystem.getGlobalPtr()

        for searchPath in searchPaths:
            candidate = Filename(
                '%s/%s' % (
                    str(mountPoint).rstrip('/'),
                    searchPath
                )
            )

            if vfs.exists(candidate):
                return str(candidate)

        return None

    @staticmethod
    def resolveAudioPath(audioPath):
        requestedPath = str(audioPath).replace('\\', '/').lstrip('/')
        normalizedPath = requestedPath.lower()

        musicKey = ContentPackCompatibility._hqLobbyMusicKeys.get(
            normalizedPath
        )
        mountPoints = ContentPackCompatibility._getMountPoints()
        vfs = VirtualFileSystem.getGlobalPtr()

        # Check each enabled pack as one priority unit. No pack names are
        # hard-coded. Later YAML entries have higher priority.
        for mountPoint in reversed(mountPoints):
            packLabel = ContentPackCompatibility._getPackLabel(mountPoint)

            if musicKey:
                musicData = (
                    ContentPackCompatibility
                    ._loadMusicJsonForMount(mountPoint)
                )
                mappingValue = (
                    ContentPackCompatibility._getMusicMappingValue(
                        musicData,
                        musicKey
                    )
                )

                if mappingValue is not None:
                    musicPath = ContentPackCompatibility._chooseMusicPath(
                        mappingValue
                    )
                    if musicPath == 'None':
                        return musicPath
                    if musicPath:
                        resolvedMusicPath = (
                            ContentPackCompatibility
                            ._resolvePathInsideMount(mountPoint, musicPath)
                        )
                        if resolvedMusicPath:
                            return resolvedMusicPath
                        return musicPath

            directCandidate = Filename('%s/%s' % (
                str(mountPoint).rstrip('/'),
                requestedPath
            ))
            if vfs.exists(directCandidate):
                return str(directCandidate)

        return audioPath

    @staticmethod
    def _loadClashGagAtlases():
        clashPaths = {
            1: 'phase_3.5/maps/prop_icons_palette_4amlc_1.png',
            2: 'phase_3.5/maps/prop_icons_palette_4amlc_2.png',
            3: 'phase_3.5/maps/prop_icons_palette_4amlc_3.png',
            4: 'phase_3.5/maps/prop_icons_palette_4amlc_4.png'
        }

        textures = {}
        images = {}

        for index in (1, 2, 3, 4):
            texture = TexturePool.loadTexture(
                Filename(clashPaths[index])
            )

            if not texture:
                return None

            image = PNMImage()
            if not texture.store(image):
                return None

            textures[index] = texture
            images[index] = image

        return textures, images

    @staticmethod
    def buildAltisCompatibleClashGagTextures():
        loaded = ContentPackCompatibility._loadClashGagAtlases()
        if not loaded:
            return None

        textures, images = loaded

        width = images[3].getXSize()
        height = images[3].getYSize()

        if width != images[4].getXSize():
            return None

        if height != images[4].getYSize():
            return None

        if height % 2:
            return None

        halfHeight = height / 2

        altisAtlas3 = PNMImage(
            width,
            height,
            images[3].getNumChannels()
        )
        altisAtlas4 = PNMImage(
            width,
            height,
            images[4].getNumChannels()
        )

        altisAtlas3.copySubImage(
            images[4],
            0, 0,
            0, 0,
            width, halfHeight
        )

        altisAtlas3.copySubImage(
            images[3],
            0, halfHeight,
            0, 0,
            width, halfHeight
        )

        altisAtlas4.copySubImage(
            images[3],
            0, 0,
            0, halfHeight,
            width, halfHeight
        )

        altisAtlas4.copySubImage(
            images[4],
            0, halfHeight,
            0, halfHeight,
            width, halfHeight
        )

        fixedTexture3 = Texture(
            'content-pack-altis-gag-icons-3'
        )
        fixedTexture4 = Texture(
            'content-pack-altis-gag-icons-4'
        )

        fixedTexture3.load(altisAtlas3)
        fixedTexture4.load(altisAtlas4)

        return {
            'gag_icons_1': textures[1],
            'gag_icons_2': textures[2],
            'gag_icons_3': fixedTexture3,
            'gag_icons_4': fixedTexture4
        }

    @staticmethod
    def applyClashGagIconCompatibility(model):
        if not model or model.isEmpty():
            return

        replacements = (
            ContentPackCompatibility
            .buildAltisCompatibleClashGagTextures()
        )

        if not replacements:
            return

        try:
            oldTextures = model.findAllTextures()
        except Exception as error:
            print('CONTENT PACK ERROR: findAllTextures failed:', error)
            return

        replaced = 0

        for oldTexture in oldTextures:
            textureKey = ''

            try:
                filename = oldTexture.getFilename().getBasename()
                textureKey = filename.rsplit('.', 1)[0].lower()
            except Exception:
                pass

            if not textureKey:
                try:
                    textureKey = oldTexture.getName().lower()
                except Exception:
                    continue

            newTexture = replacements.get(textureKey)
            if not newTexture:
                continue

            try:
                model.replaceTexture(oldTexture, newTexture)
                replaced += 1
            except Exception as error:
                print('CONTENT PACK ERROR: replaceTexture failed:', error)

        print((
            'CONTENT PACK: Applied Altis track order to %s '
            'gag atlas texture(s)' % replaced
        ))

    @staticmethod
    def applyStatusEffectsCompatibility(model):
        if not model or model.isEmpty():
            return

        replacementPaths = {
            'status_effects_palette_4allc_1':
                'phase_3.5/maps/status_effects_palette_4allc_1.png',
            'status_effects_palette_4allc_2':
                'phase_3.5/maps/status_effects_palette_4allc_2.png'
        }

        replacements = {}

        for textureKey, relativePath in replacementPaths.items():
            resolvedPath = ContentPackCompatibility.resolveMountedFile(
                relativePath
            )

            if not resolvedPath:
                continue

            replacementTexture = TexturePool.loadTexture(
                Filename(resolvedPath)
            )

            if replacementTexture:
                replacements[textureKey] = replacementTexture

        if not replacements:
            return

        try:
            oldTextures = model.findAllTextures()
        except Exception as error:
            print('CONTENT PACK ERROR: status effects findAllTextures failed:', error)
            return

        replaced = 0

        for oldTexture in oldTextures:
            textureKey = ''

            try:
                filename = oldTexture.getFilename().getBasename()
                textureKey = filename.rsplit('.', 1)[0].lower()
            except Exception:
                pass

            if not textureKey:
                try:
                    textureKey = oldTexture.getName().lower()
                except Exception:
                    continue

            newTexture = replacements.get(textureKey)
            if not newTexture:
                continue

            try:
                model.replaceTexture(oldTexture, newTexture)
                replaced += 1
            except Exception as error:
                print('CONTENT PACK ERROR: status effects replaceTexture failed:', error)

        if replaced:
            print((
                'CONTENT PACK: Replaced %s status effect atlas texture(s)' %
                replaced
            ))
