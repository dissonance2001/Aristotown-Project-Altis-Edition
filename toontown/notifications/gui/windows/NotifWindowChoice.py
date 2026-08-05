from pandac.PandaModules import TextNode
from direct.gui.DirectGui import DirectButton

from toontown.notifications.gui.ClashGuiUtils import kwargsToOptionDefs
from toontown.notifications.gui.windows.NotifWindowBase import NotifWindowBase


class NotifWindowChoice(NotifWindowBase):
    """Clash GenericYesNo window adapted to Altis callback data."""

    button_pos_left = -0.645
    button_pos_right = -0.395
    button_z = 0.25

    def __init__(self, parent, data, onResolved=None, **kw):
        optiondefs = kwargsToOptionDefs()
        self.defineoptions(kw, optiondefs)
        NotifWindowBase.__init__(self, parent, data, **kw)
        self.initialiseoptions(NotifWindowChoice)
        self.onResolved = onResolved
        self.button_yes = None
        self.button_no = None
        self.loadButtons()
        self.title_text.setText(data.getTitle())
        self.text['pos'] = (-0.5 * self.width,
                            self.getPanelHeight() -
                            (self.title_height * 2.2))
        self.text.setText(data.getSubtitle())

    def loadButtons(self):
        buttons = loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')
        self.button_yes = DirectButton(
            parent=self,
            pos=(self.button_pos_left * self.width, 0,
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
            pos=(self.button_pos_right * self.width, 0,
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
