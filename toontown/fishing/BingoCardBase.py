from toontown.fishing import FishGlobals
from toontown.fishing import BingoGlobals
from direct.showbase import RandomNumGen

from toontown.fishing.FishingRodCompat import FishingRodItemType  # TODO: swap to toontown.inventory.enums.ItemEnums once ported
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class BingoCardBase:
    """
    BingoCardBase

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
        self.rowSize = rowSize
        self.colSize = colSize
        self.cardSize = cardSize
        self.cellList = []
        self.gameType = None
        self.gameState = 1 << int(self.cardSize // 2)

    def destroy(self):
        """
        This method cleans up the Card.
        """
        del self.cellList

    def generateCard(self, tileSeed, zoneId):
        """
         This method generates the actual card, and is based-on the tileSeed that is provided by the AI
        and the zoneId which is obtained from the pond.

        :param tileSeed: Seed for the RNG to generate the same fish as those found on the AI Card.
        :param zoneId: Needed to choose the appropriate fish for the pond that the card instance is associated with.
        """
        rng = RandomNumGen.RandomNumGen(tileSeed)

        # Retrieve a list of Fish based on the Genus Type. Each Genus
        # found in the pond will be represented on the board.
        fishList = FishGlobals.getPondGeneraList(zoneId)

        # Determine the number of cells left to fill.
        emptyCells = self.cardSize - 1 - len(fishList)

        rodSubtype = FishingRodItemType.Cardboard
        for i in range(emptyCells):
            fish = FishGlobals.getRandomFishVitals(zoneId, rodSubtype, rng)
            while not fish[0]:
                fish = FishGlobals.getRandomFishVitals(zoneId, rodSubtype, rng)

            fishList.append((fish[1], fish[2]))
            rodSubtype = FishingRodItemType(rodSubtype + 1)
            if rodSubtype > FishingRodItemType.Steel:
                rodSubtype = FishingRodItemType.Cardboard

        # Now, fill up the the card by randomly placing the fish in a cell.
        for index in range(self.cardSize):
            if index != int(self.cardSize // 2):
                choice = rng.randrange(0, len(fishList))
                self.cellList.append(fishList.pop(choice))
            else:
                self.cellList.append((None, None))

        return None

    def getGameType(self):
        """
        This method retrieves the game type of the Bingo card.

        :return: the type of the Bingo Card.
        """
        return self.gameType

    def getGameState(self):
        """
        This method retrieves the game state of the current Bingo card.

        :return: the current state of the Bingo Card.
        """
        return self.gameState

    def getCardSize(self):
        """
        This method retrieves the card size of the current Bingo Card.

        :return: the card size of the Bingo Card.
        """
        return self.cardSize

    def getRowSize(self):
        """
        This method retrieves the row size of the current Bingo Card.

        :return: the row size of the Bingo Card.
        """
        return self.rowSize

    def getColSize(self):
        """
        This method retrieves the col size of the current Bingo Card.

        :return: the col size of the Bingo Card.
        """
        return self.colSize

    def setGameState(self, state):
        """
        This method sets the game state of the current Bingo card.

        :param state: New State of the Card.
        """
        self.gameState = state

    def clearCellList(self):
        """
        This method clears the list of cells corresponding to this card.
        """
        del self.cellList
        self.cellList = []

    def cellUpdateCheck(self, id, genus, species):
        """
        This method checks to see if there was a successful update on a cell.
        If so, that cell should now become disabled and the
        checkForWin method is called in order to determine if the client has won.

        :param id: Cell ID to check against.
        :param genus: Genus of the fish to check against.
        :param species: Species of the fish to check against.
        :return: 0 [NO_UPDATE] | 1 [UPDATE] | 2 [WIN]
        """
        if id >= self.cardSize:
            self.notify.warning('cellUpdateCheck: Invalid Cell Id %s. Id greater than Card Size.')
            return
        elif id < 0:
            self.notify.warning('cellUpdateCheck: Invalid Cell Id %s. Id less than zero.')
            return
        fishTuple = (genus, species)
        if self.cellList[id][0] == genus or fishTuple == FishGlobals.BingoBoot:
            self.gameState = self.gameState | 1 << id
            if self.checkForWin(id):
                return BingoGlobals.WIN
            return BingoGlobals.UPDATE
        return BingoGlobals.NO_UPDATE

    def checkForWin(self, id):
        """
        This method is really just here as a base class method. It would be equivalent to a virtual class in C++.

        :param id: Cell ID to check against.
        """
        pass

    def rowCheck(self, rowId):
        """
        This method checks to determine if there there is a win in a particular row.

        :param rowId: The Id Number of the Row to Check.
        :return: 0 | 1
        """
        for colId in range(self.colSize):
            if not self.gameState & 1 << self.rowSize * rowId + colId:
                return 0
        return 1

    def colCheck(self, colId):
        """
        This method checks to determine if a particular column has been filled out.
        Not a part of traditional bingo, but may be used for bonuses or such.

        :param colId: The Id Number of the Column to Check.
        :return: 0 | 1
        """
        for rowId in range(self.rowSize):
            if not self.gameState & 1 << self.rowSize * rowId + colId:
                return 0
        return 1

    def fDiagCheck(self, id):
        """
        This method checks along the forward diagonal of the Bingo Card square to determine if there was a win.
        The forward diagonal consists of ids from 0 to (cardSize-1)

        :param id: The ID Number of the Cell to check.
        :return: 0 | 1
        """
        checkNum = self.rowSize + 1
        if not id % checkNum:
            for i in range(self.rowSize):
                if not self.gameState & 1 << i * checkNum:
                    return 0
            return 1
        else:
            return 0

    def bDiagCheck(self, id):
        """
        This method checks along the backward diagonal of the Bingo Card square to determine if there was a win.
        The forward diagonal consists of ids from 4 to (cardSize-rowSize)

        :param id: The ID Number of the Cell to check.
        :return: 0 | 1
        """
        checkNum = self.rowSize - 1
        if not id % checkNum and not id == self.cardSize - 1:
            for i in range(self.rowSize):
                if not self.gameState & 1 << i * checkNum + checkNum:
                    return 0
            return 1
        return 0

    def cellCheck(self, id):
        """
        Determines whether a cell is occupied or not.

        :param id: The ID Number of the Cell to check.
        :return: 1 or 0 based on whether the cell is occupied.
        """
        if self.gameState & 1 << id:
            return 1
        return 0

    def onRow(self, row, id):
        """
        Determines whether a cell is located on a specific row in the card.

        :param row: row to check against
        :param id: The ID Number of the Cell to check.
        :return: 1 or 0 whether cell is on the specified row.
        """
        if int(id // self.rowSize) == row:
            return 1
        return 0

    def onCol(self, col, id):
        """
        Determines whether a cell is located on a specific column in the card.

        :param col: column to check against
        :param id: The ID Number of the Cell to check.
        :return: 1 or 0 whether cell is on the specified column.
        """
        if id % BingoGlobals.CARD_COLS == col:
            return 1
        return 0

    def onFDiag(self, id):
        """
        Determines whether a cell is located on the forward diagonal of the card.

        :param id: The ID Number of the Cell to check.
        :return: 1 or 0 whether cell is on the Forward Diagonal
        """
        checkNum = self.rowSize + 1
        if not id % checkNum:
            return 1
        return 0

    def onBDiag(self, id):
        """
        Determines whether a cell is located on the backwards diagonal of the card.

        :param id: The ID Number of the Cell to check.
        :return: 1 or 0 whether cell is on the backward Diagonal
        """
        checkNum = self.rowSize - 1
        if not id % checkNum:
            return 1
        return 0
