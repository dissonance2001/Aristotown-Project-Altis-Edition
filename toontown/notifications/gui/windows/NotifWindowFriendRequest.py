from direct.gui.DirectGui import DirectButton

from toontown.notifications.gui.ClashGuiUtils import kwargsToOptionDefs
from toontown.notifications.gui.windows.NotifWindowBase import NotifWindowBase


class NotifWindowFriendRequest(NotifWindowBase):
    """Clash's received friend-request layout with Altis callbacks."""

    button_pos_headleft = -0.509
    button_pos_headright = -0.3
    button_z = 0.2889
    wordwrap_with_head = 11
    x_mult_with_head = 0.74
    raised_text_mult = 1.2

    def __init__(self, parent, data, onResolved=None, **kw):
        optiondefs = kwargsToOptionDefs()
        self.defineoptions(kw, optiondefs)
        NotifWindowBase.__init__(self, parent, data, **kw)
        self.initialiseoptions(NotifWindowFriendRequest)
        self.onResolved = onResolved
        self.button_yes = None
        self.button_no = None
        self.loadButtons()

        self.middle_text.multPos(y_mult=self.raised_text_mult)
        self.middle_text.setWordwrap(self.wordwrap_with_head)
        self.middle_text.multPos(x_mult=self.x_mult_with_head)
        try:
            from otp.otpbase import OTPLocalizer
            text = OTPLocalizer.FriendInviteeInvitation % data.getToonName()
        except Exception:
            text = '%s wants to be your friend.' % data.getToonName()
        self.middle_text.setTextWithVerticalAlignment(text)
        self.createHeadModel(data.getDna())

    def loadButtons(self):
        buttons = loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')
        self.button_yes = DirectButton(
            parent=self,
            pos=(self.button_pos_headleft * self.width, 0,
                 self.button_z * self.getPanelHeight()),
            relief=None,
            frameSize=(-0.04, 0.04, -0.04, 0.04),
            image=(buttons.find('**/ChtBx_OKBtn_UP'),
                   buttons.find('**/ChtBx_OKBtn_DN'),
                   buttons.find('**/ChtBx_OKBtn_Rllvr')),
            image_scale=1.08,
            text='OK',
            text_scale=0.06,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_pos=(0.09, -0.017),
            command=self.onYes,
        )
        self.button_no = DirectButton(
            parent=self,
            pos=(self.button_pos_headright * self.width, 0,
                 self.button_z * self.getPanelHeight()),
            relief=None,
            frameSize=(-0.04, 0.04, -0.04, 0.04),
            image=(buttons.find('**/CloseBtn_UP'),
                   buttons.find('**/CloseBtn_DN'),
                   buttons.find('**/CloseBtn_Rllvr')),
            image_pos=(0, 0, 0.003),
            text='No',
            text_scale=0.06,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_pos=(0.09, -0.017),
            command=self.onNo,
        )
        buttons.removeNode()

    def _resolved(self):
        if self.onResolved is not None:
            self.onResolved(self.data)

    def onYes(self):
        self.data.invokeYes()
        self._resolved()

    def onNo(self):
        self.data.invokeNo()
        self._resolved()

    def onTrash(self):
        self.data.invokeDismiss()
