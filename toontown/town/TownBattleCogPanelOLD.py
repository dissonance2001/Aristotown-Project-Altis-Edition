from panda3d.core import *
from panda3d.direct import *
from toontown.toonbase import ToontownGlobals
from direct.interval.IntervalGlobal import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence, Parallel, ActorInterval, Func
from toontown.suit import Suit
from toontown.toonbase.ToontownBattleGlobals import *
from direct.directnotify import DirectNotifyGlobal
import string
from toontown.toon import LaffMeter
from toontown.battle import BattleBase
from toontown.battle import BattleProps
from direct.task.Task import Task
from direct.gui.DirectGui import *
from panda3d.core import *
from panda3d.direct import *
from toontown.toonbase import TTLocalizer

class TownBattleCogPanel(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('TownBattleCogPanel')
    healthColors = (Vec4(0.169, 1, 0, 1),
                    Vec4(0.5, 1, 0, 1),
                    Vec4(0.75, 1, 0, 1),
                    Vec4(1, 1, 0, 1),
                    Vec4(1, 0.866, 0, 1),
                    Vec4(1, 0.6, 0, 1),
                    Vec4(1, 0.5, 0, 1),
                    Vec4(1, 0.396, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0, 0, 0, 0),
                    Vec4(1, 0, 0, 1),
                    Vec4(0.0, 1.0, 1.0, 1),  # overheal
                    Vec4(0.553, 0, 1, 1),  # overcharge
                    Vec4(1, 0.416, 0.937, 1),  # 14 pink silhouette
                    Vec4(0, 0.361, 1, 1),
                    Vec4(1, 1, 1, 1),# 15 blue silhouette
                    Vec4(186 / 255, 82 / 255, 1, 1))
    healthGlowColors = (Vec4(0.25, 1, 0.25, 0.5),
                        Vec4(0.5, 1, 0.25, .5),
                        Vec4(0.75, 1, 0.25, .5),
                        Vec4(1, 1, 0.25, 0.5),
                        Vec4(1, 0.866, 0.25, .5),
                        Vec4(1, 0.6, 0.25, .5),
                        Vec4(1, 0.5, 0.25, 0.5),
                        Vec4(1, 0.396, 0.25, 0.5),
                        Vec4(1, 0, 0, 0.5),
                        Vec4(1, 0, 0, 0.5),
                        Vec4(0, 0, 0, 0.5),
                        Vec4(1, 0, 0, 0),
                        Vec4(0.0, 1.0, 1.0, 0.5),  # overheal
                        Vec4(0.553, 0, 1, 1),
                        Vec4(1, 0.416, 0.937, 1),  # 14 pink silhouette
                        Vec4(0, 0.361, 1, 1),  # 15 blue silhouette
                        Vec4(1, 1, 1, 1),
                        # overcharge
                        Vec4(186 / 255, 82 / 255, 1, 1))
    bossBarColors = (Vec4(0.169, 1, 0, 1),
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
                    Vec4(0.741, 0, 1, 1))
    colorThresholds = (0.65, 0.4, 0.2, 0.1, 0.05)
    bossBarStartPosZ = 1.5
    bossBarEndPosZ = 0.88
    bossBarIncrementAmt = 2

    def __init__(self, id):
        if settings['newGui'] == True:
            gui = loader.loadModel('phase_3.5/models/gui/suit_panel')
        else:
            gui = loader.loadModel('phase_3.5/models/gui/suit_panel')
        
        DirectFrame.__init__(self, relief=None, image=gui.find('**/suit_panel_main'))
        self.initialiseoptions(TownBattleCogPanel)
        self.hidden = False
        self.healthGui = loader.loadModel('phase_3.5/models/gui/suit_panel')
        self.cog = None
        self.suit = None
        self.isLoaded = 0
        self.notify.info("Loading Cog Battle Panel!")
        self.head = None
        self.healthNode = self.attachNewNode('health')
        self.healthNode.setPos(0.125, 0.0, 0.19)
        self.healthNode.setTransparency(1)
        healthBarModel = loader.loadModel('phase_3.5/models/gui/suit_panel')
        healthBar = healthBarModel.find('**/status_effect_slot')
        self.healthBar = healthBar
        healthBar.setScale(0.63)
        healthBar.setH(0)
        healthBar.setR(0)
        healthBar.reparentTo(self.healthNode)
        self.healthBar2 = None
        self.healthText = DirectLabel(parent=self, text='', pos=(0.11, 1.0, 0.244), text_scale=0.065)
        self.setScale(0.525)
        self.hpText = DirectLabel(parent=self, text='', text_fg=Vec4(0, 0, 0, 1), pos=(0.095, 0.125, 0.1335),
                                  text_scale=0.0725)
        self.headActor = None
        self.suitHead = None
        self.animDict = {}
        self.blinkTask = None
        self.hide()
        self.healthGui.removeNode()
        gui.removeNode()

    def setCogInformation(self, cog):
        self.cleanupHead()
        self.cog = cog
        self.updateHealthBar()
        healthBarModel = loader.loadModel('phase_3.5/models/gui/suit_panel')
        self.healthBar2 = DirectWaitBar(parent=self, pos=(-0.025, -0.11, -0.035), relief=DGG.SUNKEN, value=100,
                                        frameSize=(-2.5, 2.75, -0.6, 0.65), barTexture='phase_3.5/maps/battlegui/healthbar.png',
                                        borderWidth=(0.02, 0.02), range=self.cog.getMaxHP(), scale=0.1, sortOrder=50,
                                        frameColor=(0, 0, 0, 0), barColor=(1, 1, 1.0, 1))
        self.healthBar2.reparentTo(self.healthNode)
        self.accept('inventory-levels', self.__handleToggle)

        infoButton = healthBarModel.find('**/Info_Nuetral')
        infoButton.reparentTo(self.healthNode)
        self.infoButton = infoButton
        self.infoButton.setScale(0.3)
        self.infoButton.setH(0)
        self.infoButton.setR(0)
        self.infoButton.setPos(.235, 0, -.035)

        self.generateSuitHead(cog.getStyleName())
        self.setLevelText()

    def setLevelText(self):
        t = 'Level ' + str(self.cog.getActualLevel())
        if self.cog.getExecutive() or self.cog.getManager() or self.cog.getGovernaught():
            if self.cog.getExecutive():
                t += TTLocalizer.ExecutivePostFix
            elif self.cog.getManager():
                t += TTLocalizer.ManagerPostFix
            else:
                t += TTLocalizer.GovernaughtPostFix
        if self.cog.getSkeleRevives() > 0:
            t += TTLocalizer.SkeleRevivePostFix % (self.cog.getSkeleRevives() + 1)
        self.healthText['text'] = t

    def updateHealthBar(self):
        condition = self.cog.healthCondition
        if self.cog.getHP() >= 0:
            self.hp = self.cog.getHP()
        else:
            self.hp = 0
        self.maxHp = self.cog.getMaxHP()
        if condition == 9 and not self.cog.getImmuneStatus():
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
            self.blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(self.blinkTask, self.uniqueName('blink-task'))
        elif condition == 10 and not self.cog.getImmuneStatus():
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
            taskMgr.remove(self.uniqueName('blink-task'))
            blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(blinkTask, self.uniqueName('blink-task'))
        elif condition == 11 and not self.cog.getImmuneStatus():
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
            taskMgr.remove(self.uniqueName('blink-task'))
            blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(blinkTask, self.uniqueName('blink-task'))
        elif condition == 13 and not self.cog.getImmuneStatus():
            taskMgr.remove(self.uniqueName('blink-task'))
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
            self.hpText['text_fg'] = Vec4(1, 1, 1, 1.0)
        else:
            taskMgr.remove(self.uniqueName('blink-task'))
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
        self.hpText['text'] = str(self.hp) + '/' + str(self.maxHp)

    def generateSuitHead(self, name):
        self.suitHead = Suit.attachSuitHead(self, name)
        self.suitHead.setScale(0.1)
        AnimList = 'neutral'
        if name == 'dfh':
            self.suitHead.setPosHprScale(-0.26, 0.5, 0.125, -90, 0, 0, .105, .105, .105)
        elif name == 'ptr':
            self.suitHead.setPosHprScale(-0.26, 0.5, 0.12, -90, 0, 0, .085, .085, .085)
        elif name == 'rng' or name == 'jdg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .115, .115, .115)
        elif name == 'bgh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .09, .09, .09)
        elif name == 'ste' or name == 'wrt' or name == 'cry':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0725, .0725, .0725)
        elif name == 'bg' or name == 'gry':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .105, .105, .105)
        elif name == 'scg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1, .1, .1)
        elif name == 'kpn':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .09, .09, .09)
        elif name == 'crf' or name == 'mad':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .09, .09, .09)
        elif name == 'tld':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .07, .07, .07)
        elif name == 'sjg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .1, .1, .1)
        elif name == 'cn':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.09, -180, 0, 0, .1, .1, .1)
        elif name == 'fbd':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .09, .09, .09)
        elif name == 'mg' or name == 'cp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.135, -180, 0, 0, .06, .06, .06)
        elif name == 'arb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .115, .115, .115)
        elif name == 'ca':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .1, .1, .1)
        elif name == 'bs':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .075, .075, .075)
        elif name == 'ssm' or name == 'cvy' or name == 'mka' or name == 'txm' or name == 'kyl':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .089, .089, .089)
        elif name == 'pp' or name == 'nc' or name == 'sys':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .06, .06, .06)
        elif name == 'p':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .07, .07, .07)
        elif name == 'mb' or name == 'tbc' or name == 'kbc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1, .1, .1)
        elif name == 'bfh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .12, .12, .12)
        elif name == 'b':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .09, .09, .09)
        elif name == 'frs':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .08, .08, .08)
        elif name == 'prethink':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .1, .1, .1)
        elif name == 'gtk':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .1, .1, .1)
        elif name == 'mouthp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1, .1, .1)
        elif name == 'bf':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.011, -180, 0, 0, .11, .11, .11)
        elif name == 'cps':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .16, .16, .16)
        elif name == 'trb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .095, .095, .095)
        elif name == 'ssr' or name == 'mm' or name == 'ym' or name == 'ds' or name == 'pht' or name == 'jb' or name == 'ms' or name == 'ka' or name == 'pyc' or name == 'vpr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .1, .1, .1)
        elif name == 'ls' or name == 'mh' or name == 'sdb' or name == 'inw' or name == 'm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .085, .085, .085)
        elif name == 'sb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .075, .075, .075)
        elif name == 'cfp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .09, .09, .09)
        elif name == 'hh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .12, .12, .12)
        elif name == 'lsc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .09, .09, .09)
        elif name == 'brv':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .1, .1, .1)
        elif name == 'ac':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.09, -180, 0, 0, .09, .09, .09)
        elif name == 'gm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .11, .11, .11)
        elif name == 'rus' or name == 'tm' or name == 'cr' or name == 'shp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .085, .085, .085)
        elif name == 'bw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .06, .06, .06)
        elif name == 'le':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .09, .09, .09)
        elif name == 'sd':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.09, -180, 0, 0, .08, .08, .08)
        elif name == 'cc' or name == 'sc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .12, .12, .12)
        elif name == 'dvg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .17, .177, .177)
        elif name == 'bdb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .12, .12, .12)
        elif name == 'dot':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .175, .175, .175)
        elif name == 'f' or name == 'cpl' or name == 'trm' or name == 'sw' or name == 'skd' or name == 'bc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .175, .175, .175)
        elif name == 'rb' or name == 'gh' or name == 'phs' or name == 'sfs':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .08, .08, .08)
        elif name == 'bkp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .085, .085, .085)
        elif name == 'msr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .09, .09, .09)
        elif name == 'dsf':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .075, .075, .075)
        elif name == 'dm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .075, .075, .075)
        elif name == 'trk':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .085, .085, .085)
        elif name == 'fd':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1, .1, .1)
        elif name == 'nar':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .175, .175, .175)
        elif name == 'tc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .07, .07, .07)
        elif name == 'isw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .1, .1, .1)
        elif name == 'tb' or name == 'ts':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .08, .08, .08)
        elif name == 'tg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .12, .12, .12)
        elif name == 'adc' or name == 'drm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .08, .08, .08)
        elif name == 'mes':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .075, .075, .075)
        elif name == 'fm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .08, .08, .08)
        elif name == 'dsk':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .105, .105, .105)
        elif name == 'blr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .08, .08, .08)
        elif name == 'dfg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .055, .055, .055)
        elif name == 'yuh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .055, .055, .055)
        elif name == 'dfr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .09, .09, .09)
        elif name == 'dvk':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .08, .08, .08)
        elif name == 'tcm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .1, .1, .1)
        elif name == 'ffm' or name == 'nhy' or name == 'bsh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .08, .08, .08)
        elif name == 'jr' or name == 'prr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .065, .065, .065)
        elif name == 'cg' or name == 'laa' or name == 'csh' or name == 'kerberos' or name == 'charon' or name == 'ddv' or name == 'sya' or name == 'mdr' or name == 'fas' or name == 'gkp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .125, .125, .125)
        elif name == 'hydra' or name == 'styx' or name == 'bgr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .3, .3, .3)
        elif name == 'jur' or name == 'ant' or name == 'nix':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .2, .2, .2)
        elif name == 'cm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .1, .1, .1)
        elif name == 'whunter':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0575, .0575, .0575)
        elif name == 'th' or name == 'dvp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.155, -180, 0, 0, .07, .07, .07)
        elif name == 'mp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .08, .08, .08)
        elif name == 'tr' or name == 'msp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .075, .075, .075)
        elif name == 'kb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .09, .09, .09)
        elif name == 'csm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.15, -180, 0, 0, .09, .09, .09)
        elif name == 'hho':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .11, .11, .11)
        else:
            self.suitHead.setPos(-0.27, 0.5, 0.13)

    def show(self):
        if settings.get('show-cog-levels', True):
            if self.cog:
                self.updateHealthBar()
            self.hidden = False
            self.healthNode.show()
            DirectFrame.show(self)
        else:
            self.notify.debug('Tried to unhide Cog levels when settings have not been updated!')

    def __handleToggle(self):
        if self.cog:
            if self.hidden:
                self.show()
            else:
                self.hide()

    def __blinkRed(self, task):
        if self.healthBar2:
            self.healthBar2.setProp('barColor', self.healthColors[9])
            self.healthBar2.setProp('value', self.cog.getHP())
        
        return Task.done
		
    def __blinkGray(self, task):
        if self.healthBar2:
            self.healthBar2.setProp('barColor', self.healthColors[10])
            self.healthBar2.setProp('value', self.cog.getHP())
        
        return Task.done

    def hide(self):
        if self.blinkTask:
            taskMgr.remove(self.blinkTask)
            self.blinkTask = None

        self.hidden = True
        self.healthNode.hide()
        DirectFrame.hide(self)

    def unload(self):
        if self.isLoaded == 0:
            return
        self.isLoaded = 0
        self.exit()
        del self.cog
        del self.blinkTask
        del self.hpText
        del self.healthBar2
        DirectFrame.destroy(self)

    def cleanup(self):
        self.ignoreAll()
        self.cleanupHead()
        
        if self.blinkTask:
            taskMgr.remove(self.blinkTask)
            self.blinkTask = None
        
        del self.blinkTask
        self.healthNode.removeNode()
        DirectFrame.destroy(self)

    def cleanupHead(self):
        if self.suitHead:
            self.suitHead.removeNode()
            del self.suitHead
