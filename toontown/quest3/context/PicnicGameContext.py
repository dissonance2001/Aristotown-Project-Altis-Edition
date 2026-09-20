from toontown.quest3.base.QuestContext import QuestContext
from toontown.safezone.picnicgame.PicnicGameGlobals import PicnicGame


class PicnicGameContext(QuestContext):
    """
    Context for when a Toon completes a picnic game.
    """
    
    def __init__(self, gameType: PicnicGame, hasWon: bool, zoneId: int) -> None:
        self.gameType = gameType
        self.hasWon = hasWon
        self.zoneId = zoneId

    def getGameType(self) -> PicnicGame:
        return self.gameType
    
    def getHasWon(self) -> bool:
        return self.hasWon
    
    def getZoneId(self) -> int:
        return self.zoneId
