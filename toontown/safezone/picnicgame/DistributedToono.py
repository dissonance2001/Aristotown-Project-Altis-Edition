import random
from operator import attrgetter
from typing import Optional

from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.showbase.MessengerGlobal import messenger
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Point3, TextNode
from toontown.chat.constants.ChatGlobals import  CFSpeech, CFTimeout

from toontown.gui.game.condition.ConditionGlobals import ConditionState
from toontown.menu.MainMenuGui import MainMenuButton
from toontown.safezone.ChairConstants import MusicTypeEnum, musicEnum2Name
from toontown.safezone.picnicgame import PicnicGameGlobals
from toontown.safezone.picnicgame import ToonoGlobals
from toontown.safezone.picnicgame.BoardGameGlobals import getToonPanels
from toontown.safezone.picnicgame.DistributedPicnicGame import DistributedPicnicGame
from toontown.safezone.picnicgame.PicnicGameArrowButton import PicnicGameArrowButton
from toontown.safezone.picnicgame.PicnicGameGlobals import ARROW_COLOR_GREEN
from toontown.safezone.picnicgame.PicnicGameStatusLabel import PicnicGameStatusLabel
from toontown.safezone.picnicgame.ToonoCard import ToonoCard
from toontown.toonbase import ToontownGlobals, TTLocalizer


