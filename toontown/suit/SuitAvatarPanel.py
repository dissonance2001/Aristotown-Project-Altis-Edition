from pandac.PandaModules import *
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from direct.showbase import DirectObject
from otp.avatar import Avatar
from direct.distributed import DistributedObject
from toontown.suit import SuitDNA
from toontown.battle import SuitBattleGlobals
from toontown.toonbase import TTLocalizer
from otp.avatar import AvatarPanel
from toontown.friends import FriendsListPanel

class SuitAvatarPanel(AvatarPanel.AvatarPanel):
    currentAvatarPanel = None

    def __init__(self, avatar):
        AvatarPanel.AvatarPanel.__init__(self, avatar, FriendsListPanel=FriendsListPanel)
        self.avName = avatar.getName()
        gui = loader.loadModel('phase_3.5/models/gui/suit_detail_panel')
        self.frame = DirectFrame(geom=gui.find('**/avatar_panel'), geom_scale=0.21, geom_pos=(0, 0, 0.02), relief=None, pos=(1.1, 100, 0.525))
        disabledImageColor = Vec4(1, 1, 1, 0.4)
        text0Color = Vec4(1, 1, 1, 1)
        text1Color = Vec4(0.5, 1, 0.5, 1)
        text2Color = Vec4(1, 1, 0.5, 1)
        text3Color = Vec4(1, 1, 1, 0.2)
        self.head = self.frame.attachNewNode('head')
        for part in avatar.headParts:
            copyPart = part.copyTo(self.head)
            copyPart.setDepthTest(1)
            copyPart.setDepthWrite(1)

        p1 = Point3()
        p2 = Point3()
        self.head.calcTightBounds(p1, p2)
        d = p2 - p1
        biggest = max(d[0], d[1], d[2])
        if avatar.isSkeleton and avatar.dna.body == 'a' and not self.avatar.dna.dept == 'l' and not self.avatar.dna.dept == 'g'  and not self.avatar.dna.name == 'cg' and not self.avatar.dna.name == 'blr' and not self.avatar.dna.name == 'dsk' and not self.avatar.dna.name == 'ts' and not self.avatar.dna.name == 'jur'\
                and not self.avatar.dna.name == 'laa' and not self.avatar.dna.name == 'csh' and not self.avatar.dna.name == 'bgr' and not self.avatar.dna.name == 'tcc'\
                and not self.avatar.dna.name == 'fb' and not self.avatar.dna.name == 'jl' and not self.avatar.dna.name == 'gb' and not self.avatar.dna.name == 'lbs'\
                and not self.avatar.dna.name == 'fas' and not self.avatar.dna.name == 'mdr' and not self.avatar.dna.name == 'nar' and not self.avatar.dna.name == 'fd'\
                and not self.avatar.dna.name == 'gkp' and not self.avatar.dna.name == 'ddv' and not self.avatar.dna.name == 'sya' and not self.avatar.dna.name == 'ant' and not self.avatar.dna.name == 'cm':
            s = 0.4 / biggest
        elif avatar.isSkeleton and avatar.dna.body == 'a' and not self.avatar.dna.name == 'cg' and not self.avatar.dna.name == 'blr' and not self.avatar.dna.name == 'dsk' and not self.avatar.dna.name == 'ts' and not self.avatar.dna.name == 'jur'\
                and not self.avatar.dna.name == 'laa' and not self.avatar.dna.name == 'csh' and not self.avatar.dna.name == 'bgr' and not self.avatar.dna.name == 'tcc'\
                and not self.avatar.dna.name == 'fb' and not self.avatar.dna.name == 'jl' and not self.avatar.dna.name == 'gb' and not self.avatar.dna.name == 'lbs'\
                and not self.avatar.dna.name == 'fas' and not self.avatar.dna.name == 'mdr' and not self.avatar.dna.name == 'nar' and not self.avatar.dna.name == 'fd'\
                and not self.avatar.dna.name == 'gkp' and not self.avatar.dna.name == 'ddv' and not self.avatar.dna.name == 'sya' and not self.avatar.dna.name == 'ant' and not self.avatar.dna.name == 'cm':
            s = 0.5 / biggest
        elif avatar.isSkeleton and avatar.dna.body == 'b' and not self.avatar.dna.dept == 'l' and not self.avatar.dna.dept == 'g' and not self.avatar.dna.name == 'cg' and not self.avatar.dna.name == 'blr' and not self.avatar.dna.name == 'dsk' and not self.avatar.dna.name == 'ts' and not self.avatar.dna.name == 'jur'\
                and not self.avatar.dna.name == 'laa' and not self.avatar.dna.name == 'csh' and not self.avatar.dna.name == 'bgr' and not self.avatar.dna.name == 'tcc'\
                and not self.avatar.dna.name == 'fb' and not self.avatar.dna.name == 'jl' and not self.avatar.dna.name == 'gb' and not self.avatar.dna.name == 'lbs'\
                and not self.avatar.dna.name == 'fas' and not self.avatar.dna.name == 'mdr' and not self.avatar.dna.name == 'nar' and not self.avatar.dna.name == 'fd'\
                and not self.avatar.dna.name == 'gkp' and not self.avatar.dna.name == 'ddv' and not self.avatar.dna.name == 'sya' and not self.avatar.dna.name == 'ant' and not self.avatar.dna.name == 'cm':
            s = 0.6 / biggest
        elif avatar.isSkeleton and avatar.dna.body == 'c'  and not self.avatar.dna.dept == 'l' and not self.avatar.dna.dept == 'g'  and not self.avatar.dna.name == 'cg' and not self.avatar.dna.name == 'blr' and not self.avatar.dna.name == 'dsk' and not self.avatar.dna.name == 'ts' and not self.avatar.dna.name == 'jur'\
                and not self.avatar.dna.name == 'laa' and not self.avatar.dna.name == 'csh' and not self.avatar.dna.name == 'bgr' and not self.avatar.dna.name == 'tcc'\
                and not self.avatar.dna.name == 'fb' and not self.avatar.dna.name == 'jl' and not self.avatar.dna.name == 'gb' and not self.avatar.dna.name == 'lbs'\
                and not self.avatar.dna.name == 'fas' and not self.avatar.dna.name == 'mdr' and not self.avatar.dna.name == 'nar' and not self.avatar.dna.name == 'fd'\
                and not self.avatar.dna.name == 'gkp' and not self.avatar.dna.name == 'ddv' and not self.avatar.dna.name == 'sya' and not self.avatar.dna.name == 'ant' and not self.avatar.dna.name == 'cm':
            s = 0.6 / biggest
        elif avatar.isSkeleton and avatar.dna.body == 'b' and not self.avatar.dna.name == 'cg' and not self.avatar.dna.name == 'blr' and not self.avatar.dna.name == 'dsk' and not self.avatar.dna.name == 'ts' and not self.avatar.dna.name == 'jur' \
                 and not self.avatar.dna.name == 'laa' and not self.avatar.dna.name == 'csh' and not self.avatar.dna.name == 'bgr' and not self.avatar.dna.name == 'tcc' \
                 and not self.avatar.dna.name == 'fb' and not self.avatar.dna.name == 'jl' and not self.avatar.dna.name == 'gb' and not self.avatar.dna.name == 'lbs' \
                 and not self.avatar.dna.name == 'fas' and not self.avatar.dna.name == 'mdr' and not self.avatar.dna.name == 'nar' and not self.avatar.dna.name == 'fd' \
                 and not self.avatar.dna.name == 'gkp' and not self.avatar.dna.name == 'ddv' and not self.avatar.dna.name == 'sya' and not self.avatar.dna.name == 'ant' and not self.avatar.dna.name == 'cm':
            s = 0.5 / biggest
        elif avatar.isSkeleton and avatar.dna.body == 'c' and not self.avatar.dna.name == 'cg' and not self.avatar.dna.name == 'blr' and not self.avatar.dna.name == 'dsk' and not self.avatar.dna.name == 'ts' and not self.avatar.dna.name == 'jur' \
                and not self.avatar.dna.name == 'laa' and not self.avatar.dna.name == 'csh' and not self.avatar.dna.name == 'bgr' and not self.avatar.dna.name == 'tcc' \
                and not self.avatar.dna.name == 'fb' and not self.avatar.dna.name == 'jl' and not self.avatar.dna.name == 'gb' and not self.avatar.dna.name == 'lbs' \
                and not self.avatar.dna.name == 'fas' and not self.avatar.dna.name == 'mdr' and not self.avatar.dna.name == 'nar' and not self.avatar.dna.name == 'fd' \
                and not self.avatar.dna.name == 'gkp' and not self.avatar.dna.name == 'ddv' and not self.avatar.dna.name == 'sya' and not self.avatar.dna.name == 'ant' and not self.avatar.dna.name == 'cm':
            s = 0.5 / biggest
        else:
            s = 0.3 / biggest
        if self.avatar.dna.name == 'ptr' and not avatar.isSkeleton:
            self.head.setPosHprScale(0, 0, 0.04, 270, 0, 0, s, s, s)
        elif self.avatar.dna.name == 'dfh' and not avatar.isSkeleton:
            self.head.setPosHprScale(0, 0, 0.04, 270, 0, 0, s, s, s)
        else:
            self.head.setPosHprScale(0, 0, 0.04, 180, 0, 0, s, s, s)
        self.nameLabel = DirectLabel(parent=self.frame, pos=(0, 0, 0.35), relief=None, text=SuitBattleGlobals.SuitAttributes[avatar.dna.name]['name'],
                                     text_font=avatar.getFont(), text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0),
                                     text_scale=0.05, text_wordwrap=8.0, text_shadow=(1, 1, 1, 1))
        if avatar.getExecutive() and not avatar.getManager():
            level = str(avatar.getActualLevel()) + TTLocalizer.ExecutivePostFix
        elif avatar.getGovernaught() and not avatar.getExecutive() and not avatar.getManager():
            level = str(avatar.getActualLevel()) + TTLocalizer.GovernaughtPostFix
        elif avatar.getManager():
            level = str(avatar.getActualLevel()) + TTLocalizer.ManagerPostFix
        else:
            level = str(avatar.getActualLevel())
        relativelevel = avatar.getLevel()
        revives = avatar.getMaxSkeleRevives() + 1
        attributes = SuitBattleGlobals.SuitAttributes[avatar.getStyleName()]
        if avatar.currHP > 0:
            health = avatar.currHP
        else:
            health = 0
        maxHealth = avatar.maxHP
        currHP = attributes['hp'][relativelevel]
        maxHP = attributes['hp'][relativelevel]
        dept = SuitDNA.getSuitDeptFullname(avatar.dna.name)
        if revives > 1:
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.015), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level + TTLocalizer.AvatarPanelCogRevives % revives,
                                          text_font=avatar.getFont(), text_align=TextNode.ACenter,
                                          text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0), text_scale=0.05, text_wordwrap=8.0)
        elif avatar.dna.name == 'crf':
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.015), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level,
                                          text_font=avatar.getFont(), text_align=TextNode.ACenter,
                                          text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0), text_scale=0.05, text_wordwrap=8.0)
        elif avatar.dna.name == 'tcm':
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.015), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level,
                                          text_font=avatar.getFont(), text_align=TextNode.ACenter,
                                          text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0), text_scale=0.05, text_wordwrap=8.0)
        elif avatar.dna.name == 'cm':
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.015), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level,
                                          text_font=avatar.getFont(), text_align=TextNode.ACenter,
                                          text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0), text_scale=0.05, text_wordwrap=8.0)
        else:
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.06), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        corpIcon = avatar.corpMedallion.copyTo(hidden)
        corpIcon.setPosHprScale(0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.corpIcon = DirectLabel(parent=self.frame, geom=corpIcon, geom_scale=0.13, pos=(0, 0, -0.20), relief=None)
        if avatar.currHP >= 9999 and revives > 1:
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.115), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (health, maxHealth),
                                       text_font=avatar.getFont(), text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5, text_shadow=(1, 1, 1, 1))
        elif avatar.maxHP >= 9999 and revives > 1:
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.115), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (health, maxHealth),
                                       text_font=avatar.getFont(), text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5, text_shadow=(1, 1, 1, 1))
        elif avatar.maxHP >= 9999:
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.11), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (health, maxHealth),
                                       text_font=avatar.getFont(), text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5, text_shadow=(1, 1, 1, 1))
        elif avatar.currHP >= 9999:
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.11), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (health, maxHealth),
                                       text_font=avatar.getFont(), text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5, text_shadow=(1, 1, 1, 1))
        elif revives > 1:
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.115), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth % (health, maxHealth),
                                       text_font=avatar.getFont(), text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5, text_shadow=(1, 1, 1, 1))
        else:
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.11), relief=None,
                                   text=TTLocalizer.AvatarPanelCogHealth % (health, maxHealth),
                                   text_font=avatar.getFont(), text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5, text_shadow=(1, 1, 1, 1))
        self.deptLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.30), relief=None, text=dept,
                                     text_font=avatar.getFont(), text_align=TextNode.ACenter, text_fg=Vec4(0, 0, 0, 1),
                                     text_pos=(0, 0), text_scale=0.05, text_wordwrap=8.0)
        self.closeButton = DirectButton(parent=self.frame, relief=None, pos=(0.0, 0, -0.35),
                                        text=TTLocalizer.AvatarPanelCogDetailClose, text_font=avatar.getFont(),
                                        text0_fg=Vec4(0, 0, 0, 1), text1_fg=Vec4(0.5, 0, 0, 1),
                                        text2_fg=Vec4(1, 0, 0, 1), text_pos=(0, 0), text_scale=0.05,
                                        command=self.__handleClose)
        gui.removeNode()
        menuX = -0.05
        menuScale = 0.064
        base.localAvatar.obscureFriendsListButton(1)
        self.frame.show()
        messenger.send('avPanelDone')
        self.frame.reparentTo(base.a2dTopRight)
        self.frame.setPos(-0.25, 0, -0.5)


    def cleanup(self):
        if self.frame == None:
            return
        self.frame.destroy()
        del self.frame
        self.frame = None
        self.head.removeNode()
        del self.head
        base.localAvatar.obscureFriendsListButton(-1)
        AvatarPanel.AvatarPanel.cleanup(self)
        return

    def __handleClose(self):
        self.cleanup()
        AvatarPanel.currentAvatarPanel = None
        return
