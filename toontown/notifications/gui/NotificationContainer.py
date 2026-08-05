from pandac.PandaModules import TextNode
from direct.fsm.FSM import FSM
from direct.gui.DirectGui import DirectButton, DirectFrame
from direct.gui.DirectGuiBase import DirectGuiWidget
from direct.interval.IntervalGlobal import LerpPosInterval, Parallel

from toontown.notifications.gui.ClashGuiUtils import kwargsToOptionDefs
from toontown.notifications.gui.NotificationNavigator import NotificationNavigator
from toontown.notifications.gui.NotificationRibbon import NotificationRibbon
from toontown.notifications.gui.windows.NotifWindowChoice import NotifWindowChoice
from toontown.notifications.gui.windows.NotifWindowEmpty import NotifWindowEmpty
from toontown.notifications.gui.windows.NotifWindowFriendRequest import NotifWindowFriendRequest
from toontown.notifications.gui.windows.NotifWindowGenericText import NotifWindowGenericText


class NotificationContainer(DirectFrame, FSM):
    """Corporate Clash's notification container adapted to Altis/Python 2.

    Clash initially creates a temporary ``scale_node`` at Z +0.175, but its
    GUIPositionManager immediately reparents the actual container onto a
    managed top-right node.  Therefore the final on-screen hierarchy has no
    +0.175 vertical offset.  This class reproduces that final hierarchy.
    """

    sizeMult = 0.621
    state_open = 'Open'
    state_close = 'Close'

    # Final TOP_RIGHT placement produced by Clash's GUIPositionManager:
    # SocialPanelButtons left margin: 2.5 * 0.1425 = 0.35625
    # Notification right margin:      0.05 * 0.621 = 0.03105
    managed_anchor_pos = (-0.3873, 0, 0)

    close_empty_pos = (0, 0, 0.4)
    move_duration = 0.17
    notif_window_node_pos = (0, 0, 0)
    ribbon_pos = (-0.1, 0, 0)

    def __init__(self, manager, parent=None, **kw):
        if parent is None:
            parent = base.a2dTopRight
        FSM.__init__(self, 'notification-container')
        self.manager = manager

        # This is the node Clash's GUIPositionManager leaves the container on.
        # Do not put the panel under Clash's temporary +0.175 scale node.
        self.managed_node = DirectGuiWidget(
            parent,
            pos=self.managed_anchor_pos,
            relief=None,
        )

        optiondefs = kwargsToOptionDefs(
            relief=None,
            frameSize=(-1, 0, -0.3, 0),
            scale=self.sizeMult,
        )
        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, self.managed_node, **kw)
        self.initialiseoptions(NotificationContainer)

        self.navigator = None
        self.ribbon = None
        self.button_trash = None
        self.node_windowNode = None
        self.baseWindow = None

        self.index = 0
        self.notificationCount = 0
        self.notificationWindows = []
        self.notifications = []
        self.moveSeq = None

        self.load()
        self.request(self.state_close)
        self.setBin('sorted-gui-popup', 900)
        self.setDepthTest(False)
        self.setDepthWrite(False)

    def load(self):
        self.navigator = NotificationNavigator(
            self,
            callback=self.changeIndex,
            scale=0.13,
            pos=(-0.66, 0, 0.018),
        )
        self.navigator.exitShow(instant=True)

        self.ribbon = NotificationRibbon(
            self,
            callback=self.ribbonClicked,
            pos=self.ribbon_pos,
        )

        self.node_windowNode = DirectGuiWidget(
            self,
            relief=None,
            pos=self.notif_window_node_pos,
        )
        self.baseWindow = NotifWindowEmpty(self.node_windowNode)
        self.baseWindow.hide()

        self.setPos(self.close_pos)
        self.updateWindowVisibility()

    def show(self):
        DirectFrame.show(self)

    def hide(self):
        DirectFrame.hide(self)
        if self.state != self.state_close:
            self.request(self.state_close)
        if self.moveSeq:
            self.moveSeq.finish()
            self.moveSeq = None
        if self.ribbon:
            self.ribbon.endMovement()
        self.updateWindowVisibility()

    def destroy(self):
        if self.moveSeq:
            self.moveSeq.finish()
            self.moveSeq = None
        if self.ribbon:
            self.ribbon.endMovement()

        for window in self.notificationWindows:
            window.destroy()
        self.notificationWindows = []

        if self.button_trash:
            self.button_trash.destroy()
            self.button_trash = None
        if self.baseWindow:
            self.baseWindow.destroy()
            self.baseWindow = None
        if self.navigator:
            self.navigator.destroy()
            self.navigator = None
        if self.ribbon:
            self.ribbon.destroy()
            self.ribbon = None
        if self.node_windowNode:
            self.node_windowNode.destroy()
            self.node_windowNode = None

        DirectFrame.destroy(self)
        if self.managed_node:
            self.managed_node.destroy()
            self.managed_node = None

    def _makeWindow(self, data):
        if data.getNotificationType() == 'friend-request':
            return NotifWindowFriendRequest(
                self.node_windowNode,
                data,
                onResolved=self._choiceResolved,
            )
        if data.hasChoices():
            return NotifWindowChoice(
                self.node_windowNode,
                data,
                onResolved=self._choiceResolved,
            )
        return NotifWindowGenericText(self.node_windowNode, data)

    def _choiceResolved(self, data):
        self.manager.removeNotification(data, invokeDismiss=False)

    def setNotifications(self, notifications, newNotification=False,
                         playSound=True):
        self.notifications = list(notifications)

        for window in self.notificationWindows:
            window.destroy()
        self.notificationWindows = []

        for data in self.notifications:
            window = self._makeWindow(data)
            window.hide()
            self.notificationWindows.append(window)

        self.notificationCount = len(self.notificationWindows)
        if newNotification:
            self.index = 0
        elif self.index >= self.notificationCount:
            self.index = max(0, self.notificationCount - 1)

        self.navigator.updateNotifList(self.notifications)
        self.updateWindowVisibility()

        if newNotification and self.notificationWindows:
            if not self.isHidden():
                self.ribbon.highlightOn()
                self.notificationWindows[0].onInitialDrop()
                if self.state == self.state_close:
                    self.request(self.state_open)
                if playSound:
                    self.notificationWindows[0].playSfx()
        elif not self.notificationWindows and self.state == self.state_open:
            self.request(self.state_close)

    def ribbonClicked(self):
        if self.state == self.state_open:
            self.request(self.state_close)
        else:
            self.request(self.state_open)

    def enterOpen(self):
        # Clash always begins with the newest notification.
        self.index = 0
        self.navigator.updateIndex(self.index)
        self.updateWindowVisibility()
        self.moveContainerIntoOpenPosition()
        self.navigator.enterShow()

    def exitOpen(self):
        pass

    def enterClose(self):
        if self.moveSeq:
            self.moveSeq.pause()
            self.moveSeq = None

        if self.notificationWindows:
            duration = self.move_duration
        else:
            duration = self.move_duration * 2
        blendType = 'easeIn'

        self.moveSeq = LerpPosInterval(
            self,
            duration=duration,
            pos=self.close_pos,
            blendType=blendType,
        )
        self.moveSeq.start()
        self.ribbon.moveToClose(duration, blendType)
        self.navigator.exitShow()
        self.ribbon.highlightOff()

        if self.notificationWindows:
            self.notificationWindows[self.index].setActiveState(False)

    def exitClose(self):
        pass

    def moveContainerIntoOpenPosition(self):
        if self.moveSeq:
            self.moveSeq.pause()
            self.moveSeq = None

        # Clash corrects the local Z translation by the panel scale.
        pos = list(self.open_pos)
        pos[2] *= self.sizeMult

        intervals = [
            LerpPosInterval(
                self,
                duration=self.move_duration,
                pos=tuple(pos),
                blendType='easeIn',
            )
        ]
        if self.button_trash:
            intervals.append(
                LerpPosInterval(
                    self.button_trash,
                    duration=self.move_duration,
                    pos=self.dismiss_pos,
                    blendType='easeIn',
                )
            )

        self.moveSeq = Parallel(*intervals)
        self.moveSeq.start()
        self.ribbon.moveToOpen(self.move_duration, 'easeIn')

    def getOpenPanelHeight(self):
        window = self.baseWindow
        if self.notificationWindows:
            window = self.notificationWindows[self.index]
        return window.getPanelHeight()

    @property
    def dismiss_pos(self):
        return (-0.031, 0,
                max(0.38, self.getOpenPanelHeight() - 0.07))

    @property
    def open_pos(self):
        return (0, 0, -self.getOpenPanelHeight())

    @property
    def close_pos(self):
        if not self.notificationWindows:
            return self.close_empty_pos
        return (0, 0, 0.08)

    def changeIndex(self, direction):
        if not self.notificationWindows:
            return
        self.index += direction
        if self.index == -1:
            self.index = len(self.notificationWindows) - 1
        elif self.index == len(self.notificationWindows):
            self.index = 0
        self.updateWindowVisibility()

    def updateWindowVisibility(self):
        for window in self.notificationWindows:
            window.hide()

        self.index = max(0, min(self.index,
                                len(self.notificationWindows) - 1))
        self.navigator.updateIndex(self.index)
        self.makeTrashCanButton()

        if self.notificationWindows:
            self.notificationWindows[self.index].show()
            self.notificationWindows[self.index].setActiveState(True)
            self.baseWindow.hide()
            if self.button_trash:
                self.button_trash.show()
        else:
            self.baseWindow.show()
            if self.button_trash:
                self.button_trash.hide()

        if self.state == self.state_open:
            self.moveContainerIntoOpenPosition()

    def makeTrashCanButton(self):
        startPos = self.dismiss_pos
        if self.button_trash:
            startPos = self.button_trash.getPos()
            self.button_trash.destroy()
            self.button_trash = None

        buttonGui = loader.loadModel(
            'phase_3/models/gui/ttcc_gui_generalButtons')
        self.button_trash = DirectButton(
            self,
            pos=startPos,
            scale=0.21,
            relief=None,
            text=('', 'Dismiss', 'Dismiss', ''),
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0.5),
            text_shadow=(0, 0, 0, 1),
            text_align=TextNode.ARight,
            text_pos=(-0.348, -0.105),
            text_scale=0.285,
            image=(
                buttonGui.find('**/CloseBtn_UP'),
                buttonGui.find('**/CloseBtn_DN'),
                buttonGui.find('**/CloseBtn_Rllvr'),
                buttonGui.find('**/CloseBtn_UP'),
            ),
            image_scale=6.6,
            command=self.onDelete,
        )
        self.button_trash.setBin('sorted-gui-popup', 904)
        self.button_trash.setDepthTest(False)
        self.button_trash.setDepthWrite(False)
        buttonGui.removeNode()

    def onDelete(self):
        if not self.notificationWindows:
            return
        self.notificationWindows[self.index].onTrash()
        self.manager.removeNotificationAt(self.index, invokeDismiss=False)
