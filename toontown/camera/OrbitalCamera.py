from panda3d.core import BitMask32, CollisionHandlerFloor, CollisionHandlerQueue
from panda3d.core import CollisionNode, CollisionRay, CollisionSegment
from panda3d.core import CollisionTraverser, NodePath, Point3, Vec3
from panda3d.core import WindowProperties

from direct.directnotify import DirectNotifyGlobal
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import LerpFunc, LerpFunctionInterval
from direct.interval.IntervalGlobal import LerpPosHprInterval, Parallel
from direct.showbase.InputStateGlobal import inputState
from direct.task import Task
from direct.task.TaskManagerGlobal import taskMgr

try:
    from otp.otpbase.PythonUtil import fitSrcAngle2Dest, lerp, reduceAngle
except ImportError:
    from direct.showbase.PythonUtil import fitSrcAngle2Dest, lerp, reduceAngle

from otp.otpbase import OTPGlobals

try:
    from toontown.toonbase import ToontownGlobals
except ImportError:
    ToontownGlobals = None


class OrbitalCamera(FSM, NodePath):
    """Python 2-compatible Corporate Clash-style orbital camera for Altis.

    This keeps Altis's FSM and RMB input interface while restoring the camera
    behavior present in Corporate Clash: camera collision, moving-avatar
    alignment, smooth presets, recentering, saved camera position, disguise /
    first-person hiding, heading limits, and camera-facing helpers.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('OrbitalCamera')

    UpdateTaskName = 'OrbitCamUpdateTask'
    ReadMouseTaskName = 'OrbitCamReadMouseTask'
    CollisionCheckTaskName = 'OrbitCamCollisionTask'

    RecenterOnReleaseEnabled = True

    MinP = -50
    MaxP = 20

    baseH = None
    minH = None
    maxH = None

    _fallbackPresets = [
        [-9, 0, 0],
        [-24, 0, -10],
        [-12, 0, -15]
    ]

    if ToontownGlobals is not None and hasattr(ToontownGlobals, 'cameraPositions'):
        presets = ToontownGlobals.cameraPositions
    else:
        presets = _fallbackPresets

    TopNodeName = 'OrbitCam'

    def __init__(self, subject):
        NodePath.__init__(self, self.TopNodeName)
        FSM.__init__(self, 'OrbitalCamera')

        self.subject = subject
        self.camOffset = Vec3(0, -9, 5.5)

        self.mouseControl = False
        self.mouseDelta = (0, 0)
        self.lastMousePos = (0, 0)
        self.origMousePos = (0, 0)

        self.__inputEnabled = False
        self.mouseX = 0.0
        self.mouseY = 0.0

        self.presetPos = 0
        self.collisionTaskCount = 0
        self.ignoreRMB = False

        self.zIval = None
        self.camIval = None
        self.lerpSequence = None

        self.forceMaxDistance = True
        self.avFacingScreen = False
        self.lastCameraPos = None

        # Updated at the beginning of each frame from the final position
        # left by the previous frame's movement and collision resolution.
        self._subjectMotionPos = None
        self._subjectActuallyMoving = False

        if self.presets:
            self.lastCamY = self.presets[0][0]
        else:
            self.lastCamY = self.camOffset.getY()

        self._rmbToken = inputState.watchWithModifiers('RMB', 'mouse3')

        self.initializeCollisions()
        self.request('Off')

    def getName(self):
        return 'FPS'

    def _getTopNodeName(self):
        return self.TopNodeName

    def destroy(self):
        if self.isActive():
            self.request('Off')
        else:
            self._stopMouseControlTasks()
            self._stopCollisionCheck()
            self._stopSubjectMotionTask()

        self._finishInterval('lerpSequence')
        self._finishInterval('zIval')
        self._finishInterval('camIval')

        self.destroyCollisions()

        if self._rmbToken:
            self._rmbToken.release()
            self._rmbToken = None

        self.ignoreAll()
        self.subject = None
        FSM.cleanup(self)
        self.removeNode()

    def _finishInterval(self, name):
        interval = getattr(self, name, None)
        if interval:
            try:
                interval.finish()
            except Exception:
                pass
        setattr(self, name, None)

    def initializeCollisions(self):
        # Retained from the original Altis camera for compatibility with any
        # code that expects these floor-collision members to exist.
        self.cTravOnFloor = CollisionTraverser('CamMode.cTravOnFloor')
        self.camFloorRayNode = self.attachNewNode('camFloorRayNode')

        self.ccRay2 = CollisionRay(0.0, 0.0, 0.0, 0.0, 0.0, -1.0)

        self.ccRay2Node = CollisionNode('ccRay2Node')
        self.ccRay2Node.addSolid(self.ccRay2)

        self.ccRay2NodePath = self.camFloorRayNode.attachNewNode(self.ccRay2Node)

        self.ccRay2BitMask = OTPGlobals.FloorBitmask
        self.ccRay2Node.setFromCollideMask(self.ccRay2BitMask)
        self.ccRay2Node.setIntoCollideMask(BitMask32.allOff())

        self.ccRay2MoveNodePath = hidden.attachNewNode('ccRay2MoveNode')

        self.camFloorCollisionBroadcaster = CollisionHandlerFloor()
        self.camFloorCollisionBroadcaster.setInPattern('zone_on-floor')
        self.camFloorCollisionBroadcaster.setOutPattern('zone_off-floor')
        self.camFloorCollisionBroadcaster.addCollider(
            self.ccRay2NodePath,
            self.ccRay2MoveNodePath
        )

        self.cTravOnFloor.addCollider(
            self.ccRay2NodePath,
            self.camFloorCollisionBroadcaster
        )

    def destroyCollisions(self):
        if hasattr(self, 'cTravOnFloor') and hasattr(self, 'ccRay2NodePath'):
            try:
                self.cTravOnFloor.removeCollider(self.ccRay2NodePath)
            except Exception:
                pass

        if hasattr(self, 'camFloorCollisionBroadcaster'):
            try:
                self.camFloorCollisionBroadcaster.removeCollider(
                    self.ccRay2NodePath
                )
            except Exception:
                pass
            del self.camFloorCollisionBroadcaster

        if hasattr(self, 'cTravOnFloor'):
            del self.cTravOnFloor

        if hasattr(self, 'ccRay2'):
            del self.ccRay2

        if hasattr(self, 'ccRay2Node'):
            del self.ccRay2Node

        if hasattr(self, 'ccRay2NodePath'):
            self.ccRay2NodePath.removeNode()
            del self.ccRay2NodePath

        if hasattr(self, 'ccRay2MoveNodePath'):
            self.ccRay2MoveNodePath.removeNode()
            del self.ccRay2MoveNodePath

        if hasattr(self, 'camFloorRayNode'):
            self.camFloorRayNode.removeNode()
            del self.camFloorRayNode

    def enterActive(self):
        self.enableInput()

        try:
            base.camNode.setLodCenter(self.subject)
        except Exception:
            pass

        self._initMaxDistance()
        self._startCollisionCheck()
        self._resetSubjectMotion()
        self._startSubjectMotionTask()
        self.acceptWheel()
        self.acceptTab()

        try:
            if self.subject and not self.subject.isEmpty():
                self.reparentTo(self.subject)
        except Exception:
            pass
            
        try:
            base.camera.reparentTo(self)
        except Exception:
            pass

        self.setPos(0, 0, self.subject.getHeight())
        camera.setPosHpr(
            self.camOffset[0],
            self.camOffset[1],
            0,
            0,
            0,
            0
        )

        place = None
        try:
            place = base.cr.playGame.getPlace()
        except Exception:
            pass

        if place and place.getState() == 'walk':
            self.loadLastCameraPos()
        elif self.presets:
            self.setPresetPos(self.presetPos, transition=False)

    def exitActive(self):
        self.saveLastCameraPos()
        self._finishInterval('camIval')

        self._stopCollisionCheck()
        self._stopSubjectMotionTask()
        self._resetSubjectMotion()

        try:
            base.camNode.setLodCenter(NodePath())
        except Exception:
            pass

        self.ignoreWheel()
        self.ignoreTab()
        self.ignore('recenterCameraNow')
        self.disableInput()

    def _initMaxDistance(self):
        self._maxDistance = abs(self.camOffset[1])

    def _getSetting(self, names, default):
        if not isinstance(names, (tuple, list)):
            names = (names,)

        settingObjects = []

        if hasattr(base, 'settings'):
            settingObjects.append(base.settings)

        moduleSettings = globals().get('settings')
        if moduleSettings is not None:
            settingObjects.append(moduleSettings)

        for settingObject in settingObjects:
            for name in names:
                try:
                    if hasattr(settingObject, 'get'):
                        marker = object()
                        value = settingObject.get(name, marker)
                        if value is not marker:
                            return value
                    else:
                        return settingObject[name]
                except Exception:
                    try:
                        return settingObject[name]
                    except Exception:
                        pass

        return default

    def _camToggleLock(self):
        default = getattr(base, 'CAM_TOGGLE_LOCK', False)
        return bool(self._getSetting(
            ('cam-toggle-lock', 'camToggleLock'),
            default
        ))

    def _recenterOnRelease(self):
        return bool(self._getSetting(
            ('cam-recenter-on-release', 'camRecenterOnRelease'),
            False
        ))

    def _recenterOnMovement(self):
        return bool(self._getSetting(
            ('cam-recenter-on-movement', 'camRecenterOnMovement'),
            False
        ))

    def _handleRMB(self, pressed):
        if self.ignoreRMB:
            return

        if self._camToggleLock():
            if pressed:
                if self.mouseControl:
                    self.disableMouseControl(True)
                else:
                    self.enableMouseControl(True)
        elif pressed:
            self.enableMouseControl(True)
        else:
            self.disableMouseControl(False)

    def enableMouseControl(self, pressed):
        if pressed is False or self.ignoreRMB or self.mouseControl:
            return

        if self.oobeEnabled():
            return

        self._finishInterval('lerpSequence')
        self.mouseControl = True

        mouseData = base.win.getPointer(0)
        self.origMousePos = (mouseData.getX(), mouseData.getY())

        centerX = base.win.getXSize() // 2
        centerY = base.win.getYSize() // 2
        base.win.movePointer(0, centerX, centerY)
        self.lastMousePos = (centerX, centerY)

        if self.getCurrentOrNextState() == 'Active':
            self._startMouseControlTasks()

        self.setCursor(True)
        self._setSubjectMouseControls(True)

        if self._recenterOnMovement():
            self.ignore('recenterCameraNow')

    def disableMouseControl(self, pressed, disabledByMouse=True):
        if self.oobeEnabled() or not self.mouseControl:
            return

        self.mouseControl = False
        self._stopMouseControlTasks()

        try:
            base.win.movePointer(
                0,
                int(self.origMousePos[0]),
                int(self.origMousePos[1])
            )
        except Exception:
            pass

        self.setCursor(False)
        self._setSubjectMouseControls(False)

        if disabledByMouse:
            if self._recenterOnRelease() and self.RecenterOnReleaseEnabled:
                self.setPresetPos(self.presetPos, implicitY=True)

            if self._recenterOnMovement() and not self.isSubjectMoving():
                self.acceptOnce(
                    'recenterCameraNow',
                    self.setPresetPos,
                    [self.presetPos, True]
                )

    def _setSubjectMouseControls(self, enabled):
        controlManager = getattr(self.subject, 'controlManager', None)
        if not controlManager:
            return

        try:
            controlManager.setTurn(0 if enabled else 1)
        except Exception:
            pass

        if enabled:
            try:
                controlManager.enableLMBForward()
            except Exception:
                pass
        else:
            try:
                controlManager.disableLMBForward()
            except Exception:
                pass

    def setCursor(self, hiddenCursor):
        properties = WindowProperties()
        properties.setCursorHidden(hiddenCursor)
        base.win.requestProperties(properties)

    def enableInput(self):
        self.__inputEnabled = True
        self.accept('InputState-RMB', self._handleRMB)

        if inputState.isSet('RMB') and not self._camToggleLock():
            self.enableMouseControl(True)

    def disableInput(self):
        self.__inputEnabled = False
        self.disableMouseControl(False, False)
        self.ignore('InputState-RMB')

    def isInputEnabled(self):
        return self.__inputEnabled

    def _getSubjectControlSpeeds(self):
        controlManager = getattr(self.subject, 'controlManager', None)
        if controlManager is None:
            return (0.0, 0.0, 0.0)

        if not getattr(self.subject, 'avatarControlsEnabled', False):
            return (0.0, 0.0, 0.0)

        if not getattr(controlManager, 'isEnabled', False):
            return (0.0, 0.0, 0.0)

        try:
            speeds = controlManager.getSpeeds()
        except Exception:
            speeds = None

        if not speeds or len(speeds) < 3:
            return (0.0, 0.0, 0.0)

        result = []
        for speed in speeds[:3]:
            try:
                result.append(float(speed))
            except (TypeError, ValueError):
                result.append(0.0)

        return tuple(result)

    def _repairSubjectControls(self):
        # The Altis teleport path can leave ControlManager.isEnabled true
        # after GravityWalker.controlsTask was removed. In that state key
        # input is visible, but getSpeeds() stays at zero until another
        # teleport happens. Restore only that inconsistent state.
        if self.subject is None:
            return

        if not getattr(self.subject, 'avatarControlsEnabled', False):
            return

        controlManager = getattr(self.subject, 'controlManager', None)
        if controlManager is None or not getattr(
                controlManager, 'isEnabled', False):
            return

        controls = getattr(controlManager, 'currentControls', None)
        if controls is None:
            return

        if not getattr(controls, 'collisionsActive', False):
            return

        if hasattr(controls, 'controlsTask') and controls.controlsTask is None:
            try:
                controls.enableAvatarControls()
            except Exception:
                pass

    def _resetSubjectMotion(self):
        self._subjectActuallyMoving = False
        self._subjectMotionPos = None

        if self.subject is not None:
            try:
                self._subjectMotionPos = Point3(self.subject.getPos(render))
            except Exception:
                pass

    def _startSubjectMotionTask(self):
        self._stopSubjectMotionTask()
        taskMgr.add(
            self._subjectMotionTask,
            self.TopNodeName + '-SubjectMotion',
            priority=22
        )

    def _stopSubjectMotionTask(self):
        taskMgr.remove(self.TopNodeName + '-SubjectMotion')

    def _subjectMotionTask(self, task):
        # This task runs immediately before the RMB avatar-facing task. The
        # position delta therefore represents the previous frame after the
        # world collision traversers and pushers finished correcting it.
        self._repairSubjectControls()

        if self.subject is None:
            self._subjectActuallyMoving = False
            return task.cont

        try:
            currentPos = Point3(self.subject.getPos(render))
        except Exception:
            self._subjectMotionPos = None
            self._subjectActuallyMoving = False
            return task.cont

        previousPos = self._subjectMotionPos
        self._subjectMotionPos = currentPos

        if previousPos is None:
            self._subjectActuallyMoving = False
            return task.cont

        forwardSpeed, unusedRotateSpeed, strafeSpeed = \
            self._getSubjectControlSpeeds()

        requestedSpeed = (
            (forwardSpeed * forwardSpeed) +
            (strafeSpeed * strafeSpeed)
        ) ** 0.5

        dx = currentPos.getX() - previousPos.getX()
        dy = currentPos.getY() - previousPos.getY()
        actualDistance = ((dx * dx) + (dy * dy)) ** 0.5

        try:
            dt = globalClock.getDt()
        except Exception:
            dt = 0.0

        if dt < 0.0:
            dt = 0.0
        elif dt > 0.1:
            dt = 0.1

        # Require a useful fraction of the movement requested by the active
        # walker. A wall/boss pusher may produce tiny position jitter, but it
        # must not let RMB rotate the Toon in a stationary circle.
        minimumDistance = max(0.002, requestedSpeed * dt * 0.15)
        self._subjectActuallyMoving = bool(
            requestedSpeed > 0.0001 and
            actualDistance >= minimumDistance
        )

        return task.cont

    def isSubjectMoving(self):
        return self._subjectActuallyMoving

    def _isAimingPie(self):
        return bool(getattr(base.localAvatar, 'isAimingPie', False))

    def _avatarFacingTask(self, task):
        if self.oobeEnabled() or self.avFacingScreen:
            return task.cont

        if self.isSubjectMoving() or self._isAimingPie():
            camH = self.getH(render)
            subjectH = self.subject.getH(render)
            if abs(camH - subjectH) > 0.01:
                self.subject.setH(render, camH)
                self.setH(0)

        return task.cont

    def _mouseUpdateTask(self, task):
        if self.oobeEnabled():
            return task.cont

        subjectMoving = self.isSubjectMoving()
        aimingPie = self._isAimingPie()

        if subjectMoving or aimingPie:
            hNode = self.subject
        else:
            hNode = self

        if self.mouseDelta[0] or self.mouseDelta[1]:
            dx, dy = self.mouseDelta

            camSensitivityX = self._getSetting(
                ('camSensitivityX', 'cam-sensitivity-x'),
                0.31
            )
            camSensitivityY = self._getSetting(
                ('camSensitivityY', 'cam-sensitivity-y'),
                0.21
            )

            options = getattr(base, 'options', None)
            if options is not None and getattr(options, 'mouse_look', False):
                dy = -dy

            hNode.setH(hNode, -dx * camSensitivityX)

            curP = self.getP()
            newP = curP + -dy * camSensitivityY
            newP = min(max(newP, self.MinP), self.MaxP)
            self.setP(newP)

            if self.baseH is not None:
                try:
                    messenger.send('pistolMoved')
                except Exception:
                    pass
                self._checkHBounds(hNode)

            self.setR(render, 0)

        return task.cont

    def setHBounds(self, baseH, minH, maxH):
        self.baseH = baseH
        self.minH = minH
        self.maxH = maxH

        if self.isSubjectMoving() or self._isAimingPie():
            hNode = self.subject
        else:
            hNode = self

        hNode.setH(maxH)

    def clearHBounds(self):
        self.baseH = None
        self.minH = None
        self.maxH = None

    def _checkHBounds(self, hNode):
        currH = fitSrcAngle2Dest(hNode.getH(), 180)

        if currH < self.minH:
            hNode.setH(reduceAngle(self.minH))
        elif currH > self.maxH:
            hNode.setH(reduceAngle(self.maxH))

    def acceptWheel(self):
        self.accept('wheel_up', self._handleWheelUp)
        self.accept('wheel_down', self._handleWheelDown)
        self.accept('page_up', self._handleWheelUp)
        self.accept('page_down', self._handleWheelDown)
        self._resetWheel()

    def ignoreWheel(self):
        self.ignore('wheel_up')
        self.ignore('wheel_down')
        self.ignore('page_up')
        self.ignore('page_down')
        self._resetWheel()

    def _getCameraPosHotkey(self):
        if ToontownGlobals is not None and hasattr(
            ToontownGlobals,
            'NextCameraPosHotkey'
        ):
            return ToontownGlobals.NextCameraPosHotkey

        return 'tab'

    def acceptTab(self):
        self.accept(self._getCameraPosHotkey(), self.nextCameraPos)

    def ignoreTab(self):
        self.ignore(self._getCameraPosHotkey())

    def toggleFirstPerson(self):
        # Kept as an alias because existing Altis code may still call it.
        self.nextCameraPos()

    def _handleSetWheel(self, y):
        if hasattr(self, '_collSolid'):
            self._collSolid.setPointB(0, y + 1, 0)

        self.camOffset.setY(y)
        self.lastCamY = y

        t = (-14 - y) / -12
        height = self.subject.getHeight()
        z = lerp(height, height, t)
        self.setZ(z)

    def _handleWheelUp(self):
        y = max(-25, min(-2, self.camOffset[1] + 1.0))
        self._handleSetWheel(y)

    def _handleWheelDown(self):
        y = max(-25, min(-2, self.camOffset[1] - 1.0))
        self._handleSetWheel(y)

    def _resetWheel(self):
        if not self.isActive():
            return

        self.camOffset = Vec3(0, -14, 5.5)

        y = self.camOffset[1]
        z = self.camOffset[2]

        if hasattr(self, '_collSolid'):
            self._collSolid.setPointB(0, y + 1, 0)

        self.setZ(z)

    def getCamOffset(self):
        return self.camOffset

    def setCamOffset(self, camOffset):
        self.camOffset = Vec3(camOffset)

    def applyCamOffset(self):
        if self.isActive():
            camera.setPos(self.camOffset)

    def _setCamDistance(self, distance):
        offset = camera.getPos(self)
        if offset.lengthSquared() == 0:
            return
        offset.normalize()
        camera.setPos(self, offset * distance)

    def _getCamDistance(self):
        return camera.getPos(self).length()

    def _startCollisionCheck(self):
        self._stopCollisionCheck()

        self._collSolid = CollisionSegment(
            0,
            0,
            0,
            0,
            -(self._maxDistance + 1.0),
            0
        )

        collSolidNode = CollisionNode('OrbitCam.CollSolid')
        collSolidNode.addSolid(self._collSolid)

        collSolidNode.setFromCollideMask(
            OTPGlobals.CameraBitmask |
            OTPGlobals.CameraTransparentBitmask |
            OTPGlobals.FloorBitmask
        )
        collSolidNode.setIntoCollideMask(BitMask32.allOff())

        self._collSolidNp = self.attachNewNode(collSolidNode)

        self._cHandlerQueue = CollisionHandlerQueue()
        self._cTrav = CollisionTraverser('OrbitCam.cTrav')
        self._cTrav.addCollider(self._collSolidNp, self._cHandlerQueue)

        taskMgr.add(
            self._collisionCheckTask,
            OrbitalCamera.CollisionCheckTaskName,
            priority=45
        )

    def _getSubjectGeomRoot(self):
        if self.subject is None:
            return None

        if hasattr(self.subject, 'getGeom'):
            try:
                return self.subject.getGeom()
            except Exception:
                pass

        if hasattr(self.subject, 'getGeomNode'):
            try:
                return self.subject.getGeomNode()
            except Exception:
                pass

        return self.subject

    def _getSubjectGeomNode(self):
        if self.subject is None:
            return None

        if hasattr(self.subject, 'getGeomNode'):
            try:
                return self.subject.getGeomNode()
            except Exception:
                pass

        if hasattr(self.subject, 'getGeom'):
            try:
                return self.subject.getGeom()
            except Exception:
                pass

        return None

    def _subjectIsDisguised(self):
        for avatar in (self.subject, getattr(base, 'localAvatar', None)):
            if avatar is None:
                continue

            value = getattr(avatar, 'isDisguised', False)
            try:
                if callable(value):
                    value = value()
            except Exception:
                value = False

            if value:
                return True

        return False

    def _collisionCheckTask(self, task):
        if self.oobeEnabled():
            return Task.cont

        geomRoot = self._getSubjectGeomRoot()
        if geomRoot is None:
            return Task.cont

        self._cTrav.traverse(geomRoot)

        if self.firstPerson or self._subjectIsDisguised():
            self._hideSubjectGeom()
        else:
            self._showSubjectGeom()

        numEntries = self._cHandlerQueue.getNumEntries()
        for index in range(numEntries):
            if not self._cHandlerQueue.getEntry(index).hasSurfacePoint():
                return Task.cont

        self._cHandlerQueue.sortEntries()

        collEntry = None
        cNormal = Vec3(0, -1, 0)

        if self._cHandlerQueue.getNumEntries() > 0:
            collEntry = self._cHandlerQueue.getEntry(0)
            cNormal = collEntry.getSurfaceNormal(self)

        if not collEntry or not collEntry.hasSurfacePoint():
            if self.forceMaxDistance:
                camera.setPos(self.camOffset)
                camera.setZ(0)

            if not self.firstPerson:
                if self._subjectIsDisguised():
                    self._hideSubjectGeom()
                else:
                    self._showSubjectGeom()

            return Task.cont

        cPoint = collEntry.getSurfacePoint(self)
        camera.setPos(cPoint + cNormal * 0.9)

        if not self.firstPerson:
            if camera.getDistance(self) < 1.8 or self._subjectIsDisguised():
                self._hideSubjectGeom()
            else:
                self._showSubjectGeom()

        localAvatar = getattr(base, 'localAvatar', None)
        pusherTrav = getattr(localAvatar, 'ccPusherTrav', None)
        if pusherTrav:
            try:
                pusherTrav.traverse(render)
            except Exception:
                pass

        return Task.cont

    def _stopCollisionCheck(self):
        taskMgr.remove(OrbitalCamera.CollisionCheckTaskName)

        if hasattr(self, '_cTrav') and hasattr(self, '_collSolidNp'):
            try:
                self._cTrav.removeCollider(self._collSolidNp)
            except Exception:
                pass

        if hasattr(self, '_cHandlerQueue'):
            del self._cHandlerQueue

        if hasattr(self, '_cTrav'):
            del self._cTrav

        if hasattr(self, '_collSolidNp'):
            self._collSolidNp.detachNode()
            del self._collSolidNp

        if hasattr(self, '_collSolid'):
            del self._collSolid

        if self.subject:
            if self._subjectIsDisguised():
                self._hideSubjectGeom()
            else:
                self._showSubjectGeom()

    def _hideSubjectGeom(self):
        geomNode = self._getSubjectGeomNode()
        if geomNode:
            geomNode.hide()

    def _showSubjectGeom(self):
        geomNode = self._getSubjectGeomNode()
        if geomNode:
            geomNode.show()

    def lerpFromZOffset(self, z=0.0, duration=1):
        self._finishInterval('zIval')

        self.zIval = LerpFunc(
            self.setZ,
            duration,
            fromData=z + self.camOffset[2],
            toData=self.camOffset[2]
        )
        self.zIval.start()
        self.zIval.setT(0)

    def avFaceCamera(self):
        if not self.mouseControl or self.avFacingScreen:
            self.avFacingScreen = False
            camH = self.getH(render)
            subjectH = self.subject.getH(render)
            if abs(camH - subjectH) > 0.01:
                self.subject.setH(render, camH)
                self.setH(0)

    def avFaceScreen(self):
        if not self.mouseControl:
            self.avFacingScreen = True
            camH = self.getH(render)
            self.subject.setH(render, camH - 180)
            self.setH(180)

    def isAvFacingScreen(self):
        return self.avFacingScreen

    def setForceMaxDistance(self, force):
        self.forceMaxDistance = force

    def nextCameraPos(self):
        localAvatar = getattr(base, 'localAvatar', None)
        if localAvatar and getattr(localAvatar, 'localToonTyping', False):
            return

        if not self.presets:
            return

        self.presetPos += 1
        if self.presetPos >= len(self.presets):
            self.presetPos = 0

        self.setPresetPos(self.presetPos)
        self.lastCamY = self.presets[self.presetPos][0]

    def setPresetPos(self, presetIndex, implicitY=False, transition=True):
        if not self.presets:
            return

        self.presetPos = presetIndex % len(self.presets)
        preset = self.presets[self.presetPos]

        if implicitY:
            y = self.lastCamY
        else:
            y = preset[0]

        self.setCameraPos(
            y,
            preset[1],
            preset[2],
            transition=transition
        )

    def setCameraPos(self, y, h, p, transition=True):
        t = (-14 - y) / -12
        z = lerp(self.subject.getHeight(), self.subject.getHeight(), t)

        if hasattr(self, '_collSolid'):
            self._collSolid.setPointB(0, y + 1, 0)

        self._finishInterval('lerpSequence')

        if transition:
            self.lerpSequence = Parallel(
                LerpFunctionInterval(
                    self.camOffset.setY,
                    0.5,
                    fromData=self.camOffset.getY(),
                    toData=y,
                    blendType='easeInOut'
                ),
                LerpPosHprInterval(
                    self,
                    0.5,
                    Point3(self.getX(), self.getY(), z),
                    Point3(h, p, 0),
                    blendType='easeInOut'
                )
            )
            self.lerpSequence.start()
        else:
            self.camOffset.setY(y)
            self.setPos(self.getX(), self.getY(), z)
            self.setHpr(h, p, 0)

    def saveLastCameraPos(self):
        h, p, unusedR = self.getHpr()
        self.lastCameraPos = (self.camOffset[1], h, p)

    def loadLastCameraPos(self):
        if self.lastCameraPos:
            self.setCameraPos(
                self.lastCameraPos[0],
                self.lastCameraPos[1],
                self.lastCameraPos[2],
                transition=False
            )
        else:
            self.setPresetPos(self.presetPos)

    @property
    def firstPerson(self):
        return self.camOffset.getY() == 0

    def _startMouseControlTasks(self):
        if self.mouseControl:
            properties = WindowProperties()
            properties.setMouseMode(WindowProperties.MAbsolute)
            base.win.requestProperties(properties)

            self._startMouseReadTask()
            self._startMouseUpdateTask()

    def _stopMouseControlTasks(self):
        properties = WindowProperties()
        properties.setMouseMode(WindowProperties.MAbsolute)
        try:
            base.win.requestProperties(properties)
        except Exception:
            pass

        self._stopMouseReadTask()
        self._stopMouseUpdateTask()

    def _startMouseReadTask(self):
        self._stopMouseReadTask()

        taskMgr.add(
            self._mouseReadTask,
            self.TopNodeName + '-MouseRead',
            priority=-29
        )

    def _mouseReadTask(self, task):
        if self.oobeEnabled() or not base.mouseWatcherNode.hasMouse():
            self.mouseDelta = (0, 0)
        else:
            winWidth = base.win.getXSize()
            winHeight = base.win.getYSize()
            mouseData = base.win.getPointer(0)
            mouseX = mouseData.getX()
            mouseY = mouseData.getY()

            if (
                mouseX < 0 or
                mouseY < 0 or
                mouseX >= winWidth or
                mouseY >= winHeight
            ):
                self.mouseDelta = (0, 0)
            else:
                self.mouseDelta = (
                    mouseX - self.lastMousePos[0],
                    mouseY - self.lastMousePos[1]
                )

                centerX = winWidth // 2
                centerY = winHeight // 2
                base.win.movePointer(0, centerX, centerY)
                self.lastMousePos = (centerX, centerY)

        return task.cont

    def _stopMouseReadTask(self):
        taskMgr.remove(self.TopNodeName + '-MouseRead')

    def _startMouseUpdateTask(self):
        self._stopMouseUpdateTask()

        taskMgr.add(
            self._avatarFacingTask,
            self.TopNodeName + '-AvatarFacing',
            priority=23
        )

        taskMgr.add(
            self._mouseUpdateTask,
            self.TopNodeName + '-MouseUpdate',
            priority=40
        )

    def _stopMouseUpdateTask(self):
        taskMgr.remove(self.TopNodeName + '-MouseUpdate')
        taskMgr.remove(self.TopNodeName + '-AvatarFacing')

    def start(self):
        if not self.isActive():
            self.request('Active')

    def stop(self):
        if self.isActive():
            self.request('Off')

            if self.subject and hasattr(self.subject, 'setSpeed'):
                self.subject.setSpeed(0, 0)

    def isActive(self):
        return self.state == 'Active'

    def oobeEnabled(self):
        return hasattr(base, 'oobeMode') and base.oobeMode
