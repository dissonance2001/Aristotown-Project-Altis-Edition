from toontown.toonbase import ToontownGlobals
from direct.gui.DirectGui import *
from panda3d.core import *
from toontown.toonbase import TTLocalizer
from toontown.fishing import FishBase
from toontown.fishing import FishGlobals
from toontown.fishing import FishPhoto
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.text import getTextScaleAfterLength


@DirectNotifyCategory()
class GenusPanel(DirectFrame):
    """
    GenusPanel(DirectFrame)
    """

    # special methods
    def __init__(self, genus = None, itemIndex = 0, *extraArgs):
        """
        Create a DirectFrame for displaying the genus and it's species

        :param genus: an integer key into FishGlobals.__fishDict. Default=None
        :param itemIndex: an integer index into the item list (see optiondefs in FishBrowser). Default=0
        """
        fishingGui = loader.loadModel('phase_3.5/models/gui/fishingBook')
        albumGui = fishingGui.find('**/photo_frame1').copyTo(hidden)
        # The picture frame is in the wrong order, should be drawn first (at the back)
        albumGui.find('**/picture_frame').reparentTo(albumGui, -1)
        albumGui.find('**/arrows').removeNode()

        optiondefs = (
            ('relief', None, None),
            ('state', DGG.NORMAL, None),
            ('image', albumGui, None),
            ('image_scale', (0.025, 0.025, 0.025), None),
            ('image_pos', (0, 1, 0), None),
            ('text', TTLocalizer.UnknownFish, None),
            ('text_scale', 0.065, None),
            ('text_fg', (0.2, 0.1, 0.0, 1), None),
            ('text_pos', (-0.5, -0.34), None),
            ('text_font', ToontownGlobals.getInterfaceFont(), None),
            ('text_wordwrap', 13.5, None),
            ('text_align', TextNode.ALeft, None)
        )

        # Merge keyword options with default options
        self.defineoptions({}, optiondefs)

        # Initialize superclasses
        DirectFrame.__init__(self)
        self.initialiseoptions(GenusPanel)
        self.fishPanel = None
        self.genus = None
        self.setGenus(int(genus))
        self.setScale(1.2)
        albumGui.removeNode()

    def destroy(self):
        if self.fishPanel:
            self.fishPanel.destroy()
            del self.fishPanel
        DirectFrame.destroy(self)

    def load(self):
        pass

    def setGenus(self, genus):
        if self.genus == genus:
            return
        self.genus = genus
        if self.genus is not None:
            # load the genus image
            if self.fishPanel:
                self.fishPanel.destroy()
            f = FishBase.FishBase(self.genus, 0, 0)
            self.fishPanel = FishPhoto.FishPhoto(fish=f, parent=self)
            self.fishPanel.setPos(-0.23, 1, -0.01)

            # This is carefully placed over the book image.  Please try to keep
            # this in sync with the book position:
            self.fishPanel.setSwimBounds(-0.2461, 0.2367, -0.207, 0.2664)

            # Light blue-green water background:
            self.fishPanel.setSwimColor(0.47, 1.0, 0.99, 1.0)

            speciesList = FishGlobals.getSpecies(self.genus)
            self.speciesLabels = []
            self.weightLabels = []

            offset = 0.075
            startPos = len(speciesList) / 2 * offset
            if not len(speciesList) % 2:
                # even len's need a little shift down
                startPos -= offset / 2

            for species in range(len(speciesList)):
                speciesLabel = DirectLabel(
                    parent = self,
                    relief = None,
                    state = DGG.NORMAL,
                    pos = (0.06, 0, startPos - species * offset),
                    text = TTLocalizer.UnknownFish,
                    text_style = 3,
                    text_fg = FishGlobals.RarityColors.get(speciesList[species][FishGlobals.RARITY_INDEX]),
                    text_scale = TTLocalizer.GPgenus,
                    text_align = TextNode.ALeft,
                    text_font = ToontownGlobals.getInterfaceFont()
                )
                self.speciesLabels.append(speciesLabel)

                weightLabel = DirectLabel(
                    parent = self,
                    relief = None,
                    state = DGG.NORMAL,
                    pos = (0.06325, 0, startPos - species * offset - 0.0325),
                    text = '',
                    text_fg = (0, 0, 0, 1),
                    text_scale = TTLocalizer.GPweight,
                    text_align = TextNode.ALeft,
                    text_font = ToontownGlobals.getInterfaceFont()
                )
                self.weightLabels.append(weightLabel)

    def show(self):
        self.update()
        DirectFrame.show(self)

    def hide(self):
        if self.fishPanel is not None:
            self.fishPanel.hide()
        DirectFrame.hide(self)

    def update(self):
        if base.localAvatar.fishCollection.hasGenus(self.genus) and self.fishPanel is not None:
            self.fishPanel.show(showBackground=1)
            self['text'] = TTLocalizer.FishGenusNames[self.genus]

        for species in range(len(FishGlobals.getSpecies(self.genus))):
            theFish = base.localAvatar.fishCollection.hasFish(self.genus, species)
            if theFish:
                self.speciesLabels[species]['text'] = TTLocalizer.FishSpeciesNames[self.genus][species]
                scale = TTLocalizer.GPgenus
                xScale = getTextScaleAfterLength(self.speciesLabels[species]['text'], 21, modifier=0.0014, baseScale=scale)
                self.speciesLabels[species]['text_scale'] = (xScale, scale, scale)
                fishWeight = theFish.getWeight()

                conv = TTLocalizer.FishPageWeightConversion
                large = fishWeight / conv
                if large == 1:
                    largeStr = TTLocalizer.FishPageWeightLargeS % large
                else:
                    largeStr = TTLocalizer.FishPageWeightLargeP % large

                small = fishWeight % conv
                if small == 1:
                    smallStr = TTLocalizer.FishPageWeightSmallS % small
                else:
                    smallStr = TTLocalizer.FishPageWeightSmallP % small
                self.weightLabels[species]['text'] = TTLocalizer.FishPageWeight % largeStr + smallStr
