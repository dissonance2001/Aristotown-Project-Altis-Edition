from toontown.utils.EnhancedIntEnum import EnhancedIntEnum


class ChatChannel(EnhancedIntEnum):
    """
    Channels are the routing system used into of chat.
    When sending a message to the AI, the channel is used to direct your message.
    The channel is also used inside of systems like the UI.
    It's worth noting, these are different from channels in Astron.
    """
    Zone = 1
    """Messages sent out into the open world."""

    Whisper = 2
    """Messages sent to a single toon."""

    System = 3
    """Messages sent by the system or staff members to a collection of players."""

    NPC = 4
    """Messages sent by NPC toons or cogs."""

    Clubs = 5
    """Messages directed to all members inside of a club."""

    Groups = 6
    """Messages directed to all members of a group."""

    StaffLocal = 7
    """Messages directed to all staff members inside of a zone group."""

    StaffGlobal = 8
    """Messages directed to all staff members on the game."""

    Shortcut = 9
    """Messages directed to the Shortcut system."""


AllChatChannels = [item.value for item in ChatChannel]
