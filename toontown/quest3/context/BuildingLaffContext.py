"""
A module containing the contextual results for defeating Cog Buildings with a laff threshold.
"""
from toontown.quest3.base.QuestContext import QuestContext


class BuildingLaffContext(QuestContext):
    """
    Context when a building is killed and also checks your laff teehee
    """

    def __init__(self, zoneId: int, track: str, floors: int, laffRatio: int):
        self.zoneId = zoneId
        self.track = track
        self.floors = floors
        self.laffRatio = laffRatio
