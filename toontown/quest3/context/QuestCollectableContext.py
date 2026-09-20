from toontown.quest3.QuestEnums import QuestCollectable
from toontown.quest3.base.QuestContext import QuestContext


class QuestCollectableContext(QuestContext):

    def __init__(self, collectable: QuestCollectable):
        self.collectable = collectable

    def getCollectable(self) -> QuestCollectable:
        return self.collectable
