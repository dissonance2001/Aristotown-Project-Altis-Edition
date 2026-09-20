from typing import List, Optional

from direct.distributed.ClockDelta import globalClockDelta
from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.fsm.FSM import FSM
from direct.task.TaskManagerGlobal import taskMgr

from otp.ai.AIBaseGlobal import simbase
from toontown.safezone.picnicgame import ToonoGlobals
from toontown.safezone.picnicgame.DistributedCheckersAI import DistributedCheckersAI
from toontown.safezone.picnicgame.DistributedChessAI import DistributedChessAI
from toontown.safezone.picnicgame.DistributedPicnicGameAI import DistributedPicnicGameAI
from toontown.safezone.picnicgame.DistributedToonoAI import DistributedToonoAI
from toontown.safezone.picnicgame.PicnicGameGlobals import PicnicGame, NUM_SEATS, PGT_PLAYER_LIMITS, BOARDING_TIME, \
    SEAT_INDEX_ORDER
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedPicnicGameTableAI(DistributedNodeAI, FSM):

    def __init__(self, air, tableNumber: int) -> None:
        DistributedNodeAI.__init__(self, air)
        FSM.__init__(self, "DistributedPicnicGameTableAI")

        # Identifier for each table.
        self.tableNumber = tableNumber

        self.seats = {}

        self.boardingEnd = None

        self.canBoard = True

        # The leader is the toon who is in charge of picking games and who gets to play the game.
        # This toon is determined by who joined the table first, and will change when that toon leaves.
        self.leader: int = 0

        # This is a list of every avatar id in the order that they joined the table.
        # This is used to determine who should be the leader.
        self.avIds = []

        # Keep track of the game that the leader has picked so that any toons
        # newly joining the table can be made aware of what's going on.
        self.chosenGame: int = -1

        # Keep track of every avatar due to start playing the game (including the leader).
        self.playerList = []

        # Keep track of every avatar who is not participating in the game.
        self.spectators = []

        # The distributed object dedicated to the game chosen created upon entering the playing state.
        self.game: Optional[DistributedPicnicGameAI] = None

        # Store the house rules to be toggled on/off when going to play TOONO.
        self.houseRules = ToonoGlobals.DEFAULT_HOUSE_RULES.copy()

        # A dict of user ids to tasks which when fired, enable the gui on their screen.
        self.joinBufferTasks = {}

    def delete(self) -> None:
        self.seats = {}

        self.boardingEnd = None

        self.ignoreAll()

        for task in self.joinBufferTasks.values():
            taskMgr.remove(task)

        self.joinBufferTasks = {}

        FSM.cleanup(self)
        DistributedNodeAI.delete(self)

    def prepDelete(self) -> None:
        self.canBoard = False
        seatIndices = list(self.seats.keys())
        for i in seatIndices:
            self.emptySeat(self.seats[i], i)

    def requestTableState(self) -> None:
        """Process the client's request for the current table state.
        """
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # The avatar doesn't exist.
        if av is None:
            return

        tableState = [(seatIndex, avId) for seatIndex, avId in self.seats.items()]

        self.sendUpdateToAvatarId(avId, "setTableState", [tableState])

    def requestBoard(self, seatIndex: int) -> None:
        """Receives a request from the client to fill the indicated seat index
        and handles it accordingly.
        """
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if av is None:
            return

        # The avatar is already seated.
        if avId in self.seats.values():
            return

        # This seat is currently occupied.
        if self.seats.get(seatIndex):
            self.rejectBoarder(avId)
            return

        # For whatever reason, the seat index isn't valid.
        if not (0 <= seatIndex < NUM_SEATS):
            self.rejectBoarder(avId)
            return

        # Make sure the table isn't cleaning up.
        if not self.canBoard:
            return

        # OK, they're good to go.
        self.acceptBoarder(avId, seatIndex)

    def requestExit(self) -> None:
        """
        Receives a request from the client to empty the indicated seat index
        and handles it accordingly.
        """
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if av is None:
            return

        # The avatar id isn't seated here.
        if avId not in self.seats.values():
            return

        for seatIndex, seatAvId in self.seats.items():
            if avId == seatAvId:
                self.acceptExiter(avId, seatIndex)
                self.isTableEmpty()
                break

    def requestChosenGame(self, gameChosen: int) -> None:
        """Receives a request from the client to change the current game chosen
        and handles it accordingly.
        """
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if av is None:
            return

        # The game index isn't valid or isn't being cleared.
        if not (-1 <= gameChosen < len(PicnicGame)):
            return

        self.b_setChosenGame(gameChosen)

    def requestPlayerList(self, players: List[int]) -> None:
        """
        Receives a request from the client to update the current player list.
        """
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if av is None:
            return

        # Only allow changes to the player list during the boarding state.
        if self.state != "Boarding":
            return

        # Set the list of players but make sure there aren't any duplicates.
        self.b_setPlayerList(sorted(set(players), key=lambda x: players.index(x)))

    def requestPlayGame(self) -> None:
        """Receives a request from the client to start the game chosen with the
        players chosen and handles it accordingly. This should only be called
        by the leader.
        """
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if av is None:
            return

        # Only the leader is allowed to start the game.
        if avId != self.leader:
            return

        # Check all the game specific stuff.
        if not self.allowGame:
            return

        # Everything looks OK, start the game.
        self.b_setState("Playing")

    def sendHouseRules(self, houseRuleData: List) -> None:
        """
        Receives a request from the client to update all the house rules. (TOONO)
        """
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if av is None:
            return

        # Only the leader can change house rules.
        if avId != self.leader:
            return

        houseRules = {houseRule: value for houseRule, value in houseRuleData}

        if not all([isinstance(houseRule, str) for houseRule in houseRules]):
            return

        self.houseRules.update(houseRules)

        self.d_setHouseRules(houseRuleData)

    def acceptBoarder(self, avId: int, seatIndex: int) -> None:
        # If the table is currently empty, begin the boarding state.
        if not self.seats:
            self.b_setState("Boarding")

        self.fillSeat(avId, seatIndex)

        # Add a hook that handles the case where the avatar exits
        # the district unexpectedly.
        self.acceptOnce(simbase.air.getAvatarExitEvent(avId),
                        self.handleUnexpectedExit, extraArgs=[avId, seatIndex])

        self.sendUpdate("fillSeat", [avId, seatIndex])

    def rejectBoarder(self, avId: int) -> None:
        self.sendUpdateToAvatarId(avId, "rejectBoard", [])

    def handleUnexpectedExit(self, avId: int, seatIndex: int) -> None:
        self.notify.warning(f"Avatar {avId} has unexpectedly disconnected.")
        self.acceptExiter(avId, seatIndex)
        self.isTableEmpty()

    def isTableEmpty(self) -> None:
        """If every seat of this table is empty, turn off.
        """
        # If all of our seats are empty, return to the off state.
        if not self.seats and self.getCurrentOrNextState() != "Off":
            self.request("Off")

    def kickOffPlayer(self, avId: int) -> None:
        """Function that should only really be called by the game to request
        a player be kicked off the table, most likely due to inactivity.
        """
        reverseSeats = {v: k for k, v in self.seats.items()}

        # This avatar isn't seated.
        if avId not in reverseSeats:
            return

        # This avatar isn't a player.
        if avId not in self.playerList:
            return

        seatIndex = reverseSeats[avId]

        self.acceptExiter(avId, seatIndex)
        self.isTableEmpty()

    def acceptExiter(self, avId: int, seatIndex: int) -> None:
        self.ignore(simbase.air.getAvatarExitEvent(avId))

        self.emptySeat(avId, seatIndex)
        self.sendUpdate("emptySeat", [avId, seatIndex])

    def removeJoinBufferTask(self, avId: int) -> None:
        task = self.joinBufferTasks.get(avId)
        if task is not None:
            taskMgr.remove(task)
            del self.joinBufferTasks[avId]

    def fillSeat(self, avId: int, seatIndex: int) -> None:
        if seatIndex in self.seats:
            return

        self.seats[seatIndex] = avId

        # There is no leader and there aren't any toons currently on the table,
        # make the toon joining the table the leader.
        if self.leader == 0 and len(self.avIds) == 0:
            self.b_setLeader(avId)
        else:
            self.spectators.append(avId)

        self.avIds.append(avId)

        # Inform any relevant guis of the new avatar entering after a few
        # seconds of buffer time.
        self.joinBufferTasks[avId] = taskMgr.doMethodLater(1.9, self.d_informAvatarEnter,
                                                           self.uniqueName(f"informAvatarEnter-{avId}"),
                                                           extraArgs=[avId, seatIndex])

        # Let the game know that an avatar has entered.
        if self.state == "Playing":
            self.game.b_setSpectators(self.spectators)
            self.game.avatarEnter(avId)

    def emptySeat(self, avId: int, seatIndex: int) -> None:
        if self.seats.get(seatIndex) != avId:
            return

        self.removeJoinBufferTask(avId)

        del self.seats[seatIndex]

        if avId in self.avIds:
            self.avIds.remove(avId)

        # The leader is leaving, pick a new one if there are any other
        # toons left on the table.
        if avId == self.leader:
            self.b_setLeader(self.avIds[0] if len(self.avIds) else 0)

        # If this person was a player, remove them from the list.
        if avId in self.playerList:
            self.playerList.remove(avId)
            self.b_setPlayerList(self.playerList[:])

        # Remove the avatar id from the spectator list.
        if avId in self.spectators:
            self.spectators.remove(avId)

        # If there are no more toons on the table, reset the chosen game.
        if len(self.avIds) == 0:
            self.b_setChosenGame(-1)

        # Dedicate a message to inform any relevant guis that this toon
        # has exited without having to use the message which animates them
        # hopping off of the seat.
        self.sendUpdate("informAvatarExit", [avId, seatIndex])

        # If there's a game currently going on, update the list of
        # players for the game.
        if self.state == "Playing":
            self.game.b_setPlayers(self.playerList)
            self.game.b_setSpectators(self.spectators)
            self.game.avatarExit(avId)

    def stopGame(self) -> None:
        self.b_setState("Boarding")

    def b_setChosenGame(self, gameChosen: int) -> None:
        self.d_setChosenGame(gameChosen)
        self.setChosenGame(gameChosen)

    def d_setChosenGame(self, gameChosen: int) -> None:
        self.sendUpdate("setChosenGame", [gameChosen])

    def setChosenGame(self, gameChosen: int) -> None:
        self.chosenGame = gameChosen

    def getChosenGame(self) -> int:
        return self.chosenGame

    def b_setLeader(self, avId: int) -> None:
        self.d_setLeader(avId)
        self.setLeader(avId)

    def d_setLeader(self, avId: int) -> None:
        self.sendUpdate("setLeader", [avId])

    def setLeader(self, avId: int) -> None:
        self.leader = avId

    def getLeader(self) -> int:
        return self.leader

    def b_setState(self, state: str) -> None:
        self.d_setState(state)
        self.setState(state)

    def d_setState(self, state: str) -> None:
        self.sendUpdate("setState", [state])

    def setState(self, state: str) -> None:
        self.request(state)

    def getState(self) -> str:
        return self.state

    def b_setPlayerList(self, players: List[int]) -> None:
        self.d_setPlayerList(players)
        self.setPlayerList(players)

    def d_setPlayerList(self, players: List[int]) -> None:
        self.sendUpdate("setPlayerList", [players])

    def setPlayerList(self, players: List[int]):
        self.playerList = players
        # Update the spectators based on the player list.
        self.spectators = [avId for avId in self.spectators if avId not in players]

    def getPlayerList(self) -> List[int]:
        return self.playerList

    def b_setTableNumber(self, tableNumber: int) -> None:
        self.d_setTableNumber(tableNumber)
        self.setTableNumber(tableNumber)

    def d_setTableNumber(self, tableNumber: int) -> None:
        self.sendUpdate("setTableNumber", [tableNumber])

    def setTableNumber(self, tableNumber: int) -> None:
        self.tableNumber = tableNumber

    def getTableNumber(self) -> int:
        return self.tableNumber

    def d_informAvatarEnter(self, avId: int, seatIndex: int) -> None:
        """
        Dedicate a message to inform any relevant guis that the indicated
        avatar has joined without having to use the message which animates them
        hopping onto the seat.
        """
        self.removeJoinBufferTask(avId)
        self.sendUpdate("informAvatarEnter", [avId, seatIndex])

    def d_setHouseRules(self, houseRuleData: List) -> None:
        self.sendUpdate("setHouseRules", [houseRuleData])

    @property
    def allowGame(self) -> bool:
        """To play the game chosen, there should be a valid amount of players chosen,
        and if it's a game that has a player max of less than the amount of seats,
        there should be at least one player on the other side.
        """
        if not (0 <= self.getChosenGame() < len(PicnicGame)):
            # The chosen game isn't valid.
            return False

        playerMin, playerMax = PGT_PLAYER_LIMITS[self.chosenGame]

        return playerMin <= len(self.playerList) <= playerMax

    """
    FSM states
    """

    def enterOff(self) -> None:
        # Empty all the seats when going into the off state.
        for seatIndex, avId in list(self.seats.items()):
            self.acceptExiter(avId, seatIndex)

        self.seats = {}

        # Reset the house rules.
        self.houseRules = ToonoGlobals.DEFAULT_HOUSE_RULES.copy()
        houseRuleData = [(houseRule, value) for houseRule, value in self.houseRules.items()]
        self.d_setHouseRules(houseRuleData)

    def enterBoarding(self) -> None:
        def requestOff():
            self.request("Off")

        # Begin the boarding timeout.
        taskMgr.doMethodLater(BOARDING_TIME, requestOff, self.uniqueName("PGT_BoardingTimeout"), extraArgs=[])
        self.boardingEnd = globalClock.getFrameTime() + BOARDING_TIME
        self.sendUpdate("setTimerEnd", [globalClockDelta.localToNetworkTime(self.boardingEnd)])

    def exitBoarding(self) -> None:
        self.boardingEnd = None
        taskMgr.remove(self.uniqueName("PGT_BoardingTimeout"))

    def enterPlaying(self) -> None:
        if self.chosenGame == PicnicGame.TOONO:
            # Have the player order be based on the seat index.
            seats = {avId: seat for seat, avId in self.seats.items() if avId in self.playerList}

            def sortPlayers(player: int) -> int:
                return SEAT_INDEX_ORDER[seats[player]]

            self.b_setPlayerList(sorted(list(seats), key=sortPlayers))

        if self.chosenGame == PicnicGame.CHECKERS:
            self.game = DistributedCheckersAI(simbase.air, self)
        elif self.chosenGame == PicnicGame.TOONO:
            self.game = DistributedToonoAI(simbase.air, self, self.houseRules)
        elif self.chosenGame == PicnicGame.CHESS:
            self.game = DistributedChessAI(simbase.air, self)
        else:
            return

        self.game.generateWithRequired(self.zoneId)
        self.game.b_setState("PrepareGame")

    def exitPlaying(self) -> None:
        self.game.requestDelete()
        self.game = None
