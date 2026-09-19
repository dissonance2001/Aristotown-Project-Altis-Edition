from panda3d.core import ConfigVariableInt, Filename, DSearchPath, AudioManager
from toontown.audio.AudioGlobals import getAdjustedSfxVolume
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

'''
BattleSounds exists as a separate audiomanager from the default one in Showbase.py
so we can completely flush battle sounds when we go to areas that battles
cannot occur. (see globalBattleSoundCache.clear() in TownLoader.py)

It might be simpler to use 1 audio manager so you have only 1 set if audio settings, but
you could add tagged sounds so all the 'battle'-tagged sounds could be flushed from the 
cache at once.  cache size might need to be increased in battle areas though
'''


@DirectNotifyCategory()
class BattleSounds:
    def __init__(self):
        self.mgr = AudioManager.createAudioManager()
        self.isValid = 0
        if self.mgr is not None and self.mgr.isValid():
            self.isValid = 1
            limit = ConfigVariableInt('battle-sound-cache-size', 15).getValue()
            self.mgr.setCacheLimit(limit)
            sfxVol = getAdjustedSfxVolume()
            self.mgr.setVolume(sfxVol)
            
            # make sure user sound settings are applied to this snd manager
            base.addSfxManager(self.mgr)
            self.setupSearchPath()

    def setupSearchPath(self):
        """ Sets self.sfxSearchPath with the appropriate search path
        to find battle sound effects. """

        self.sfxSearchPath = DSearchPath()
        self.sfxSearchPath.appendDirectory(Filename('../resources/phase_3/audio/sfx'))
        self.sfxSearchPath.appendDirectory(Filename('../resources/phase_3.5/audio/sfx'))
        self.sfxSearchPath.appendDirectory(Filename('../resources/phase_4/audio/sfx'))
        self.sfxSearchPath.appendDirectory(Filename('../resources/phase_5/audio/sfx'))
        self.sfxSearchPath.appendDirectory(Filename('/phase_3/audio/sfx'))
        self.sfxSearchPath.appendDirectory(Filename('/phase_3.5/audio/sfx'))
        self.sfxSearchPath.appendDirectory(Filename('/phase_4/audio/sfx'))
        self.sfxSearchPath.appendDirectory(Filename('/phase_5/audio/sfx'))

    def clear(self):
        if self.isValid:
            self.mgr.clearCache()

    def getSound(self, name):
        if self.isValid:
            # If given the full phase string, just load up the sfx and use it.
            if name.find('phase_') != -1:
                sfx = loader.loadSfx(name)
                return sfx
            filename = Filename(name)
            found = vfs.resolveFilename(filename, self.sfxSearchPath)
            if not found:
                # If it wasn't found, try once more to reset the
                # search path.  Maybe the first time we set it, we
                # didn't have all of the phases loaded yet.
                self.setupSearchPath()
                found = vfs.resolveFilename(filename, self.sfxSearchPath)
            if not found:
                # If it's still not found, something's wrong.
                self.notify.warning('%s not found on:' % name)
                print(self.sfxSearchPath)
            else:
                return self.mgr.getSound(filename.getFullpath())
        return self.mgr.getNullSound()


globalBattleSoundCache = BattleSounds()
