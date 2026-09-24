"""
DistributedChairAI: home of the universal chair

@author: Travis
@date: 4/15/2022
"""

from typing import List

from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.showbase.MessengerGlobal import messenger

from otp.ai.AIBaseGlobal import simbase
from toontown.quest3.SpecialQuestZones import SpecialQuestZones
from toontown.safezone.ChairConstants import ChairTypeEnum, MusicTypeEnum
from toontown.safezone.picnicgame.PicnicGameGlobals import PicnicGame
from toontown.safezone.picnicgame import ToonoGlobals
from toontown.safezone.picnicgame.DistributedToonoAI import DistributedToonoAI
from toontown.toon.DistributedToonAI import DistributedToonAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedChairAI(DistributedNodeAI):
    """DistributedChairAI: the server side representation of various sitting devices.
    Handles what toon is currently sitting in the chair, as well as requests
    sent to sit in the chair.

    :param air: The AI repository.
    :param chairNumber: A unique identifier for the chair.
    :param radius: The radius of the chair collision.
    :param hopOnPos: The position to sit the toon when they hop
    onto the chair.
    :param hopOffPos: The position to set the toon when they hop
    off the chair.
    :param chairType: The chair type to display as flavor text
    when using the interact key.
    :param chairGroup: The grouping of chairs which this chair
    belongs to. 
    :param wantToono: Determines whether toono games are allowed
    using this chair.
    :param wantOrbitCamera: Determines if the orbital camera
    should be enabled using this chair.
    """
    chosenGame = PicnicGame.TOONO
    
    def __init__(self, air, chairNumber: int, radius: int=4,
                 hopOnPos: List[float] = [-0.1, -4.75, 2.15], 
                 hopOffPos: List[float] = [0, -5, 0.4],
                 chairType: ChairTypeEnum=ChairTypeEnum.CHAIR,
                 chairGroup: int=0, wantToono: bool=False,
                 musicType: int=MusicTypeEnum.DEFAULT,
                 wantOrbitCamera: bool=True) -> None:
        super().__init__(air)

        # The id of the currently seated avatar.
        self.seatedAvId = 0

        # Unique identifier for the chair.
        self.chairNumber = chairNumber

        # Radius of the enter chair collision.
        self.radius = radius

        # Where to position the toon when they're seated.
        self.hopOnPos = hopOnPos

        # Where to position the toon when they're unseated.
        self.hopOffPos = hopOffPos

        # The type of chair.
        # This field is used for flavor text on the enter key sequence.
        self.chairType = chairType

        # The grouping of chairs which this chair belongs to.
        self.chairGroup = chairGroup

        # Do we want to allow this chair to have access to the orbital camera?
        self.wantOrbitCamera = wantOrbitCamera

        # Do we want Toons to be able to hop onto the chair?
        self.lockChair = False

        ### TOONO ###

        # Do we want to allow this chair to have access to TOONO?
        self.wantToono = wantToono

        # What music type should play for this TOONO game?
        self.musicType = musicType

        # List of avatars which are interested in playing TOONO.
        self.playerList = []

        # List of avatars which have joined during a game of TOONO,
        # and are just here to watch until the game is over.
        self.spectators = []

        # Contains the picnic game.
        self.game: DistributedToonoAI = None

        # Store the house rules to be toggled on/off when going to play TOONO.
        self.houseRules = ToonoGlobals.DEFAULT_HOUSE_RULES.copy()

        # Stores the game's "owner"'s avatar id.
        # The owner manages the house rules and the status of the game.
        self.owner = 0

        # Accept some hooks.
        self.accept(f"seatedAvatar-{self.chairGroup}", self.seatedAvatar)
        self.accept(f"unseatedAvatar-{self.chairGroup}", self.unseatedAvatar)
        self.accept(f"gameStarted-{self.chairGroup}", self.gameStarted)
        self.accept(f"gameStopped-{self.chairGroup}", self.gameStopped)
    
    def announceGenerate(self):
        super().announceGenerate()
        self.accept(self.uniqueName("forceExitChair"), self.forceUnseatAvatar)
    
    def delete(self):
        self.ignoreAll()
        if self.wantToono:
            self.stopGame()
        if self.seatedAvId:
            self.d_unseatAvatar(self.seatedAvId, animate=False)
        
        del self.playerList
        del self.spectators
        del self.hopOnPos
        del self.hopOffPos
        del self.houseRules
        
        super().delete()

    """
    Messages sent from the client
    """

    def requestSeat(self) -> None:
        """Request sent by the client to seat an avatar.
        """
        avId = simbase.air.getAvatarIdFromSender()
        av: DistributedToonAI = simbase.air.doId2do.get(avId)

        # The avatar doesn't exist.
        if av is None:
            return

        # An avatar is already seated here.
        if self.seatedAvId != 0:
            self.d_rejectAvatar(avId)
            return
        
        # The chair is currently not accepting new seaters.
        if self.lockChair:
            return

        self.seatedAvId = avId

        # Add a hook that handles the case where the avatar exits
        # the district unexpectedly.
        self.acceptOnce(simbase.air.getAvatarExitEvent(avId),
                        self.handleUnexpectedExit, extraArgs=[avId])

        # Add a hook that handles the case where the avatar dies.
        self.acceptOnce(DistributedToonAI.getGoneSadMessageForAvId(avId),
                        self.d_unseatAvatar, extraArgs=[avId])
        
        # Add a hook that handles the case where the avatar is
        # somehow dragged into battle.
        self.acceptOnce(av.uniqueName("toonEnteredBattle"),
                        self.d_unseatAvatar, extraArgs=[avId])

        messenger.send(f"seatedAvatar-{self.chairGroup}", [avId])

        # Let the game know that an avatar has entered.
        if self.game is not None:
            self.game.b_setSpectators(self.spectators)
        
        # Tell the client to seat the toon.
        self.d_seatAvatar(avId)
    
    def requestExit(self) -> None:
        """Request sent by the client to let the avatar get up.
        """
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # The avatar doesn't exist.
        if av is None:
            return

        # The given avatar id isn't seated here.
        if self.seatedAvId != avId:
            return

        # Tell the client to unseat the avatar.
        self.d_unseatAvatar(avId)
    
    def requestChairState(self) -> None:
        """Request sent by a newly interested client to see who is
        currently on the chair.
        """
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # The avatar doesn't exist.
        if av is None:
            return

        if self.seatedAvId != 0:
            self.sendUpdateToAvatarId(avId, "seatAvatar", [self.seatedAvId])
    
    def requestGame(self) -> None:
        """Request sent by a client interested in playing a good
        old game of TOONO.
        """
        # Do nothing if this update was somehow sent while a game
        # was in progress.
        if self.game is not None:
            return

        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # The avatar doesn't exist.
        if av is None:
            return

        # The avatar isn't the owner; therefore they can't
        # invoke a game.
        if avId != self.owner:
            return
        
        # The avatar isn't the first avatar (the owner).
        if avId != self.playerList[0]:
            return
        
        # There aren't enough participants to start the game.
        if len(self.playerList) < 2:
            return

        # Handle special zones.
        if self.musicType == MusicTypeEnum.OCLO:
            specialZone = SpecialQuestZones.HM_LawbotBoss
        else:
            specialZone = None

        # Create the instance of the game on this chair.
        # The owner chair acts as a "host" for the game,
        # and will stick around so long as there are enough people
        # playing the game.
        self.game = DistributedToonoAI(self.air, self, self.houseRules, self.musicType, specialZone)
        self.game.generateWithRequired(self.zoneId)
        self.game.b_setState("PrepareGame")
        # Distribute the game to the other chairs in the group.
        messenger.send(f"gameStarted-{self.chairGroup}", [self.game])
    
    def requestSetHouseRules(self, houseRuleData: list) -> None:
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if not av:
            return

        # Only the owner can change house rules.
        if avId != self.owner:
            return

        houseRules = dict(houseRuleData)

        if not all([isinstance(houseRule, str) for houseRule in houseRules]):
            return

        self.houseRules.update(houseRules)

        self.d_setHouseRules(houseRuleData)


    """
    Messages sent to the client
    """

    def d_seatAvatar(self, avId: int) -> None:
        """Sends an update to all interested clients to show the
        seated toon taking their seat, as they should.
        """
        self.sendUpdate("seatAvatar", [avId])
    
    def d_unseatAvatar(self, avId: int, animate: bool=True) -> None:
        """Sends an update to all interested clients to show the
        seated toon getting out of their seat.
        """
        # Remove the unexpected exit hook.
        self.ignore(simbase.air.getAvatarExitEvent(avId))
        # Remove the death hook.
        self.ignore(DistributedToonAI.getGoneSadMessageForAvId(avId))
        # Remove the battle hook.
        self.ignore(f"toonEnteredBattle-{avId}")

        # Set the seated av id to 0.
        self.seatedAvId = 0

        messenger.send(f"unseatedAvatar-{self.chairGroup}", [avId])

        self.sendUpdate("unseatAvatar", [avId, animate])
        
    def d_rejectAvatar(self, avId: int) -> None:
        """Sends an update to the given avatar id to gently reject
        their sincere request to take this seat.
        """
        self.sendUpdateToAvatarId(avId, "rejectAvatar", [])
    
    def d_setOwner(self) -> None:
        if not self.wantToono:
            return

        if not self.playerList:
            self.owner = 0
        else:
            self.owner = self.playerList[0]

        self.sendUpdate("setOwner", [self.owner, self.playerList])
    
    def d_setHouseRules(self, houseRuleData: list) -> None:
        if not self.wantToono:
            return

        self.sendUpdate("setHouseRules", [houseRuleData])
    
    def d_toggleGame(self, flag: bool) -> None:
        if not self.wantToono:
            return

        self.sendUpdate("toggleGame", [flag])
    
    def b_setLockChair(self, flag: bool) -> None:
        self.d_setLockChair(flag)
        self.setLockChair(flag)        
    
    def d_setLockChair(self, flag: bool) -> None:
        self.sendUpdate("setLockChair", [flag])

    def setLockChair(self, flag: bool) -> None:
        self.flag = flag
    
    """
    Getters
    """

    def getWantToono(self) -> bool:
        return self.wantToono

    def getMusicType(self) -> MusicTypeEnum:
        return self.musicType

    def getChairType(self) -> ChairTypeEnum:
        return self.chairType

    def getChairNumber(self) -> int:
        return self.chairNumber
    
    def getRadius(self) -> int:
        return self.radius
    
    def getHopOnPos(self):
        return self.hopOnPos

    def getHopOffPos(self):
        return self.hopOffPos
    
    def getWantOrbitCamera(self):
        return self.wantOrbitCamera
    
    def getLockChair(self):
        return self.lockChair
    
    """
    Misc methods
    """

    def handleUnexpectedExit(self, avId: int) -> None:
        """Oh no! Our seated toon has, for some reason, exited the game while
        they were lounging! 
        Sad.
        Get rid of them.
        """
        self.notify.warning(f"Avatar {avId} has unexpectedly disconnected.")
        self.d_unseatAvatar(avId)
    
    def forceUnseatAvatar(self, lockChair: bool=False) -> None:
        # Also set the lock flag.
        self.b_setLockChair(lockChair)

        if self.seatedAvId == 0:
            return
        
        self.d_unseatAvatar(self.seatedAvId)
    
    """
    Picnic game specific logic
    """

    def seatedAvatar(self, avId: int) -> None:
        if not self.wantToono:
            return

        if self.game is None:
            self.playerList.append(avId)
        else:
            self.spectators.append(avId)

        self.d_setOwner()
    
    def unseatedAvatar(self, avId: int) -> None:
        if not self.wantToono:
            return

        if avId in self.playerList:
            self.playerList.remove(avId)
        if avId in self.spectators:
            self.spectators.remove(avId)

        if self.game is not None:
            self.game.b_setPlayers(self.playerList)
            self.game.b_setSpectators(self.spectators)
            self.game.avatarExit(avId)

        self.d_setOwner()
    
    def gameStarted(self, game: DistributedToonoAI) -> None:
        """Message sent by the owner of the game that the game has been started.
        This will distribute the game to every chair in the chair group.
        """
        self.game = game
        self.d_toggleGame(True)

    def stopGame(self) -> None:
        if self.game is not None:
            self.game.requestDelete()
            self.game = None

        messenger.send(f"gameStopped-{self.chairGroup}")

    def gameStopped(self) -> None:
        """Message sent by the owner of the table that the game has ended.
        This will ensure that the game is removed from memory.
        """
        self.game = None

        if self.seatedAvId != 0:
            if self.seatedAvId in self.spectators:
                self.spectators.remove(self.seatedAvId)
            if self.seatedAvId not in self.playerList:
                self.playerList.append(self.seatedAvId)

        self.d_toggleGame(False)
        self.d_setOwner()
    
    def kickOffPlayer(self, avId: int) -> None:
        pass # stub, let the natural afk timer kick them off the seat (and the game)
