from toontown.utils.EnhancedIntEnum import EnhancedIntEnum


class ChatZoneModifier(EnhancedIntEnum):
    """
    All the modifiers for zoned chat.
    """
    Normal = 1
    """A speech bubble which disappears after some time."""

    Thought = 2
    """A speech bubble which stays until it's cleared."""

    Clear = 3
    """Clears the current chat message"""


AllChatZoneModifiers = [item.value for item in ChatZoneModifier]
