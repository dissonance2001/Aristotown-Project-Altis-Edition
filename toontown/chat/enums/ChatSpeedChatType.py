from toontown.utils.EnhancedIntEnum import EnhancedIntEnum


class ChatSpeedChatType(EnhancedIntEnum):
    """
    Inside the SpeedChat system, there is multiple different types of messages.
    Each of those message types need to be parsed differently.
    To inform the recipient how to parse the message, we add the type.
    """
    Static = 1
    """A static SpeedChat message, potentially with a linked emote."""

    Custom = 2
    """A bought phrase, potentially with a linked emote."""

    Quest = 3
    """An automatically generated quest message."""
