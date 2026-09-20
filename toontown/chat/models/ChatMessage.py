from typing import Union, Optional

from toontown.chat.enums.ChatChannel import ChatChannel
from toontown.chat.enums.ChatContentType import ChatContentType
from toontown.chat.models.ChatMessageContent import ChatTextContent, ChatSpeedChatContent, ChatStickerContent
from toontown.chat.models.ChatMessageSender import ChatMessageSender
from toontown.chat.services import ChatSpeedChatEncoding
from toontown.inventory.enums.ItemEnums import ChatStickersItemType
from toontown.inventory.registry import ItemTypeRegistry

from toontown.toonbase import TTLocalizer


class ChatMessage:
    """
    A chat message sent by an entity in the game.
    """
    __slots__ = ("channel", "modifier", "contentType", "content", "sender")

    def __init__(self, channel: ChatChannel, modifier: int, contentType: ChatContentType, content: str, sender: ChatMessageSender):
        self.channel: ChatChannel = channel
        """The channel the message was sent on."""

        self.modifier: int = modifier
        """The modifier to apply to the chat channel."""

        self.contentType: ChatContentType = contentType
        """The type of content that was sent."""

        self.content: Union[ChatTextContent, ChatSpeedChatContent, ChatStickerContent] = self.__parseContent(content)
        """The contents of the message."""

        self.sender: ChatMessageSender = sender
        """Information about the sender of the message."""

    def __parseContent(self, content: str) -> Optional[Union[ChatTextContent, ChatSpeedChatContent, ChatStickerContent]]:
        """Parses the content string based on the set content type."""
        if self.contentType == ChatContentType.Text:
            return ChatTextContent(content)

        elif self.contentType == ChatContentType.SpeedChat:
            return ChatSpeedChatEncoding.decode(content)

        elif self.contentType == ChatContentType.Sticker:
            stickerSubtype = ChatStickersItemType(content)
            if stickerSubtype is not None:
                stickerDefinition = ItemTypeRegistry.getItemDefinition(stickerSubtype)
                return ChatStickerContent(TTLocalizer.StickerText % stickerDefinition.getName(modifier=self.modifier), stickerSubtype)

        return None
