from panda3d.core import VirtualFileSystem, Filename
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
import json
import random
import os

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

NULL_MUSIC = 'None'


@DirectNotifyCategory()
class ToontownMusic(object):
    """
    Created on 11/12/2020

    ToontownMusic

    A class built to handle management of music files and music filepaths,
    specifically to streamline development processes that use music in game.

    @author: CheezedFish
    """

    import os

    def __init__(self):
        projectRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        musicPath = os.path.join(projectRoot, 'resources', 'phase_3', 'audio', 'music.json')

        self.prevMusicList = []
        self.prevMusicChoice = ''
        with open(musicPath, 'r') as f:
            self.musicData = json.load(f)
        self.overrideContentPackMusic()
        self.playingMusic = {}
        self.crossfadeSequence = None

    def overrideContentPackMusic(self):
        """
        Loads up all the path overrides defined in content packs' music.json files.
        """
        for season, _ in ContentPackMgr.overrideMusicData.items():
            # Make a temporary season dictionary, we will overwrite it once we are done
            tempSeasonDict = self.musicData.get(season, {})
            for key, value in ContentPackMgr.overrideMusicData[season].items():
                tempSeasonDict[key] = value
            self.musicData[season] = tempSeasonDict  # Overwrite it with the changes from content packs

    def loadMusic(self, musicCode):
        """
        Loads music from filepath specified in phase_3/audio/music.json, returns an AudioSound

        musicCode: A str representation for use in self.musicData lookup table.
        """
        musicPath = self.getMusicFilepath(musicCode)
        if musicPath == NULL_MUSIC:  # Special identifier for if we don't want music to play.
            return None

        result = None

        if not isinstance(musicPath, (list, set)):
            # We were given a single song path
            result = base.loader.loadMusic(musicPath)  # Just return this song back to the caller
            # Dummy out the previous music choices so they can properly randomize at next call
            self.prevMusicChoice = ''
            self.prevMusicList = []
        else:
            # We were given multiple songs, randomly choose from them
            if musicPath == self.prevMusicList:  # The two lists are the same, meaning it's likely a subzone
                choice = self.prevMusicChoice   # Get the exact song played previously in this list.
            else:
                choice = random.choice(musicPath)  # Otherwise, randomly select.

            # Store the list data for future use
            self.prevMusicList = musicPath
            self.prevMusicChoice = choice

            result = base.loader.loadMusic(choice)

        return result

    def playMusic(self, music, looping=0, interrupt=1, volume=None, time=0.0, musicCode=None):
        """
        Plays music using either a music code or an AudioSound

        looping: Whether the song should loop or not.
        interrupt: Should the song stop all other songs before playing?
        volume: Volume the audio should be set at, as a float
        time: Time to start the music at, as a float in seconds.
        musicCode: If loading a preloaded, specify a music code please
        """
        if interrupt:
            self.stopMusic()

        if isinstance(music, str):
            # Music passed in is a str, assume it is a music code
            musicFile = self.loadMusic(music) # Load the music file
            if musicFile:
                self.playingMusic[music] = musicFile  # Store this music file in self.playingMusic
                base.playMusic(musicFile, looping, 1, volume, time)
                # This means that it is a NullAudioSound, something didn't load right
                if (musicFile.length() == 0) and music != NULL_MUSIC:
                    musicFile = self.loadMusic('error')  # Load up error music
                    self.playingMusic[music] = musicFile  # Store this music file in self.playingMusic
                    base.playMusic(musicFile, looping, 1, volume, time)
                    self.notify.warning(
                        'Music path {0} is either misnnamed or incorrectly pathed in music.json. '
                        'Check to make sure you are using relative paths (/audio/bgm/file.ogg)'.format(music)
                    )
                # Let ToontownContentLuts know we've loaded a key.
                # self.contentLutsMgr.keyLoaded(music)
        else:
            # It's a predefined music file, just allow ToonBase to handle it.
            base.playMusic(music, looping, 1, volume, time)

        if musicCode:
            self.playingMusic[musicCode] = music

    def isMusicPlaying(self, music):
        """
        Returns whether the music is actively playing.

        music: Polymorphic representation of either musicCode str, or AudioSound
        """

        if isinstance(music, str):
            # It's a music code, check for it in self.playingMusic
            return music in list(self.playingMusic.keys())
        else:
            # Assume it's an AudioSound
            return music.status() == music.PLAYING

    def stopMusic(self, music=None):
        """
        Stops the music.

        music: Can be str, AudioSound, or NoneType. If it's NoneType, this function will stop ALL active music.
        """
        if isinstance(music, str):
            # It's a music code, check for it in self.playingMusic
            playingSong = self.playingMusic.get(music)
            if playingSong:  # Song exists
                playingSong.stop()  # Stop the song
                del self.playingMusic[music]  # And remove it from the dictionary
        else:
            if music:
                # It's a music file, just stop it.
                music.stop()
            else:
                # It's a request to disable ALL currently playing music.
                # Go through all playing music, and stop them
                playingMusicCopy = self.playingMusic.copy()  # Make a copy of the dict to prevent fail fast iteration
                for code, song in playingMusicCopy.items():
                    if song:  # In case the content pack author made it a NoneType
                        song.stop()
                    del self.playingMusic[code]

    def crossfadeIntoMusic(self, music, duration=0.0, delay=0.0,
                           looping=1, matchTime=False, volume=None, musicCode=None, time=0.0):
        """
        Crossfades the current playing song into another song.
        :param music:       The song to crossfade into. Can be a music key or file already loaded.
        :param duration:    The duration of the crossfade.
        :param delay:       How long to wait before beginning the crossfade.
        :param looping:     Does the new song loop?
        :param matchTime:   Match the current time of the old song to the new one.
        :param volume:      The volume to play the new song at.
        :param time:        The time that the new song should start at. Doesn't work if matchTime is set.
        :param musicCode:   If the music is preloaded, a music code MUST MUST **MUST** be defined.
        """
        if not (isinstance(music, str) or musicCode):
            return

        # Clean up the crossfade sequence.
        if self.crossfadeSequence and self.crossfadeSequence.isPlaying():
            self.crossfadeSequence.finish()
            self.crossfadeSequence = None

        def setVolume(volume, music):
            # We gotta wrap setVolume like this to use it in function intervals.
            self.setVolume(music, volume)

        crossfadeParallel = Parallel()
        alignTrack = Parallel()

        songToAlignWith = None

        # Create a fade-out track for all music that is playing.
        if self.playingMusic:
            for code, song in self.playingMusic.items():
                songToAlignWith = song
                # TODO - start the fromData at the volume the song was set at
                crossfadeParallel.append(Sequence(
                    LerpFunctionInterval(
                        setVolume, duration=duration, blendType='easeIn',
                        fromData=1.0, toData=0.0, extraArgs=[song]
                    ),
                    Wait(0.5),
                    Func(self.stopMusic, code),
                ))

        # Now, create a fade-in track for the new song.
        def alignMusic():
            # Align the music to crossfade into with the alignment track.
            t = songToAlignWith.getTime() if songToAlignWith and matchTime else time
            self.playMusic(music, looping=looping, interrupt=0, volume=0.0, time=t, musicCode=musicCode)

        # Build the align track.
        alignTrack.append(Func(alignMusic))
        alignTrack.append(LerpFunctionInterval(
            setVolume, duration=duration, blendType='easeOut',
            fromData=0.0, toData=volume or 1.0, extraArgs=[music]
        ))

        # Run our crossfade sequence.
        self.crossfadeSequence = Sequence(Wait(delay), Parallel(alignTrack, crossfadeParallel))
        self.crossfadeSequence.start()

    def getMusicKeyExists(self, musicCode):
        """
        Returns if a music key exists in music.json

        musicCode: A str representation for use in self.musicData lookup table.
        """
        season = base.currHoliday
        if not season or season == 'None':
            season = "default"  # Default to the default season if the season is not defined.
        seasonList = self.musicData.get(season)
        if musicCode in seasonList.keys():
            return True
        return False

    def getMusicFilepath(self, musicCode):
        """
        Returns the filepath for the musicCode as specified in music.json

        musicCode: A str representation for use in self.musicData lookup table.
        """
        season = base.currHoliday
        if not season or season == 'None':
            season = "default"  # Default to the default season if the season is not defined.

        seasonList = self.musicData.get(season)  # Get the dict of seasonal music
        if seasonList:
            musicPath = seasonList.get(musicCode)   # Get the filepath of the song
        else:
            musicPath = None

        if musicPath is None:
            try:
                musicPath = self.musicData.get('default').get(musicCode)
                if not musicPath:
                    raise Exception("Music file not found in default season.")
            except:
                self.notify.warning(
                    "Music with code {0} did not load properly. Check music.json and see if it was properly implemented.".format(musicCode)
                )
                return 'error'

        return musicPath

    def getMusicTime(self, music):
        """
        Returns the current time of the song.

        musicCode: Polymorphic representation of either musicCode str, or AudioSound
        """
        if isinstance(music, str):
            music = self.playingMusic.get(music)

        if music:
            return music.getTime()
        else:
            self.notify.warning('Tried to get music time for song {0} that was not active. Returning 0'.format(music))
            return 0

    def setPlayRate(self, music, playRate):
        """
        Sets the playrate of a song.

        music: Polymorphic representation of either musicCode str, or AudioSound
        """
        if isinstance(music, str):
            # It's a music code, get the AudioSound for it
            sound = self.playingMusic.get(music)
            if sound:
                sound.setPlayRate(playRate)
            else:
                self.notify.warning('Tried to set the playrate of music {0} when it was not active!'.format(music))
        else:
            # Assume it's an AudioSound
            music.setPlayRate(playRate)

    def setVolume(self, music, volume):
        """
        Sets the volume of a song.

        music: Polymorphic representation of either musicCode str, or AudioSound
        """
        if isinstance(music, str):
            # It's a music code, get the AudioSound for it
            sound = self.playingMusic.get(music)
            if sound:
                sound.setVolume(volume)
            else:
                self.notify.warning('Tried to set the volume of music {0} when it was not active!'.format(music))
        else:
            # Assume it's an AudioSound
            music.setVolume(volume)

    def getVolume(self, music):
        """
        Returns the volume of a song

        music: Polymorphic representation of either musicCode str, or AudioSound
        """
        if isinstance(music, str):
            # It's a music code, get the AudioSound for it
            sound = self.playingMusic.get(music)
            if sound:
                return sound.getVolume()
            else:
                self.notify.warning('Tried to set the volume of music {0} when it was not active!'.format(music))
                return 0
        else:
            # Assume it's an AudioSound
            return music.getVolume()

    def fadeOutMusic(self, time=3.0, music=None):
        """
        Fade out the track specified by <music> or all playing tracks if <music> is None

        :param time: Time interval over which to fade out music
        :param music: Polymorphic representation of either musicCode str, or AudioSound
        """
        for soundName, sound in self.playingMusic.items():
            if music is not None and soundName != music:
                continue

            Sequence(
                LerpFunctionInterval(
                    sound.setVolume, duration=time,
                    fromData=sound.getVolume(), toData=0.0,
                    blendType='easeIn',
                ),
                Func(self.stopMusic, soundName),
            ).start()