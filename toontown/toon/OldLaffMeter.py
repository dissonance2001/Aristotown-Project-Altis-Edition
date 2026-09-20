"""OldLaffMeter module: contains the class definition for handling the
laff-o-meter"""
from typing import Optional

from panda3d.core import Vec4
from direct.gui.DirectGui import DirectFrame, DirectLabel
from direct.interval.IntervalGlobal import *

from toontown.modifiers.ModifierEnums import HP_MODIFIERS, ModifierType
from toontown.quest3.base import QuestGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownIntervals

defaultPosScale = (0, -0.002, -0.35, 0.95, 0.95, 0.9)
species2PosScale = {
    'cat': [0, -0.002, -0.35, 0.95, 0.95, 0.85],
    'bat': [0, -0.002, -0.35, 0.95, 0.95, 0.85],
}

species2ImagePos = {
    'dog': (0, 0, 0.025),
    'bat': (0.05, 0, 0),
    'koala': (0.05, 0, 0.05),
    'kangaroo': (0.05, 0, 0.15),
    'armadillo': (-0.015, 0, 0.05),
    'turkey': (0.15, 0, 0),
    'deer': (0.05, 0, 0),
}
species2ImageScale = {
    'armadillo': (0.9, 0.925, 0.925),
}


class OldLaffMeter(DirectFrame):
    deathColor = Vec4(0.58039216, 0.80392157, 0.34117647, 1.0)

    def __init__(self, avdna, hp, maxHp, isLocalHealth=False, animated=True, isOverhead=False, battleGui: bool = False):
        """__init(self, AvatarDNA, int, int)
        OldLaffMeter constructor: create a laff-o-meter for a given DA

        :param ToonDNA avdna: AvatarDNA
        :type hp: int
        :type maxHp: int
        """
        DirectFrame.__init__(self, relief=None, sortOrder=50)
        self.initialiseoptions(OldLaffMeter)
        self.style = avdna
        self.av = None
        self.hp = hp
        self.maxHp = maxHp
        self.hit = base.loader.loadSfx('phase_6/audio/sfx/laff_loss.ogg')
        self.flashInterval = None
        self.warningFlash = None
        self.__obscured = 0
        self.isLocalHealth = isLocalHealth
        self.container = DirectFrame(parent=self, relief=None)
        self.rotateIval = None
        self.animated = animated
        self.isOverhead = isOverhead
        self.color = None
        self.speciesOverride = None
        self.cleanedUp = False
        self.stopped: bool = False
        self.battleGui = battleGui
        self.accept(self.globalUpdateEvent(), self.update)
        self.accept('option-update-health-meter-mode', lambda _: self.show())

        if self.style.type == 't':
            self.isToon = 1
        else:
            self.isToon = 0

        self.load()

    def show(self, force: bool = False):
        if not force:
            if self.__obscured or self.stopped or (self.isOverhead and not self.__shouldDisplayMeter()):
                return super().hide()
        super().show()

    def __shouldDisplayMeter(self):
        if base.localAvatar and base.localAvatar.getHideLaffMeters():
            return False
        meterMode = settings.get('health-meter-mode', 2)
        if not self.av:
            return False
        elif QuestGlobals.isInTutorial(self.av):
            return False
        elif meterMode == 0:
            return False
        elif meterMode == 1:
            return True
        elif meterMode == 2:
            if not self.av.getHp() or not self.av.getMaxHp():
                return False
            return self.av.getHp() < self.av.getMaxHp()

    def acceptEvents(self):
        # Called when self.av is defined.
        if self.cleanedUp:
            return
        self.accept(self.av.uniqueName('set-laff-meter-color'), self.setMeterColor)
        self.accept(self.av.uniqueName('set-laff-meter-species'), self.setSpeciesOverride)
        self.acceptModifierEvent()

    def acceptModifierEvent(self):
        self.cleanupModifierEvent()
        self.av.hookCallbackToModifier(
            *HP_MODIFIERS,
            method=self.update,
        )

    def cleanupModifierEvent(self):
        self.av.clearCallbackToModifier(*HP_MODIFIERS)

    @staticmethod
    def globalUpdateEvent() -> str:
        return 'update-laff-meter'

    def obscure(self, obscured):
        """
        Make the be button be obscured, regardless of show and hide

        :param int obscured: 1 = obscure, 0 = unobscured
        """
        self.__obscured = obscured
        if self.__obscured:
            self.hide()
        else:
            self.show()

    def isObscured(self):
        return self.__obscured

    def load(self):
        gui = loader.loadModel('phase_3/models/gui/laff_o_meter')
        if self.isToon:
            hType = self.style.getType()
            try:
                headModel = gui.find('**/laffMeter_%s' % hType)
            except:
                raise Exception('unknown toon species: ', hType)
            self.color = self.style.getHeadColor()

            self.container['image'] = headModel
            self.container['image_pos'] = species2ImagePos.get(hType, (0, 0, 0))
            self.container['image_scale'] = species2ImageScale.get(hType, 1.0)
            self.container['image_color'] = self.color
            self.container.setDepthTest(1)
            self.container.setDepthWrite(1)

            self.resetFrameSize()
            self.setScale(0.1)
            self.frown = DirectFrame(parent=self.container, relief=None, image=gui.find('**/frown'))
            self.smile = DirectFrame(parent=self.container, relief=None, image=gui.find('**/smile'))
            self.eyes = DirectFrame(parent=self.container, relief=None, image=gui.find('**/eyes'))
            if self.isOverhead:
                self.container.setY(0.01)
            self.frown.setY(-0.002)
            self.smile.setY(-0.001)
            self.eyes.setY(-0.001)
            self.openSmile = DirectFrame(parent=self.container, relief=None, image=gui.find('**/open_smile'))

            posScale = species2PosScale.get(hType, defaultPosScale)
            self.openSmile.setPos(*posScale[:3])
            self.openSmile.setScale(*posScale[3:6])

            self.tooth1 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_1'))
            self.tooth2 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_2'))
            self.tooth3 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_3'))
            self.tooth4 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_4'))
            self.tooth5 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_5'))
            self.tooth6 = DirectFrame(parent=self.openSmile, relief=None, image=gui.find('**/tooth_6'))

            self.maxLabel = DirectLabel(
                parent=self.eyes,
                relief=None,
                pos=(0.442, 0, 0.051),
                text='120',
                text_scale=0.45,
                text_font=ToontownGlobals.getInterfaceFont()
            )
            self.maxLabel.setY(-0.01)
            self.hpLabel = DirectLabel(
                parent=self.eyes,
                relief=None,
                pos=(-0.408, 0, 0.051),
                text='120',
                text_scale=0.45,
                text_font=ToontownGlobals.getInterfaceFont()
            )
            self.hpLabel.setY(-0.01)
            battleGui = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
            syncIconZ = 0.61323 if self.battleGui else -1.12486
            self.syncIcon = DirectLabel(
                parent=self.container, relief=None,
                image=battleGui.find('**/sync_icon'),
                pos=(1.2864, -0.01, syncIconZ),
                scale=0.69305,
            )
            self.syncIcon.setY(-0.01)
            self.syncIcon.hide()
            battleGui.removeNode()

            self.teeth = [
                self.tooth6,
                self.tooth5,
                self.tooth4,
                self.tooth3,
                self.tooth2,
                self.tooth1
            ]
            for tooth in self.teeth:
                tooth.setY(-0.01)

            self.fractions = [
                0.0,
                0.166666,
                0.333333,
                0.5,
                0.666666,
                0.833333
            ]

        if self.animated:
            self.rotateIval = Sequence(
                LerpHprInterval(self, 5, (0, 0, 4), (0, 0, -4), blendType='easeInOut'),
                LerpHprInterval(self, 5, (0, 0, -4), (0, 0, 4), blendType='easeInOut')
            )
            self.rotateIval.loop()
            self.warningFlash = Sequence(
                Sequence(
                    self.colorScaleInterval(0.1, colorScale=VBase4(1, 0, 0, 1)),
                    self.colorScaleInterval(0.3, colorScale=VBase4(1, 1, 1, 1))), Wait(1)
            )

    def destroy(self):
        if self.av:
            ToontownIntervals.cleanup(self.av.uniqueName('laffMeterBoing') + '-' + str(self.this))
            ToontownIntervals.cleanup(self.av.uniqueName('laffMeterBoing') + '-' + str(self.this) + '-play')
            self.cleanupModifierEvent()
        self.ignoreAll()
        self.cleanedUp = True
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
            del self.syncIcon

        DirectFrame.destroy(self)

        if self.rotateIval:
            self.rotateIval.finish()
            self.rotateIval = None

        if self.warningFlash:
            self.warningFlash.finish()
            self.warningFlash = None

    def setMeterColor(self, col=None):
        """Updates the color of the laff meter."""
        if col is None:
            self.color = self.style.getHeadColor()
        else:
            self.color = col
        self.container['image_color'] = self.color

    def setSpeciesOverride(self, species=None):
        """Updates the species override of the laff meter."""
        if species == self.speciesOverride:
            return

        self.speciesOverride = species
        self.adjustSpecies()

    def adjustSpecies(self):
        gui = loader.loadModel('phase_3/models/gui/laff_o_meter')
        if self.isToon:
            if self.speciesOverride:
                from toontown.toon import ToonDNA
                hType = ToonDNA.getSpeciesName(self.speciesOverride)
            else:
                hType = self.style.getType()
            try:
                headModel = gui.find('**/laffMeter_%s' % hType)
            except:
                raise Exception('unknown toon species: ', hType)

            self.container['image'] = headModel
            self.container['image_pos'] = species2ImagePos.get(hType, (0, 0, 0))
            self.container['image_scale'] = species2ImageScale.get(hType, 1.0)
            self.container['image_color'] = self.color
            self.resetFrameSize()

            posScale = species2PosScale.get(hType, defaultPosScale)
            self.openSmile.setPos(*posScale[:3])
            self.openSmile.setScale(*posScale[3:6])
            if self.speciesOverride == self.style.getType():
                self.speciesOverride = None
        gui.removeNode()

    def adjustTeeth(self):
        """
        if teeth are showing, decide which ones should be
        """
        if self.isToon:
            for i in range(len(self.teeth)):
                if self.hp > self.maxHp * self.fractions[i]:
                    self.teeth[i].show()
                else:
                    self.teeth[i].hide()

    def adjustText(self):
        """
        set the text for current HP and maxHp
        """
        if not self.isToon:
            return

        if self.maxLabel['text'] != str(self.maxHp) or self.hpLabel['text'] != str(self.hp):
            self.maxLabel['text'] = str(self.maxHp)
            self.hpLabel['text'] = str(self.hp)
            textScale = 0.4 if self.maxHp >= 200 else 0.45
            self.maxLabel['text_scale'] = textScale
            self.hpLabel['text_scale'] = textScale

    def animatedEffect(self, delta):
        # Note: the task name here must be unique to this avatar and to this laffmeter.
        # We'll use the python this pointer to differentiate multiple laffmeters watching the same toon
        # This happens in battle and on avatar detail panels
        if delta == 0 or self.av is None:
            return
        name = self.av.uniqueName('laffMeterBoing') + '-' + str(self.this)
        ToontownIntervals.cleanup(name)
        if delta > 0:
            # Laffmeter increase
            ToontownIntervals.start(ToontownIntervals.getPulseLargerIval(self.container, name))
            self.flashGreen()
        else:
            # Laffmeter decrease
            ToontownIntervals.start(ToontownIntervals.getPulseSmallerIval(self.container, name))
            self.flashRed()
            if self.av == base.localAvatar:
                base.playSfx(self.hit, looping=0, volume=0.8)

    def flashRed(self):
        self.cleanupFlash()
        self.setColorScale(1, 1, 1, 1)
        i = Sequence(
            self.colorScaleInterval(0.1, colorScale=VBase4(1, 0, 0, 1)),
            self.colorScaleInterval(0.3, colorScale=VBase4(1, 1, 1, 1))
        )
        self.flashInterval = i
        i.start()

    def flashGreen(self):
        self.cleanupFlash()
        if not self.isEmpty():
            self.setColorScale(1, 1, 1, 1)
            i = Sequence(
                self.colorScaleInterval(0.1, colorScale=VBase4(0, 1, 0, 1)),
                self.colorScaleInterval(0.3, colorScale=VBase4(1, 1, 1, 1))
            )
            self.flashInterval = i
            i.start()

    def cleanupFlash(self):
        if self.flashInterval:
            self.flashInterval.finish()
            self.flashInterval = None

    def adjustFace(self, hp, maxHp, quietly=0):
        """
        make sure the laff-o-meter face is in sync with the avatar state

        :type hp: int
        :type maxHp: int
        :type quietly: int | bool
        """
        if self.isToon and self.hp is not None:
            self.frown.hide()
            self.smile.hide()
            self.openSmile.hide()
            self.eyes.hide()
            for tooth in self.teeth:
                tooth.hide()

            delta = hp - self.hp
            self.hp = hp
            self.maxHp = maxHp

            if self.maxHp > 999:
                self.eyes['image_scale'] = (1.2, 1, 1.1)
                self.maxLabel['text_pos'] = (0.09, 0, 0)
                self.maxLabel['text_scale'] = 0.425
                self.hpLabel['text_pos'] = (-0.125, 0, 0)
                self.hpLabel['text_scale'] = 0.425
            else:
                self.eyes['image_scale'] = (1, 1, 1)
                self.maxLabel['text_pos'] = (0, 0, 0)
                self.maxLabel['text_scale'] = 0.45
                self.hpLabel['text_pos'] = (0, 0, 0)
                self.hpLabel['text_scale'] = 0.45

            if self.maxHp * self.fractions[1] > self.hp > 0 and self.animated:
                if self.warningFlash:
                    self.warningFlash.loop()
            else:
                if self.warningFlash:
                    self.warningFlash.finish()
            if self.hp < 1:
                self.frown.show()
                self.container['image_color'] = self.deathColor
            elif self.hp >= self.maxHp:
                self.smile.show()
                self.eyes.show()
                self.container['image_color'] = self.color
                if self.maxHp == 1:
                    self.smile.setR(180)
                    self.smile.setPos(0, -0.001, -.9)
                    self.smile.setScale(0.75, 1, 0.6)
                else:
                    self.smile.setR(0)
                    self.smile.setPos(0, -0.001, 0)
                    self.smile.setScale(1)
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

            # Show or hide the content sync icon.
            if self.av and (self.av.hasModifier(ModifierType.LaffContentSync) and not self.battleGui):
                self.syncIcon.show()
            else:
                self.syncIcon.hide()

    def start(self):
        """
        manage the GUI elements of the laff-o-meter
        """
        self.stopped = False
        if self.av:
            # Refresh the hp and max hp, in case they changed when we weren't managed.
            self.hp = self.av.getHp()
            self.maxHp = self.av.getMaxHp()
        if self.isToon:
            if not self.__obscured:
                self.show()
            self.adjustFace(self.hp, self.maxHp, 1)
            if self.av:
                self.accept(self.av.uniqueName('hpChange'), self.adjustFace)
                self.acceptModifierEvent()

    def update(self):
        if not self:
            return
        if self.cleanedUp:
            return
        if not self.av:
            return
        self.adjustFace(
            hp=self.av.getHp(),
            maxHp=self.av.getMaxHp(),
            quietly=1,
        )
        self.show()

    def stop(self):
        """
        unmanage the GUI elements of the laff-o-meter
        """
        self.stopped = True
        if self.isToon:
            self.hide()
            if self.av:
                self.ignore(self.av.uniqueName('hpChange'))
                self.cleanupModifierEvent()

    def setAvatar(self, av):
        """
        set an avatar structure for use by the auto-update system

        :param av: DistributedAvatar
        """
        # Get rid of any previous avatar hooks
        if self.av:
            self.ignore(self.av.uniqueName('hpChange'))
        self.av = av
        self.acceptEvents()
