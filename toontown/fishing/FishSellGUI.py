import math

from direct.gui.DirectGui import *

from toontown.gui.ScaledFrame import ScaledFrame
from toontown.toon.gui import GuiBinGlobals
from toontown.fishing import FishPicker
from toontown.toonbase import TTLocalizer
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class FishSellGUI(ScaledFrame):
    """
    FishSellGUI(ScaledFrame)
    """

    def __init__(self, doneEvent):
        ScaledFrame.__init__(
            self,
            parent=aspect2d,
            relief=None,
            state='normal',
            #geom_scale=(2.0, 1, 1.5),
            frameSize=(-1, 1, -0.75, 0.75),
            pos=(0, 0, 0),
            text='',
            text_wordwrap=26,
            text_scale=0.06,
            text_pos=(0, 0.65)
        )
        self.initialiseoptions(FishSellGUI)
        self['shadowStrength'] = 0.04

        # Send this when we are done so whoever made us can get a callback
        self.doneEvent = doneEvent

        # Create the fish picker
        self.picker = FishPicker.FishPicker(self)
        self.picker.load()
        self.picker.setPos(-0.59, 0, 0.03)
        self.picker.setScale(0.93)
        newTankFish = base.localAvatar.fishTank.getFish()
        self.picker.update(newTankFish)
        self.picker.show()

        # Init buttons
        buttons = loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')

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

        self.cancelButton = DirectButton(
            parent=self,
            relief=None,
            image=cancelImageList,
            pos=(0.3, 0, -0.58),
            text=TTLocalizer.FishGuiCancel,
            text_scale=TTLocalizer.FSGUIcancelButton,
            text_pos=(0, -0.1),
            command=self.__cancel
        )

        self.okButton = DirectButton(
            parent=self,
            relief=None,
            image=okImageList,
            pos=(0.6, 0, -0.58),
            text=TTLocalizer.FishGuiOk,
            text_scale=TTLocalizer.FSGUIokButton,
            text_pos=(0, -0.1),
            command=self.__sellFish
        )

        buttons.removeNode()

        # update the value of the fish tank
        self.__updateFishValue()
        self.setBin('sorted-gui-popup', GuiBinGlobals.TTDialogBin)

    def destroy(self):
        ScaledFrame.destroy(self)

    def __cancel(self):
        messenger.send(self.doneEvent, [0])

    def __sellFish(self):
        messenger.send(self.doneEvent, [1])

    def __updateFishValue(self):
        fishTank = base.localAvatar.getFishTank()
        num = len(fishTank)
        # TODO: route through Altis's booster/gumball multiplier system (toontown.gumball.GumballGlobals.applyBoosters)
        # once jellybean boosters are wired up; no multiplier applied for now.
        value = round(fishTank.getTotalValue())
        self['text'] = TTLocalizer.FishTankValue % {
            'name': base.localAvatar.getName(),
            'num': num,
            'value': value
        }
        self.setText()
