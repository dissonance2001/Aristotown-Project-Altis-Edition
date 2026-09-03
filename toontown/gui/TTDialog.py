from panda3d.core import Vec3, TextNode, Point3, VBase3, NodePath
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from direct.directnotify import DirectNotifyGlobal
from direct.showbase import ShowBaseGlobal
from toontown.gui.ScaledFrame import ScaledFrame
from toontown.toon.gui import GuiBinGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

# No buttons at all
NoButtons = 0
# just an OK button
Acknowledge = 1
# Just a CANCEL button
CancelOnly = 2
# OK and CANCEL buttons
TwoChoice = 3
# Yes and No buttons
YesNo = 4
# custom 2 buttons
TwoChoiceCustom = 5
YesYesNo = 6
YesYesYesNo = 7


class ScaledDialog(ScaledFrame):
    """
    "Scaled" frame variant of DirectDialog that allows Scaled Frames to be used
    instead of normal static DirectFrames.
    """

    def __init__(self, parent=None, **kw):
        """Creates a popup dialog to alert and/or interact with user.
        Some of the main keywords that can be used to customize the dialog:

        Parameters:
            text (str): Text message/query displayed to user
            geom: Geometry to be displayed in dialog
            buttonTextList: List of text to show on each button
            buttonGeomList: List of geometry to show on each button
            buttonImageList: List of images to show on each button
            buttonValueList: List of values sent to dialog command for
                each button.  If value is [] then the ordinal rank of
                the button is used as its value.
            buttonHotKeyList: List of hotkeys to bind to each button.
                Typing the hotkey is equivalent to pressing the
                corresponding button.
            suppressKeys: Set to true if you wish to suppress keys
                (i.e. Dialog eats key event), false if you wish Dialog
                to pass along key event.
            buttonSize: 4-tuple used to specify custom size for each
                button (to make bigger then geom/text for example)
            pad: Space between border and interior graphics
            topPad: Extra space added above text/geom/image
            midPad: Extra space added between text/buttons
            sidePad: Extra space added to either side of text/buttons
            buttonPadSF: Scale factor used to expand/contract button
                horizontal spacing
            command: Callback command used when a button is pressed.
                Value supplied to command depends on values in
                buttonValueList.

        Note:
            The number of buttons on the dialog depends on the maximum
            length of any button[Text|Geom|Image|Value]List specified.
            Values of None are substituted for lists that are shorter
            than the max length
         """

        # Inherits from ScaledFrame
        optiondefs = (
            # Define type of DirectGuiWidget
            ('dialogName', 'DirectDialog_' + repr(DirectDialog.PanelIndex), DGG.INITOPT),
            # Default position is slightly forward in Y, so as not to
            # intersect the near plane, which is incorrectly set to 0
            # in DX for some reason.
            ('pos', (0, 0.1, 0), None),
            ('pad', (0.1, 0.1), None),
            ('text', '', None),
            ('text_align', TextNode.ALeft, None),
            ('text_scale', 0.06, None),
            ('image', None, None),
            ('relief', DGG.getDefaultDialogRelief(), None),
            ('borderWidth', (0.01, 0.01), None),
            ('buttonTextList', [], DGG.INITOPT),
            ('buttonGeomList', [], DGG.INITOPT),
            ('buttonImageList', [], DGG.INITOPT),
            ('buttonValueList', [], DGG.INITOPT),
            ('buttonHotKeyList', [], DGG.INITOPT),
            ('button_borderWidth', (.01, .01), None),
            ('button_pad', (.01, .01), None),
            ('button_relief', DGG.RAISED, None),
            ('button_text_scale', 0.06, None),
            ('buttonSize', None, DGG.INITOPT),
            ('topPad', 0.11, DGG.INITOPT),
            ('midPad', 0.12, DGG.INITOPT),
            ('sidePad', -0.016, DGG.INITOPT),
            ('botPad', 0.02, None),
            ('buttonPadSF', 1.1, DGG.INITOPT),
            # Alpha of fade screen behind dialog
            ('fadeScreen', 0.5, None),
            ('command', None, None),
            ('extraArgs', [], None),
            ('sortOrder', DGG.NO_FADE_SORT_INDEX, None),
            ('popIn',             True,          None),
            ('shadowStrength',    0.04,          None),
            )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs, dynamicGroups = ("button",))

        # Initialize superclasses
        ScaledFrame.__init__(self, parent)

        # Clean up any previously existing panel with the same unique
        # name.  We don't allow any two panels with the same name to
        # coexist.
        cleanupDialog(self['dialogName'])
        # Store this panel in our map of all open panels.
        DirectDialog.AllDialogs[self['dialogName']] = self
        DirectDialog.PanelIndex += 1

        # Determine number of buttons
        self.numButtons = max(len(self['buttonTextList']),
                              len(self['buttonGeomList']),
                              len(self['buttonImageList']),
                              len(self['buttonValueList']))
        # Create buttons
        self.buttonList = []
        index = 0
        for i in range(self.numButtons):
            name = 'Button' + repr(i)
            try:
                text = self['buttonTextList'][i]
            except IndexError:
                text = None
            try:
                geom = self['buttonGeomList'][i]
            except IndexError:
                geom = None
            try:
                image = self['buttonImageList'][i]
            except IndexError:
                image = None
            try:
                value = self['buttonValueList'][i]
            except IndexError:
                value = i
                self['buttonValueList'].append(i)
            try:
                hotKey = self['buttonHotKeyList'][i]
            except IndexError:
                hotKey = None
            button = self.createcomponent(
                name, (), "button",
                DirectButton, (self,),
                text = text,
                geom = geom,
                image = image,
                suppressKeys = self['suppressKeys'],
                frameSize = self['buttonSize'],
                command = lambda s = self, v = value: s.buttonCommand(v)
                )
            self.buttonList.append(button)

        # Update dialog when everything has been initialised
        self.postInitialiseFuncList.append(self.configureDialog)
        self.initialiseoptions(ScaledDialog)
        self._fadedScreen = False
        if self.cget('popIn'):
            self.doPopInAnimation()

    def configureDialog(self):
        # Set up hot key bindings
        bindList = zip(self.buttonList, self['buttonHotKeyList'],
                       self['buttonValueList'])
        for button, hotKey, value in bindList:
            if isinstance(hotKey, (list, tuple)):
                for key in hotKey:
                    button.bind('press-' + key + '-', self.buttonCommand,
                                extraArgs = [value])
                    self.bind('press-' + key + '-', self.buttonCommand,
                              extraArgs = [value])

            else:
                button.bind('press-' + hotKey + '-', self.buttonCommand,
                            extraArgs = [value])
                self.bind('press-' + hotKey + '-', self.buttonCommand,
                          extraArgs = [value])
        # Position buttons and text
        pad = self['pad']
        if self.hascomponent('image0'):
            image = self.component('image0')
        else:
            image = None
        # Get size of text/geom without image (for state 0)
        if image:
            image.reparentTo(ShowBaseGlobal.hidden)
        bounds = self.stateNodePath[0].getTightBounds()
        if image:
            image.reparentTo(self.stateNodePath[0])
        if bounds is None:
            l = 0
            r = 0
            b = 0
            t = 0
        else:
            l = bounds[0][0]
            r = bounds[1][0]
            b = bounds[0][2]
            t = bounds[1][2]
        # Center text and geom around origin
        # How far is center of text from origin?
        xOffset = -(l+r)*0.5
        zOffset = -(b+t)*0.5
        # Update bounds to reflect text movement
        l += xOffset
        r += xOffset
        b += zOffset
        t += zOffset
        # Offset text and geom to center
        if self['text']:
            self['text_pos'] = (self['text_pos'][0] + xOffset,
                                self['text_pos'][1] + zOffset)
        if self['geom']:
            self['geom_pos'] = Point3(self['geom_pos'][0] + xOffset,
                                      self['geom_pos'][1],
                                      self['geom_pos'][2] + zOffset)
        if self.numButtons != 0:
            bpad = self['button_pad']
            # Get button size
            if self['buttonSize']:
                # Either use given size
                buttonSize = self['buttonSize']
                bl = buttonSize[0]
                br = buttonSize[1]
                bb = buttonSize[2]
                bt = buttonSize[3]
            else:
                # Or get bounds of union of buttons
                bl = br = bb = bt = 0
                for button in self.buttonList:
                    bounds = button.stateNodePath[0].getTightBounds()
                    if bounds is None:
                        bl = 0
                        br = 0
                        bb = 0
                        bt = 0
                    else:
                        bl = min(bl, bounds[0][0])
                        br = max(br, bounds[1][0])
                        bb = min(bb, bounds[0][2])
                        bt = max(bt, bounds[1][2])
                bl -= bpad[0]
                br += bpad[0]
                bb -= bpad[1]
                bt += bpad[1]
                # Now resize buttons to match largest
                for button in self.buttonList:
                    button['frameSize'] = (bl, br, bb, bt)
            # Must compensate for scale
            scale = self['button_scale']
            # Can either be a Vec3 or a tuple of 3 values
            if isinstance(scale, (VBase3, list, tuple)):
                sx = scale[0]
                sz = scale[2]
            elif isinstance(scale, (int, float)):
                sx = sz = scale
            else:
                sx = sz = 1
            bl *= sx
            br *= sx
            bb *= sz
            bt *= sz
            # Position buttons
            # Calc button width and height
            bHeight = bt - bb
            bWidth = br - bl
            # Add pad between buttons
            bSpacing = self['buttonPadSF'] * bWidth
            bPos = -bSpacing * (self.numButtons - 1)*0.5
            index = 0
            for button in self.buttonList:
                button.setPos(bPos + index * bSpacing, 0,
                              b - self['midPad'] - bpad[1] - bt)
                index += 1
            bMax = bPos + bSpacing * (self.numButtons - 1)
        else:
            bpad = 0
            bl = br = bb = bt = 0
            bPos = 0
            bMax = 0
            bpad = (0, 0)
            bHeight = bWidth = 0
        # Resize frame to fit text and buttons
        l = min(bPos + bl, l) - pad[0]
        r = max(bMax + br, r) + pad[0]
        sidePad = self['sidePad']
        l -= sidePad
        r += sidePad
        # reduce bottom by pad, button height and 2*button pad
        b = min(b - self['midPad'] - bpad[1] - bHeight - bpad[1], b) - pad[1] + self['botPad']
        t = t + self['topPad'] + pad[1]
        if self['frameSize'] is None:
            self['frameSize'] = (l, r, b, t)

        # Center frame about text and buttons
        self['image_pos'] = ((l + r) * 0.5, 0.0, (b + t) * 0.5)
        self.resetFrameSize()

    def show(self):
        if self['fadeScreen']:
            self._fadedScreen = True
            base.transitions.fadeScreen(self['fadeScreen'])
            self.setBin('sorted-gui-popup', GuiBinGlobals.TTDialogBin)
        ScaledFrame.show(self)

    def hide(self):
        if self['fadeScreen'] and self._fadedScreen:
            self._fadedScreen = False
            base.transitions.noTransitions()
        ScaledFrame.hide(self)

    def buttonCommand(self, value, event = None):
        if self['command']:
            self['command'](value, *self['extraArgs'])

    def setMessage(self, message):
        self.setText(message)
        self.configureDialog()

    def cleanup(self):
        # Remove this panel out of the AllDialogs list
        uniqueName = self['dialogName']
        if uniqueName in DirectDialog.AllDialogs:
            del DirectDialog.AllDialogs[uniqueName]
        self.destroy()

    def destroy(self):
        if self['fadeScreen'] and self._fadedScreen:
            base.transitions.noTransitions()
        for button in self.buttonList:
            button.destroy()
        self._fadedScreen = False
        ScaledFrame.destroy(self)


