from typing import Optional

from panda3d.core import BitMask32, CollisionNode, CollisionSphere, Point3, Quat, Vec3
from direct.distributed.ClockDelta import globalClockDelta
from direct.distributed.DistributedNode import DistributedNode
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import *
from direct.showbase import PythonUtil
from direct.showbase.MessengerGlobal import messenger

from toontown.gui.game.condition import ConditionGlobals
from toontown.safezone.picnicgame import PicnicGameGlobals, ToonoGlobals
from toontown.safezone.picnicgame.PicnicGameChooser import PicnicGameChooser
from toontown.safezone.picnicgame.PicnicGameGlobals import PicnicTableState
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownTimer import ToontownTimer
from toontown.inventory.enums.ItemEnums import CheesyEffectItemType
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedPicnicGameTable(DistributedNode, FSM):
    cameraControl = False

    def __init__(self, cr) -> None:
        DistributedNode.__init__(self, cr)
        FSM.__init__(self, "DistributedPicnicGameTable")

        self.picnicTable = None
        self.tableCloth = None
        self.tableClothNode = None

        self.tableNumber: int = 0

        self.avatars: dict[int, PicnicTableState] = {}

        self.seats = []
        self.jumpOffsets = []
        self.picnicTableNodes = []

        self.clockNode: Optional[ToontownTimer] = None

        self.timerEnd = None

        self.camTrack = None
        self.toonTracks = {}

        self.gameChooser: Optional[PicnicGameChooser] = None

        # The leader is the toon who is in charge of picking games and who gets
        # to play the game. This toon is determined by who joined the table
        # first, and will change when that toon leaves.
        self.leader: int = 0

        # Keep track of the game that the leader has picked so that any toons
        # newly joining the table can be made aware of what's going on.
        self.gameChosen: int = -1

        # Keep track of every avatar due to start playing the game, including
        # the leader themself.
        self.playerList = []

        self.localSeatIndex: int = -1

        self.houseRules = ToonoGlobals.DEFAULT_HOUSE_RULES.copy()

    def generate(self) -> None:
        DistributedNode.generate(self)
        self.loader = self.cr.playGame.hood.loader

    def announceGenerate(self) -> None:
        DistributedNode.announceGenerate(self)

        self.tableName = self.uniqueName("TableSeat")

        # Find all of the seats and jumpout locators.
        for i in range(PicnicGameGlobals.NUM_SEATS):
            self.seats.append(self.getModel().find(f"**/*seat{i + 1}"))
            self.jumpOffsets.append(self.getModel().find(f"**/*jumpOut{i + 1}"))

        self.tableCloth = self.getModel().find("**/basket_locator")
        # Make a node, copying the position and hpr of table cloth but parented to render.
        # This gives us a node to parent toons to for placement purposes.
        # (If we reparented toons to tableCloth, then their color scale would be unintentionally changed on Halloween.)
        self.toonPlacementNode = render.attachNewNode('toonPlacementNode')
        self.toonPlacementNode.setPosHpr(self.tableCloth, 0, 0, 0, 0, 0, 0)

        # Stops you from walking on the table
        self.tableClothNode = self.tableCloth.attachNewNode(CollisionNode('tablecloth_sphere'))
        self.tableClothNode.node().addSolid(CollisionSphere(0, 0, 2, 5.5))

        # Set up the collision spheres for the seats.
        for i in range(PicnicGameGlobals.NUM_SEATS):
            self.picnicTableNodes.append(self.seats[i].attachNewNode(CollisionNode(f"{self.tableName}-{i}")))
            self.picnicTableNodes[i].node().addSolid(CollisionSphere(0, 0, 0, 2))

        self._enableCollisions()

        self.d_requestTableState()

    def delete(self) -> None:
        self.leader = None

        self.stopMoveCamera()
        self.destroyUI()

        self.clearToonTracks()
        self.destroyCollisions()
        self.toonPlacementNode.removeNode()
        self.toonPlacementNode = None

        self.ignoreAll()

        FSM.cleanup(self)
        DistributedNode.delete(self)

    def getModel(self):
        if self.picnicTable is None:
            self.picnicTable = self.loader.geom.find(f'**/*game_table_{self.tableNumber}')
        return self.picnicTable

    def allowExit(self) -> None:
        messenger.send("enableExitButton")
        self.accept("TableExit", self.d_requestExit)
        self.accept(base.MAP_PAGE_HOTKEY, messenger.send, extraArgs=["RequestTableExit"])

    """
    Functions for the picnic table's collisions
    """

    def _enableCollisions(self) -> None:
        """Begin listening for toons to enter."""
        for i in range(PicnicGameGlobals.NUM_SEATS):
            self.accept(f"enter{self.tableName}-{i}", self.enterTableSeatCollision, [i])
            self.accept(f"enter{self.tableName}-{i}_OK", self.enterTableSeat, [i])
            self.picnicTableNodes[i].setCollideMask(ToontownGlobals.WallBitmask)

        self.tableClothNode.setCollideMask(ToontownGlobals.WallBitmask)

    def _disableCollisions(self) -> None:
        """Stop listening for toons to enter."""
        for i in range(PicnicGameGlobals.NUM_SEATS):
            self.ignore(f"enter{self.tableName}")
            self.ignore(f"enter{self.tableName}_OK")
            self.picnicTableNodes[i].setCollideMask(BitMask32(0))

        self.tableClothNode.setCollideMask(BitMask32(0))

    def destroyCollisions(self) -> None:
        """Destroy all the collisions."""
        for col in self.picnicTableNodes:
            col.remove_node()

        self.picnicTableNodes = []

        self.tableClothNode.remove_node()
        self.tableClothNode = None

    def enterTableSeatCollision(self, seatIndex: int, entry) -> None:
        self.loader.place.request("PicnicTableBlock", self.tableName, seatIndex)

    def enterTableSeat(self, seatIndex: int) -> None:
        self.d_requestBoard(seatIndex)

    """
    Messages sent to the server from the client
    """

    def d_requestPlayGame(self) -> None:
        self.sendUpdate("requestPlayGame")

    def d_requestPlayerList(self, players) -> None:
        self.sendUpdate("requestPlayerList", [players])

    def d_requestChosenGame(self, gameChosen: int) -> None:
        self.sendUpdate("requestChosenGame", [gameChosen])

    def d_requestTableState(self) -> None:
        """This function is called when a client enters the zone, and needs to
        be made aware of the current state of the table. This will do things
        like animate the toons into their seats, etc.
        """
        self.sendUpdate("requestTableState")

    def d_requestBoard(self, seatIndex: int) -> None:
        self.sendUpdate("requestBoard", [seatIndex])

    def d_requestExit(self) -> None:
        self.sendUpdate("requestExit")

    def d_sendHouseRules(self, houseRuleData) -> None:
        self.sendUpdate("sendHouseRules", [houseRuleData])

    """
    Messages that the client receives from the server
    """

    def setHouseRules(self, houseRuleData) -> None:
        houseRules = {houseRule: value for houseRule, value in houseRuleData}
        self.houseRules.update(houseRules)

        # Let any listeners know that the house rules have been changed.
        messenger.send(self.uniqueName("pgt_houseRules_updated"), [self.houseRules])

    def setPlayerList(self, players) -> None:
        self.playerList = players

        for avatar in self.avatars:
            if avatar != self.leader:
                if avatar in players:
                    self.avatars[avatar] = PicnicTableState.PLAYER
                else:
                    self.avatars[avatar] = PicnicTableState.SPECTATOR

        messenger.send(ConditionGlobals.RefreshMsg)

        # Let any listeners know that the player list has been changed.
        messenger.send(self.uniqueName("pgt_playerList_updated"), [players])

    def setChosenGame(self, gameChosen: int) -> None:
        self.gameChosen = gameChosen

        # Let any listeners know that the chosen game has been changed.
        messenger.send(self.uniqueName("pgt_chosenGame_updated"), [gameChosen])

    def setLeader(self, leader: int) -> None:
        self.leader = leader

        self.avatars[leader] = PicnicTableState.LEADER
        messenger.send(ConditionGlobals.RefreshMsg)

        # Let any listeners know that there has been a change in leadership.
        messenger.send(self.uniqueName("pgt_leader_updated"), [leader])

    def setTableNumber(self, tableNumber: int) -> None:
        self.tableNumber = tableNumber

    def setTableState(self, tableState) -> None:
        """Process the table state data that the server has sent to us.
        """
        # Animate each toon going into their respective seat.
        for seatIndex, avId in tableState:
            self.fillSeat(avId, seatIndex)

    def setState(self, state: str) -> None:
        self.request(state)

    def rejectBoard(self) -> None:
        # This toon is rejected, let them walk.
        self.loader.place.trolley.handleRejectBoard()

    def fillSeat(self, avId: int, seatIndex: int) -> None:
        """Animate the toon entering the seat for every interested client, and
        animate the local toon's camera accordingly.
        """
        toon = self.cr.doId2do.get(avId)
        if not toon or toon.isEmpty():
            return

        toon.stopSmooth()
        toon.setGeomNodeH(0)
        toon.wrtReparentTo(self.toonPlacementNode)

        jumpTrack = self.createHopOnTrack(toon, seatIndex)

        track = Sequence(
            jumpTrack,
            Func(toon.setAnimState, "Sit", 1.0),
            autoFinish=1,
        )

        if toon.isLocal():
            base.localAvatar.stopSleepWatch()
            base.cr.gameGui.expBar.hide()

            track.append(Func(self._disableCollisions))
            track.append(Func(self.createUI))
            track.append(Func(self.startTimer))

        elif self.localToonSeated:
            track.append(Func(messenger.send, ConditionGlobals.RefreshMsg))

        track.append(Func(self.clearToonTrack, avId))

        self.storeToonTrack(track, avId)

        track.start()

    def emptySeat(self, avId: int, seatIndex: int) -> None:
        """Animate the toon exiting the seat for every interested client, and
        animate the local toon's camera accordingly.
        """
        if avId in self.avatars:
            del self.avatars[avId]

        if self.localToonSeated:
            messenger.send(ConditionGlobals.RefreshMsg)

        toon = self.cr.doId2do.get(avId)
        if not toon or toon.isEmpty():
            return

        toon.stopSmooth()

        jumpOutTrack = self.createHopOffTrack(toon, seatIndex)

        track = Sequence(jumpOutTrack)

        if base.localAvatar.getDoId() == avId:
            base.cr.gameGui.expBar.show()
            self.destroyUI()
            self.stopMoveCamera()
            self.ignore(base.MAP_PAGE_HOTKEY)
            self.ignore("TableExit")

            track.append(Func(self._enableCollisions))
        else:
            track.append(Func(toon.startSmooth))

        track.append(Func(self.clearToonTrack, avId))

        self.storeToonTrack(track, avId)

        track.start()

    def informAvatarEnter(self, avId: int, seatIndex: int) -> None:
        if base.localAvatar.doId == avId:
            self.localSeatIndex = seatIndex

        if avId not in self.avatars:
            self.avatars[avId] = PicnicTableState.SPECTATOR

        messenger.send(ConditionGlobals.RefreshMsg)

        # Let any listeners know that a toon has entered the seat.
        messenger.send(self.uniqueName("enteredTableSeat"), [avId])

    def informAvatarExit(self, avId: int, seatIndex: int) -> None:
        if base.localAvatar.doId == avId:
            self.localSeatIndex = -1

        if avId in self.avatars:
            del self.avatars[avId]

        # Let any listeners know that a toon has exited the seat.
        messenger.send(self.uniqueName("exitedTableSeat"), [avId])

    """
    Functions that help make stuff happen on the screen
    """

    def storeToonTrack(self, track: Sequence, avId: int) -> None:
        if avId in self.toonTracks:
            self.clearToonTrack(avId)

        self.toonTracks[avId] = track

    def clearToonTrack(self, avId: int) -> None:
        track = self.toonTracks.get(avId)
        if track:
            track.pause()

    def clearToonTracks(self) -> None:
        for avId in self.toonTracks:
            self.clearToonTrack(avId)

        self.toonTracks = {}

    def createHopOnTrack(self, av, seatIndex: int) -> Sequence:
        """
        Return an interval of the toon jumping onto the picnic table.
        :param av:
        :param seatIndex:
        :return:
        """

        av.pose('sit', 47)
        hipOffset = av.getHipsParts()[0].getPos(av)

        # using a local func allows the ProjectileInterval to
        # calculate this pos at run-time
        def getJumpDest():
            if av.cheesyEffect in [CheesyEffectItemType.SmallToon, CheesyEffectItemType.SmallLegs]:
                if seatIndex < 3:
                    hipOffset.setY(-0.75)
                else:
                    hipOffset.setY(-1.25)

            dest = Vec3(0, 0, 0)
            seatNode = self.getModel().find(f"**/seat{seatIndex + 1}")
            dest += seatNode.getPos(self.toonPlacementNode)
            dna = av.getStyle()
            dest -= hipOffset
            if seatIndex > 2:
                dest.setY(dest.getY() - 2.0)
            if seatIndex == 1:
                dest.setY(dest.getY() - .5)
            dest.setZ(dest.getZ() + 0.2)

            return dest

        def getJumpHpr():
            hpr = self.seats[seatIndex].getHpr(self.toonPlacementNode)
            if seatIndex < 3:
                hpr.setX(hpr.getX())
            elif not av.isEmpty() and av.getH() < 0:
                hpr.setX(hpr.getX() - 180)
            else:
                hpr.setX(hpr.getX() + 180)
            return hpr

        jumpTrack = Sequence(
            Parallel(
                Parallel(
                    ActorInterval(av, 'jump'),
                    Sequence(
                        Wait(0.43),
                        Parallel(
                            LerpHprInterval(av, hpr=getJumpHpr, duration=1),
                            ProjectileInterval(av, endPos=getJumpDest, duration=1)
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
                ),
            ),
        )

        if av.isLocal():
            jumpTrack.append(Func(base.localAvatar.setTeleportAvailable, 1))
            jumpTrack.append(Func(self.allowExit))

            camera.wrtReparentTo(self.tableCloth)

            if self.getCurrentOrNextState() != "Playing":
                heading = PythonUtil.fitDestAngle2Src(camera.getH(self.tableCloth), 90)
                return Parallel(
                    jumpTrack,
                    LerpPosHprInterval(
                        camera, 2, Point3(19, 0, 14), Point3(heading, -30, 0), blendType='easeInOut'
                    )
                )

        return jumpTrack

    def createHopOffTrack(self, av, seatIndex: int) -> Sequence:
        """
        Return an interval of the toon jumping off of the picnic table.
        :param av:
        :param seatIndex:
        :return:
        """

        # using a local func allows the ProjectileInterval to
        # calculate this pos at run-time
        def getJumpDest(node=self.toonPlacementNode):
            dest = node.getPos(self.toonPlacementNode)
            dest += self.jumpOffsets[seatIndex].getPos(self.toonPlacementNode)
            return dest

        jumpTrack = Sequence(
            Parallel(
                Func(av.setShadowHeight, 0),
                ActorInterval(av, 'jump'),
                Sequence(
                    Wait(0.1),
                    Parallel(
                        LerpHprInterval(av, hpr=(av.getH(render), 0, 0), other=render, duration=.9),
                        ProjectileInterval(av, endPos=getJumpDest, duration=.9)
                    ),
                )
            ),
            Func(av.loop, 'neutral'),
            Func(av.wrtReparentTo, render),
        )
        if av.isLocal():
            jumpTrack.append(Func(messenger.send, "ExitTableDone"))

        return jumpTrack

    def moveCamera(self) -> None:
        """
        Smoothly moves the camera above the picnic table.
        :return: None
        """
        if self.toonPlacementNode is None:
            return

        heading = PythonUtil.fitDestAngle2Src(camera.getH(self.toonPlacementNode), 90)

        quat = Quat()
        quat.setHpr((heading, -30, 0))

        self.camTrack = LerpPosQuatInterval(camera, 2, Point3(14, 0, 14), quat, blendType='easeInOut')
        self.camTrack.start()

    def stopMoveCamera(self) -> None:
        if self.camTrack is not None:
            self.camTrack.finish()
            self.camTrack = None

    """
    UI specific functions
    """

    def createUI(self) -> None:
        self.destroyUI()

        # Don't make the ui if the table is off or a game is in session.
        if self.getCurrentOrNextState() != "Boarding":
            return

        # Create the conditional frames.
        stateArgs = ConditionGlobals.ConditionStateArgs()
        stateArgs[ConditionGlobals.ConditionStateArg.PICNIC_TABLE] = self
        messenger.send(ConditionGlobals.SetStateMsg, [ConditionGlobals.ConditionState.PGT_TABLE, stateArgs])

        self.createTimer()

        self.gameChooser = PicnicGameChooser(self)
        self.gameChooser.setGameChosen(self.gameChosen)
        self.gameChooser.setLeader(self.leader)
        self.gameChooser.setPlayerList(self.playerList)

    def destroyUI(self) -> None:
        self.destroyTimer()

        messenger.send(ConditionGlobals.SetStateMsg, [ConditionGlobals.ConditionState.GLOBAL])

        if self.gameChooser is not None:
            self.gameChooser.destroy()
            self.gameChooser = None

    """
    Timer specific functions
    """

    def setTimerEnd(self, timerEnd: int) -> None:
        """Set the timestamp that the timer should stop at.
        """
        now = globalClock.getFrameTime()
        self.timerEnd = globalClockDelta.networkToLocalTime(timerEnd, now)
        self.startTimer()

    def startTimer(self) -> None:
        if not self.clockNode:
            return

        # Stop the timer in case it's still running.
        self.clockNode.stop()

        now = globalClock.getFrameTime()
        timeLeft = self.timerEnd - now

        self.clockNode.countdown(timeLeft, self.stopTimer)
        self.clockNode.show()

    def stopTimer(self) -> None:
        self.clockNode.stop()
        self.clockNode.hide()

    def createTimer(self) -> None:
        if self.clockNode:
            return

        self.clockNode = ToontownTimer()
        self.clockNode.posInBottomRightCorner()
        self.clockNode.setScale(0.35)
        self.clockNode.hide()

    def destroyTimer(self) -> None:
        if not self.clockNode:
            return

        self.stopTimer()
        self.clockNode.destroy()
        self.clockNode = None

    """
    FSM states
    """

    def enterBoarding(self) -> None:
        if self.localToonSeated:
            self.createUI()

    def exitBoarding(self) -> None:
        self.destroyUI()

    def exitPlaying(self) -> None:
        if self.localToonSeated:
            self.moveCamera()

    """
    Properties
    """

    @property
    def localToonSeated(self) -> bool:
        return self.localSeatIndex != -1
