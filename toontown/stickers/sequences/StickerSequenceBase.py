from abc import ABC, abstractmethod
from typing import Optional

from direct.showbase.DirectObject import DirectObject
from panda3d.core import NodePath

from toontown.chat.services.ChatAssetCache import ChatAssetCache
from toontown.inventory.enums.ItemEnums import ChatStickersItemType
from toontown.toon import TTEmote


class StickerSequenceBase(ABC, DirectObject):
    assetCache = ChatAssetCache()

    def __init__(self, worldParent: NodePath, toon: NodePath, stickerSubtype: ChatStickersItemType, modifier: Optional[int] = None):
        self.worldParent = worldParent
        self.toon = toon
        self.stickerSubtype = stickerSubtype
        self.modifier = modifier

        self.__emotesActive = True

    @abstractmethod
    def startSequence(self):
        """Creates and plays the sticker sequence."""
        pass

    @abstractmethod
    def stopSequence(self):
        """Stops and cleans up the sticker sequence."""
        pass

    def enableEmotes(self):
        """Enable user emotes."""
        if not self.__emotesActive:
            self.__emotesActive = True
            TTEmote.globalEmote.releaseBody(self.toon, 'sticker')

    def disableEmotes(self):
        """Disable user emotes."""
        if self.__emotesActive:
            self.__emotesActive = False
            TTEmote.globalEmote.disableBody(self.toon, 'sticker')
