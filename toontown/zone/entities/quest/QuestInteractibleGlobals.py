from strenum import StrEnum


class QuestInteractibleType(StrEnum):
    TestCrate = 'test_crate'


QuestInteractibleNames = {
    QuestInteractibleType.TestCrate: "a Crate",
}
