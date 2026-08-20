from __future__ import absolute_import
from pandac.PandaModules import TextNode
from direct.gui.DirectGui import DirectButton, DirectFrame
from direct.gui import DirectGuiGlobals as DGG

from toontown.notifications.gui.ClashGuiUtils import ExtendedOnscreenText, kwargsToOptionDefs


class NotifWindowBase(DirectFrame):
    """Corporate Clash's notification window, adapted for Altis DirectGUI.

    Altis's older DirectGUI build can draw a DirectFrame's own ``image`` after
    child text when the parent is placed in a popup bin.  The exact Clash
    ``notification_base`` node is therefore kept as a dedicated child in the
    same popup bin with a lower sort value.  Geometry and transforms are
    unchanged; only draw ordering is made explicit.
    """

    gui = loader.loadModel('phase_3.5/models/gui/notifications/notifications')
    width = 1.1
    title_height = 0.1
    shadow_image_ratio = 573.0 / 627.0
    shadow_xscale = 1.365
    shadow_zscale = 1.385

    button_x_left = -0.76
    button_x_mid = -0.52
    button_x_right = -0.351
    button_z = 0.2

    textZOffsetWithButtons = 1.14
    sfx = 'phase_3.5/audio/sfx/UI_notif_general.ogg'

    No = 0
    Yes = 1

    def __init__(self, parent, data=None, **kw):
        optiondefs = kwargsToOptionDefs(
            relief=None,
            scale=1,
            height=0.45,
            heightMult=1.0,
        )
        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, parent, **kw)
        self.initialiseoptions(NotifWindowBase)

        self['frameSize'] = (-1, 0, 0, self.getPanelHeight())
        self.data = data
        self.active = False
        self.activeButtons = []
        self.headModel = None

        self.setBin('sorted-gui-popup', 900)
        self.setDepthTest(False)
        self.setDepthWrite(False)

        self.shadow = DirectFrame(
            parent=self,
            relief=None,
            state=DGG.DISABLED,
            image=self.gui.find('**/notifpanel_shadow'),
            image_pos=(-0.50 * self.width, 0, 0.41),
            image_scale=(self.shadow_image_ratio * self.shadow_xscale,
                         1,
                         self.shadow_zscale * 0.815),
            image_color=(1, 1, 1, 0.7),
        )
        self.shadow.setBin('sorted-gui-popup', 898)
        self.shadow.setDepthTest(False)
        self.shadow.setDepthWrite(False)

        # The model node and all of its original transforms are exactly Clash's.
        self.background = DirectFrame(
            parent=self,
            relief=None,
            state=DGG.DISABLED,
            image=self.gui.find('**/notification_base'),
            image_pos=(-0.5 * self.width, 0, 0.5),
            image_scale=(1.0 * self.width, 1, 1),
        )
        self.background.setBin('sorted-gui-popup', 899)
        self.background.setDepthTest(False)
        self.background.setDepthWrite(False)

        self.text = ExtendedOnscreenText(
            parent=self,
            align=TextNode.ACenter,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1),
            scale=0.056,
            wordwrap=16.8,
            pos=(-0.5 * self.width,
                 (self.getPanelHeight() - self.title_height) / 2.0),
        )
        self.middle_text = ExtendedOnscreenText(
            parent=self,
            align=TextNode.ACenter,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1),
            scale=0.056,
            wordwrap=16.8,
            pos=(-0.5 * self.width, self.getPanelHeight() / 2.0),
        )
        self.title_text = ExtendedOnscreenText(
            parent=self,
            align=TextNode.ACenter,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 1),
            scale=0.075,
            pos=(-0.5 * self.width,
                 self.getPanelHeight() - (self.title_height * 1.1)),
        )

        for textNode in (self.text, self.middle_text, self.title_text):
            textNode.setBin('sorted-gui-popup', 901)
            textNode.setDepthTest(False)
            textNode.setDepthWrite(False)

    def destroy(self):
        self.cleanupButtons()
        self.clearHeadModel()
        self.ignoreAll()

        if self.background:
            self.background.destroy()
            self.background = None
        if self.shadow:
            self.shadow.destroy()
            self.shadow = None
        if self.text:
            self.text.destroy()
            self.text = None
        if self.middle_text:
            self.middle_text.destroy()
            self.middle_text = None
        if self.title_text:
            self.title_text.destroy()
            self.title_text = None

        DirectFrame.destroy(self)

    def show(self):
        self.active = True
        DirectFrame.show(self)

    def hide(self):
        self.active = False
        DirectFrame.hide(self)

    def getPanelHeight(self):
        return self.cget('height') * self.cget('heightMult')

    def setActiveState(self, mode):
        self.active = mode

    def onInitialDrop(self):
        pass

    def onTrash(self):
        if self.data is not None:
            self.data.invokeDismiss()

    def getNotifData(self):
        return self.data

    def getSfxPath(self):
        if self.data is not None and getattr(self.data, 'sfx', None):
            return self.data.sfx
        return self.sfx

    def playSfx(self):
        path = self.getSfxPath()
        if path is not None:
            base.loader.loadSfx(path).play()

    def createButton(self, buttonType, callback, center=False):
        text = {self.No: 'No', self.Yes: 'OK'}.get(buttonType)
        xpos = {self.No: self.button_x_left,
                self.Yes: self.button_x_right}.get(buttonType)
        if center:
            xpos = self.button_x_mid
        prefix = {self.No: 'CloseBtn_',
                  self.Yes: 'ChtBx_OKBtn_'}.get(buttonType)
        suffix = ('UP', 'DN', 'Rllvr')

        buttons = loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')
        button = DirectButton(
            parent=self,
            pos=(xpos * self.width, 0,
                 self.button_z * self.getPanelHeight()),
            relief=None,
            frameSize=(-0.04, 0.04, -0.04, 0.04),
            image=(
                buttons.find('**/' + prefix + suffix[0]),
                buttons.find('**/' + prefix + suffix[1]),
                buttons.find('**/' + prefix + suffix[2]),
            ),
            image_scale=1.08,
            text=text,
            text_scale=0.06,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_pos=(0.09, -0.017),
            command=callback,
        )
        button.setBin('sorted-gui-popup', 903)
        button.setDepthTest(False)
        button.setDepthWrite(False)
        buttons.removeNode()

        if not self.activeButtons:
            self.text.multPos(y_mult=self.textZOffsetWithButtons)
        self.activeButtons.append(button)
        return button

    def cleanupButtons(self):
        for button in self.activeButtons:
            button.destroy()
        if self.activeButtons:
            self.text.multPos(y_mult=1.0 / self.textZOffsetWithButtons)
        self.activeButtons = []

    def createHeadModel(self, dna):
        self.clearHeadModel()
        if dna is None:
            return
        try:
            from toontown.toon.ToonHead import ToonHead
            head = hidden.attachNewNode('head', 20)
            self.headModel = ToonHead()
            self.headModel.setupHead(dna, forGui=1)
            self.headModel.fitAndCenterHead(1.0, forGui=1)
            self.headModel.reparentTo(head)
            self.headModel.setName('headModel')
            self.headModel.startBlink()
            self['geom'] = self.headModel
            self['geom_scale'] = 0.14
            self['geom_pos'] = (-0.79 * self.width, 0,
                                self.getPanelHeight() * 0.43)
        except Exception:
            self.clearHeadModel()

    def clearHeadModel(self):
        if self.headModel is None:
            return
        try:
            self.headModel.stopBlink()
            self.headModel.stopLookAroundNow()
            self.headModel.delete()
        except Exception:
            try:
                self.headModel.removeNode()
            except Exception:
                pass
        self.headModel = None
        try:
            self['geom'] = None
        except Exception:
            pass
