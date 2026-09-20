from toontown.quest3.base.QuestContext import QuestContext


class StompGoonContext(QuestContext):
    """
    Context for when a goon is stomped.
    """

    def __init__(self, goonsStomped: int, zoneId: int) -> None:
        self.goonsStomped = goonsStomped
        self.zoneId = zoneId
    
    def getGoonsStomped(self) -> int:
        return self.goonsStomped
    
    def getZoneId(self) -> int:
        return self.zoneId
