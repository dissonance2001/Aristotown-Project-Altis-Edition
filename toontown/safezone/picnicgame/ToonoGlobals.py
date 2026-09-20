from enum import IntEnum

# How many cards should each player start with?
START_CARDS = 7

# How many cards can any player have at max?
MAX_CARDS = 20

# Enum for every color, or type that a card can be. This includes wild cards.
CARD_COLORS = IntEnum("CardColors", ("RED", "YELLOW", "GREEN", "BLUE", "WILD", "WILD_FOUR"), start = 0)

# Enum for colored action cards.
COLORED_ACTIONS = IntEnum("ColoredActions", ("DRAW_TWO", "SKIP", "REVERSE"), start = 10)

# Map each color to a string which can be used to help identify the card to
# create on the client.
COLOR_2_STRING = {
    CARD_COLORS.RED: "r",
    CARD_COLORS.YELLOW: "y",
    CARD_COLORS.GREEN: "g",
    CARD_COLORS.BLUE: "b",
    CARD_COLORS.WILD: "wild",
    CARD_COLORS.WILD_FOUR: "wild_draw4",
}

# Map each colored action to a string which can be used to help identify the
# card to create on the client.
ACTION_2_STRING = {
    COLORED_ACTIONS.DRAW_TWO: "draw2",
    COLORED_ACTIONS.SKIP: "skip",
    COLORED_ACTIONS.REVERSE: "reverse",
}

# Debug mode.
FORCE_PICK = False
FORCE_COLORS = (*CARD_COLORS,)
FORCE_WILDS = ()
FORCE_NUMBERS = (7,)
FORCE_ACTIONS = ()

# Actions which apply immediately regardless of jump-in
IMMEDIATE_ACTIONS = {
    COLORED_ACTIONS.REVERSE,
}

# All actions that the player can make in Toono.
PLAY_TYPES = IntEnum("PlayTypes", ("PLAY_CARD", "DRAW_CARD", "JUMP_IN", "DRAW_CARD_PLAY", "DRAW_CARD_PASS"))

# Minimum and maximum rotations for the cards.
CARD_MIN_R = -7
CARD_MAX_R = 7

COLOR_BUTTON_POS = (
    (0.0, 0.0, -0.45),
    (0.43, 0.0, 0.0),
    (0.0, 0.0, 0.45),
    (-0.43, 0.0, 0.0),
)

COLOR_BUTTON_COLOR = (
    (0.8, 0.15, 0.15, 1),  # R
    (0.8, 0.8, 0, 1),  # Y
    (0.1, 0.7, 0.3, 1),  # G
    (0.2, 0.4, 0.6, 1),  # B
)

STATUSES = IntEnum("ToonoStatuses", ("DRAW", "DRAW_2", "DRAW_4", "TOONO", "SKIPPED", "DRAW_AMT"))

# Map of every house rule with its default value.
DEFAULT_HOUSE_RULES = {
    "drawUntilPlay": False,
    "sevenZeroes": False,
    "stacking": False,
    "autoPlay": False,
    "jumpIn": False,
}

# The amount of time allotted to players to jump in.
JUMP_IN_TIME = 3


class ToonoCard:

    def __init__(self, cardType: int, cardNumber: int, cardIndex: int) -> None:
        self.cardType = int(cardType)
        self.cardNumber = int(cardNumber)
        self.cardIndex = cardIndex

    def __str__(self) -> str:
        return f"cardType={self.cardType}, cardNumber={self.cardNumber}, cardIndex={self.cardIndex}"

    def __eq__(self, other) -> bool:
        return (self.cardType == other.cardType and self.cardNumber == other.cardNumber)

    def toTuple(self):
        return (self.cardType, self.cardNumber)

    def verify(self, currentColor, lastCard) -> bool:
        if self.wild:
            return True
        elif self.cardType in (currentColor, lastCard.cardType) or self.cardNumber == lastCard.cardNumber:
            return True

        return False

    @property
    def wild(self) -> bool:
        return self.cardType in list(CARD_COLORS)[4:]

    @property
    def drawTwo(self) -> bool:
        return self.cardNumber == COLORED_ACTIONS.DRAW_TWO

    @property
    def drawFour(self) -> bool:
        return self.cardType == CARD_COLORS.WILD_FOUR
