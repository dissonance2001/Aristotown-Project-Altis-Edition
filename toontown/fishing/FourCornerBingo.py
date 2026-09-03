from toontown.fishing import BingoGlobals
from toontown.fishing import BingoCardBase
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class FourCornerBingo(BingoCardBase.BingoCardBase):
    """
    FourCornerBingo(BingoCardBase)

    Provide a base layout of the bingo card which can be used in a variety of games.
    """

    corners = [
        0,
        BingoGlobals.CARD_ROWS - 1,
        BingoGlobals.CARD_COLS * (BingoGlobals.CARD_ROWS - 1),
        BingoGlobals.CARD_COLS * BingoGlobals.CARD_ROWS - 1
    ]

    def __init__(self, cardSize = BingoGlobals.CARD_SIZE, rowSize = BingoGlobals.CARD_ROWS, colSize = BingoGlobals.CARD_COLS):
        """
        This method provides initial construction of the Card.
        It determines if the card is of a valid size, and that it is square.
        Checking of a non-square card is impossible for diagonal cases.

        :param cardSize: The size of the card rowSize x colSize.
        :param rowSize: The number of rows in the card.
        :param colSize: The number of cols in the card.
        """
        BingoCardBase.BingoCardBase.__init__(self, cardSize, rowSize, colSize)
        self.gameType = BingoGlobals.FOURCORNER_CARD

    def checkForWin(self, id):
        """
        This method checks if there was a win after the last cell update.
        It calls all of the game logic methods which are required to determine a win.

        :param id: The ID Number of the cell to Check.
        :return: 0 [NO_UPDATE] | 2 [WIN]
        """
        corners = self.corners
        if self.cellCheck(corners[0]) and self.cellCheck(corners[1]) \
                and self.cellCheck(corners[2]) and self.cellCheck(corners[3]):
            return BingoGlobals.WIN
        return BingoGlobals.NO_UPDATE

    def checkForColor(self, id):
        """
        This method determines if a specified cell ID should be a particular color.

        :param id: The ID Number of the cell to Check.
        :return: 1 if on a corner, 0 if it is not
        """
        topLeft, topRight, bottomLeft, bottomRight = (0, 0, 0, 0)
        if id == self.corners[0]:
            topLeft = 1
        elif id == self.corners[1]:
            topRight = 1
        elif id == self.corners[2]:
            bottomLeft = 1
        elif id == self.corners[3]:
            bottomRight = 1
        return topLeft or topRight or bottomLeft or bottomRight

    def checkForBingo(self):
        """
        This method checks if there was a win after the last cell update.
        It calls all of the game logic methods which are required to determine a win.

        :return: 0 [NO_UPDATE] | 2 [WIN]
        """
        return self.checkForWin(0)
