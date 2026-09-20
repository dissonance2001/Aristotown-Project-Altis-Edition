from toontown.quest3.base.QuestContext import QuestContext


class TossPieContext(QuestContext):
    """
    Context for when a pie is thrown.
    """
    
    def __init__(self, pieAmount: int, pieType: int, zoneId: int) -> None:
        self.pieAmount = pieAmount
        self.pieType = pieType
        self.zoneId = zoneId
    
    def getPieAmount(self) -> int:
        return self.pieAmount
    
    def getPieType(self) -> int:
        return self.pieType
    
    def getZoneId(self) -> int:
        return self.zoneId
