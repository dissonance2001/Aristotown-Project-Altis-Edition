from enum import IntEnum, auto

from direct.showbase import PythonUtil

from toontown.club import ClubGlobals
from toontown.club.ClubClasses import ClubTask
from toontown.club.ClubContainerClient import ClubContainerClient
from toontown.gui.TTGui import ExtendedOnscreenText
from toontown.quest3.QuestEnums import QuestSource
from toontown.quest3.base import QuestGlobals
from toontown.quest3.base.QuestChain import QuestChain
from toontown.quest3.base.QuestLine import QuestLine
from toontown.quest3 import QuestLocalizer
from toontown.quest3.base.QuestObjective import QuestObjective
from toontown.quest3.base.QuestReference import QuestId, QuestReference
from toontown.quest3.gui.DailyQuestPoster import DailyQuestPoster
from toontown.quest3.gui.Quest3Poster import QuestPoster
from toontown.quest3.gui.Quest3SidequestPoster import SidequestPoster
from toontown.shtiker import ShtikerPage
from direct.gui.DirectGui import *
from panda3d.core import Vec4, TextNode, TransparencyAttrib
from direct.showbase.MessengerGlobal import messenger
from toontown.makeatoon.MakeAToonGlobals import *
from toontown.menu import MainMenuGui
from toontown.shtiker.KudosPage import KudosPage
from toontown.shtiker.daily.DailyTaskSubpage import DailyTaskSubpage
from toontown.toon import OneTimeCutsceneGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.menu.MainMenuGui import MainMenuButton
from toontown.toon.gui import ToonTipsGUI
from datetime import datetime, timedelta
from direct.interval.IntervalGlobal import *

from toontown.gui import TTDialog, UiHelpers
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget

"""
CONSTANTS - Sorted in order of page order
    - ToonTasks
    - Sidequest Directory
    - Daily Task
"""

"""
ToonTasks
"""

# Locations of quest frames on the ToonTasks tab
questFramePlaceList = ((-0.45, 0, 0.25, 0, 0, 0),
                       (0.45, 0, 0.25, 0, 0, 0),
                       (-0.45, 0, -0.35, 0, 0, 0),
                       (0.45, 0, -0.35, 0, 0, 0))

dailyQuestFramePlaceList = (
    (-0.46, 0, 0.35),
    (-0.46, 0, -0.05),
    (-0.46, 0, -0.45)
)

# Locations of quest frames when Onscreen Preview outside of book (END Key)
questFramePlaceListOnscreen = ((-0.46, 0, 0.3, 0, 0, 0),
                               (0.44, 0, 0.3, 0, 0, 0),
                               (-0.46, 0, -0.3, 0, 0, 0),
                               (0.44, 0, -0.3, 0, 0, 0))

sidequestFramePlacement = (0.45, 0, 0.25, 0, 0, 0)

posterGroupXpos = {
    1: (0.9,),
    2: (0.6, 1.25),
}
posterGroupXOffset = {
    0: 0.0,
    1: -0.35,
    2: -0.65,
}
extraQuestFrameHeight = 3

textInProgressColor = Vec4(.8, .55, 0, 1)
textCompletedColor = Vec4(.6, .2, .2, 1)

textRolloverColor = Vec4(1, 1, 0, 1)
textDownColor = Vec4(0.5, 0.9, 1, 1)
textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)

"""
Sidequest Directory
"""


# Used for playground pages in the directory
class QuestTier(IntEnum):
    TTC = auto()
    BB = auto()
    YOTT = auto()
    DG = auto()
    MML = auto()
    TB = auto()
    AA = auto()
    DDL = auto()
    LBHQ = auto()
    SPECIAL_EVENTS = auto()
    ALL_QUESTS = auto()


QuestTierStrings = {
    # Flags
    QuestTier.SPECIAL_EVENTS: "Special\nEvents",
    QuestTier.ALL_QUESTS: "All\nToonTasks",

    # Zones
    QuestTier.TTC: TTLocalizer.ToontownCentral[2],
    QuestTier.BB: TTLocalizer.DonaldsDock[2],
    QuestTier.YOTT: TTLocalizer.YeOlde[2],
    QuestTier.DG: TTLocalizer.DaisyGardens[2],
    QuestTier.MML: TTLocalizer.MinniesMelodyland[2],
    QuestTier.TB: "The\nBrrrgh",
    QuestTier.AA: TTLocalizer.OutdoorZone[2],
    QuestTier.DDL: TTLocalizer.DonaldsDreamland[2],
    QuestTier.LBHQ: "Lawbot\nHQ",
}

ZoneId2QuestTier = {
    ToontownGlobals.ToontownCentral: QuestTier.TTC,
    ToontownGlobals.DonaldsDock: QuestTier.BB,
    ToontownGlobals.YeOlde: QuestTier.YOTT,
    ToontownGlobals.DaisyGardens: QuestTier.DG,
    ToontownGlobals.MinniesMelodyland: QuestTier.MML,
    ToontownGlobals.TheBrrrgh: QuestTier.TB,
    ToontownGlobals.OutdoorZone: QuestTier.AA,
    ToontownGlobals.DonaldsDreamland: QuestTier.DDL,
    ToontownGlobals.LawbotHQ: QuestTier.LBHQ,
}

