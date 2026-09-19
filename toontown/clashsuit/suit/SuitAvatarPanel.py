from panda3d.core import Point3, Vec4, TextNode
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton
from direct.showbase.MessengerGlobal import messenger

from toontown.avatar import AvatarPanel
from toontown.battle.statuses import StatusEffects
from toontown.friends import FriendsListPanel
from toontown.gui.PositionedGUI import OnscreenPositionData
from toontown.suit import SuitDNA
from toontown.suit.SuitDefinitionsBase import SuitDefinitions
from toontown.toon.gui import GuiBinGlobals
from toontown.toonbase import TTLocalizer, ToontownGlobals


class SuitAvatarPanel(AvatarPanel.AvatarPanel):
    """
    This is a panel that pops up in response to clicking on a Cog
    It draws a little picture of the avatar's head, and shows you
    some info about the avatar.
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
        super().__init__(avatar, FriendsListPanel=FriendsListPanel)
        self.av = avatar
        self.avName = avatar.getName()
        self.cachedHp = None
        gui = loader.loadModel('phase_3.5/models/gui/suit_detail_panel')
        hidden = self.isHidden()

        self.managedGuiElement = DirectFrame(
            parent=base.a2dTopRight,
            relief=None,
        )

        self.frame = DirectFrame(parent=self.managedGuiElement,
                                 geom=gui.find('**/avatar_panel'),
                                 geom_scale=0.21,
                                 geom_pos=(0, 0, 0.02),
                                 relief=None)
        self.frame.setBin('sorted-gui-popup', GuiBinGlobals.SuitAvatarPanelBin)
        # Now put the avatar's head in the panel.
        self.head = self.frame.attachNewNode('head')

        if not hidden:
            for part in avatar.headParts:
                copyPart = part.copyTo(self.head)
                # Turn on depth write and test.
                copyPart.setDepthTest(1)
                copyPart.setDepthWrite(1)

        p1 = Point3()
        p2 = Point3()
        self.head.calcTightBounds(p1, p2)
        d = p2 - p1
        biggest = max(d[0], d[1], d[2], 0.01)
        s = 0.3 / biggest
        h = 180
        if not self.av.isSkeleton and self.av.style.name in ToontownGlobals.rotatedSuitHeads:
            h += ToontownGlobals.rotatedSuitHeads[self.av.style.name]
        self.head.setPosHprScale(0, 0, 0.05, h, 0, 0, s, s, s)
        # Put the avatar's name across the top.
        self.nameLabel = DirectLabel(parent=self.frame,
                                     pos=(0.0, 0, 0.36),
                                     relief=None,
                                     text=self.avName if not hidden else '???',
                                     text_font=avatar.getFont(),
                                     text_fg=Vec4(0, 0, 0, 1),
                                     text_pos=(0, 0),
                                     text_scale=0.047,
                                     text_wordwrap=7.5,
                                     text_shadow=(1, 1, 1, 1))
        level = avatar.getActualLevel()
        level_label_info = self.getCogDetails(level)
        self.levelLabel = DirectLabel(parent=self.frame,
                                      pos=(0, 0, -0.03),
                                      relief=None,
                                      text=level_label_info,
                                      text_font=avatar.getFont(),
                                      text_align=TextNode.ACenter,
                                      text_fg=Vec4(0, 0, 0, 1),
                                      text_pos=(0, 0),
                                      text_scale=0.05,
                                      text_wordwrap=8.0)
        # Re-create the corporate medallion for this suit
        if not avatar.fired and not SuitDefinitions[self.av.style.name].hideDepartment and not hidden:
            # If we have a department override, use that name and don't make an emblem.
            dept = SuitDefinitions[self.av.style.name].departmentOverride
            if not dept:
                dept = SuitDNA.getSuitDeptFullname(avatar.dna.name)
                corpIcon = self.makeMedallion()
                corpIcon.setPosHprScale(0, 0, 0, 0, 0, 0, 0, 0, 0)
                self.corpIcon = DirectLabel(parent=self.frame,
                                            geom=corpIcon,
                                            geom_scale=0.13,
                                            pos=(0, 0, -0.21),
                                            relief=None)
                # Delete it.
                corpIcon.removeNode()
            self.deptLabel = DirectLabel(parent=self.frame,
                                         pos=(0, 0, -0.31),
                                         relief=None,
                                         text=dept,
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

        self.startPositionManagement()

        self.frame.show()
        messenger.send('avPanelCreated')
        self.accept(f'suitHpChanged-{self.av.doId}', self.adjustHpText)

    def adjustHpText(self, force: bool = False):
        if not self.av:
            return
        if (not force) and (not self.isHidden()):
            if self.cachedHp == self.av.getHp():
                return
        self.cachedHp = self.av.getHp()
        labelInfo = self.getCogDetails(self.av.getActualLevel())
        self.levelLabel.setText(labelInfo)

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

    def getCogDetails(self, level):
        if self.isHidden():
            return TTLocalizer.AvatarPanelCogLevel % "???"

        output = TTLocalizer.AvatarPanelCogLevel % level
        if self.av.isMiniboss():
            output += TTLocalizer.AvatarSuitPanelManager
        elif self.av.isElite:
            output += TTLocalizer.AvatarSuitPanelExecutive

        revives = self.av.getSkeleRevives()
        if revives:
            output += f'\n{TTLocalizer.AvatarSuitPanelVersion} {revives + 1}.0'

        if self.av.getMaxHp() < 10000:
            output += f'\n{TTLocalizer.AvatarSuitPanelHP}: {self.av.getHp()}/{self.av.getMaxHp()}'
        else:
            output += f'\n{self.av.getHp()}/{self.av.getMaxHp()}'
        return output

    def cleanup(self):
        if self.frame is None:
            return
        
        self.stopPositionManagement()

        self.managedGuiElement.destroy()
        del self.managedGuiElement

        self.frame.destroy()
        del self.frame
        self.frame = None

        self.head.removeNode()
        del self.head

        super().cleanup()
        
        # Show the friend gui
        base.localAvatar.refreshOnscreenButtons()
        self.ignore(f'suitHpChanged-{self.av.doId}')

    def __handleClose(self):
        self.cleanup()
        messenger.send('avPanelClosed')

    def isHidden(self) -> bool:
        return bool(base.localAvatar.getStatusEffectOfType(StatusEffects.ObscureInformationStatusEffect))