class TTDialog(ScaledDialog):
    """
    GUI Class for a generic green-border dialog box.
    """
    path = 'phase_3/models/gui/ttcc_gui_generalButtons'

    def __init__(self, parent=None, style=NoButtons, **kw):
        if parent is None:
            parent = aspect2d

        self.style = style

        # Load gui elements if necessary
        buttons = None
        if self.style != NoButtons:
            buttons = loader.loadModel(self.path)

        # Init buttons
        if self.style == TwoChoiceCustom:
            okImageList = (
                buttons.find('**/ChtBx_OKBtn_UP'),
                buttons.find('**/ChtBx_OKBtn_DN'),
                buttons.find('**/ChtBx_OKBtn_Rllvr')
            )
            cancelImageList = (
                buttons.find('**/CloseBtn_UP'),
                buttons.find('**/CloseBtn_DN'),
                buttons.find('**/CloseBtn_Rllvr')
            )
            buttonImage = [okImageList, cancelImageList]
            buttonValue = [DGG.DIALOG_OK, DGG.DIALOG_CANCEL]
            if 'buttonText' in kw:
                buttonText = kw['buttonText']
                del kw['buttonText']
            else:
                buttonText = [TTLocalizer.DialogOK, TTLocalizer.DialogCancel]

        elif self.style == TwoChoice:
            okImageList = (
                buttons.find('**/ChtBx_OKBtn_UP'),
                buttons.find('**/ChtBx_OKBtn_DN'),
                buttons.find('**/ChtBx_OKBtn_Rllvr')
            )
            cancelImageList = (
                buttons.find('**/CloseBtn_UP'),
                buttons.find('**/CloseBtn_DN'),
                buttons.find('**/CloseBtn_Rllvr')
            )
            buttonImage = [okImageList, cancelImageList]
            buttonText = [TTLocalizer.DialogOK, TTLocalizer.DialogCancel]
            buttonValue = [DGG.DIALOG_OK, DGG.DIALOG_CANCEL]

        elif self.style == YesNo:
            okImageList = (
                buttons.find('**/ChtBx_OKBtn_UP'),
                buttons.find('**/ChtBx_OKBtn_DN'),
                buttons.find('**/ChtBx_OKBtn_Rllvr')
            )
            cancelImageList = (
                buttons.find('**/CloseBtn_UP'),
                buttons.find('**/CloseBtn_DN'),
                buttons.find('**/CloseBtn_Rllvr')
            )
            buttonImage = [okImageList, cancelImageList]
            buttonText = [TTLocalizer.DialogYes, TTLocalizer.DialogNo]
            buttonValue = [DGG.DIALOG_OK, DGG.DIALOG_CANCEL]

        elif self.style == YesYesNo:
            okImageList = (
                buttons.find('**/ChtBx_OKBtn_UP'),
                buttons.find('**/ChtBx_OKBtn_DN'),
                buttons.find('**/ChtBx_OKBtn_Rllvr')
            )
            cancelImageList = (
                buttons.find('**/CloseBtn_UP'),
                buttons.find('**/CloseBtn_DN'),
                buttons.find('**/CloseBtn_Rllvr')
            )
            buttonImage = [okImageList, okImageList, cancelImageList]
            buttonValue = [1, 2, 3]
            if 'buttonText' in kw:
                buttonText = kw['buttonText']
                del kw['buttonText']
            else:
                buttonText = [TTLocalizer.DialogOK, TTLocalizer.DialogOK, TTLocalizer.DialogCancel]

        elif self.style == YesYesYesNo:
            okImageList = (
                buttons.find('**/ChtBx_OKBtn_UP'),
                buttons.find('**/ChtBx_OKBtn_DN'),
                buttons.find('**/ChtBx_OKBtn_Rllvr')
            )
            cancelImageList = (
                buttons.find('**/CloseBtn_UP'),
                buttons.find('**/CloseBtn_DN'),
                buttons.find('**/CloseBtn_Rllvr')
            )
            buttonImage = [okImageList, okImageList, okImageList, cancelImageList]
            buttonValue = [1, 2, 3, 4]
            if 'buttonText' in kw:
                buttonText = kw['buttonText']
                del kw['buttonText']
            else:
                buttonText = [
                    TTLocalizer.DialogOK,
                    TTLocalizer.DialogOK,
                    TTLocalizer.DialogOK,
                    TTLocalizer.DialogCancel
                ]

        elif self.style == Acknowledge:
            okImageList = (
                buttons.find('**/ChtBx_OKBtn_UP'),
                buttons.find('**/ChtBx_OKBtn_DN'),
                buttons.find('**/ChtBx_OKBtn_Rllvr')
            )
            buttonImage = [okImageList]
            buttonText = [TTLocalizer.DialogOK]
            buttonValue = [DGG.DIALOG_OK]

        elif self.style == CancelOnly:
            cancelImageList = (
                buttons.find('**/CloseBtn_UP'),
                buttons.find('**/CloseBtn_DN'),
                buttons.find('**/CloseBtn_Rllvr')
            )
            buttonImage = [cancelImageList]
            buttonText = [TTLocalizer.DialogCancel]
            buttonValue = [DGG.DIALOG_CANCEL]

        elif self.style == NoButtons:
            buttonImage = []
            buttonText = []
            buttonValue = []
        else:
            self.notify.error('No such style as: ' + str(self.style))

        optiondefs = (
            # Define type of DirectGuiWidget
            ('buttonImageList', buttonImage, DGG.INITOPT),
            ('buttonTextList', buttonText, DGG.INITOPT),
            ('buttonValueList', buttonValue, DGG.INITOPT),
            ('buttonPadSF', 2.2, DGG.INITOPT),
            ('text_font', DGG.getDefaultFont(), None),
            ('text_wordwrap', 12, None),
            ('text_scale', 0.07, None),
            ('buttonSize', (-.05, 0.05, -.05, 0.05), None),
            ('button_pad', (0, 0), None),
            ('button_relief', None, None),
            ('button_text_pos', (0, -0.1), None),
            ('fadeScreen', 0.5, None),
            ('fadeTime', 0.3, None),
            ('image_color', None, None),
            ('image', None, None),
        )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)
        ScaledDialog.__init__(self, parent)
        self.initialiseoptions(TTDialog)
        if buttons is not None:
            buttons.removeNode()
        if self.cget('popIn'):
            self.doPopInAnimation()

    def show(self):
        if self['fadeScreen']:
            self._fadedScreen = True
            if self['fadeTime'] is not None:
                base.transitions.fadeScreen(alpha=self['fadeScreen'], t=self['fadeTime'])
            else:
                base.transitions.fadeScreen(alpha=self['fadeScreen'])
        self.setBin('sorted-gui-popup', GuiBinGlobals.TTDialogBin)
        NodePath.show(self)


