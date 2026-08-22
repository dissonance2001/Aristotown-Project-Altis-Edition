"""
DynamicSound module: contains the DynamicSound class, used as an interface for all DynamicSoundObjects.

Dynamic sounds are currently considered as 'special' sound effects. They are SoundIntervals; NOT managed by 3D audio.
Essentially, they are parented to some node and will have their audio volume determined by the listenerNode's distance
from them.

DynamicSoundObjects are most effective when parented to a locator / origin / DCS node.
The location of where the center of the audio is located is based off the node's pivot point location.

This also allows for true "ambient" sounds to exist outside of entities/levels/facilities (toontown.level.AmbientSound)

Todo:
    - Currently does not support async sound effect loading.
    - Proper audio cleaning up
    - Things might get a bit weird (or crash) if someone accidentally creates two objects with the same name
"""
from direct.interval.SoundInterval import SoundInterval
import random
from panda3d.core import NodePath, AudioManager
from toontown.audio.AudioGlobals import getAdjustedSfxVolume
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

dynamicSoundData_default = {
    # Friendly name of the DynamicSoundNode (Ensure this is unique)
    'name': 'DynamicSoundNode',
    # Audio filepath (note: currently not asynchronous supported)
    'filepath': 'phase_4/audio/sfx/MG_lose.ogg',
    'seamlessLoop': True,
    'loop': True,
    # How much  will the track play? (0.0 is all of it)
    'duration': 0.0,
    # Base volume setting
    'volume': 1.0,
    # Cutoff distance for the sound effect. You can think of this as the audio radius.
    # base.sfxPlayer.getCutoffDistance()
    'cutOff': 50,
    # Begin at some random time of the playback
    'randomStart': False,
    # Speed of the audio playback
    'playRate': 2.0,
    # FilterProperties config
    'filterProperties': None,
}

WantDebugSpheres = False

"""
from toontown.audio import DynamicSound
dSound = base.dynamicSound.createDynamicSoundObject(render.find("**/coll_plaza"), nodeName="dSoundTest")
dSound.addSoundObject(DynamicSound.dynamicSoundData_default, base.localAvatar)
"""


@DirectNotifyCategory()
class DynamicSound:
    """
    Manages tall the loaded in dynamic sounds. base.dynamicSound is an alias for this.

    base.dynamicSound.mgr --> AudioManager for the dynamic sounds
    base.dynamicSound.uid2SoundObject --> Dict containing all loaded in dynamic sound objects. uid : DynamicSoundObject
    """

    def __init__(self):
        self.mgr = None
        self.uid2SoundObject = {}  # id : DynamicSoundObject
        # While we don't necessarily need to do this, we'll use a separate audio manager for our dynamic sounds.
        # Notice: This makes DynamicSounds desynced with changes made with ToontownAudio atm
        self.initMgr()

    def initMgr(self):
        self.mgr = AudioManager.createAudioManager()
        self.isValid = 0
        if self.mgr is not None and self.mgr.isValid():
            self.isValid = 1
            self.mgr.setVolume(getAdjustedSfxVolume())
            # make sure user sound settings are applied to this manager
            base.addSfxManager(self.mgr)

    def createDynamicSoundObject(self, parent, nodeName = 'DynamicSoundNodePath'):
        """
        :param parent: Parent node; PREFERABLY a locator/origin node.
         The location of the nodes pivot point determines the location of the sound node.
        :param str nodeName: A *unique* name for this DynamicSoundNode.
        :rtype: DynamicSoundObject
        """
        dSound = DynamicSoundObject(parent, nodeName)
        self.uid2SoundObject[dSound.uniqueId] = dSound
        return dSound

    def cleanupSound(self, uniqueId):
        if uniqueId in self.uid2SoundObject:
            self.uid2SoundObject[uniqueId].cleanup()
            self.uid2SoundObject[uniqueId] = None

    def cleanupAllSounds(self):
        # todo
        pass

    def getAllActiveSounds(self):
        """
        :return: a list of DynamicSoundObject instances with __paused or __deleted != True
        """
        # todo
        pass

    def getAllPausedSounds(self):
        """
        :return: a list of DynamicSoundObject instances with __paused == True
        """
        # todo
        pass

    def getSoundUid(self, dSound):
        """
        :type dSound: DynamicSoundObject
        :returns: The Unique Identifier for the given DynamicSoundObject.
        :rtype: str
        """
        return dSound.uniqueId


