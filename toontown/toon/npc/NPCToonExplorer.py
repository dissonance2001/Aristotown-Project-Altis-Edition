from toontown.toon import Toon
from toontown.toon import ToonDNA
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.gui.DirectGui import *
from panda3d.core import *
from toontown.menu.MainMenuGui import MainMenuButton
from toontown.toon.npc import NPCToons
from toontown.utils.text import getTextScaleAfterLength
from toontown.toonbase import TTLocalizer

from toontown.toon.npc.NPCToonConstants import NPCToonEnum as NPC

# Page Vars
itemFrameXorigin = -0.237
itemFrameZorigin = 0.365
buttonXstart = itemFrameXorigin + 0.293
listXorigin = -0.02
listFrameSizeX = 0.67
listZorigin = -0.96
listFrameSizeZ = 1.04
title_text_scale = 0.12
arrowButtonScale = 1.3
rightSideItemsX = 0.36
textRolloverColor = Vec4(1, 1, 0, 1)
textDownColor = Vec4(0.5, 0.9, 1, 1)
textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)


@DirectNotifyCategory()
class NPCToonExplorer(DirectFrame):
    """
    NPCToonExplorer(DirectFrame)

    Developer tool to view all of the NPCs in the game and modify some attributes.

    Provides an option to print out the NPCToon's data that was modified using this tool.

    todo: Option to edit more attributes, such as the toon species and body types
    """


    def __init__(self, parent = base.aspect2d, solo = False):
        self.notify.debug("__init__()")
        self.solo = solo

        self.textColor = Vec4(0, 0, 0, 1)
        frameScale = (1.75, 1, 1.5)
        geom = DGG.getDefaultDialogGeom()
        if self.solo:
            self.textColor = Vec4(1, 1, 1, 1)
            bgColor = (0.15, 0.15, 0.15)
            frameScale = (3.75, 3.0, 3.5)
            geom = None
            base.setBackgroundColor(bgColor)

        DirectFrame.__init__(
            self,
            parent = parent,
            relief = None,
            geom = geom,
            geom_scale = frameScale,
        )
        """
        :param bool solo: If we're running outside of a normal client (see bottom of this file)
        This dictates certain placements and loaded GUI.
        """
        DirectFrame.initialiseoptions(self, NPCToonExplorer)

        self.title = None  # DirectLabel that is instantiated in load(), gives us the "NPC Toons" text on the top.
        self.editMode = [0]  # The Toon attribute we are editing (check the dna/accessory functions below)

        # Left Page Vars
        self.NPCToonPanelList = None  # DirectScrolledList that is instantiated in load()
        self.NPCFrames = {}  # Contains DirectFrame info for each and every loaded NPC in the menu.
        self.npcSelected = None  # Holds the currently selected NPC's ID.

        # "Toon" object of our NPC
        self.NPCAvatarToon = None  # type: Toon.Toon

        self.DNAString = None  # Allow us to transform into the NPC

        self.NPCToons = NPCToons  # NOT the NPCToon class, just the module here!
        self.NPCToonsList = NPCToons.NPCToonDict
        self.defaultColors = ToonDNA.defaultColorList

        # "[{topTex}, {topTexColor}] [{sleeveTex}, {sleeveTexColor}] [{botTex}, {botTexColor}]"
        self.npcDNA = ""

        # "{hat}, {backpack}, {glasses}, {shoes}"
        self.npcAccessory = ""

        # This is used for printing out the modified NPC data for convenience purposes.
        self.NPCToonItem = {
            "npcID": 0,  # npcID
            "NPCToonObject": [
                None,  # INTERIOR ZoneID
                None,  # name key, will be used for names[x]
                None,  # head type
                None,  # body type
                None,  # leg type
                None,  # internal gender
                None,  # armColor
                None,  # legColor
                None,  # headColor
                None,  # topTex
                None,  # topColor
                None,  # sleeveTex
                None,  # sleeveColor
                None,  # botTex
                None,  # botColor
                None,  # npcType (this has constants so it must be represented as a string)
                None,  # hat (extra arg)
                None,  # hatColor (extra arg)
                None,  # glasses (extra arg
                None,  # glassesColor
                None,  # backpack
                None,  # backpackColor
                None,  # shoes
                None,  # shoesTex
                None,  # ce
                None,  # animation
                None,  # animationSpeed
                None,  # tag
                None,  # pos
                None,  # earColor
                None,  # eyeColor
                None,  # gloveColor
                None, # holidayIds

            ]
        }

        self.load()

    def load(self):
        gui = loader.loadModel("phase_3/models/gui/ttcc_menu_buttons")
        friendsGui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        buttons = loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')
        eraserGui = loader.loadModel('phase_3.5/models/gui/optionspage/keybinds_gui.bam')
        self.title = DirectLabel(
            parent = self,
            relief = None,
            text = 'NPC Toons',
            text_scale = title_text_scale,
            text_fg = self.textColor,
            textMayChange = 0,
            pos = (0, 0, 0.65)
        )

        # Left Page
        self.NPCToonPanelList = DirectScrolledList(
            parent = self,
            relief = None,
            pos = (-0.5, 0, 0),
            itemFrame_pos = (itemFrameXorigin, 0, itemFrameZorigin),
            itemFrame_scale = 1.0, itemFrame_relief = DGG.SUNKEN,
            itemFrame_frameSize = (
                listXorigin, listXorigin + listFrameSizeX,
                listZorigin,
                listZorigin + listFrameSizeZ
            ),
            itemFrame_frameColor = (0.85, 0.95, 1, 1),
            itemFrame_borderWidth = (0.01, 0.01),
            numItemsVisible = 15,
            forceHeight = 0.065,
            incButton_image = (
                friendsGui.find('**/FndsLst_ScrollUp'),
                friendsGui.find('**/FndsLst_ScrollDN'),
                friendsGui.find('**/FndsLst_ScrollUp_Rllvr'),
                friendsGui.find('**/FndsLst_ScrollUp')
            ),
            incButton_relief = None,
            incButton_scale = (arrowButtonScale, arrowButtonScale, -arrowButtonScale),
            incButton_pos = (buttonXstart, 0, itemFrameZorigin - 0.999),
            incButton_image3_color = Vec4(1, 1, 1, 0.2),
            decButton_image = (
                friendsGui.find('**/FndsLst_ScrollUp'),
                friendsGui.find('**/FndsLst_ScrollDN'),
                friendsGui.find('**/FndsLst_ScrollUp_Rllvr'),
                friendsGui.find('**/FndsLst_ScrollUp')
            ),
            decButton_relief = None,
            decButton_scale = (arrowButtonScale, arrowButtonScale, arrowButtonScale),
            decButton_pos = (buttonXstart, 0, itemFrameZorigin + 0.125),
            decButton_image3_color = Vec4(1, 1, 1, 0.2)
        )
        self['state'] = DGG.NORMAL
        self.bind(DGG.WHEEL_UP, lambda _: self.scroll(1), [])
        self.bind(DGG.WHEEL_DOWN, lambda _: self.scroll(-1), [])
        self.NPCToonPanelList.bind(DGG.WHEEL_UP, lambda _: self.scroll(1), [])
        self.NPCToonPanelList.bind(DGG.WHEEL_DOWN, lambda _: self.scroll(-1), [])
        self.NPCToonPanelList.incButton.bind(DGG.WHEEL_UP, lambda _: self.scroll(1), [])
        self.NPCToonPanelList.incButton.bind(DGG.WHEEL_DOWN, lambda _: self.scroll(-1), [])
        self.NPCToonPanelList.decButton.bind(DGG.WHEEL_UP, lambda _: self.scroll(1), [])
        self.NPCToonPanelList.decButton.bind(DGG.WHEEL_DOWN, lambda _: self.scroll(-1), [])

        # Right Page
        self.selectednpcID = DirectLabel(
            parent = self,
            relief = None,
            text = '',
            text_align = TextNode.ACenter,
            text_scale = 0.08,
            text_fg = self.textColor,
            textMayChange = 1,
            pos = (rightSideItemsX, 0, 0.39)
        )

        self.selectednpcZone = DirectLabel(
            parent = self,
            relief = None,
            text = "",
            text_align = TextNode.ACenter,
            text_scale = 0.05,
            text_fg = self.textColor,
            textMayChange = 1,
            pos = (rightSideItemsX, 0, 0.3),
            text_wordwrap = 18
        )

        self.DNAValueText = DirectLabel(
            parent = self,
            relief = None, text = '',
            text_align = TextNode.ACenter,
            text_scale = 0.042,
            text_fg = self.textColor,
            textMayChange = 1,
            pos = (rightSideItemsX, 0, -0.465)
        )

        self.AccValueText = DirectLabel(
            parent = self,
            relief = None,
            text = '',
            text_align = TextNode.ACenter,
            text_scale = 0.042,
            text_fg = self.textColor,
            textMayChange = 1,
            pos = (rightSideItemsX, 0, -0.51)
        )

        if not self.solo:
            self.exitButton = DirectButton(
                parent = self,
                relief = None,
                scale = 1.55,
                text = ('', 'Exit', 'Exit'),
                text_align = TextNode.ACenter,
                text_scale = 0.075,
                text_shadow = Vec4(0, 0, 0, 1),
                text_pos = (-0.0125, -0.09),
                pos = (0.79, 0, 0.7),
                textMayChange = 0,
                image = (
                    buttons.find('**/CloseBtn_UP'),
                    buttons.find('**/CloseBtn_DN'),
                    buttons.find('**/CloseBtn_Rllvr')
                ),
                command = self.destroy
            )

        self.printButton = DirectButton(
            parent = self,
            relief = None,
            scale = 1.55, text = ('', 'Print', 'Print'),
            text_align = TextNode.ACenter,
            text_scale = 0.075,
            text_fg = self.textColor,
            text_shadow = Vec4(0, 0, 0, 1),
            text_pos = (-0.0125, -0.09),
            pos = (0.50, 0, 0.7),
            textMayChange = 0,
            image = (buttons.find('**/ChtBx_OKBtn_UP'),
                     buttons.find('**/ChtBx_OKBtn_DN'),
                     buttons.find('**/ChtBx_OKBtn_Rllvr')),
            command = self.printFormat
        )

        self.searchBar = DirectEntry(
            parent = self,
            relief = DGG.SUNKEN,
            initialText = TTLocalizer.FriendsListSearchBarDefaultText,
            scale = 0.07,
            pos = (-0.74, 0, -0.7625),
            width = 9,
            numLines = 1,
            focus = 0,
            cursorKeys = 1,
            command = self.finishSearch
        )
        self.searchBar.bind(DGG.B1PRESS, self.updateSearch)

        self.eraser = DirectButton(
            parent = self,
            pos = (-0.02, 0, -0.74),
            image = eraserGui.find('**/eraser'),
            scale = (0.6, 1, 0.32),
            relief = None,
            frameSize = (0.1, -0.085, 0.175, -0.175),
            command = self.resetSearch
        )

        self.toonPreview = DirectFrame(
            pos = (rightSideItemsX, 0, -0.1),
            scale = (1.5, 1.5, 1.5),
            parent = self
        )

        self.editDnaInc = DirectButton(
            parent = self,
            relief = None,
            scale = (0.5, 1, 1), pos = (rightSideItemsX + 0.3, 0, 0.1),
            hpr = (0, 0, 90),
            image = (
                friendsGui.find('**/FndsLst_ScrollUp'),
                friendsGui.find('**/FndsLst_ScrollDN'),
                friendsGui.find('**/FndsLst_ScrollUp_Rllvr'),
                friendsGui.find('**/FndsLst_ScrollUp')
            ),
            command = self.updateDNA,
            extraArgs = [1]
        )

        self.editDnaDec = DirectButton(
            parent = self,
            relief = None,
            scale = (0.5, 1, 1),
            pos = (rightSideItemsX - 0.3, 0, 0.1),
            hpr = (0, 0, -90),
            image = (
                friendsGui.find('**/FndsLst_ScrollUp'),
                friendsGui.find('**/FndsLst_ScrollDN'),
                friendsGui.find('**/FndsLst_ScrollUp_Rllvr'),
                friendsGui.find('**/FndsLst_ScrollUp')
            ),
            command = self.updateDNA,
            extraArgs = [-1]
        )

        self.editDnaColorInc = DirectButton(
            parent = self,
            relief = None,
            scale = (0.5, 1, 1),
            pos = (rightSideItemsX + 0.3, 0, -0.1),
            hpr = (0, 0, 90),
            image = (
                friendsGui.find('**/FndsLst_ScrollUp'),
                friendsGui.find('**/FndsLst_ScrollDN'),
                friendsGui.find('**/FndsLst_ScrollUp_Rllvr'),
                friendsGui.find('**/FndsLst_ScrollUp')
            ),
            command = self.updateDNAColor,
            extraArgs = [1]
        )

        self.editDnaColorDec = DirectButton(
            parent = self, relief = None, scale = (0.5, 1, 1),
            pos = (rightSideItemsX - 0.3, 0, -0.1),
            hpr = (0, 0, -90),
            image = (
                friendsGui.find('**/FndsLst_ScrollUp'),
                friendsGui.find('**/FndsLst_ScrollDN'),
                friendsGui.find('**/FndsLst_ScrollUp_Rllvr'),
                friendsGui.find('**/FndsLst_ScrollUp')
            ),
            command = self.updateDNAColor,
            extraArgs = [-1]
        )

        self.editModeButtons = [
            DirectRadioButton(parent = self, text = 'Shirt', variable = self.editMode, value = [0],
                              scale = 0.055, pos = (rightSideItemsX - 0.072, 0, -0.6)),
            DirectRadioButton(parent = self, text = 'Sleeve', variable = self.editMode, value = [1],
                              scale = 0.055, pos = (rightSideItemsX - 0.072, 0, -0.67)),
            DirectRadioButton(parent = self, text = 'Bottoms', variable = self.editMode, value = [2],
                              scale = 0.055, pos = (rightSideItemsX - 0.072, 0, -0.74)),
            DirectRadioButton(parent = self, text = 'Hat', variable = self.editMode, value = [3],
                              scale = 0.055, pos = (rightSideItemsX + 0.17, 0, -0.6)),
            DirectRadioButton(parent = self, text = 'Glasses', variable = self.editMode, value = [4],
                              scale = 0.055, pos = (rightSideItemsX + 0.17, 0, -0.67)),
            DirectRadioButton(parent = self, text = 'Backpack', variable = self.editMode, value = [5],
                              scale = 0.055, pos = (rightSideItemsX + 0.17, 0, -0.74)),
            DirectRadioButton(parent = self, text = 'Shoes', variable = self.editMode, value = [6],
                              scale = 0.055, pos = (rightSideItemsX + 0.17, 0, -0.81))
        ]
        for button in self.editModeButtons:
            button.setOthers(self.editModeButtons)
            button.hide()

        if not self.solo:
            self.transformNPCButton = DirectButton(
                parent = self,
                relief = None,
                scale = (0.1),
                text = "Transform!",
                pos = (rightSideItemsX + 0.17, 0, -0.9),
                text_align = TextNode.ACenter,
                text_fg = self.textColor,
                text_style = 3,
                command = self.transformIntoNPC
            )
            self.transformNPCButton.hide()

        self.NPCToonSlider = DirectSlider(
            parent = self,
            pos = (0, 0, 0.58),
            value = 0,
            range = (-180, 180),
            pageSize = 1,
            scale = (.3, 1, .3),
            frameColor = (181. / 255., 88. / 255., 1. / 255., 1),
            orientation = DGG.HORIZONTAL,
            thumb_relief = None,
            thumb_geom = loader.loadModel("phase_3/models/gui/ttcc_gui_generic").find("**/gui_slider_thumb"),
            thumb_geom_scale = (.2, .2, .2),
            command = self.rotateNPC
        )

        self.editDnaInc.hide()
        self.editDnaDec.hide()
        self.editDnaColorInc.hide()
        self.editDnaColorDec.hide()
        self.NPCToonSlider.hide()

        gui.removeNode()
        friendsGui.removeNode()
        buttons.removeNode()
        eraserGui.removeNode()

        for npcID in list(self.NPCToonsList.keys()):  # spits out the npc ids
            npcButton = self.createNPCButton(npcID)
            self.NPCToonPanelList.addItem(npcButton)

        # Disable sleeping because we're busy looking at all the cool NPCs
        if hasattr(base, 'localAvatar') and base.localAvatar is not None:
            if not base.localAvatar.neverSleep:
                base.localAvatar.disableSleeping()

    def rotateNPC(self):
        if self.NPCAvatarToon is not None:
            self.NPCAvatarToon.getGeomNode().setH(int(self.NPCToonSlider['value']))

    def scroll(self, amount):
        self.NPCToonPanelList.scrollTo(self.NPCToonPanelList.index - amount)

    def updateSearch(self, _ = None):
        if not self.solo:
            base.localAvatar.lockControlsForEntry()
        # Lets remove the search prompt if it's there
        if self.searchBar.get() == TTLocalizer.FriendsListSearchBarDefaultText:
            self.searchBar.set('')

    def finishSearch(self, _ = None):
        # Unfocus the search bar just in case it is focused when we are entering
        self.searchBar['focus'] = 0
        if not self.solo:
            base.localAvatar.unlockControlsForEntry()
        self.__updateAll(self.searchBar.get())

    def __updateAll(self, searchedText = ""):
        self.__removeAllInList()
        for npcID, NPCTuple in list(self.NPCFrames.items()):
            if self.NPCToons.getNPCName(npcID).lower().replace(" ", "").find(searchedText.lower().replace(" ", "")) != -1 and NPCTuple[0] not in self.NPCToonPanelList['items']:
                self.NPCToonPanelList.addItem(NPCTuple[0], refresh = 0)
                NPCTuple[0].show()
        self.NPCToonPanelList.refresh()

    def __removeAllInList(self):
        for npcs in list(self.NPCFrames.values()):
            npcs[0].hide()
            self.NPCToonPanelList.removeItem(npcs[0], refresh = 0)
        self.NPCToonPanelList.refresh()

    def __showAllInList(self):
        for npcs in self.NPCFrames:
            if npcs[0] not in self.NPCToonPanelList['items']:
                self.NPCToonPanelList.addItem(npcs[0], refresh = 0)
            NPCTuple[0].show()
        self.NPCToonPanelList.refresh()

    def resetSearch(self):
        self.searchBar.set('')
        self.finishSearch()
        self.searchBar.set(TTLocalizer.FriendsListSearchBarDefaultText)

    def destroy(self):
        if hasattr(self, 'toonPreview'):
            del self.toonPreview

        if hasattr(base, 'localAvatar'):
            if base.localAvatar.neverSleep:
                base.localAvatar.enableSleeping()

        self.finishSearch()
        del self.NPCFrames
        DirectFrame.destroy(self)

    """
    Left Page
    All of these methods handle the left hand side of the page.
    This includes
    - Updating the list
    - Handling command select events
    """

    def createNPCButton(self, npcID):
        """
        Generates a button for an NPC
        """
        # Generate the buttons
        NPCButtonFrame = DirectFrame()
        NPCToonName = DirectButton(
            parent = NPCButtonFrame,
            relief = None,
            text = self.NPCToons.getNPCName(npcID),
            text_scale = 0.06,
            text_align = TextNode.ALeft,
            text1_bg = textDownColor,
            text2_bg = textRolloverColor,
            text3_fg = textDisabledColor,
            textMayChange = 1,
            command = self.selectNPC,
            extraArgs = [npcID]
        )
        NPCToonName.bind(DGG.WHEEL_UP, lambda _: self.scroll(1), [])
        NPCToonName.bind(DGG.WHEEL_DOWN, lambda _: self.scroll(-1), [])

        # Now get it ready for the big return
        NPCTuple = (NPCButtonFrame, NPCToonName)
        self.NPCFrames[npcID] = NPCTuple
        return NPCButtonFrame

    def updateNPCType(self, npcID, selected):
        """
        Updates the provided shard button state
        """
        buttons = self.NPCFrames[npcID]
        if selected:
            state = DGG.DISABLED
        else:
            state = DGG.NORMAL
        buttons[0]['state'] = state
        buttons[1]['state'] = state

    def selectNPC(self, npcID):
        """
        Updates both the left and the right page to display the selected NPC information.
        """
        self.editDnaInc.show()
        self.editDnaDec.show()
        self.NPCToonSlider.show()
        if not self.solo:
            self.transformNPCButton.show()

        for button in self.editModeButtons:
            button.show()
        self.editDnaColorInc.show()
        self.editDnaColorDec.show()

        if self.npcSelected:  # Enable the currently disabled button
            self.updateNPCType(self.npcSelected, False)

        # Update the scroll list (Left Page)
        self.updateNPCType(npcID, True)
        self.npcSelected = npcID

        # Update the Right Page
        self.updateNPCPanelInformation(npcID)

    """
    Right Page
    Handles the right hand side of the page, who would have guessed...
    This includes
    - Updating the Command title.
    - Updating the "Say it" button.
    """

    def updateDNA(self, index):
        if self.NPCAvatarToon is None:
            return
        if self.editMode[0] == 0:  # Shirt / TopTex
            changetexID = self.rotateUnorderedIndex(self.NPCAvatarToon.style.topTex + index, ToonDNA.Shirts)
            self.NPCAvatarToon.setTop(changetexID, self.NPCAvatarToon.style.topTexColor)
            self.fillNPCObject(10, str(changetexID))
        elif self.editMode[0] == 1:  # Sleeve
            changetexID = self.rotateUnorderedIndex(self.NPCAvatarToon.style.sleeveTex + index, ToonDNA.Sleeves)
            self.NPCAvatarToon.setSleeve(changetexID, self.NPCAvatarToon.style.sleeveTexColor)
            self.fillNPCObject(12, str(changetexID))
        elif self.editMode[0] == 2:  # Bottom / botTex
            changetexID = self.rotateUnorderedIndex(self.NPCAvatarToon.style.botTex + index, ToonDNA.Bottoms)
            self.NPCAvatarToon.setBottom(changetexID, self.NPCAvatarToon.style.botTexColor)
            self.fillNPCObject(14, str(changetexID))
        else:
            self.updateAccessory(index)
            return
        self.refreshClothingIDs()

    def updateDNAColor(self, index):
        color = len(self.defaultColors)
        if self.NPCAvatarToon is None:
            return
        if self.editMode[0] == 0:  # ShirtColor
            changedColorID = self.rotateIndex(self.NPCAvatarToon.style.topTexColor + index, color)
            self.NPCAvatarToon.setTop(self.NPCAvatarToon.style.topTex, changedColorID)
            self.fillNPCObject(11, str(changedColorID))
        elif self.editMode[0] == 1:  # SleeveColor
            changedColorID = self.rotateIndex(self.NPCAvatarToon.style.sleeveTexColor + index, color)
            self.NPCAvatarToon.setSleeve(self.NPCAvatarToon.style.sleeveTex, changedColorID)
            self.fillNPCObject(13, str(changedColorID))
        elif self.editMode[0] == 2:  # BottomColor
            changedColorID = self.rotateIndex(self.NPCAvatarToon.style.botTexColor + index, color)
            self.NPCAvatarToon.setBottom(self.NPCAvatarToon.style.botTex, changedColorID)
            self.fillNPCObject(15, str(changedColorID))
        else:
            self.updateAccessoryStyle(index)
            return
        self.refreshClothingIDs()

    def updateAccessory(self, index):
        """
        changeAccID[0], changeAccID[1], changeAccID[2]
        0 --> model
        1 --> texture
        2 --> aux (should be for shoes)
        """
        if self.NPCAvatarToon is None:
            return
        if self.editMode[0] == 3:  # HatModels
            currAccID = self.NPCAvatarToon.getHat()
            changeAccID = [currAccID[0] + index, currAccID[1], currAccID[2]]  # Use a list instead of a tuple
            changeAccID[0] = self.rotateIndex(changeAccID[0], len(ToonDNA.HatModels))
            self.NPCAvatarToon.setHat(changeAccID[0], changeAccID[1], changeAccID[2])  # We can't just pass a tuple here
            if changeAccID[0] != 0:
                self.fillNPCObject(16, "hat=%s" % str(changeAccID[0]))
            else:
                self.fillNPCObject(16, None)

        elif self.editMode[0] == 4:  # GlassesModels
            currAccID = self.NPCAvatarToon.getGlasses()
            changeAccID = [currAccID[0] + index, currAccID[1], currAccID[2]]
            changeAccID[0] = self.rotateIndex(changeAccID[0], len(ToonDNA.GlassesModels))
            self.NPCAvatarToon.setGlasses(changeAccID[0], changeAccID[1], changeAccID[2])
            if changeAccID[0] != 0:
                self.fillNPCObject(18, "glasses=%s" % str(changeAccID[0]))
            else:
                self.fillNPCObject(18, None)

        elif self.editMode[0] == 5:  # BackpackModels
            currAccID = self.NPCAvatarToon.getBackpack()
            changeAccID = [currAccID[0] + index, currAccID[1], currAccID[2]]
            changeAccID[0] = self.rotateIndex(changeAccID[0], len(ToonDNA.BackpackModels))
            self.NPCAvatarToon.setBackpack(changeAccID[0], changeAccID[1], changeAccID[2])
            if changeAccID[0] != 0:
                self.fillNPCObject(20, "backpack=%s" % str(changeAccID[0]))
            else:
                self.fillNPCObject(20, None)


        elif self.editMode[0] == 6:  # ShoesModels
            currAccID = self.NPCAvatarToon.getShoes()
            changeAccID = [currAccID[0] + index, currAccID[1], currAccID[2]]
            changeAccID[0] = self.rotateIndex(changeAccID[0], len(ToonDNA.ShoesModels))
            self.NPCAvatarToon.setShoes(changeAccID[0], changeAccID[1], changeAccID[2])
            if changeAccID[0] != 0:
                self.fillNPCObject(22, "shoes=%s" % str(changeAccID[0]))
            else:
                self.fillNPCObject(22, None)

        self.refreshClothingIDs()

    def updateAccessoryStyle(self, index):
        if self.NPCAvatarToon is None:
            return
        if self.editMode[0] == 3:  # HatTextures
            currAccID = self.NPCAvatarToon.getHat()
            changeAccID = [currAccID[0], currAccID[1] + index, currAccID[2]]  # Use a list instead of a tuple
            changeAccID[1] = self.rotateIndex(changeAccID[1], len(ToonDNA.HatTextures))
            self.NPCAvatarToon.setHat(changeAccID[0], changeAccID[1], changeAccID[2])  # We can't just pass a tuple here
            if changeAccID[1] != 0:
                self.fillNPCObject(17, "hatColor=%s" % str(changeAccID[1]))
            else:
                self.fillNPCObject(17, None)

        elif self.editMode[0] == 4:  # GlassesTextures
            currAccID = self.NPCAvatarToon.getGlasses()
            changeAccID = [currAccID[0], currAccID[1] + index, currAccID[2]]
            changeAccID[1] = self.rotateIndex(changeAccID[1], len(ToonDNA.GlassesTextures))
            self.NPCAvatarToon.setGlasses(changeAccID[0], changeAccID[1], changeAccID[2])
            if changeAccID[1] != 0:
                self.fillNPCObject(19, "glassesColor=%s" % str(changeAccID[1]))
            else:
                self.fillNPCObject(19, None)

        elif self.editMode[0] == 5:  # BackpackTextures
            currAccID = self.NPCAvatarToon.getBackpack()
            changeAccID = [currAccID[0], currAccID[1] + index, currAccID[2]]
            changeAccID[1] = self.rotateIndex(changeAccID[1], len(ToonDNA.BackpackTextures))
            self.NPCAvatarToon.setBackpack(changeAccID[0], changeAccID[1], changeAccID[2])
            if changeAccID[1] != 0:
                self.fillNPCObject(21, "backpackColor=%s" % str(changeAccID[1]))
            else:
                self.fillNPCObject(21, None)

        elif self.editMode[0] == 6:  # ShoesTextures
            currAccID = self.NPCAvatarToon.getShoes()
            changeAccID = [currAccID[0], currAccID[1] + index, currAccID[2]]
            changeAccID[1] = self.rotateIndex(changeAccID[1], len(ToonDNA.ShoesTextures))
            self.NPCAvatarToon.setShoes(changeAccID[0], changeAccID[1], changeAccID[2])
            if changeAccID[1] != 0:
                self.fillNPCObject(23, "shoesTex=%s" % str(changeAccID[1]))
            else:
                self.fillNPCObject(23, None)

        self.refreshClothingIDs()

    def rotateIndex(self, newIndex, listSize):
        """
        Used if ids/index match the length of the dict (ex: accessories)
        """
        if newIndex < 0:
            newIndex = listSize - 1
            return newIndex
        elif newIndex >= listSize:
            newIndex = 0
            return newIndex
        return newIndex

    def rotateUnorderedIndex(self, newIndex, dict):
        """
        Used if the ids/index don't match up with the actual length of the dict (ex: clothing)

        Empty values will just give us white clothing (do not use them though)
        """
        minimum = min(dict.keys())
        maximum = max(dict.keys())
        if newIndex < minimum:
            newIndex = maximum
            return newIndex
        elif newIndex >= maximum:
            newIndex = minimum
            return newIndex
        return newIndex

    def updateNPCPanelInformation(self, npcID):
        """
        Updates the information on the right page.
        """
        self.selectednpcID['text'] = self.NPCToons.getNPCName(npcID)

        self.NPCToonItem["npcID"] = npcID

        npcZone = self.NPCToons.getNPCZone(npcID)

        npcType = self.NPCToons.getNPCType(npcID)
        buildingArticle = self.NPCToons.getBuildingArticle(npcZone)
        buildingName = self.NPCToons.getBuildingTitle(npcZone)

        self.selectedNPC = self.NPCToonsList.get(npcID)  # type: NPCToons
        npcDNA = self.selectedNPC.getToonDNA()  # get raw DNA; type: ToonDNA

        if self.NPCAvatarToon is not None:
            self.NPCAvatarToon.cleanup()

        self.NPCAvatarToon = self.generateToon(npcDNA)  # type: Toon

        if self.NPCAvatarToon is not None:
            self.notify.debug("We were able to spawn {}".format(self.NPCToons.getNPCName((npcID))))
            self.NPCAvatarToon.reparentTo(self.toonPreview)
        else:
            self.notify.warning("Something is wrong, could not generate a toon")

        # Accessories aren't officially part of ToonDNA yet so we'll have to grab them individually
        hat = self.selectedNPC.hat
        hatColor = self.selectedNPC.hatColor
        glasses = self.selectedNPC.glasses
        glassesColor = self.selectedNPC.glassesColor
        backpack = self.selectedNPC.backpack
        backpackColor = self.selectedNPC.backpackColor
        shoes = self.selectedNPC.shoes
        shoesTex = self.selectedNPC.shoesTex

        # Toon object has getters & setters for accessories
        self.NPCAvatarToon.setHat(hat, hatColor, 0)
        self.NPCAvatarToon.setGlasses(glasses, glassesColor, 0)
        self.NPCAvatarToon.setBackpack(backpack, backpackColor, 0)
        self.NPCAvatarToon.setShoes(shoes, shoesTex, 0)

        self.refreshClothingIDs()
        self.updateNPCObjectGeneral()
        self.selectednpcZone['text'] = "{} (Zone {})".format(buildingName, npcZone)

    def updateNPCObjectGeneral(self):
        """
        Called when a new NPC is on the panel; resets the NPCToonItem list & populates it with default values
        """
        self.resetNPCToonItem()
        self.fillNPCObject(0, self.selectedNPC.zoneId)

        # hoping there are no double entries in the name list...
        name = self.NPCToons.getNPCNameID(self.selectedNPC.name)
        self.fillNPCObject(1, "names[%s]" % str(name))

        self.fillNPCObject(2, "\'%s\'" % str(self.selectedNPC.head))
        self.fillNPCObject(3, "\'%s\'" % str(self.selectedNPC.torso))
        self.fillNPCObject(4, "\'%s\'" % str(self.selectedNPC.legs))
        self.fillNPCObject(5, "\'%s\'" % str(self.selectedNPC.gender))
        self.fillNPCObject(6, str(self.selectedNPC.armColor))
        self.fillNPCObject(7, str(self.selectedNPC.legColor))
        self.fillNPCObject(8, str(self.selectedNPC.headColor))
        self.fillNPCObject(9, str(self.selectedNPC.topTex))
        self.fillNPCObject(10, str(self.selectedNPC.topColor))
        self.fillNPCObject(11, str(self.selectedNPC.sleeveTex))
        self.fillNPCObject(12, str(self.selectedNPC.sleeveColor))
        self.fillNPCObject(13, str(self.selectedNPC.botTex))
        self.fillNPCObject(14, str(self.selectedNPC.botColor))

        if self.selectedNPC.npcType != NPC.REGULAR:
            # annoying hacky bc npc types arent in a list
            val = self.NPCToons.getNPCTypeValue(self.selectedNPC.npcType)  # type: str
            self.fillNPCObject(15, "npcType=%s" % val)

        if self.selectedNPC.hat != 0:
            self.fillNPCObject(16, "hat=%s" % str(self.selectedNPC.hat))
        if self.selectedNPC.hatColor != 0:
            self.fillNPCObject(17, "hatColor=%s" % str(self.selectedNPC.hatColor))

        if self.selectedNPC.glasses != 0:
            self.fillNPCObject(18, "glasses=%s" % str(self.selectedNPC.glasses))
        if self.selectedNPC.glassesColor != 0:
            self.fillNPCObject(19, "glassesColor=%s" % str(self.selectedNPC.glassesColor))

        if self.selectedNPC.backpack != 0:
            self.fillNPCObject(20, "backpack=%s" % str(self.selectedNPC.backpack))
        if self.selectedNPC.backpackColor != 0:
            self.fillNPCObject(21, "backpackColor=%s" % str(self.selectedNPC.backpackColor))

        if self.selectedNPC.shoes != 0:
            self.fillNPCObject(22, "shoes=%s" % str(self.selectedNPC.shoes))
        if self.selectedNPC.shoesTex != 0:
            self.fillNPCObject(23, "shoesTex=%s" % str(self.selectedNPC.shoesTex))

        if self.selectedNPC.cheesyEffect != 0:
            self.fillNPCObject(24, "ce=%s" % str(self.selectedNPC.cheesyEffect))
        if self.selectedNPC.animation.lower() != "neutral":
            self.fillNPCObject(25, "animation=\"%s\"" % self.selectedNPC.animation)
        if self.selectedNPC.animationSpeed != 1.0:
            self.fillNPCObject(26, "animationSpeed= %s" % str(self.selectedNPC.animationSpeed))
        if self.selectedNPC.tag != "":
            self.fillNPCObject(27, "tag=\"%s\"" % self.selectedNPC.tag)
        if self.selectedNPC.pos is not None:
            self.fillNPCObject(28, "pos=%s" % str(self.selectedNPC.pos))
        if self.selectedNPC.earColor != self.selectedNPC.headColor:
            self.fillNPCObject(29, "earColor=%s" % str(self.selectedNPC.earColor))
        if self.selectedNPC.eyeColor != 0:
            self.fillNPCObject(30, "eyeColor=%s" % str(self.selectedNPC.eyeColor))
        if self.selectedNPC.gloveColor != 0:
            self.fillNPCObject(31, "gloveColor=%s" % str(self.selectedNPC.gloveColor))
        if self.selectedNPC.holidayIds:
            self.fillNPCObject(32, "holidayIds=%s" % str(self.selectedNPC.holidayIds))

    def transformIntoNPC(self):
        """
        Changes the avatar's DNA to the NPC's DNA (Client sided only and temporary)
        """
        if not hasattr(base, 'localAvatar'):
            self.notify.warning("localAvatar doesn't exist, deleting panel!")
            self.destroy()
            return

        hat = self.NPCAvatarToon.getHat()
        gl = self.NPCAvatarToon.getGlasses()
        bp = self.NPCAvatarToon.getBackpack()
        sh = self.NPCAvatarToon.getShoes()
        if not self.solo or hasattr(base, 'localAvatar'):
            base.localAvatar.setDNAString(self.DNAString)
            base.localAvatar.setHat(hat[0], hat[1], hat[2])
            base.localAvatar.setGlasses(gl[0], gl[1], gl[2])
            base.localAvatar.setBackpack(bp[0], bp[1], bp[2])
            base.localAvatar.setShoes(sh[0], sh[1], sh[2])
            base.localAvatar.setName(self.NPCAvatarToon.getName())

    def refreshClothingIDs(self):
        """
        Called on the end of updateDNA/Accessory to update the text reflecting the new IDs.
        """
        self.npcDNA = "[{}, {}] [{}, {}] [{}, {}]".format(
            self.NPCAvatarToon.style.topTex, self.NPCAvatarToon.style.topTexColor,
            self.NPCAvatarToon.style.sleeveTex, self.NPCAvatarToon.style.sleeveTexColor,
            self.NPCAvatarToon.style.botTex, self.NPCAvatarToon.style.botTexColor
        )
        # example formatting: [1, 12] [1, 12] [5, 20]

        self.npcAccessory = "{}, {}, {}, {}".format(
            self.NPCAvatarToon.getHat(), self.NPCAvatarToon.getGlasses(),
            self.NPCAvatarToon.getBackpack(), self.NPCAvatarToon.getShoes()
        )
        # example formatting: (1, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)

        self.DNAValueText['text'] = self.npcDNA
        self.AccValueText['text'] = self.npcAccessory

    def generateToon(self, npc):
        toon = Toon.Toon()
        toon.flattenStrong()
        self.DNAString = npc.makeNetString()
        toon.setDNAString(self.DNAString)
        toon.getGeomNode().setDepthWrite(1)
        toon.getGeomNode().setDepthTest(1)
        toon.getGeomNode().setTwoSided(True)
        toon.loop('neutral')
        self.fitGeometry(toon, fFlip = 1)
        return toon

    def fitGeometry(self, geom, fFlip = 0, dimension = 0.4):
        p1 = Point3()
        p2 = Point3()
        geom.calcTightBounds(p1, p2)
        if fFlip:
            t = p1[0]
            p1.setX(-p2[0])
            p2.setX(-t)
        d = p2 - p1
        biggest = max(d[0], d[2])
        s = dimension / biggest
        mid = (p1 + d / 2.0) * s
        geomXform = hidden.attachNewNode('geomXform')
        for child in geom.getChildren():
            child.reparentTo(geomXform)

        posOffset = (0, 0, 0)
        geomXform.setPosHprScale(-mid[0] + posOffset[0], -mid[1] + 2 + posOffset[1], -mid[2] - 0.02 + posOffset[2], 180,
                                 0, 0, s, s, s)
        geomXform.reparentTo(geom)

    def fillNPCObject(self, index, value):
        self.NPCToonItem.get("NPCToonObject")[index] = value

    def resetNPCToonItem(self):
        # We don't need to reset the npcID to None, every NPC will ALWAYS have a unique NPC id.
        # self.NPCToonItem["npcID"] = None
        npcList = self.NPCToonItem.get("NPCToonObject")
        if not npcList:
            return
        for npcEntry in npcList:
            npcList[npcList.index(npcEntry)] = None

    def printFormat(self):
        tab = "    "
        finalString = ""
        endl = "),  #  %s" % self.selectednpcID['text']

        wantTab = True
        if wantTab:
            finalString += tab

        wantFullFormat = True
        if wantFullFormat:
            finalString += str(self.NPCToonItem["npcID"]) + ": NPCToon("

        toonObjects = self.NPCToonItem.get("NPCToonObject")
        npcEntry = lambda value: toonObjects[value]
        finalString += ', '.join(str(npcEntry(value)) for value in range(len(toonObjects)) if (npcEntry(value)))

        if wantFullFormat:
            finalString += endl

        print(finalString)


"""
from toontown.toon import NPCToonExplorer
npcx = NPCToonExplorer.NPCToonExplorer()
"""
