"""FishBrowser module: contains the FishBrowser class"""

from direct.gui.DirectGui import *
from panda3d.core import *
from toontown.fishing import GenusPanel
from toontown.fishing import FishGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class FishBrowser(DirectScrolledList):
    """
    FishBrowser(DirectScrolledList)

    This is the class that handles the photo album view of the kinds of fish the toon has collected.

    The tab on the FishPage is "Album".
    """

    # special methods
    def __init__(self, parent = aspect2d, **kw):
        """
        FishBrowser constructor: create a scrolling list of fish
        """
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
            ('incButton_scale', (1.3, 1.3, -1.3), None),
            ('incButton_pos', (0, 0, -0.525), None),
            # Make the disabled button fade out
            ('incButton_image3_color', Vec4(0.8, 0.8, 0.8, 0.5), None),
            ('decButton_image', (
                gui.find('**/FndsLst_ScrollUp'),
                gui.find('**/FndsLst_ScrollDN'),
                gui.find('**/FndsLst_ScrollUp_Rllvr'),
                gui.find('**/FndsLst_ScrollUp')), None),
            ('decButton_relief', None, None),
            ('decButton_scale', (1.3, 1.3, 1.3), None),
            ('decButton_pos', (0, 0, 0.525), None),
            # Make the disabled button fade out
            ('decButton_image3_color', Vec4(0.8, 0.8, 0.8, 0.5), None),
            ('numItemsVisible', 1, None),
            ('items', list(map(str, FishGlobals.getGenera())), None),
            ('scrollSpeed', 4, None),
            ('itemMakeFunction', GenusPanel.GenusPanel, None),
            ('itemMakeExtraArgs', None, None)
        )
        gui.removeNode()

        # Merge keyword options with default options
        self.defineoptions(kw, optiondefs)

        # Initialize superclasses
        DirectScrolledList.__init__(self, parent)
        self.initialiseoptions(FishBrowser)

    def destroy(self):
        DirectScrolledList.destroy(self)

    def update(self):
        pass

    def show(self):
        if not self.parent.isHidden():
            self['items'][self.index].show()
            DirectScrolledList.show(self)

    def hide(self):
        self['items'][self.index].hide()
        DirectScrolledList.hide(self)
