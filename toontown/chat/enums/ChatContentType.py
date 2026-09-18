from toontown.utils.EnhancedIntEnum import EnhancedIntEnum


class ChatContentType(EnhancedIntEnum):
    """
    Inside the message protocol, content is always sent as a string.
    However, not all messages are pure strings.
    For this reason, we also send a ContentType, so the receiver knows how to parse the message.
    """
    Text = 1
    """Messages which contain freely typed content."""

    SpeedChat = 2
    """Messages which use a predefined phrase."""

    Sticker = 3
    """Messages which use a predefined sticker."""


AllChatContentTypes = [item.value for item in ChatContentType]
