from toontown.fishing import BingoGlobals
from toontown.fishing import BingoCardBase
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class CheckerboardBingo(BingoCardBase.BingoCardBase):
    """
    CheckerboardBingo(BingoCardBase)

    Provide a base layout of the bingo card which can be used in a variety of games.
    """

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
        self.gameType = BingoGlobals.CHECKERBOARD_CARD
        self.fDiagResult = 0
        self.bDiagResult = 0

    def checkForWin(self, id):
        """
        This method checks if there was a win after the last cell update.
        It calls all of the game logic methods which are required to determine a win.

        :param int id: The ID Number of the cell to Check.
        :return: 0 [NO_UPDATE] | 2 [WIN]
        """
        if self.fDiagCheck(id):
            self.fDiagResult = 1
        if self.bDiagCheck(id):
            self.bDiagResult = 1
        corners = [2, 10, 14, 22]
        if self.cellCheck(corners[0]) and self.cellCheck(corners[1]) \
            and self.cellCheck(corners[2]) and self.cellCheck(corners[3]) \
                and self.fDiagResult and self.bDiagResult:
            return BingoGlobals.WIN
        return BingoGlobals.NO_UPDATE

    def checkForColor(self, id):
        """
        This method determines if a specified cell ID should be a particular color.

        :param int id: The ID Number of the cell to Check.
        :return: 1 if on a corner, 0 if it is not
        """
        top, left, right, bottom = (0, 0, 0, 0)
        corners = [2, 10, 14, 22]
        if id == corners[0]:
            top = 1
        elif id == corners[1]:
            left = 1
        elif id == corners[2]:
            right = 1
        elif id == corners[3]:
            bottom = 1
        return top or left or right or bottom or self.onFDiag(id) | self.onBDiag(id)

    def checkForBingo(self):
        """
        This method checks if there was a win after the last cell update.
        It calls all of the game logic methods which are required to determine a win.

        :return: 0 [NO_UPDATE] | 2 [WIN]
        """
        id = self.cardSize // 2
        if self.checkForWin(id):
            return BingoGlobals.WIN
        return BingoGlobals.NO_UPDATE
