from typing import Any


class ChatMessageSender:
    """
    Information about the entity which sent the message.
    """
    __slots__ = ("id", "name", "toon")

    def __init__(self, toonId: int, name: str, instance: Any):
        self.id: int = toonId
        """The ID of the toon or npc that sent the message."""

        self.name: str = name
        """The name of the toon or npc that sent the message."""

        self.toon: Any = instance
        """The instance of the toon that sent the message. This will be None on UD."""
