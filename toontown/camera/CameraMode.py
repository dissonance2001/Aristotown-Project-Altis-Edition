from pandac.PandaModules import *
from direct.showbase import DirectObject
from direct.fsm.FSM import FSM
from direct.showbase.InputStateGlobal import inputState
from otp.otpbase import OTPGlobals


def getCameraSetting(name, default=None):
    """Read a Clash camera setting from the settings sources available in Altis."""
    try:
        return settings.get(name, default)
    except (NameError, AttributeError, TypeError, KeyError):
        pass

    settingsObj = getattr(base, 'settings', None)
    if settingsObj is not None:
        try:
            return settingsObj.get(name, default)
        except (AttributeError, TypeError, KeyError):
            pass

    return default


def _getCameraToggleLock():
    """Return the Clash camera toggle setting using Altis-compatible sources."""
    return bool(getCameraSetting('cam-toggle-lock', False))


class CameraMode(FSM, DirectObject.DirectObject):
    MouseControl = WindowProperties()
    MouseControl.setMouseMode(WindowProperties.MRelative)
    HideCursor = WindowProperties()
    HideCursor.setCursorHidden(1)
    # Altis ToonBase has no getCursorAndIcon(). Requesting only the
    # cursor-hidden property restores visibility without altering the icon.
    ShowCursor = WindowProperties()
    ShowCursor.setCursorHidden(0)
    ExitControl = WindowProperties()
    ExitControl.setMouseMode(WindowProperties.MAbsolute)

    def __init__(self):
        FSM.__init__(self, 'CameraMode')
        self.mouseControl = False
        self.mouseDelta = (0, 0)
        self.lastMousePos = (0, 0)
        self.origMousePos = (0, 0)
        self.request('Off')
        self.__inputEnabled = False
        self._hadMouse = False
        self.__cursorLock = 0.0
        self._rmbToken = inputState.watchWithModifiers('RMB', 'mouse3')

    def destroy(self):
        # OrbitCamera destroys its subject reference before calling this.
        # Active-state cleanup is performed by exitActive(), so do not call
        # the virtual disableInput()/disableMouseControl() chain here.
        if self._rmbToken:
            self._rmbToken.release()
            self._rmbToken = None
        self.ignoreAll()

    def getName(self):
        pass

    def start(self):
        if not self.isActive():
            self.request('Active')

    def stop(self):
        if self.isActive():
            self.request('Off')

    def isActive(self):
        return self.state == 'Active'

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    def enterActive(self):
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
        self.camFloorCollisionBroadcaster.setInPattern('on-floor')
        self.camFloorCollisionBroadcaster.setOutPattern('off-floor')
        self.camFloorCollisionBroadcaster.addCollider(self.ccRay2NodePath, self.ccRay2MoveNodePath)
        self.cTravOnFloor.addCollider(self.ccRay2NodePath, self.camFloorCollisionBroadcaster)
        self.enableInput()

    def exitActive(self):
        self.disableInput()
        del self.cTravOnFloor
        del self.ccRay2
        del self.ccRay2Node
        self.ccRay2NodePath.removeNode()
        del self.ccRay2NodePath
        self.ccRay2MoveNodePath.removeNode()
        del self.ccRay2MoveNodePath
        self.camFloorRayNode.removeNode()
        del self.camFloorRayNode

    def enableInput(self):
        self.__inputEnabled = True
        self.accept('InputState-RMB', self.enableMouseControl)
        if inputState.isSet('RMB') and not _getCameraToggleLock():
            self.enableMouseControl(True)

    def disableInput(self):
        self.__inputEnabled = False
        self._hadMouse = self.mouseControl
        # Pass the value that satisfies OrbitCamera.disableMouseControl's
        # toggle/hold condition so shutdown always releases mouse control.
        self.disableMouseControl(_getCameraToggleLock(), False)
        self.ignore('InputState-RMB')

    def isInputEnabled(self):
        return self.__inputEnabled

    def enableMouseControl(self, pressed):
        if pressed is False or getattr(self, 'ignoreRMB', False):
            return

        if hasattr(base, 'oobeMode') and base.oobeMode:
            return

        self.ignore('InputState-RMB')
        self.accept('InputState-RMB', self.disableMouseControl)

        self.mouseControl = True
        self.__cursorLock = 0.0
        mouseData = base.win.getPointer(0)
        self.origMousePos = (mouseData.getX(), mouseData.getY())
        if getattr(base, 'localAvatar', None) is not None:
            base.win.requestProperties(self.HideCursor)
            base.graphicsEngine.openWindows()

        base.win.movePointer(0, base.win.getXSize() / 2, base.win.getYSize() / 2)
        self.lastMousePos = (base.win.getXSize() / 2, base.win.getYSize() / 2)
        if self.getCurrentOrNextState() == 'Active':
            self._startMouseControlTasks()

    def disableMouseControl(self, pressed, disabledByMouse=True):
        if pressed != _getCameraToggleLock():
            return

        self.ignore('InputState-RMB')
        if self.__inputEnabled:
            self.accept('InputState-RMB', self.enableMouseControl)

        if hasattr(base, 'oobeMode') and base.oobeMode:
            return

        if self.mouseControl:
            self.mouseControl = False
            self._stopMouseControlTasks()
            if getattr(base, 'localAvatar', None) is not None:
                base.win.requestProperties(self.ShowCursor)
                base.graphicsEngine.openWindows()

            base.win.movePointer(0, int(self.origMousePos[0]), int(self.origMousePos[1]))

    def _startMouseControlTasks(self):
        if self.mouseControl:
            base.win.requestProperties(self.MouseControl)
            self._startMouseReadTask()
            self._startMouseUpdateTask()

    def _stopMouseControlTasks(self):
        base.win.requestProperties(self.ExitControl)
        self._stopMouseReadTask()
        self._stopMouseUpdateTask()

    def _startMouseReadTask(self):
        self._stopMouseReadTask()
        taskMgr.add(self._mouseReadTask, '%s-MouseRead' % self._getTopNodeName(), priority=-29)

    def _mouseReadTask(self, task):
        winSize = (base.win.getXSize(), base.win.getYSize())
        if (hasattr(base, 'oobeMode') and base.oobeMode) or not base.mouseWatcherNode.hasMouse():
            self.mouseDelta = (0, 0)
        elif self.__cursorLock <= 0.05:
            self.mouseDelta = (0, 0)
            self.__cursorLock = task.time
        else:
            mouseData = base.win.getPointer(0)
            self.mouseDelta = (
                mouseData.getX() - self.lastMousePos[0],
                mouseData.getY() - self.lastMousePos[1]
            )

        base.win.movePointer(0, winSize[0] / 2, winSize[1] / 2)
        mouseData = base.win.getPointer(0)
        self.lastMousePos = (mouseData.getX(), mouseData.getY())
        return task.cont

    def _stopMouseReadTask(self):
        taskMgr.remove('%s-MouseRead' % self._getTopNodeName())

    def _startMouseUpdateTask(self):
        self._stopMouseUpdateTask()
        taskMgr.add(self._avatarFacingTask, '%s-AvatarFacing' % self._getTopNodeName(), priority=23)
        taskMgr.add(self._mouseUpdateTask, '%s-MouseUpdate' % self._getTopNodeName(), priority=40)

    def _avatarFacingTask(self, task):
        return task.cont

    def _mouseUpdateTask(self, task):
        return task.cont

    def _stopMouseUpdateTask(self):
        taskMgr.remove('%s-MouseUpdate' % self._getTopNodeName())
        taskMgr.remove('%s-AvatarFacing' % self._getTopNodeName())

    def avFaceCamera(self):
        pass