@DirectNotifyCategory()
class DynamicSoundObject(NodePath):
    """
    NodePath attached to a parent node, containing a SoundInterval w/ arranged AudioSound properties (dynamicSoundData).
    """

    def __init__(self, parent, nodeName):
        """
        :param parent: Preferably a locator / origin / DCS node.
        """
        node = parent.attachNewNode(nodeName)
        NodePath.__init__(self, node)
        self.sound = [node, None]  # (node, SoundInterval)
        self.uniqueId = f"{nodeName}"  # todo: ensure uniqueIds are unique in case nodeName is a dupe
        self.__deleted = False
        self.__paused = False

        if __debug__ and WantDebugSpheres:
            parent.show()
            self.sphere = loader.loadModel("models/misc/sphere")
            self.sphere.setColorScale(1, 0, 1, 0.6)
            self.sphere.setTransparency(1)
            self.sphere.reparentTo(node)
            self.sphere.show()

    def addSoundObject(self, dynamicSoundData, listenerNode):
        """
        :param dict dynamicSoundData: List of audio properties
        :param NodePath listenerNode: Preferably base.localAvatar or base.cam [for headless clients]
        """
        loop = dynamicSoundData.get('loop', False)
        duration = dynamicSoundData.get('duration', 0.0)
        name = dynamicSoundData.get('name', 'DynamicSoundNode')
        filepath = dynamicSoundData.get('filepath', None)
        volume = dynamicSoundData.get('volume', 1.0)
        seamlessLoop = dynamicSoundData.get('seamlessLoop', False)
        cutOff = dynamicSoundData.get('cutOff', None)
        randomStart = dynamicSoundData.get('randomStart', False)
        playRate = dynamicSoundData.get('playRate', 1.0)
        filterProperties = dynamicSoundData.get('filterProperties', None)

        if filepath is None:
            # To prevent crashes, let's just return out.
            self.notify.warning("Tried to add a sound object with a Nonetype filepath!")
            return
        if name == "DynamicSoundNode":
            # Since we currently don't have support for ensuring that each node has a unique identifier, let's
            # warn our user about it in case things go wrong.
            self.notify.warning("Name of DynamicSoundObject is default. (DynamicSoundNode)")

        loader.loadSound(
            soundPath = filepath,
            # manager = base.sfxManagerList[0],
            manager = base.dynamicSound.mgr,
            callback = self.__addSoundObjectCallback,
            extraArgs = [
                loop, duration, name, volume, seamlessLoop,
                listenerNode, cutOff, randomStart, playRate,
                filterProperties
            ]
        )

    def __addSoundObjectCallback(self, sfx, loop, duration, name, volume, seamlessLoop, listenerNode, cutOff,
                                 randomStart, playRate, filterProperties):
        """
        Private callback function used for loading in our desired sound.
        This makes any adjustments needed to our sfx and generates the desired SoundInterval.

        :param AudioSound sfx: Our track that has been loaded in.
        :type: filterProperties: FilterProperties
        """
        if self.__deleted or self.__paused:
            return

        # Configure AudioSound properties here
        sfx.setPlayRate(playRate)
        # note: we don't really use 3D audio so don't worry about it here
        if filterProperties is not None:
            sfx.configureFilters(filterProperties)

        # Configure SoundInterval properties here
        sound = SoundInterval(
            sfx,
            node = self,
            loop = loop,
            duration = duration,
            name = name,
            volume = volume,
            seamlessLoop = seamlessLoop,
            cutOff = cutOff,
            listenerNode = listenerNode,
        )
        sound.loop()
        if randomStart:
            sound.setT(random.random() * sfx.length())
        self.sound[1] = sound
        self.__paused = False

    def disable(self):
        if self.sound[1]:
            self.sound[1].pause()
            self.__paused = True

    def enable(self):
        if self.sound[1]:
            self.sound[1].loop()
            self.__paused = False

    def cleanup(self):
        if __debug__ and WantDebugSpheres:
            self.sphere.removeNode()
        self.sound[1].finish()
        self.__deleted = True
        self.removeNode()


# Note: Dataclasses would be better to use here, but since we're stuck on Python 3.6, we can't use em :(

# from dataclasses import dataclass
#
#
# @dataclass
# class DynamicSound:
#     path: str
#     volume: float = 1.0
#     enabled: bool = False

"""
from toontown.audio import DynamicSoundObject

dso = DynamicSoundObject.DynamicSoundObject(render.find("**/coll_plaza"))
dso.addSoundObject(DynamicSoundObject.dynamicSoundData_default, base.localAvatar)
"""
