from toontown.utils.EnhancedIntEnum import EnhancedIntEnum


class ChatSystemMessagePreset(EnhancedIntEnum):
    """
    System messages are used for many systems in the game.
    These presets allow the customization of the popup which appears.
    They can also prevent logging the message to the chat display.
    """
    Default = 1
    """Used for general system messages."""

    Shortcuts = 2
    """Used to display the result of a Shortcut invocation."""

    Alert = 3
    """Used to display urgent messages (Mainly used for moderation)."""

    PlayerLogin = 4
    """Used to display login and logout notifications."""

    Invasion = 5
    """Used to display invasion notifications."""

    TabDescription = 6
    """Used to display a small description about the selected tab in the chat display."""

    Halloween = 7
    """Used to display spooky messages at halloween."""

    Winter = 8
    """Used to display festive messages at winter."""

    Surprise = 9
    """Used to display game wide surprises to Toons."""
