from direct.distributed.DistributedObjectAI import DistributedObjectAI

from toontown.fishing import BingoGlobals
from toontown.fishing import FishGlobals
from toontown.fishing.NormalBingo import NormalBingo
from toontown.fishing.ThreewayBingo import ThreewayBingo
from toontown.fishing.DiagonalBingo import DiagonalBingo
from toontown.fishing.BlockoutBingo import BlockoutBingo
from toontown.fishing.FourCornerBingo import FourCornerBingo
from toontown.fishing.PerimeterBingo import PerimeterBingo
from toontown.fishing.TBingo import TBingo
from toontown.fishing.CrossoutBingo import CrossoutBingo
from toontown.fishing.FourEdgeBingo import FourEdgeBingo
from toontown.fishing.CheckerboardBingo import CheckerboardBingo
from direct.distributed.ClockDelta import *
import random
from typing import TYPE_CHECKING

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository

RequestCard = {}
cardDict = {
    BingoGlobals.NORMAL_CARD:       NormalBingo,
    BingoGlobals.DIAGONAL_CARD:     DiagonalBingo,
    BingoGlobals.THREEWAY_CARD:     ThreewayBingo,
    BingoGlobals.FOURCORNER_CARD:   FourCornerBingo,
    BingoGlobals.BLOCKOUT_CARD:     BlockoutBingo,
    BingoGlobals.PERIMETER_CARD:    PerimeterBingo,
    BingoGlobals.T_CARD:            TBingo,
    BingoGlobals.CROSSOUT_CARD:     CrossoutBingo,
    BingoGlobals.FOUREDGES_CARD:    FourEdgeBingo,
    BingoGlobals.CHECKERBOARD_CARD:   CheckerboardBingo
}

