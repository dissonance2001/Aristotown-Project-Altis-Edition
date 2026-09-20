from toontown.quest3.base.QuestContext import QuestContext


class ManualContext(QuestContext):
    """
    A quest context that the player generates manually.
    """

    def __init__(self, _id: int):
        self._id = _id

    def getId(self):
        return self._id
