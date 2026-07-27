from pandac.PandaModules import *
import __builtin__


class ContentPackCompatibility:
    @staticmethod
    def getManager():
        try:
            return __builtin__.ContentPackMgr
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
                print 'CONTENT PACK: Resolved font %s to %s' % (
                    requestedPath,
                    resolvedPath
                )
                return resolvedPath

        return fontPath

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
            print 'CONTENT PACK ERROR: findAllTextures failed:', error
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
                print 'CONTENT PACK ERROR: replaceTexture failed:', error

        print (
            'CONTENT PACK: Applied Altis track order to %s '
            'gag atlas texture(s)' % replaced
        )

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
            print 'CONTENT PACK ERROR: status effects findAllTextures failed:', error
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
                print 'CONTENT PACK ERROR: status effects replaceTexture failed:', error

        if replaced:
            print (
                'CONTENT PACK: Replaced %s status effect atlas texture(s)' %
                replaced
            )

