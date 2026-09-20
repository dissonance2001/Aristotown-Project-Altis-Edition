from toontown.quest3.base.QuestContext import QuestContext
from toontown.zone.entities.quest.QuestInteractibleGlobals import QuestInteractibleType


class InteractibleEntityContext(QuestContext):
    """
    Context for when an interactible entity is interacted with.
    """

    def __init__(self, interactibleType: QuestInteractibleType, zoneId: int) -> None:
        self.interactibleType = interactibleType
        self.zoneId = zoneId

    def getInteractibleType(self) -> QuestInteractibleType:
        return self.interactibleType

    def getZoneId(self) -> int:
        return self.zoneId
