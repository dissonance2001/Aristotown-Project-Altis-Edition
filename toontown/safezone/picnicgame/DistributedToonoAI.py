import collections
import itertools
import random
from typing import Dict, List

from direct.task.TaskManagerGlobal import taskMgr

from otp.ai.AIBaseGlobal import simbase
from toontown.quest3.SpecialQuestZones import SpecialQuestZones
from toontown.safezone.ChairConstants import MusicTypeEnum
from toontown.safezone.picnicgame import ToonoGlobals
from toontown.safezone.picnicgame.DistributedPicnicGameAI import DistributedPicnicGameAI


PlayerCards = Dict[int, ToonoGlobals.ToonoCard]


class DistributedToonoAI(DistributedPicnicGameAI):

    def __init__(self, air, table, houseRules, musicType=MusicTypeEnum.DEFAULT, 
                 specialZone: SpecialQuestZones=None) -> None:
        super().__init__(air, table, specialZone)

        self.globalCardIndex = 0

        self.turnTime = 30
        self.playerCards: PlayerCards = {}
        self.musicType = musicType

        # Keep track of the last played card.
        self.lastPlayedCard: ToonoGlobals.ToonoCard = None

        self.wildCardDrawn: ToonoGlobals.ToonoCard = None
        self.drawPlayChoiceCard: ToonoGlobals.ToonoCard = None

        self.playerJumpedIn = None
        self.allowJumpIn = False

        self.unoCall = None

        self.playerTimedOut = False
        self.currentPlayerPlayed = False
        self.currentPlayerDrew = False
        self.currentPlayerChose = False
        self.currentPlayerSwapped = False

        self.playType = None

        self.currentColor = 0

        self._pendingGiveCards = None
        self.pendingCardsModified = False

        # House rules.
        self.drawUntilPlay = houseRules.get("drawUntilPlay", False)
        self.sevenZeroes = houseRules.get("sevenZeroes", False)
        self.stacking = houseRules.get("stacking", False)
        self.autoPlay = houseRules.get("autoPlay", False)
        self.jumpIn = houseRules.get("jumpIn", False)

    def delete(self) -> None:
        self.clearTasks()

        self.playerCards = {}

        super().delete()

    def requestGameState(self) -> None:
        avId = simbase.air.getAvatarIdFromSender()
        if self.ratelimiter is None or self.ratelimiter.userBlocked(avId):
            return

        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if av is None:
            return

        gameState = [(p, self.convertCardDictToTuple(c)) for p, c in self.playerCards.items()]

        lastPlayedCard = [255, 255] if self.lastPlayedCard is None else self.lastPlayedCard.toTuple()

        self.sendUpdateToAvatarId(avId, "setGameState", [lastPlayedCard, gameState])

    def requestPlayCard(self, index: int) -> None:
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if not av:
            return

        # This avatar isn't the current player.
        if avId != self.currentPlayer and not self.allowJumpIn:
            return

        if avId not in self.playerCards:
            return

        # This card doesn't exist in this player's cards
        if index not in self.playerCards[avId]:
            return

        # The current player has already acted during their turn.
        if self.currentPlayerActed and not self.allowJumpIn:
            return

        # Someone has jumped in before.
        if self.allowJumpIn and self.playerJumpedIn is not None:
            return

        card: ToonoGlobals.ToonoCard = self.playerCards[avId][index]

        if not card.verify(self.currentColor, self.lastPlayedCard) or \
            (self.allowJumpIn and card != self.lastPlayedCard):
            return

        # Stop the end turn task to have it restarted when we want it to be.
        self.stopEndTurnTask()
        self.d_stopTimer()

        taskMgr.remove(self.uniqueName("canJumpIn"))

        if self.allowJumpIn:
            self.playerJumpedIn = avId
            self.currentPlayer = avId
            self.playerOrder.position = self.playerOrder.index(avId)

        # If jumping in is possible, give the other players a chance to do so for 5 seconds.
        # If after 5 seconds, nobody jumps in, THEN we can apply the card effect.
        if self.playerCanJumpIn(card):
            # Tell the beginTurn() function that we're going to
            # await a jump in from a player.
            self.playType = ToonoGlobals.PLAY_TYPES.JUMP_IN

            # Show the card being played on the client.
            # (show the action being played if its immediate)
            immediate = card.cardNumber in ToonoGlobals.IMMEDIATE_ACTIONS
            self.b_playCard(avId, card, index, immediate)
            self.waitToChangeTurn(1)
        else:
            self.playType = ToonoGlobals.PLAY_TYPES.PLAY_CARD

            displayJumpIn = self.allowJumpIn

            # Jumping in isn't possible, immediately apply the card's effect.
            if self.allowJumpIn:
                self.b_setAllowJumpIn(False, (card.cardIndex, card.toTuple()))

            if len(self.playerCards[avId]) > 1:
                cardAction = True
                changeTurnDelay = self.determineCardAction(avId, card)
            else:
                cardAction = False
                changeTurnDelay = 1

            # Show the card being played on the client.
            self.b_playCard(avId, card, index, jumpedIn=displayJumpIn)

            if not cardAction or (not card.wild and not
            (self.sevenZeroes and card.cardNumber == 7 and len(self.playerOrder) != 2)):
                self.waitToChangeTurn(changeTurnDelay)

    def determineCardAction(self, avId: int, card: ToonoGlobals.ToonoCard, drawPlay: bool = False) -> int:
        """Based on the card's color and number, determine what action to take.
        """
        changeTurnDelay = 1

        if card.wild:
            # This is a wild card, tell the player to input what color they'd
            # like to change to.
            self.waitToQueryColor(avId, card, drawPlay)
        elif self.sevenZeroes and (card.cardNumber == 0 or (card.cardNumber == 7 and len(self.playerOrder) == 2)):
            # Swaps all hands when the card played is a zero, or is a seven with 2 players active.
            self.waitToSwapAllHands(drawPlay)
            changeTurnDelay += 3
        elif self.sevenZeroes and card.cardNumber == 7:
            self.waitToQueryHandshake(avId, drawPlay)
        elif card.cardNumber == ToonoGlobals.COLORED_ACTIONS.DRAW_TWO:
            # Give the next player 2 cards.
            if self.playerTimedOut:
                delay = 3
            elif drawPlay:
                delay = 2
            else:
                delay = 1

            delay = self.attemptGiveCards(card, delay, 2)

            changeTurnDelay += delay
        elif card.cardNumber == ToonoGlobals.COLORED_ACTIONS.REVERSE:
            self.playerOrder.reverse()
            self.sendUpdate("reverseOrder", [])

            # If there are only two players currently here, let the player who
            # played the reverse card play again.
            if len(self.playerOrder) == 2:
                next(self.playerOrder)

            changeTurnDelay = 2
        elif card.cardNumber == ToonoGlobals.COLORED_ACTIONS.SKIP:
            # Increment the current player index now, so when the next turn
            # begins, it will skip the next player's turn.
            self.sendUpdate("skipPlayer", [next(self.playerOrder)])
            changeTurnDelay = 2

        return changeTurnDelay

    def requestColorChange(self, color: int, cardIndex: int) -> None:
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if not av:
            return

        # This isn't the current player.
        if avId != self.currentPlayer:
            return

        # The avatar id and the card doesn't match that of the wild card drawn.
        if (self.wildCardDrawn is None) or cardIndex != self.wildCardDrawn.cardIndex:
            return

        # The requested color isn't valid.
        if color not in list(ToonoGlobals.CARD_COLORS)[:4]:
            return

        delay = 4 if self.playerTimedOut else 2

        if self.wildCardDrawn.drawFour:
            delay += self.attemptGiveCards(self.wildCardDrawn, delay, 4)

        self.wildCardDrawn = None

        self.d_changeColor(color)

        taskMgr.remove(self.uniqueName("chooseRandomColor"))
        self.waitToChangeTurn(delay)

    def requestHandshake(self, handshakee: int) -> None:
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if not av:
            return

        # This isn't the current player.
        if avId != self.currentPlayer:
            return

        if handshakee not in self.players or handshakee == avId:
            return

        # The player already did a handshake.
        if self.currentPlayerSwapped:
            return

        self.currentPlayerSwapped = True

        # Swap the current player's cards with the handshakee.
        self.playerCards[handshakee], self.playerCards[avId] = \
            self.playerCards[avId], self.playerCards[handshakee]

        # Send the game state to the client.
        self.d_setCards(avId, [(av, self.convertCardDictToTuple(cards)) \
                               for av, cards in self.playerCards.items()], [avId, handshakee])

        # Let the client know about the swap.
        self.sendUpdate('successHandshake', [handshakee])

        # Stop the end turn task to have it restarted when we want it to be.
        self.stopEndTurnTask()
        self.d_stopTimer()

        taskMgr.remove(self.uniqueName("chooseRandomPlayer"))

        self.waitToChangeTurn(3)

    def requestUno(self) -> None:
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if not av:
            return

        if self.unoCall is not None:
            return

        if self.currentPlayer not in self.playerCards:
            return

        playerCards = self.playerCards[self.currentPlayer]
        lastCard = self.lastPlayedCard

        if not len(playerCards) == 1 and not \
            (len(playerCards) == 2 and any(card.verify(self.currentColor, lastCard) for card in playerCards.values())):
            return

        # Uno hasn't been called yet, make it this player.
        self.unoCall = avId

        self.sendUpdate("acceptUno", [avId])

    def requestDraw(self) -> None:
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if not av:
            return

        # This avatar isn't the current player.
        if avId != self.currentPlayer:
            return

        # Cannot give cards when stacking is forced.
        if self.pendingGiveCards is not None:
            return

        # This avatar already acted during their turn.
        if self.currentPlayerActed:
            return

        self.currentPlayerDrew = True

        # Stop the end turn task to have it restarted when we want it to be.
        self.stopEndTurnTask()
        self.d_stopTimer()

        self.playType = ToonoGlobals.PLAY_TYPES.DRAW_CARD

        if self.pendingGiveCards is not None:
            self.waitToGiveCards(*self.pendingGiveCards[:2])
            self.pendingGiveCards = None
        else:
            self.drawUntilPlayable()

    def sendPlayCardResponse(self, response: bool) -> None:
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if not av:
            return

        # This avatar isn't the current player.
        if avId != self.currentPlayer:
            return

        # Autoplay rule is currently in effect.
        if self.autoPlay:
            return

        # The current player has already acted during their turn.
        if self.currentPlayerChose:
            return

        self.currentPlayerChose = True

        taskMgr.remove(self.uniqueName("autoPlayChoice"))

        delay = 1
        if response:
            self.playType = ToonoGlobals.PLAY_TYPES.DRAW_CARD_PLAY

            self.setLastCardPlayed(self.drawPlayChoiceCard)

            delay += self.determineCardAction(avId, self.drawPlayChoiceCard)

            # Show the card being played on the client.
            self.sendUpdate("setPlayCardResponse", [response, self.drawPlayChoiceCard.cardIndex, avId])

            self.checkToAwaitTurnChange(self.lastPlayedCard, delay)
        else:
            self.playType = ToonoGlobals.PLAY_TYPES.DRAW_CARD_PASS

            self.drawCards(avId, [self.drawPlayChoiceCard])
            self.sendUpdate("setPlayCardResponse", [response, self.drawPlayChoiceCard.cardIndex, avId])

            self.waitToChangeTurn(delay)

        self.drawPlayChoiceCard = None

    def avatarExit(self, avId: int) -> None:
        if avId in self.playerCards:
            del self.playerCards[avId]

        super().avatarExit(avId)

    def d_setMusicType(self, musicType: int) -> None:
        self.sendUpdate("setMusicType", [musicType])

    def getMusicType(self) -> MusicTypeEnum:
        return self.musicType

    def d_changeColor(self, color: int) -> None:
        self.currentColor = color
        self.sendUpdate("changeColor", [color])

    def d_queryColorChange(self, avId: int, cardIndex: int) -> None:
        self.sendUpdate("queryColorChange", [avId, cardIndex])

    def d_queryHandshake(self, avId: int) -> None:
        self.sendUpdate("queryHandshake", [avId])

    def d_setFirstCardPlayed(self, card: ToonoGlobals.ToonoCard) -> None:
        self.sendUpdate("setFirstCardPlayed", [card.toTuple()])

    def b_playCard(self, avId: int, card: ToonoGlobals.ToonoCard, cardIndex: int,
                   cardEffect: bool=True, jumpedIn: bool=False) -> None:
        self.d_playCard(avId, cardIndex, cardEffect, jumpedIn)
        self.playCard(avId, card)

    def d_playCard(self, avId: int, cardIndex: int, cardEffect: bool=True, jumpedIn: bool=False) -> None:
        self.sendUpdate("playCard", [avId, cardIndex, cardEffect, jumpedIn])

    def playCard(self, avId: int, card: ToonoGlobals.ToonoCard) -> None:
        if avId in self.playerCards and card.cardIndex in self.playerCards[avId]:
            del self.playerCards[avId][card.cardIndex]

            self.currentPlayerPlayed = True
            self.setLastCardPlayed(card)

    def b_drawCards(self, avId: int, cards: List[ToonoGlobals.ToonoCard],
                    first: bool = False, preview: bool = True) -> None:
        # Cap the amount of cards drawn.
        if avId in self.playerCards:
            diff = (len(self.playerCards[avId]) + len(cards)) - ToonoGlobals.MAX_CARDS
            if diff > 0:
                cards = cards[:-diff]

        self.d_drawCards(avId, cards, first, preview)
        self.drawCards(avId, cards)

    def d_drawCards(self, avId: int, cards: List[ToonoGlobals.ToonoCard],
                    first: bool = False, preview: bool = True) -> None:
        self.sendUpdate("drawCards", [avId, self.convertCardListToTuple(cards), first, preview])

    def drawCards(self, avId: int, cards: List[ToonoGlobals.ToonoCard]) -> None:
        if avId in self.playerCards:
            self.playerCards[avId].update(self.convertCardListToDict(cards))

    def d_drawAndPlayCard(self, avId: int, card: ToonoGlobals.ToonoCard, autoPlay: bool) -> None:
        self.sendUpdate("drawAndPlayCard", [avId, [card.cardIndex, card.toTuple()], autoPlay])
        if autoPlay:
            self.setLastCardPlayed(card)
        else:
            self.drawPlayChoiceCard = card

    def d_setCards(self, avId: int, cards: PlayerCards, affectedPlayers: List[int]) -> None:
        self.sendUpdate("setCards", [avId, cards, affectedPlayers])

    def b_setAllowJumpIn(self, allowJumpIn: bool, card = (0, (255, 255))) -> None:
        self.d_setAllowJumpIn(allowJumpIn, card)
        self.setAllowJumpIn(allowJumpIn)

    def d_setAllowJumpIn(self, allowJumpIn: bool, card = (0, (255, 255))) -> None:
        self.sendUpdate("setAllowJumpIn", [allowJumpIn, card])

    def setAllowJumpIn(self, allowJumpIn: bool) -> None:
        self.allowJumpIn = allowJumpIn

    def attemptGiveCards(self, card: ToonoGlobals.ToonoCard, delay: int, cardAmt: int) -> int:
        nextPlayer = self.playerOrder.getNext()

        changeTurnDelay = delay

        # A draw two was drawn and the next player has one as well.
        if self.stacking and card.drawTwo and nextPlayer in self.playersHaveDrawTwo and \
            (self.pendingGiveCards is None or card.cardNumber in self.pendingGiveCards[2]):
            self.addPendingCards(delay, cardAmt, card)
            changeTurnDelay = 0
        # A draw four was drawn and the next player has one as well.
        elif self.stacking and card.drawFour and nextPlayer in self.playersHaveDrawFour and \
            (self.pendingGiveCards is None or card.cardType in self.pendingGiveCards[2]):
            self.addPendingCards(delay, cardAmt, card)
            changeTurnDelay = 0
        elif self.pendingGiveCards is not None:
            if any([x == y for x in (card.cardType, card.cardNumber) \
                    for y in self.pendingGiveCards[2]]):
                self.addPendingCards(delay, cardAmt, card)
                changeTurnDelay += self.pendingGiveCards[0]

            self.waitToGiveCards(delay, self.pendingGiveCards[1])
            self.pendingGiveCards = None
        else:
            self.waitToGiveCards(delay, cardAmt)

        return changeTurnDelay

    def addPendingCards(self, delay: int, cardAmt: int, card: ToonoGlobals.ToonoCard) -> None:
        if self.pendingGiveCards is None:
            self._pendingGiveCards = [delay, cardAmt, card.toTuple()]
        else:
            self._pendingGiveCards[0] += delay
            self._pendingGiveCards[1] += cardAmt
        self.pendingCardsModified = True
        self.pendingGiveCards = self._pendingGiveCards

    def waitToGiveCards(self, delay: int, cardAmt: int, currentPlayer: bool = False) -> None:
        taskName = self.uniqueName("waitToGiveCards")
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(delay, self.giveCards, taskName, extraArgs = [cardAmt, currentPlayer])

    def giveCards(self, cardAmt: int, currentPlayer: bool) -> None:
        if not currentPlayer:
            # Making the next player draw cards means that they have to skip
            # their turn.
            # Advance the player order now, so when the next turn
            # begins, it will skip the next player's turn.
            player = next(self.playerOrder)
        else:
            player = self.currentPlayer

        self.b_drawCards(player, self.generateCards(cardAmt), preview = False)

    def waitToQueryColor(self, avId: int, card: ToonoGlobals.ToonoCard, drawPlay: bool = False) -> None:
        taskName = self.uniqueName("waitToQueryColor")
        taskMgr.remove(taskName)

        delay = 2 if drawPlay else 1
        taskMgr.doMethodLater(delay, self.queryColorChange, taskName, extraArgs = [avId, card])

    def queryColorChange(self, avId: int, card: ToonoGlobals.ToonoCard) -> None:
        self.turnEndTime = globalClock.getFrameTime() + self.turnTime
        self.d_setTimerEnd()

        self.wildCardDrawn = card

        self.d_queryColorChange(avId, card.cardIndex)

        taskMgr.doMethodLater(self.turnTime, self.chooseRandomColor, self.uniqueName("chooseRandomColor"))

    def waitToQueryHandshake(self, avId: int, drawPlay: bool = False) -> None:
        taskName = self.uniqueName("waitToQueryHandshake")
        taskMgr.remove(taskName)

        delay = 2 if drawPlay else 1
        taskMgr.doMethodLater(delay, self.queryHandshake, taskName, extraArgs = [avId])

    def queryHandshake(self, avId: int) -> None:
        self.turnEndTime = globalClock.getFrameTime() + self.turnTime
        self.d_setTimerEnd()

        self.d_queryHandshake(avId)

        taskMgr.doMethodLater(self.turnTime, self.chooseRandomPlayer, self.uniqueName("chooseRandomPlayer"))

    def waitToSwapAllHands(self, drawPlay: bool = False) -> None:
        taskName = self.uniqueName("waitToSwapAllHands")
        taskMgr.remove(taskName)

        delay = 2 if drawPlay else 1
        taskMgr.doMethodLater(delay, self.swapAllHands, taskName, extraArgs = [])

    def swapAllHands(self) -> None:
        self.playerCards = self.dictRoll(self.playerCards, self.playerOrder.delta)
        self.d_setCards(self.currentPlayer, [(avId, self.convertCardDictToTuple(cards)) \
                                             for avId, cards in self.playerCards.items()], self.players)
        self.sendUpdate('notifyDeckRotate', [])

    def setCurrentPlayer(self, avId: int) -> None:
        self.currentPlayerPlayed = False
        self.currentPlayerDrew = False
        self.currentPlayerChose = False
        self.currentPlayerSwapped = False

        super().setCurrentPlayer(avId)

    def drawRandomCard(self, includeActions: bool = True) -> ToonoGlobals.ToonoCard:
        if ToonoGlobals.FORCE_PICK:
            return self.drawRandomCardDebug()

        cards = []

        colors = list(ToonoGlobals.CARD_COLORS)[:4]
        numbers = list(range(10))
        actions = list(ToonoGlobals.COLORED_ACTIONS)

        # Add a card for every possible color number pair.
        cards.extend(list(itertools.product(colors, numbers)))

        if includeActions:
            # Add the wild cards.
            cards.extend([(wild, 100) for wild in list(ToonoGlobals.CARD_COLORS)[4:]])

            # Add a colored action card for every color.
            cards.extend(list(itertools.product(colors, actions)))

        self.globalCardIndex += 1
        if self.globalCardIndex >= 4294967295:
            self.globalCardIndex = 0

        card = random.choice(cards)
        return ToonoGlobals.ToonoCard(*card, self.globalCardIndex)

    def drawRandomCardDebug(self) -> ToonoGlobals.ToonoCard:
        """Used for testing."""
        cards = []

        colors = list(ToonoGlobals.FORCE_COLORS)
        wilds = list(ToonoGlobals.FORCE_WILDS)
        numbers = list(ToonoGlobals.FORCE_NUMBERS)
        actions = list(ToonoGlobals.FORCE_ACTIONS)

        # Add a card for every possible color number pair.
        if colors and numbers:
            cards.extend(list(itertools.product(colors, numbers)))

        # Add the wild cards.
        if wilds:
            cards.extend([(wild, 100) for wild in list(wilds)])

        # Add a colored action card for every color.
        if colors and actions:
            cards.extend(list(itertools.product(colors, actions)))

        self.globalCardIndex += 1
        if self.globalCardIndex >= 4294967295:
            self.globalCardIndex = 0

        card = random.choice(cards)
        return ToonoGlobals.ToonoCard(*card, self.globalCardIndex)

    def generateCards(self, amount: int) -> List[ToonoGlobals.ToonoCard]:
        return [self.drawRandomCard() for _ in range(amount)]

    def checkToAwaitTurnChange(self, card: ToonoGlobals.ToonoCard, delay: int) -> None:
        if not card.wild and \
           not (self.sevenZeroes and card.cardNumber == 7 and len(self.playerOrder) != 2):
            self.waitToChangeTurn(delay)

    def waitToChangeTurn(self, delayTime: int) -> None:
        taskName = self.uniqueName("waitToChangeTurn")
        taskMgr.remove(taskName)

        def beginTurn(task):
            if self.playerTimedOut:
                self.beginTurn(task)
            else:
                self.beginTurn()

        taskMgr.doMethodLater(delayTime, beginTurn, taskName)

    def beginTurn(self, task = None) -> None:
        # Get a list of any potential winners, with the win condition being that
        # they have zero cards remaining.
        winners = [avId for avId, cards in self.playerCards.items() if len(cards) == 0]

        if winners:
            # There are winners, only use the first winner because obviously
            # there shouldn't be multiple winners in TOONO.
            self.declareWinner(winners[0])
        elif self.unoCall not in (self.currentPlayer, None) and len(self.playerCards.get(self.currentPlayer, [])) == 1:
            # If the current player has one card left after playing, the other
            # players had a chance to call out their uno before this player could.
            # If that is the case, make them draw 2 cards.

            self.b_drawCards(self.currentPlayer, self.generateCards(2), preview = False)

            self.stopEndTurnTask()
            self.d_stopTimer()
            self.waitToChangeTurn(3)
        elif task is not None and not self.playerTimedOut and not self.currentPlayerActed:
            self.playerTimedOut = True

            # Stop the end turn task to have it restarted when we want it to be.
            self.stopEndTurnTask()
            self.d_stopTimer()

            if self.pendingGiveCards is not None:
                self.waitToGiveCards(1, self.pendingGiveCards[1], currentPlayer = True)
                self.waitToChangeTurn(1 + self.pendingGiveCards[0])
                self.pendingGiveCards = None
            else:
                # This method was called by the task, meaning that the player didn't
                # choose to play a card. Give them a card.
                self.drawUntilPlayable()
        elif not self.playerTimedOut and self.pendingGiveCards is not None and not self.pendingCardsModified:
            # Stop the end turn task to have it restarted when we want it to be.
            self.stopEndTurnTask()
            self.d_stopTimer()

            # The current player could have jumped in but didn't,
            # give them the cards accumulated.
            self.waitToGiveCards(*self.pendingGiveCards[:2], currentPlayer = True)
            self.waitToChangeTurn(1 + self.pendingGiveCards[0])

            self.pendingGiveCards = None
        elif self.currentPlayer in self.playerCards and len(self.playerCards[self.currentPlayer]) > 0 and \
            self.playerCanJumpIn(self.lastPlayedCard) and not self.allowJumpIn and \
                self.playType == ToonoGlobals.PLAY_TYPES.JUMP_IN:
            # We can enable jumping in if:
            # - The current player didn't play their winning card.
            # - Any of the players have the same card that was played.
            # - Jumping in hasn't already been enabled for this turn.

            # Stop the end turn task to have it restarted when we want it to be.
            self.stopEndTurnTask()
            self.d_stopTimer()

            jumpinTaskName = self.uniqueName("canJumpIn")
            taskMgr.remove(jumpinTaskName)

            def setCardEffect(immediate):
                # Set jump in to false for just the client to prevent a softlock.
                if self.allowJumpIn:
                    self.d_setAllowJumpIn(False, (self.lastPlayedCard.cardIndex, self.lastPlayedCard.toTuple()))

                # Apply card effect now if it's not immediate.
                if not immediate:
                    delay = self.determineCardAction(self.currentPlayer, self.lastPlayedCard)
                else:
                    delay = 0

                # Since we delayed the functionality of this card, show it
                # via this update.
                self.sendUpdate("showCardEffect")

                self.checkToAwaitTurnChange(self.lastPlayedCard, delay)

            # Display the playable cards for the player.
            self.b_setAllowJumpIn(True, (self.lastPlayedCard.cardIndex, self.lastPlayedCard.toTuple()))

            self.turnEndTime = globalClock.getFrameTime() + ToonoGlobals.JUMP_IN_TIME
            self.d_setTimerEnd()

            # Delay the functionality of the played card to allow the other
            # players to jump in. If someone else jumps in, the functionality
            # of this card will be overwritten.
            # If the effect was immediate, apply the action immediately instead.
            immediate = self.lastPlayedCard.cardNumber in ToonoGlobals.IMMEDIATE_ACTIONS
            if immediate:
                self.determineCardAction(self.currentPlayer, self.lastPlayedCard)

            taskMgr.doMethodLater(ToonoGlobals.JUMP_IN_TIME, setCardEffect, jumpinTaskName, extraArgs=[immediate])
        else:
            taskMgr.remove(self.uniqueName("canJumpIn"))

            if self.allowJumpIn:
                self.b_setAllowJumpIn(False, (self.lastPlayedCard.cardIndex, self.lastPlayedCard.toTuple()))

            self.playerTimedOut = False
            super().beginTurn(task)

        self.unoCall = None
        self.wildCardDrawn = None
        self.playerJumpedIn = None
        self.pendingCardsModified = False

    def drawUntilPlayable(self, task = None) -> None:
        """This function will be called to draw cards until a card is drawn which
        then can be played.
        """
        card = self.drawRandomCard()

        # Different drawing scenarios:
        # Autoplay is enabled, drawUntilPlay is enabled:
        # - Draws until a playable card is drawn, then auto play that card.
        # Autoplay is enabled, drawUntilPlay is disabled:
        # - Draws one card, then auto play that card if it's playable.
        # Autoplay is disabled, drawUntilPlay is enabled:
        # - Draws until a playable card is drawn, then ask to play that card.
        # Autoplay is disabled, drawUntilPlay is disabled:
        # - Draws a single card then ask to play if it's playable.

        taskMgr.remove(self.uniqueName("canJumpIn"))

        drawTaskName = self.uniqueName("drawAnotherCard")
        taskMgr.remove(drawTaskName)

        # If the card drawn can be played, do it.
        if card.verify(self.currentColor, self.lastPlayedCard):
            # If this player has less than the maximum amount of cards, dictate whether
            # they can choose based on the house rule.
            if self.currentPlayer in self.playerCards and \
                len(self.playerCards[self.currentPlayer]) < ToonoGlobals.MAX_CARDS:
                autoPlay = self.autoPlay
            else:
                # Otherwise, force autoplay as true.
                autoPlay = True

            if autoPlay:
                changeTurnDelay = self.determineCardAction(self.currentPlayer, card, drawPlay=True)
                if not card.wild:
                    changeTurnDelay += 1

                # Show the card being played on the client.
                self.d_drawAndPlayCard(self.currentPlayer, card, autoPlay)

                self.checkToAwaitTurnChange(card, changeTurnDelay)
            else:
                self.d_drawAndPlayCard(self.currentPlayer, card, autoPlay)

                # Stop the end turn task to have it restarted when we want it to be.
                self.stopEndTurnTask()
                self.d_stopTimer()

                autoPlayChoiceTask = self.uniqueName("autoPlayChoice")
                taskMgr.remove(autoPlayChoiceTask)
                taskMgr.doMethodLater(10, self.sendPlayCardResponse, autoPlayChoiceTask, extraArgs = [True])
        else:
            self.b_drawCards(self.currentPlayer, [card], preview = False)

            # The card can't be played, and drawUntilPlay is enabled, so continue
            # drawing until we get a card to play.
            if self.drawUntilPlay and self.currentPlayer in self.playerCards and \
                len(self.playerCards[self.currentPlayer]) < ToonoGlobals.MAX_CARDS:
                taskMgr.doMethodLater(1, self.drawUntilPlayable, drawTaskName)
            # The card can't be played, and drawUntilPlay is disabled,
            # just go to the next turn.
            else:
                self.waitToChangeTurn(1)

    def chooseRandomColor(self, task) -> None:
        color = random.choice(list(ToonoGlobals.CARD_COLORS)[:4])

        self.d_changeColor(color)

        self.waitToChangeTurn(3)

    def chooseRandomPlayer(self, task) -> None:
        # Choose a random player (that isn't the current player).
        players = [player for player in self.players if player != self.currentPlayer]
        delay = 1

        if players:
            player = random.choice(players)

            # Swap their cards.
            self.playerCards[self.currentPlayer], self.playerCards[player] = \
                self.playerCards[player], self.playerCards[self.currentPlayer]

            # Send the new game state to the client.
            self.d_setCards(self.currentPlayer, [(avId, self.convertCardDictToTuple(cards)) \
                                                 for avId, cards in self.playerCards.items()],
                            [self.currentPlayer, player])

            # Let the client know about the swap.
            self.sendUpdate('successHandshake', [player])

            # Set the delay to the max amount of cards in this exchange.
            maxCards = max([len(cards) for av, cards in self.playerCards.items() \
                            if av in (self.currentPlayer, player)])
            delay = self.getSwapHandsDelay(maxCards)

        self.waitToChangeTurn(delay)

    def clearTasks(self) -> None:
        for task in ("startFirstTurn", "waitToChangeTurn", "waitToGiveCards", "chooseRandomColor",
                     "waitToQueryColor", "drawAnotherCard", "chooseRandomPlayer", "waitToQueryHandshake",
                     "autoPlayChoice", "canJumpIn", "waitToSwapAllHands"):
            taskMgr.remove(self.uniqueName(task))

    def setLastCardPlayed(self, card: ToonoGlobals.ToonoCard) -> None:
        self.lastPlayedCard = card
        self.currentColor = card.cardType
    
    def playerCanJumpIn(self, currentCard: ToonoGlobals.ToonoCard) -> bool:
        """Determine if any of the players can jump in on the given card.

        Draw 2 or Draw 4 cards are excluded because of bad synergies
        with stacking rules. :smile:
        """
        return self.jumpIn and self.playerJumpedIn is None and \
            not currentCard.drawTwo and not currentCard.drawFour and \
            any([card == currentCard and card.cardIndex != currentCard.cardIndex \
                for cards in self.playerCards.values() for card in cards.values()])

    """
    FSM states
    """

    def enterPlaying(self) -> None:
        # Put the initial card on the table. (and don't have it be a wild card)
        self.setLastCardPlayed(self.drawRandomCard(includeActions = False))
        self.d_setFirstCardPlayed(self.lastPlayedCard)

        # Choose a random player to start with.
        pos = random.choice(range(len(self.players)))
        self.playerOrder.setStartPos(pos)

        self.playerCards = {player: {} for player in self.players}

        for player in self.players:
            cards = self.generateCards(ToonoGlobals.START_CARDS)
            self.b_drawCards(player, cards, first = True)

        taskMgr.doMethodLater(6, super().enterPlaying, self.uniqueName("startFirstTurn"), extraArgs=[])

    def exitPlaying(self) -> None:
        self.clearTasks()

        super().exitPlaying()

    """
    Properties
    """

    @property
    def currentPlayerActed(self) -> bool:
        """Determine if the current player has acted during their turn, either
        by drawing or playing a card.
        """
        return self.currentPlayerPlayed or self.currentPlayerDrew or self.currentPlayerChose or \
               self.playerTimedOut or self.currentPlayerSwapped

    @property
    def playersHaveDrawTwo(self) -> bool:
        return [avId for avId, cards in self.playerCards.items() if any([card.drawTwo for card in cards.values()])]

    @property
    def playersHaveDrawFour(self) -> bool:
        return [avId for avId, cards in self.playerCards.items() if any([card.drawFour for card in cards.values()])]

    @property
    def playerRewards(self) -> Dict[int, int]:
        rewards = super().playerRewards

        # Increase rewards gradually every 75 turns.
        rewardMult = min(1.0 + (0.5 * (self.turns // 75)), 10.0)

        # Verbosely create the dict because we're on python 3.6
        retdict = {}
        for avId in rewards:
            retdict[avId] = round(rewards[avId] * rewardMult)
        return retdict

    @property
    def pendingGiveCards(self) -> Dict:
        return self._pendingGiveCards

    @pendingGiveCards.setter
    def pendingGiveCards(self, _pendingGiveCards) -> None:
        """Set the currently pending cards to give out.

        This is dedicated to a setter function for the extended
        functionality of updating the flash mode every time we're
        called, or every time this variable is updated.
        """
        self._pendingGiveCards = _pendingGiveCards

        # Set the current flash mode.
        # This dictates what type of card that should be flashing for the
        # current player. (for stacking)
        if self.stacking:
            if not self._pendingGiveCards:
                flashMode = 0
            elif self._pendingGiveCards[2][0] == ToonoGlobals.CARD_COLORS.WILD_FOUR:
                flashMode = 1
            else:
                flashMode = 2

            self.sendUpdate("setFlashMode", [flashMode])

    """
    Static Methods
    """

    @staticmethod
    def convertCardDictToTuple(cards: PlayerCards):
        return [(index, (card.cardType, card.cardNumber)) for index, card in cards.items() if card is not None]

    @staticmethod
    def convertCardListToDict(cards: List[ToonoGlobals.ToonoCard]) -> Dict[int, ToonoGlobals.ToonoCard]:
        return {card.cardIndex: card for card in cards if card is not None}

    @staticmethod
    def convertCardListToTuple(cards: List[ToonoGlobals.ToonoCard]):
        return [(card.cardIndex, (card.cardType, card.cardNumber)) for card in cards if card is not None]

    @staticmethod
    def dictRoll(dct, n):
        # shift dct (dict) values by n to right if n is positive
        # and to left if n is negative; returns new dictionary
        shiftValues = collections.deque(dct.values())
        shiftValues.rotate(n)
        return dict(zip(dct.keys(), shiftValues))

    @staticmethod
    def getSwapHandsDelay(cards: int) -> float:
        """Get the total time it should take for the given
        amount of cards to be swapped.
        """
        return 1 + (cards * (cards ** -0.4))
