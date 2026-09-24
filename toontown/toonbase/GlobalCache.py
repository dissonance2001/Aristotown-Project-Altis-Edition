from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from .GlobalCacheData import GlobalCacheDataRegistry, GlobalCacheCategory, GlobalCacheKey
from typing import Dict


@DirectNotifyCategory()
class GlobalCache(DirectObject):
    """
    A global cache for models, textures, fonts, and sounds.
    """

    def __init__(self):
        # Holds modelPath -> nodePath info
        self.__loadedModels: Dict[str, NodePath] = {}
        self.__loadedSounds: Dict[str, AudioSound] = {}

    @staticmethod
    def getGlobalCacheDict():
        return GlobalCacheDataRegistry[GlobalCacheKey.Global]

    # region Models

    def loadModelIntoCache(self, modelPath, **kwargs):
        if modelPath not in self.__loadedModels.keys():
            baseModel = loader.loadModel(modelPath, **kwargs)
            self.__loadedModels[modelPath] = baseModel

    def addModelToCache(self, modelPath, model):
        if modelPath not in self.__loadedModels:
            self.__loadedModels[modelPath] = model

    def getModel(self, modelPath, **kwargs):
        modelPath.replace('.bam', '')
        # Load base model for copy purposes if it's not loaded yet
        self.loadModelIntoCache(modelPath, **kwargs)

        # Return a copy of our cached model
        return self.__loadedModels[modelPath].copyTo(NodePath())

    def clearModelFromCache(self, modelPath: str):
        if modelPath in self.__loadedModels.keys():
            self.__loadedModels[modelPath].removeNode()
            del self.__loadedModels[modelPath]
            loader.unloadModel(modelPath)

    def clearAllModelsFromCache(self):
        for modelPath in list(self.__loadedModels.keys()):
            self.clearModelFromCache(modelPath)

    # endregion
    # region Sounds

    def loadSoundIntoCache(self, soundPath):
        if soundPath not in self.__loadedSounds.keys():
            baseSound = loader.loadSfxRaw(soundPath)
            self.__loadedSounds[soundPath] = baseSound

    def getSound(self, soundPath):
        return loader.loadSfxRaw(soundPath)
        # Load base model for copy purposes if it's not loaded yet
        self.loadSoundIntoCache(soundPath)

        # Return a copy of our cached sound
        return self.__loadedSounds[soundPath]

    def clearSoundFromCache(self, soundPath: str):
        if soundPath in self.__loadedSounds.keys():
            self.__loadedSounds[soundPath].stop()
            del self.__loadedSounds[soundPath]

    def clearAllSoundsFromCache(self):
        for soundPath in list(self.__loadedSounds.keys()):
            self.clearSoundFromCache(soundPath)

    # endregion

    def loadFromKey(self, cacheKey):
        cacheCatDict = GlobalCacheDataRegistry.get(cacheKey, dict())
        for cacheValue in cacheCatDict.get(GlobalCacheCategory.Models, []):
            self.loadModelIntoCache(cacheValue)
        for cacheValue in cacheCatDict.get(GlobalCacheCategory.Sounds, []):
            pass
            # self.loadSoundIntoCache(cacheValue)

    def swapToKey(self, cacheKey):
        cacheCatDict = GlobalCacheDataRegistry.get(cacheKey, dict())
        globalDict = self.getGlobalCacheDict()
        neededModels = set(cacheCatDict.get(GlobalCacheCategory.Models, []) + globalDict[GlobalCacheCategory.Models])
        neededSounds = set(cacheCatDict.get(GlobalCacheCategory.Sounds, []) + globalDict[GlobalCacheCategory.Sounds])

        # Clear out unneeded models
        for modelPath in list(self.__loadedModels.keys()):
            if modelPath not in neededModels:
                self.clearModelFromCache(modelPath)

        # Clear out unneeded sounds
        for soundPath in list(self.__loadedSounds.keys()):
            if soundPath not in neededSounds:
                pass
                # self.clearSoundFromCache(soundPath)

        # Load new needed models
        for modelPath in set(self.__loadedModels.keys()).difference(neededModels):
            self.loadModelIntoCache(modelPath)

        # Load new needed sounds
        for soundPath in set(self.__loadedSounds.keys()).difference(neededSounds):
            pass
            # self.loadSoundIntoCache(soundPath)
