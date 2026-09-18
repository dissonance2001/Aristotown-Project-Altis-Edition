from typing import Dict

from panda3d.core import AudioSound, NodePath


class ChatAssetCache:
    """
    A cache used to reduce asset loading throughout the chat system.
    """

    def __init__(self):
        self._soundEffects: Dict[str, AudioSound] = {}
        self._models: Dict[str, NodePath] = {}

    def cleanup(self):
        for nodePath in self._models.values():
            nodePath.removeNode()

        self._soundEffects.clear()
        self._models.clear()

    def getSfx(self, filePath: str, forceLoad: bool = False) -> AudioSound:
        """
        Gets a sound effect from the cache.

        :param filePath: The path to the sound effect in the resources.
        :param forceLoad: Force loads the audio.
        :return: The cached sound effect.
        """
        if forceLoad:
            return loader.loadSfx(filePath)

        soundEffect = self._soundEffects.get(filePath)
        if soundEffect is None:
            soundEffect = loader.loadSfx(filePath)
            self._soundEffects[filePath] = soundEffect

        return soundEffect

    def getNodePath(self, modelPath: str, path: str):
        """
        Gets a NodePath from a model which is stored in the cache.

        :param modelPath: The path to the model in the resources.
        :param path: The NodePath to get.
        :return: The requested NodePath.
        """
        modelNodePath = self._models.get(modelPath)
        if modelNodePath is None:
            modelNodePath = loader.loadModel(modelPath)
            self._models[modelPath] = modelNodePath

        output = NodePath(f"Cached-{path}")
        a = modelNodePath.find(path)
        a.copyTo(output)
        return output
