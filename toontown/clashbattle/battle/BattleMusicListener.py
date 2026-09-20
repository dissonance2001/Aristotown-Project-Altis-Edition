from direct.interval.IntervalGlobal import *

from toontown.clashsuit.suit import SuitBase
from toontown.toonbase import ToontownGlobals
from direct.interval.IntervalGlobal import Sequence, LerpFunc
import random
from enum import Enum, auto

"""
General dictionary for suits that we want to listen for special themes for
Index [0] is a 'default' for suits that have multiple themes
For future cogs we want to add to this listener, simply add their codename, the theme organization type as listed below, then add their theme(s) in a list.

'general' - Used for suits that have only one theme that we want to play (mercs, some facility bosses, etc.)
    'suitName':
        {
        'general': ["track"]
        }

'zone' - Used for suits that that we want to specify a specific zone for their battle (count erclaim) ZONE_FALLBACK is an edgecase in case we fight in a non-defined zone
    'suitName':
        {
        'zone': 
            {
            ZONE_FALLBACK: ["track"]
            zoneId: ["track1"]
            zoneId2: ["track2"]
            }
        }

Multiple themes in a list allows for random choice.
"""
ZONE_FALLBACK = 0


# Special attributes that may trigger certain songs to play
class SpecialChecks(Enum):
    Virtual = auto()
    Nuclear = auto()


# Dict of type -> attribute name
SpecialCheckAttributes = {
    SpecialChecks.Virtual: 'isVirtual',
    # For FTF
    SpecialChecks.Nuclear: 'isFinalNuclear',
}

suitToMusic = {
    'count': {
        'zone': {
             ZONE_FALLBACK: ["count_battle_two"],  # Default/Fallback
             ToontownGlobals.ToontownCentral: ["count_battle_two"],
             ToontownGlobals.DonaldsDock: ["count_battle_two"],
             ToontownGlobals.OldeToontown: ["count_battle_street_yott"],
             ToontownGlobals.DaisyGardens: ["count_battle_street_dg"],
             ToontownGlobals.MinniesMelodyland: ["count_battle_street_mml"],
             ToontownGlobals.TheBrrrgh: ["count_battle_street_tb"],
             ToontownGlobals.OutdoorZone: ["count_battle_street_aa"],
             ToontownGlobals.DonaldsDreamland: ["count_battle_street_ddl"],
        }
    },
    'foreman': {
        'zone': {
             ZONE_FALLBACK: ["sellbot_factory_boss"],  # Default/Fallback
             ToontownGlobals.SellbotFactoryInt: ["sellbot_factory_boss"],
             ToontownGlobals.SellbotFactorySideInt: ["sellbot_factory_boss_side"],
             ToontownGlobals.SellbotFindForemanInt: ["sellbot_ftf_battle"],
        }
    },
    'erfit': {
        'general': ['erfit_battle_two']
    },
    'supervis': {
        'zone': {
             ZONE_FALLBACK: ["cashbot_mint_boss_11500"],  # Default/Fallback
             ToontownGlobals.CashbotMintIntA: ["cashbot_mint_boss_11500"],
             ToontownGlobals.CashbotMintIntB: ["cashbot_mint_boss_11600"],
             ToontownGlobals.CashbotMintIntC: ["cashbot_mint_boss_11700"],
             ToontownGlobals.SellbotFindForemanInt: ["sellbot_ftf_battle"],
        }
    },
    'clerk': {
        'zone': {
             ZONE_FALLBACK: ["lawbot_lawfice_a_boss"],  # Default/Fallback
             ToontownGlobals.LawbotStageIntA: ["lawbot_lawfice_a_boss"],
             ToontownGlobals.LawbotStageIntB: ["lawbot_lawfice_b_boss"],
             ToontownGlobals.LawbotStageIntC: ["lawbot_lawfice_c_boss"],
             ToontownGlobals.SellbotFindForemanInt: ["sellbot_ftf_battle"],
        }
    },
    'clubpres': {
        'zone': {
             ZONE_FALLBACK: ["bossbot_country_club_boss_13500"],  # Default/Fallback
             ToontownGlobals.BossbotCountryClubIntA: ["bossbot_country_club_boss_13500"],
             ToontownGlobals.BossbotCountryClubIntB: ["bossbot_country_club_boss_13600"],
             ToontownGlobals.BossbotCountryClubIntC: ["bossbot_country_club_boss_13700"],
             ToontownGlobals.SellbotFindForemanInt: ["sellbot_ftf_battle"],
        }
    },
    'duckshfl': {
        'general': ['duckshuffler_battle']
    },
    'ddiver': {
        'general': ['deepdiver_battle']
    },
    'gatekeep': {
        'general': ['gatekeeper_battle']
    },
    'bellring': {
        'general': ['bellringer_battle']
    },
    'mouthp': {
        'general': ['mouthpiece_battle']
    },
    'fires': {
        'general': ['firestarter_battle']
    },
    'treek': {
        'general': ['treekiller_battle']
    },
    'fbed': {
        'general': ['featherbedder_battle']
    },
    'prethink': {
        'general': ['prethinker_battle']
    },
    'rainmake': {
        'general': ['rainmaker_battle']
    },
    'whunter': {
        'general': ['witchhunter_battle']
    },
    'mslacker': {
        'general': ['multislacker_battle']
    },
    'mplayer': {
        'general': ['majorplayer_battle']
    },
    'pcrat': {
        'general': ['plutocrat_battle']
    },
    'chainsaw': {
        'general': ['chainsaw_battle']
    },
    'psetter': {
        'general': ['pacesetter_battle']
    },
    SpecialChecks.Virtual: {
        'zone': {
             ZONE_FALLBACK: [None],  # Default/Fallback
             ToontownGlobals.LawbotStageIntA: ["lawbot_lawfice_a_battle_virtual"],
             ToontownGlobals.LawbotStageIntB: ["lawbot_lawfice_b_battle_virtual"],
             ToontownGlobals.LawbotStageIntC: ["lawbot_lawfice_c_battle_virtual"]
        }
    },

    # EVENT
    'ftf_s': {
        'general': ["None"]
    },
    'ftf_m': {
        'general': ["None"]
    },
    'ftf_l': {
        'general': ["None"]
    },
    'ftf_c': {
        'general': ["None"]
    },
    'ftf_s_rt': {
        'general': ["None"]
    },
    'ftf_s_br': {
        'general': ["None"]
    },
    'ftf_m_cf': {
        'general': ["None"]
    },
    'ftf_c_ac': {
        'general': ["None"]
    },
    SpecialChecks.Nuclear: {
        'general': ['ftf_oc_battle_final']
    },
}


