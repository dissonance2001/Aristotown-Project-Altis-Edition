'''
Created on Feb 19, 2017

@author: Drew
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

        self.sortFile = os.path.join(
            self.packPath,
            'pack-load-order.yaml'
        )
        if not os.path.exists(self.sortFile):
            open(self.sortFile, 'a').close()

        self.vfSys = VirtualFileSystem.getGlobalPtr()
        self.modelPath = getModelPath()

        self.sort = []
        self.mountedPacks = []
        self.mountPoints = []
        self.mountIndex = 0

    def loadAll(self):
        with open(self.sortFile, 'r') as sortFile:
            self.sort = yaml.load(sortFile) or []

        loadedCount = 0

        for filename in self.sort[:]:
            if not self.isValid(filename):
                self.notify.warning(
                    'Removing missing content pack from load order: %s' %
                    filename
                )
                self.sort.remove(filename)
                continue

            if self.applyFile(filename):
                loadedCount += 1

        for root, _, filenames in os.walk(self.packPath):
            relativeRoot = root[len(self.packPath):]

            for filename in filenames:
                filename = os.path.join(
                    relativeRoot,
                    filename
                ).replace('\\', '/')

                if filename in self.sort:
                    continue

                if not self.isValid(filename):
                    continue

                if self.applyFile(filename):
                    self.sort.append(filename)
                    loadedCount += 1

        with open(self.sortFile, 'w') as sortFile:
            for filename in self.sort:
                sortFile.write('- %s\n' % filename)

        print('Loaded %s content pack(s).' % loadedCount)
        print('Content pack model path: %s' % self.modelPath)

    def isValid(self, filename):
        fullPath = os.path.join(self.packPath, filename)
        if not os.path.isfile(fullPath):
            return False

        return fnmatch.fnmatch(
            os.path.basename(filename).lower(),
            '*.mf'
        )

    def applyFile(self, filename):
        fullPath = os.path.abspath(
            os.path.join(self.packPath, filename)
        )
        packFilename = Filename.fromOsSpecific(fullPath)

        multifile = Multifile()
        if not multifile.openRead(packFilename):
            self.notify.warning(
                'Failed to open content pack: %s' % filename
            )
            return False

        # Give every pack its own root. This avoids Panda's ambiguous
        # duplicate-file behaviour when many Multifiles share one mount point.
        mountPoint = Filename(
            '/__contentpacks__/%04d' % self.mountIndex
        )
        self.mountIndex += 1

        if not self.vfSys.mount(
                multifile,
                mountPoint,
                VirtualFileSystem.MFReadOnly):
            self.notify.warning(
                'Failed to mount content pack: %s' % filename
            )
            multifile.close()
            return False

        # prependDirectory means packs loaded later take priority.
        self.modelPath.prependDirectory(mountPoint)

        self.mountedPacks.append(multifile)
        self.mountPoints.append(mountPoint)

        print(
            'Successfully Mounted Content Pack: %s '
            '(%s files at %s)' % (
                filename,
                multifile.getNumSubfiles(),
                mountPoint
            )
        )
        return True
