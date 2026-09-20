from toontown.level.BasicEntities import DistributedNodePathEntity
from direct.distributed.ClockDelta import *
from toontown.building.ElevatorUtils import *
from toontown.building.SuitBuildingGlobals import *
from direct.gui.DirectGui import *
from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from toontown.suit import SuitDNA
from toontown.toonbase import TTLocalizer
from toontown.distributed import DelayDelete
from toontown.toon import TTEmote
from direct.fsm.FSM import FSM
from toontown.building.DistributedBuilding import INSIGNIA_COLORS


SBP = 'phase_4/models/modules/suit_landmark_'
SuitBuildingModels = {}
for dept, deptName in (('g', 'board'), ('c', 'corp'), ('l', 'legal'), ('m', 'money'), ('s', 'sales')):
    SuitBuildingModels[dept] = f'{SBP}{deptName}'


class DistributedBuildingEntity(DistributedNodePathEntity, FSM):
    """
    DistributedBuildingEntity(DistributedNodePathEntity)

    A building that leads you to an interior zone
    or suit interior.
    """
    defaultTransitions = {
        'Off': ['WaitForVictors', 'BecomingToon', 'Toon', 'ClearOutToonInterior', 'BecomingSuit', 'Suit'],
        'WaitForVictors': ['BecomingToon'],
        'BecomingToon': ['Toon'],
        'Toon': ['ClearOutToonInterior'],
        'ClearOutToonInterior': ['BecomingSuit'],
        'BecomingSuit': ['Suit'],
        'Suit': ['WaitForVictors', 'BecomingToon'],
    }

    SUIT_INIT_HEIGHT = 125
    TAKEOVER_SFX_PREFIX = 'phase_5/audio/sfx/'

    def __init__(self, cr):
        DistributedNodePathEntity.__init__(self, cr)
        FSM.__init__(self, self.__class__.__name__)
        self.geom = None
        self.suitGeom = None
        self.suitBuildingOrigin = None
        self.buildingReady = False
        self.suitDoorOrigin = None
        self.elevatorModel = None
        self.request("Off")

        # multitrack used to animate the transitions between suit and toon buildings
        self.transitionTrack = None

        # reference to the elevator created when a building is a suit type
        self.elevatorNodePath = None

        # The list of toons who just won the building back.
        self.victorList = [0, 0, 0, 0]

        # This becomes a Label for the text that is displayed while we are waiting for the elevator doors to open.
        self.waitingMessage = None

        self.floorIndicator = []
        self.leftDoor = None

    @property
    def loader(self):
        return base.cr.playGame.hood.loader

    def generate(self):
        DistributedNodePathEntity.generate(self)
        self.mode = 'Toon'

    def announceGenerate(self):
        DistributedNodePathEntity.announceGenerate(self)
        self.geom = loader.loadModel(self.modelFilename)
        self.geom.reparentTo(self)
        self.geom.flattenLight()
        self.suitBuildingOrigin = self.attachNewNode('suitBuildingOrigin')
        suitOrigin = self.geom.find('**/*suit_building_origin')
        if suitOrigin:
            self.suitBuildingOrigin.setPos(suitOrigin.getPos(self.geom))

    def disable(self):
        # Go to the off state when the object is put in the cache
        self.request('Off')
        self.stopTransition()
        if self.suitGeom:
            self.suitGeom.removeNode()
            self.suitGeom = None
        if self.geom:
            self.geom.removeNode()
            self.geom = None
        DistributedNodePathEntity.disable(self)

    def delete(self):
        if self.elevatorNodePath:
            self.elevatorNodePath.removeNode()
            del self.elevatorNodePath
            del self.elevatorModel
            if hasattr(self, 'cab'):
                del self.cab
            del self.leftDoor
            del self.rightDoor
        del self.suitDoorOrigin
        self.cleanupSuitBuilding()
        FSM.cleanup(self)
        DistributedNodePathEntity.delete(self)

    def setSuitData(self, suitTrack, difficulty, numFloors):
        self.debugPrint("setSuitData(%s, %d, %d)" % (suitTrack, difficulty, numFloors))
        self.track = suitTrack
        self.difficulty = difficulty
        self.numFloors = numFloors

    def setState(self, state, timestamp):
        self.request(state, globalClockDelta.localElapsedTime(timestamp))

    def getSuitElevatorNodePath(self):
        """
        :returns: the elevator node path associated with the suit building.

        This assumes the building is in suit mode.
        If the building is not in suit mode (in particular, if it hasn't had any mode at all set yet), assumes the
        building is meant to be in suit mode and switches it immediately.
        """
        if self.mode != 'Suit':
            self.setToSuit()
        return self.elevatorNodePath

    def getSuitDoorOrigin(self):
        if self.mode != 'Suit':
            self.setToSuit()
        return self.suitDoorOrigin

    def setVictorList(self, victorList):
        self.victorList = victorList

    ##### off state #####

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    ##### waitForVictors state #####

    def enterWaitForVictors(self, ts):
        if self.mode != 'Suit':
            self.setToSuit()
        victorCount = self.victorList.count(base.localAvatar.doId)
        if victorCount == 1:
            self.acceptOnce('insideVictorElevator', self.handleInsideVictorElevator)

            # Since the localToon is on the elevator, we should position the camera in front of the building so we have
            # something to look at while we're waiting for everyone to load up the zone.
            # This duplicates the camera setup in the beginning of walkOutCameraTrack().
            camera.reparentTo(render)
            camera.setPosHpr(self.elevatorNodePath, 0, -32.5, 9.4, 0, 348, 0)
            base.camLens.setMinFov(settings['fieldofview'] / (4. / 3.))

            # Are we waiting for any other players to come out?
            anyOthers = 0
            for v in self.victorList:
                if v != 0 and v != base.localAvatar.doId:
                    anyOthers = 1

            if anyOthers:
                self.waitingMessage = DirectLabel(
                    text=TTLocalizer.BuildingWaitingForVictors,
                    text_fg=VBase4(1, 1, 1, 1),
                    text_align=TextNode.ACenter,
                    relief=None,
                    pos=(0, 0, 0.35),
                    scale=0.1
                )

        elif victorCount == 0:
            pass
        else:
            self.error('enterWaitForVictors(): localToon is on the victorList %d times' % victorCount)

        # Make sure the elevator doors are still closed in this state.
        closeDoors(self.leftDoor, self.rightDoor)

        # And turn off the elevator light.
        for light in self.floorIndicator:
            if light is not None:
                light.setColor(LIGHT_OFF_COLOR)

    def handleInsideVictorElevator(self):
        self.notify.debug('handleInsideVictorElevator(): inside victor elevator')
        self.sendUpdate('setVictorReady', [])

    def exitWaitForVictors(self):
        self.ignore('insideVictorElevator')
        if self.waitingMessage is not None:
            self.waitingMessage.destroy()
            self.waitingMessage = None

    ##### becomingToon state #####

    def enterBecomingToon(self, ts):
        self.debugPrint("enterBecomingToon() %s" % (str(self.getDoId())))
        self.animToToon(ts)

    def exitBecomingToon(self):
        self.debugPrint("exitBecomingToon()")

    ##### toon state #####

    def enterToon(self, ts):
        self.debugPrint("enterToon()")
        self.setToToon()

    def exitToon(self):
        self.debugPrint("exitToon()")

    ##### ClearOutToonInterior state #####

    def enterClearOutToonInterior(self, ts):
        self.debugPrint("enterClearOutToonInterior()")

    def exitClearOutToonInterior(self):
        self.debugPrint("exitClearOutToonInterior()")

    ##### becomingSuit state #####

    def enterBecomingSuit(self, ts):
        self.debugPrint("enterBecomingSuit()")
        self.animToSuit(ts)

    def exitBecomingSuit(self):
        self.debugPrint("exitBecomingSuit()")

    ##### suit state #####

    def enterSuit(self, ts):
        self.debugPrint("enterSuit()")
        self.setToSuit()

    def exitSuit(self):
        self.debugPrint("exitSuit()")

    def loadElevator(self, newNP):
        self.debugPrint("loadElevator(newNP=%s)" % (newNP,))
        # Put up a display to show the current floor of the elevator
        self.floorIndicator = []
        # Load up an elevator
        self.elevatorNodePath = hidden.attachNewNode('elevatorNodePath')
        self.elevatorModel = loader.loadModel('phase_4/models/modules/elevator')

        self.elevatorModel.clearColorScale()
        npc = self.elevatorModel.findAllMatches('**/floor_light_?;+s')
        for np in reversed(npc):
            np.setDepthTest(1)
            np.setBin('fixed', 0)
            # Get the last character, and make it zero based:
            floor = int(np.getName()[-1:]) - 1
            self.floorIndicator.append(np)
            if floor < self.numFloors:
                np.setColor(LIGHT_OFF_COLOR)
            else:
                np.hide()

        self.elevatorModel.reparentTo(self.elevatorNodePath)

        if self.mode == 'Suit':
            # Add in a corporate icon
            self.cab = self.elevatorModel.find('**/elevator')
            cogIcons = loader.loadModel('phase_3/models/gui/cog_icons')
            dept = chr(self.track)
            if dept == 'c':
                corpIcon = cogIcons.find('**/CorpIcon').copyTo(self.cab)
            elif dept == 's':
                corpIcon = cogIcons.find('**/SalesIcon').copyTo(self.cab)
            elif dept == 'l':
                corpIcon = cogIcons.find('**/LegalIcon').copyTo(self.cab)
            elif dept == 'm':
                corpIcon = cogIcons.find('**/MoneyIcon').copyTo(self.cab)
            elif dept == 'g':
                corpIcon = cogIcons.find('**/BoardIcon').copyTo(self.cab)
            corpIcon.setPos(0, 6.79, 6.8)
            corpIcon.setScale(3)
            corpIcon.setColor(INSIGNIA_COLORS[dept])
            cogIcons.removeNode()

        self.leftDoor = self.elevatorModel.find('**/left-door')
        if self.leftDoor.isEmpty():
            self.leftDoor = self.elevatorModel.find('**/left_door')

        self.rightDoor = self.elevatorModel.find('**/right-door')
        if self.rightDoor.isEmpty():
            self.rightDoor = self.elevatorModel.find('**/right_door')

        # Find the door origin
        self.suitDoorOrigin = newNP.find('**/*_door_origin')

        # Put the elevator under the door origin
        self.elevatorNodePath.reparentTo(self.suitDoorOrigin)
        self.normalizeElevator()

    def loadAnimToSuitSfx(self):
        """
        Loads up the sound effects necessary for the animToSuit effect.
        """
        if ConfigVariableBool('want-qa-regression', False).getValue():
            self.notify.info('QA-REGRESSION: COGBUILDING: Cog Take Over')

    def loadAnimToToonSfx(self):
        """
        Loads up the sound effects necessary for the animToToon effect.
        """
        if ConfigVariableBool('want-qa-regression', False).getValue():
            self.notify.info('QA-REGRESSION: COGBUILDING: Toon Take Over')

    def _deleteTransitionTrack(self):
        if self.transitionTrack:
            DelayDelete.cleanupDelayDeletes(self.transitionTrack)
            self.transitionTrack = None

    def animToSuit(self, timeStamp):
        """
        creates the multitrack that contains the animation sequence to transition this bldg from a toon to suit building
        :param timeStamp:
        :type timeStamp:
        :return:
        :rtype:
        """
        self.debugPrint("animToSuit(timeStamp=%s)" % (timeStamp,))
        self.stopTransition()
        if self.mode != 'Toon':
            self.setToToon()
        self.loadAnimToSuitSfx()

        self.setupSuitBuilding()
        self.suitGeom.stash()

        # Make sure the doors are closed for now.
        closeDoors(self.leftDoor, self.rightDoor)

        timeForDrop = TO_SUIT_BLDG_TIME * 0.85

        # create intervals to position and/or hide/stash the building parts
        # depending if it is part of the toon or suit version
        tracks = Parallel(name=self.taskName('toSuitTrack'))

        # set the position of the node, then unstash it to show it
        showTrack = Sequence(name=self.taskName('ToSuitFlatsTrack') + '-' + str(self.blockNumber))
        initPos = Point3(0, 0, self.SUIT_INIT_HEIGHT) + self.suitGeom.getPos()
        showTrack.append(Func(self.suitGeom.setPos, initPos))
        showTrack.append(Func(self.suitGeom.unstash))

        showTrack.append(Func(self.normalizeElevator))
        showTrack.append(Func(base.playSfx, self.loader.cogDropSound, 0, 1, None, 0.0))
        showTrack.append(LerpPosInterval(self.suitGeom, timeForDrop, self.suitGeom.getPos(),
                                         name=self.taskName('ToSuitAnim') + '-' + str(self.blockNumber)))
        showTrack.append(Func(base.playSfx, self.loader.cogLandSound, 0, 1, None, 0.0))
        showTrack.append(self.createBounceTrack(self.suitGeom, 2, 0.65, TO_SUIT_BLDG_TIME - timeForDrop, slowInitBounce=1.0))
        showTrack.append(Func(base.playSfx, self.loader.cogSettleSound, 0, 1, None, 0.0))
        tracks.append(showTrack)

        hideToonTrack = Sequence(name=self.taskName('ToSuitToonFlatsTrack'))

        # figure how long till the toon building will start to be compressed by the suit bldg coming down on it
        timeTillSquish = (self.SUIT_INIT_HEIGHT - 20.0) / self.SUIT_INIT_HEIGHT
        timeTillSquish *= timeForDrop
        hideToonTrack.append(
            LerpFunctionInterval(self.adjustColorScale, fromData=1, toData=0.25, duration=timeTillSquish,
                                 extraArgs=[self.geom]))
        hideToonTrack.append(LerpScaleInterval(self.geom, timeForDrop - timeTillSquish, Vec3(1, 1, 0.01)))
        hideToonTrack.append(Func(self.geom.stash))
        hideToonTrack.append(Func(self.geom.setScale, Vec3(1)))
        hideToonTrack.append(Func(self.geom.clearColorScale))
        tracks.append(hideToonTrack)

        # bundle up all of our tracks for the entire transition and start playing
        self.stopTransition()
        self._deleteTransitionTrack()
        self.transitionTrack = tracks
        self.transitionTrack.start(timeStamp)

    def setupSuitBuilding(self):
        self.suitGeom = loader.loadModel(SuitBuildingModels[chr(self.track)])

        # Setup the sign:
        buildingTitle = self.buildingName
        if not buildingTitle:
            buildingTitle = TTLocalizer.CogsInc + TTLocalizer.DeptBldgExt.get(chr(self.track), TTLocalizer.CogsIncExt)
        else:
            buildingTitle += TTLocalizer.DeptBldgExt.get(chr(self.track), TTLocalizer.CogsIncExt)
        buildingTitle += '\n%s' % SuitDNA.getDeptFullname(chr(self.track))

        # Try to find this signText in the node map
        textNode = TextNode('sign')
        textNode.setTextColor(1.0, 1.0, 1.0, 1.0)
        textNode.setFont(ToontownGlobals.getSuitFont())
        textNode.setAlign(TextNode.ACenter)
        textNode.setWordwrap(17.0)
        textNode.setText(buildingTitle)

        # Since the text is wordwrapped, it may flow over more than one line.
        # Try to adjust the scale and position of the sign accordingly.
        textHeight = textNode.getHeight()
        zScale = (textHeight + 2) / 3.0

        # Determine where the sign should go:
        signOrigin = self.suitGeom.find('**/sign_origin;+s')

        backgroundNP = loader.loadModel('phase_5/models/modules/suit_sign')
        backgroundNP.reparentTo(signOrigin)
        backgroundNP.setPosHprScale(
            0.0, 0.0, textHeight * 0.8 / zScale,
            0.0, 0.0, 0.0,
            8.0, 8.0, 8.0 * zScale
        )
        # backgroundNP.node().setEffect(DecalEffect.make())

        # Get the text node path:
        signTextNodePath = backgroundNP.attachNewNode(textNode.generate())
        # Scale the text:
        signTextNodePath.setPosHprScale(
            0.0, -0.001, -0.21 + textHeight * 0.1 / zScale,
            0.0, 0.0, 0.0,
            0.1, 0.1, 0.1 / zScale
        )
        # Clear parent color higher in the hierarchy
        signTextNodePath.setColor(1.0, 1.0, 1.0, 1.0)
        # Decal sign onto the front of the building:
        frontNP = self.suitGeom.find('**/*_front/+GeomNode;+s')
        backgroundNP.wrtReparentTo(frontNP)
        if frontNP.node().isGeomNode():
            frontNP.node().setEffect(DecalEffect.make())

        # Get rid of any transitions and extra nodes
        self.suitGeom.flattenMedium()
        self.suitGeom.reparentTo(self.suitBuildingOrigin)
        self.loadElevator(self.suitGeom)

    def cleanupSuitBuilding(self):
        if hasattr(self, 'floorIndicator'):
            del self.floorIndicator

    def adjustColorScale(self, scale, node):
        node.setColorScale(scale, scale, scale, 1)

    def animToToon(self, timeStamp):
        """
        create the multitrack that contains the animation sequence to transition this building from a suit to toon bldg
        """

        self.stopTransition()
        if self.mode != 'Suit':
            self.setToSuit()

        self.loadAnimToToonSfx()

        # create ivals to position and/or hide/stash the building parts depending if it is part of the toon or suit ver
        tracks = Parallel()

        hideSuitTrack = Sequence(name=self.taskName('ToToonSuitFlatsTrack'))
        hideSuitTrack.append(Func(base.playSfx, self.loader.cogWeakenSound, 0, 1, None, 0.0))
        hideSuitTrack.append(self.createBounceTrack(self.suitGeom, 3, 1.2, TO_TOON_BLDG_TIME * 0.05, slowInitBounce=0.0))
        hideSuitTrack.append(self.createBounceTrack(self.suitGeom, 5, 0.8, TO_TOON_BLDG_TIME * 0.1, slowInitBounce=0.0))
        hideSuitTrack.append(self.createBounceTrack(self.suitGeom, 7, 1.2, TO_TOON_BLDG_TIME * 0.17, slowInitBounce=0.0))
        hideSuitTrack.append(self.createBounceTrack(self.suitGeom, 9, 1.2, TO_TOON_BLDG_TIME * 0.18, slowInitBounce=0.0))
        realScale = self.suitGeom.getScale()
        hideSuitTrack.append(LerpScaleInterval(self.suitGeom, TO_TOON_BLDG_TIME * 0.1, Vec3(realScale[0], realScale[1], 0.01)))

        def clearSuitGeom():
            self.suitGeom.removeNode()
            self.suitGeom = None

        # the landmark portion is recreated each time a suit building is generated, so we can just
        # completely remove the node
        hideSuitTrack.append(Func(clearSuitGeom))
        tracks.append(hideSuitTrack)

        hideToonTrack = Sequence(name=self.taskName('ToToonFlatsTrack'))
        # show the toon portion of the building and set up transparency transition so we can slowly fade it in
        hideToonTrack.append(Wait(TO_TOON_BLDG_TIME * 0.5))
        hideToonTrack.append(Func(base.playSfx, self.loader.toonGrowSound, 0, 1, None, 0.0))
        hideToonTrack.append(Func(self.geom.unstash))
        hideToonTrack.append(Func(self.geom.setScale, Vec3(1, 1, 0.01)))
        hideToonTrack.append(Func(base.playSfx, self.loader.toonSettleSound, 0, 1, None, 0.0))
        hideToonTrack.append(self.createBounceTrack(self.geom, 11, 1.2, TO_TOON_BLDG_TIME * 0.5, slowInitBounce=4.0))
        tracks.append(hideToonTrack)

        # bundle up all of our tracks for the entire transition and start playing
        self.stopTransition()
        bldgMTrack = tracks

        localToonIsVictor = self.localToonIsVictor()
        victoryRunTrack, delayDeletes = self.getVictoryRunTrack()

        trackName = self.taskName('toToonTrack')
        self._deleteTransitionTrack()
        if localToonIsVictor:
            camTrack = self.walkOutCameraTrack()
            freedomTrack = Sequence(
                # "Stun" the toon so that they get i-frames from cog battles and a very brief
                # inability to enter doors (for the sake of YOTT)
                Func(base.localAvatar.stunToon, short=True),
                Func(self.cr.playGame.getPlace().setState, 'Walk'),
                Func(base.localAvatar.d_setParent, ToontownGlobals.SPRender)
            )
            self.transitionTrack = Parallel(
                camTrack,
                Sequence(
                    Func(base.transitions.fadeIn, 0.8),
                    victoryRunTrack,
                    bldgMTrack,
                    freedomTrack,
                ),
                name=trackName
            )
        else:
            self.transitionTrack = Sequence(
                victoryRunTrack,
                bldgMTrack,
                name=trackName
            )
        self.transitionTrack.delayDeletes = delayDeletes
        if localToonIsVictor:
            self.transitionTrack.start(0)
        else:
            self.transitionTrack.start(timeStamp)

    def walkOutCameraTrack(self):
        track = Sequence(
            # Put the camera under render
            Func(camera.reparentTo, render),
            # Watch the toons come out of the door
            Func(camera.setPosHpr, self.elevatorNodePath, 0, -32.5, 9.4, 0, 348, 0),
            Func(base.camLens.setMinFov, settings['fieldofview'] / (4. / 3.)),
            Wait(VICTORY_RUN_TIME),
            # Watch the building transform
            Func(camera.setPosHpr, self.elevatorNodePath, 0, -32.5, 17, 0, 347, 0),
            Func(base.camLens.setMinFov, 75.0 / (4. / 3.)),
            Wait(TO_TOON_BLDG_TIME),
            # Put the camera fov back to normal
            Func(base.camLens.setMinFov, settings['fieldofview'] / (4. / 3.))
        )
        return track

    def plantVictorsOutsideBldg(self):
        self.notify.debug("plantVictorsOutsideBldg(): planting Victors %s !" % self.victorList)
        retVal = 0
        for victor in self.victorList:
            if victor != 0 and victor in self.cr.doId2do:
                toon = self.cr.doId2do[victor]
                toon.setPosHpr(self.elevatorModel, 0, -10, 0, 0, 0, 0)
                toon.startSmooth()
                if victor == base.localAvatar.getDoId():
                    retVal = 1
                    self.cr.playGame.getPlace().setState('Walk')

        return retVal

    def getVictoryRunTrack(self):
        # Put each toon in the elevator
        origPosTrack = Sequence()
        delayDeletes = []
        i = 0
        for victor in self.victorList:
            if victor != 0 and victor in self.cr.doId2do:
                toon = self.cr.doId2do[victor]
                delayDeletes.append(DelayDelete.DelayDelete(toon, 'getVictoryRunTrack'))
                toon.stopSmooth()
                toon.setParent(ToontownGlobals.SPHidden)
                origPosTrack.append(
                    Func(toon.setPosHpr, self.elevatorNodePath, Point3(*ElevatorPoints[i]), Point3(180, 0, 0)))
                origPosTrack.append(Func(toon.setParent, ToontownGlobals.SPRender))
            i += 1

        # Open the elevator doors
        openDoors = getOpenInterval(self, self.leftDoor, self.rightDoor, self.loader.elevatorOpenSfx, None)
        toonDoor = self.geom.find('**/*door_origin')
        useFarExitPoints = True  # toonDoor.getPos(render).getZ() > 1.0

        # Run the toons out of the elevator
        runOutAll = Parallel()
        i = 0
        for victor in self.victorList:
            if victor != 0 and victor in self.cr.doId2do:
                toon = self.cr.doId2do[victor]
                p0 = Point3(0, 0, 0)
                p1 = Point3(ElevatorPoints[i][0], ElevatorPoints[i][1] - 5.0, ElevatorPoints[i][2])
                if useFarExitPoints:
                    p2 = Point3(ElevatorOutPointsFar[i][0], ElevatorOutPointsFar[i][1], ElevatorOutPointsFar[i][2])
                else:
                    p2 = Point3(ElevatorOutPoints[i][0], ElevatorOutPoints[i][1], ElevatorOutPoints[i][2])

                runOutSingle = Sequence(
                    # Disallow body emotes so we don't slide
                    Func(TTEmote.globalEmote.disableBody, toon, 'getVictory'),
                    # Start the run animation
                    Func(toon.request, 'Run'),
                    # Move the toon out of the elevator
                    LerpPosInterval(toon, TOON_VICTORY_EXIT_TIME * 0.25, p1, other=self.elevatorNodePath),
                    # Run him from there to his observation point
                    Func(toon.headsUp, self.elevatorNodePath, p2),
                    LerpPosInterval(toon, TOON_VICTORY_EXIT_TIME * 0.5, p2, other=self.elevatorNodePath),
                    # Turn the toon around to face the building
                    LerpHprInterval(
                        toon, TOON_VICTORY_EXIT_TIME * 0.25, Point3(0, 0, 0), other=self.elevatorNodePath
                    ),
                    # Stop the toon from running
                    Func(toon.request, 'Neutral'),
                    # Free the toon up to walk around on his own again
                    Func(toon.startSmooth),
                    Func(TTEmote.globalEmote.releaseBody, toon, 'getVictory')
                )
                runOutAll.append(runOutSingle)
            i += 1

        victoryRunTrack = Sequence(
            origPosTrack,
            openDoors,
            runOutAll
        )

        return (victoryRunTrack, delayDeletes)

    def localToonIsVictor(self):
        retVal = 0
        for victor in self.victorList:
            if victor == base.localAvatar.getDoId():
                retVal = 1

        return retVal

    def createBounceTrack(self, nodeObj, numBounces, startScale, totalTime, slowInitBounce=0.0):
        if not nodeObj or numBounces < 1 or startScale == 0.0 or totalTime == 0:
            self.notify.warning('createBounceTrack(): called with invalid parameter')
            return

        # add an extra bounce to make sure the object is properly scaled to 1 on the last lerpScaleInterval
        result = Sequence()
        numBounces += 1

        # calculate how long, in seconds, each bounce should last, make the time of each bounce smaller if we want to
        # extend the length the initial bounce
        if slowInitBounce:
            bounceTime = totalTime / (numBounces + slowInitBounce - 1.0)
        else:
            bounceTime = totalTime / float(numBounces)

        # if specified, the first bounce lasts the length of 3 bounces, useful for when initially appearing, the first
        # bounce of the object is more pronounced than the others
        if slowInitBounce:
            currTime = bounceTime * float(slowInitBounce)
        else:
            currTime = bounceTime

        # determine the how much of a change in scale the first bounce will produce based on the node's base scale
        # (current scale) and the given start scale
        realScale = nodeObj.getScale()
        currScaleDiff = startScale - realScale[2]

        # create a lerpScaleInterval for each bounce, making sure to figure out the new scale, which progressively gets
        # closer to our base scale
        for currBounceScale in range(numBounces):
            # determine the direction that this scale should go, alternating for each lerpScaleInterval to simulate
            # a spring effect
            if currBounceScale == numBounces - 1:
                currScale = realScale[2]
            elif currBounceScale % 2:
                currScale = realScale[2] - currScaleDiff
            else:
                currScale = realScale[2] + currScaleDiff
            result.append(
                LerpScaleInterval(
                    nodeObj,
                    currTime,
                    Vec3(realScale[0], realScale[1], currScale),
                    blendType='easeInOut'
                )
            )

            # the scale diff from the base gets smaller for each consecutive bounce, and make sure to update for
            # possibly a new amount of time the next bounce will take
            currScaleDiff *= 0.5
            currTime = bounceTime

        return result

    def stopTransition(self):
        if self.transitionTrack:
            self.transitionTrack.finish()
            self._deleteTransitionTrack()

    def setToSuit(self):
        self.debugPrint("setToSuit()")
        self.stopTransition()
        if self.mode == 'Suit':
            return
        self.mode = 'Suit'

        # Trusting this based on old code...
        if self.geom:
            self.geom.stash()
        if self.suitGeom:
            self.suitGeom.removeNode()
            self.suitGeom = None
        self.setupSuitBuilding()

    def setToToon(self):
        self.debugPrint("setToToon() mode=%s" % (self.mode))
        self.stopTransition()
        if self.mode == 'Toon':
            return
        self.mode = 'Toon'

        if self.geom:
            self.geom.unstash()
        if self.suitGeom:
            self.suitGeom.removeNode()
            self.suitGeom = None

        # Clear reference to the suit door.
        self.suitDoorOrigin = None

    def normalizeElevator(self):
        """
        Normalize the size of the elevator
        The suit building probably has a funny scale on it, but by doing this, we normalize the scale on the elevator.
        """
        self.elevatorNodePath.setScale(render, Vec3(1, 1, 1))
        self.elevatorNodePath.setPosHpr(0, 0, 0, 0, 0, 0)

    def debugPrint(self, message):
        """for debugging"""
        if __debug__:
            return self.notify.debug(str(self.__dict__.get('blockNumber', '?')) + ' ' + message)

    def getBossLevel(self):
        return False
