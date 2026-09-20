from toontown.quest3.base.QuestContext import QuestContext


class CollectBarrelContext(QuestContext):
    """
    Context for when a Toon collects a barrel.
    """
    def __init__(self, healBarrels: int, gagBarrels: int, beanBarrels: int, zoneId: int) -> None:
        self.healBarrels = healBarrels
        self.gagBarrels = gagBarrels
        self.beanBarrels = beanBarrels
        self.zoneId = zoneId

    def getHealBarrels(self) -> int:
        return self.healBarrels

    def getGagBarrels(self) -> int:
        return self.gagBarrels

    def getBeanBarrels(self) -> int:
        return self.beanBarrels

    def getZoneId(self) -> int:
        return self.zoneId