@DirectNotifyCategory()
class TTGlobalDialog(TTDialog):
    def __init__(self, message = '', doneEvent = None, style = NoButtons, okButtonText = TTLocalizer.DialogOK,
                 cancelButtonText = TTLocalizer.DialogCancel, **kw):  
        # Sanity check
        if doneEvent is None and style != NoButtons:
            self.notify.error('Boxes with buttons must specify a doneEvent.')

        self.__doneEvent = doneEvent

        if style == NoButtons:
            buttonText = []
        elif style == Acknowledge:
            buttonText = [okButtonText]
        elif style == CancelOnly:
            buttonText = [cancelButtonText]
        else:
            buttonText = [okButtonText, cancelButtonText]

        optiondefs = (
            # Define type of DirectGuiWidget
            ('dialogName', 'globalDialog', DGG.INITOPT),
            ('buttonTextList', buttonText, DGG.INITOPT),
            ('text', message, None),
            ('command', self.handleButton, None),
            ('fadeScreen', 0.5, None),
        )
        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)
        TTDialog.__init__(self, style = style)
        self.initialiseoptions(TTGlobalDialog)
        if self.cget('popIn'):
            self.doPopInAnimation()

    def handleButton(self, value):
        if value == DGG.DIALOG_OK:
            self.doneStatus = 'ok'
            messenger.send(self.__doneEvent)
        elif value == DGG.DIALOG_CANCEL:
            self.doneStatus = 'cancel'
            messenger.send(self.__doneEvent)
