from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from panda3d.core import *

from toontown.gui.ScaledFrame import ScaledFrame
from toontown.toonbase import TTLocalizer
from toontown.fishing import FishGlobals
from toontown.fishing import FishPhoto
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
import math
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class FishPanel(ScaledFrame):
    """
    FishPanel(ScaledFrame)
    """

    def __init__(self, fish = None, parent = aspect2d, doneEvent = None, width=1.0, **kw):
        """
        Create a ScaledFrame for displaying the fish and it's info.
        """
        optiondefs = (
            ('relief', None, None),
            ('state', DGG.DISABLED, None),
            ('frameSize', (-width/2, width/2, -0.85/2, 0.85/2), None),
            ('text', '', None),
            ('text_scale', 0.06, None),
            ('text_fg', (0, 0, 0, 1), None),
            ('text_pos', (0, 0.35, 0), None),
            ('text_font', ToontownGlobals.getBuildingNametagFont(), None),
            ('text_wordwrap', 20, None)
        )

        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        ScaledFrame.__init__(self, parent)
        self.initialiseoptions(FishPanel)
        self['shadowStrength'] = 0.04
        self.width = width
        self.doneEvent = doneEvent
        self.fish = fish
        self.photo = None

    def destroy(self):
        if self.photo:
            self.photo.destroy()
            self.photo = None
        self.fish = None
        ScaledFrame.destroy(self)

    def load(self):
        # fish detail panel
        self.weight = DirectLabel(
            parent = self,
            pos = (0, 0, -0.28),
            relief = None,
            state = DGG.NORMAL,
            text = '',
            text_scale = 0.05,
            text_fg = (0, 0, 0, 1),
            text_pos = (0, 0.0, 0),
            text_font = ToontownGlobals.getInterfaceFont(),
            text_wordwrap = 15
        )

        self.value = DirectLabel(
            parent = self,
            pos = (0, 0, -0.35),
            relief = None,
            state = DGG.NORMAL,
            text = '',
            text_scale = 0.05,
            text_fg = (0, 0, 0, 1),
            text_pos = (0, 0, 0),
            text_font = ToontownGlobals.getInterfaceFont(),
            text_wordwrap = 15
        )

        self.rarity = DirectLabel(
            parent = self,
            pos = (0, 0, -0.42),
            relief = None,
            state = DGG.NORMAL,
            text = '',
            text_scale = 0.05,
            text_fg = (0, 0, 0, 1),
            text_pos = (0, 0, 0),
            text_font = ToontownGlobals.getInterfaceFont(),
            text_wordwrap = 15
        )

        self.mystery = DirectLabel(
            parent = self,
            pos = (-0.025, 0, -0.055),
            relief = None,
            state = DGG.NORMAL,
            text = '?', text_scale = 0.25,
            text_fg = (0, 0, 0, 1),
            text_pos = (0, 0, 0),
            text_font = ToontownGlobals.getInterfaceFont(),
            text_wordwrap = 15
        )

        self.extraLabel = DirectLabel(
            parent = self,
            relief = None,
            state = DGG.NORMAL,
            text = '',
            text_fg = (0.2, 0.8, 0.4, 1),
            text_font = ToontownGlobals.getSignFont(),
            text_scale = 0.08,
            pos = (0, 0, 0.26)
        )

        buttons = loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')

        # fish detail close button
        self.cancel = DirectButton(
            parent = self,
            pos = (self.width - 0.575, 0, -0.375),
            relief = None,
            state = DGG.NORMAL,
            image = (
                buttons.find('**/CloseBtn_UP'),
                buttons.find('**/CloseBtn_DN'),
                buttons.find('**/CloseBtn_Rllvr')
            ),
            image_scale = (0.6, 1, 0.6),
            command = self.handleCancel
        )
        buttons.removeNode()
        self.photo = FishPhoto.FishPhoto(parent=self)
        # make the scroll list
        self.update(self.fish)

    def update(self, fish):
        self.fish = fish
        if self.fish is None:
            return
        # pop up a little doober
        self['text'] = self.fish.getSpeciesName()
        weight = self.fish.getWeight()
        rarity = self.fish.getRarity()
        self['text_fg'] = FishGlobals.RarityColors.get(rarity)
        self.rarity['text'] = TTLocalizer.FishPageRarity % TTLocalizer.RarityToString.get(rarity)
        conv = TTLocalizer.FishPageWeightConversion

        large = weight / conv
        if large == 1:
            largeStr = TTLocalizer.FishPageWeightLargeS % large
        else:
            largeStr = TTLocalizer.FishPageWeightLargeP % large
        small = weight % conv
        if small == 1:
            smallStr = TTLocalizer.FishPageWeightSmallS % small
        else:
            smallStr = TTLocalizer.FishPageWeightSmallP % small
        self.weight['text'] = TTLocalizer.FishPageWeightStr + largeStr + smallStr
        # TODO: route through Altis's booster/gumball multiplier system (toontown.gumball.GumballGlobals.applyBoosters)
        # once jellybean boosters are wired up; no multiplier applied for now.
        value = round(self.fish.getValue())
        if value == 1:
            self.value['text'] = TTLocalizer.FishPageValueS % value
        else:
            self.value['text'] = TTLocalizer.FishPageValueP % value
        self.photo.update(fish)

    def setSwimBounds(self, *bounds):
        """
        :param bounds: floats: left, right, top, bottom
        """
        self.swimBounds = bounds

    def setSwimColor(self, *colors):
        """
        :param colors: floats: red, green, blue, alpha
        """
        self.swimColor = colors

    def handleCancel(self):
        self.hide()
        if self.doneEvent:
            messenger.send(self.doneEvent)

    def show(self, code = FishGlobals.FishItem):
        # if we are browsing fish we must be awake
        messenger.send('wakeup')
        self.photo.setSwimBounds(*self.swimBounds)
        self.photo.setSwimColor(*VBase4(0.9843, 0.9843, 0.7373, 1))

        if code == FishGlobals.FishItem:
            self.extraLabel.hide()
        elif code == FishGlobals.FishItemNewEntry:
            self.extraLabel.show()
            self.extraLabel['text'] = TTLocalizer.FishingNewEntry
            self.extraLabel['text_scale'] = TTLocalizer.FPnewEntry
            self.extraLabel.setPos(0, 0, 0.26)
        elif code == FishGlobals.FishItemNewRecord:
            self.extraLabel.show()
            self.extraLabel['text'] = TTLocalizer.FishingNewRecord
            self.extraLabel['text_scale'] = TTLocalizer.FPnewRecord
            self.extraLabel['text_fg'] = (0.25, 0.35, 1.0, 1.0)

        self.photo.show()
        ScaledFrame.show(self)

    def hide(self):
        self.photo.hide()
        ScaledFrame.hide(self)
