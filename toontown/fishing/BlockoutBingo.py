from toontown.fishing import BingoGlobals
from toontown.fishing import BingoCardBase
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class BlockoutBingo(BingoCardBase.BingoCardBase):
    """
    BlockoutBingo(BingoCardBase)

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
        self.gameType = BingoGlobals.BLOCKOUT_CARD

    def checkForWin(self, id = 0):
        """
        This method checks if there was a win after the last cell update.
        It calls all of the game logic methods which are required to determine a win.

        :param int id: The ID Number of the cell to Check. (Default = 0)
        :return: 0 [NO_UPDATE] | 2 [WIN]
        """
        for i in range(self.rowSize):
            if not self.rowCheck(i):
                return BingoGlobals.NO_UPDATE
        return BingoGlobals.WIN

    def checkForColor(self, id):
        """
        This method determines if a specified cell ID should be a particular color.

        :param int id: The ID Number of the cell to Check.
        :return: 1 since this is normal bingo.
        """
        return 1

    def checkForBingo(self):
        """
        This method checks if there was a win after the last cell update.
        It calls all of the game logic methods which are required to determine a win.

        :return: 0 [NO_UPDATE] | 2 [WIN]
        """
        if self.checkForWin():
            return BingoGlobals.WIN
        return BingoGlobals.NO_UPDATE
