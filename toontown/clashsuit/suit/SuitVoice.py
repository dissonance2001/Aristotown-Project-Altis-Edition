from panda3d.core import *


class SuitVoice:
    """
    Container class for managing the sound files loaded by a Suit.
    """

    def __init__(self, voiceArray, skelVoiceArray, death, skelDeath):
        self.voiceArray = voiceArray
        self.skelVoiceArray = skelVoiceArray
        self.death = death
        self.skelDeath = skelDeath
        
    def setVoiceArray(self, voiceArray):
        self.voiceArray = voiceArray    
    
    def getVoiceArray(self):
        return self.voiceArray
        
    def setSkelVoiceArray(self, voiceArray):
        self.skelVoiceArray = voiceArray    
    
    def getSkelVoiceArray(self):
        return self.skelVoiceArray

    def getDeathSound(self, skelecog=False):
        soundPath = self.death if not skelecog else self.skelDeath
        return loader.loadSfx(soundPath)
