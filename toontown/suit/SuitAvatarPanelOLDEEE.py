from panda3d.core import *
from direct.gui.DirectGui import *
from direct.showbase import DirectObject
from otp.avatar import Avatar
from direct.distributed import DistributedObject
from direct.task.Task import Task
from direct.task.TaskManagerGlobal import taskMgr
from . import SuitDNA
from toontown.battle import SuitBattleGlobals
from toontown.toonbase import TTLocalizer
from toontown.battle import BattleProps
from otp.avatar import AvatarPanel
from toontown.friends import FriendsListPanel
from toontown.suit import Suit
from direct.interval.IntervalGlobal import *
from direct.showbase import DirectObject
from panda3d.core import *


class SuitAvatarPanel(AvatarPanel.AvatarPanel, DirectObject.DirectObject):
    currentAvatarPanel = None

    healthColors = (Vec4(0.169, 1, 0, 1),
                    Vec4(0.5, 1, 0, 1),
                    Vec4(0.75, 1, 0, 1),
                    Vec4(1, 1, 0, 1),
                    Vec4(1, 0.866, 0, 1),
                    Vec4(1, 0.6, 0, 1),
                    Vec4(1, 0.5, 0, 1),
                    Vec4(1, 0.25, 0, 1.0),
                    Vec4(1, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0.0, 1.0, 1.0, 1),  # overheal
                    Vec4(0.741, 0, 1, 1),  # overcharge
                    Vec4(186 / 255, 82 / 255, 1, 1))
    healthGlowColors = (Vec4(0.25, 1, 0.25, 0.5),
                        Vec4(0.5, 1, 0.25, .5),
                        Vec4(0.75, 1, 0.25, .5),
                        Vec4(1, 1, 0.25, 0.5),
                        Vec4(1, 0.866, 0.25, .5),
                        Vec4(1, 0.6, 0.25, .5),
                        Vec4(1, 0.5, 0.25, 0.5),
                        Vec4(1, 0.25, 0.25, 0.5),
                        Vec4(1, 0, 0, 0.5),
                        Vec4(1, 0, 0, 0.5),
                        Vec4(0, 0, 0, 0.5),
                        Vec4(1, 0, 0, 0),
                        Vec4(0.0, 1.0, 1.0, 0.5),  # overheal
                        Vec4(0.741, 0, 1, 1),  # overcharge
                        Vec4(186 / 255, 82 / 255, 1, 1))

    POPUP_ANIMATION_DURATION = 0
    POPOUT_ANIMATION_DURATION = 0

    def __init__(self, avatar):
        AvatarPanel.AvatarPanel.__init__(self, avatar, FriendsListPanel=FriendsListPanel)
        self.avName = avatar.getName()
        self.avatr = avatar
        gui = loader.loadModel('phase_3.5/models/gui/suit_detail_panel')
        gui.find('**/shadow').setTransparency(TransparencyAttrib.MAlpha)
        gui.find('**/shadow').setColor(1, 1, 1, 0.4)
        self.frame = DirectFrame(geom=gui.find('**/avatar_panel'), geom_scale=0.21, geom_pos=(0, 0, 0.02), relief=None, pos=(-0.2348, 0, -0.475), parent=base.a2dTopRight)
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
        if avatar.isSkeleton and avatar.dna.body == 'a' and not self.avatar.dna.dept == 'l' and not self.avatar.dna.dept == 'g' and not self.avatar.dna.name == 'cg' and not self.avatar.dna.name == 'blr' and not self.avatar.dna.name == 'dsk' and not self.avatar.dna.name == 'ts' and not self.avatar.dna.name == 'jur' \
                and not self.avatar.dna.name == 'laa' and not self.avatar.dna.name == 'csh' and not self.avatar.dna.name == 'bgr' and not self.avatar.dna.name == 'styx' \
                and not self.avatar.dna.name == 'nix' and not self.avatar.dna.name == 'hydra' and not self.avatar.dna.name == 'kerberos' and not self.avatar.dna.name == 'charon' \
                and not self.avatar.dna.name == 'fas' and not self.avatar.dna.name == 'mdr' and not self.avatar.dna.name == 'nar' and not self.avatar.dna.name == 'fd' \
                and not self.avatar.dna.name == 'gkp' and not self.avatar.dna.name == 'ddv' and not self.avatar.dna.name == 'sya' and not self.avatar.dna.name == 'ant' and not self.avatar.dna.name == 'cm':
            s = 0.4 / biggest
        elif avatar.isSkeleton and avatar.dna.body == 'a' and not self.avatar.dna.name == 'cg' and not self.avatar.dna.name == 'blr' and not self.avatar.dna.name == 'dsk' and not self.avatar.dna.name == 'ts' and not self.avatar.dna.name == 'jur' \
                and not self.avatar.dna.name == 'laa' and not self.avatar.dna.name == 'csh' and not self.avatar.dna.name == 'bgr' and not self.avatar.dna.name == 'styx' \
                and not self.avatar.dna.name == 'nix' and not self.avatar.dna.name == 'hydra' and not self.avatar.dna.name == 'kerberos' and not self.avatar.dna.name == 'charon' \
                and not self.avatar.dna.name == 'fas' and not self.avatar.dna.name == 'mdr' and not self.avatar.dna.name == 'nar' and not self.avatar.dna.name == 'fd' \
                and not self.avatar.dna.name == 'gkp' and not self.avatar.dna.name == 'ddv' and not self.avatar.dna.name == 'sya' and not self.avatar.dna.name == 'ant' and not self.avatar.dna.name == 'cm':
            s = 0.45 / biggest
        elif avatar.isSkeleton and avatar.dna.body == 'b' and not self.avatar.dna.dept == 'l' and not self.avatar.dna.dept == 'g' and not self.avatar.dna.name == 'cg' and not self.avatar.dna.name == 'blr' and not self.avatar.dna.name == 'dsk' and not self.avatar.dna.name == 'ts' and not self.avatar.dna.name == 'jur' \
                and not self.avatar.dna.name == 'laa' and not self.avatar.dna.name == 'csh' and not self.avatar.dna.name == 'bgr' and not self.avatar.dna.name == 'styx' \
                and not self.avatar.dna.name == 'nix' and not self.avatar.dna.name == 'hydra' and not self.avatar.dna.name == 'kerberos' and not self.avatar.dna.name == 'charon' \
                and not self.avatar.dna.name == 'fas' and not self.avatar.dna.name == 'mdr' and not self.avatar.dna.name == 'nar' and not self.avatar.dna.name == 'fd' \
                and not self.avatar.dna.name == 'gkp' and not self.avatar.dna.name == 'ddv' and not self.avatar.dna.name == 'sya' and not self.avatar.dna.name == 'ant' and not self.avatar.dna.name == 'cm':
            s = 0.6 / biggest
        elif avatar.isSkeleton and avatar.dna.body == 'c' and not self.avatar.dna.dept == 'l' and not self.avatar.dna.dept == 'g' and not self.avatar.dna.name == 'cg' and not self.avatar.dna.name == 'blr' and not self.avatar.dna.name == 'dsk' and not self.avatar.dna.name == 'ts' and not self.avatar.dna.name == 'jur' \
                and not self.avatar.dna.name == 'laa' and not self.avatar.dna.name == 'csh' and not self.avatar.dna.name == 'bgr' and not self.avatar.dna.name == 'styx' \
                and not self.avatar.dna.name == 'nix' and not self.avatar.dna.name == 'hydra' and not self.avatar.dna.name == 'kerberos' and not self.avatar.dna.name == 'charon' \
                and not self.avatar.dna.name == 'fas' and not self.avatar.dna.name == 'mdr' and not self.avatar.dna.name == 'nar' and not self.avatar.dna.name == 'fd' \
                and not self.avatar.dna.name == 'gkp' and not self.avatar.dna.name == 'ddv' and not self.avatar.dna.name == 'sya' and not self.avatar.dna.name == 'ant' and not self.avatar.dna.name == 'cm':
            s = 0.6 / biggest
        elif avatar.isSkeleton and avatar.dna.body == 'b' and not self.avatar.dna.name == 'cg' and not self.avatar.dna.name == 'blr' and not self.avatar.dna.name == 'dsk' and not self.avatar.dna.name == 'ts' and not self.avatar.dna.name == 'jur' \
                and not self.avatar.dna.name == 'laa' and not self.avatar.dna.name == 'csh' and not self.avatar.dna.name == 'bgr' and not self.avatar.dna.name == 'styx' \
                and not self.avatar.dna.name == 'nix' and not self.avatar.dna.name == 'hydra' and not self.avatar.dna.name == 'kerberos' and not self.avatar.dna.name == 'charon' \
                and not self.avatar.dna.name == 'fas' and not self.avatar.dna.name == 'mdr' and not self.avatar.dna.name == 'nar' and not self.avatar.dna.name == 'fd' \
                and not self.avatar.dna.name == 'gkp' and not self.avatar.dna.name == 'ddv' and not self.avatar.dna.name == 'sya' and not self.avatar.dna.name == 'ant' and not self.avatar.dna.name == 'cm':
            s = 0.5 / biggest
        elif avatar.isSkeleton and avatar.dna.body == 'c' and not self.avatar.dna.name == 'cg' and not self.avatar.dna.name == 'blr' and not self.avatar.dna.name == 'dsk' and not self.avatar.dna.name == 'ts' and not self.avatar.dna.name == 'jur' \
                and not self.avatar.dna.name == 'laa' and not self.avatar.dna.name == 'csh' and not self.avatar.dna.name == 'bgr' and not self.avatar.dna.name == 'styx' \
                and not self.avatar.dna.name == 'nix' and not self.avatar.dna.name == 'hydra' and not self.avatar.dna.name == 'kerberos' and not self.avatar.dna.name == 'charon' \
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
        self.nameLabel = DirectLabel(parent=self.frame, pos=(0, 0, 0.36), relief=None, text=SuitBattleGlobals.SuitAttributes[avatar.dna.name]['name'],
                                     text_font=avatar.getFont(), text_pos=(0, 0),
                                     text_scale=0.0475, text_wordwrap=8.0, text_shadow=(1, 1, 1, 1))
        if avatar.getExecutive() and not avatar.getManager():
            level = str(avatar.getActualLevel()) + TTLocalizer.ExecutivePostFix
        elif avatar.getGovernaught() and not avatar.getExecutive() and not avatar.getManager():
            level = str(avatar.getActualLevel()) + TTLocalizer.GovernaughtPostFix
        elif avatar.getManager():
            level = str(avatar.getActualLevel()) + TTLocalizer.ManagerPostFix
        else:
            level = str(avatar.getActualLevel())
        healthGui = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
        button = healthGui.find('**/minnieCircle')
        button.setScale(1.5)
        button.setH(180)
        button.setColor(Vec4(0, 1, 0, 1))
        self.healthNode = self.frame.attachNewNode('health')
        self.healthNode.setPos(0, 0, -0.21)
        button.reparentTo(self.healthNode)
        glow = BattleProps.globalPropPool.getProp('glow')
        glow.reparentTo(button)
        glow.setScale(0.3)
        glow.setPos(-0.005, 0.01, 0.015)
        glow.setColor(Vec4(0.25, 1, 0.25, 0.5))
        self.button = button
        self.glow = glow

        condition = avatar.healthCondition
        if condition == 10:
            self.blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task.pause(0.1))
            taskMgr.add(self.blinkTask, self.frame.uniqueName('blink-task'))
        elif condition == 11:
            taskMgr.remove(self.frame.uniqueName('blink-task'))
            blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(blinkTask, self.frame.uniqueName('blink-task'))
        else:
            taskMgr.remove(self.frame.uniqueName('blink-task'))
            if not self.button.isEmpty():
                self.button.setColor(self.healthColors[condition], 1)

            if not self.glow.isEmpty():
                self.glow.setColor(self.healthGlowColors[condition], 1)

        revives = avatar.getMaxSkeleRevives() + 1
        maxHP = avatar.maxHP
        if avatar.currHP > 0:
            HP = avatar.currHP
        else:
            HP = 0
        if avatar.currHP >= 9999 and revives > 1:
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.115), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
        elif avatar.maxHP >= 9999:
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.09), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
        elif avatar.currHP >= 9999:
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.09), relief=None,
                                       text=TTLocalizer.AvatarPanelCogHealth2 % (HP, maxHP),
                                       text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
        else:
            self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.09), relief=None,
                                   text=TTLocalizer.AvatarPanelCogHealth % (HP, maxHP),
                                   text_font=avatar.getFont(), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
        dept = SuitDNA.getSuitDeptFullname(avatar.dna.name)
        if avatar.dna.name == 'crf':
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.015), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level,
                                          text_font=avatar.getFont(), text_align=TextNode.ACenter,
                                          text_pos=(0, 0), text_scale=0.05, text_wordwrap=8.0)
        elif avatar.dna.name == 'tcm':
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.015), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level,
                                          text_font=avatar.getFont(), text_align=TextNode.ACenter,
                                          text_pos=(0, 0), text_scale=0.05, text_wordwrap=8.0)
        else:
            self.levelLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.04), relief=None,
                                          text=TTLocalizer.AvatarPanelCogLevel % level, text_font=avatar.getFont(),
                                          text_align=TextNode.ACenter, text_pos=(0, 0),
                                          text_scale=0.05, text_wordwrap=8.0)
        corpIcon = avatar.corpMedallion.copyTo(hidden)
        corpIcon.setPosHprScale(0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.corpIcon = DirectLabel(parent=self.frame, geom=corpIcon, geom_scale=0.13, pos=(0, 0, -0.21), relief=None)
        corpIcon.removeNode()
        if revives > 1:
            self.deptLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.31), relief=None, text=dept + ' v%s.0' % revives,
                                     text_font=avatar.getFont(), text_align=TextNode.ACenter, text_fg=Vec4(0, 0, 0, 1),
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
        gui.removeNode()
        base.localAvatar.obscureFriendsListButton(1)

        #create a LerpScaleInterval that scales the frame from 0 to 1
        self.currentInterval = self.__getOpenSequence()
        self.currentInterval.start()

        self.labelInterval = None

        self.frame.setBin("gui-popup", 0)
        self.frame.show()
        messenger.send('avPanelDone')

        self.accept(avatar.uniqueName('suitHpUpdate'), self.__updateHp)
        self.accept(avatar.uniqueName('suitHpUpdate'), self.__updateHealthBar)
        return

    def __updateHealthBar(self, maxHp):
        self.currHP -= self.currHP
        health = float(self.currHP) / float(maxHp)
        if health > 1.5:
            condition = 13
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
        elif health > 0.25:
            condition = 6
        elif health > 0.20:
            condition = 7
        elif health > 0.15:
            condition = 8
        elif health > 0.10:
            condition = 9
        elif health > 0.0:
            condition = 10
        else:
            condition = 11
        #print('UpdateHealthBar - condition is %i' % condition)

        if self.healthCondition != condition:
            if condition in (10, 11):
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75 if condition == 10 else 0.25),
                                      Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, 'blink-task-%s' % id(self))
            else:
                taskMgr.remove(self.uniqueName('blink-task'))
                if self.isImmune:
                    self.healthNode.setColor(1, 1, 1, 1)
                    self.healthNode.setColor(1, 1, 1, 1)
                else:
                    self.healthNode.setColor(self.healthColors[condition], 1)
                    self.healthNode.setColor(self.healthGlowColors[condition], 1)
            self.healthCondition = condition


    def __updateHp(self, currHp, maxHp, delta):
        def __updateLabel(tempHp):
            if tempHp > 9999:
                self.hpLabel['text'] = TTLocalizer.AvatarPanelCogHealth2 % (int(tempHp), maxHp)
            elif maxHp > 9999 and tempHp <= 0:
                self.hpLabel['text'] = TTLocalizer.AvatarPanelCogHealth2 % (0, maxHp)
            elif maxHp > 9999:
                self.hpLabel['text'] = TTLocalizer.AvatarPanelCogHealth2 % (int(tempHp), maxHp)
            elif tempHp <= 0:
                self.hpLabel['text'] = TTLocalizer.AvatarPanelCogHP % (0, maxHp)
            else:
                self.hpLabel['text'] = TTLocalizer.AvatarPanelCogHP % (int(tempHp), maxHp)

        self.labelInterval = Parallel(
            LerpColorScaleInterval(self.hpLabel, duration=0, startColorScale=(1, 0, 0, 1), colorScale=(1, 1, 1, 1), blendType='easeInOut'),
            LerpFunctionInterval(__updateLabel, duration=0, fromData=currHp+delta, toData=currHp, blendType='easeInOut')
        )
        self.labelInterval.start()


    def __blinkRed(self, task):
        if not self.button.isEmpty():
            self.button.setColor(self.healthColors[9], 1)

        if not self.glow.isEmpty():
            self.glow.setColor(self.healthGlowColors[9], 1)

        return Task.done

    def __blinkGray(self, task):
        if not self.button.isEmpty():
            self.button.setColor(self.healthColors[10], 1)

        if not self.glow.isEmpty():
            self.glow.setColor(self.healthGlowColors[10], 1)

        return Task.done



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

    def __cleanupSequence(self):
        if self.currentInterval:
            self.currentInterval.finish()
            self.currentInterval = None

        if self.labelInterval:
            self.labelInterval.finish()
            self.labelInterval = None

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

    @classmethod
    def getRevives(cls, cog):
        return cog.getSkeleRevives()
