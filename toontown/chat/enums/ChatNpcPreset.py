from toontown.utils.EnhancedIntEnum import EnhancedIntEnum


class ChatNpcPreset(EnhancedIntEnum):
    """
    The UI presets for the messages sent on the NPC channel.
    These presets are used on the chat display to apply colouring and a prefix.
    """
    Toon = 1
    """The general preset for NPC toons around the game."""

    Cog = 2
    """The general preset for cogs around the game."""

    Boss = 3
    """The override for boss cogs around the game."""

    Plant = 4
    """The general preset for plants. Kinda based."""

    LowBaller = 5
    """The preset for low ballers, for the high roller teleporter."""
