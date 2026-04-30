from panda3d.core import *
from direct.gui.DirectGui import *
from direct.showbase import DirectObject
from otp.avatar import Avatar
from direct.distributed import DistributedObject
from . import SuitDNA
from toontown.battle import SuitBattleGlobals
from toontown.toonbase import TTLocalizer
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

    healthColors = (Vec4(0, 1, 0.078, 1),
                    Vec4(0.388, 1, 0, 1),
                    Vec4(0.686, 1, 0, 1),
                    Vec4(0.882, 1, 0, 1),
                    Vec4(0.988, 1, 0, 1),
                    Vec4(1, 0.831, 0, 1),
                    Vec4(1, 0.714, 0, 1),
                    Vec4(1, 0.533, 0, 1.0),
                    Vec4(1, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0.3, 0.3, 0.3, 1),  # out
                    Vec4(1, 0, 0, 1),  # 12
                    Vec4(0.0, 1.0, 1.0, 1),  # overheal
                    Vec4(0.553, 0, 1, 1),  # overcharge
                    Vec4(1, 0.6, 0.89, 1),  # 14 pink silhouette
                    Vec4(0, 0.361, 1, 1),
                    Vec4(1, 1, 1, 1),  # 15 blue silhouette
                    Vec4(186 / 255, 82 / 255, 1, 1),
                    Vec4(0.702, 0, 1, 1),
                    Vec4(1, 1, 1, 1),
                    Vec4(1, 0, 0.906, 1))  # 18 white (20 magenta sil)
    healthGlowColors = (Vec4(0, 1, 0.078, 1),
                        Vec4(0.388, 1, 0, 1),
                        Vec4(0.686, 1, 0, 1),
                        Vec4(0.882, 1, 0, 1),
                        Vec4(0.988, 1, 0, 1),
                        Vec4(1, 0.831, 0, 1),
                        Vec4(1, 0.714, 0, 1),
                        Vec4(1, 0.533, 0, 1.0),
                        Vec4(1, 0, 0, 1),
                        Vec4(1, 0, 0, 1),
                        Vec4(0, 0, 0, 0),  # out
                        Vec4(1, 0, 0, 1),
                        Vec4(0.0, 1.0, 1.0, 1),  # overheal
                        Vec4(0.553, 0, 1, 1),  # overcharge
                        Vec4(1, 0.6, 0.89, 1),  # 14 pink silhouette
                        Vec4(0, 0.361, 1, 1),
                        Vec4(1, 1, 1, 1),  # 15 blue silhouette
                        Vec4(186 / 255, 82 / 255, 1, 1),
                        Vec4(0.702, 0, 1, 1),
                        Vec4(1, 1, 1, 1),
                        Vec4(1, 0, 0.906, 1)
                        )  # 18 white

    def __init__(self, avatar):
        AvatarPanel.AvatarPanel.__init__(self, avatar, FriendsListPanel=FriendsListPanel)
        self.avName = avatar.getName()
        self.avatr = avatar
        gui = loader.loadModel('phase_3.5/models/gui/suit_detail_panel')
        gui.find('**/shadow').setTransparency(TransparencyAttrib.MAlpha)
        gui.find('**/shadow').setColor(1, 1, 1, 0.4)
        self.frame = DirectFrame(geom=gui.find('**/avatar_panel'), geom_scale=0.21, geom_color=(0.69, 0.706, 0.718, 1), geom_pos=(0, 0, 0.02), relief=None, pos=(-0.23, 0, -0.46), parent=base.a2dTopRight)
        self.head = self.frame.attachNewNode('head')
        health = float(avatar.currHP) / float(avatar.maxHP)
        if not self.avatar.dna.name == 'hrollers' and not self.avatar.dna.name == 'bcaster' and not (self.avatar.dna.name == 'redd' and self.avatar.isVirtual) and not (self.avatar.dna.name == 'wsi' and self.avatar.isVirtual):
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
            if self.avatar.dna.name == 'cbutcher':
                self.head.setColor((0, 0, 0, 1))
            if self.avatar.dna.name == 'ls' and not avatar.isSkeleton:
                self.head.setPosHprScale(0, 0, 0.05, 270, 0, 0, s, s, s)
            elif self.avatar.dna.name == 'bfh2' and not avatar.isSkeleton:
                self.head.setPosHprScale(0, 0, 0.05, 270, 0, 0, s, s, s)
            elif self.avatar.dna.name == 'redd' and not avatar.isSkeleton:
                self.head.setPosHprScale(0, 0, 0.09, 180, 0, 0, s, s, s)
            elif self.avatar.dna.name == 'rainmake' and not avatar.isSkeleton:
                self.head.setPosHprScale(0, 0, 0.09, 180, 0, 0, s, s, s)
            elif self.avatar.dna.name == 'dking' and not avatar.isSkeleton:
                self.head.setPosHprScale(0, 0, 0.09, 180, 0, 0, s, s, s)
            elif avatar.isSkeleton and self.avatar.dna.name == 'ambass':
                self.head.setPosHprScale(0, 0, 0.08, 180, 0, 0, s, s, s)
            else:
                self.head.setPosHprScale(0, 0, 0.05, 180, 0, 0, s, s, s)
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
        elif health > 0.25:
            self.condition = 8
        elif health > 0.15:
            self.condition = 9
        elif health > 0.0:
            self.condition = 10
        else:
            self.condition = 11
        self.avatar = avatar
        if self.avatar.dna.name == 'bcaster':
        #if avatar.isVirtual:
            self.head.setColor(1, 1, 1, 1)
            self.head.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
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
            self.head.setPosHprScale(0, 0, 0.05, 180, 0, 0, s, s, s)
        if self.avatar.dna.name == 'redd' and self.avatar.isVirtual:
        #if avatar.isVirtual:
            self.head.setColor(1, 1, 1, 1)
            self.head.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
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
            self.head.setPosHprScale(0, 0, 0.09, 180, 0, 0, s, s, s)
        if self.avatar.dna.name == 'wsi' and self.avatar.isVirtual:
        #if avatar.isVirtual:
            self.head.setColor(1, 1, 1, 1)
            self.head.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
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
            self.head.setPosHprScale(0, 0, 0.05, 180, 0, 0, s, s, s)
        if self.avatar.dna.name == 'hrollers':
        #if avatar.isVirtual:
            self.head.setColor(1, 1, 1, 1)
            self.head.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
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
            self.head.setPosHprScale(0, 0, 0.05, 180, 0, 0, s, s, s)
        self.nameLabel = DirectLabel(parent=self.frame, pos=(0, 0, 0.36), relief=None,
                                     text=SuitBattleGlobals.SuitAttributes[avatar.dna.name]['name'],
                                     text_font=avatar.getFont(), text_pos=(0, 0),
                                     text_scale=0.0475, text_wordwrap=8, text_shadow=(1, 1, 1, 1))
        healthGui = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        glow = healthGui.find('**/glow')
        glow.setScale(0)
        glow.setPos(0, 0, 0)
        glow.hide()
        button = healthGui.find('**/emblem_hp')
        button.setScale(0.2)
        button.setH(0)
        button.setPos(0, 0, -0.18)
        base2 = healthGui.find('**/emblem_base')
        base2.setScale(0.2)
        base2.setH(0)
        base2.setPos(0, 0, -0.18)
        glow.reparentTo(button)
        self.button = button
        self.glow = glow
        self.base2 = base2
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
        corpIcon = avatar.corpMedallion.copyTo(hidden)
        corpIcon.setPosHprScale(0, 0, 0, 0, 0, 0, 0, 0, 0)
        #self.corpIcon = DirectLabel(parent=self.frame, geom=corpIcon, geom_scale=0.13, pos=(0, 0, -0.20), relief=None)
        self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.035), relief=None,
                                       text='',
                                       text_font=avatar.getFont(), text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
        dept = SuitDNA.getSuitDeptFullname(avatar.dna.name)
        self.healthNode = self.frame.attachNewNode('health')
        self.healthNode.setPos(0, 0, -0.24)
        #self.healthBar2 = healthBar2
        #self.healthBar2.setProp('barColor', self.healthColors[self.condition])
        #self.healthBar2.setProp('value', self.avatar.currHP)
        #self.healthBar2.setProp('range', self.avatar.getMaxHP())
        button.reparentTo(self.hpLabel)
        base2.reparentTo(self.hpLabel)
        corpIcon = avatar.corpMedallion.copyTo(hidden)
        corpIcon.setPosHprScale(0, 0, 0, 0, 0, 0, 0, 0, 0)
        if avatar.dna.dept == 't':
            corpScale = 1.275
        else:
            corpScale = 1.175
        self.corpIcon = DirectLabel(parent=self.hpLabel, geom=corpIcon, geom_scale=0.2, pos=(0, 0, -0.18), relief=None)
        #self.healthNode.hide()
        self.healthNode.setY(2)
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

        self.headTask = None
       # hasAnimatedHead = False
        #for part in avatar.animatedHeadParts:
        #    hasAnimatedHead = True
       # if self.avatar.isSkeleton:
         #   hasAnimatedHead = True
       # headTask = Task.loop(Task(self.__headAnim))
       # if hasAnimatedHead:
        #    taskMgr.add(headTask, self.frame.uniqueName('head-task'))
       # elif not hasAnimatedHead and not self.avatar.isSkeleton and not self.avatar.dna.name == 'blr' and not self.avatar.dna.name == 'dsk' and not self.avatar.dna.name == 'bdb' and not self.avatar.dna.name == 'bs':
           # for part in avatar.headParts:
             #   hasAnimatedHead = False
             #   if not hasAnimatedHead and not self.avatar.isSkeleton:
             #       copyPart = part.copyTo(self.head)
               #     copyPart.setDepthTest(1)
                   # copyPart.setDepthWrite(1)

          #  p1 = Point3()
          #  p2 = Point3()
          #  self.head.calcTightBounds(p1, p2)
          #  d = p2 - p1
          #  biggest = max(d[0], d[1], d[2])
           # s = 0.3 / biggest
          #  if self.avatar.dna.name == 'ptr' and not avatar.isSkeleton and not hasAnimatedHead:
            #  #  self.head.setPosHprScale(0, 0, 0.05, 270, 0, 0, s, s, s)
           # elif self.avatar.dna.name == 'dfh' and not avatar.isSkeleton and not hasAnimatedHead:
             #   self.head.setPosHprScale(0, 0, 0.05, 270, 0, 0, s, s, s)
           # elif not hasAnimatedHead and not self.avatar.isSkeleton:
               # self.head.setPosHprScale(0, 0, 0.05, 180, 0, 0, s, s, s)

        self.labelInterval = None

        self.healthBarInterval = None

        self.buttonInterval = None

        self.changeInterval = None

        self.blinkTask = None

        self.frame.setBin("gui-popup", 0)
        self.frame.show()
        messenger.send('avPanelDone')

        self.accept(avatar.uniqueName('suitHpUpdate'), self.__updateHp)
        return

    def __updateLabel(self, tempHp, level, maxHp):
        revives = self.avatar.getSkeleRevives() + 1
        if self.avatar.isFired:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            0, maxHp)
            self.corpIcon.hide()
            self.deptLabel['text'] = ''
        elif self.avatar.isImmortal and not self.avatar.dna.name == 'hroller' and not self.avatar.isPhase3:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogImmune % (
            'Immune')
        elif self.avatar.dna.name == 'hrollers' and self.maxHp > 9999 and tempHp <= 0:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % '25.mgr' + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            0, maxHp)
        elif self.avatar.isShadow and self.maxHp > 9999 and tempHp <= 0:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % '30.mgr' + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            0, maxHp)
        elif self.avatar.isShadow and self.maxHp > 9999:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % '30.mgr' + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            int(tempHp), maxHp)
        elif self.avatar.isShadow and tempHp <= 0:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % '30.mgr' + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            0, maxHp)
        elif self.avatar.isShadow:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % '30.mgr' + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            int(tempHp), maxHp)
        elif self.avatar.dna.name == 'hrollers' and self.maxHp > 9999:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % '25.mgr' + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            int(tempHp), maxHp)
        elif self.avatar.dna.name == 'hrollers' and tempHp <= 0:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % '25.mgr' + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            0, maxHp)
        elif self.avatar.dna.name == 'hrollers':
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % '25.mgr' + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            int(tempHp), maxHp)
        elif revives > 2 and self.avatar.isVirtual and maxHp > 9999 and tempHp <= 0:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            0, maxHp)
        elif revives > 2 and self.avatar.isVirtual and maxHp > 9999:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            int(tempHp), maxHp)
        elif revives > 2 and self.avatar.isVirtual and tempHp <= 0:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            0, maxHp)
        elif revives > 2 and self.avatar.isVirtual:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            int(tempHp), maxHp)
        elif revives > 2 and self.avatar.isSkeleton and maxHp > 9999 and tempHp <= 0:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\nVersion %s.0' % (
                        revives - 1) + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (0, maxHp)
        elif revives > 2 and self.avatar.isSkeleton and maxHp > 9999:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\nVersion %s.0' % (
                        revives - 1) + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (int(tempHp), maxHp)
        elif revives > 2 and self.avatar.isSkeleton and tempHp <= 0:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\nVersion %s.0' % (
                        revives - 1) + '\n' + TTLocalizer.AvatarPanelCogHealth % (0, maxHp)
        elif revives > 2 and self.avatar.isSkeleton:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\nVersion %s.0' % (
                        revives - 1) + '\n' + TTLocalizer.AvatarPanelCogHealth % (int(tempHp), maxHp)
        elif revives > 1 and self.avatar.isVirtual and maxHp > 9999 and tempHp <= 0:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            0, maxHp)
        elif revives > 1 and self.avatar.isVirtual and maxHp > 9999:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            int(tempHp), maxHp)
        elif revives > 1 and self.avatar.isVirtual and tempHp <= 0:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            0, maxHp)
        elif revives > 1 and self.avatar.isVirtual:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            int(tempHp), maxHp)
        elif revives > 1 and self.avatar.isSkeleton and self.avatar.isRevived and maxHp > 9999 and tempHp <= 0:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            0, maxHp)
        elif revives > 1 and self.avatar.isSkeleton and self.avatar.isRevived and maxHp > 9999:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            int(tempHp), maxHp)
        elif revives > 1 and self.avatar.isSkeleton and self.avatar.isRevived and tempHp <= 0:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            0, maxHp)
        elif revives > 1 and self.avatar.isSkeleton and self.avatar.isRevived:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            int(tempHp), self.maxHp)
        elif revives > 1 and self.maxHp > 9999 and tempHp <= 0:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\nVersion %s.0' % revives + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            0, maxHp)
        elif revives > 1 and self.maxHp > 9999:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\nVersion %s.0' % revives + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            int(tempHp), maxHp)
        elif revives > 1 and tempHp <= 0:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\nVersion %s.0' % revives + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            0, maxHp)
        elif revives > 1:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\nVersion %s.0' % revives + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            int(tempHp), maxHp)
        elif self.avatar.dna.name == 'hroller' and tempHp <= 0:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            0, maxHp)
        elif self.avatar.dna.name == 'hroller':
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            int(tempHp), maxHp)
        elif self.avatar.dna.name == 'chairman' and tempHp <= 0:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            0, maxHp)
        elif self.avatar.dna.name == 'chairman':
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            int(tempHp), maxHp)
        elif self.avatar.dna.name == 'hroller2' and tempHp <= 0:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            0, maxHp)
        elif self.avatar.dna.name == 'hroller2':
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            int(tempHp), maxHp)
        elif tempHp > 9999:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            int(tempHp), maxHp)
        elif self.maxHp > 9999 and tempHp <= 0:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            0, maxHp)
        elif self.maxHp > 9999:
            self.hpLabel[
                'text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth2 % (
            int(tempHp), maxHp)
        elif tempHp <= 0:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            0, maxHp)
        else:
            self.hpLabel['text'] = TTLocalizer.AvatarPanelCogLevel % level + '\n' + TTLocalizer.AvatarPanelCogHealth % (
            int(tempHp), maxHp)


    def __updateHp(self, currHp, maxHp, delta):
        taskMgr.remove(self.frame.uniqueName('pulse-task'))
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
        elif health > 0.25:
            condition = 7
        elif health > 0.2:
            condition = 8
        elif health > 0.1:
            condition = 9
        elif health > 0.0:
            condition = 10
        else:
            condition = 11
        avatar = self.avatar
        if self.avatar.isFired:
            level = str(self.avatar.getActualLevel())
        elif self.avatar.getExecutive() and not self.avatar.getManager():
            level = str(self.avatar.getActualLevel()) + TTLocalizer.ExecutivePostFix
        elif self.avatar.getGovernaught() and not self.avatar.getExecutive() and not self.avatar.getManager():
            level = str(self.avatar.getActualLevel()) + TTLocalizer.GovernaughtPostFix
        elif self.avatar.getManager():
            level = str(self.avatar.getActualLevel()) + TTLocalizer.ManagerPostFix
        else:
            level = str(self.avatar.getActualLevel())
        self.__updateLabel(currHp, level, maxHp)

        #self.labelInterval = Parallel(Func(__updateLabel, currHp))
        #self.labelInterval.start()

        if condition == 10:
            taskMgr.remove(self.frame.uniqueName('blink-task'))
            self.button.setColor(1, 1, 1, 1)
            blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray), Task.pause(0.1))
            taskMgr.add(blinkTask, self.frame.uniqueName('blink-task'))
        elif condition == 11:
            taskMgr.remove(self.frame.uniqueName('blink-task'))
            self.button.setColor(1, 1, 1, 1)
            self.buttonInterval = Parallel(
                LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 1, 1, 1),
                                       blendType='easeInOut'))
            blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray), Task.pause(0.1))
            taskMgr.add(blinkTask, self.frame.uniqueName('blink-task'))
        elif condition == 13:
            taskMgr.remove(self.frame.uniqueName('pulse-task'))
            self.button.setColor(1, 1, 1, 1)
            blinkTask = Task.loop(Task(self.__pulsePurple), Task.pause(1), Task(self.__pulsePurpleColor),
                                  Task.pause(3))
            taskMgr.add(blinkTask, self.frame.uniqueName('pulse-task'))
        else:
            self.button.setColor(1, 1, 1, 1)
            if self.avatar.isImmortal and not self.avatar.isPhase3 and not self.avatar.dna.name == 'hroller':
                self.changeInterval = Parallel(LerpColorScaleInterval(self.button, duration=1, colorScale=(1, 1, 1, 1),
                                       blendType='easeInOut'))
                self.changeInterval.start()
            else:
                if self.avatar.dna.name == 'bcaster':
                    self.changeInterval = Parallel(
                        LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                               blendType='easeInOut'), LerpColorScaleInterval(self.head, duration=1, colorScale=(self.healthColors[condition]),
                                               blendType='easeInOut'))
                    self.changeInterval.start()
                if self.avatar.dna.name == 'wsi' and self.avatar.isVirtual:
                    self.changeInterval = Parallel(
                        LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                               blendType='easeInOut'), LerpColorScaleInterval(self.head, duration=1, colorScale=(self.healthColors[condition]),
                                               blendType='easeInOut'))
                    self.changeInterval.start()
                if self.avatar.dna.name == 'redd' and self.avatar.isVirtual:
                    self.changeInterval = Parallel(
                        LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                               blendType='easeInOut'), LerpColorScaleInterval(self.head, duration=1, colorScale=(self.healthColors[condition]),
                                               blendType='easeInOut'))
                    self.changeInterval.start()
                if self.avatar.dna.name == 'hrollers':
                    if self.avatar.getActualLevel() == 34:
                        self.changeInterval = Parallel(
                            LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                                   blendType='easeInOut'),
                            LerpColorScaleInterval(self.head, duration=1, colorScale=(self.healthColors[20]),
                                                   blendType='easeInOut'))
                        self.changeInterval.start()
                    if self.avatar.getActualLevel() == 33:
                        self.changeInterval = Parallel(
                            LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                                   blendType='easeInOut'),
                            LerpColorScaleInterval(self.head, duration=1, colorScale=(self.healthColors[19]),
                                                   blendType='easeInOut'))
                        self.changeInterval.start()
                    if self.avatar.getActualLevel() == 32:
                        self.changeInterval = Parallel(
                            LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                                   blendType='easeInOut'),
                            LerpColorScaleInterval(self.head, duration=1, colorScale=(self.healthColors[13]),
                                                   blendType='easeInOut'))
                        self.changeInterval.start()
                    if self.avatar.getActualLevel() == 31:
                        self.changeInterval = Parallel(
                            LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                                   blendType='easeInOut'),
                            LerpColorScaleInterval(self.head, duration=1, colorScale=(self.healthColors[12]),
                                                   blendType='easeInOut'))
                        self.changeInterval.start()
                    if self.avatar.getActualLevel() == 30:
                        self.changeInterval = Parallel(
                            LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                                   blendType='easeInOut'),
                            LerpColorScaleInterval(self.head, duration=1, colorScale=(self.healthColors[14]),
                                                   blendType='easeInOut'))
                        self.changeInterval.start()
                    if self.avatar.getActualLevel() == 29:
                        self.changeInterval = Parallel(
                            LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                                   blendType='easeInOut'),
                            LerpColorScaleInterval(self.head, duration=1, colorScale=(self.healthColors[8]),
                                                   blendType='easeInOut'))
                        self.changeInterval.start()
                    if self.avatar.getActualLevel() == 28:
                        self.changeInterval = Parallel(
                            LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                                   blendType='easeInOut'),
                            LerpColorScaleInterval(self.head, duration=1, colorScale=(self.healthColors[15]),
                                                   blendType='easeInOut'))
                        self.changeInterval.start()
                    if self.avatar.getActualLevel() == 27:
                        self.changeInterval = Parallel(
                            LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                                   blendType='easeInOut'),
                            LerpColorScaleInterval(self.head, duration=1, colorScale=(self.healthColors[3]),
                                                   blendType='easeInOut'))
                        self.changeInterval.start()
                    if self.avatar.getActualLevel() == 26:
                        self.changeInterval = Parallel(
                            LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                                   blendType='easeInOut'),
                            LerpColorScaleInterval(self.head, duration=1, colorScale=(self.healthColors[7]),
                                                   blendType='easeInOut'))
                        self.changeInterval.start()
                    if self.avatar.getActualLevel() == 25:
                        self.changeInterval = Parallel(
                            LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                                   blendType='easeInOut'),
                            LerpColorScaleInterval(self.head, duration=1, colorScale=(self.healthColors[0]),
                                                   blendType='easeInOut'))
                        self.changeInterval.start()
                else:
                    self.changeInterval = Parallel(
                        LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[condition]),
                                               blendType='easeInOut'))
                    self.changeInterval.start()
            taskMgr.remove(self.frame.uniqueName('blink-task'))
            taskMgr.remove(self.frame.uniqueName('pulse-task'))
            self.blinkTask = None
        #self.buttonInterval.start()
        #self.hideCorpIcon.start()

    def __blinkRed(self, task):
        self.healthBar2.setProp('barColor', self.healthColors[9])
        self.button.setColor(self.healthColors[9], 1)

    def __blinkGray(self, task):
        self.healthBar2.setProp('barColor', self.healthColors[10])
        self.button.setColor(0.431, 0.431, 0.431, 1)

    def __blinkRedVirtual(self, task):
        self.head.setColor(self.healthColors[9], 1)

    def __blinkGrayVirtual(self, task):
        self.head.setColor(self.healthColors[10], 1)

    def __changeColor(self):
        if self.avatar.isImmortal and not self.avatar.isPhase3 and not self.avatar.dna.name == 'hroller':
            self.interval = Parallel(LerpColorScaleInterval(self.button, duration=1, colorScale=(1, 1, 1, 1),
                                   blendType='easeInOut'))
            self.interval.start()
        elif self.avatar.isImmortal and not self.avatar.isPhase3 and self.avatar.dna.name == 'hroller':
            self.interval = Sequence(
                LerpColorScaleInterval(self.button, duration=1, colorScale=(1, 0, 0, 1),
                                       blendType='easeInOut'),
                LerpColorScaleInterval(self.button, duration=1, colorScale=(1, 0.5, 0, 1),
                                       blendType='easeInOut'),
                LerpColorScaleInterval(self.button, duration=1, colorScale=(1, 1, 0, 1),
                                       blendType='easeInOut'),
                LerpColorScaleInterval(self.button, duration=1, colorScale=(0, 1, 0, 1),
                                       blendType='easeInOut'),
                LerpColorScaleInterval(self.button, duration=1, colorScale=(0, 0, 1, 1),
                                       blendType='easeInOut'),
                LerpColorScaleInterval(self.button, duration=1, colorScale=(0.29, 0, 0.51, 1),
                                       blendType='easeInOut'),
                LerpColorScaleInterval(self.button, duration=1, colorScale=(0.56, 0, 1, 1),
                                       blendType='easeInOut')).loop()
            self.interval.start()
        else:
            self.interval = Parallel(
                    LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[self.condition]),
                                           blendType='easeInOut'))
            self.interval.start()

    def __changeColorHead(self):
        self.interval = Parallel(LerpColorScaleInterval(self.button, duration=0, colorScale=(self.healthColors[self.condition]),
                                   blendType='easeInOut'))
        self.interval.start()

    def __pulseRed(self, task):
        if self.avatar.dna.name == 'bcaster':
            self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(1, 0, 0, 1),
                                                            blendType='easeInOut'), LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
            self.interval.start()
        if self.avatar.dna.name == 'redd' and self.avatar.isVirtual:
            self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(1, 0, 0, 1),
                                                            blendType='easeInOut'), LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
            self.interval.start()
        if self.avatar.dna.name == 'wsi' and self.avatar.isVirtual:
            self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(1, 0, 0, 1),
                                                            blendType='easeInOut'), LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
            self.interval.start()
        if self.avatar.dna.name == 'hrollers':
            if self.avatar.getActualLevel() == 34:
                self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(self.healthColors[20]),
                                                                blendType='easeInOut'),
                                         LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                                                blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 33:
                self.interval = Parallel(
                    LerpColorScaleInterval(self.head, duration=0, colorScale=(self.healthColors[19]),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 32:
                self.interval = Parallel(
                    LerpColorScaleInterval(self.head, duration=0, colorScale=(self.healthColors[13]),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 31:
                self.interval = Parallel(
                    LerpColorScaleInterval(self.head, duration=0, colorScale=(self.healthColors[12]),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 30:
                self.interval = Parallel(
                    LerpColorScaleInterval(self.head, duration=0, colorScale=(self.healthColors[14]),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 29:
                self.interval = Parallel(
                    LerpColorScaleInterval(self.head, duration=0, colorScale=(self.healthColors[8]),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 28:
                self.interval = Parallel(
                    LerpColorScaleInterval(self.head, duration=0, colorScale=(self.healthColors[15]),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 27:
                self.interval = Parallel(
                    LerpColorScaleInterval(self.head, duration=0, colorScale=(self.healthColors[3]),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 26:
                self.interval = Parallel(
                    LerpColorScaleInterval(self.head, duration=0, colorScale=(self.healthColors[7]),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 25:
                self.interval = Parallel(
                    LerpColorScaleInterval(self.head, duration=0, colorScale=(self.healthColors[0]),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'))
                self.interval.start()
        else:
            self.interval = Parallel(LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 0, 0, 1),
                                       blendType='easeInOut'))
            self.interval.start()

    def __pulseWhite(self):
        self.interval = Parallel(LerpColorScaleInterval(self.button, duration=0, colorScale=(1, 1, 1, 1),
                                   blendType='easeInOut'))
        self.interval.start()

    def __pulseGray(self, task):
        if self.avatar.dna.name == 'bcaster':
            self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                            blendType='easeInOut'), LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                   blendType='easeInOut'))
            self.interval.start()
        if self.avatar.dna.name == 'wsi' and self.avatar.isVirtual:
            self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                            blendType='easeInOut'), LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                   blendType='easeInOut'))
            self.interval.start()
        if self.avatar.dna.name == 'redd' and self.avatar.isVirtual:
            self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                            blendType='easeInOut'), LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                   blendType='easeInOut'))
            self.interval.start()
        if self.avatar.dna.name == 'hrollers':
            if self.avatar.getActualLevel() == 34:
                self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'),
                                         LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 33:
                self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'),
                                         LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 32:
                self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'),
                                         LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 31:
                self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'),
                                         LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 30:
                self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'),
                                         LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 29:
                self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'),
                                         LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 28:
                self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'),
                                         LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 27:
                self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'),
                                         LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 26:
                self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'),
                                         LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'))
                self.interval.start()
            if self.avatar.getActualLevel() == 25:
                self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'),
                                         LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                                                blendType='easeInOut'))
                self.interval.start()
        else:
            self.interval = Parallel(LerpColorScaleInterval(self.button, duration=0, colorScale=(0.3, 0.3, 0.3, 1),
                                       blendType='easeInOut'))
            self.interval.start()

    def __pulseRedHead(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
        self.interval.start()

    def __pulseGrayHead(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.head, duration=0, colorScale=(0.431, 0.431, 0.431, 1),
                                   blendType='easeInOut'))
        self.interval.start()

    def __pulsePurple(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.button, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                   blendType='easeInOut'))
        self.interval.start()

    def __pulsePurpleColor(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.button, duration=1, colorScale=(self.healthColors[13]),
                                   blendType='easeInOut'))
        self.interval.start()

    def __pulsePurpleHead(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.head, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                   blendType='easeInOut'))
        self.interval.start()

    def __headAnim(self, task):
        hasAnimatedHead = False
        for part in self.avatar.animatedHeadParts:
            if not self.avatar.isSkeleton and self.avatar.dna.name == 'radiog' or not self.avatar.isSkeleton and self.avatar.dna.name == 'ubuster' or not self.avatar.isSkeleton and self.avatar.dna.name == 'ang' or not self.avatar.isSkeleton and self.avatar.dna.name == 'cv':
                hasAnimatedHead = True
                copyPart = part.copyTo(self.head)
                p1 = Point3()
                p2 = Point3()
                copyPart.calcTightBounds(p1, p2)
                d = p2 - p1
                biggest = max(d[0], d[1], d[2])
                if self.avatar.dna.name == 'radiog' and not self.avatar.isSkeleton:
                    s = 0.4 / biggest
                    headInterval = Sequence(Parallel(Func(copyPart.setDepthTest, 1), Func(copyPart.setDepthWrite, 1),
                                                     Func(copyPart.setPosHprScale, 0, 0, 0.04, 180, 0, 0, s, s, s)),
                                            Wait(0.05), Func(copyPart.removeNode))
                    headInterval.start()
                elif self.avatar.dna.name == 'radiog' and not self.avatar.isSkeleton:
                    s = 0.4 / biggest
                    headInterval = Sequence(Parallel(Func(copyPart.setDepthTest, 1), Func(copyPart.setDepthWrite, 1),
                                                     Func(copyPart.setPosHprScale, 0, 0, 0.04, 180, 0, 0, s, s, s)),
                                            Wait(0.05), Func(copyPart.removeNode))
                    headInterval.start()
                else:
                    s = 0.3 / biggest
                    headInterval = Sequence(Parallel(Func(copyPart.setDepthTest, 1), Func(copyPart.setDepthWrite, 1),
                                                     Func(self.head.setPosHprScale, 0, 0, 0.05, 180, 0, 0, s, s, s)),
                                            Wait(0.05), Func(copyPart.removeNode))
                    headInterval.start()
        for part in self.avatar.headParts:
            if self.avatar.isSkeleton and self.avatar.dna.name == 'radiog' or self.avatar.isSkeleton and self.avatar.dna.name == 'ubuster' or self.avatar.isSkeleton and self.avatar.dna.name == 'ang' or self.avatar.isSkeleton and self.avatar.dna.name == 'cv':
                hasAnimatedHead = True
                copyPart = part.copyTo(self.head)
                p1 = Point3()
                p2 = Point3()
                copyPart.calcTightBounds(p1, p2)
                d = p2 - p1
                biggest = max(d[0], d[1], d[2])
                s = 0.3 / biggest
                headInterval = Sequence(Parallel(Func(copyPart.setDepthTest, 1), Func(copyPart.setDepthWrite, 1),
                                                     Func(self.head.setPosHprScale, 0, 0, 0.03, 180, 0, 0, s, s, s)),
                                            Wait(0.05), Func(copyPart.removeNode))
                headInterval.start()
        for part in self.avatar.headParts:
            if not self.avatar.dna.name == 'radiog' and not self.avatar.dna.name == 'ubuster' and not self.avatar.dna.name == 'ang' and not self.avatar.dna.name == 'cv':
                hasAnimatedHead = True
                copyPart = part.copyTo(self.head)
                p1 = Point3()
                p2 = Point3()
                copyPart.calcTightBounds(p1, p2)
                d = p2 - p1
                biggest = max(d[0], d[1], d[2])
                s = 0.3 / biggest
                if self.avatar.dna.name == 'rainmake' and not self.avatar.isSkeleton:
                    headInterval = Sequence(Parallel(Func(copyPart.setDepthTest, 1), Func(copyPart.setDepthWrite, 1),
                                                     Func(copyPart.setPosHprScale, 0, 0, 0.09, 180, 0, 0, s, s, s)),
                                            Wait(0.05), Func(copyPart.removeNode))
                    headInterval.start()
                elif self.avatar.dna.name == 'redd' and not self.avatar.isSkeleton:
                    headInterval = Sequence(Parallel(Func(copyPart.setDepthTest, 1), Func(copyPart.setDepthWrite, 1),
                                                     Func(copyPart.setPosHprScale, 0, 0, 0.09, 180, 0, 0, s, s, s)),
                                            Wait(0.05), Func(copyPart.removeNode))
                    headInterval.start()
                elif self.avatar.dna.name == 'radiog' and not self.avatar.isSkeleton:
                    headInterval = Sequence(Parallel(Func(copyPart.setDepthTest, 1), Func(copyPart.setDepthWrite, 1),
                                                     Func(copyPart.setPosHprScale, 0, 0, 0.04, 180, 0, 0, s, s, s)),
                                            Wait(0.05), Func(copyPart.removeNode))
                    headInterval.start()
                elif self.avatar.dna.name == 'ubuster' and not self.avatar.isSkeleton:
                    headInterval = Sequence(Parallel(Func(copyPart.setDepthTest, 1), Func(copyPart.setDepthWrite, 1),
                                                     Func(copyPart.setPosHprScale, 0, 0, 0.04, 180, 0, 0, s, s, s)),
                                            Wait(0.05), Func(copyPart.removeNode))
                    headInterval.start()
                elif self.avatar.isSkeleton and self.avatar.dna.name == 'ambass':
                    headInterval = Sequence(Parallel(Func(copyPart.setDepthTest, 1), Func(copyPart.setDepthWrite, 1),
                                                     Func(copyPart.setPosHprScale, 0, 0, 0.08, 180, 0, 0, s, s, s)),
                                            Wait(0.05), Func(copyPart.removeNode))
                    headInterval.start()
                elif self.avatar.isSkeleton and not self.avatar.dna.name == 'ambass':
                    headInterval = Sequence(Parallel(Func(copyPart.setDepthTest, 1), Func(copyPart.setDepthWrite, 1),
                                                     Func(copyPart.setPosHprScale, 0, 0, 0.03, 180, 0, 0, s, s, s)),
                                            Wait(0.05), Func(copyPart.removeNode))
                    headInterval.start()
                else:
                    headInterval = Sequence(Parallel(Func(copyPart.setDepthTest, 1), Func(copyPart.setDepthWrite, 1),
                                                     Func(self.head.setPosHprScale, 0, 0, 0.05, 180, 0, 0, s, s, s)),
                                            Wait(0.05), Func(copyPart.removeNode))
                    headInterval.start()


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

    def startHeadTask(self):
        self.headTask = Task.loop(Task(self.__headAnim))
        taskMgr.add(self.blinkTask, 'head-task')

    def stopHeadTask(self):
        taskMgr.remove('head-task')
        self.headTask = None

    def __cleanupSequence(self):
        self.blinkTask = None
        taskMgr.remove(self.frame.uniqueName('blink-task'))
        taskMgr.remove(self.frame.uniqueName('pulse-task'))
        self.headTask = None
        taskMgr.remove(self.frame.uniqueName('head-task'))
        if self.labelInterval:
            self.labelInterval.finish()
            self.labelInterval = None

        if self.healthBarInterval:
            self.healthBarInterval.finish()
            self.healthBarInterval = None

        if self.changeInterval:
            self.changeInterval.finish()
            self.changeInterval = None

        if self.buttonInterval:
            self.buttonInterval.finish()
            self.buttonInterval = None

        if self.blinkTask:
            self.blinkTask.finish()
            self.blinkTask = None

        if self.headTask:
            self.headTask.finish()
            self.headTask = None

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

        taskMgr.remove(self.frame.uniqueName('blink-task'))
        self.blinkTask = None
        self.currentInterval = self.__getCloseSequence()
        self.currentInterval.start()
        return

        return

    @classmethod
    def getRevives(cls, cog):
        return cog.getSkeleRevives()