@DirectNotifyCategory()
class DistributedPondBingoManagerAI(DistributedObjectAI):
    """
    DistributedPondBingoManagerAI(DistributedObjectAI)
    """

    def __init__(self, air):
        """
        :type air: ToontownAIRepository
        """
        DistributedObjectAI.__init__(self, air)
        self.air = air  # type: ToontownAIRepository
        self.bingoCard = None
        self.tileSeed = None
        self.typeId = None
        self.state = 'Off'
        self.canCall = False
        self.shouldStop = False
        self.lastUpdate = globalClockDelta.getRealNetworkTime()
        self.cardId = 0
        self.forceId = None

    def delete(self):
        # kill all of our tasks
        for taskName in (f'startWait{self.getDoId()}',
                         f'finishGame{self.getDoId()}',
                         f'turnOff{self.getDoId()}',
                         f'createGame{self.getDoId()}'):
            taskMgr.remove(taskName)
        # remove pond reference
        del self.pond
        # finish with superclass cleanup
        DistributedObjectAI.delete(self)

    def setPondDoId(self, pondId):
        self.pond = self.air.doId2do[pondId]

    def getPondDoId(self):
        return self.pond.getDoId()

    def updateGameState(self, gameState, cellId):
        pass

    def setCardState(self, cardId, typeId, tileSeed, gameState):
        pass

    def setState(self, state, timeStamp):
        pass

    def cardUpdate(self, cardId, cellId, genus, species):
        avId = self.air.getAvatarIdFromSender()
        spot = self.pond.hasToon(avId)
        if not spot:
            self.air.writeServerEvent('suspicious', avId, 'Toon tried to call bingo while not fishing!')
            return
        fishTuple = (genus, species)
        if (genus != spot.lastFish[1] or species != spot.lastFish[2]) and (spot.lastFish[0] != FishGlobals.BootItem):
            self.air.writeServerEvent('suspicious', avId, 'Toon tried to update bingo card with a fish they didn\'t catch!')
            return
        if cardId != self.cardId:
            self.air.writeServerEvent('suspicious', avId, 'Toon tried to update expired bingo card!')
            return
        if self.state != 'Playing':
            self.air.writeServerEvent('suspicious', avId, 'Toon tried to update while the game is not running!')
            return
        spot.lastFish = [None, None, None, None]
        result = self.bingoCard.cellUpdateCheck(cellId, genus, species)
        if result == BingoGlobals.WIN:
            self.canCall = True
            self.sendCanBingo()
            self.sendGameStateUpdate(cellId)
        elif result == BingoGlobals.UPDATE:
            self.sendGameStateUpdate(cellId)

    def enableBingo(self):
        self.createGame()

    def d_enableBingo(self):
        self.sendUpdate('enableBingo', [])

    def handleBingoCall(self, cardId):
        avId = self.air.getAvatarIdFromSender()
        spot = self.pond.hasToon(avId)
        if not self.canCall:
            self.notify.debug(f"avId {avId} attempted to claim BINGO when it was already claimed or the game wasn't"
                              " started. Strange.")
            return
        if not spot:
            self.air.writeServerEvent('suspicious', avId, 'Toon tried to call bingo while not fishing!')
            return
        if cardId != self.cardId:
            self.air.writeServerEvent('suspicious', avId, 'Toon tried to call bingo with an expired cardId!')
            return
        av = self.air.doId2do.get(avId)
        if av:
            av.d_announceBingo()
        self.rewardAll()
        self.canCall = False

    def setJackpot(self, jackpot):
        self.jackpot = jackpot

    def d_setJackpot(self, jackpot):
        self.sendUpdate('setJackpot', [jackpot])

    def b_setJackpot(self, jackpot):
        self.setJackpot(jackpot)
        self.d_setJackpot(jackpot)

    def activateBingoForPlayer(self, avId):
        self.sendUpdateToAvatarId(avId, 'setCardState', [self.cardId, self.typeId, self.tileSeed,
                                                         self.bingoCard.getGameState()])
        self.sendUpdateToAvatarId(avId, 'setState', [self.state, self.lastUpdate])
        self.canCall = True

    def sendStateUpdate(self):
        self.lastUpdate = globalClockDelta.getRealNetworkTime()
        for spot in self.pond.spots:
            if self.pond.spots[spot].avId is None or self.pond.spots[spot].avId == 0:
                continue
            avId = self.pond.spots[spot].avId
            self.sendUpdateToAvatarId(avId, 'setState', [self.state, self.lastUpdate])

    def sendCardStateUpdate(self):
        for spot in self.pond.spots:
            if self.pond.spots[spot].avId is None or self.pond.spots[spot].avId == 0:
                continue
            avId = self.pond.spots[spot].avId
            self.sendUpdateToAvatarId(avId, 'setCardState', [self.cardId, self.typeId, self.tileSeed,
                                                             self.bingoCard.getGameState()])

    def sendGameStateUpdate(self, cellId):
        for spot in self.pond.spots:
            if self.pond.spots[spot].avId is None or self.pond.spots[spot].avId == 0:
                continue
            avId = self.pond.spots[spot].avId
            self.sendUpdateToAvatarId(avId, 'updateGameState', [self.bingoCard.getGameState(), cellId])

    def sendCanBingo(self):
        for spot in self.pond.spots:
            if self.pond.spots[spot].avId is None or self.pond.spots[spot].avId == 0:
                continue
            avId = self.pond.spots[spot].avId
            self.sendUpdateToAvatarId(avId, 'enableBingo', [])

    def rewardAll(self):
        self.state = 'Reward'
        self.sendStateUpdate()
        for spot in self.pond.spots:
            if self.pond.spots[spot].avId is None or self.pond.spots[spot].avId == 0:
                continue
            av = self.air.doId2do.get(self.pond.spots[spot].avId)
            if av:
                # TODO: route through Altis's booster/gumball multiplier system (toontown.gumball.GumballGlobals.applyBoosters)
                # once jellybean boosters are wired up; straight jackpot payout, no multiplier, for now.
                reward = round(self.jackpot)
                av.addMoney(reward, False, wantBooster=False)
        if self.shouldStop:
            self.stopGame()
            return
        taskMgr.doMethodLater(5, DistributedPondBingoManagerAI.startWait, f'startWait{self.getDoId()}', [self])
        taskMgr.remove(f'finishGame{self.getDoId()}')

    def finishGame(self):
        self.state = 'GameOver'
        self.sendStateUpdate()
        if self.shouldStop:
            self.stopGame()
            return
        taskMgr.doMethodLater(5, DistributedPondBingoManagerAI.startWait, f'startWait{self.getDoId()}', [self])

    def stopGame(self):
        self.state = 'CloseEvent'
        self.sendStateUpdate()
        taskMgr.doMethodLater(10, DistributedPondBingoManagerAI.turnOff, f'turnOff{self.getDoId()}', [self])

    def turnOff(self):
        self.state = 'Off'
        self.sendStateUpdate()

    def startIntermission(self):
        self.state = 'Intermission'
        self.sendStateUpdate()
        taskMgr.doMethodLater(300, DistributedPondBingoManagerAI.startWait, f'startWait{self.getDoId()}', [self])

    def startWait(self):
        self.state = 'WaitCountdown'
        self.sendStateUpdate()
        taskMgr.doMethodLater(15, DistributedPondBingoManagerAI.createGame, f'createGame{self.getDoId()}', [self])

    def createGame(self):
        if not hasattr(self, 'pond') or self.pond.isDeleted():
            self.notify.warning("Pond or bingo manager not generated or already deleted: can't start a bingo game.")
            return self.requestDelete()

        self.canCall = False
        self.tileSeed = None
        self.typeId = None
        self.cardId += 1
        for spot in self.pond.spots:
            avId = self.pond.spots[spot].avId
            request = RequestCard.get(avId)
            if request:
                self.typeId, self.tileSeed = request
                del RequestCard[avId]
        if self.cardId > 65535:
            self.cardId = 0
        if not self.tileSeed:
            self.tileSeed = random.randrange(0, 65535)
        if self.typeId is None:
            self.typeId = random.choice(list(cardDict.keys()))
        if self.forceId is not None:
            self.typeId = self.forceId
        self.bingoCard = cardDict[self.typeId]()
        self.bingoCard.generateCard(self.tileSeed, self.pond.getArea())
        self.sendCardStateUpdate()
        self.b_setJackpot(BingoGlobals.getJackpot(self.typeId))
        self.state = 'Playing'
        self.sendStateUpdate()
        taskMgr.doMethodLater(BingoGlobals.getGameTime(self.typeId), DistributedPondBingoManagerAI.finishGame,
                              f'finishGame{self.getDoId()}', [self])
