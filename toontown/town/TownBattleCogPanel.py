from panda3d.core import *
from panda3d.direct import *
from toontown.toonbase import ToontownGlobals
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
                    Vec4(1, 0.25, 0, 1.0),
                    Vec4(1, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0.0, 1.0, 1.0, 1),  # overheal
                    Vec4(0.741, 0, 1, 1))
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
                        Vec4(0.741, 0, 1, 0.5))
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
        self.cog = None
        self.suit = None
        self.isLoaded = 0
        self.notify.info("Loading Cog Battle Panel!")
        self.healthText = DirectLabel(parent=self, text='', pos=(0.11, 1.0, 0.244), text_scale=0.065)
        healthGui = loader.loadModel('phase_3.5/models/gui/suit_panel')
        button = healthGui.find('**/status_effect_slot')
        button.setScale(0.63)
        button.setH(0)
        button.setR(0)
        button.setColor(Vec4(0, 1, 0, 1))
        self.accept('inventory-levels', self.__handleToggle)
        self.healthNode = self.attachNewNode('health')
        self.healthNode.setPos(0.125, 0.0, 0.19)
        self.healthNode.setTransparency(1)
        button.reparentTo(self.healthNode)
        self.hpText = DirectLabel(parent=self, text='', text_fg=Vec4(0, 0, 0, 1), pos=(0.115, 0.1, 0.132), text_scale=0.075)
        self.setScale(0.525)
        #glow = BattleProps.globalPropPool.getProp('glow')
        #glow.reparentTo(button)
        #glow.setScale(0.28)
        #glow.setPos(-0.005, 0.01, 0.015)
        #glow.setColor(Vec4(0.25, 1, 0.25, 0.5))
        self.button = button
        #self.glow = glow
        self.head = None
        self.suitHead = None
        self.blinkTask = None
        self.hide()
        healthGui.removeNode()
        gui.removeNode()

    def setCogInformation(self, cog):
        self.cleanupHead()
        self.cog = cog
        self.updateHealthBar()
        #if self.head:
            #self.head.removeNode()

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
        if self.cog.getImmuneStatus():
            if not self.button.isEmpty():
                self.button.setColor(1, 1, 1, 1)
        elif condition == 7 and not self.cog.getImmuneStatus():
            if not self.button.isEmpty():
                self.button.setColor(self.healthColors[condition], 1)
            self.hpText['text_fg'] = Vec4(1, 1, 1, 1.0)
        elif condition == 8 and not self.cog.getImmuneStatus():
            if not self.button.isEmpty():
                self.button.setColor(self.healthColors[condition], 1)
            self.hpText['text_fg'] = Vec4(1, 1, 1, 1.0)
        elif condition == 9 and not self.cog.getImmuneStatus():
            self.blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(self.blinkTask, self.uniqueName('blink-task'))
            self.hpText['text_fg'] = Vec4(1, 1, 1, 1.0)
        elif condition == 10 and not self.cog.getImmuneStatus():
            taskMgr.remove(self.uniqueName('blink-task'))
            blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            self.hpText['text_fg'] = Vec4(1, 1, 1, 1.0)
        elif condition == 11 and not self.cog.getImmuneStatus():
            taskMgr.remove(self.uniqueName('blink-task'))
            blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            self.hpText['text_fg'] = Vec4(1, 1, 1, 1.0)
        elif condition == 13 and not self.cog.getImmuneStatus():
            taskMgr.remove(self.uniqueName('blink-task'))
            if not self.button.isEmpty():
                self.button.setColor(self.healthColors[condition], 1)
            self.hpText['text_fg'] = Vec4(1, 1, 1, 1.0)
        else:
            taskMgr.remove(self.uniqueName('blink-task'))
            if not self.button.isEmpty():
                self.button.setColor(self.healthColors[condition], 1)
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            
            #if not self.glow.isEmpty():
                #self.glow.setColor(self.healthGlowColors[condition], 1)
        if self.cog.getHP() >= 0:
            self.hp = self.cog.getHP()
        else:
            self.hp = 0
        self.maxHp = self.cog.getMaxHP()
        self.hpText['text'] = str(self.hp) + '/' + str(self.maxHp)

    def generateSuitHead(self, name):
        self.suitHead = Suit.attachSuitHead(self, name)
        needBigScaledHeads = 'dot', 'bc', 'cps'
        needMedScaledHeads = 'bf', 'cc', 'sc', 'dsk', 'nar'
        needSmallScaledHeads = 'jas'
        needSmallerScaledHeads = 'mka', 'txm', 'ym', 'bs', 'tw', 'ssm', 'kyl', 'kpn', 'blr', 'fd', 'tb', 'adc', 'drm', 'ffm', 'frs', 'fbd'
        needEvenSmallerScaledHeads = 'ste', 'sd', 'b', 'ac', 'prr', 'wrt', 'jr', 'dvp', 'sb', 'yuh', 'kc'
        if name in needBigScaledHeads:
            self.suitHead.setScale(.13)
        elif name in needMedScaledHeads:
            self.suitHead.setScale(0.12)
        elif name in needSmallScaledHeads:
            self.suitHead.setScale(0.11)
        elif name in needSmallerScaledHeads:
            self.suitHead.setScale(0.09)
        elif name in needEvenSmallerScaledHeads:
            self.suitHead.setScale(0.08)
        elif name == 'cpl':
            self.suitHead.setScale(0.15)
        elif name == 'dvg':
            self.suitHead.setScale(0.15)
        elif name == 'skd':
            self.suitHead.setScale(0.15)
        elif name == 'trm':
            self.suitHead.setScale(0.15)
        elif name == 'cp':
            self.suitHead.setScale(0.065)
        elif name == 'mg':
            self.suitHead.setScale(0.065)
        else:
            self.suitHead.setScale(0.1)
        if name == 'dfh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -90, 0, 0, .1, .1, .1)
        elif name == 'ptr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -90, 0, 0, .1, .1, .1)
        elif name == 'dvp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .08, .08, .08)
        elif name == 'bg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .13, .13, .13)
        elif name == 'scg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .1, .1, .1)
        elif name == 'crf':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .1, .1, .1)
        elif name == 'sjg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .1, .1, .1)
        elif name == 'mad':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .1, .1, .1)
        elif name == 'cg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .14, .14, .14)
        elif name == 'ant':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .3, .3, .3)
        elif name == 'sya':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .14, .14, .14)
        elif name == 'laa':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .14, .14, .14)
        elif name == 'lbs':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .14, .14, .14)
        elif name == 'gb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .14, .14, .14)
        elif name == 'tcc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .3, .3, .3)
        elif name == 'jl':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .3, .3, .3)
        elif name == 'fb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .2, .2, .2)
        elif name == 'mdr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .14, .14, .14)
        elif name == 'fas':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .14, .14, .14)
        elif name == 'jur':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .3, .3, .3)
        elif name == 'bgr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .3, .3, .3)
        elif name == 'gkp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .14, .14, .14)
        elif name == 'ddv':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .14, .14, .14)
        elif name == 'csh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.10, -180, 0, 0, .14, .14, .14)
        elif name == 'cm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.10, -180, 0, 0, .14, .14, .14)
        elif name == 'csm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .09, .09, .09)
        else:
            self.suitHead.setPos(-0.27, 0.5, 0.13)

    def show(self):
        if settings.get('show-cog-levels', True):
            if self.cog:
                self.updateHealthBar()
            self.hidden = False
            self.healthNode.show()
            self.button.show()
            #self.glow.show()
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
        if not self.button.isEmpty():
            self.button.setColor(self.healthColors[9], 1)

        #if not self.glow.isEmpty():
            #self.glow.setColor(self.healthGlowColors[9], 1)
        
        return Task.done
		
    def __blinkGray(self, task):
        if not self.button.isEmpty():
            self.button.setColor(self.healthColors[10], 1)

        #if not self.glow.isEmpty():
            #self.glow.setColor(self.healthGlowColors[10], 1)
        
        return Task.done

    def hide(self):
        if self.blinkTask:
            taskMgr.remove(self.blinkTask)
            self.blinkTask = None

        self.hidden = True
        self.healthNode.hide()
        self.button.hide()
        #self.glow.hide()
        DirectFrame.hide(self)

    def unload(self):
        if self.isLoaded == 0:
            return
        self.isLoaded = 0
        self.exit()
        #del self.glow
        del self.cog
        del self.button
        del self.blinkTask
        del self.hpText
        DirectFrame.destroy(self)

    def cleanup(self):
        self.ignoreAll()
        self.cleanupHead()
        
        if self.blinkTask:
            taskMgr.remove(self.blinkTask)
            self.blinkTask = None
        
        del self.blinkTask
        self.healthNode.removeNode()
        self.button.removeNode()
        #self.glow.removeNode()
        DirectFrame.destroy(self)

    def cleanupHead(self):
        if self.suitHead:
            self.suitHead.removeNode()
            del self.suitHead