# Positions of the information text nodes
informationTextNodePositions = {
    'description': (.45, 0, -.09),
    'location': (.45, 0, -.42),
    'reward': (.45, 0, -.60)
}
# Avail Sidequest Page Vars
itemFrameXorigin = -0.237
itemFrameZorigin = .03
listXorigin = -0.02
listFrameSizeX = 0.67
listZorigin = -0.63
listFrameSizeZ = .7
title_text_scale = 0.12


@DirectNotifyCategory()
class QuestPage(ShtikerPage.ShtikerPage):
    @InjectorTarget
    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.textRolloverColor = Vec4(1, 1, 0, 1)
        self.textDownColor = Vec4(0.5, 0.9, 1, 1)
        self.textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
        self.onscreen = 0
        self.lastQuestTime = globalClock.getRealTime()

        # List of available sidequests
        self.sidequestList = None
        self.sidequestFrames = {}
        self.selectedQuest = None
        # This will be used to determine current playground the player is viewing quests for
        self.currentPlayground = QuestTier.TTC
        self.kudosFlashIval = None

    def load(self):
        self.title = DirectLabel(parent=self, relief=None, text=TTLocalizer.QuestPageToonTasks, text_scale=0.12,
                                 textMayChange=1, pos=(0, 0, 0.6))

        # Gui models we need for gui elements
        tabsGUI = loader.loadModel('phase_3.5/models/gui/fishingBook.bam')
        scrollGUI = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        playgroundGUI = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')

        # Tabs at top of book
        self.TasksButton = DirectButton(parent=self, relief=None, text=TTLocalizer.QuestPageToonTasks,
                                        text_scale=TTLocalizer.GPrecordsTab, text_align=TextNode.ACenter, scale=0.9,
                                        image=tabsGUI.find('**/tabs/polySurface2'),
                                        image_pos=(0, 0, -1.06),
                                        image_hpr=(0, 0, -90), image_scale=(0.038, 0, 0.045), image_color=(1, 1, 1, 1),
                                        image1_color=(0.8, 0.8, 0, 1), image2_color=(0.15, 0.82, 1.0, 1),
                                        image3_color=(1.0, 0.98, 0.15, 1),
                                        text_fg=Vec4(0.2, 0.1, 0, 1), command=self.switchToQuests,
                                        pos=(-0.5, 0, 0.785))

        self.AvailSidequestsButton = DirectButton(parent=self, relief=None, text=TTLocalizer.QuestPageDirectory,
                                                  text_scale=TTLocalizer.GPrecordsTab, text_align=TextNode.ACenter,
                                                  scale=0.9,
                                                  image=tabsGUI.find('**/tabs/polySurface2'),
                                                  image_pos=(0, 0, -1.06),
                                                  image_hpr=(0, 0, -90), image_scale=(0.038, 0, 0.045),
                                                  image_color=(1, 1, 1, 1),
                                                  image1_color=(0.8, 0.8, 0, 1), image2_color=(0.15, 0.82, 1.0, 1),
                                                  image3_color=(1.0, 0.98, 0.15, 1),
                                                  text_fg=Vec4(0.2, 0.1, 0, 1), command=self.switchToAvailSidequests,
                                                  pos=(0, 0, 0.785))

        self.dailyObjectivesButton = DirectButton(parent=self, relief=None, text=TTLocalizer.QuestPageDailyTask,
                                                  text_scale=TTLocalizer.GPrecordsTab, text_align=TextNode.ACenter,
                                                  scale=0.9,
                                                  image=tabsGUI.find('**/tabs/polySurface2'),
                                                  image_pos=(0, 0, -1.06),
                                                  image_hpr=(0, 0, -90), image_scale=(0.038, 0, 0.045),
                                                  image_color=(1, 1, 1, 1),
                                                  image1_color=(0.8, 0.8, 0, 1), image2_color=(0.15, 0.82, 1.0, 1),
                                                  image3_color=(1.0, 0.98, 0.15, 1),
                                                  text_fg=Vec4(0.2, 0.1, 0, 1), command=self.switchToDailyTask,
                                                  pos=(0.5, 0, 0.785))

        self.kudosQuestsButton = DirectButton(
            parent=self, relief=None, text=TTLocalizer.QuestPageKudos,
            text_scale=TTLocalizer.GPrecordsTab, text_align=TextNode.ACenter,
            scale=0.9,
            image=tabsGUI.find('**/tabs/polySurface2'),
            image_pos=(0, 0, -1.06),
            image_hpr=(0, 0, -90), image_scale=(0.038, 0, 0.045),
            image_color=(1, 1, 1, 1),
            image1_color=(0.8, 0.8, 0, 1), image2_color=(0.15, 0.82, 1.0, 1),
            image3_color=(1.0, 0.98, 0.15, 1),
            text_fg=Vec4(0.2, 0.1, 0, 1), command=self.switchToKudosTask,
            pos=(0.5, 0, 0.785)
        )

        self.updateTabPositions()

        # Create the Toon Tip history button
        gui = loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')
        self.toonTipButton = DirectButton(parent=self, relief=None, pos=(0.7, 0, 0.635), image=(
            gui.find('**/report_BtnUP'),
            gui.find('**/report_BtnDN'),
            gui.find('**/report_BtnRLVR'),
            gui.find('**/report_BtnDN')), image_scale=0.775 * 1.4, command=self.popupTipGui,
                                          text=('', TTLocalizer.ToonTipButtonText, TTLocalizer.ToonTipButtonText, ''),
                                          text_scale=0.0425, text_pos=(0, -0.07))
        gui.removeNode()

        # Hide them because they WILL show upon pressing quests hotkey, we will show them when we enter the book
        self.TasksButton.hide()
        self.AvailSidequestsButton.hide()
        self.dailyObjectivesButton.hide()
        self.kudosQuestsButton.hide()
        self.toonTipButton.hide()

        # TOONTASKS PAGE ELEMENTS=======================================================================================

        # Create active quests GUI Components
        self.questFrames = []
        self.questFrameScales = []
        for i in range(ToontownGlobals.MaxQuestCarryLimit):
            questFrame = QuestPoster(parent=self)
            questFrame.setPosHpr(*questFramePlaceList[i])
            questFrame.setScale(1.06)
            questFrame.setMapIndex(i + 1)
            questFrame.reverseBG(reverse=i % 2)
            self.questFrames.append(questFrame)
            self.questFrameScales.append(questFrame.getScale())

        # SIDEQUEST DIRECTORY PAGE ELEMENTS=============================================================================

        # Create Sidequest Dict GUI Components
        playgroundFrame = playgroundGUI.find('**/tt_t_gui_mat_shuffleFrame')
        shuffleImage = (playgroundGUI.find('**/tt_t_gui_mat_shuffleArrowUp'),
                        playgroundGUI.find('**/tt_t_gui_mat_shuffleArrowDown'),
                        playgroundGUI.find('**/tt_t_gui_mat_shuffleArrowUp'),
                        playgroundGUI.find('**/tt_t_gui_mat_shuffleArrowDisabled'))

        self.playgroundFrame = DirectFrame(parent=self, image=playgroundFrame, image_scale=halfButtonInvertScale,
                                           relief=None, pos=(-0.43256, 0.0, 0.42658), hpr=(0, 0, 0), scale=0.93642,
                                           frameColor=(1, 1, 1, 1))
        self.playgroundLButton = DirectButton(parent=self.playgroundFrame, relief=None, image=shuffleImage,
                                              image_scale=halfButtonScale, image1_scale=halfButtonHoverScale,
                                              image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0),
                                              command=self.doPlaygroundPageChange,
                                              extraArgs=[-1])
        self.playgroundLButton['state'] = DGG.DISABLED
        self.playgroundRButton = DirectButton(parent=self.playgroundFrame, relief=None, image=shuffleImage,
                                              image_scale=halfButtonInvertScale,
                                              image1_scale=halfButtonInvertHoverScale,
                                              image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0),
                                              command=self.doPlaygroundPageChange,
                                              extraArgs=[1])
        self.playgroundText = ExtendedOnscreenText(
            parent=self.playgroundFrame,
            text='',
            pos=(-0.004, -0.014),
            scale=0.0485,
            wordwrap=5,
            fg=(1, 1, 1, 1),
            roll=3,
        )
        self.playgroundText.setTextWithVerticalAlignment(QuestTierStrings[self.currentPlayground])

        self.sidequestList = DirectScrolledList(parent=self, relief=None, pos=(-0.5, 0, 0.15868),
                                                itemFrame_pos=(itemFrameXorigin, 0, itemFrameZorigin),
                                                itemFrame_scale=1.0,
                                                incButton_image=(scrollGUI.find('**/FndsLst_ScrollUp'),
                                                                 scrollGUI.find('**/FndsLst_ScrollDN'),
                                                                 scrollGUI.find('**/FndsLst_ScrollUp_Rllvr'),
                                                                 scrollGUI.find('**/FndsLst_ScrollUp')),
                                                incButton_relief=None, incButton_scale=(1.3, 1.3, -1.3),
                                                incButton_pos=(.065, 0, -0.81847),
                                                incButton_image3_color=Vec4(1, 1, 1, 0.2),
                                                decButton_image=(scrollGUI.find('**/FndsLst_ScrollUp'),
                                                                 scrollGUI.find('**/FndsLst_ScrollDN'),
                                                                 scrollGUI.find('**/FndsLst_ScrollUp_Rllvr'),
                                                                 scrollGUI.find('**/FndsLst_ScrollUp')),
                                                decButton_relief=None, decButton_scale=(1.3, 1.3, 1.3),
                                                decButton_pos=(.065, 0, .135),
                                                decButton_image3_color=Vec4(1, 1, 1, 0.2),
                                                itemFrame_relief=DGG.SUNKEN,
                                                itemFrame_frameSize=(-0.02, 0.65, -0.81191, 0.07),
                                                # (listXorigin, listXorigin + listFrameSizeX, listZorigin, listZorigin + listFrameSizeZ),
                                                itemFrame_frameColor=(0.85, 0.95, 1, 1),
                                                itemFrame_borderWidth=(0.01, 0.01), numItemsVisible=13,
                                                forceHeight=0.065)

        self.sidequestInformationText = {  # Reference these if you want to change text content
            'location': TextNode(''),
            'reward': TextNode(''),
        }
        self.sidequestInformationTextNodes = {key: self.attachNewNode(value) for key, value in list(
            self.sidequestInformationText.items())}  # Reference these if you want to change pos and size

        self.text_sidequestDescription = ExtendedOnscreenText(
            parent=self,
            pos=(0.44482, -0.31423),
            text='',
            wordwrap=16,
            scale=0.053,
        )

        self.setInformationText()  # first lets make the text show their default values

        # Set up the text properties of each of the text thingys
        for key in self.sidequestInformationText:
            self.sidequestInformationText[key].setAlign(
                TextNode.ACenter)  # We want the text to be centered, looks nicer
            self.sidequestInformationText[key].setWordwrap(
                16)  # Set the text to word wrap so we dont have to put \n's all over the place
            self.sidequestInformationText[key].setTextColor(0, 0, 0, 1)  # Set the text color to black
            self.sidequestInformationText[key].setFont(ToontownGlobals.getInterfaceFont())  # Make the font look toony

        # Now lets set up the nodes
        for key in (self.sidequestInformationTextNodes):
            self.sidequestInformationTextNodes[key].setScale(.053)  # Set our text size
            self.sidequestInformationTextNodes[key].setPos(informationTextNodePositions[key])  # Set our text positions

        # Create the sidequest poster to display info
        self.sidequestPoster = SidequestPoster(parent=self)  # Create a quest poster object
        self.sidequestPoster.setPosHpr(
            *sidequestFramePlacement)  # We want the sidequest to show to be in the top right spot
        self.sidequestPoster.setScale(1.06)
        self.sidequestPoster.reverseBG(1)

        # Create the stamp image over the sidequest poster
        stampImage = loader.loadModel('phase_3.5/models/gui/SideQuestDir').find('**/stamp')
        self.sidequestPosterStamp = DirectFrame(parent=self, image=stampImage, image_scale=.6, relief=None,
                                                pos=(.45, 0, .25),
                                                frameColor=(1, 1, 1, 1))  # Create stamp image for completed sidequests
        self.sidequestPosterStamp.setTransparency(
            TransparencyAttrib.MAlpha)  # This line and next line just give the image some transparency, not sure if want to keep or not
        self.sidequestPosterStamp.setAlphaScale(.9)

        self.updateSideQuestList()  # By default we want our list to display TTC quests in our directory
        self.hideAvailSidequests()  # Hide this section of the page so it's not seen right when you open to the ToonTasks section

        # DAILY TASK PAGE ELEMENTS======================================================================================

        # Load display elements for the daily tasks page
        self.dailyQuestPosters = []
        for i in range(3):
            questPoster = DailyQuestPoster(parent=self, onscreen=True)
            questPoster.setScale(0.75)
            questPoster.setPos(*dailyQuestFramePlaceList[i])
            questPoster.reverseBG(1)
            questPoster.hide()
            self.dailyQuestPosters.append(questPoster)
            # add it to questFrameScales for the pop-in effect
            self.questFrameScales.append(questPoster.getScale())

        self.dailyTaskSubpage = DailyTaskSubpage(parent=self)
        self.dailyTaskSubpage.hide()

        # We'll make a club task poster too.
        self.clubTaskPosters = [QuestPoster(parent=self) for _ in range(ClubGlobals.ClubTaskCount)]
        for qp in self.clubTaskPosters:
            qp.setScale(0.75)
            qp.reverseBG(1)
            self.questFrameScales.append(qp.getScale())
            qp.hide()

        # List of active token icons displaying on the bottom left of the page
        self.tokenIcons = []

        # Make kudos page
        self.kudosPage = KudosPage(
            parent=self,
        )
        self.kudosPage.hide()

        # Gui models we need for gui elements
        tabsGUI.removeNode()
        scrollGUI.removeNode()
        playgroundGUI.removeNode()

        self.currentBoosts = base.localAvatar.getAllBoosters()  # Used to test whether or not we should do boost adding and removing animations

        self.accept('questsChanged', self.updatePage)
        self.accept('kudosUpdated', self.updateTabPositions)
        self.boostQueue = []  # List of boost IDs in line to be added
        return

    def updateTabPositions(self, _=None):
        tabsList = [self.TasksButton, self.AvailSidequestsButton, self.dailyObjectivesButton]
        width = 0.5
        if base.localAvatar.getKudos():
            width = 0.675
            tabsList.append(self.kudosQuestsButton)
            if not self.TasksButton.isHidden():
                self.kudosQuestsButton.show()
        for i, tab in enumerate(tabsList):
            xpos = PythonUtil.lerp(-width, width, i / (len(tabsList) - 1))
            zpos = 0.785
            tab.setPos(xpos, 0, zpos)

    """
    Methods for switching between the pages
    """

    def switchToAvailSidequests(self):
        self.hideQuests()
        self.toonTipButton.show()
        self.showAvailSidequests()
        self.hideDailyTask()
        self.hideKudos()
        self.toonTipButton.hide()
        self.title['text'] = TTLocalizer.QuestPageDirectoryTitle
        self.TasksButton['state'] = DGG.NORMAL
        self.AvailSidequestsButton['state'] = DGG.DISABLED
        self.dailyObjectivesButton['state'] = DGG.NORMAL
        self.kudosQuestsButton['state'] = DGG.NORMAL
        messenger.send("enterSidequestPage")

    def switchToQuests(self):
        self.showQuests()
        self.hideAvailSidequests()
        self.hideDailyTask()
        self.hideKudos()
        if self.onscreen:
            self.showDailyQuests()
            self.toonTipButton.hide()
        else:
            self.toonTipButton.show()
        self.title['text'] = TTLocalizer.QuestPageToonTasks
        self.TasksButton['state'] = DGG.DISABLED
        self.AvailSidequestsButton['state'] = DGG.NORMAL
        self.dailyObjectivesButton['state'] = DGG.NORMAL
        self.kudosQuestsButton['state'] = DGG.NORMAL

    def switchToDailyTask(self):
        self.showDailyTask()
        self.hideAvailSidequests()
        self.hideQuests()
        self.hideKudos()
        self.toonTipButton.hide()

        self.title['text'] = ''
        self.dailyObjectivesButton['state'] = DGG.DISABLED
        self.TasksButton['state'] = DGG.NORMAL
        self.AvailSidequestsButton['state'] = DGG.NORMAL
        self.kudosQuestsButton['state'] = DGG.NORMAL

    def switchToKudosTask(self):
        self.stopKudosFlashIval()
        self.hideDailyTask()
        self.hideAvailSidequests()
        self.hideQuests()
        self.showKudos()
        self.toonTipButton.hide()

        if self.showKudosFlash:
            # Mark the book flash as seen by our local av.
            # This should save and they should never see it again.
            base.localAvatar.requestAddSeenCutscene(OneTimeCutsceneGlobals.OneTimeCutscenes.KudosBookFlash)
            # Also request the kudos page toon tip on the first time visit
            base.localAvatar.sendUpdate('requestToonTip', [77])

        self.title['text'] = ''
        self.TasksButton['state'] = DGG.NORMAL
        self.AvailSidequestsButton['state'] = DGG.NORMAL
        self.dailyObjectivesButton['state'] = DGG.NORMAL
        self.kudosQuestsButton['state'] = DGG.DISABLED

    """
    Methods responsible for hiding certain pages' elements
    """

    def hideQuests(self):  # Hide the quests on the ToonTasks Page
        for questFrame in self.questFrames:
            questFrame.hide()

    def showQuests(self):  # Show the quests on the ToonTasks Page
        for questFrame in self.questFrames:
            questFrame.show()

    def showDailyQuests(self):
        for questPoster in self.dailyQuestPosters:
            questPoster.show()

    def hideDailyQuests(self):
        for questPoster in self.dailyQuestPosters:
            questPoster.hide()

    def hideAvailSidequests(self):
        self.sidequestList.hide()
        self.sidequestPoster.hide()
        self.sidequestPosterStamp.hide()
        self.playgroundFrame.hide()
        self.playgroundLButton.hide()
        self.playgroundRButton.hide()
        self.text_sidequestDescription.hide()
        [self.sidequestInformationTextNodes[key].hide() for key in self.sidequestInformationTextNodes]

    def showAvailSidequests(self):
        self.sidequestList.show()
        self.sidequestPoster.show()
        self.playgroundFrame.show()
        if self.selectedQuest:
            if self.selectedQuest[1]:
                self.sidequestPosterStamp.show()
        self.playgroundLButton.show()
        self.playgroundRButton.show()
        self.text_sidequestDescription.show()
        [self.sidequestInformationTextNodes[key].show() for key in self.sidequestInformationTextNodes]

    def hideDailyTask(self):
        self.dailyTaskSubpage.hide()

    def showDailyTask(self):
        self.dailyTaskSubpage.show()

    def hideKudos(self):
        self.kudosPage.hide()

    def showKudos(self):
        self.kudosPage.show()

    """
    Methods for the ToonTasks page
    """

    def setQuestFrame(self, questReference: QuestReference, index: int):
        if questReference.getQuestSource() == QuestSource.DailyQuest:
            questPoster = self.dailyQuestPosters[index]
        else:
            questPoster = self.questFrames[index]

        questPoster.setQuestReference(questReference)

        # Set this quest's deletable state.
        deleteCallback = self.__deleteQuest if questReference and self.canDeleteQuest(questReference) else None
        questPoster.setDeleteCallback(deleteCallback)

    def showQuestsOnscreenTutorial(self):
        self.setPos(0, 0, -0.2)
        self.showQuestsOnscreen()

    def showQuestsOnscreen(self):
        messenger.send('wakeup')
        timedif = globalClock.getRealTime() - self.lastQuestTime
        if timedif < 0.7:
            return

        if localAvatar and getattr(localAvatar, 'localToonTyping', False):
            return

        self.lastQuestTime = globalClock.getRealTime()
        if self.onscreen:
            return
        self.onscreen = 1

        self.updatePage()

        # Update the daily posters.
        for poster in self.dailyQuestPosters:
            poster.hide()
        activeDailyPosters = [poster for poster in self.dailyQuestPosters if poster.questReference]

        # Update the club poster.
        for posterIndex, poster in enumerate(self.clubTaskPosters):
            poster.hide()
            clubContainer = base.cr.clubMgr.getLocalClub()  # type: ClubContainerClient
            if clubContainer:
                clubTask = clubContainer.getClubTaskIndex(posterIndex)  # type: ClubTask
                if clubTask:
                    poster.setQuestReference(clubTask.getQuestReference())
                    poster.label_headLine.setText('Club Task')
                    activeDailyPosters.insert(0, poster)

        # Place the posters.
        for poster in activeDailyPosters:
            poster.show()
        posterGroups = 1 + ((len(activeDailyPosters) - 1) // extraQuestFrameHeight)
        for i in range(posterGroups):
            posters = activeDailyPosters[i * extraQuestFrameHeight:(i + 1) * extraQuestFrameHeight]
            xpos = posterGroupXpos.get(posterGroups)[i]
            UiHelpers.placeElementsInVerticalLine(posters, startPos=(xpos, 0, 0), scale=0.7, alignCenter=True)
        for i in range(ToontownGlobals.MaxQuestCarryLimit):
            x, y, z, h, p, r = questFramePlaceListOnscreen[i]
            x += posterGroupXOffset.get(posterGroups)
            self.questFrames[i].setPosHpr(x, y, z, h, p, r)

        self.reparentTo(aspect2d)
        self.title.hide()
        MainMenuGui.staggeredFadePopin(self.questFrames + activeDailyPosters, self.questFrameScales)
        self.show()

    def hideQuestsOnscreenTutorial(self):
        self.setPos(0, 0, 0)
        self.hideQuestsOnscreen()

    def hideQuestsOnscreen(self):
        if not self.onscreen:
            return
        self.onscreen = 0
        for i in range(ToontownGlobals.MaxQuestCarryLimit):
            self.questFrames[i].setPosHpr(*questFramePlaceList[i])

        for i, questPoster in enumerate(self.dailyQuestPosters):
            questPoster.setPos(*dailyQuestFramePlaceList[i])

        self.reparentTo(self.book)
        self.title.show()
        self.hideDailyQuests()
        self.hide()

    def canDeleteQuest(self, questRef: QuestReference):
        questChain = QuestLine.getQuestChainFromQuestId(questRef.getQuestId(), quester=base.localAvatar)
        return questChain.isDeletable()

    def __deleteQuest(self, questReference: QuestReference):
        base.localAvatar.d_requestDeleteQuest(questReference)

    def popupTipGui(self):
        self.toonTipGui = ToonTipsGUI.ToonTipsSeenPanel(base.localAvatar)
        self.toonTipGui.enter()

    """
    Methods for the Sidequest Directory page
    """

    def doPlaygroundPageChange(self, direction):
        self.currentPlayground += direction

        # Clamp the value between the start and end.
        self.currentPlayground = min(max(self.currentPlayground, QuestTier.TTC), QuestTier.ALL_QUESTS)

        # Handle button states
        if self.currentPlayground >= QuestTier.ALL_QUESTS:
            self.playgroundRButton['state'] = DGG.DISABLED
        elif self.currentPlayground <= QuestTier.TTC:
            self.playgroundLButton['state'] = DGG.DISABLED
        else:
            self.playgroundRButton['state'] = DGG.NORMAL
            self.playgroundLButton['state'] = DGG.NORMAL

        # Update our sidequest list, deselect a quest if selected
        if self.selectedQuest:
            self.deselectQuest()

        self.updateSideQuestList()
        self.playgroundText.setTextWithVerticalAlignment(QuestTierStrings[self.currentPlayground])

    # Call this method to update the sidequest list with a certain playground's sidequests
    def updateSideQuestList(self):
        self.clearSidequestList()  # Remove the current quests listed

        if self.selectedQuest:
            self.deselectQuest()  # Deselect a quest if one is already selected

        # Get all of the sidequests that are accessible to this quester.
        sidequests = QuestGlobals.getSidequests(base.localAvatar)
        directives = QuestGlobals.getDirectives(base.localAvatar)

        for quests, questSource in zip((sidequests, directives), (QuestSource.SideQuest, QuestSource.Directive)):
            for chainId, chain in quests:
                chain: QuestChain
                questId = QuestId(questSource, chainId, chain.getStartObjectiveId())
                questReference = QuestReference(questId)

                # The chainId does not exist in the quester's quest history.
                if not base.localAvatar.hasCompletedQuest(questSource, chainId):
                    # The questId is currently in progress.
                    if base.localAvatar.inQuestChain(questId):
                        # We want a different color for our in progress quests
                        self.createSidequestButton(questReference, textColor=textInProgressColor)
                    else:
                        # Create the sidequest button
                        self.createSidequestButton(questReference)
                else:
                    # We want a different color for our completed quests
                    self.createSidequestButton(questReference, textColor=textCompletedColor)

        if len(self.sidequestFrames) == 0:
            if self.currentPlayground == QuestTier.SPECIAL_EVENTS:
                self.setInformationText(description=TTLocalizer.QuestPageSidequestNoEvents)
            else:
                self.setInformationText(description=TTLocalizer.QuestPageSidequestLocked)

        if len(self.sidequestFrames) < self.sidequestList['numItemsVisible']:
            self.sidequestList.incButton.hide()
            self.sidequestList.decButton.hide()
        else:
            self.sidequestList.incButton.show()
            self.sidequestList.decButton.show()

    def clearSidequestList(self):  # Make the list on the left side of the page empty, pretty simple
        self.sidequestList.removeAndDestroyAllItems()  # Remove the quests from the list
        self.setInformationText()  # Clear the information text
        self.sidequestFrames = {}

    # This method is used to make a button on left side of page that can be clicked to show a quest's info
    def createSidequestButton(self, questReference: QuestReference, textColor=Vec4(0, 0, 0, 1)):
        questChain = QuestLine.getQuestChainFromQuestId(questId=questReference.getQuestId(), quester=base.localAvatar)
        for questObjective in QuestLine.dereferenceQuestReference(questReference,
                                                                  quester=base.localAvatar).getQuestObjectives():
            questObjective: QuestObjective

            success = self.currentPlayground == QuestTier.ALL_QUESTS \
                      or (self.currentPlayground == QuestTier.SPECIAL_EVENTS and questChain.isEventChain()) \
                      or self.currentPlayground == ZoneId2QuestTier.get(questObjective.getFromNpcHoodId())

            if success:
                sidequestButtonFrame = DirectFrame()
                sidequestButton = DirectButton(
                    parent=sidequestButtonFrame,
                    relief=None,
                    text=QuestLocalizer.getQuestHeadline(questReference),
                    text_fg=textColor,
                    text_scale=0.053,
                    text_align=TextNode.ALeft,
                    text1_bg=textDownColor,
                    text2_bg=textRolloverColor,
                    text3_fg=textDisabledColor,
                    command=self.selectQuest,
                    extraArgs=[questReference])

                self.sidequestFrames[(questReference.getQuestSource(), questReference.getChainId())] = \
                    (sidequestButtonFrame, sidequestButton)

                self.sidequestList.addItem(sidequestButtonFrame)
                return sidequestButtonFrame

    def updateSidequestState(self, questReference: QuestReference,
                             selected=False):  # This method is for handling whether or not sidequest buttons should be enabled or disabled
        buttons = self.sidequestFrames[(questReference.getQuestSource(), questReference.getChainId())]  # Get the button

        if selected:  # Calling this method with intent to 'select', disable the button
            buttons[1]['state'] = DGG.DISABLED
        else:  # or else we are re-enabling it
            buttons[1]['state'] = DGG.NORMAL

    def selectQuest(self, questReference: QuestReference):  # Call this method when clicking on a quest
        messenger.send("wakeup")
        if self.selectedQuest:  # We already have a quest selected, let's deselect our current one first
            self.deselectQuest()

        # Find out if the player has already completed the quest
        questIsComplete = base.localAvatar.hasCompletedQuest(questReference.getQuestSource(),
                                                             questReference.getChainId())

        self.updateSidequestState(questReference,
                                  selected=True)  # Disable the sidequest button, no reason they should already be able to click selected quests
        self.selectedQuest = (questReference, questIsComplete)  # Store this quest as selected

        self.sidequestPoster.setQuestReference(
            questReference)  # Display the quest poster with the selected quests information

        rewardString = QuestLocalizer.SideQuestRewards[questReference.getQuestSource()][questReference.getChainId()]
        rewardString = f"Reward: {rewardString}"

        self.setInformationText(
            description=QuestLocalizer.SideQuestDescriptions[questReference.getQuestSource()][
                questReference.getChainId()],
            reward=rewardString,
        )  # Display the informational text below the poster

        if questIsComplete:  # Quest has been completed, display the stamp
            self.sidequestPosterStamp.show()

    def deselectQuest(
            self):  # Call this method when clicking another quest, switching playground tabs, or leaving the book
        if self.selectedQuest:
            self.sidequestPoster.setQuestReference(None)  # Make the quest poster (top right) empty
            self.setInformationText()  # Make the information display their default values
            self.updateSidequestState(self.selectedQuest[0], selected=False)  # Enable the button

            if self.selectedQuest[1]:  # Quest was completed
                self.sidequestPosterStamp.hide()  # So hide the stamp

        self.selectedQuest = None  # We have nothing selected, remove this value

    def setInformationText(self, description=TTLocalizer.QuestPageSidequestInfo, location=' ',
                           reward=' '):  # Used for changing the text that appears on the bottom right section
        self.text_sidequestDescription.setTextWithVerticalAlignment(description)
        self.sidequestInformationText['location'].setText(location)
        self.sidequestInformationText['reward'].setText(reward)

    """
    Misc methods in charge of unloading/cleanup, hooking quests hotkey etc
    """

    def enter(self):
        self.TasksButton.show()
        self.AvailSidequestsButton.show()
        self.dailyObjectivesButton.show()
        self.stopKudosFlashIval()
        if base.localAvatar.getKudos():
            self.kudosQuestsButton.show()
            if self.showKudosFlash:
                self.startKudosFlashIval()
        self.toonTipButton.show()
        for qp in self.clubTaskPosters:
            qp.hide()

        if not self.currentPlayground:
            self.currentPlayground = QuestTier.TTC

        if self.currentPlayground == QuestTier.TTC:
            self.playgroundLButton['state'] = DGG.DISABLED
        else:
            self.playgroundLButton['state'] = DGG.NORMAL

        if self.currentPlayground == QuestTier.ALL_QUESTS:
            self.playgroundRButton['state'] = DGG.DISABLED
        else:
            self.playgroundRButton['state'] = DGG.NORMAL

        self.playgroundText.setTextWithVerticalAlignment(TTLocalizer.QuestPagePlaygrounds[self.currentPlayground])
        self.updateSideQuestList()
        self.updatePage()
        self.TasksButton['state'] = DGG.DISABLED
        ShtikerPage.ShtikerPage.enter(self)

    def exit(self):
        self.stopKudosFlashIval()
        self.switchToQuests()
        self.TasksButton.hide()
        self.dailyObjectivesButton.hide()
        self.kudosQuestsButton.hide()
        self.AvailSidequestsButton.hide()
        self.toonTipButton.hide()
        self.deselectQuest()

        if hasattr(self, 'onePointConfirm') and self.onePointConfirm:
            self.onePointConfirm.cleanup()
            del self.onePointConfirm

        if hasattr(self, 'chooseReward') and self.chooseReward:
            self.chooseReward.cleanup()
            del self.chooseReward

        ShtikerPage.ShtikerPage.exit(self)

    def unload(self):
        self.ignoreAll()
        del self.title
        del self.questFrames
        del self.toonTipButton
        loader.unloadModel('phase_3.5/models/gui/stickerbook_gui')
        ShtikerPage.ShtikerPage.unload(self)

    def acceptOnscreenHooks(self):
        self.accept(ToontownGlobals.QuestsHotkeyOn, self.showQuestsOnscreen)
        self.accept(ToontownGlobals.QuestsHotkeyOff, self.hideQuestsOnscreen)

    def ignoreOnscreenHooks(self):
        self.ignore(ToontownGlobals.QuestsHotkeyOn)
        self.ignore(ToontownGlobals.QuestsHotkeyOff)

    def updatePage(self):
        if not self.toonTipButton.isHidden():
            self.switchToQuests()
        self.notify.debug('updatePage()')

        # Update quest information
        carryLimit = base.localAvatar.getQuestCarryLimit()

        for questPoster in self.dailyQuestPosters + self.questFrames:
            questPoster.setQuestReference(None)

        [questPoster.hide() for i, questPoster in enumerate(self.questFrames) if i >= carryLimit]

        # Show quests now.
        questIndex = 0
        dailyQuestIndex = 0
        for questReference in base.localAvatar.getVisibleQuests():
            questReference: QuestReference
            self.setQuestFrame(questReference, questIndex)
            questIndex += 1
        for questReference in base.localAvatar.getQuestReferencesOfSource(QuestSource.DailyQuest):
            questReference: QuestReference
            self.setQuestFrame(questReference, dailyQuestIndex)
            dailyQuestIndex += 1

    @property
    def showKudosFlash(self):
        return base.localAvatar.hasSeenAnyCutscene(OneTimeCutsceneGlobals.AllKudosUnlocks) \
            and not base.localAvatar.hasSeenCutscene(OneTimeCutsceneGlobals.OneTimeCutscenes.KudosBookFlash)

    def startKudosFlashIval(self):
        self.stopKudosFlashIval()
        self.kudosFlashIval = Sequence(
            LerpFunctionInterval(self.setKudosTabColor, 1, Vec4(0.8, 0.8, 0.8, 1.0), Vec4(0.55, 0.55, 0.95, 1.0)),
            LerpFunctionInterval(self.setKudosTabColor, 1, Vec4(0.55, 0.55, 0.95, 1.0), Vec4(0.8, 0.8, 0.8, 1.0))
        )
        self.kudosFlashIval.loop()

    def setKudosTabColor(self, color):
        try:
            self.kudosQuestsButton['image_color'] = color
        except AttributeError:
            pass

    def stopKudosFlashIval(self):
        if self.kudosFlashIval:
            self.kudosFlashIval.finish()
            self.kudosFlashIval = None

        normalColor = (1, 1, 1, 1)
        clickColor = (0.8, 0.8, 0, 1)
        rolloverColor = (0.15, 0.82, 1.0, 1)
        disabledColor = (1.0, 0.98, 0.15, 1)
        self.kudosQuestsButton['image_color'] = normalColor
        self.kudosQuestsButton['image1_color'] = clickColor
        self.kudosQuestsButton['image2_color'] = rolloverColor
        self.kudosQuestsButton['image3_color'] = disabledColor
