import math
from time import time
from typing import List, Dict, Union, Optional

from direct.distributed.ClockDelta import globalClockDelta
from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.fsm.FSM import FSM
from direct.showbase.MessengerGlobal import messenger
from direct.task.TaskManagerGlobal import taskMgr

from otp.ai.AIBaseGlobal import simbase
#from toontown.groups.GroupEnums import GroupType
from toontown.quest3.SpecialQuestZones import SpecialQuestZones
from toontown.quest3.context.PicnicGameContext import PicnicGameContext
from toontown.safezone.picnicgame.BoardGameGlobals import REWARD_TIME_LIMIT, REWARD_TURN_LIMIT
from toontown.safezone.picnicgame.PicnicGameGlobals import PicnicGame, PlayerOrder, PGT_BASE_BEANS, PGT_WINNER_MULT, \
    PGT_PLAYER_LIMITS
from toontown.utils import AIUtil
from toontown.utils.RateLimiter import IdRateLimiter


class DistributedPicnicGameAI(DistributedNodeAI, FSM):

    def __init__(self, air, table, specialZone: Optional[SpecialQuestZones] = None) -> None:
        DistributedNodeAI.__init__(self, air)
        FSM.__init__(self, self.__class__.__name__)

        self.table = table
        self.gameType: PicnicGame = self.table.chosenGame

        self.players = self.table.playerList[:]
        self.spectators = self.table.spectators[:]
        self.tableDoId = self.table.doId

        self.playerOrder = PlayerOrder(self.players)

        self.currentPlayer: int = 0

        # How long should each turn last for?
        self.turnTime: int = 0
        self.turnEndTime: Optional[int] = None

        # PASS = the player doesn't play during their turn and the timer runs out.
        # How many turns can any player pass until they're kicked off?
        self.maxPassTurns: int = 4
        # Keep track of how many turns each player has passed for.
        self.turnsPassed: Dict[int, int] = {}

        # Who won the game?
        self.winner: int = 0

        # Keeps track of the total amount of turns.
        self.turns: int = 0

        self.specialZone = specialZone

        self.ratelimiter = IdRateLimiter(1, 3)
        self.gameActionRatelimiter = IdRateLimiter(3, 1)

        # Keep track of the start of the game.
        self.gameStart = time()

    def delete(self) -> None:
        self.stopEndTurnTask()

        self.turnsPassed = {}

        self.players = []
        self.spectators = []
        self.tableDoId = None
        self.ratelimiter = None
        self.gameActionRatelimiter = None

        FSM.cleanup(self)
        super().delete()

    def getGameTime(self) -> float:
        """Calculate the amount of time in seconds spent on the current game."""
        return time() - self.gameStart

    def getGameType(self) -> int:
        return self.gameType

    def avatarEnter(self, avId: int) -> None:
        self.sendUpdate("avatarEnter", [avId])

    def avatarExit(self, avId: int) -> None:
        # Stop the game if there are fewer players than the game can possibly support.
        if len(self.players) < PGT_PLAYER_LIMITS[self.gameType][0]:
            # Let them win if enough turns and time has passed.
            if self.turns > REWARD_TURN_LIMIT and len(self.players) == 1 and self.getGameTime() > REWARD_TIME_LIMIT:
                self.declareWinner(self.players[0])
            else:
                # Otherwise, just have the table return to the boarding state
                # immediately.
                self.table.stopGame()
            return

        self.playerOrder.remove(avId)

        if avId == self.currentPlayer:
            self.beginTurn()

        self.sendUpdate("avatarExit", [avId])

    def b_setState(self, state: str) -> None:
        self.d_setState(state)
        self.setState(state)

    def d_setState(self, state: str) -> None:
        self.sendUpdate("setState", [state])

    def setState(self, state: str) -> None:
        self.request(state)

    def getState(self) -> str:
        return self.state

    def b_setPlayers(self, players: List[int]) -> None:
        self.d_setPlayers(players)
        self.setPlayers(players)

    def d_setPlayers(self, players: List[int]) -> None:
        self.sendUpdate("setPlayers", [players])

    def setPlayers(self, players: List[int]) -> None:
        self.players = players

    def getPlayers(self) -> List[int]:
        return self.players

    def b_setSpectators(self, spectators: List[int]) -> None:
        self.d_setSpectators(spectators)
        self.setSpectators(spectators)

    def d_setSpectators(self, spectators: List[int]) -> None:
        self.sendUpdate("setSpectators", [spectators])

    def setSpectators(self, spectators: List[int]) -> None:
        self.spectators = spectators

    def getSpectators(self) -> List[int]:
        return self.spectators

    def b_setCurrentPlayer(self, avId: int) -> None:
        self.d_setCurrentPlayer(avId)
        self.setCurrentPlayer(avId)

    def d_setCurrentPlayer(self, avId: int) -> None:
        self.sendUpdate("setCurrentPlayer", [avId])

    def setCurrentPlayer(self, avId: int) -> None:
        self.currentPlayer = avId

    def b_setWinner(self, avId: int) -> None:
        self.d_setWinner(avId)
        self.setWinner(avId)

    def d_setWinner(self, avId: int) -> None:
        self.sendUpdate("setWinner", [avId])

    def setWinner(self, avId: int) -> None:
        self.winner = avId

    def getTableDoId(self) -> int:
        return self.table.doId

    def beginTurn(self, task=None) -> None:
        # Increment the amount of turns.
        self.turns += 1

        # This is an easy way of telling whether this function was called by
        # the task or not. If it wasn't, the player successfully made a move
        # before the timer ran out.
        if self.currentPlayer in self.turnsPassed:
            if task is None:
                self.turnsPassed[self.currentPlayer] = 0
            else:
                # The timer ran out, increment their turns passed.
                self.turnsPassed[self.currentPlayer] += 1

                if self.turnsPassed[self.currentPlayer] >= self.maxPassTurns:
                    # Kick the player off for being inactive.
                    self.table.kickOffPlayer(self.currentPlayer)

        self.b_setCurrentPlayer(next(self.playerOrder))
        self.b_setTimerEnd()

        # Reset the task to change the turn.
        taskName = self.uniqueName("endTurn")
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(self.turnEndTime - globalClock.getFrameTime(), self.beginTurn, taskName)

    def stopEndTurnTask(self) -> None:
        taskMgr.remove(self.uniqueName("endTurn"))

    def b_setTimerEnd(self) -> None:
        self.setTimerEnd()
        self.d_setTimerEnd()

    def setTimerEnd(self) -> None:
        self.turnEndTime = globalClock.getFrameTime() + self.turnTime

    def d_setTimerEnd(self) -> None:
        self.sendUpdate("setTimerEnd", [globalClockDelta.localToNetworkTime(self.turnEndTime, bits=32)])

    def d_stopTimer(self) -> None:
        self.sendUpdate("stopTimer")

    def initTurnsPassed(self) -> None:
        self.turnsPassed = {avId: 0 for avId in self.players}

    def declareWinner(self, winner: int) -> None:
        if self.getCurrentOrNextState() == "Reward":
            return

        self.b_setWinner(winner)
        self.b_setState("Reward")

    def getZoneId(self) -> Union[int, SpecialQuestZones]:
        if self.specialZone is not None:
            return self.specialZone
        return self.zoneId

    """
    FSM states
    """

    def enterPrepareGame(self) -> None:
      #  if self.players:
       #     messenger.send('GroupManager-DisbandToonGroup', [
        #        self.players[0], [GroupType.TOONO, GroupType.Chess, GroupType.Checkers]
         #   ])

        taskMgr.doMethodLater(3, self.b_setState, self.uniqueName("requestPlaying"), extraArgs=["Playing"])

    def exitPrepareGame(self) -> None:
        taskMgr.remove(self.uniqueName("requestPlaying"))

    def enterPlaying(self) -> None:
        self.initTurnsPassed()
        self.beginTurn()

    def exitPlaying(self) -> None:
        self.stopEndTurnTask()

    def enterReward(self) -> None:
        rewards = self.playerRewards
        batcoins = self.batcoinRewards
        for avId in self.players:
            av = simbase.air.doId2do.get(avId)
            if av and avId in rewards:
                av.sendEarnMoneyAnimation(rewards[avId])
                av.addMoney(rewards[avId])
                av.giveBatcoins(batcoins)
                simbase.air.quest3Manager.progressObjective(
                    quester=av, context=PicnicGameContext(self.gameType, avId == self.winner, self.getZoneId()),
                )

        # Let's handle rewarding the players with club coins.

        # Get a list of player avatars.
        players = AIUtil.avIds2Avs(self.players)

        # Calculate the amount of club coins to give.
        clubCoins = 0.07 * min(5, math.ceil(self.turns / 8))

        # Reward the club coins.
        simbase.air.clubMgr.addClubCoinsForAvatars(players, clubCoins)

        taskMgr.doMethodLater(5, self.table.stopGame, self.uniqueName("requestBoarding"), extraArgs=[])

    def exitReward(self) -> None:
        taskMgr.remove(self.uniqueName("requestBoarding"))

    """
    Properties
    """

    @property
    def playerRewards(self) -> Dict[int, int]:
        baseBeans = PGT_BASE_BEANS
        turnMult = min(4, math.ceil(self.turns / 10))
        playersMult = 1 if len(self.players) <= 2 else 2
        winningMult = PGT_WINNER_MULT
        gameMult = 1.0 if self.gameType == PicnicGame.TOONO else 2.0

        # beans earned normal players
        beansEarned = baseBeans * turnMult * gameMult * playersMult
        # beans earned for winner
        winningBeans = beansEarned * winningMult

        return {avId: winningBeans if avId == self.winner else beansEarned for avId in self.players}

    @property
    def batcoinRewards(self) -> int:
        """
        Calculates how many batcoins should be awarded for this game
        :return: an int for batcoins this game generates
        """
        return round(7 * min(5, math.ceil(self.turns / 8)))
