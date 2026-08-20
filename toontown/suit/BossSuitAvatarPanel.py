from __future__ import absolute_import
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
from toontown.suit import SuitDNA
from toontown.suit import BossCog
from toontown.battle import BattleProps
from toontown.shtiker import CogPageGlobals as CPG
from toontown.friends import FriendsListPanel
from toontown.suit import Suit
from direct.interval.IntervalGlobal import *
from direct.showbase import DirectObject
from panda3d.core import *


class BossSuitAvatarPanel(AvatarPanel.AvatarPanel, DirectObject.DirectObject):
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
                    Vec4(0.3, 0.3, 0.3, 1), #out
                    Vec4(1, 0, 0, 1), #12
                    Vec4(0.0, 1.0, 1.0, 1),  # overheal
                    Vec4(0.553, 0, 1, 1),  # overcharge
                    Vec4(1, 0.6, 0.89, 1),  # 14 pink silhouette
                    Vec4(0, 0.361, 1, 1),
                    Vec4(1, 1, 1, 1),  # 15 blue silhouette
                    Vec4(186 / 255, 82 / 255, 1, 1),
                    Vec4(0.702, 0, 1, 1),
                    Vec4(1, 1, 1, 1),
                    Vec4(1, 0, 0.906, 1), #18
                    Vec4(0, 0.502, 0.502, 1), #19 teal
                    Vec4(0.827, 0.686, 0.216, 1)) # 20 gold
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
                    Vec4(0, 0, 0, 0), #out
                    Vec4(1, 0, 0, 1),
                    Vec4(0.0, 1.0, 1.0, 1),  # overheal
                    Vec4(0.553, 0, 1, 1),  # overcharge
                    Vec4(1, 0.6, 0.89, 1),  # 14 pink silhouette
                    Vec4(0, 0.361, 1, 1),
                    Vec4(1, 1, 1, 1),  # 15 blue silhouette
                    Vec4(186 / 255, 82 / 255, 1, 1),
                        Vec4(0.702, 0, 1, 1),
                        Vec4(1, 1, 1, 1),
                        Vec4(1, 0, 0.906, 1), 
                   Vec4(0, 0.502, 0.502, 1), #19 teal
                    Vec4(0.827, 0.686, 0.216, 1)
                        ) #18 white

    def __init__(self, avatar):
        AvatarPanel.AvatarPanel.__init__(self, avatar, FriendsListPanel=FriendsListPanel)
        self.avName = avatar.getName()
        self.avatr = avatar
        self.name = None
        gui = loader.loadModel('phase_3.5/models/gui/suit_detail_panel')
        gui.find('**/shadow').setTransparency(TransparencyAttrib.MAlpha)
        gui.find('**/shadow').setColor(1, 1, 1, 0.4)
        self.frame = DirectFrame(geom=gui.find('**/avatar_panel'), geom_scale=0.21, geom_color=(0.69, 0.706, 0.718, 1), geom_pos=(0, 0, 0.02), relief=None, pos=(-0.23, 0, -0.46), parent=base.a2dTopRight)
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
        s = 0.3 / biggest
        self.head.setPosHprScale(0, 0, 0.05, -90, 0, 270, s, s, s)
        self.avatar = avatar
        if avatar.dna.dept == 't':
            nameText = "Chief Information Officer"
        elif avatar.dna.dept == 's':
            nameText = "Senior Vice President"
        elif avatar.dna.dept == 'c':
            nameText = "Chief Executive Officer"
        elif avatar.dna.dept == 'm':
            nameText = "Chief Financial Officer"
        elif avatar.dna.dept == 'l':
            nameText = "Chief Legal Officer"
        elif avatar.dna.dept == 'g':
            nameText = "Chairman Of The Board"
        elif avatar.dna.dept == 'p':
            nameText = "Chief Press Officer"
        else:
            nameText = ""
        self.nameLabel = DirectLabel(parent=self.frame, pos=(0, 0, 0.36), relief=None,
                                     text=nameText,
                                     text_font=avatar.getFont(), text_pos=(0, 0),
                                     text_scale=0.0475, text_wordwrap=8, text_shadow=(1, 1, 1, 1))
        healthGui = loader.loadModel('phase_3.5/models/char/ttcc_ene_insignias')
        glow = healthGui.find('**/glow')
        glow.setScale(0)
        glow.setPos(0, 0, 0)
        glow.hide()
        button = healthGui.find('**/emblem_hp')
        button.setScale(0.275)
        button.setH(0)
        button.setPos(0, 0, -0.05)
        base2 = healthGui.find('**/emblem_base')
        base2.setScale(0.275)
        base2.setH(0)
        base2.setPos(0, 0, -0.05)
        glow.reparentTo(button)
        self.button = button
        self.glow = glow
        self.base2 = base2
        corpIcon = avatar.corpMedallion.copyTo(hidden)
        corpIcon.setPosHprScale(0, 0, 0, 0, 0, 0, 0, 0, 0)
        #self.corpIcon = DirectLabel(parent=self.frame, geom=corpIcon, geom_scale=0.13, pos=(0, 0, -0.20), relief=None)
        self.hpLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.035), relief=None,
                                       text='',
                                       text_font=avatar.getFont(), text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0),
                                       textMayChange=1,
                                       text_scale=0.05, text_wordwrap=7.5)
        if avatar.dna.dept == 't':
            dept = "Head Of The Techbot Department"
        elif avatar.dna.dept == 's':
            dept = "Head Of The Sellbot Department"
        elif avatar.dna.dept == 'c':
            dept = "Head Of The Bossbot Department"
        elif avatar.dna.dept == 'm':
            dept = "Head Of The Cashbot Department"
        elif avatar.dna.dept == 'l':
            dept = "Head Of The Lawbot Department"
        elif avatar.dna.dept == 'g':
            dept = "Head Of The Boardbot Department"
        elif avatar.dna.dept == 'p':
            dept = "Head Of The Pressbot Department"
        else:
            dept = "Head Of The Nothing Department"
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
        self.corpIcon = DirectLabel(parent=self.hpLabel, geom=corpIcon, geom_scale=0.275, pos=(0, 0, -0.05), relief=None)
        #self.healthNode.hide()
        self.healthNode.setY(2)
        self.deptLabel = DirectLabel(parent=self.frame, pos=(0, 0, -0.2175), relief=None,
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


        self.currentInterval = self.__getOpenSequence()
        self.currentInterval.start()

        self.headTask = None

        self.labelInterval = None

        self.healthBarInterval = None

        self.buttonInterval = None

        self.changeInterval = None

        self.blinkTask = None

        self.frame.setBin("gui-popup", 0)
        self.frame.show()
        messenger.send('avPanelDone')
        return


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
