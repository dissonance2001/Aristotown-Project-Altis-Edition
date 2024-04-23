from panda3d.core import *
from panda3d.direct import *
from toontown.toonbase import ToontownGlobals
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
        self.hpText = DirectLabel(parent=self, text='', pos=(0.115, 0.1, 0.132), text_scale=0.075)
        self.setScale(0.5)
        #glow = BattleProps.globalPropPool.getProp('glow')
        #glow.reparentTo(button)
        #glow.setScale(0.28)
        #glow.setPos(-0.005, 0.01, 0.015)
        #glow.setColor(Vec4(0.25, 1, 0.25, 0.5))
        self.button = button
        #self.glow = glow
        self.head = None
        self.blinkTask = None
        self.hide()
        healthGui.removeNode()
        gui.removeNode()

    def setCogInformation(self, cog):
        self.cog = cog
        self.updateHealthBar()
        if self.head:
            self.head.removeNode()

        self.head = self.attachNewNode('head')
        for part in cog.headParts:
            copyPart = part.copyTo(self.head)
            copyPart.setDepthTest(1)
            copyPart.setDepthWrite(1)

        p1, p2 = Point3(), Point3()
        self.head.calcTightBounds(p1, p2)
        d = p2 - p1
        biggest = max(d[0], d[1], d[2])
        s = 0.19 / biggest
        if self.cog.dna.name == 'ptr':
            self.head.setPosHprScale(-0.27, 0.5, 0.12, 270, 0, 0, s, s, s)
        elif self.cog.dna.name == 'dfh':
            self.head.setPosHprScale(-0.27, 0.5, 0.12, 270, 0, 0, s, s, s)
        elif self.cog.dna.name == 'bf':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'b':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'dt':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'ac':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'bs':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'cp':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'le':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'brv':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'arb':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'jgd':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'sjg':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'mg':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'ca':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'dvk':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'lsc':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'jdg':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'lit':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'ste':
            self.head.setPosHprScale(-0.27, 0.5, 0.13, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'tyh':
            self.head.setPosHprScale(-0.27, 0.5, 0.13, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'ghd':
            self.head.setPosHprScale(-0.27, 0.5, 0.13, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'csm':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'ffm':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'gm':
            self.head.setPosHprScale(-0.27, 0.5, 0.14, 180, 0, 0, s, s, s)
        elif self.cog.dna.name == 'dvp':
            self.head.setPosHprScale(-0.27, 0.5, 0.16, 180, 0, 0, s, s, s)
        else:
            self.head.setPosHprScale(-0.27, 0.5, 0.12, 180, 0, 0, s, s, s)
        self.setLevelText()

    def setLevelText(self):
        t = 'Level ' + str(self.cog.getActualLevel())
        if self.cog.getSkeleRevives() > 0:
            #self['image_color'] = Vec4(0.5, 0.5, 0.5, 1.0)
            t += TTLocalizer.SkeleRevivePostFix
        if self.cog.getExecutive() or self.cog.getManager() or self.cog.getGovernaught():
            if self.cog.getExecutive():
                #self['image_color'] = Vec4(0.3, 0.3, 0.3, 1.0)
                t += TTLocalizer.ExecutivePostFix
            elif self.cog.getManager():
                #self['image_color'] = Vec4(0.7, 0.4, 0.4, 1.0)
                t += TTLocalizer.ManagerPostFix
            else:
                #self['image_color'] = Vec4(0.361, 0.635, 0.839, 1.0)
                t += TTLocalizer.GovernaughtPostFix
        self.healthText['text'] = t

    def updateHealthBar(self):
        condition = self.cog.healthCondition
        if condition == 7:
            self.blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(1.2), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(self.blinkTask, self.uniqueName('blink-task'))
        elif condition == 8:
            self.blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(1.2), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(self.blinkTask, self.uniqueName('blink-task'))
        elif condition == 9:
            self.blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(self.blinkTask, self.uniqueName('blink-task'))
        elif condition == 10:
            taskMgr.remove(self.uniqueName('blink-task'))
            blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
            taskMgr.add(blinkTask, self.uniqueName('blink-task'))
        else:
            taskMgr.remove(self.uniqueName('blink-task'))
            if not self.button.isEmpty():
                self.button.setColor(self.healthColors[condition], 1)
            
            #if not self.glow.isEmpty():
                #self.glow.setColor(self.healthGlowColors[condition], 1)
        self.hp = self.cog.getHP()
        self.maxHp = self.cog.getMaxHP()
        self.hpText['text'] = str(self.hp) + '/' + str(self.maxHp)

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
        if self.head:
            self.head.removeNode()
            del self.head
        
        if self.blinkTask:
            taskMgr.remove(self.blinkTask)
            self.blinkTask = None
        
        del self.blinkTask
        self.healthNode.removeNode()
        self.button.removeNode()
        #self.glow.removeNode()
        DirectFrame.destroy(self)
