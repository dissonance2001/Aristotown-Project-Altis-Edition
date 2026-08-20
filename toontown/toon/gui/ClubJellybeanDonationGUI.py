from __future__ import absolute_import
import random

from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from direct.gui.DirectSlider import DirectSlider
from direct.gui import DirectGuiGlobals as DGG
from pandac.PandaModules import TextNode, TransparencyAttrib

from toontown.club import ClubGlobals
from toontown.toon.socialpanel.SocialPanelGlobals import sp_gui
from toontown.toonbase import ToontownGlobals


class ClubJellybeanDonationGUI(DirectFrame):
    """Compact Python 2-compatible Club Jellybean donation notification.

    This intentionally behaves like Corporate Clash's notification panel:
    it attaches beside the Social Panel and does not darken or block the game.
    """

    width = 1.1
    height = 0.7

    def __init__(self, parent, manager, doneCallback=None):
        self.manager = manager
        self.doneCallback = doneCallback
        self._destroyed = False
        self._waiting = False
        self.amount = 0
        self.slider = None
        self.donateButton = None
        self.cancelButton = None
        self.closeButton = None
        self.buttonGui = None
        self.notificationGui = None
        self.activeButtons = []

        panelNode = None
        try:
            self.notificationGui = loader.loadModel(
                'phase_3.5/models/gui/notifications/notifications')
            panelNode = self.notificationGui.find('**/notification_base')
            if panelNode.isEmpty():
                panelNode = None
        except:
            self.notificationGui = None
            panelNode = None

        options = {
            'parent': parent,
            'pos': (-0.270, 0, 0.160),
            # Match Corporate Clash's NotificationContainer sizeMult.
            'scale': 0.621,
            'frameSize': (-self.width, 0, 0, self.height),
        }
        if panelNode is not None:
            options.update({
                'relief': None,
                'image': panelNode,
                'image_pos': (-0.5 * self.width, 0, 0.5),
                'image_scale': (self.width, 1, 1),
            })
        else:
            options.update({
                'relief': DGG.RAISED,
                'borderWidth': (0.025, 0.025),
                'frameColor': (0.52, 0.52, 0.52, 0.98),
            })

        DirectFrame.__init__(self, **options)
        self.initialiseoptions(ClubJellybeanDonationGUI)
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.setBin('sorted-gui-popup', 160)

        self.titleLabel = DirectLabel(
            parent=self,
            relief=None,
            text='Donate Jellybeans',
            text_font=ToontownGlobals.getMinnieFont(),
            text_scale=0.075,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(-0.5 * self.width, 0, 0.590),
        )
        self.messageLabel = DirectLabel(
            parent=self,
            relief=None,
            text='',
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.056,
            text_wordwrap=16.8,
            text_align=TextNode.ACenter,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(-0.5 * self.width, 0, 0.455),
        )
        self.amountLabel = DirectLabel(
            parent=self,
            relief=None,
            text='',
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.056,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(-0.5 * self.width, 0, 0.245),
        )

        self._makeCloseButton()
        self.accept('club-jellybean-donation-result', self._handleResult)
        try:
            self.accept(base.localAvatar.uniqueName('moneyChange'),
                        self._moneyChanged)
            self.accept(base.localAvatar.uniqueName('bankMoneyChange'),
                        self._moneyChanged)
        except:
            pass
        self.acceptOnce('escape', self.destroy)

        self._buildContent()

    def _formatNumber(self, value):
        try:
            return '{:,}'.format(int(value))
        except:
            return str(int(value))

    def _getToonMoney(self):
        try:
            return max(0, int(base.localAvatar.getTotalMoney()))
        except:
            try:
                return max(0, int(base.localAvatar.getMoney()) +
                           int(base.localAvatar.getBankMoney()))
            except:
                return 0

    def _getClubMoney(self):
        try:
            return max(0, int(self.manager.getClubJellybeans()))
        except:
            return 0

    def _getMaximumDonation(self):
        capacity = max(0, ClubGlobals.CLUB_MAX_JELLYBEANS -
                       self._getClubMoney())
        return min(self._getToonMoney(), capacity)

    def _buildContent(self):
        maximum = self._getMaximumDonation()
        clubMoney = self._getClubMoney()

        if maximum <= 0:
            if clubMoney >= ClubGlobals.CLUB_MAX_JELLYBEANS:
                message = 'Your Club Jellybean Bank is full.'
            else:
                message = 'You do not have any Jellybeans to donate.'
            self.messageLabel['text'] = message
            self.amountLabel['text'] = ''
            self._makeButtons(onlyClose=True)
            return

        self.messageLabel['text'] = (
            'Select the amount of Jellybeans you\nwould like to donate.')
        self._makeSlider(maximum)
        self._makeButtons(onlyClose=False)
        self._setAmount()

    def _makeSlider(self, maximum):
        track = sp_gui.find('**/Scrollbar_Screen')
        thumb = sp_gui.find('**/Scroll1')
        options = {
            'parent': self,
            'pos': (-0.5 * self.width, 0, 0.335),
            'scale': 0.40,
            'range': (1, max(1, int(maximum))),
            'value': 1,
            'command': self._setAmount,
        }
        if not track.isEmpty() and not thumb.isEmpty():
            options.update({
                'relief': None,
                'image': track,
                'image_scale': ((790.0 / 36.0) * 0.09, 0.09, 0.09),
                'thumb_image': thumb,
                'thumb_relief': None,
                'thumb_image_scale': 0.2,
            })
        else:
            options.update({
                'relief': DGG.SUNKEN,
                'frameSize': (-1.0, 1.0, -0.07, 0.07),
                'frameColor': (0.28, 0.28, 0.28, 1),
                'thumb_relief': DGG.RAISED,
                'thumb_frameSize': (-0.08, 0.08, -0.12, 0.12),
                'thumb_frameColor': (0.85, 0.85, 0.85, 1),
            })
        self.slider = DirectSlider(**options)

    def _buttonImages(self, prefix):
        if self.buttonGui is None:
            try:
                self.buttonGui = loader.loadModel(
                    'phase_3/models/gui/ttcc_gui_generalButtons')
            except:
                try:
                    self.buttonGui = loader.loadModel(
                        'phase_3/models/gui/dialog_box_buttons_gui')
                except:
                    self.buttonGui = None
        if self.buttonGui is None:
            return None

        candidates = (
            ('%s_UP' % prefix, '%s_DN' % prefix, '%s_Rllvr' % prefix),
            ('%sUP' % prefix, '%sDN' % prefix, '%sRllvr' % prefix),
        )
        for normalName, pressedName, hoverName in candidates:
            normal = self.buttonGui.find('**/' + normalName)
            if normal.isEmpty():
                continue
            pressed = self.buttonGui.find('**/' + pressedName)
            hover = self.buttonGui.find('**/' + hoverName)
            if pressed.isEmpty():
                pressed = normal
            if hover.isEmpty():
                hover = normal
            return (normal, pressed, hover, normal)
        return None

    def _makeCloseButton(self):
        images = self._buttonImages('CloseBtn')
        self.closeButton = DirectButton(
            parent=self,
            relief=None if images else DGG.RAISED,
            image=images,
            # Keep the dismiss button fully inside the notification frame.
            pos=(-0.062, 0, 0.625),
            frameSize=(-0.060, 0.060, -0.060, 0.060),
            text='' if images else 'X',
            text_scale=0.070,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            image_scale=0.76 if images else 0.62,
            command=self.destroy,
        )
        # Force the button above the notification artwork on Altis.
        self.closeButton.setBin('sorted-gui-popup', 170)
        self.closeButton.setDepthTest(False)
        self.closeButton.setDepthWrite(False)

    def _createActionButton(self, isYes, callback, center=False):
        text = 'OK' if isYes else 'No'
        prefix = 'ChtBx_OKBtn' if isYes else 'CloseBtn'
        images = self._buttonImages(prefix)
        if center:
            xPos = -0.520 * self.width
        elif isYes:
            xPos = -0.351 * self.width
        else:
            xPos = -0.760 * self.width
        button = DirectButton(
            parent=self,
            relief=None if images else DGG.RAISED,
            image=images,
            image_scale=1.08,
            pos=(xPos, 0, 0.140),
            frameSize=(-0.08, 0.08, -0.06, 0.06),
            text=text,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.060,
            text_pos=(0.09, -0.017) if images else (0, -0.018),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            command=callback,
        )
        self.activeButtons.append(button)
        return button

    def _makeButtons(self, onlyClose=False):
        self._cleanupActionButtons()
        if onlyClose:
            self.cancelButton = self._createActionButton(
                True, self.destroy, center=True)
            return
        self.cancelButton = self._createActionButton(
            False, self.destroy, center=False)
        self.donateButton = self._createActionButton(
            True, self._performDonate, center=False)

    def _cleanupActionButtons(self):
        for button in self.activeButtons:
            try:
                button.destroy()
            except:
                pass
        self.activeButtons = []
        self.donateButton = None
        self.cancelButton = None

    def _setAmount(self):
        if self.slider is None:
            self.amount = 0
            return
        self.amount = max(1, int(round(self.slider.getValue())))
        plural = '' if self.amount == 1 else 's'
        self.amountLabel['text'] = '%s Jellybean%s' % (
            self._formatNumber(self.amount), plural)

    def _performDonate(self):
        if self._waiting or self.amount < 1:
            return
        self._waiting = True
        if self.slider is not None:
            self.slider['state'] = DGG.DISABLED
        if self.donateButton is not None:
            self.donateButton['state'] = DGG.DISABLED
        if self.cancelButton is not None:
            self.cancelButton['state'] = DGG.DISABLED
        self.messageLabel['text'] = 'Donating Jellybeans...'
        if not self.manager.requestDonateJellybeans(self.amount):
            self._handleResult(
                False, self.amount,
                'The Jellybean donation could not be sent.')

    def _handleResult(self, success, amount, message):
        if self._destroyed:
            return
        self._waiting = False

        if success:
            if self.slider is not None:
                self.slider.destroy()
                self.slider = None
            self._cleanupActionButtons()
            self.amountLabel['text'] = ''
            plural = '' if int(amount) == 1 else 's'
            response = self._successResponse(int(amount))
            self.messageLabel['text'] = (
                'You have donated %s Jellybean%s.\n%s' % (
                    self._formatNumber(amount), plural, response))
            self.messageLabel.setPos(-0.5 * self.width, 0, 0.390)
            self._makeButtons(onlyClose=True)
            try:
                loader.loadSfx(
                    'phase_5/audio/sfx/SA_life_insurance_register.ogg').play()
            except:
                pass
            return

        self.messageLabel['text'] = str(message)
        maximum = self._getMaximumDonation()
        if maximum <= 0:
            if self.slider is not None:
                self.slider.destroy()
                self.slider = None
            if self.donateButton is not None:
                self.donateButton['state'] = DGG.DISABLED
            if self.cancelButton is not None:
                self.cancelButton['state'] = DGG.NORMAL
            return

        if self.slider is not None:
            self.slider['range'] = (1, maximum)
            self.slider['value'] = min(self.amount, maximum)
            self.slider['state'] = DGG.NORMAL
            self._setAmount()
        if self.donateButton is not None:
            self.donateButton['state'] = DGG.NORMAL
        if self.cancelButton is not None:
            self.cancelButton['state'] = DGG.NORMAL

    def _successResponse(self, beans):
        choices = [
            'Your friends will be excited!',
            'Thank you for your gratitude.',
            'This is not tax-deductible.',
        ]
        if beans == 1:
            choices = [
                'Great work.',
                'Stellar performance.',
                'Nobody asked.',
            ]
        elif 10000 <= beans < 50000:
            choices = [
                "That's certainly a lot!",
                'WOW! What a great donation!',
                'You are most charitable.',
            ]
        elif 50000 <= beans < 100000:
            choices = [
                'You must have worked hard for that!',
                "That's outrageous!",
            ]
        elif 100000 <= beans < 1000000:
            choices = [
                'Goodbye, jellybean bank.',
                'You feel a heavy burden pass.',
            ]
        return random.choice(choices)

    def _moneyChanged(self, *args):
        if self._waiting or self.slider is None:
            return
        maximum = self._getMaximumDonation()
        if maximum < 1:
            self.slider['state'] = DGG.DISABLED
            if self.donateButton is not None:
                self.donateButton['state'] = DGG.DISABLED
            return
        self.slider['range'] = (1, maximum)
        self.slider['value'] = min(max(1, self.amount), maximum)
        self._setAmount()

    def show(self):
        DirectFrame.show(self)
        self.setBin('sorted-gui-popup', 160)

    def destroy(self):
        if self._destroyed:
            return
        self._destroyed = True
        self.ignoreAll()
        self._cleanupActionButtons()
        if self.closeButton is not None:
            try:
                self.closeButton.destroy()
            except:
                pass
            self.closeButton = None
        if self.slider is not None:
            try:
                self.slider.destroy()
            except:
                pass
            self.slider = None
        if self.buttonGui is not None:
            try:
                self.buttonGui.removeNode()
            except:
                pass
            self.buttonGui = None
        if self.notificationGui is not None:
            try:
                self.notificationGui.removeNode()
            except:
                pass
            self.notificationGui = None
        DirectFrame.destroy(self)
        callback = self.doneCallback
        self.doneCallback = None
        if callback is not None:
            try:
                callback()
            except:
                pass
