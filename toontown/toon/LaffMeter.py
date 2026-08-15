from pandac.PandaModules import Vec4
import random
from direct.task import Task
import math

from panda3d.core import *
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton
from direct.interval.FunctionInterval import Func, Wait
from direct.interval.MetaInterval import Sequence, Parallel
from otp.otpbase import OTPGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownIntervals
from toontown.toonbase import TTLocalizer

class LaffMeter(DirectFrame):
    deathColor = Vec4(0.58039216, 0.80392157, 0.34117647, 1.0)
    flyoutLabelGenerator = TextNode('flyoutLabelGenerator')

    def __init__(self, avdna, hp, maxHp, isLocalHealth=False):
        DirectFrame.__init__(self, relief=None, sortOrder=50)
        self.initialiseoptions(LaffMeter)

        self.style = avdna
        self.av = None
        self.hp = hp
        self.maxHp = maxHp
        self.flashName = None
        self.flashIval = None
        self.flashThreshold = 1
        self.overhead = False
        self.__obscured = 0
        self.isLocalHealth = isLocalHealth
        self.container = DirectFrame(parent=self, relief=None)
        self.boosterPopup = None
        self.boosterDetailsButton = None

        self.isToon = 1 if self.style.type == 't' else 0

        self.load()
        self.baseX = self.getX()
        self.swayAmplitude = 0.01
        self.swaySpeed = 2.0

        taskMgr.add(self.swayTask, "LaffMeterSwayTask")

    def swayTask(self, task):
        if self.isEmpty() or self.getParent() is None:
            return Task.done

        t = task.time
        tiltAmplitude = 3.0
        tiltSpeed = 1.2
        newR = math.sin(t * tiltSpeed) * tiltAmplitude
        self.setR(newR)
        return Task.cont

    def fixOverhead(self):
        self.container.setDepthTest(1)
        self.container.setDepthWrite(1)
        self.container.setY(.01)
        self.frown.setY(-.02)
        self.smile.setY(-.01)
        self.eyes.setY(-.01)
        self.openSmile.setY(-.02)
        self.maxLabel.setY(-.01)
        self.hpLabel.setY(-.01)
        for t in self.teeth:
            t.setY(-.01)

        self.overhead = True

    # Called when we take damage or get laff, makes a number fly out of the meter
    def makeDeltaNumber(self, delta):

        def cleanup(node):
            node.removeNode()

        if delta == 0:
            return

        numString = '+' if delta > 0 else ''
        numColor = (0, .9, 0, 1) if delta > 0 else (.9, 0, 0, 1)
        numString += str(delta)

        self.flyoutLabelGenerator.setFont(OTPGlobals.getSignFont())
        self.flyoutLabelGenerator.setText(numString)
        self.flyoutLabelGenerator.clearShadow()
        self.flyoutLabelGenerator.setAlign(TextNode.ACenter)
        self.flyoutLabelGenerator.setTextColor(numColor)
        node = self.flyoutLabelGenerator.generate()
        hptextnode = self.attachNewNode(node)
        hptextnode.setScale(.1)
        hptextnode.setBillboardPointEye()
        if self.overhead:
            hptextnode.setBin('fixed', 100)
        ypos = -1.01 + random.random()  # Used to mitigate z fighting
        hptextnode.setPos(0, ypos, 0)
        hptextnode.setR(9)
        xgoal = random.random() + 1.4
        zgoal = random.random() + 1.4
        sgoal = 1.4
        if self.overhead:
            sgoal *= 1.5
        Sequence(
            Parallel(
                hptextnode.scaleInterval(.2, sgoal),
                hptextnode.posInterval(1.3, Point3(xgoal, ypos, zgoal), blendType='easeInOut'),
                hptextnode.colorScaleInterval(1.3, Vec4(numColor[0], numColor[1], numColor[2], 0))
            ),
            Func(cleanup, hptextnode)
        ).start()

    def setFlashThreshold(self, num):
        self.flashThreshold = num
        
    def showGags(self):
        self.showDetailsButton['command'] = self.backToDetails
        self.gagsBtn.hide()
        self.toontasksButton.hide()
        messenger.send('home')
        self.accept('home-up', self.backToDetails)
        self.accept('end-up', self.backToDetails)
        
    def showTasks(self):
        self.showDetailsButton['command'] = self.backToDetails
        self.gagsBtn.hide()
        self.toontasksButton.hide()
        messenger.send('end')
        self.accept('home-up', self.backToDetails)
        self.accept('end-up', self.backToDetails)
        
    def backToDetails(self):
        self.showDetailsButton['command'] = self.hideDetailsPopup
        self.gagsBtn.show()
        self.toontasksButton.show()
        self.ignore('home-up')
        self.ignore('end-up')
        messenger.send('home-up')
        messenger.send('end-up')

    def showDetailsPopup(self):
        # TODO: Bring up a little popup with buttons to choose between showing tasks and showing gags
        self.showDetailsButton.setColorScale(1, 1, 1, 1)
        gagicnmodel = loader.loadModel('phase_3.5/models/gui/inventory_icons')
        gagicon = gagicnmodel.find('**/inventory_tart')
        gagicnmodel.removeNode()
        self.gagsBtn = DirectButton(parent = aspect2d, relief = None, pos = (-.4, 0, 0), text_style = 3, text_pos = (0, -.3), text_scale = 0.08, text = TTLocalizer.InventoryPageTitle, geom = gagicon, geom_scale = 2, scale = 1, command = self.showGags)
        tasksicnmodel = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        tasksicon = tasksicnmodel.find('**/questCard')
        tasksicnmodel.removeNode()
        self.toontasksButton = DirectButton(parent = aspect2d, relief = None, pos = (.4, 0, 0), text_style = 3, text_pos = (0, -.3), text_scale = 0.08, text = TTLocalizer.QuestPageToonTasks, geom = tasksicon, geom_scale = .35, scale = 1, command = self.showTasks)
        self.backToDetails()
        
    def hideDetailsPopup(self):
        self.showDetailsButton.setColorScale(1, 1, 1, 0)
        messenger.send('home-up')
        messenger.send('end-up')
        self.gagsBtn.destroy()
        self.toontasksButton.destroy()
        
        self.showDetailsButton['command'] = self.showDetailsPopup
        
    def closeBoosterPopup(self):
        if not self.boosterPopup:
            return
        try:
            self.boosterPopup.close()
        except:
            try:
                self.boosterPopup.destroy()
            except:
                pass
        self.boosterPopup = None

    def toggleBoosterPopup(self):
        if not self.isLocalHealth:
            return
        if self.boosterPopup:
            self.closeBoosterPopup()
            return
        try:
            from toontown.gumball.BoosterStatusPopup import BoosterStatusPopup
            self.boosterPopup = BoosterStatusPopup(self)
        except:
            self.boosterPopup = None

    def obscure(self, obscured):
        self.__obscured = obscured
        if self.__obscured:
            self.closeBoosterPopup()
            self.hide()
            base.localAvatar.expBar.hide() # Hacky, I know, but I'll figure out a better way to hide the exp bar

    def isObscured(self):
        return self.__obscured

    def load(self):
        gui = loader.loadModel('phase_3/models/gui/laff_o_meter')
        if self.isToon:
            hType = self.style.getType()
            if hType == 'dog':
                headModel = gui.find('**/laffMeter_dog')
            elif hType == 'cat':
                headModel = gui.find('**/laffMeter_cat')
            elif hType == 'mouse':
                headModel = gui.find('**/laffMeter_mouse')
            elif hType == 'horse':
                headModel = gui.find('**/laffMeter_horse')
            elif hType == 'rabbit':
                headModel = gui.find('**/laffMeter_rabbit')
            elif hType == 'duck':
                headModel = gui.find('**/laffMeter_duck')
            elif hType == 'monkey':
                headModel = gui.find('**/laffMeter_monkey')
            elif hType == 'bear':
                headModel = gui.find('**/laffMeter_bear')
            elif hType == 'pig':
                headModel = gui.find('**/laffMeter_pig')
            elif hType == 'deer':
                headModel = gui.find('**/laffMeter_deer')
            elif hType == 'beaver':
                headModel = gui.find('**/laffMeter_beaver')
            elif hType == 'alligator':
                headModel = gui.find('**/laffMeter_alligator')
            elif hType == 'fox':
                headModel = gui.find('**/laffMeter_fox')
            elif hType == 'bat':
                headModel = gui.find('**/laffMeter_bat')
            elif hType == 'raccoon':
                headModel = gui.find('**/laffMeter_raccoon')
            elif hType == 'turkey':
                headModel = gui.find('**/laffMeter_turkey')
            elif hType == 'koala':
                headModel = gui.find('**/laffMeter_koala')
            elif hType == 'kangaroo':
                headModel = gui.find('**/laffMeter_kangaroo')
            elif hType == 'kiwi':
                headModel = gui.find('**/laffMeter_kiwi')
            elif hType == 'armadillo':
                headModel = gui.find('**/laffMeter_armadillo')
            else:
                raise StandardError('unknown toon species: ', hType)
            self.color = self.style.getHeadColor()
            self.container['image'] = headModel
            self.container['image_color'] = self.color
            self.resetFrameSize()
            self.setScale(0.1)
            self.frown = DirectFrame(parent=self.container, relief=None, image=gui.find('**/frown'))
            self.frown.setY(-0.1)
            self.smile = DirectFrame(parent=self.container, relief=None, image=gui.find('**/smile'))
            self.smile.setY(-0.1)
            self.eyes = DirectFrame(parent=self.container, relief=None, image=gui.find('**/eyes'))
            self.eyes.setY(-0.1)
            toothScale = (.92, .92, 0.87)
            toothPos = (-0.03, 0.0, -0.33)
            self.openSmile = DirectFrame(parent=self.container, relief=None, image=gui.find('**/open_smile'), image_pos=(-0.03, 0.0, -0.63), image_scale=toothScale)
            self.openSmile.setY(-0.1)
            self.tooth1 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_1'),
                                      image_pos=toothPos, image_scale=toothScale)
            self.tooth2 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_2'),
                                      image_pos=toothPos, image_scale=toothScale)
            self.tooth3 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_3'),
                                      image_pos=toothPos, image_scale=toothScale)
            self.tooth4 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_4'),
                                      image_pos=toothPos, image_scale=toothScale)
            self.tooth5 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_5'),
                                      image_pos=toothPos, image_scale=toothScale)
            self.tooth6 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_6'),
                                      image_pos=toothPos, image_scale=toothScale)
            self.maxLabel = DirectLabel(parent=self.eyes, relief=None, pos=(0.442, 0, 0.051), text='120', text_scale=0.4, text_font=ToontownGlobals.getInterfaceFont())
            self.maxLabel.setY(-0.1)
            self.hpLabel = DirectLabel(parent=self.eyes, relief=None, pos=(-0.398, 0, 0.051), text='120', text_scale=0.4, text_font=ToontownGlobals.getInterfaceFont())
            self.hpLabel.setY(-0.1)
            self.teeth = [self.tooth6,
             self.tooth5,
             self.tooth4,
             self.tooth3,
             self.tooth2,
             self.tooth1]
            for tooth in self.teeth:
                tooth.setY(-0.6)
            self.fractions = [0.0,
             0.166666,
             0.333333,
             0.5,
             0.666666,
             0.833333]
            if self.isLocalHealth:
                self.boosterDetailsButton = DirectButton(parent=self.container, relief=None,
                                                         frameColor=(1, 1, 1, 0),
                                                         frameSize=(-1.15, 1.15, -1.25, 1.20),
                                                         command=self.toggleBoosterPopup, pressEffect=0)
                self.boosterDetailsButton.setTransparency(TransparencyAttrib.MAlpha)
            #if self.isLocalHealth: # Embed a little invisible button to show gags when clicking on the laff
               # self.showDetailsButton = DirectButton(relief = None, parent = self.container, image = 'phase_3/maps/android/tui_move_l.png', scale = (1), command = self.showDetailsPopup)
                #self.showDetailsButton.setTransparency(1)
               # self.showDetailsButton.setColorScale(1, 1, 1, 0) # Make it invisible - it still recognizes clicks
        gui.removeNode()

    def destroy(self):
        self.closeBoosterPopup()
        if self.boosterDetailsButton:
            try:
                self.boosterDetailsButton.destroy()
            except:
                pass
            self.boosterDetailsButton = None
        if self.av:
            ToontownIntervals.cleanup(self.av.uniqueName('laffMeterBoing') + '-' + str(self.this))
            ToontownIntervals.cleanup(self.av.uniqueName('laffMeterBoing') + '-' + str(self.this) + '-play')
            self.stopFlash()
            self.ignore(self.av.uniqueName('hpChange'))
        del self.style
        del self.av
        del self.hp
        del self.maxHp
        if self.isToon:
            del self.frown
            del self.smile
            del self.openSmile
            del self.tooth1
            del self.tooth2
            del self.tooth3
            del self.tooth4
            del self.tooth5
            del self.tooth6
            del self.teeth
            del self.fractions
            del self.maxLabel
            del self.hpLabel
        DirectFrame.destroy(self)

    def adjustTeeth(self):
        if self.isToon:
            for i in xrange(len(self.teeth)):
                if self.hp > self.maxHp * self.fractions[i]:
                    self.teeth[i].show()
                else:
                    self.teeth[i].hide()

    def adjustText(self):
        if self.isToon:
            if self.maxLabel['text'] != str(self.maxHp) or self.hpLabel['text'] != str(self.hp):
                self.maxLabel['text'] = str(self.maxHp)
                self.hpLabel['text'] = str(self.hp)

    def animatedEffect(self, delta):
        if delta == 0 or self.av == None:
            return
        name = self.av.uniqueName('laffMeterBoing') + '-' + str(self.this)
        ToontownIntervals.cleanup(name)
        if delta > 0:
            ToontownIntervals.start(ToontownIntervals.getPulseLargerIval(self, name))
        else:
            ToontownIntervals.start(ToontownIntervals.getPulseSmallerIval(self, name))

    def startFlash(self):
        self.stopFlash()
        self.flashIval = ToontownIntervals.getFlashIval(self, self.flashName)
        ToontownIntervals.loop(self.flashIval)

    def stopFlash(self):
        if not self.flashIval:
            return

        self.flashIval.finish()
        ToontownIntervals.cleanup(self.flashName)
        self.flashIval = None

    def adjustFace(self, hp, maxHp, quietly=0):

        self.stopFlash()
        if self.isToon and self.hp != None:
            self.frown.hide()
            self.smile.hide()
            self.openSmile.hide()
            self.eyes.hide()
            for tooth in self.teeth:
                tooth.hide()

            delta = hp - self.hp
            deltaIgnoringNegative = hp - max(0, self.hp)
            numToShow = deltaIgnoringNegative

            # If laff is negative, and new laff is also negative dont show
            if hp < 0 and self.hp < 0:
                numToShow = 0

            self.makeDeltaNumber(numToShow)
            self.hp = hp
            self.maxHp = maxHp
            if self.hp < 1:
                self.frown.show()
                self.container['image_color'] = self.deathColor
            elif self.hp >= self.maxHp:
                self.smile.show()
                self.eyes.show()
                self.container['image_color'] = self.color
            else:
                self.openSmile.show()
                self.eyes.show()
                self.maxLabel.show()
                self.hpLabel.show()
                self.container['image_color'] = self.color
                self.adjustTeeth()
            self.adjustText()
            if not quietly:
                self.animatedEffect(delta)

            if (float(self.hp) / float(self.maxHp)) <= 0.166666:
                self.startFlash()

    def start(self):
        if self.av:
            self.hp = self.av.hp
            self.maxHp = self.av.maxHp
        if self.isToon:
            if not self.__obscured:
                self.show()
            self.adjustFace(self.hp, self.maxHp, 1)
            if self.av:
                self.accept(self.av.uniqueName('hpChange'), self.adjustFace)

    def stop(self):
        if self.isToon:
            self.closeBoosterPopup()
            self.hide()
            if self.av:
                self.ignore(self.av.uniqueName('hpChange'))

    def setMeterColor(self, color=None):
        if color is None:
            self.color = self.style.getHeadColor()
        else:
            self.color = Vec4(color)
        try:
            self.container['image_color'] = self.color
        except:
            pass

    def setAvatar(self, av):
        if self.av:
            self.ignore(self.av.uniqueName('hpChange'))
            self.ignore(self.av.uniqueName('set-laff-meter-color'))
        
        self.av = av
        self.flashName = self.av.uniqueName('laffMeterFlash') + '-' + str(self.this)
        self.accept(self.av.uniqueName('set-laff-meter-color'), self.setMeterColor)
        try:
            frozenColor = getattr(self.av, '_plutocratLaffMeterColor', None)
            if frozenColor is not None:
                self.setMeterColor(frozenColor)
        except:
            pass
