"""FishPicker module: contains the FishPicker class"""

from direct.gui.DirectGui import *
from panda3d.core import *

from toontown.toonbase import TTLocalizer
from toontown.fishing import FishPanel
from toontown.fishing import FishGlobals
import math

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class FishPicker(DirectScrolledList):
    """
    FishPicker(DirectScrolledList)
    """

    # special methods
    def __init__(self, parent = aspect2d, **kw):
        """
        FishPicker constructor: create a scrolling list of fish
        """
        self.fishList = []
        self.shown = 0

        # make the scrolling pick list for the fish names
        gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')

        optiondefs = (
            ('parent', parent, None),
            ('relief', None, None),
            # inc and dec are DirectButtons
            ('incButton_image', (
                gui.find('**/FndsLst_ScrollUp'),
                gui.find('**/FndsLst_ScrollDN'),
                gui.find('**/FndsLst_ScrollUp_Rllvr'),
                gui.find('**/FndsLst_ScrollUp')), None),
            ('incButton_relief', None, None),
            ('incButton_scale', (1.6, 1.6, -1.6), None),
            ('incButton_pos', (0.16, 0, -0.47), None),
            # Make the disabled button fade out
            ('incButton_image3_color', Vec4(0.7, 0.7, 0.7, 0.75), None),
            ('decButton_image', (
                gui.find('**/FndsLst_ScrollUp'),
                gui.find('**/FndsLst_ScrollDN'),
                gui.find('**/FndsLst_ScrollUp_Rllvr'),
                gui.find('**/FndsLst_ScrollUp')), None),
            ('decButton_relief', None, None),
            ('decButton_scale', (1.6, 1.6, 1.6), None),
            ('decButton_pos', (0.16, 0, 0.09), None),
            # Make the disabled button fade out
            ('decButton_image3_color', Vec4(0.7, 0.7, 0.7, 0.75), None),
            # itemFrame is a DirectFrame
            ('itemFrame_pos', (-0.025, 0, 0), None),
            ('itemFrame_scale', 0.54, None),
            ('itemFrame_relief', None, None),
            ('itemFrame_frameSize', (-0.05, 0.75, -0.75, 0.05), None),
            # each item is a button with text on it
            ('numItemsVisible', 10, None),
            ('items', [], None)
        )

        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectScrolledList.__init__(self, parent)
        self.initialiseoptions(FishPicker)

        self.fishGui = loader.loadModel('phase_3.5/models/gui/fishingBook').find('**/bucket')
        # We do not need the rod frame in this gui
        self.fishGui.find('**/fram1').removeNode()
        # Get rid of the bubble until we use it
        self.fishGui.find('**/bubble').removeNode()
        self.fishGui.reparentTo(self, -1)
        self.fishGui.setPos(0.63, 0.1, -0.1)
        self.fishGui.setScale(0.035)

        # fish value total
        self.info = DirectLabel(
            parent = self,
            relief = None,
            text = '',
            text_scale = 0.055,
            pos = (0.18, 0, -0.67)
        )

        self.fishPanel = FishPanel.FishPanel(parent = self, width = 1.0)
        # This is carefully placed over the book image.  Please try to keep
        # this in sync with the book position:
        # (tip: DistributedFishingSpot.py uses the same bounds
        # for its fish dialog.  OK, maybe they should pull
        # from the same variable; fix it if you like):
        self.fishPanel.setSwimBounds(-0.3, 0.3, -0.235, 0.25)
        # Parchment paper background:
        self.fishPanel.setSwimColor(1.0, 1.0, 0.74901, 1.0)

        gui.removeNode()

    def destroy(self):
        DirectScrolledList.destroy(self)
        self.fishList = []
        self.fishPanel = None

    def hideFishPanel(self):
        self.fishPanel.hide()

    def hide(self):
        if not hasattr(self, 'loaded'):
            return
        self.hideFishPanel()
        DirectScrolledList.hide(self)
        self.shown = 0

    def show(self):
        if not hasattr(self, 'loaded'):
            self.load()
        self.updatePanel()
        DirectScrolledList.show(self)
        self.shown = 1

    def load(self):
        self.loaded = 1
        # make the fish detail panel
        self.fishPanel.load()
        self.fishPanel.setPos(1.05, 0, 0.1)
        self.fishPanel.setScale(0.75)

    def update(self, newFishes):
        # Remove old buttons
        for fish, fishButton in self.fishList[:]:
            self.removeItem(fishButton)
            fishButton.destroy()
            self.fishList.remove([fish, fishButton])

        # Add new buttons
        for fish in newFishes:
            fishButton = self.makeFishButton(fish)
            self.addItem(fishButton)
            self.fishList.append([fish, fishButton])

        value = 0

        for fish in newFishes:
            value += fish.getValue()

        # TODO: route through Altis's booster/gumball multiplier system (toontown.gumball.GumballGlobals.applyBoosters)
        # once jellybean boosters are wired up; no multiplier applied for now.
        value = round(value)

        maxFish = base.localAvatar.getMaxFishTank()
        self.info['text'] = TTLocalizer.FishPickerTotalValue % (len(newFishes), maxFish, value)
        # if currently shown, reset panel
        if self.shown:
            self.updatePanel()

    def updatePanel(self):
        # If we have any fish at all, show the first one
        if len(self.fishList) >= 1:
            self.showFishPanel(self.fishList[0][0])
        else:
            self.hideFishPanel()

    def makeFishButton(self, fish):
        return DirectScrolledListItem(
            parent = self,
            relief = None,
            text = fish.getSpeciesName(),
            text_scale = 0.07,
            text_fg = FishGlobals.RarityColors.get(fish.getRarity()),
            text_style = 3,
            text_align = TextNode.ALeft,
            text1_fg = Vec4(1, 1, 0, 1),
            text2_fg = Vec4(0.5, 0.9, 1, 1),
            text3_fg = Vec4(0.4, 0.8, 0.4, 1),
            command = self.showFishPanel,
            extraArgs = [fish]
        )

    def showFishPanel(self, fish):
        self.fishPanel.update(fish)
        self.fishPanel.show()
