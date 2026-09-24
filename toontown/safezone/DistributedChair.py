"""
DistributedChair: home of the universal chair

@author: Travis
@date: 4/15/2022
"""
from typing import Optional

from panda3d.core import CollisionSphere, CollisionNode, Vec3, Point3
from direct.distributed.DistributedNode import DistributedNode
from direct.gui.DirectGui import DGG
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import *
from direct.showbase.MessengerGlobal import messenger

from toontown.gui.game.condition import ConditionGlobals
from toontown.menu.MainMenuGui import MainMenuButton
from toontown.safezone.ChairConstants import ChairTypeEnum, MusicTypeEnum, truePositionChairs, standingChairs
from toontown.safezone.picnicgame.HouseRulesFrame import HouseRulesFrame
from toontown.safezone.picnicgame import ToonoGlobals
from toontown.toon.DistributedToon import DistributedToon
from toontown.toonbase import TTLocalizer, ToontownGlobals


class DistributedChair(DistributedNode):
    """DistributedChair: the client side representation of various sitting devices.
    Handles toon collisions and animating the toon into the chair.
    """
    cameraControl = True

    def __init__(self, cr):
        super().__init__(cr)

        # Sequence for toons jumping on/off the chair.
        self.jumpTrack: Optional[Sequence] = None

        # Unique identifier for the chair.
        self.chairNumber: Optional[int] = None

        # The type of chair.
        self.chairType: ChairTypeEnum = ChairTypeEnum.CHAIR

        # Chair hotkey text
        self.enterText: Optional[OnscreenText] = None

        # Chair hotkey text sequence
        self.enterTextSeq: Optional[Sequence] = None

        # Seated avatar id.
        self.seatedAvId: int = 0

        ### TOONO ###

        # Button used to display house rules.
        self.button_houseRules: MainMenuButton = None

        # Stores the frame of the house rules. 
        self.frame_houseRules: HouseRulesFrame = None

        # Button to begin the game.
        self.button_playGame: MainMenuButton = None

        # Copy of the generic house rules.
        self.houseRules = ToonoGlobals.DEFAULT_HOUSE_RULES.copy()

        # The leader of the game.
        self.owner: int = 0

        # The players of the game.
        self.playerIds = []

        # Stores the status of the game.
        self.gameActive = False

    def generate(self) -> None:
        self.chairName = self.uniqueName('chairSphere')
        self.loader = self.cr.playGame.hood.loader

        super().generate()

    def announceGenerate(self):
        super().announceGenerate()
        self.d_requestChairState()
        self.wrtReparentTo(render)
        self.load()

    def load(self) -> None:
        self.chairSphere = CollisionSphere(0, 0, 0, self.radius)
        self.chairSphere.setTangible(0)
        self.chairSphereNode = CollisionNode(self.chairName)
        self.chairSphereNode.setIntoCollideMask(ToontownGlobals.WallBitmask)
        self.chairSphereNode.addSolid(self.chairSphere)
        self.chairSphereNodePath = self.attachNewNode(self.chairSphereNode)
        self.chairSphereNodePath.reparentTo(self)
        self.acceptCollisions()
        self.accept(f"exit{self.chairName}", self.exitChairCollision)

    def delete(self):
        self.destroyEnterText()
        messenger.send("chairDeleted", [self.chairNumber])
        self.destroyGameButtons()
        self.ignoreAll()
        self.finishJumpTrack()
        super().delete()

    def destroyEnterText(self) -> None:
        if self.enterText is not None:
            self.enterText.destroy()
            self.enterText = None

        if self.enterTextSeq is not None:
            self.enterTextSeq.finish()
            self.enterTextSeq = None

    def acceptCollisions(self) -> None:
        self.accept(f"enter{self.chairName}", self.enterChairCollision)
        self.accept(f"enter{self.chairName}-OK", self.d_requestSeat)

    def ignoreCollisions(self) -> None:
        self.ignore(f"enter{self.chairName}")
        self.ignore(f"enter{self.chairName}-OK")

    def enterChairCollision(self, entry) -> None:
        if self.seatedAvId != 0 or self.lockChair:
            return

        if base.settings["chairkey"]:
            self.destroyEnterText()
            self.accept(base.INTERACT, self.attemptBoardChair)
            self.accept('teleportBegin', self.exitChairCollision)

            chairName = TTLocalizer.ChairNames[self.chairType]
            chairAction = TTLocalizer.ChairActions.get(self.chairType, TTLocalizer.ChairDefaultAction)

            self.enterText = OnscreenText(
                TTLocalizer.ChairEnterText.format(base.INTERACT.upper(), chairAction, chairName),
                style=3,
                scale=.09,
                parent=base.a2dBottomCenter,
                fg=(1, 0.9, 0.1, 1),
                pos=(0.0, 0.5)
            )
            self.enterText.setColorScale(1, 1, 1, 0)
            self.enterTextSeq = Sequence(
                LerpColorScaleInterval(self.enterText, .8, VBase4(1, 1, 1, 1)),
                LerpColorScaleInterval(self.enterText, .8, VBase4(.5, .6, 1, .9))
            )
            self.enterTextSeq.loop()
            return

        self.attemptBoardChair()

    def attemptBoardChair(self) -> None:
        # Remove the hooks + enter text.
        self.exitChairCollision()

        self.loader.place.handleChairCollision(self.chairName)

    def exitChairCollision(self, entry=None) -> None:
        self.ignore(base.INTERACT)
        self.ignore('teleportBegin')

        self.destroyEnterText()

    def allowExit(self) -> None:
        messenger.send("enableExitButton")
        self.accept("ChairExit", self.d_requestExit)
        self.accept(base.MAP_PAGE_HOTKEY, messenger.send, extraArgs=["RequestChairExit"])

    def afkTimeout(self, task) -> None:
        messenger.send("RequestChairExit")
        self.d_requestExit()

    def setLockChair(self, flag: bool) -> None:
        self.lockChair = flag

    """
    Messages sent to the AI
    """

    def d_sendHouseRules(self, houseRuleData: list) -> None:
        self.sendUpdate("requestSetHouseRules", [houseRuleData])

    def d_requestGame(self) -> None:
        self.sendUpdate("requestGame")

    def d_requestSeat(self) -> None:
        """Send a request to the AI for the local toon to
        take this seat.
        """
        self.sendUpdate("requestSeat")

    def d_requestExit(self) -> None:
        """Send a request to the AI for the local toon to
        exit this seat.
        """
        self.sendUpdate("requestExit")

    def d_requestChairState(self) -> None:
        """Send a request to the AI to fetch the
        currently seated avatar.
        """
        self.sendUpdate("requestChairState")

    """
    Messages sent from the AI
    """

    def toggleGame(self, flag: bool) -> None:
        if not self.wantToono:
            return
        self.gameActive = flag
        self.updateButtons()

        if self.seatedAvId == base.localAvatar.doId:
            if not self.gameActive:
                messenger.send(ConditionGlobals.SetStateMsg, [ConditionGlobals.ConditionState.GLOBAL])

                base.localAvatar.startSleepWatch(self.afkTimeout)
            else:
                base.localAvatar.stopSleepWatch()

    def setOwner(self, avId: int, playerIds: list) -> None:
        if not self.wantToono:
            return
        self.owner = avId
        self.playerIds = playerIds
        self.updateButtons()

    def setWantToono(self, wantToono: bool) -> None:
        self.wantToono = wantToono

    def setChairType(self, chairType: ChairTypeEnum) -> None:
        self.chairType = chairType

    def setMusicType(self, musicType: MusicTypeEnum) -> None:
        self.musicType = musicType

    def setChairNumber(self, chairNumber: int) -> None:
        self.chairNumber = chairNumber

    def setRadius(self, radius: int) -> None:
        self.radius = radius

    def setHopOnPos(self, x: float, y: float, z: float) -> None:
        self.hopOnPos = (x, y, z)

    def setHopOffPos(self, x: float, y: float, z: float) -> None:
        self.hopOffPos = (x, y, z)

    def setWantOrbitCamera(self, flag: bool) -> None:
        self.wantOrbitCamera = flag

    def rejectAvatar(self) -> None:
        base.cr.playGame.getPlace().request("Walk")

    def seatAvatar(self, avId: int) -> None:
        """Handles seating the given avatar into the chair.
        """
        toon: DistributedToon = self.cr.doId2do.get(avId)
        if not toon or toon.isEmpty():
            return

        self.seatedAvId = avId

        toon.stopSmooth()
        toon.setGeomNodeH(0)
        toon.wrtReparentTo(self)

        self.jumpTrack = self.generateToonHopOnTrack(toon)

        if toon.isLocal():
            toon.startSleepWatch(self.afkTimeout)
            if __debug__:
                setattr(base, 'chair', self)

        self.jumpTrack.start()

    def unseatAvatar(self, avId: int, animate: bool) -> None:
        """Handles unseating the given avatar from the chair.
        """
        toon: DistributedToon = self.cr.doId2do.get(avId)
        if not toon or toon.isEmpty():
            return

        self.seatedAvId = 0

        toon.stopSmooth()

        self.ignore("ChairExit")
        self.ignore(base.MAP_PAGE_HOTKEY)

        self.jumpTrack = self.generateToonHopOffTrack(toon)

        if toon.isLocal():
            # Force correct the Chair object in our place to ensure
            # that we cleanly exit the state.
            # This is necessary due to the nature of forced exits on the server
            # skipping the entire process of the exit button.
            place = base.cr.playGame.getPlace()
            if place and place.getState() == "Chair":
                if place.chair.getCurrentOrNextState() == "Boarded":
                    place.chair.request("RequestExit")

            toon.stopSleepWatch()
            # toon.cameraFSM.request("Off")

        self.jumpTrack.start()

        if not animate:
            self.jumpTrack.finish()

    """
    Sequencing functions
    """

    def generateToonHopOnTrack(self, av: DistributedToon) -> Sequence:
        """Return an interval of the toon jumping onto the picnic table.
        """
        av.pose('sit', 47)
        hipOffset = av.getHipsParts()[0].getPos(av)

        # using a local func allows the ProjectileInterval to
        # calculate this pos at run-time
        def getJumpDest():
            if self.chairType in truePositionChairs:
                return Vec3(0)
            return Vec3(self.hopOnPos) - hipOffset

        def getJumpHpr():
            return Vec3(180, 0, 0)

        isStanding = self.chairType in standingChairs
        jumpTrack = Sequence(
            Parallel(
                Parallel(
                    ActorInterval(av, 'jump'),
                    Sequence(
                        Wait(0.43),
                        Parallel(
                            LerpHprInterval(av, hpr=getJumpHpr, duration=1),
                            (
                                ProjectileInterval(av, endPos=getJumpDest, duration=1)
                            ) if not isStanding else (
                                ProjectileInterval(av, endPos=getJumpDest, duration=1, gravityMult=1.4)
                            )
                        ),
                    )
                ),
                Sequence(
                    Wait(1),
                    Sequence(
                        ActorInterval(av, 'sit-start'),
                        Func(av.loop, 'sit'),
                        Func(av.setShadowHeight, 7 - av.getHeight())
                    ),
                ) if not isStanding else Wait(0.0),
            ),
            Func(av.setAnimState, "Sit", 1.0) if not isStanding else Wait(0.0),
            autoFinish=1
        )

        if av.isLocal():
            jumpTrack.append(Func(base.localAvatar.setTeleportAvailable, 1))
            jumpTrack.append(Func(self.allowExit))
            if self.wantOrbitCamera:
                jumpTrack.append(Func(base.localAvatar.cameraFSM.request, "Chair"))

            if self.wantToono and self.owner == av.doId:
                jumpTrack.append(Func(self.createGameButtons))

            return Parallel(jumpTrack, self.generateCameraSequence(duration=jumpTrack.getDuration()))

        return jumpTrack

    def generateToonHopOffTrack(self, av: DistributedToon) -> Sequence:
        """Return an interval of the toon jumping off of the picnic table.
        """

        # using a local func allows the ProjectileInterval to
        # calculate this pos at run-time
        def getJumpDest():
            return Vec3(self.hopOffPos)

        isStanding = self.chairType in standingChairs
        jumpTrack = Sequence(
            Parallel(
                Func(av.setShadowHeight, 0),
                ActorInterval(av, 'jump'),
                Sequence(
                    Wait(0.1),
                    Parallel(
                        LerpHprInterval(av, hpr=(av.getH(render), 0, 0), other=render, duration=.9),
                        (
                            ProjectileInterval(av, endPos=getJumpDest, duration=.9)
                        ) if not isStanding else (
                            ProjectileInterval(av, endPos=getJumpDest, duration=.9, gravityMult=1.4)
                        )
                    ),
                )
            ),
            Func(av.loop, 'neutral'),
            Func(av.wrtReparentTo, render),
            Func(messenger.send, "ExitChairDone")
        )

        if av.getHp() <= 0:
            jumpTrack.append(Func(av.died))

        if not av.isLocal():
            jumpTrack.append(Func(av.startSmooth))

        return jumpTrack

    def finishJumpTrack(self) -> None:
        if self.jumpTrack is not None:
            self.jumpTrack.finish()
            self.jumpTrack = None

    def generateCameraSequence(self, duration: float = 2.0):
        """Reparents the camera to the chair and return an interval
        which moves it into place.
        """
        camHeight = (base.localAvatar.getHeight() / 2) + 2
        camera.wrtReparentTo(self)
        camTrack = camera.posHprInterval(
            duration - 0.01, Point3(0, -13, camHeight), Point3(0, 0, 0), blendType='easeInOut')
        return camTrack

    """
    Picnic game specific logic
    """

    def createGameButtons(self) -> None:
        self.destroyGameButtons()

        img_scale = (.35, .15, .15)

        self.button_playGame = MainMenuButton(
            base.a2dBottomRight, pos=(-0.17, 0.0, 0.30),
            text=TTLocalizer.PGTPlayGame,
            command=self.d_requestGame,
            image_scale=img_scale,
            image1_scale=img_scale,
            image2_scale=img_scale,
        )
        self.button_playGame["state"] = DGG.DISABLED if len(self.playerIds) < 2 else DGG.NORMAL

        self.button_houseRules = MainMenuButton(
            base.a2dBottomRight, pos=(-0.17, 0.0, 0.45),
            text=TTLocalizer.PGTHouseRules,
            command=self.openHouseRules,
            image_scale=img_scale,
            image1_scale=img_scale,
            image2_scale=img_scale,
        )

    def updateButtons(self) -> None:
        if not self.gameActive and self.owner == base.localAvatar.doId:
            self.createGameButtons()
        else:
            self.destroyGameButtons()

    def openHouseRules(self) -> None:
        if base.localAvatar.doId != self.owner:
            return

        self.frame_houseRules = HouseRulesFrame(aspect2d, self)

    def destroyGameButtons(self) -> None:
        if self.button_houseRules is not None:
            self.button_houseRules.destroy()
            self.button_houseRules = None

        if self.button_playGame is not None:
            self.button_playGame.destroy()
            self.button_playGame = None

        self.destroyHouseRules()

    def destroyHouseRules(self):
        if self.frame_houseRules is not None:
            self.frame_houseRules.destroy()
            self.frame_houseRules = None
