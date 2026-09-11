"""
# AudioUtil (Formerly AudioDebugInfo) #

"""

audio = base.musicManager

# https://docs.panda3d.org/1.10/python/reference/panda3d.core.AudioSound
def getSoundInfo(audioSound):
    SoundInfo = {
        "Status":audioSound.status(),
        "Active":audioSound.getActive(),
        "Priority Level":audioSound.getPriority(),
        "Balance level":audioSound.getBalance(),
        "Is looping?":audioSound.getLoop(),
        "Loop count":audioSound.getLoopCount(),
        "Max 3D Audio Distance":audioSound.get3dMaxDistance(),
        "Min 3D Audio Distance":audioSound.get3dMinDistance(),
        "Finished Event":audioSound.getFinishedEvent(),
        "Audio Time":audioSound.getTime(),
        "Audio Length":audioSound.getLength(),
        "Audio Volume":audioSound.getVolume()
    }
    return SoundInfo

# https://docs.panda3d.org/1.10/python/reference/panda3d.core.AudioManager
def getAudioInfo():
    if audio is None:
        return
    AudioInfo = {
        "Active":audio.getActive(),
        "Valid":audio.isValid(),
        "Cache Limit":audio.getCacheLimit(),
        "Concurrent Sound Limit":audio.getConcurrentSoundLimit(),
        "Dls Pathname":audio.getDlsPathname(),
        "Speaker Setup":audio.getSpeakerSetup(),
        "Volume":audio.getVolume(),
        "3D Audio Distance Factor":audio.audio3dGetDistanceFactor(),
        "3D Audio Doppler Factor":audio.audio3dGetDopplerFactor(),
        "3D Audio Dropoff Factor":audio.audio3dGetDropOffFactor()
    }
    return AudioInfo

def printAudioInfo():
    AudioInfo = getAudioInfo()
    for k, v in AudioInfo.items():
        print(k, v)
