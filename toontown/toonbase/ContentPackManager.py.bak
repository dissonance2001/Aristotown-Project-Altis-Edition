'''
Project Altis content pack manager.

Content packs keep Altis's Panda 2-compatible private VFS mount roots. Packs
later in pack-load-order.yaml have higher priority.

A pack can optionally be marked music-only or sfx-only. This is useful for
legacy soundtrack packs that contain copied default SFX: they can continue to
supply music without overriding button sounds. Packs without a role remain
unrestricted, so one combined pack can still provide music, SFX, models,
textures, fonts, and other assets at the same time.
'''
from direct.directnotify.DirectNotifyGlobal import directNotify
from panda3d.core import Multifile, Filename, VirtualFileSystem, getModelPath
import fnmatch
import os
from toontown.pandautils import yaml


class ContentPackManager:
    notify = directNotify.newCategory('ContentPackManager')

    def __init__(self):
        self.packPath = 'resources/contentpacks/'
        if not os.path.exists(self.packPath):
            os.makedirs(self.packPath)

        self.sortFile = os.path.join(self.packPath, 'pack-load-order.yaml')
        if not os.path.exists(self.sortFile):
            open(self.sortFile, 'a').close()

        self.vfSys = VirtualFileSystem.getGlobalPtr()
        self.modelPath = getModelPath()

        self.sort = []
        self.musicOnly = []
        self.sfxOnly = []
        self.mountedPacks = []
        self.mountPoints = []
        self.packEntries = []
        self.mountIndex = 0

        # Retained for compatibility with Clash-style music.json readers.
        self.overrideMusicData = {}

    def _normaliseFilename(self, filename):
        return str(filename).replace('\\', '/').strip().lstrip('/')

    def _normaliseVirtualPath(self, path):
        return str(path).replace('\\', '/').lstrip('/')

    def _normaliseList(self, value):
        if value is None:
            return []
        if isinstance(value, basestring):
            value = [value]
        if not isinstance(value, (list, tuple)):
            return []

        result = []
        seen = set()
        for filename in value:
            if not isinstance(filename, basestring):
                continue
            filename = self._normaliseFilename(filename)
            if not filename:
                continue
            key = filename.lower()
            if key in seen:
                continue
            seen.add(key)
            result.append(filename)
        return result

    def _readSortFile(self):
        with open(self.sortFile, 'r') as sortFile:
            config = yaml.load(sortFile) or []

        if isinstance(config, dict):
            self.sort = self._normaliseList(
                config.get('packs', config.get('load-order', []))
            )
            self.musicOnly = self._normaliseList(
                config.get('music-only', config.get('music_only', []))
            )
            self.sfxOnly = self._normaliseList(
                config.get('sfx-only', config.get('sfx_only', []))
            )
        else:
            # Backwards compatibility with the original plain YAML list.
            self.sort = self._normaliseList(config)
            self.musicOnly = []
            self.sfxOnly = []

    def _containsFilename(self, filenames, filename):
        wanted = self._normaliseFilename(filename).lower()
        wantedBase = os.path.basename(wanted)
        for current in filenames:
            current = self._normaliseFilename(current).lower()
            if current == wanted or os.path.basename(current) == wantedBase:
                return True
        return False

    def _removeRoleReference(self, filename):
        key = self._normaliseFilename(filename).lower()
        base = os.path.basename(key)

        def keep(current):
            current = self._normaliseFilename(current).lower()
            return current != key and os.path.basename(current) != base

        self.musicOnly = [item for item in self.musicOnly if keep(item)]
        self.sfxOnly = [item for item in self.sfxOnly if keep(item)]

    def _writeYamlList(self, sortFile, key, values):
        if not values:
            sortFile.write('%s: []\n' % key)
            return

        sortFile.write('%s:\n' % key)
        for filename in values:
            sortFile.write("  - '%s'\n" % filename.replace("'", "''"))

    def _writeSortFile(self):
        with open(self.sortFile, 'w') as sortFile:
            sortFile.write(
                '# Entries lower in packs have higher normal priority.\n'
                '# music-only packs are ignored for SFX lookups.\n'
                '# sfx-only packs are ignored for music lookups.\n'
                '# Unlisted packs remain unrestricted and can contain everything.\n'
            )
            self._writeYamlList(sortFile, 'packs', self.sort)
            sortFile.write('\n')
            self._writeYamlList(sortFile, 'music-only', self.musicOnly)
            sortFile.write('\n')
            self._writeYamlList(sortFile, 'sfx-only', self.sfxOnly)

    def loadAll(self):
        self._readSortFile()
        loadedCount = 0

        print('Content Pack Manager: reading %s' % self.sortFile)
        print('Content Pack Manager: %s listed pack(s)' % len(self.sort))

        for filename in self.sort[:]:
            if not self.isValid(filename):
                self.notify.warning(
                    'Removing missing content pack from load order: %s' %
                    filename
                )
                self.sort.remove(filename)
                self._removeRoleReference(filename)
                continue

            if self.applyFile(filename):
                loadedCount += 1

        # Discover valid packs not yet listed.
        for root, _, filenames in os.walk(self.packPath):
            relativeRoot = root[len(self.packPath):]
            for filename in filenames:
                filename = os.path.join(relativeRoot, filename).replace('\\', '/')

                if self._containsFilename(self.sort, filename):
                    continue
                if not self.isValid(filename):
                    continue

                if self.applyFile(filename):
                    self.sort.append(filename)
                    loadedCount += 1

        self._writeSortFile()

        print('Loaded %s content pack(s).' % loadedCount)
        print('Content pack model path: %s' % self.modelPath)
        print('Content pack priority: later YAML entries override earlier entries.')
        if self.musicOnly:
            print('Content pack music-only role: %s' % ', '.join(self.musicOnly))
        if self.sfxOnly:
            print('Content pack SFX-only role: %s' % ', '.join(self.sfxOnly))

        self._printGuiSfxResolution()

    def isValid(self, filename):
        fullPath = os.path.join(self.packPath, filename)
        if not os.path.isfile(fullPath):
            return False
        return fnmatch.fnmatch(os.path.basename(filename).lower(), '*.mf')

    def _buildSubfileMap(self, multifile):
        subfiles = {}
        for index in xrange(multifile.getNumSubfiles()):
            realName = self._normaliseVirtualPath(
                multifile.getSubfileName(index)
            )
            subfiles[realName.lower()] = realName
        return subfiles

    def applyFile(self, filename):
        filename = self._normaliseFilename(filename)
        fullPath = os.path.abspath(os.path.join(self.packPath, filename))
        packFilename = Filename.fromOsSpecific(fullPath)

        multifile = Multifile()
        if not multifile.openRead(packFilename):
            self.notify.warning('Failed to open content pack: %s' % filename)
            return False

        mountPoint = Filename('/__contentpacks__/%04d' % self.mountIndex)
        self.mountIndex += 1

        if not self.vfSys.mount(
                multifile,
                mountPoint,
                VirtualFileSystem.MFReadOnly):
            self.notify.warning('Failed to mount content pack: %s' % filename)
            multifile.close()
            return False

        self.modelPath.prependDirectory(mountPoint)

        entry = {
            'filename': filename,
            'mountPoint': mountPoint,
            'multifile': multifile,
            'subfiles': self._buildSubfileMap(multifile)
        }
        self.mountedPacks.append(multifile)
        self.mountPoints.append(mountPoint)
        self.packEntries.append(entry)

        print(
            'Successfully Mounted Content Pack: %s (%s files at %s)' % (
                filename,
                multifile.getNumSubfiles(),
                mountPoint
            )
        )
        return True

    def _findPackEntry(self, packName):
        requested = self._normaliseFilename(packName).lower()
        requestedBase = os.path.basename(requested)

        for entry in reversed(self.packEntries):
            current = entry['filename'].lower()
            if current == requested or os.path.basename(current) == requestedBase:
                return entry
        return None

    def _entryHasRole(self, entry, roleList):
        return self._containsFilename(roleList, entry['filename'])

    def _entryAllowsCategory(self, entry, category):
        if category == 'sfx' and self._entryHasRole(entry, self.musicOnly):
            return False
        if category == 'music' and self._entryHasRole(entry, self.sfxOnly):
            return False
        return True

    def resolveFileFromPack(self, packName, virtualPath):
        entry = self._findPackEntry(packName)
        if not entry:
            return virtualPath

        requested = self._normaliseVirtualPath(virtualPath)
        realName = entry['subfiles'].get(requested.lower())
        if realName is None:
            return virtualPath

        candidate = Filename('%s/%s' % (
            str(entry['mountPoint']).rstrip('/'),
            realName
        ))
        if self.vfSys.exists(candidate):
            return str(candidate)
        return virtualPath

    def _resolveEntry(self, virtualPath, category=None):
        requested = self._normaliseVirtualPath(virtualPath)
        requestedKey = requested.lower()

        for entry in reversed(self.packEntries):
            if not self._entryAllowsCategory(entry, category):
                continue

            realName = entry['subfiles'].get(requestedKey)
            if realName is None:
                continue

            candidate = Filename('%s/%s' % (
                str(entry['mountPoint']).rstrip('/'),
                realName
            ))
            if self.vfSys.exists(candidate):
                return entry, str(candidate)

        return None, virtualPath

    def resolveFile(self, virtualPath, category=None):
        if virtualPath is None:
            return virtualPath

        rawPath = str(virtualPath).replace('\\', '/')
        lowerPath = rawPath.lower()
        if lowerPath.startswith('/__contentpacks__/'):
            return virtualPath
        if lowerPath.startswith('__contentpacks__/'):
            return virtualPath
        if len(rawPath) > 2 and rawPath[1] == ':':
            return virtualPath

        _, resolved = self._resolveEntry(rawPath, category)
        if resolved != rawPath or category != 'music':
            return resolved

        requested = self._normaliseVirtualPath(rawPath)
        requestedBase = os.path.basename(requested).lower()
        sellbotMusic = (
            'sb_courtyard.ogg',
            'sb_courtyard_encntr.ogg',
            'sb_factory_ext.ogg',
            'sb_factory_ext_encntr.ogg',
            'sb_boss_lobby.ogg'
        )
        if requestedBase not in sellbotMusic:
            return resolved

        for entry in reversed(self.packEntries):
            if not self._entryAllowsCategory(entry, category):
                continue
            for realName in entry['subfiles'].values():
                if os.path.basename(realName).lower() != requestedBase:
                    continue
                candidate = Filename('%s/%s' % (
                    str(entry['mountPoint']).rstrip('/'),
                    realName
                ))
                if self.vfSys.exists(candidate):
                    return str(candidate)

        return resolved

    def _printGuiSfxResolution(self):
        paths = (
            'phase_3/audio/sfx/GUI_rollover.ogg',
            'phase_3/audio/sfx/GUI_create_toon_fwd.ogg',
            'phase_3/audio/sfx/GUI_create_toon_back.ogg'
        )

        for path in paths:
            providers = []
            skipped = []
            key = path.lower()

            for entry in reversed(self.packEntries):
                if key not in entry['subfiles']:
                    continue
                if not self._entryAllowsCategory(entry, 'sfx'):
                    skipped.append(entry['filename'])
                else:
                    providers.append(entry['filename'])

            if providers:
                print(
                    'CONTENT PACK GUI SFX: %s -> %s' %
                    (path, providers[0])
                )
            else:
                print('CONTENT PACK GUI SFX: %s -> default Altis' % path)

            if skipped:
                print(
                    'CONTENT PACK GUI SFX: skipped music-only provider(s): %s' %
                    ', '.join(skipped)
                )

    def resolveMountedFile(self, virtualPath):
        resolved = self.resolveFile(virtualPath)
        if str(resolved) == str(virtualPath):
            return None
        return resolved

    def resolveSelectiveAudioOverride(self, virtualPath):
        # Compatibility with Build 29/30 callers. No pack name is hard-coded.
        resolved = self.resolveMountedFile(virtualPath)
        if resolved:
            return resolved
        return virtualPath

    def resolveMusic(self, virtualPath):
        return self.resolveFile(virtualPath, 'music')

    def resolveSfx(self, virtualPath):
        return self.resolveFile(virtualPath, 'sfx')