class DistributedToono(DistributedPicnicGame):
    gameMusicKey = "picnic_toono"
    discordPreset = "toono"
    guiState = ConditionState.PGT_TOONO

    EVENT_CHOICE_ARROW = "ChoiceArrowRequest"

    def __init__(self, cr):
        super().__init__(cr)

        self.musicType = MusicTypeEnum.DEFAULT

        self.playerCards = {}
        self.localAvCards = []
        self.lastPlayedCard: Optional[ToonoCard] = None
        self.playedCard: Optional[ToonoCard] = None

        self.firstCardSeq: Optional[Sequence] = None
        self.drawSeq: Optional[Sequence] = None
        self.drawAndPlaySeq: Optional[Sequence] = None
        self.playSeq: Optional[Sequence] = None
        self.autoPlaySeq: Optional[Sequence] = None
        self.updateCardsSeq: Optional[Sequence] = None
        self.colorButtonsPopup: Optional[Parallel] = None

        self.statusLabels: dict[int, PicnicGameStatusLabel] = {}

        self.eventLabelSeqQueue = {}

        self.toonoButton: Optional[DirectButton] = None
        self.drawButton: Optional[DirectButton] = None
        self.toonoButtonFrame: Optional[DirectFrame] = None

        self.playChoiceButton: Optional[MainMenuButton] = None
        self.drawChoiceButton: Optional[MainMenuButton] = None
        self.choiceTimeoutTime = 5
        self.choiceTimeoutTask = 'toono-choiceTimeout'

        self.enableColorFrame: bool = False
        self.legalColorFrame: Optional[DirectFrame] = None
        self.colorTextLabel: Optional[DirectFrame] = None

        self.colorButtons = {}
        self.choiceArrows: list[PicnicGameArrowButton] = []

        self.buttonModels = base.loader.loadModel("phase_3.5/models/gui/inventory_gui")
        self.upButton = self.buttonModels.find("**/InventoryButtonUp")
        self.downButton = self.buttonModels.find("**/InventoryButtonDown")
        self.rolloverButton = self.buttonModels.find("**/InventoryButtonRollover")

        self.deck = base.loader.loadModel("phase_6/models/golf/toono_cards")
        self.coloredWildcards = base.loader.loadModel("phase_6/models/golf/toono_wild_cards")
        self.toonoUI = base.loader.loadModel("phase_6/models/gui/toono_ui")

        self.toonoSfx = base.loader.loadSfx("phase_5/audio/sfx/SZ_DD_foghorn.ogg")
        self.forceDrawSfx = base.loader.loadSfx("phase_6/audio/sfx/trumpet_toono.ogg")
        self.dealCardSfx = [base.loader.loadSfx(f"phase_6/audio/sfx/dealcard{i}.ogg") for i in range(1, 8)]
        self.shuffleSfx = base.loader.loadSfx("phase_6/audio/sfx/shufflecards.ogg")
        self.eventSfx = base.loader.loadSfx("phase_6/audio/sfx/color_change_guitar.ogg")

        self.alertSevenSfx = base.loader.loadSfx("phase_6/audio/sfx/toono_alert7.ogg")
        self.playSevenSfx = base.loader.loadSfx("phase_6/audio/sfx/toono_play7.ogg")
        self.playZeroSfx = base.loader.loadSfx("phase_6/audio/sfx/toono_play0.ogg")

        self.currentColor = None
        self.currentCardInfo = None

        self.unoCall = None
        self.skippedPlayer = None
        self._reverseOrder = False

        self.flashMode = -1

    def announceGenerate(self) -> None:
        super().announceGenerate()
        self.d_requestGameState()

    def delete(self) -> None:
        self.buttonModels.remove_node()
        self.buttonModels = None
        self.upButton.remove_node()
        self.upButton = None
        self.downButton.remove_node()
        self.downButton = None
        self.rolloverButton.remove_node()
        self.rolloverButton = None
        self.deck.remove_node()
        self.deck = None
        self.toonoUI.remove_node()
        self.toonoUI = None

        self.toonoSfx = None
        self.forceDrawSfx = None
        self.dealCardSfx = None
        self.shuffleSfx = None
        self.eventSfx = None

        self.alertSevenSfx = None
        self.playSevenSfx = None
        self.playZeroSfx = None

        self.playerCards = {}

        if self.colorButtonsPopup is not None:
            self.colorButtonsPopup.finish()
            self.colorButtonsPopup = None

        self.destroyLastCardPlayed()

        self.stopGameSequences()
        self.destroyPlayedCard()
        self.destroyLocalCards()

        self.destroyToonoGui()
        self.destroyStatusLabels()
        self.destroyColorButtons()
        self.destroyLegalColorFrame()
        self.destroyPlayChoiceButtons()

        taskMgr.remove(self.choiceTimeoutTask)

        super().delete()

    def destroyPlayedCard(self) -> None:
        if self.playedCard is not None:
            self.playedCard.destroy()
            self.playedCard = None

    def destroyLocalCards(self) -> None:
        for card in self.localAvCards:
            card.destroy()

        self.localAvCards = []

    def destroyChoiceArrows(self) -> None:
        self.ignore(self.EVENT_CHOICE_ARROW)

        for button in self.choiceArrows:
            button.destroy()

        self.choiceArrows = []

    def stopGameSequences(self) -> None:
        if self.firstCardSeq is not None:
            self.firstCardSeq.finish()
            self.firstCardSeq = None

        if self.drawSeq is not None:
            self.drawSeq.pause()
            self.drawSeq = None

        if self.drawAndPlaySeq is not None:
            self.drawAndPlaySeq.pause()
            self.drawAndPlaySeq = None

        if self.playSeq is not None:
            self.playSeq.pause()
            self.playSeq = None

        if self.autoPlaySeq is not None:
            self.autoPlaySeq.pause()
            self.autoPlaySeq = None

        if self.updateCardsSeq is not None:
            self.updateCardsSeq.pause()
            self.updateCardsSeq = None

        self.clearEventLabelSeq()

    def setGameState(self, lastPlayedCard, cards) -> None:
        if self.state != "PrepareGame":
            self.playerCards = {p: {c[0]: c[1] for c in pc} for p, pc in cards}
            if 255 not in lastPlayedCard:
                self.currentCardInfo = (*lastPlayedCard, 0)

    def setFlashMode(self, flashMode: int) -> None:
        """Set what type of cards should flash.
        """
        self.flashMode = flashMode

    def setCurrentPlayer(self, avId: int) -> None:
        super().setCurrentPlayer(avId)

        self.unoCall = None
        self.skippedPlayer = None

        if not self.isGameVisible:
            return

        if avId == base.localAvatar.doId:
            self.enableCards()
            self.accept("toonoCardClicked", self.d_requestPlayCard)
            self.enableDrawButton()
            self.playSfx(self.turnChangeSfx)

            # If the player has two cards remaining, and at least one of them
            # can be played this turn, enable the tuno button.
            if len(self.localAvCards) == 2 and self.canPlayCard():
                self.enableToonoButton()
            else:
                self.disableToonoButton()
        else:
            self.disableCards()
            self.disableDrawButton()
            self.disableToonoButton()

    def acceptUno(self, avId: int) -> None:
        if not self.isGameVisible:
            return

        self.disableToonoButton()

        self.unoCall = avId

        avatar = base.cr.getDo(avId)
        if avatar and hasattr(avatar, 'setChatAbsolute'):
            avatar.setChatAbsolute(TTLocalizer.SpeedChatStaticText[4600], CFSpeech | CFTimeout)

    def setMusicType(self, musicType) -> None:
        self.musicType = musicType
        name = musicEnum2Name.get(self.musicType, 'picnic')
        self.gameMusicKey = f'{name}_toono'
        self.gameMusic = base.musicMgr.loadMusic(self.gameMusicKey)

    def getMusicType(self) -> MusicTypeEnum:
        return self.musicType

    def getCardAmount(self, avId: int) -> Optional[int]:
        if avId not in self.playerCards:
            return
        return len(self.playerCards[avId])

    def setFirstCardPlayed(self, card) -> None:
        if not self.isGameVisible:
            return

        firstCard = self.createCard(*card, 0)

        self.firstCardSeq = Sequence()
        self.firstCardSeq.append(self.generateDrawCardInterval(firstCard, Point3(0.0, 0.0, 0.0)))
        self.firstCardSeq.start()

        self.setLastCardPlayed(firstCard)

    def setLastCardPlayed(self, card: ToonoCard) -> None:
        if card is None or card.isEmpty():
            return

        self.destroyLastCardPlayed()

        card.setBin("fixed", 0)
        self.lastPlayedCard = card

        if card.cardType in list(ToonoGlobals.CARD_COLORS)[:4]:
            self.changeLegalColor(card.cardType)

    def destroyLastCardPlayed(self) -> None:
        if self.lastPlayedCard is not None:
            self.lastPlayedCard.destroy()
            self.lastPlayedCard = None

    def d_requestPlayCard(self, index: int) -> None:
        self.sendUpdate("requestPlayCard", [index])

    def d_requestColorChange(self, color: int, cardIndex: int) -> None:
        self.sendUpdate("requestColorChange", [color, cardIndex])

    def d_requestHandshake(self, handshakee: int) -> None:
        self.sendUpdate("requestHandshake", [handshakee])

    def d_requestUno(self) -> None:
        self.sendUpdate("requestUno")

    def d_requestDraw(self) -> None:
        if base.localAvatar.doId != self.currentPlayer:
            return
        self.sendUpdate("requestDraw")

    def d_sendPlayCardResponse(self, response: bool) -> None:
        taskMgr.remove(self.choiceTimeoutTask)
        self.sendUpdate("sendPlayCardResponse", [response])

    def sendPlayCardTimeout(self, task):
        if hasattr(self, 'cr'):
            self.sendUpdate("sendPlayCardResponse", [False])
        return task.done

    def drawCards(self, avId: int, cards, first: bool, preview: bool) -> None:
        self.ignore("toonoCardClicked")

        if avId not in self.playerCards:
            return

        self.playerCards[avId].update({index: card for index, card in cards})

        if not self.isGameVisible:
            return

        # Based on the amount of cards being drawn, display the correlating
        # status on the indicated toon's panel.
        if not first:
            if len(cards) == 1:
                status = ToonoGlobals.STATUSES.DRAW
            elif len(cards) == 2:
                status = ToonoGlobals.STATUSES.DRAW_2
            elif len(cards) == 4:
                status = ToonoGlobals.STATUSES.DRAW_4
            elif len(cards) != 0:
                status = ToonoGlobals.STATUSES.DRAW_AMT
            else:
                status = None

            if status is not None:
                self.animateStatusLabel(avId, status, extra=len(cards))

        # Play the sfx if they've been forced to draw.
        if not first and len(cards) > 1:
            self.playSfx(self.forceDrawSfx)

        if avId != base.localAvatar.doId:
            return

        self.disableDrawButton()

        self.drawSeq = Sequence()

        for card in ((*c, index) for index, c in cards):
            cardObj = self.createCard(*card)

            if first:
                self.localAvCards.append(cardObj)

                reverseCards = list(reversed(self.localAvCards))
                cardPos = self.getInitialCardPos(cardObj, reverseCards)

                self.drawSeq.append(self.generateDrawCardInterval(cardObj, cardPos))
                self.drawSeq.append(
                    self.generateInitialCardsShiftInterval(self.localAvCards, reverseCards))
            else:
                self.localAvCards.append(cardObj)
                self.sortLocalAvCards()

                cardPos = self.getCardPos(cardObj, self.localAvCards)
                excludeCard = [c for c in self.localAvCards if c != cardObj]

                if preview:
                    # Show the card to the player for a bit before shoving it
                    # into the deck.
                    self.drawSeq.append(
                        Sequence(
                            Func(self.updateCardBin, self.localAvCards),
                            Parallel(
                                self.generateDrawCardInterval(cardObj, Point3(0, 0, -0.4)),
                                self.generateShiftCardsInterval(excludeCard, self.localAvCards),
                                self.generateShiftCardsHprInterval(excludeCard, self.localAvCards),
                            ),
                            Wait(2.0),
                            self.generateDrawCardInterval(cardObj, cardPos),
                            self.generateShiftCardsHprInterval(self.localAvCards, self.localAvCards),
                        )
                    )
                else:
                    self.drawSeq.append(
                        Sequence(
                            Func(self.updateCardBin, self.localAvCards),
                            Parallel(
                                self.generateDrawCardInterval(cardObj, cardPos),
                                self.generateShiftCardsInterval(excludeCard, self.localAvCards),
                                self.generateShiftCardsHprInterval(self.localAvCards, self.localAvCards),
                            )
                        )
                    )

        if first:
            self.drawSeq.append(Wait(1.0))
            self.drawSeq.append(self.generateCardSortInterval(self.localAvCards))

        self.drawSeq.append(Func(self.enableCardHover))
        self.drawSeq.start()

    def queryHandshake(self, avId: int) -> None:
        if not self.isGameVisible:
            return

        self.playSfx(self.alertSevenSfx)

        if avId != base.localAvatar.doId:
            return

        # Create the event label.
        eventLabel = self.createEventLabel(
            text_fg=(1, 1, 1, 1),
            text=TTLocalizer.PGTToonoHandshakeRequest
        )

        self.animateEventLabel(eventLabel)

        self.choiceArrows = []

        for panel in getToonPanels():
            # Ignore our own panel.
            if panel.obj.isLocal():
                continue

            arrow = PicnicGameArrowButton(
                panel.flipAnchor, self.EVENT_CHOICE_ARROW, [panel.obj.doId],
                pos=(0.14, 0, 0), scale=0.2,
            )
            arrow.startColorLoop(ARROW_COLOR_GREEN)
            self.choiceArrows.append(arrow)

        self.accept(self.EVENT_CHOICE_ARROW, self.d_requestHandshake)

    def successHandshake(self, avId: int) -> None:
        if not self.isGameVisible:
            return

        toon = base.cr.getDo(avId)

        if toon is None:
            return

        self.playSfx(self.playSevenSfx)

        # Create the event label.
        eventLabel = self.createEventLabel(
            text_fg=(1, 1, 1, 1),
            text=TTLocalizer.PGTToonoHandshakeAccept % toon.getName()
        )

        self.animateEventLabel(eventLabel)

        self.ignore(self.EVENT_CHOICE_ARROW)

    def notifyDeckRotate(self) -> None:
        if not self.isGameVisible:
            return

        self.playSfx(self.playZeroSfx)

        # Create the event label.
        eventLabel = self.createEventLabel(
            text_fg=(1, 1, 1, 1),
            text=TTLocalizer.PGTToonoDeckRotate
        )

        self.animateEventLabel(eventLabel)

    def setCards(self, avId: int, playerCards, affectedPlayers) -> None:
        self.playerCards = {avId: {c[0]: c[1] for c in cards} for avId, cards in playerCards}

        if not self.isGameVisible:
            return

        if base.localAvatar.doId == avId:
            self.destroyChoiceArrows()

        # The local avatar's cards won't change.
        if base.localAvatar.doId not in affectedPlayers:
            return

        self.disableCards()

        def addNewLocalCards():
            self.destroyLocalCards()

            for index, card in self.playerCards[base.localAvatar.doId].items():
                cardObj = self.createCard(*card, index)
                cardObj.setPos(0, 0, -10)
                cardObj.show()
                self.localAvCards.append(cardObj)

            seq = Sequence(
                self.generateMoveCardsInterval(self.localAvCards, -0.66),
                Wait(0.5),
                self.generateCardSortInterval(self.localAvCards),
                Func(self.enableCardHover)
            )
            seq.play()

        self.updateCardsSeq = Sequence(
            self.generateMoveCardsInterval(self.localAvCards, -10),
            Func(addNewLocalCards)
        )

        self.updateCardsSeq.start()

    def queryColorChange(self, avId: int, cardIndex: int) -> None:
        if not self.isGameVisible:
            return

        self.createColorButtons(cardIndex)

        if base.localAvatar.doId != avId:
            for button in self.colorButtons.values():
                button["state"] = DGG.DISABLED

        self.colorButtonsPopup = Parallel()

        for button in self.colorButtons.values():
            scale = button.getScale()
            self.colorButtonsPopup.append(
                Sequence(
                    LerpScaleInterval(button, 0.2, scale * 1.2, 0.01, blendType="easeInOut"),
                    LerpScaleInterval(button, 0.2, scale, scale * 1.2, blendType="easeInOut")
                )
            )

        self.colorButtonsPopup.start()

    def changeColor(self, color: int) -> None:
        if not self.isGameVisible:
            return

        self.stopTimer()

        self.colorButtonsPopup = Parallel()

        for button in self.colorButtons.values():
            scale = button.getScale()
            self.colorButtonsPopup.append(
                Sequence(
                    LerpScaleInterval(button, 0.2, scale * 1.2, scale, blendType="easeInOut"),
                    LerpScaleInterval(button, 0.2, 0.01, scale * 1.2, blendType="easeInOut"),
                    Func(button.hide)
                )
            )

        self.colorButtonsPopup.start()

        # Change color of wildcard
        identifier = ToonoGlobals.COLOR_2_STRING[self.lastPlayedCard.cardType] \
                     + '_' + ToonoGlobals.COLOR_2_STRING[color]
        cardGeom = self.coloredWildcards.find(f"**/{identifier}")
        if not cardGeom.isEmpty():
            self.lastPlayedCard['geom'] = cardGeom

        self.changeLegalColor(color)

    def drawAndPlayCard(self, avId: int, card, autoPlay: bool) -> None:
        self.ignore("toonoCardClicked")

        self.currentCardInfo = (*card[1], card[0])

        if not self.isGameVisible:
            return

        def enableToonoButton():
            # Enable the button which allows us to call out their uno.
            if len(self.playerCards[avId]) == 1 and self.unoCall is None:
                self.enableToonoButton()
                self.animateStatusLabel(avId, ToonoGlobals.STATUSES.TOONO)

        self.animateStatusLabel(avId, ToonoGlobals.STATUSES.DRAW)

        playedCard = self.createCard(*card[1], card[0])

        if avId == base.localAvatar.doId:
            self.disableDrawButton()

            # Enable the current player's toono button.
            enableToonoButton()

            self.drawAndPlaySeq = Sequence(
                self.generateDrawCardInterval(playedCard, Point3(-0.4, 0, -0.4)),
            )
            if autoPlay:
                self.drawAndPlaySeq.append(Wait(1.0))
                self.drawAndPlaySeq.append(self.generatePlayCardInterval(playedCard))
            else:
                self.drawAndPlaySeq.append(Wait(0.5))
                self.drawAndPlaySeq.append(Func(self.createPlayChoiceButtons, playedCard))
        else:
            self.drawAndPlaySeq = Sequence(Wait(1.5))
            if autoPlay:
                # Enable the opponents' toono buttons right before it shows the current player's 
                # card moving to the middle.
                self.drawAndPlaySeq.append(Func(enableToonoButton))
                self.drawAndPlaySeq.append(self.generateNonlocalPlayCardInterval(playedCard, avId))

        if autoPlay:
            self.appendStatusSequencing(self.drawAndPlaySeq)

        self.drawAndPlaySeq.start()

        self.playedCard = playedCard

    def createPlayChoiceButtons(self, card) -> None:
        button_size = (.25, .15, .12)
        self.playChoiceButton = MainMenuButton(
            card, pos=(-0.35, 0, 0.2),
            text=TTLocalizer.PGTToonoPlayChoice,
            command=self.d_sendPlayCardResponse, extraArgs=[True],
            image_scale=button_size,
            image1_scale=button_size,
            image2_scale=button_size,
        )
        self.drawChoiceButton = MainMenuButton(
            card, pos=(-0.35, 0, 0.06),
            text=TTLocalizer.PGTToonoDrawChoice,
            command=self.d_sendPlayCardResponse, extraArgs=[False],
            image_scale=button_size,
            image1_scale=button_size,
            image2_scale=button_size,
        )
        taskMgr.doMethodLater(self.choiceTimeoutTime, self.sendPlayCardTimeout, self.choiceTimeoutTask)

    def destroyPlayChoiceButtons(self) -> None:
        if self.playChoiceButton is not None:
            self.playChoiceButton.destroy()
            self.playChoiceButton = None

        if self.drawChoiceButton is not None:
            self.drawChoiceButton.destroy()
            self.drawChoiceButton = None

    def setPlayCardResponse(self, response: bool, cardIndex: int, avId: int) -> None:
        if not self.playedCard:
            return

        if not response and avId in self.playerCards:
            self.playerCards[avId][cardIndex] = (self.playedCard.cardType, self.playedCard.cardNumber)

        if not self.isGameVisible:
            return

        self.destroyPlayChoiceButtons()

        if response:
            if avId == base.localAvatar.doId:
                self.autoPlaySeq = Sequence(
                    self.generatePlayCardInterval(self.playedCard)
                )
            else:
                self.autoPlaySeq = Sequence(
                    self.generateNonlocalPlayCardInterval(self.playedCard, avId)
                )

                # The current player has decided to play the card, and has had their
                # toono button enabled already, so we'll enable the rest of the players'
                # toono buttons.
                if len(self.playerCards[avId]) == 1:
                    if self.unoCall is None:
                        self.enableToonoButton()
                    self.animateStatusLabel(avId, ToonoGlobals.STATUSES.TOONO)

            self.appendStatusSequencing(self.autoPlaySeq)
            self.autoPlaySeq.start()
        elif avId == base.localAvatar.doId:
            self.localAvCards.append(self.playedCard)
            self.sortLocalAvCards()

            cardPos = self.getCardPos(self.playedCard, self.localAvCards)
            excludeCard = [c for c in self.localAvCards if c != self.playedCard]

            self.autoPlaySeq = Sequence(
                Func(self.updateCardBin, self.localAvCards),
                Parallel(
                    self.generateDrawCardInterval(self.playedCard, cardPos, start=self.playedCard.getPos()),
                    self.generateShiftCardsInterval(excludeCard, self.localAvCards),
                    self.generateShiftCardsHprInterval(self.localAvCards, self.localAvCards),
                ),
                Func(self.enableCardHover),
            )
            self.autoPlaySeq.start()

    def playCard(self, avId: int, cardIndex: int, effect: bool, jumpedIn: bool) -> None:
        self.ignore("toonoCardClicked")

        if avId not in self.playerCards or cardIndex not in self.playerCards[avId]:
            return

        card = self.playerCards[avId][cardIndex]

        # Delete the card in the list of this player's cards.
        del self.playerCards[avId][cardIndex]

        self.currentCardInfo = (*card, cardIndex)

        if not self.isGameVisible:
            return

        # Enable the button which allows us to call out their uno.
        if len(self.playerCards[avId]) == 1:
            if self.unoCall is None:
                self.enableToonoButton()
            self.animateStatusLabel(avId, ToonoGlobals.STATUSES.TOONO)

        if avId == base.localAvatar.doId:
            self.disableDrawButton()

            # Get the card object from the list of the local avatar's cards.
            playedCard = self.getLocalCard(cardIndex)

            def removeCard():
                if self.getLocalCard(cardIndex) == playedCard:
                    del self.localAvCards[self.getLocalCardIndex(cardIndex)]

            self.playSeq = self.generatePlayCardInterval(playedCard)
            self.playSeq.append(Func(removeCard))
        else:
            playedCard = self.createCard(*card, cardIndex)
            self.playSeq = self.generateNonlocalPlayCardInterval(playedCard, avId)

        # This card wasn't a jump in, immediately display
        # the effect.
        if effect:
            self.appendStatusSequencing(self.playSeq)

        if jumpedIn:
            # Display that the given avId played
            def makeJumpInLabel():
                toon = base.cr.getDo(avId)

                if toon is None:
                    return

                # Create the event label.
                eventLabel = self.createEventLabel(
                    text_fg=(1, 1, 1, 1),
                    text=TTLocalizer.PGTToonoJumpedIn.format(toon.getName())
                )

                self.animateEventLabel(eventLabel)

            self.playSeq.append(Func(makeJumpInLabel))

        self.playSeq.start()

        self.playedCard = playedCard

    def showCardEffect(self) -> None:
        if not self.isGameVisible:
            return

        self.playSeq = Sequence()
        self.appendStatusSequencing(self.playSeq)
        self.playSeq.start()

    def cardMatches(self, cardOne, cardTwo) -> bool:
        return ((cardOne[0] == cardTwo[0] in (ToonoGlobals.CARD_COLORS.WILD, ToonoGlobals.CARD_COLORS.WILD_FOUR)) or
                (cardOne[0] == cardTwo[0] and cardOne[1] == cardTwo[1]))

    def setAllowJumpIn(self, allowJumpIn: bool, lastCard) -> None:
        if not self.isGameVisible:
            return

        if allowJumpIn:
            canJumpIn = False
            for card in self.localAvCards:
                if card.index != lastCard[0] and \
                    self.cardMatches((card.cardType, card.cardNumber), lastCard[1]):
                    card.enableCard(True)
                    canJumpIn = True
                else:
                    card.disableCard()

            if canJumpIn:
                self.accept("toonoCardClicked", self.d_requestPlayCard)
        else:
            for card in self.localAvCards:
                if card.index != lastCard[0]:
                    card.disableCard()

            self.ignore("toonoCardClicked")

    def skipPlayer(self, skippedPlayer: int) -> None:
        self.skippedPlayer = skippedPlayer

    def reverseOrder(self) -> None:
        self._reverseOrder = True

    def avatarEnter(self, avId: int) -> None:
        if avId != base.localAvatar.doId:
            return

        if self.getCurrentOrNextState() == "Playing":
            self.startTimer()
            self.createLegalColorFrame()

        if self.currentCardInfo is not None:
            card = self.createCard(*self.currentCardInfo)
            card.show()
            card.setPos(0, 0, 0)
            self.setLastCardPlayed(card)

        super().avatarEnter(avId)

        if self.getCurrentOrNextState() == "Playing":
            self.createStatusLabels()

    def avatarExit(self, avId: int) -> None:
        if avId in self.playerCards:
            del self.playerCards[avId]

        if avId != base.localAvatar.doId:
            return

        self.ignore(self.EVENT_CHOICE_ARROW)

        self.destroyLegalColorFrame()
        self.destroyLastCardPlayed()
        self.destroyPlayChoiceButtons()

        self.stopGameSequences()
        self.destroyPlayedCard()
        self.destroyLocalCards()
        self.destroyColorButtons()

        self.destroyToonoGui()
        self.destroyStatusLabels()

        self.stopTimer()

        super().avatarExit(avId)

    def createCard(self, color: int, number: int, index: int) -> ToonoCard:
        """Based on the color and the number given, create a TOONO card.
        """
        identifier = ToonoGlobals.COLOR_2_STRING[color]

        if color not in list(ToonoGlobals.CARD_COLORS)[4:]:
            if number in list(ToonoGlobals.COLORED_ACTIONS):
                identifier = ToonoGlobals.ACTION_2_STRING[number] + identifier
            else:
                identifier = str(number) + identifier

        cardGeom = self.deck.find(f"**/{identifier}")

        return ToonoCard(color, number, index, cardGeom)

    def getInitialCardPos(self, card: ToonoCard, cardList) -> Point3:
        """Returns the position that the indicated card should be in relative
        to the rest of the cards.
        """
        index = cardList.index(card)
        x = 0.6 - (0.2 * index)
        return Point3(x, 0, -0.66)

    def getCardPos(self, card: ToonoCard, cardList) -> Point3:
        """Returns the position that the indicated card should be in relative
        to the rest of the cards.
        """
        index = cardList.index(card)
        length = len(cardList)

        f = 1 + (-0.8 ** (length - 1))

        min_x = -f
        max_x = f

        x = (min_x - (min_x - max_x) * (index / length))

        return Point3(x, 0.0, -0.66)

    def getCardHpr(self, card: ToonoCard, cardList) -> Point3:
        """Returns the rotation that the indicated card should be in relative
        to the rest of the cards.
        """
        index = cardList.index(card)
        length = len(cardList)

        f = 1 + (-0.8 ** (length - 1))

        min_r = ToonoGlobals.CARD_MIN_R * f
        max_r = ToonoGlobals.CARD_MAX_R * f

        r = (min_r - (min_r - max_r) * (index / length))

        return Point3(0, 0, r)

    def generateNonlocalPlayCardInterval(self, card: ToonoCard, avId: int) -> Sequence:
        panels = [p for p in getToonPanels() if p.obj.doId == avId]
        if panels:
            return Sequence(
                Func(card.show),
                Func(card.setPos, panels[0].getPos(aspect2d)),
                Func(self.playRandomDealSfx),
                LerpPosInterval(card, 0.5, Point3(0, 0, 0)),
                Func(self.setLastCardPlayed, card),
            )

        # Couldn't find the panel, let's just put the card down in the center.
        return Sequence(
            Func(card.show),
            Func(card.setPos, Point3(0, 0, 0)),
            Func(self.setLastCardPlayed, card)
        )

    def generatePlayCardInterval(self, card: ToonoCard) -> Sequence:
        remainingCards = [c for c in self.localAvCards if c != card]
        return Sequence(
            Func(card.disableButton),
            # Stop the flash loop (just in case it's playing)
            Func(self.stopFlash),
            Func(self.untintCards),
            Func(self.playRandomDealSfx),
            Parallel(
                LerpHprInterval(card, 0.2, Point3(0, 0, 0)),
                LerpPosInterval(card, 0.5, Point3(0, 0, 0)),
            ),
            Func(self.setLastCardPlayed, card),
            Parallel(
                self.generateShiftCardsInterval(remainingCards, remainingCards),
                self.generateShiftCardsHprInterval(remainingCards, remainingCards),
            )
        )

    def generateDrawCardInterval(self, card: ToonoCard, dest: Point3,
                                 start: Point3 = Point3(-2.0, 0.0, 0.0), duration: int = 0.5) -> Sequence:
        """Generate an interval which moves the card from their original
        position to the player's hand.
        """
        return Sequence(
            # Stop the flash loop (just in case it's playing)
            Func(self.stopFlash),
            Func(self.playRandomDealSfx),
            Func(card.show),
            LerpPosInterval(card, duration, dest, start)
        )

    def generateMoveCardsInterval(self, cards, z: int) -> Parallel:
        """Generate an interval to adjust the positions of all of the cards
        based on how many exist.
        """
        return Parallel(*[LerpPosInterval(card, 1.0, Point3(card.getX(), card.getY(), z)) for card in cards])

    def generateShiftCardsInterval(self, cards, cardList) -> Parallel:
        """Generate an interval to adjust the positions of all of the cards
        based on how many exist.
        """
        return Parallel(*[LerpPosInterval(card, 0.2, self.getCardPos(card, cardList)) for card in cards])

    def generateInitialCardsShiftInterval(self, cards, cardList) -> Parallel:
        """Generate an interval to adjust the positions of all of the cards
        based on how many exist.
        """
        return Parallel(*[LerpPosInterval(card, 0.2, self.getInitialCardPos(card, cardList)) for card in cards])

    def generateShiftCardsHprInterval(self, cards, cardList) -> Parallel:
        """Generate an interval to adjust the rotations of all of the cards
        based on how many exist.
        """
        return Parallel(*[LerpHprInterval(card, 0.2, self.getCardHpr(card, cardList)) for card in cards])

    def generateCardSortInterval(self, cards) -> Parallel:
        """Generate an interval to sort all of the cards based on their card
        type and number.
        """
        self.sortLocalAvCards()
        return Parallel(
            Func(self.playShuffleSfx),
            Parallel(
                self.generateShiftCardsInterval(cards, self.localAvCards),
                self.generateShiftCardsHprInterval(cards, self.localAvCards)
            ),
            Sequence(
                Wait(0.25),
                Func(self.updateCardBin, self.localAvCards)
            )
        )

    def playRandomDealSfx(self) -> None:
        if self.dealCardSfx is not None:
            self.playSfx(random.choice(self.dealCardSfx))

    def playShuffleSfx(self) -> None:
        self.playSfx(self.shuffleSfx)

    def enableCards(self) -> None:
        for card in self.localAvCards:
            # Flashing is disabled.
            if self.flashMode <= 0:
                card.enableCard(True)
            # Flashing is enabled, and this card can be used
            # to jump in with.
            elif (self.flashMode == 1 and card.cardType == ToonoGlobals.CARD_COLORS.WILD_FOUR) or \
                (self.flashMode == 2 and card.cardNumber == ToonoGlobals.COLORED_ACTIONS.DRAW_TWO):
                card.enableCard(False)
                card.startFlash()
            # Flashing is enabled, and this card cannot be used
            # to jump in with.
            else:
                card.disableCard()

    def untintCards(self) -> None:
        [card.untintCard() for card in self.localAvCards]

    def stopFlash(self) -> None:
        [card.stopFlash() for card in self.localAvCards]

    def disableCards(self) -> None:
        [card.disableCard() for card in self.localAvCards]

    def enableCardHover(self) -> None:
        [card.enableHover() for card in self.localAvCards]

    def updateCardBin(self, cards) -> None:
        [card.setBin("fixed", index + 1) for index, card in enumerate(cards)]

    def sortLocalAvCards(self) -> None:
        self.localAvCards.sort(key=attrgetter("cardType", "cardNumber"))

    def appendStatusSequencing(self, seq) -> None:
        # A player has been skipped, display the fact as a status on their
        # toon panel.
        if self.skippedPlayer is not None:
            def animateStatusLabel(player: int) -> None:
                self.animateStatusLabel(player, ToonoGlobals.STATUSES.SKIPPED)

                self.playSfx(self.forceDrawSfx)

            seq.append(Func(animateStatusLabel, self.skippedPlayer))

            self.skippedPlayer = None
        # A player has reversed the player order, display it similarly to the
        # color changing event.
        elif self._reverseOrder:
            def animateEventLabel():
                eventLabel = self.createEventLabel(
                    text_fg=(1, 1, 1, 1),
                    text=TTLocalizer.PGTToonoReverseOrder
                )

                self.animateEventLabel(eventLabel)

            seq.append(Func(animateEventLabel))

            self._reverseOrder = False

    def createStatusLabels(self) -> None:
        panels = {panel.obj.doId: panel for panel in getToonPanels()}

        for avId in self.players:
            if avId not in panels:
                continue

            self.statusLabels[avId] = PicnicGameStatusLabel(
                avId, parent=panels[avId].flipAnchor, pos=(0.04, 0, -0.025),
                relief=None, text="", textMayChange=True,
                text_fg=(1, 0.9, 0.2, 1), text_scale=0.08,
                text_font=ToontownGlobals.getMinnieFont(),
                text_align=TextNode.ALeft, text_shadow=(0, 0, 0, 1)
            )
    
    def destroyStatusLabels(self) -> None:
        for label in self.statusLabels.values():
            label.destroy()

        self.statusLabels = {}

    def animateStatusLabel(self, avId: int, status: int, extra=None) -> None:
        text = TTLocalizer.PGTToonoStatuses.get(status)
        if extra is not None:
            text = text.format(extra)

        messenger.send(f"AnimateStatusLabel-{avId}", [text])

        if status == ToonoGlobals.STATUSES.TOONO:
            self.playSfx(self.toonoSfx)

    def animateEventLabel(self, label: DirectLabel) -> None:
        # Find a suitable position to put this in the queue.
        queuePos = 0
        while queuePos in self.eventLabelSeqQueue.keys():
            queuePos += 1

        # Move the Z position of the label relative to the queue position.
        zOffset = (0, 0.3, -0.3)
        newZPos = label.getZ() + zOffset[queuePos % len(zOffset)]
        label.setZ(newZPos)

        # Make the sequence, and put it in the queue.
        eventLabelSeq = Sequence(
            Parallel(
                LerpScaleInterval(label, 3.5, (0.7, 0.7, 0.7), (1, 1, 1)),
                Sequence(
                    Wait(3),
                    LerpColorScaleInterval(label, 0.5, (1, 1, 1, 0), (1, 1, 1, 1)),
                ),
                Func(base.loader.playSfx, self.eventSfx)
            )
        )
        self.eventLabelSeqQueue[queuePos] = eventLabelSeq

        # Finish up the label sequence.
        def removeEventLabelSeq(queuePos):
            if queuePos in self.eventLabelSeqQueue.keys():
                self.eventLabelSeqQueue.pop(queuePos)

        eventLabelSeq.append(Func(removeEventLabelSeq, queuePos))
        eventLabelSeq.start()

    def createToonoGui(self) -> None:
        self.toonoButtonFrame = DirectFrame(
            parent=base.a2dBottomRight, relief=None, pos=(-0.7, 0, 0.22),
            image=self.toonoUI.find("**/button_backdrop"), image_scale=(0.6, 1, 0.4)
        )

        self.drawButton = DirectButton(
            parent=self.toonoButtonFrame, relief=None, pos=(0, 0, 0.095),
            image=(
                self.toonoUI.find("**/draw_UP"), self.toonoUI.find("**/draw_DN"), self.toonoUI.find("**/draw_RLVR")),
            image_scale=(0.56, 1, 0.175),
            command=self.d_requestDraw,
        )

        self.toonoButton = DirectButton(
            parent=self.toonoButtonFrame, relief=None, pos=(0, 0, -0.095),
            image=(
                self.toonoUI.find("**/toono_UP"), self.toonoUI.find("**/toono_DN"), self.toonoUI.find("**/toono_RLVR")),
            image_scale=(0.56, 1, 0.175),
            command=self.d_requestUno,
        )

    def destroyToonoGui(self) -> None:
        if self.toonoButtonFrame is not None:
            self.toonoButtonFrame.destroy()
            self.toonoButtonFrame = None

        if self.drawButton is not None:
            self.drawButton.destroy()
            self.drawButton = None

        if self.toonoButton is not None:
            self.toonoButton.destroy()
            self.toonoButton = None

        self.destroyChoiceArrows()

    def enableToonoButton(self) -> None:
        if self.toonoButton is not None and self.toonoButton["state"] != DGG.NORMAL:
            self.toonoButton["state"] = DGG.NORMAL
            self.toonoButton.setColorScale(1, 1, 1, 1)

    def disableToonoButton(self) -> None:
        if self.toonoButton is not None and self.toonoButton["state"] != DGG.DISABLED:
            self.toonoButton["state"] = DGG.DISABLED
            self.toonoButton.setColorScale(1, 1, 1, 0.7)

    def enableDrawButton(self) -> None:
        if self.drawButton is not None and self.drawButton["state"] != DGG.NORMAL:
            self.drawButton["state"] = DGG.NORMAL
            self.drawButton.setColorScale(1, 1, 1, 1)

    def disableDrawButton(self) -> None:
        if self.drawButton is not None and self.drawButton["state"] != DGG.DISABLED:
            self.drawButton["state"] = DGG.DISABLED
            self.drawButton.setColorScale(1, 1, 1, 0.7)

    def createColorButtons(self, cardIndex: int) -> None:
        self.colorButtons = {}

        for color in list(ToonoGlobals.CARD_COLORS)[:4]:
            self.colorButtons[color] = DirectButton(
                parent=aspect2d,
                relief=None,
                text=TTLocalizer.PGTToonoColors[color].upper(),
                text_fg=(1, 1, 1, 1),
                text_pos=(0, -0.2),
                text_scale=0.55,
                text_font=ToontownGlobals.getBuildingNametagFont(),
                text_align=TextNode.ACenter,
                image=(self.upButton, self.downButton, self.rolloverButton),
                image_color=ToonoGlobals.COLOR_BUTTON_COLOR[color],
                image_scale=(15, 1, 15),
                pos=ToonoGlobals.COLOR_BUTTON_POS[color],
                scale=0.15,
                command=self.d_requestColorChange,
                extraArgs=[color, cardIndex]
            )

    def destroyColorButtons(self) -> None:
        for button in self.colorButtons.values():
            button.destroy()

        self.colorButtons = {}

    def createLegalColorFrame(self) -> None:
        if not self.enableColorFrame:
            return

        self.legalColorFrame = DirectFrame(
            parent=self.toonoButtonFrame, relief=None,
            image=self.toonoUI.find("**/color_backdrop"),
            image_color=ToonoGlobals.COLOR_BUTTON_COLOR[0],
            image_scale=(0.5, 1, 0.25),
            pos=(0, 0, 0.75), sortOrder=0
        )
        self.colorTextLabel = DirectLabel(
            parent=self.legalColorFrame, relief=None, pos=(0, 0, -0.03),
            image=self.toonoUI.find("**/color_innerlay"),
            image_scale=(0.45, 1, 0.15),
            text=TTLocalizer.PGTToonoColors[0].title(),
            text_fg=ToonoGlobals.COLOR_BUTTON_COLOR[0],
            text_scale=0.12,
            text_pos=(0, -0.035),
            text_align=TextNode.ACenter,
            text_shadow=(0, 0, 0, 1), sortOrder=1
        )
        label = DirectLabel(
            parent=self.legalColorFrame, relief=None, text_scale=0.07,
            text_fg=(1, 1, 1, 1), text_pos=(0, 0.065), text=TTLocalizer.PGTColorLabel,
            text_font=ToontownGlobals.getMinnieFont(),
            text_shadow=(0, 0, 0, 1)
        )

    def createEventLabel(self, **kwargs) -> DirectLabel:
        eventLabel = DirectLabel(
            parent=aspect2d, relief=None, textMayChange=True,
            text_scale=0.15, text_shadow=(0, 0, 0, 1),
            text_font=ToontownGlobals.getMinnieFont(), text_wordwrap=10, sortOrder=2,
            **kwargs
        )
        return eventLabel

    def changeLegalColor(self, color: int) -> None:
        if color == self.currentColor:
            return

        if self.currentColor is not None:
            colorString = TTLocalizer.PGTToonoColors[color].title()

            eventLabel = self.createEventLabel(
                text_fg=ToonoGlobals.COLOR_BUTTON_COLOR[color],
                text=TTLocalizer.PGTToonoColorChange.format(colorString)
            )

            self.animateEventLabel(eventLabel)

        if self.legalColorFrame is not None:
            self.legalColorFrame.configure(image_color=ToonoGlobals.COLOR_BUTTON_COLOR[color])
            self.colorTextLabel.configure(text=TTLocalizer.PGTToonoColors[color].title(),
                                          text_fg=ToonoGlobals.COLOR_BUTTON_COLOR[color])

        self.currentColor = color

    def clearEventLabelSeq(self) -> None:
        for seq in list(self.eventLabelSeqQueue.values()):
            seq.finish()

        self.eventLabelSeqQueue = {}

    def destroyLegalColorFrame(self) -> None:
        if self.legalColorFrame is not None:
            self.legalColorFrame.destroy()
            self.legalColorFrame = None

        if self.colorTextLabel is not None:
            self.colorTextLabel.destroy()
            self.colorTextLabel = None

    def getLocalCard(self, index: int) -> ToonoCard:
        cards = [card for card in self.localAvCards if card.index == index]
        if cards:
            return cards[0]

    def getLocalCardIndex(self, index: int) -> int:
        card = self.getLocalCard(index)
        if card in self.localAvCards:
            return self.localAvCards.index(card)
        return -1

    def canPlayCard(self):
        return any(
            [card.cardType in list(ToonoGlobals.CARD_COLORS)[4:] + [self.lastPlayedCard.cardType, self.currentColor]
             or \
             card.cardNumber == self.lastPlayedCard.cardNumber for card in self.localAvCards])

    """
    FSM states
    """

    def enterPrepareGame(self) -> None:
        super().enterPrepareGame()

        self.playerCards = {avId: {} for avId in self.players}

        if self.isGameVisible:
            self.createStatusLabels()
            self.createToonoGui()
            self.disableDrawButton()
            self.disableToonoButton()

            self.helpButton = self.makeQuestionButton(
                PicnicGameGlobals.PicnicGame.TOONO, parent=base.a2dBottomRight,
                pos=(-0.173, 1, 0.70), text_fg=(1, 1, 1, 1),
            )

    def enterPlaying(self) -> None:
        if self.isGameVisible:
            self.createLegalColorFrame()

        super().enterPlaying()

    def enterReward(self) -> None:
        if not self.isGameVisible:
            return

        self.destroyToonoGui()
        self.destroyStatusLabels()
        self.destroyColorButtons()

        self.destroyLegalColorFrame()

        avId = self.winner

        av = base.cr.getDo(avId)
        if not av:
            return

        label = DirectLabel(
            relief=None, text=TTLocalizer.PGTPlayerWonGame.format(av.getName()),
            pos=(0.0, 0.0, 0.6), text_fg=(1, 1, 1, 1), text_scale=0.08,
            text_font=ToontownGlobals.getSignFont(), scale=1.2,
        )

        self.playLabelSeq(label)

        if base.localAvatar.doId == self.winner:
            self.playSfx(self.victorySfx)
        else:
            self.playSfx(self.loseSfx)

        super().enterReward()
