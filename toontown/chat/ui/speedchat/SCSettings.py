from toontown.chat.ui.speedchat.SCColorScheme import SCColorScheme
from toontown.toonbase import TTLocalizer


class SCSettings:
    def __init__(self, eventPrefix, whisperMode=0, colorScheme=None, submenuOverlap=TTLocalizer.SCOsubmenuOverlap, topLevelOverlap=None):
        self.eventPrefix = eventPrefix
        self.whisperMode = whisperMode
        if colorScheme is None:
            colorScheme = SCColorScheme()
        self.colorScheme = colorScheme
        self.submenuOverlap = submenuOverlap
        self.topLevelOverlap = topLevelOverlap
