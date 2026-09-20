from toontown.quest3.base.QuestContext import QuestContext


class MoleStompContext(QuestContext):
    """
    Context for when a Toon stomps a red mole.
    """
    
    def __init__(self, molesStomped : int, zoneId: int) -> None:
        self.molesStomped  = molesStomped 
        self.zoneId = zoneId
    
    def getMolesStomped(self) -> int:
        return self.molesStomped 
    
    def getZoneId(self) -> int:
        return self.zoneId