# Instance the class (reference DistributedBattle.py) if we want to use the listener in an obscure place
class BattleMusicListener:
    """
    ===Battle Music Listener===
    The BML is used for playing special/custom music if there are specific
    suits in the battle like Count or a Facililty miniboss.
    If something breaks, yell at Turkeybone.
    """
    def __init__(self):
        """
        We want to store the theme so the battle knows 
        which one to stop at the end of the fight
        also used to let the client know if the theme is already playing or not
        """
        self.storedMusic = None
        self.currentVolume = 1.0
        self.currentPlayback = 1.0

    def lookForSuits(self, suits, zone):
        # looping through the suits currently in battle
        for suit in suits:
            # First check special attributes that may influence what music plays.
            self.checkSpecialAttributes(suit, zone)
            # Get the suit's name for all of the checks
            suitName = suit.getStyleName()
            if suitName in suitToMusic.keys():
                # Do everything we need to do with this information
                self.checkApplicableMusicData(suitToMusic[suitName], zone)

    def checkApplicableMusicData(self, musicData, zone):
        # Get the type of music list we want to use from the dictionary
        musicType = musicData.keys()
        # Checking for the different musictypes
        # The 'general' music type, just pick a random one from the array
        if 'general' in musicType:
            musicList = musicData['general']
            if len(musicList) > 1:
                self.storedMusic = random.choice(musicList)
            else:
                self.storedMusic = musicList[0]
        # The 'zone' music type, check for themes in the zone
        elif 'zone' in musicType:
            self.checkForZoneThemes(musicData['zone'], zone)
        else:
            self.storedMusic = 'error'

    # Use the zone, if we have one, to get the zone to get a theme for each identified zone
    def checkForZoneThemes(self, zoneMusicDict, zone):
        musicList = zoneMusicDict[ZONE_FALLBACK]
        if zone:
            # If the zone is in the array, set the suit music to the zone index
            # If it doesn't find one for whatever reason, play the fallback theme for the suit
            for zoneId in zone:
                if zoneId in zoneMusicDict.keys():
                    # We've got a valid track, redefine the musicList
                    musicList = zoneMusicDict[zoneId]
                    if len(musicList) > 1:
                        self.storedMusic = random.choice(musicList)
                    else:
                        self.storedMusic = musicList[0]
                else:
                    if len(musicList) > 1:
                        self.storedMusic = random.choice(musicList)
                    else:
                        self.storedMusic = musicList[0]
        else:
            if len(musicList) > 1:
                self.storedMusic = random.choice(musicList)
            else:
                self.storedMusic = musicList[0]

    def checkSpecialAttributes(self, suit, zone):
        # Do special checks first
        for specialCheck in SpecialChecks:
            suitAttrs = SpecialCheckAttributes[specialCheck]
            if type(suitAttrs) not in (list, tuple):
                suitAttrs = [suitAttrs]
            results = []
            for suitAttr in suitAttrs:
                # See if attribute is true
                result = getattr(suit, suitAttr, False)
                if callable(result):
                    result = result()
                results.append(result)
            # If all attributes are true, see what music we can grab from it
            if all(results):
                self.checkApplicableMusicData(suitToMusic[specialCheck], zone)

    """
    General function for playing the music, use this in files we want the listener
    If we don't find a suit we're listening for, don't play their theme
    """
    def playMusic(self, suits, zone=None, playbackSpeed=1.0, keyOverride: str = None, volumeOverride: float = 1.0):
        if keyOverride is not None:
            self.storedMusic = keyOverride
        else:
            self.lookForSuits(suits, zone)
        self.currentVolume = volumeOverride
        self.currentPlayback = playbackSpeed
        if self.storedMusic and self.storedMusic != 'None':
            base.musicMgr.playMusic(self.storedMusic, looping=1, volume=self.currentVolume)
            base.musicMgr.setPlayRate(self.storedMusic, playbackSpeed)

    # Stops the music when we want it to, but only if we're playing music
    def stopMusic(self):
        base.musicMgr.stopMusic(self.storedMusic)

    def setVolume(self, volume):
        self.currentVolume = volume
        base.musicMgr.setVolume(self.storedMusic, self.currentVolume)

    def updateStoredMusic(self):
        if base.musicMgr.playingMusic:
            self.storedMusic = list(base.musicMgr.playingMusic.keys())[0]

    def changePlaybackSpeed(self, end, duration=0.0, start=None):
        """Change the BML's playback speed."""
        def updateMusicSpeed(speed):
            if self.storedMusic and self.storedMusic != 'None':
                base.musicMgr.setPlayRate(self.storedMusic, speed)
            self.currentPlayback = speed

        if start is None:
            start = self.currentPlayback

        Sequence(
            LerpFunc(
                updateMusicSpeed, fromData=start, toData=end, duration=duration
            )
        ).start()
