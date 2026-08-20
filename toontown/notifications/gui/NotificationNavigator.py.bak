from direct.gui.DirectGui import DirectButton, DirectFrame

from toontown.notifications.gui.ClashGuiUtils import kwargsToOptionDefs
from toontown.notifications.gui.windows.NotifWindowBase import NotifWindowBase


class NotificationNavigator(DirectFrame):
    """Python 2 port of Clash's notification navigator."""

    def __init__(self, parent, callback=None, **kw):
        optiondefs = kwargsToOptionDefs(
            relief=None,
            image=NotifWindowBase.gui.find('**/notification_middlebutton'),
            image_pos=(0, 0, -0.5),
            image_scale=(3.25, 1, 1),
            text='None',
            text_pos=(-0.03, -0.68),
            text_scale=0.66,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0.039, 0.388, 0.604, 1.0),
            pos=(0, 0, 0.018),
        )
        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, parent, **kw)
        self.initialiseoptions(NotificationNavigator)
        self.setBin('sorted-gui-popup', 0)
        self.setDepthTest(False)
        self.setDepthWrite(False)

        self.callback = callback
        self.index = 0
        self.notifList = []

        self.button_left = DirectButton(
            self,
            pos=(-1.95, 0, 0),
            relief=None,
            frameSize=(-0.5, 0.5, -1.1, -0.1),
            image=(
                NotifWindowBase.gui.find('**/notification_button'),
                NotifWindowBase.gui.find('**/notification_button_press'),
                NotifWindowBase.gui.find('**/notification_button_hover'),
            ),
            image_pos=(0.05, 0, -0.45),
            image_scale=(1, 1, 1),
            command=self.change,
            extraArgs=[-1],
        )
        self.button_right = DirectButton(
            self,
            pos=(1.95, 0, 0),
            relief=None,
            frameSize=(-0.5, 0.5, -1.1, -0.1),
            image=(
                NotifWindowBase.gui.find('**/notification_button'),
                NotifWindowBase.gui.find('**/notification_button_press'),
                NotifWindowBase.gui.find('**/notification_button_hover'),
            ),
            image_pos=(-0.05, 0, -0.45),
            image_scale=(-1, 1, 1),
            command=self.change,
            extraArgs=[1],
        )
        for button in (self.button_left, self.button_right):
            button.setBin('sorted-gui-popup', 10)
            button.setDepthTest(False)
            button.setDepthWrite(False)

    def change(self, direction):
        if self.callback is not None:
            self.callback(direction)

    def enterShow(self, instant=False):
        return

    def exitShow(self, instant=False):
        return

    def updateIndex(self, index):
        self.index = index
        self.updateText()

    def updateNotifList(self, notifList):
        self.notifList = notifList
        self.updateText()

    def updateText(self):
        if not self.notifList:
            self.setText('None')
        else:
            self.setText('%s / %s' %
                         (self.index + 1, len(self.notifList)))
