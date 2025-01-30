from panda3d.core import *
from direct.gui.DirectGui import *
from direct.showbase import DirectObject
from otp.avatar import Avatar
from direct.distributed import DistributedObject
from . import SuitDNA
from toontown.battle import SuitBattleGlobals
from toontown.toonbase import TTLocalizer
from direct.task.Task import Task
from direct.task.Task import Task
from direct.task.TaskManagerGlobal import taskMgr
from otp.avatar import AvatarPanel
from toontown.battle import BattleProps
from toontown.friends import FriendsListPanel
from toontown.suit import Suit
from direct.interval.IntervalGlobal import *
from direct.showbase import DirectObject
from panda3d.core import *


class SuitAvatarPanel(AvatarPanel.AvatarPanel, DirectObject.DirectObject):
    currentAvatarPanel = None

    POPUP_ANIMATION_DURATION = 0
    POPOUT_ANIMATION_DURATION = 0

    healthColors = (Vec4(0.169, 1, 0, 1),
                    Vec4(0.5, 1, 0, 1),
                    Vec4(0.75, 1, 0, 1),
                    Vec4(1, 1, 0, 1),
                    Vec4(1, 0.866, 0, 1),
                    Vec4(1, 0.7, 0, 1),
                    Vec4(1, 0.6, 0, 1),
                    Vec4(1, 0.5, 0, 1.0),
                    Vec4(1, 0.25, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0.0, 1.0, 1.0, 1),  # overheal
                    Vec4(0.553, 0, 1, 1),  # overcharge
                    Vec4(1, 0.416, 0.937, 1),  # 14 pink silhouette
                    Vec4(0, 0.361, 1, 1),
                    Vec4(1, 1, 1, 1),  # 15 blue silhouette
                    Vec4(186 / 255, 82 / 255, 1, 1))
    healthGlowColors = (Vec4(0.169, 1, 0, .5),
                        Vec4(0.5, 1, 0, .5),
                        Vec4(0.75, 1, 0, .5),
                        Vec4(1, 1, 0, .5),
                        Vec4(1, 0.866, 0, .5),
                        Vec4(1, 0.7, 0, .5),
                        Vec4(1, 0.6, 0, .5),
                        Vec4(1, 0.5, 0, .5),
                        Vec4(1, 0.25, 0, .5),
                        Vec4(1, 0, 0, .5),
                        Vec4(0, 0, 0, .5),
                        Vec4(1, 0, 0, 1),
                        Vec4(0.0, 1.0, 1.0, .5),  # overheal
                        Vec4(0.553, 0, 1, .5),  # overcharge
                        Vec4(1, 0.416, 0.937, .5),  # 14 pink silhouette
                        Vec4(0, 0.361, 1, .5),
                        Vec4(1, 1, 1, .5),  # 15 blue silhouette
                        Vec4(186 / 255, 82 / 255, 1, .5))

    def __init__(self, avatar):
        AvatarPanel.AvatarPanel.__init__(self, avatar, FriendsListPanel=FriendsListPanel)
        self.avName = avatar.getName()
        self.avatr = avatar
        gui = loader.loadModel('phase_3.5/models/gui/suit_detail_panel')
        gui.find('**/shadow').setTransparency(TransparencyAttrib.MAlpha)
        gui.find('**/shadow').setColor(1, 1, 1, 0.4)
        self.frame = DirectFrame(geom=gui.find('**/avatar_panel'), geom_scale=0.21, geom_color=(0.655, 0.686, 0.698, 1), geom_pos=(0, 0, 0.02), relief=None, pos=(-0.2348, 0, -0.475), parent=base.a2dTopRight)
        self.head = self.frame.attachNewNode('head')
        health = float(avatar.currHP) / float(avatar.maxHP)
        if health > 1.5:
            self.condition = 13
        elif health > 1.25:
            self.condition = 12
        elif health > 1.0:
            self.condition = 12
        elif health > 0.95:
            self.condition = 0
        elif health > 0.9:
            self.condition = 1
        elif health > 0.8:
            self.condition = 2
        elif health > 0.7:
            self.condition = 3
        elif health > 0.6:
            self.condition = 4
        elif health > 0.5:
            self.condition = 5
        elif health > 0.4:
            self.condition = 6
        elif health > 0.3:
            self.condition = 7
        elif health > 0.2:
            self.condition = 8
        elif health > 0.1:
            self.condition = 9
        elif health > 0.0:
            self.condition = 10
        else:
            self.condition = 11
        self.avatar = avatar
        if avatar.isVirtual:
            self.head.setColor(1, 1, 1, 1)
            self.head.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
            for part in avatar.headParts:
                copyPart = part.copyTo(self.head)
                copyPart.setDepthTest(1)
                copyPart.setDepthWrite(1)
        else:
            for part in avatar.headParts:
                copyPart = part.copyTo(self.head)
                copyPart.setDepthTest(1)
                copyPart.setDepthWrite(1)

        p1 = Point3()
        p2 = Point3()
        self.head.calcTightBounds(p1, p2)
        d = p2 - p1
        biggest = max(d[0], d[1], d[2])
        s = 0.3 / biggest
        if self.avatar.dna.name == 'ptr' and not avatar.isSkeleton:
            self.head.setPosHprScale(0, 0, 0.05, 270, 0, 0, s, s, s)
        elif self.avatar.dna.name == 'dfh' and not avatar.isSkeleton:
            self.head.setPosHprScale(0, 0, 0.05, 270, 0, 0, s, s, s)
        elif self.avatar.dna.name == 'dvp' and not avatar.isSkeleton:
            self.head.setPosHprScale(0, 0, 0.09, 180, 0, 0, s, s, s)
        elif self.avatar.dna.name == 'th' and not avatar.isSkeleton:
            self.head.setPosHprScale(0, 0, 0.09, 180, 0, 0, s, s, s)
        else:
            self.head.setPosHprScale(0, 0, 0.05, 180, 0, 0, s, s, s)
        self.nameLabel = DirectLabel(parent=self.frame, pos=(0, 0, 0.36), relief=None,
                                     text=SuitBattleGlobals.SuitAttributes[avatar.dna.name]['name'],
                                     text_font=avatar.getFont(), text_pos=(0, 0),
                                     text_scale=0.0475, text_wordwrap=8, text_shadow=(1, 1, 1, 1))
        if avatar.isFired:
            level = str(avatar.getActualLevel())
        elif avatar.getExecutive() and not avatar.getManager():
            level = str(avatar.getActualLevel()) + TTLocalizer.ExecutivePostFix
        elif avatar.getGovernaught() and not avatar.getExecutive() and not avatar.getManager():
            level = str(avatar.getActualLevel()) + TTLocalizer.GovernaughtPostFix
        elif avatar.getManager():
            level = str(avatar.getActualLevel()) + TTLocalizer.ManagerPostFix
        else:
            level = str(avatar.getActualLevel())
        revives = avatar.getSkeleRevives() + 1
        name = avatar.dna.name
        maxHP = avatar.maxHP
        if avatar.currHP > 0:
            HP = avatar.currHP
        else:
            HP = 0
        if avatar.isFired:
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.08), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.08), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif revives > 2 and avatar.isVirtual and avatar.maxHP > 9999:
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.08), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.08), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif revives > 2 and avatar.isVirtual:
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.08), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.08), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif revives > 2 and avatar.isSkeleton and avatar.maxHP > 9999:
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.13), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.13), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level + '\nVersion %s.0' % (revives - 1),
                                          text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif revives > 2 and avatar.isSkeleton and avatar.maxHP > 9999:
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.08), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.08), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif revives > 2 and avatar.isSkeleton:
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.13), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.13), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level + '\nVersion %s.0' % (
                                                      revives - 1),
                                          text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif revives > 1 and avatar.isVirtual:
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.08), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.08), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif revives > 1 and avatar.isSkeleton and avatar.isRevived:
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.08), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.08), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif revives > 1 and avatar.maxHP > 9999:
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.13), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.13), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level + '\nVersion %s.0' % revives, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif revives > 1 and avatar.maxHP <= 9999:
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.13), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.13), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level + '\nVersion %s.0' % revives, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif avatar.dna.name == 'dsf':
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.13), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.13), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif avatar.dna.name == 'tcm':
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.13), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.13), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif avatar.dna.name == 'crf':
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.13), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.13), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif avatar.maxHP >= 9999:
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.08), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.08), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        elif avatar.currHP >= 9999:
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.08), relief=DGG.SUNKEN, value=100,
                                       frameSize=(-1.9, 1.9, -0.2, 0.4),
                                       borderWidth=(0.02, 0.02), scale=0.1,
                                       frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.08), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        else:
            healthBar2 = DirectWaitBar(parent=self.frame, pos=(0, 0, -0.08), relief=DGG.SUNKEN, value=100,
                                            frameSize=(-1.9, 1.9, -0.2, 0.4),
                                            borderWidth=(0.02, 0.02), scale=0.1,
                                            frameColor=(0.5, 0.5, 0.5, .6), barColor=(1, 1, 1.0, 1),  text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0), text_scale=0.5, text_wordwrap=7.5)
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.08), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                      text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.03), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        self.healthBar2 = healthBar2
        self.healthBar2.setProp('barColor', self.healthColors[self.condition])
        self.healthBar2.setProp('value', self.avatar.currHP)
        self.healthBar2.setProp('range', self.avatar.getMaxHP())
        dept = SuitDNA.getSuitDeptFullname(avatar.dna.name)
        healthGui = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        glow = BattleProps.globalPropPool.getProp('glow')
        glow.setScale(0.25)
        glow.setPos(-0.0075, 0, 0.02)
        glow.setColor(Vec4(1, 1, 1, 0.5))
        button = healthGui.find('**/minnieCircle')
        button.setScale(0.75)
        button.setH(180)
        button.setColor(Vec4(1, 1, 1, 1))
        glow.reparentTo(button)
        self.healthNode = self.frame.attachNewNode('health')
        self.healthNode.setPos(-0.0075, 0, -0.22)
        button.reparentTo(self.healthNode)
        corpIcon = avatar.corpMedallion.copyTo(hidden)
        corpIcon.setPosHprScale(0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.corpIcon = DirectLabel(parent=self.frame, geom=corpIcon, geom_scale=0.13, pos=(0, 0, -0.21), relief=None)
        self.button = button
        self.glow = glow
        if avatar.isFired:
            self.deptLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.31), relief=None,
                                         text='',
                                         text_font=avatar.getFont(), text_align=TextNode.ACenter,
                                         text_fg=Vec4(0, 0, 0, 1),
                                         text_pos=(0, 0), text_scale=0.05, text_wordwrap=8.0)
        else:
            self.deptLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.31), relief=None,
                                         text=dept,
                                         text_font=avatar.getFont(), text_align=TextNode.ACenter,
                                         text_fg=Vec4(0, 0, 0, 1),
                                         text_pos=(0, 0), text_scale=0.05, text_wordwrap=8.0)
        self.closeButton = DirectButton(parent=self.frame, relief=None, pos=(0.0, 0, -0.36),
                                        text=TTLocalizer.AvatarPanelCogDetailClose, text_font=avatar.getFont(),
                                        text0_fg=Vec4(0, 0, 0, 1), text1_fg=Vec4(0.5, 0, 0, 1),
                                        text2_fg=Vec4(1, 0, 0, 1), text_pos=(0, 0), text_scale=0.05,
                                        command=self.__handleClose)


        self.condition = avatar.healthCondition


        self.maxHp = avatar.maxHP

        self.hp = self.maxHp

        self.currHp = avatar.currHP

        #self.updateHealthBar(self.maxHp)



        gui.removeNode()
        base.localAvatar.obscureFriendsListButton(1)

        #create a LerpScaleInterval that scales the frame from 0 to 1
        self.__updateHp(self.currHp, self.maxHp, 0)

        self.currentInterval = self.__getOpenSequence()
        self.currentInterval.start()

        self.labelInterval = None

        self.healthBarInterval = None

        self.blinkTask = None

        self.frame.setBin("gui-popup", 0)
        self.frame.show()
        messenger.send('avPanelDone')

        self.accept(avatar.uniqueName('suitHpUpdate'), self.__updateHp)
        return


    def __updateHp(self, currHp, maxHp, delta):
        health = float(self.avatar.currHP) / float(self.avatar.maxHP)
        if health > 1.5:
            condition = 13
        elif health > 1.25:
            condition = 12
        elif health > 1.0:
            condition = 12
        elif health > 0.95:
            condition = 0
        elif health > 0.9:
            condition = 1
        elif health > 0.8:
            condition = 2
        elif health > 0.7:
            condition = 3
        elif health > 0.6:
            condition = 4
        elif health > 0.5:
            condition = 5
        elif health > 0.4:
            condition = 6
        elif health > 0.3:
            condition = 7
        elif health > 0.2:
            condition = 8
        elif health > 0.1:
            condition = 9
        elif health > 0.0:
            condition = 10
        else:
            condition = 11
        def __updateLabel(tempHp):
            if tempHp > 9999:
                #self.hpLabel['text'] = TTLocalizer.AvatarPanelCogHealth2 % (int(tempHp), maxHp)
                self.healthBar2['text'] = TTLocalizer.AvatarPanelCogHealth2 % (int(tempHp), maxHp)
            elif maxHp > 9999 and tempHp <= 0:
                #self.hpLabel['text'] = TTLocalizer.AvatarPanelCogHealth2 % (0, maxHp)
                self.healthBar2['text'] = TTLocalizer.AvatarPanelCogHealth2 % (0, maxHp)
            elif maxHp > 9999:
                self.healthBar2['text'] = TTLocalizer.AvatarPanelCogHealth2 % (int(tempHp), maxHp)
                #self.hpLabel['text'] = TTLocalizer.AvatarPanelCogHealth2 % (int(tempHp), maxHp)
            elif tempHp <= 0:
                self.healthBar2['text'] = TTLocalizer.AvatarPanelCogHealth2 % (0, maxHp)
                #self.hpLabel['text'] = TTLocalizer.AvatarPanelCogHP % (0, maxHp)
            else:
                self.healthBar2['text'] = TTLocalizer.AvatarPanelCogHealth2 % (int(tempHp), maxHp)
                #self.hpLabel['text'] = TTLocalizer.AvatarPanelCogHP % (int(tempHp), maxHp)

        self.labelInterval = Parallel(
                LerpColorScaleInterval(self.hpLabel, duration=0, startColorScale=(1, 0, 0, 1), colorScale=(1, 1, 1, 1), blendType='easeInOut'),
            Func(self.healthBar2.setProp, 'barColor', self.healthColors[condition]),
                 Func(self.healthBar2.setProp, 'value', (int(currHp))),
                LerpFunctionInterval(__updateLabel, duration=0, fromData=currHp+delta, toData=currHp, blendType='easeInOut')
            )
        if condition == 10 and self.avatar.isVirtual:
            blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
            #blinkTask2 = Task.loop(Task(self.__blinkRedVirtual), Task.pause(0.75), Task(self.__blinkGrayVirtual), Task.pause(0.1))
            taskMgr.add(blinkTask, self.frame.uniqueName('blink-task'))
            #taskMgr.add(blinkTask2, self.frame.uniqueName('blink-task'))
            self.colorInterval = Parallel(
                LerpColorScaleInterval(self.head, duration=0, colorScale=(self.healthColors[9]),
                                       blendType='easeInOut'))
            self.colorInterval.start()
        elif condition == 11 and self.avatar.isVirtual:
            blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
            #blinkTask2 = Task.loop(Task(self.__blinkRedVirtual), Task.pause(0.25), Task(self.__blinkGrayVirtual), Task.pause(0.1))
            taskMgr.add(blinkTask, self.frame.uniqueName('blink-task'))
            #taskMgr.add(blinkTask2, self.frame.uniqueName('blink-task'))
            self.colorInterval = Parallel(
                LerpColorScaleInterval(self.head, duration=0, colorScale=(self.healthColors[9]),
                                       blendType='easeInOut'))
            self.colorInterval.start()
        elif condition == 10:
            blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(blinkTask, self.frame.uniqueName('blink-task'))
        elif condition == 11:
            blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(blinkTask, self.frame.uniqueName('blink-task'))
        elif self.avatar.isVirtual:
            self.colorInterval = Parallel(
                LerpColorScaleInterval(self.button, duration=0, colorScale=(self.healthColors[condition]),
                                       blendType='easeInOut'),
                LerpColorScaleInterval(self.head, duration=0, colorScale=(self.healthColors[condition]),
                                       blendType='easeInOut'),
                LerpColorScaleInterval(self.glow, duration=0, colorScale=(self.healthColors[condition]),
                                       blendType='easeInOut'))
            taskMgr.remove(self.frame.uniqueName('blink-task'))
            self.colorInterval.start()
        else:
            self.colorInterval = Parallel(
                LerpColorScaleInterval(self.button, duration=0, colorScale=(self.healthColors[condition]),
                                       blendType='easeInOut'),
                LerpColorScaleInterval(self.glow, duration=0, colorScale=(self.healthColors[condition]),
                                       blendType='easeInOut'))
            taskMgr.remove(self.frame.uniqueName('blink-task'))
            self.colorInterval.start()
        self.labelInterval.start()
        #self.hideCorpIcon.start()

    def __blinkRed(self, task):
        self.button.setColor(self.healthColors[9], 1)
        self.glow.setColor(self.healthGlowColors[9], 1)

    def __blinkGray(self, task):
        self.button.setColor(self.healthColors[10], 1)
        self.glow.setColor(self.healthGlowColors[10], 1)

    def __blinkRedVirtual(self, task):
        self.head.setColor(self.healthColors[9], 1)

    def __blinkGrayVirtual(self, task):
        self.head.setColor(self.healthColors[10], 1)


    def __getOpenSequence(self):
        return Sequence(
            LerpScaleInterval(self.frame, self.POPUP_ANIMATION_DURATION, Vec3(1.2, 1.2, 1.2), Vec3(0, 0, 0), blendType='easeIn'),
            LerpScaleInterval(self.frame, self.POPUP_ANIMATION_DURATION/2.0, Vec3(1, 1, 1), Vec3(1.2, 1.2, 1.2), blendType='easeInOut'),
        )

    def __getCloseSequence(self):
        return Sequence(
            LerpScaleInterval(self.frame, self.POPOUT_ANIMATION_DURATION, Vec3(1.2, 1.2, 1.2), Vec3(1, 1, 1), blendType='easeIn'),
            LerpScaleInterval(self.frame, self.POPOUT_ANIMATION_DURATION/2.0, Vec3(0, 0, 0), Vec3(1.2, 1.2, 1.2),blendType='easeInOut'),
            Func(self.cleanup),
        )

    def startBlinkTask(self):
        self.blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
        taskMgr.add(self.blinkTask, 'bosshealthbar-blink-task')

    def stopBlinkTask(self):
        taskMgr.remove('bosshealthbar-blink-task')
        self.blinkTask = None

    def __cleanupSequence(self):

        if self.labelInterval:
            self.labelInterval.finish()
            self.labelInterval = None

        if self.healthBarInterval:
            self.healthBarInterval.finish()
            self.healthBarInterval = None

        if self.blinkTask:
            self.blinkTask.finish()
            self.blinkTask = None

    def cleanup(self):
        self.ignoreAll()
        self.__cleanupSequence()

        if self.frame:
            self.frame.destroy()
            self.frame = None
            base.localAvatar.obscureFriendsListButton(-1)

        if self.head:
            self.head.removeNode()
            self.head = None

        AvatarPanel.AvatarPanel.cleanup(self)
        self.panelNoneFunc()
        return
    
    def panelNoneFunc(self):
        AvatarPanel.currentAvatarPanel = None
        return

    def __handleClose(self):
        self.__cleanupSequence()

        # If someone abuses the GUI enough, frame could get deleted before we have a chance to play an animation :(
        if self.frame is None:
            self.cleanup()
            return

        self.currentInterval = self.__getCloseSequence()
        self.currentInterval.start()
        return

        return

    @classmethod
    def getRevives(cls, cog):
        return cog.getSkeleRevives()
