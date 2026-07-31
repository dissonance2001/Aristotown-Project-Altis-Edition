import math
import time

from toontown.pgui.DirectGui import DirectFrame, DirectButton, DirectScrolledFrame
from toontown.pgui import DirectGuiGlobals as DGG
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import Point3, TextNode, PGButton, MouseButton

from toontown.stickers import StickerGlobals


# Project Altis's older DirectGuiGlobals does not define WHEEL_UP/WHEEL_DOWN.
# Build the native DirectGUI event prefixes ourselves, with compatibility for
# both the old Python 2 Panda API and Panda3D's newer snake_case API.
try:
    _wheelUpButton = MouseButton.wheelUp()
    _wheelDownButton = MouseButton.wheelDown()
except AttributeError:
    _wheelUpButton = MouseButton.wheel_up()
    _wheelDownButton = MouseButton.wheel_down()

GUI_WHEEL_UP = PGButton.getPressPrefix() + _wheelUpButton.getName() + '-'
GUI_WHEEL_DOWN = PGButton.getPressPrefix() + _wheelDownButton.getName() + '-'


class StickerMenu(DirectFrame, DirectObject):
    """Corporate Clash-style sticker picker adapted to Altis/Python 2."""

    BUTTONS_PER_ROW = 4
    CLIENT_COOLDOWN = 2.0

    # Each physical wheel notch adds one row to the target.  The canvas eases
    # toward that target continuously, so rapid wheel input accumulates rather
    # than cancelling or restarting an interval.
    SMOOTH_SCROLL_RESPONSE = 28.0
    SMOOTH_SCROLL_EPSILON = 0.00025
    IMMEDIATE_SCROLL_FRACTION = 0.30

    # Accurate local-space bounds of the visible green panel.  This is used
    # only to decide whether the orbital camera should own the wheel; actual
    # sticker scrolling uses native DirectGUI wheel bindings on every region.
    PANEL_BOUNDS = (-0.53, 0.53, -0.52, 0.52)

    # Clash does not rely on a special model node for menu placement. Its
    # GUIPositionManager stacks this menu below the active chat window.
    BASE_POS = (0.32, 0, -0.28)
    COMPACT_CHAT_DOWN = 0.154
    OPEN_CHAT_DOWN = 0.55

    # Corporate Clash's four-stickers-per-row layout.
    BUTTON_SCALE = 0.25 * 0.833
    ROW_EDGE = 0.31
    ROW_DISTANCE = -0.26 * 0.833
    ROW_PADDING = -0.15 * 0.833

    def __init__(self, parent, chatAssets):
        DirectFrame.__init__(
            self,
            parent=parent,
            relief=None,
            pos=self.BASE_POS,
            scale=0.60,
            sortOrder=1200,
        )
        DirectObject.__init__(self)

        try:
            self.setBin('sorted-gui-popup', 1201)
        except:
            pass

        self.chatLog = parent
        self.isOpen = False
        self.lastSendTime = 0.0
        self.buttons = []
        self.panelNode = None
        self.wheelCaptureFrames = []
        self.wheelWidgets = []

        self.scrollTaskName = 'StickerMenuSmoothScroll-%s' % id(self)
        self.hoverTaskName = 'StickerMenuWheelOwner-%s' % id(self)
        self.scrollTaskActive = False
        self.hoverTaskActive = False
        self.scrollTarget = 1.0
        self.scrollCurrent = 1.0
        self.scrollTopValue = 1.0
        self.scrollBottomValue = 0.0
        self.scrollStep = 0.12

        self._suppressedOrbitalCamera = None
        self._orbitalWheelWasEnabled = False
        self._chatWheelWasEnabled = False

        # ChatLog already loaded the real Clash chat_panel.bam and passes it
        # here. Reuse that exact model instead of inventing a second BAM path.
        panel = chatAssets.find('**/Chat-Stickers-Menu')
        if not panel.isEmpty():
            self.panelNode = panel.copyTo(self)
            self.panelNode.setScale(1.0, 1.0, 414.0 / 436.0)
            try:
                self.panelNode.setBin('fixed', -20)
            except:
                pass
        else:
            self.panelNode = DirectFrame(
                parent=self,
                relief=DGG.FLAT,
                frameColor=(0.15, 0.56, 0.29, 0.98),
                frameSize=(-0.50, 0.50, -0.50, 0.50),
                sortOrder=-20,
            )

        # Do not place one mouse-active DirectFrame across the whole menu.
        # That invisible region can win Panda's mouse-region sort and swallow
        # mouse1 before the sticker DirectButtons receive it. The scroll frame
        # and every sticker button are bound separately below; these four thin
        # regions cover only the outer panel border, so scrolling still works
        # anywhere without blocking sticker clicks.
        left, right, bottom, top = self.PANEL_BOUNDS
        scrollLeft = -0.475
        scrollRight = 0.478
        scrollBottom = -0.44
        scrollTop = 0.44
        borderRegions = (
            (left, scrollLeft, bottom, top),
            (scrollRight, right, bottom, top),
            (scrollLeft, scrollRight, scrollTop, top),
            (scrollLeft, scrollRight, bottom, scrollBottom),
        )
        for frameSize in borderRegions:
            capture = DirectFrame(
                parent=self,
                relief=DGG.FLAT,
                frameColor=(0, 0, 0, 0),
                frameSize=frameSize,
                state=DGG.NORMAL,
                sortOrder=-100,
            )
            self._bindWheelWidget(capture)
            self.wheelCaptureFrames.append(capture)

        self.stickerModel = loader.loadModel(
            'phase_3.5/models/gui/stickers')

        totalRows = int(math.ceil(
            float(len(StickerGlobals.STICKERS)) / self.BUTTONS_PER_ROW))
        lastRowZ = self.ROW_PADDING + ((totalRows - 1) * self.ROW_DISTANCE)
        canvasBottom = lastRowZ - 0.16

        scrollbar = chatAssets.find('**/Scrollbar')
        scrollblock = chatAssets.find('**/Scrollblock')

        scrollOptions = dict(
            parent=self,
            relief=None,
            state=DGG.NORMAL,
            pos=(-0.055, 0, 0),
            frameSize=(-0.42, 0.42, -0.44, 0.44),
            canvasSize=(-0.42, 0.42, canvasBottom, 0.02),
            autoHideScrollBars=False,
            manageScrollBars=False,
            verticalScroll_pos=(0.483, 0, 0),
            verticalScroll_scale=(1, 1, 1),
            verticalScroll_frameSize=(-0.05, 0.05, -0.43, 0.43),
            verticalScroll_relief=None,
            verticalScroll_resizeThumb=0,
            verticalScroll_scrollSize=0.16,
            verticalScroll_pageSize=0.80,
            verticalScroll_thumb_relief=None,
            sortOrder=10,
        )
        if not scrollbar.isEmpty():
            scrollOptions['verticalScroll_geom'] = scrollbar
            scrollOptions['verticalScroll_geom_scale'] = (0.05, 1, 0.86)
        if not scrollblock.isEmpty():
            scrollOptions['verticalScroll_thumb_image'] = scrollblock
            scrollOptions['verticalScroll_thumb_image_scale'] = (0.12, 1, 0.156)
            scrollOptions['verticalScroll_thumb_image_color'] = (1, 1, 1, 1)

        self.scroll = DirectScrolledFrame(**scrollOptions)
        self.scroll.horizontalScroll.hide()
        try:
            self.scroll.verticalScroll.incButton.destroy()
            self.scroll.verticalScroll.decButton.destroy()
        except:
            pass

        # One wheel notch equals one authored sticker-row distance, converted
        # to the scrollbar's normalized 0..1 travel range.
        frameHeight = 0.44 - (-0.44)
        canvasHeight = 0.02 - canvasBottom
        scrollableHeight = max(0.001, canvasHeight - frameHeight)
        self.scrollStep = min(0.25, abs(self.ROW_DISTANCE) / scrollableHeight)

        try:
            self.scrollCurrent = self.scrollTopValue
            self.scrollTarget = self.scrollTopValue
            self._setScrollValue(self.scrollTopValue)
            self.scroll.verticalScroll.thumb.show()
        except:
            pass

        # Bind every actual GUI surface.  This is the important difference
        # from the previous global-wheel approach: Panda now emits one native
        # widget event for every physical wheel notch under the cursor.
        self._bindWheelWidget(self.scroll)
        self._bindWheelWidget(self.scroll.verticalScroll)
        self._bindWheelWidget(self.scroll.verticalScroll.thumb)

        self.nameLabel = DirectFrame(
            parent=self,
            relief=None,
            state=DGG.NORMAL,
            pos=(-0.02, 0, -0.465),
            text='',
            text_scale=0.045,
            text_align=TextNode.ACenter,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            sortOrder=20,
        )
        self._bindWheelWidget(self.nameLabel)

        self._buildButtons()
        self.hideMenu()

    def _bindWheelWidget(self, widget):
        if widget is None:
            return
        try:
            # Altis/Panda reports these native DirectGUI wheel events with
            # the opposite visual direction from the generic messenger events.
            # Map wheel-down toward the bottom of the list and wheel-up toward
            # the top.
            widget.bind(GUI_WHEEL_UP, self._handlePanelWheel, [1])
            widget.bind(GUI_WHEEL_DOWN, self._handlePanelWheel, [-1])
            self.wheelWidgets.append(widget)
        except:
            pass

    def _buildButtons(self):
        totalDistance = self.ROW_EDGE * 2.0
        for index, data in enumerate(StickerGlobals.STICKERS):
            stickerId, name, nodePath, unusedScale3d, scale2d = data
            row = index // self.BUTTONS_PER_ROW
            column = index % self.BUTTONS_PER_ROW
            image = self.stickerModel.find(nodePath)
            if image.isEmpty():
                continue

            xPos = -self.ROW_EDGE + (
                totalDistance * (float(column) / (self.BUTTONS_PER_ROW - 1)))
            zPos = self.ROW_PADDING + (row * self.ROW_DISTANCE)

            button = DirectButton(
                parent=self.scroll.getCanvas(),
                relief=None,
                pos=(xPos, 0, zPos),
                scale=self.BUTTON_SCALE,
                image=image,
                image_scale=scale2d,
                command=self._selectSticker,
                extraArgs=[stickerId],
                pressEffect=0,
            )
            try:
                button.resetFrameSize()
            except:
                pass
            button.bind(DGG.ENTER, self._setHoverName, [name])
            button.bind(DGG.EXIT, self._setHoverName, [''])
            self._bindWheelWidget(button)
            self.buttons.append(button)

    def _setHoverName(self, name, event=None):
        self.nameLabel['text'] = name

    def _selectSticker(self, stickerId):
        if time.time() - self.lastSendTime < self.CLIENT_COOLDOWN:
            return
        avatar = getattr(base, 'localAvatar', None)
        if not avatar or not hasattr(avatar, 'd_requestSticker'):
            return
        self.lastSendTime = time.time()
        avatar.d_requestSticker(stickerId)
        self.hideMenu()

    def _getScrollValue(self):
        try:
            return float(self.scroll.verticalScroll.getValue())
        except:
            try:
                return float(self.scroll.verticalScroll['value'])
            except:
                return self.scrollTarget

    def _setScrollValue(self, value):
        value = max(self.scrollBottomValue, min(self.scrollTopValue, value))
        try:
            # Set through the public scrollbar API so PGScrollFrame receives
            # the linked slider adjustment and moves its canvas immediately.
            self.scroll.verticalScroll.setValue(value)
        except:
            try:
                self.scroll.verticalScroll['value'] = value
            except:
                pass

    def _stopScrollTask(self):
        if self.scrollTaskActive:
            try:
                taskMgr.remove(self.scrollTaskName)
            except:
                pass
        self.scrollTaskActive = False

    def _startScrollTask(self):
        if self.scrollTaskActive:
            return
        self.scrollTaskActive = True
        taskMgr.add(self._smoothScrollTask, self.scrollTaskName)

    def _smoothScrollTask(self, task):
        currentValue = self._getScrollValue()
        difference = self.scrollTarget - currentValue

        if abs(difference) <= self.SMOOTH_SCROLL_EPSILON:
            self._setScrollValue(self.scrollTarget)
            self.scrollCurrent = self.scrollTarget
            self.scrollTaskActive = False
            return task.done

        try:
            deltaTime = globalClock.getDt()
        except:
            deltaTime = 1.0 / 60.0
        deltaTime = max(0.0, min(0.10, float(deltaTime)))

        blend = 1.0 - math.exp(-self.SMOOTH_SCROLL_RESPONSE * deltaTime)
        nextValue = currentValue + (difference * blend)
        self._setScrollValue(nextValue)
        self.scrollCurrent = nextValue
        return task.cont

    def _handlePanelWheel(self, direction, event=None):
        if not self.isOpen:
            return

        # Ensure camera ownership changes before the following frame even if
        # the cursor entered and scrolled within the same render frame.
        self._suppressOrbitalWheel()
        self._scrollMenu(direction)

    def _scrollMenu(self, direction):
        currentValue = self._getScrollValue()

        # Continue from a manually dragged thumb when no easing is active.
        if not self.scrollTaskActive:
            self.scrollTarget = currentValue

        # On this vertical scrollbar, 1.0 is the top and 0.0 is the
        # bottom. Native Altis DirectGUI wheel events are remapped in
        # _bindWheelWidget so wheel-down decreases this value and wheel-up
        # increases it.
        requestedTarget = self.scrollTarget - (float(direction) * self.scrollStep)
        requestedTarget = max(
            self.scrollBottomValue,
            min(self.scrollTopValue, requestedTarget),
        )

        if abs(requestedTarget - self.scrollTarget) <= 0.000001:
            return

        oldTarget = self.scrollTarget
        self.scrollTarget = requestedTarget

        # Move a fixed fraction of this exact wheel notch immediately.  This
        # guarantees visible feedback for every notch, while the remainder is
        # completed smoothly by the persistent easing task.
        notchDistance = self.scrollTarget - oldTarget
        immediateValue = currentValue + (
            notchDistance * self.IMMEDIATE_SCROLL_FRACTION)
        if notchDistance < 0.0:
            immediateValue = max(immediateValue, self.scrollTarget)
        else:
            immediateValue = min(immediateValue, self.scrollTarget)
        self._setScrollValue(immediateValue)
        self.scrollCurrent = immediateValue

        self._startScrollTask()
        try:
            messenger.send('wakeup')
        except:
            pass

    def _isAccepting(self, directObject, eventName, fallback=False):
        try:
            return bool(directObject.isAccepting(eventName))
        except:
            return fallback

    def _suppressChatWheel(self):
        self._chatWheelWasEnabled = False
        try:
            chatOpen = not self.chatLog.isHidden
            self._chatWheelWasEnabled = self._isAccepting(
                self.chatLog, 'wheel_up', chatOpen)
            if self._chatWheelWasEnabled:
                self.chatLog.ignore('wheel_up')
                self.chatLog.ignore('wheel_down')
        except:
            self._chatWheelWasEnabled = False

    def _restoreChatWheel(self):
        if self._chatWheelWasEnabled:
            try:
                if not self.chatLog.isHidden:
                    self.chatLog.accept(
                        'wheel_up', self.chatLog._scrollCurrent, [-1])
                    self.chatLog.accept(
                        'wheel_down', self.chatLog._scrollCurrent, [1])
            except:
                pass
        self._chatWheelWasEnabled = False

    def _getOrbitalCamera(self):
        try:
            avatar = getattr(base, 'localAvatar', None)
            return getattr(avatar, 'orbitalCamera', None)
        except:
            return None

    def _suppressOrbitalWheel(self):
        if self._suppressedOrbitalCamera is not None:
            return

        orbitalCamera = self._getOrbitalCamera()
        if orbitalCamera is None:
            return

        try:
            cameraActive = orbitalCamera.isActive()
        except:
            cameraActive = True

        wheelEnabled = self._isAccepting(
            orbitalCamera, 'wheel_up', cameraActive)
        if not wheelEnabled:
            return

        try:
            # Avoid OrbitalCamera.ignoreWheel(), which resets camera distance
            # in this Altis port. Remove only its two wheel listeners.
            orbitalCamera.ignore('wheel_up')
            orbitalCamera.ignore('wheel_down')
            self._suppressedOrbitalCamera = orbitalCamera
            self._orbitalWheelWasEnabled = True
        except:
            self._suppressedOrbitalCamera = None
            self._orbitalWheelWasEnabled = False

    def _restoreOrbitalWheel(self):
        orbitalCamera = self._suppressedOrbitalCamera
        self._suppressedOrbitalCamera = None

        if orbitalCamera is not None and self._orbitalWheelWasEnabled:
            try:
                if orbitalCamera.isActive():
                    orbitalCamera.accept(
                        'wheel_up', orbitalCamera._handleWheelUp)
                    orbitalCamera.accept(
                        'wheel_down', orbitalCamera._handleWheelDown)
            except:
                pass
        self._orbitalWheelWasEnabled = False

    def _isMouseOverPanel(self):
        try:
            watcher = base.mouseWatcherNode
            if not watcher.hasMouse():
                return False

            mouse = watcher.getMouse()
            localPoint = self.getRelativePoint(
                render2d, Point3(mouse.getX(), 0, mouse.getY()))
            left, right, bottom, top = self.PANEL_BOUNDS
            return (
                left <= localPoint.getX() <= right and
                bottom <= localPoint.getZ() <= top
            )
        except:
            return False

    def _startHoverTask(self):
        if self.hoverTaskActive:
            return
        self.hoverTaskActive = True
        taskMgr.add(self._wheelOwnerTask, self.hoverTaskName)

    def _stopHoverTask(self):
        if self.hoverTaskActive:
            try:
                taskMgr.remove(self.hoverTaskName)
            except:
                pass
        self.hoverTaskActive = False

    def _wheelOwnerTask(self, task):
        if not self.isOpen:
            self.hoverTaskActive = False
            return task.done

        if self._isMouseOverPanel():
            self._suppressOrbitalWheel()
        else:
            self._restoreOrbitalWheel()
        return task.cont

    def _updateMenuPosition(self):
        chatDown = self.COMPACT_CHAT_DOWN
        try:
            if not self.chatLog.isHidden:
                chatDown = self.OPEN_CHAT_DOWN
        except:
            pass

        self.setPos(
            self.BASE_POS[0],
            self.BASE_POS[1],
            self.BASE_POS[2] - chatDown,
        )

    def toggleMenu(self):
        if self.isOpen:
            self.hideMenu()
        else:
            self.showMenu()

    def showMenu(self):
        self._updateMenuPosition()
        self.isOpen = True
        self.show()
        self._stopScrollTask()
        try:
            self._setScrollValue(self.scrollTopValue)
            self.scrollCurrent = self._getScrollValue()
            self.scrollTarget = self.scrollCurrent
        except:
            self.scrollCurrent = self.scrollTopValue
            self.scrollTarget = self.scrollTopValue

        # Chat history remains disabled for the entire time the sticker menu
        # is open. Camera zoom remains active outside the panel and is disabled
        # only while the cursor is within the visible green panel.
        self._suppressChatWheel()
        self._startHoverTask()
        self.accept('escape', self.hideMenu)

    def hideMenu(self):
        self.isOpen = False
        self.ignore('escape')
        self._stopScrollTask()
        self._stopHoverTask()
        self._restoreOrbitalWheel()
        self._restoreChatWheel()
        if getattr(self, 'nameLabel', None):
            self.nameLabel['text'] = ''
        self.hide()

    def destroy(self):
        self._stopScrollTask()
        self._stopHoverTask()
        self._restoreOrbitalWheel()
        self._restoreChatWheel()
        self.ignoreAll()

        for button in self.buttons:
            try:
                button.destroy()
            except:
                pass
        self.buttons = []
        self.wheelWidgets = []

        if getattr(self, 'nameLabel', None):
            try:
                self.nameLabel.destroy()
            except:
                pass
            self.nameLabel = None

        if getattr(self, 'scroll', None):
            try:
                self.scroll.destroy()
            except:
                pass
            self.scroll = None

        for capture in getattr(self, 'wheelCaptureFrames', []):
            try:
                capture.destroy()
            except:
                pass
        self.wheelCaptureFrames = []

        if getattr(self, 'panelNode', None):
            try:
                self.panelNode.removeNode()
            except:
                try:
                    self.panelNode.destroy()
                except:
                    pass
            self.panelNode = None

        if getattr(self, 'stickerModel', None):
            try:
                self.stickerModel.removeNode()
            except:
                pass
            self.stickerModel = None

        DirectFrame.destroy(self)
