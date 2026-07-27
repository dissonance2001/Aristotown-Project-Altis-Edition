from pandac.PandaModules import *
from direct.directnotify.DirectNotifyGlobal import *
from direct.showbase import Loader as nLoader
from toontown.toontowngui import ToontownLoadingScreen
from toontown.dna.DNAParser import *
import traceback
import __builtin__

class ToontownLoader(nLoader.Loader):
    TickPeriod = 0.1

    def __init__(self, base):
        nLoader.Loader.__init__(self, base)
        self.inBulkBlock = None
        self.blockName = None
        self.loadingScreen = ToontownLoadingScreen.ToontownLoadingScreen()

    def destroy(self):
        self.loadingScreen.destroy()
        del self.loadingScreen
        nLoader.Loader.destroy(self)

    def loadDNAFile(self, dnastore, filename):
        return loadDNAFile(dnastore, filename)

    def beginBulkLoad(self, name, label, range, gui, tipCategory, zoneId):
        self._loadStartT = globalClock.getRealTime()
        nLoader.Loader.notify.info("starting bulk load of block '%s'" % name)
        if self.inBulkBlock:
            Loader.Loader.notify.warning("Tried to start a block ('%s'), but am already in a block ('%s')" % (name, self.blockName))
            return
        
        self.inBulkBlock = 1
        self._lastTickT = globalClock.getRealTime()
        self.blockName = name
        self.loadingScreen.begin(range, label, gui, tipCategory, zoneId)
         
    def endBulkLoad(self, name):
        if not self.inBulkBlock:
            nLoader.Loader.notify.warning("Tried to end a block ('%s'), but not in one" % name)
            return
        
        if name != self.blockName:
            nLoader.Loader.notify.warning("Tried to end a block ('%s'), other then the current one ('%s')" % (name, self.blockName))
            return
        
        self.inBulkBlock = None
        expectedCount, loadedCount = self.loadingScreen.end()
        now = globalClock.getRealTime()
        nLoader.Loader.notify.info("At end of block '%s', expected %s, loaded %s, duration=%s" % (self.blockName,
         expectedCount,
         loadedCount,
         now - self._loadStartT))

    def abortBulkLoad(self):
        if self.inBulkBlock:
            nLoader.Loader.notify.info("Aborting block ('%s')" % self.blockName)
            self.inBulkBlock = None
            self.loadingScreen.abort()

    def tick(self):
        if self.inBulkBlock:
            now = globalClock.getRealTime()
            if now - self._lastTickT > self.TickPeriod:
                self._lastTickT += self.TickPeriod
                self.loadingScreen.tick()
                if hasattr(base, 'cr'):
                    base.cr.considerHeartbeat()

    def _buildAltisCompatibleClashGagTextures(self):
        clashPaths = {
            1: 'phase_3.5/maps/prop_icons_palette_4amlc_1.png',
            2: 'phase_3.5/maps/prop_icons_palette_4amlc_2.png',
            3: 'phase_3.5/maps/prop_icons_palette_4amlc_3.png',
            4: 'phase_3.5/maps/prop_icons_palette_4amlc_4.png'
        }

        textures = {}
        images = {}

        for index in (1, 2, 3, 4):
            texture = TexturePool.loadTexture(Filename(clashPaths[index]))
            if not texture:
                print 'CONTENT PACK ERROR: Could not load:', clashPaths[index]
                return None

            image = PNMImage()
            if not texture.store(image):
                print 'CONTENT PACK ERROR: Could not read texture data:', clashPaths[index]
                return None

            textures[index] = texture
            images[index] = image

        width = images[3].getXSize()
        height = images[3].getYSize()

        if width != images[4].getXSize() or height != images[4].getYSize():
            print 'CONTENT PACK ERROR: Gag atlases 3 and 4 have different sizes'
            return None

        if height % 2:
            print 'CONTENT PACK ERROR: Gag atlas height is not divisible by 2'
            return None

        halfHeight = height / 2

        # Clash:
        #   atlas 3 = Squirt / Zap
        #   atlas 4 = Throw  / Drop
        #
        # Altis inventory_icons.bam expects:
        #   atlas 3 = Throw  / Squirt
        #   atlas 4 = Zap    / Drop
        altisAtlas3 = PNMImage(width, height, images[3].getNumChannels())
        altisAtlas4 = PNMImage(width, height, images[4].getNumChannels())

        # Atlas 3 top: Throw from Clash atlas 4 top.
        altisAtlas3.copySubImage(
            images[4],
            0, 0,
            0, 0,
            width, halfHeight
        )

        # Atlas 3 bottom: Squirt from Clash atlas 3 top.
        altisAtlas3.copySubImage(
            images[3],
            0, halfHeight,
            0, 0,
            width, halfHeight
        )

        # Atlas 4 top: Zap from Clash atlas 3 bottom.
        altisAtlas4.copySubImage(
            images[3],
            0, 0,
            0, halfHeight,
            width, halfHeight
        )

        # Atlas 4 bottom: Drop from Clash atlas 4 bottom.
        altisAtlas4.copySubImage(
            images[4],
            0, halfHeight,
            0, halfHeight,
            width, halfHeight
        )

        fixedTexture3 = Texture('content-pack-altis-gag-icons-3')
        fixedTexture4 = Texture('content-pack-altis-gag-icons-4')

        fixedTexture3.load(altisAtlas3)
        fixedTexture4.load(altisAtlas4)

        return {
            'gag_icons_1': textures[1],
            'gag_icons_2': textures[2],
            'gag_icons_3': fixedTexture3,
            'gag_icons_4': fixedTexture4
        }

    def _applyClashGagIconCompatibility(self, model):
        if not model or model.isEmpty():
            return

        replacements = self._buildAltisCompatibleClashGagTextures()
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

        print 'CONTENT PACK: Applied Altis track order to %s gag atlas texture(s)' % replaced

    def loadModel(self, *args, **kw):
        ret = nLoader.Loader.loadModel(self, *args, **kw)

        modelName = ''
        if args:
            try:
                modelName = str(args[0]).replace('\\', '/').lower()
            except Exception:
                modelName = ''

        if ret and 'inventory_icons' in modelName:
            self._applyClashGagIconCompatibility(ret)

        if ret:
            gsg = base.win.getGsg()
            if gsg:
                ret.prepareScene(gsg)

        self.tick()
        return ret

    def _findContentPackFont(self, requestedPath):
        path = str(requestedPath).replace('\\', '/')

        clashFontMap = {
            'phase_3/models/fonts/ImpressBT.ttf':
                'phase_3/fonts/ImpressBT.ttf',
            'phase_3/models/fonts/MinnieFont':
                'phase_3/fonts/MinnieFont.ttf',
            'phase_3/models/fonts/MinnieFont.ttf':
                'phase_3/fonts/MinnieFont.ttf'
        }

        replacementPath = clashFontMap.get(path)
        if not replacementPath:
            return None

        try:
            manager = __builtin__.ContentPackMgr
            mountPoints = manager.mountPoints
        except Exception:
            return None

        vfs = VirtualFileSystem.getGlobalPtr()

        for mountPoint in reversed(mountPoints):
            candidate = Filename(
                '%s/%s' % (
                    str(mountPoint).rstrip('/'),
                    replacementPath
                )
            )

            if vfs.exists(candidate):
                return candidate

        return None

    def loadFont(self, *args, **kw):
        ret = None

        if args:
            contentPackFont = self._findContentPackFont(args[0])

            if contentPackFont:
                newArgs = list(args)
                newArgs[0] = contentPackFont

                try:
                    ret = nLoader.Loader.loadFont(
                        self,
                        *tuple(newArgs),
                        **kw
                    )
                    print 'CONTENT PACK: Loaded Clash font override:', contentPackFont
                except Exception as error:
                    print 'CONTENT PACK ERROR: Clash font override failed:', error
                    ret = None

        if not ret:
            ret = nLoader.Loader.loadFont(self, *args, **kw)

        self.tick()
        return ret

    def loadTexture(self, texturePath, alphaPath = None, okMissing = False):
        ret = nLoader.Loader.loadTexture(self, texturePath, alphaPath, okMissing=okMissing)
        self.tick()
        if alphaPath:
            self.tick()
        
        return ret

    def playSfx(self, *args, **kw):
        ret = base.playSfx(*args, **kw)
        self.tick()
        return ret

    def pdnaModel(self, *args, **kw):
        ret = nLoader.Loader.loadModel(self, *args, **kw)

        modelName = ''
        if args:
            try:
                modelName = str(args[0]).replace('\\', '/').lower()
            except Exception:
                modelName = ''

        if ret and 'inventory_icons' in modelName:
            self._applyClashGagIconCompatibility(ret)

        if ret:
            gsg = base.win.getGsg()
            if gsg:
                ret.prepareScene(gsg)
        self.tick()
        return ret

    def pdnaFont(self, *args, **kw):
        ret = None

        if args:
            contentPackFont = self._findContentPackFont(args[0])

            if contentPackFont:
                newArgs = list(args)
                newArgs[0] = contentPackFont

                try:
                    ret = nLoader.Loader.loadFont(
                        self,
                        *tuple(newArgs),
                        **kw
                    )
                    print 'CONTENT PACK: Loaded Clash PDNA font override:', contentPackFont
                except Exception as error:
                    print 'CONTENT PACK ERROR: Clash PDNA font override failed:', error
                    ret = None

        if not ret:
            ret = nLoader.Loader.loadFont(self, *args, **kw)

        self.tick()
        return ret

    def pdnaTexture(self, texturePath, alphaPath = None, okMissing = False):
        ret = nLoader.Loader.loadTexture(self, texturePath, alphaPath, okMissing=okMissing)
        self.tick()
        return ret

    def loadSfx(self, soundPath):
        ret = nLoader.Loader.loadSfx(self, soundPath)
        self.tick()
        return ret

    def loadMusic(self, soundPath):
        ret = nLoader.Loader.loadMusic(self, soundPath)
        self.tick()
        return ret