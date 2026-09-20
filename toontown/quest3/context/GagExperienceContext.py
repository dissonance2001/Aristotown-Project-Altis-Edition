from toontown.quest3.base.QuestContext import QuestContext


class GagExperienceContext(QuestContext):
    """
    Context for when a Toon takes a swim.
    """
    def __init__(self, track: int, experience: int) -> None:
        self.track = track
        self.experience = experience

    def getTrack(self) -> int:
        return self.track

    def getExperience(self) -> int:
        return self.experience
