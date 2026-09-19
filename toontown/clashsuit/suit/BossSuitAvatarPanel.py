from direct.gui.DirectGui import *
from panda3d.core import *
from panda3d.physics import Physical

from toontown.gui.PositionedGUI import OnscreenPositionData
from toontown.suit import SuitDNA
from toontown.suit import BossCog
from toontown.shtiker import CogPageGlobals as CPG
from toontown.toonbase import TTLocalizer
from toontown.avatar import AvatarPanel
from toontown.friends import FriendsListPanel


class BossSuitAvatarPanel(AvatarPanel.AvatarPanel):
    """
    This is a panel that pops up in response to clicking on a Cog
    Boss. It draws a little picture of the avatar's head, and shows
    you some info about the boss avatar.
    """

    GUI_BOUNDS = OnscreenPositionData(
        right=0.23,
        left=0.25,
        top=0.46,
        down=0.44,
    )

    # Limit to only have one avatar panel at a time
    currentAvatarPanel = None

    def __init__(self, avatar):
        AvatarPanel.AvatarPanel.__init__(self, avatar, FriendsListPanel=FriendsListPanel)
        self.av = avatar
        self.avName = avatar.getName()
        gui = loader.loadModel('phase_3.5/models/gui/suit_detail_panel')
        self.managedGuiElement = DirectFrame(
            parent=base.a2dTopRight,
            relief=None,
        )
        self.frame = DirectFrame(parent=self.managedGuiElement,
                                 geom=gui.find('**/avatar_panel'),
                                 geom_scale=0.21,
                                 geom_pos=(0, 0, 0.02),
                                 relief=None)
        # Now put the avatar's head in the panel.
        self.head = self.frame.attachNewNode('head')
        dept = avatar.style.dept
        # Handle this a little differently than the normal panel due to physics objects like the cashbot safes.
        copyPart = loader.loadModel(BossCog.ModelDict[dept] + '-head-zero').copyTo(self.head)
        # Turn on depth write and test.
        copyPart.setDepthTest(1)
        copyPart.setDepthWrite(1)

        p1 = Point3()
        p2 = Point3()
        self.head.calcTightBounds(p1, p2)
        d = p2 - p1
        biggest = max(d[0], d[1], d[2])
        scaleFactor = 0.285 if dept == 'l' else 0.335
        s = scaleFactor / biggest
        self.head.setPosHprScale(0, 0, 0.05, -90, 0, 270, s, s, s)
        # Put the avatar's name across the top.
        nameText = CPG.bossAbrToFull[CPG.deptToBossAbr[dept]]
        self.nameLabel = DirectLabel(parent=self.frame,
                                     pos=(0.0, 0, 0.36),
                                     relief=None,
                                     text=nameText,
                                     text_font=avatar.getFont(),
                                     text_fg=Vec4(0, 0, 0, 1),
                                     text_pos=(0, 0),
                                     text_scale=0.047,
                                     text_wordwrap=7.5,
                                     text_shadow=(1, 1, 1, 1))
        # Re-create the corporate medallion for this suit
        corpIcon = self.makeMedallion()
        corpIcon.setPosHprScale(0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.corpIcon = DirectLabel(parent=self.frame,
                                    geom=corpIcon,
                                    geom_scale=0.18,
                                    pos=(0, 0, -0.07),
                                    relief=None)
        # Delete it.
        corpIcon.removeNode()
        deptText = TTLocalizer.HeadOfTheDepartment % SuitDNA.suitDeptFullnames[dept]
        self.deptLabel = DirectLabel(parent=self.frame,
                                     pos=(0, 0, -0.205),
                                     relief=None,
                                     text=deptText,
                                     text_font=avatar.getFont(),
                                     text_align=TextNode.ACenter,
                                     text_fg=Vec4(0, 0, 0, 1),
                                     text_pos=(0, 0),
                                     text_scale=0.05,
                                     text_wordwrap=8.0)
        self.closeButton = DirectButton(parent=self.frame,
                                        relief=None,
                                        pos=(0.0, 0, -0.36),
                                        text=TTLocalizer.AvatarPanelCogDetailClose,
                                        text_font=avatar.getFont(),
                                        text0_fg=Vec4(0, 0, 0, 1),
                                        text1_fg=Vec4(0.5, 0, 0, 1),
                                        text2_fg=Vec4(1, 0, 0, 1),
                                        text_pos=(0, 0),
                                        text_scale=0.05,
                                        command=self.__handleClose)
        gui.removeNode()
        # hide the friend gui
        base.localAvatar.obscureFriendsListButton(1)

        self.frame.show()
        self.startPositionManagement()
        messenger.send('avPanelCreated', ['s'])

    def makeMedallion(self):
        icons = loader.loadModel('phase_3/models/gui/cog_icons')
        dept = self.av.style.dept
        if dept == 'c':
            corpMedallion = icons.find('**/CorpIcon')
        elif dept == 's':
            corpMedallion = icons.find('**/SalesIcon')
        elif dept == 'l':
            corpMedallion = icons.find('**/LegalIcon')
        elif dept == 'm':
            corpMedallion = icons.find('**/MoneyIcon')
        elif dept == 'g':
            corpMedallion = icons.find('**/BoardIcon')

        corpMedallion.setPosHprScale(0.02, 0.05, 0.04, 180.0, 0.0, 0.0, 0.51, 0.51, 0.51)
        icons.removeNode()
        return corpMedallion

    def cleanup(self):
        if self.frame is None:
            return
        if not self.managedGuiElement:
            return
        self.stopPositionManagement()
        self.managedGuiElement.destroy()
        del self.managedGuiElement
        self.frame.destroy()
        del self.frame
        self.frame = None
        self.head.removeNode()
        del self.head
        # Show the friend gui
        # base.localAvatar.obscureFriendsListButton(-1)
        AvatarPanel.AvatarPanel.cleanup(self)
        base.localAvatar.refreshOnscreenButtons()
        return

    def __handleClose(self):
        self.cleanup()
        messenger.send('avPanelClosed')
        AvatarPanel.currentAvatarPanel = None
        return
