from typing import Optional

from toontown.chat.enums.ChatSpeedChatType import ChatSpeedChatType

from toontown.inventory.enums.ItemEnums import ChatStickersItemType


class ChatTextContent:
    """
    The contents of a Text chat message.
    """
    __slots__ = ("text",)

    def __init__(self, text: str):
        self.text: str = text
        """The scrubbed content of the message."""


class ChatSpeedChatContent:
    """
    The contents of a SpeedChat chat message.
    """
    __slots__ = ("type", "primaryId", "secondaryId", "text")

    def __init__(self, speedChatType: ChatSpeedChatType, primaryId: Optional[int], secondaryId: Optional[int], text: str):
        self.type: ChatSpeedChatType = speedChatType
        """The type of SpeedChat message this is."""

        self.primaryId: Optional[int] = primaryId
        """
        Emote SpeedChat: None\n
        Static SpeedChat: Phrase ID\n
        Custom SpeedChat: Phrase ID\n
        Quest SpeedChat: Quest ID
        """

        self.secondaryId: Optional[int] = secondaryId
        """
        Emote SpeedChat: Emote ID\n
        Static SpeedChat: Emote ID\n
        Custom SpeedChat: Emote ID\n
        Quest SpeedChat: Phrase index
        """

        self.text: str = text
        """The parsed phrase to speak."""


class ChatStickerContent:
    """
    The contents of a Sticker chat message.
    """
    __slots__ = ("text", "stickerSubtype")

    def __init__(self, text: str, stickerSubtype: ChatStickersItemType):
        self.text: str = text
        """The phrase version of using the sticker."""

        self.stickerSubtype: ChatStickersItemType = stickerSubtype
        """The instance of the sticker."""
