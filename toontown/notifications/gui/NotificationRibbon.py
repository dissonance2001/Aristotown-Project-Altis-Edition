from __future__ import absolute_import
from direct.gui.DirectGui import DirectButton, DirectFrame
from direct.interval.IntervalGlobal import Func, LerpPosInterval, Sequence

from toontown.notifications.gui.ClashGuiUtils import kwargsToOptionDefs
from toontown.notifications.gui.windows.NotifWindowBase import NotifWindowBase


class NotificationRibbon(DirectButton):
    """Python 2 port of Clash's notification ribbon."""

    on_geom = NotifWindowBase.gui.find('**/notification_exclamation_on')
    off_geom = NotifWindowBase.gui.find('**/notification_exclamation_off')

    xpos = -0.19
    zpos_closed = -0.06
    zpos_opened = 0.0

    shadow_image_ratio = 139.0 / 306.0
    shadow_xscale = 0.54
    shadow_zscale = 0.54

    def __init__(self, parent, callback=None, **kw):
        self.callback = callback
        optiondefs = kwargsToOptionDefs(
            relief=None,
            pos=(self.xpos, 0, self.zpos_closed),
            scale=1.0,
            frameSize=(-0.075, 0.075, -0.38, 0),
            text='',
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_pos=(-0.00338, -0.44379),
            text_scale=0.07,
            image=(
                NotifWindowBase.gui.find('**/notification_flag'),
                NotifWindowBase.gui.find('**/notification_flag_press'),
                NotifWindowBase.gui.find('**/notification_flag_hover'),
            ),
            image_scale=(0.45 * (84.0 / 256.0), 1, 0.45),
            image_pos=(0, 0, -0.13),
            geom=self.off_geom,
            geom_scale=(0.15 * (37.0 / 91.0), 1, 0.15),
            geom_pos=(0, 0, -0.2),
            command=self.click,
        )
        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent, **kw)
        self.initialiseoptions(NotificationRibbon)
        self.setBin('sorted-gui-popup', 10)
        self.setDepthTest(False)
        self.setDepthWrite(False)
        self.setTextTo('Notifications')

        self.highlighted = False
        self.moveSeq = None
        self.loadingHidden = bool(getattr(loader, 'inBulkBlock', None))

        self.shadow = DirectFrame(
            parent=self,
            relief=None,
            image=NotifWindowBase.gui.find('**/notification_flag_shadow'),
            image_pos=(0.005, 0, -0.127),
            image_scale=(self.shadow_image_ratio * self.shadow_xscale,
                         1,
                         self.shadow_zscale),
            image_color=(1, 1, 1, 0.7),
        )
        self.shadow.setBin('sorted-gui-popup', 0)
        self.shadow.setDepthTest(False)
        self.shadow.setDepthWrite(False)

        if self.loadingHidden:
            DirectButton.hide(self)

    def setLoadingHidden(self, hiddenState):
        # The ribbon is independently guarded as well as being parented beneath
        # NotificationContainer, preventing it from flashing on a loading frame.
        self.loadingHidden = bool(hiddenState)
        if self.loadingHidden:
            self.endMovement()
            DirectButton.hide(self)
        else:
            DirectButton.show(self)

    def destroy(self):
        self.endMovement()
        DirectButton.destroy(self)

    def click(self):
        if self.callback is not None:
            self.callback()
        self.highlightOff()

    def highlightOn(self):
        if self.highlighted:
            return
        self.highlighted = True
        self['geom'] = self.on_geom

    def highlightOff(self):
        if not self.highlighted:
            return
        self.highlighted = False
        self['geom'] = self.off_geom

    def endMovement(self):
        if self.moveSeq:
            self.moveSeq.finish()
            self.moveSeq = None

    def moveToOpen(self, duration, blendType):
        self.endMovement()
        pos = (self.xpos, 0, self.zpos_opened)
        self.moveSeq = Sequence(
            Func(self.setTextTo),
            LerpPosInterval(self, duration=duration, pos=pos,
                            blendType='easeInOut'),
            Func(self.setTextTo, 'Close'),
        )
        self.moveSeq.start()

    def moveToClose(self, duration, blendType):
        self.endMovement()
        pos = (self.xpos, 0, self.zpos_closed)
        self.moveSeq = Sequence(
            Func(self.setTextTo),
            LerpPosInterval(self, duration=duration, pos=pos,
                            blendType='easeInOut'),
            Func(self.setTextTo, 'Notifications'),
        )
        self.moveSeq.start()

    def setTextTo(self, text=''):
        self['text'] = ('', text, text, '')
