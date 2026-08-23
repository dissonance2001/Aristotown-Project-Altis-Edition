"""
Created on 10/17/2021

A class built to load up LUTs from a LUT json file.
Used for content pack creators for excessive visual customization.

@author: Main
"""

import json
from panda3d.core import Filename, VirtualFileSystem
from toontown.toonbase.ContentPackManager import ContentPackManager
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

NULL_LUT = 'None'


@DirectNotifyCategory()
class ToontownContentLuts:
    def __init__(self):
        vfs = VirtualFileSystem.getGlobalPtr()

        # If we are in dev mode, use our model path instead
        if __debug__:
            lutPath = Filename("../resources/phase_3/luts/luts.json")
        else:
            lutPath = Filename("/phase_3/luts/luts.json")

        self.currentKey = ""
        self.luts = json.loads(vfs.readFile(lutPath, True))
        self.affect2d = False
        self.getContentPackLuts()

    def getContentPackLuts(self):
        """
        Loads up all the luts from the content pack manager.
        """
        self.affect2d = ContentPackManager.lutsAffectUI
        for key, str in list(ContentPackManager.luts.items()):
            # The ContentPackMgr will have already filtered out bad luts.
            self.luts[key] = str

    def keyLoaded(self, key):
        """
        Called from ToontownMusic when a key is loaded.
        """
        previousKey = self.currentKey
        if key in self.luts:
            if self.luts[key] != "pass":
                self.currentKey = key
        else:
            self.currentKey = ""
        if previousKey != self.currentKey:
            base.updateFilterSettings()

    def loadLut(self):
        """
        Loads a lut, returns a lut texture path.
        """
        result = self.attemptLoadLut()
        if result is False:
            self.notify.info(f"ToontownContentLuts tried to load a key and failed.")
            return ""
        else:
            return result

    def attemptLoadLut(self):
        """
        Attempts to load a lut, given a key.
        """
        key = self.currentKey
        if key not in self.luts:
            self.notify.warning(f"ToontownContentLuts tried to load invalid key '{key}'!")
            return False
        path = self.luts[key]
        if type(path) is list:
            self.affect2d = True
            return path[0]
        else:
            self.affect2d = False
            return path
