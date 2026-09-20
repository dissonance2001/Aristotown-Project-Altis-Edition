from toontown.quest3.base.QuestContext import QuestContext


class CatchingGameContext(QuestContext):
    """
    Context for when a Toon completes the catching game.
    """
    
    def __init__(self, fruits: int, zoneId: int) -> None:
        self.fruits = fruits
        self.zoneId = zoneId
    
    def getFruitsCollected(self) -> int:
        return self.fruits
    
    def getZoneId(self) -> int:
        return self.zoneId
