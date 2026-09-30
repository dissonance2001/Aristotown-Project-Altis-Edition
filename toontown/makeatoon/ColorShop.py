from direct.fsm import StateData
from direct.gui.DirectGui import *
from panda3d.core import *

from toontown.makeatoon import ShuffleButton
from toontown.makeatoon.MakeAToonGlobals import *
from toontown.makeatoon.ColorGUI import ColorGUI
from toontown.toon import ToonDNA
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class ColorShop(StateData.StateData):
    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)
        self.toon = None
        self.colorAll = 1
        self.eyeMode = 'both'

    def getGenderColorList(self, dna):
        return ToonDNA.defaultColorList
        
    def getEyeColorList(self):
        return ToonDNA.eyeColorsList

    def enter(self, toon, shopsVisited = []):
        base.disableMouse()
        self.toon = toon
        self.dna = toon.getStyle()
        self.adjustFrames()
        colorList = self.getGenderColorList(self.dna)
        self.allParts = (
            TTLocalizer.ColorShopToon, TTLocalizer.ColorShopHead, TTLocalizer.ColorShopEar, TTLocalizer.ColorShopBody, TTLocalizer.ColorShopLegs)

        if not hasattr(self, 'headChoice'):
            #All these try excepts aren't the most elegant thing, but they do the trick.  They exist because going into restoratin station with a custom color
            #causes an issue when looking up that custom color in the colorList.  If that issue occurs it just sets the choice to 1.
            #This is done instead of 0 because both left and right buttons are lit up upon entering page and, 
            #while pressing the wrong arrow on a 0 index won't crash anything, it seems more appropriate and looks better when applied in game.
            try:
                self.headChoice = colorList.index(self.dna.headColor)
            except:
                self.headChoice = 1
            try:
                self.earChoice = colorList.index(self.dna.earColor)
            except:
                self.earChoice = 1
            self.leftEyeChoice, self.rightEyeChoice = ToonDNA.decodeEyeColors(self.dna.eyeColor)
            self.eyeChoice = self.leftEyeChoice
            try:
                self.armChoice = colorList.index(self.dna.armColor)
            except:
                self.armChoice = 1
            try:
                self.legChoice = colorList.index(self.dna.legColor)
            except:
                self.legChoice = 1
            self.partChoice = 0

        self.startColor = 0
        self.acceptOnce('last', self.__handleBackward)
        self.acceptOnce('next', self.__handleForward)
        choicePool = [self.getGenderColorList(self.dna), self.getGenderColorList(self.dna), self.getGenderColorList(self.dna), self.getGenderColorList(self.dna)]
        self.shuffleButton.setChoicePool(choicePool)
        self.accept(self.shuffleFetchMsg, self.changeColor)
        self.acceptOnce('MAT-newToonCreated', self.shuffleButton.cleanHistory)
        self.accept("colorPicked", self.__pickColor)

    def acceptNextAgain(self):
        self.acceptOnce('next', self.__handleForward)

    def adjustFrames(self):
        if self.dna.getAnimal() in self.dna.AnimalsWithColoredEars:
            self.earFrame.show()
            self.bodyFrame.show()
            self.earFrame.setPos(0, 0, -0.4)
            self.bodyFrame.setPos(0, 0, -.6)
            self.headFrame.setPos(0, 0, -0.05)
            self.eyeFrame.setPos(0, 0, -0.2)
            self.toonFrame.setPos(0, 0, 0.2927)
            self.legsFrame.setPos(0, 0, -0.8)
        elif self.dna.getAnimal() == 'kiwi':
            self.earFrame.hide()
            self.bodyFrame.hide()
            self.headFrame.setPos(0, 0, -0.43)
            self.eyeFrame.setPos(0, 0, -0.2)
            self.toonFrame.setPos(0, 0, -.2)
            self.legsFrame.setPos(0, 0, -0.8)
        else:
            self.earFrame.hide()
            self.bodyFrame.show()
            self.earFrame.setPos(0, 0, -0.4)
            self.bodyFrame.setPos(0, 0, -.6)
            self.headFrame.setPos(0, 0, -0.2)
            self.eyeFrame.setPos(0, 0, -0.2)
            self.toonFrame.setPos(0, 0, 0.1)
            self.legsFrame.setPos(0, 0, -0.8)

    def showButtons(self):
        self.parentFrame.show()

    def hideButtons(self):
        self.parentFrame.hide()
        self.pickerFrame.hide()

    def exit(self):
        self.ignore('last')
        self.ignore('next')
        self.ignore('enter')
        self.ignore(self.shuffleFetchMsg)
        try:
            del self.toon
        except:
            print('ColorShop: toon not found')

        self.hideButtons()

    def load(self):
        self.gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        guiRArrowUp = self.gui.find('**/tt_t_gui_mat_arrowUp')
        guiRArrowRollover = self.gui.find('**/tt_t_gui_mat_arrowUp')
        guiRArrowDown = self.gui.find('**/tt_t_gui_mat_arrowDown')
        guiRArrowDisabled = self.gui.find('**/tt_t_gui_mat_arrowDisabled')
        shuffleFrame = self.gui.find('**/tt_t_gui_mat_shuffleFrame')
        shuffleUp = self.gui.find('**/tt_t_gui_mat_shuffleUp')
        shuffleDown = self.gui.find('**/tt_t_gui_mat_shuffleDown')
        shuffleImage = (
            self.gui.find('**/tt_t_gui_mat_shuffleArrowUp'), self.gui.find('**/tt_t_gui_mat_shuffleArrowDown'),
            self.gui.find('**/tt_t_gui_mat_shuffleArrowUp'), self.gui.find('**/tt_t_gui_mat_shuffleArrowDisabled'))
        self.parentFrame = self.getNewFrame()

        self.pickerFrame = self.getNewFrame()
        self.pickerFrame.setScale(0.75)
        self.pickerFrame.setPos(-0.36, 0, -0.7)

        self.colorPicker = ColorGUI(parent = self.pickerFrame)
        self.colorPicker.setScale(0.4)

        self.toonFrame = DirectFrame(parent = self.parentFrame, image = shuffleFrame,
                                     image_scale = halfButtonInvertScale, relief = None, pos = (0, 0, -0.073),
                                     hpr = (0, 0, 0), scale = 1.3, frameColor = (1, 1, 1, 1),
                                     text = TTLocalizer.ColorShopToon, text_scale = TTLocalizer.CStoonFrame,
                                     text_pos = (-0.001, -0.015), text_fg = (1, 1, 1, 1))
        self.allLButton = DirectButton(parent = self.toonFrame, relief = None, image = shuffleImage,
                                       image_scale = halfButtonScale, image1_scale = halfButtonHoverScale,
                                       image2_scale = halfButtonHoverScale, pos = (-0.2, 0, 0),
                                       command = self.__swapAllColor, extraArgs = [-1])
        self.allRButton = DirectButton(parent = self.toonFrame, relief = None, image = shuffleImage,
                                       image_scale = halfButtonInvertScale, image1_scale = halfButtonInvertHoverScale,
                                       image2_scale = halfButtonInvertHoverScale, pos = (0.2, 0, 0),
                                       command = self.__swapAllColor, extraArgs = [1])
        self.headFrame = DirectFrame(parent = self.parentFrame, image = shuffleFrame,
                                     image_scale = halfButtonInvertScale, relief = None, pos = (0, 0, -0.3),
                                     hpr = (0, 0, 2), scale = 0.9, frameColor = (1, 1, 1, 1),
                                     text = TTLocalizer.ColorShopHead, text_scale = 0.0625, text_pos = (-0.001, -0.015),
                                     text_fg = (1, 1, 1, 1))
        self.headLButton = DirectButton(parent = self.headFrame, relief = None, image = shuffleImage,
                                        image_scale = halfButtonScale, image1_scale = halfButtonHoverScale,
                                        image2_scale = halfButtonHoverScale, pos = (-0.2, 0, 0),
                                        command = self.__swapHeadColor, extraArgs = [-1])
        self.headRButton = DirectButton(parent = self.headFrame, relief = None, image = shuffleImage,
                                        image_scale = halfButtonInvertScale, image1_scale = halfButtonInvertHoverScale,
                                        image2_scale = halfButtonInvertHoverScale, pos = (0.2, 0, 0),
                                        command = self.__swapHeadColor, extraArgs = [1])
        self.eyeFrame = DirectFrame(parent = self.headFrame, image = shuffleFrame,
                                     image_scale = halfButtonScale, relief = None, pos = (0, 0, -0.125),
                                     hpr = (0, 0, 2), scale = 0.9, frameColor = (1, 1, 1, 1),
                                     text = TTLocalizer.ColorShopEye, text_scale = 0.0625, text_pos = (-0.001, -0.015),
                                     text_fg = (1, 1, 1, 1))
        self.eyeLButton = DirectButton(parent = self.eyeFrame, relief = None, image = shuffleImage,
                                        image_scale = halfButtonScale, image1_scale = halfButtonHoverScale,
                                        image2_scale = halfButtonHoverScale, pos = (-0.2, 0, 0),
                                        command = self.__swapEyeColor, extraArgs = [-1])
        self.eyeRButton = DirectButton(parent = self.eyeFrame, relief = None, image = shuffleImage,
                                        image_scale = halfButtonInvertScale, image1_scale = halfButtonInvertHoverScale,
                                        image2_scale = halfButtonInvertHoverScale, pos = (0.2, 0, 0),
                                        command = self.__swapEyeColor, extraArgs = [1])
        self.eyeModeFrame = DirectFrame(parent = self.headFrame, image = shuffleFrame,
                                          image_scale = halfButtonInvertScale, relief = None, pos = (-0.48, 0, -0.125),
                                          hpr = (0, 0, 2), scale = 0.9, frameColor = (1, 1, 1, 1),
                                          text = '', text_scale = 0.0625, text_pos = (-0.001, -0.015),
                                          text_fg = (1, 1, 1, 1))
        self.eyeModeLButton = DirectButton(parent = self.eyeModeFrame, relief = None, image = shuffleImage,
                                           image_scale = halfButtonScale, image1_scale = halfButtonHoverScale,
                                           image2_scale = halfButtonHoverScale, pos = (-0.2, 0, 0),
                                           command = self.__cycleEyeMode, extraArgs = [-1])
        self.eyeModeRButton = DirectButton(parent = self.eyeModeFrame, relief = None, image = shuffleImage,
                                           image_scale = halfButtonInvertScale, image1_scale = halfButtonInvertHoverScale,
                                           image2_scale = halfButtonInvertHoverScale, pos = (0.2, 0, 0),
                                           command = self.__cycleEyeMode, extraArgs = [1])
        self.eyeModeButton = DirectButton(parent = self.eyeModeFrame, relief = None,
                                          frameColor = (0, 0, 0, 0),
                                          text = 'Both Eyes', text_scale = 0.05,
                                          text_fg = (1, 1, 1, 1), text_shadow = (0, 0, 0, 1),
                                          text_font = ToontownGlobals.getInterfaceFont(),
                                          frameSize = (-0.14, 0.14, -0.06, 0.06),
                                          pos = (0, 0, 0),
                                          command = self.__cycleEyeMode, extraArgs = [1])
        self.earFrame = DirectFrame(parent = self.parentFrame, image = shuffleFrame,
                                     image_scale = halfButtonInvertScale, relief = None, pos = (0, 0, -0.3),
                                     hpr = (0, 0, 2), scale = 0.9, frameColor = (1, 1, 1, 1),
                                     text = TTLocalizer.ColorShopEar, text_scale = 0.0625, text_pos = (-0.001, -0.015),
                                     text_fg = (1, 1, 1, 1))
        self.earLButton = DirectButton(parent = self.earFrame, relief = None, image = shuffleImage,
                                        image_scale = halfButtonScale, image1_scale = halfButtonHoverScale,
                                        image2_scale = halfButtonHoverScale, pos = (-0.2, 0, 0),
                                        command = self.__swapEarColor, extraArgs = [-1])
        self.earRButton = DirectButton(parent = self.earFrame, relief = None, image = shuffleImage,
                                        image_scale = halfButtonInvertScale, image1_scale = halfButtonInvertHoverScale,
                                        image2_scale = halfButtonInvertHoverScale, pos = (0.2, 0, 0),
                                        command = self.__swapEarColor, extraArgs = [1])
        self.bodyFrame = DirectFrame(parent = self.parentFrame, image = shuffleFrame, image_scale = halfButtonScale,
                                     relief = None, pos = (0, 0, -0.5), hpr = (0, 0, -2), scale = 0.9,
                                     frameColor = (1, 1, 1, 1), text = TTLocalizer.ColorShopBody, text_scale = 0.0625,
                                     text_pos = (-0.001, -0.015), text_fg = (1, 1, 1, 1))
        self.armLButton = DirectButton(parent = self.bodyFrame, relief = None, image = shuffleImage,
                                       image_scale = halfButtonScale, image1_scale = halfButtonHoverScale,
                                       image2_scale = halfButtonHoverScale, pos = (-0.2, 0, 0),
                                       command = self.__swapArmColor, extraArgs = [-1])
        self.armRButton = DirectButton(parent = self.bodyFrame, relief = None, image = shuffleImage,
                                       image_scale = halfButtonInvertScale, image1_scale = halfButtonInvertHoverScale,
                                       image2_scale = halfButtonInvertHoverScale, pos = (0.2, 0, 0),
                                       command = self.__swapArmColor, extraArgs = [1])
        self.legsFrame = DirectFrame(parent = self.parentFrame, image = shuffleFrame,
                                     image_scale = halfButtonInvertScale, relief = None, pos = (0, 0, -0.7),
                                     hpr = (0, 0, 3), scale = 0.9, frameColor = (1, 1, 1, 1),
                                     text = TTLocalizer.ColorShopLegs, text_scale = 0.0625, text_pos = (-0.001, -0.015),
                                     text_fg = (1, 1, 1, 1))
        self.legLButton = DirectButton(parent = self.legsFrame, relief = None, image = shuffleImage,
                                       image_scale = halfButtonScale, image1_scale = halfButtonHoverScale,
                                       image2_scale = halfButtonHoverScale, pos = (-0.2, 0, 0),
                                       command = self.__swapLegColor, extraArgs = [-1])
        self.legRButton = DirectButton(parent = self.legsFrame, relief = None, image = shuffleImage,
                                       image_scale = halfButtonInvertScale, image1_scale = halfButtonInvertHoverScale,
                                       image2_scale = halfButtonInvertHoverScale, pos = (0.2, 0, 0),
                                       command = self.__swapLegColor, extraArgs = [1])
        self.pickerButton = DirectButton(parent = self.parentFrame, relief = None,
                                         image = (shuffleUp, shuffleDown, shuffleUp), image_scale = (-0.8, 0.6, 0.6),
                                         image1_scale = (-0.83, 0.6, 0.6), image2_scale = (-0.83, 0.6, 0.6),
                                         text = TTLocalizer.ColorShopPicker,
                                         text_font = ToontownGlobals.getInterfaceFont(),
                                         text_scale = 0.06, text_pos = (0, -0.02),
                                         text_fg = (1, 1, 1, 1), text_shadow = (0, 0, 0, 1), pos = (0, 0, -1.15),
                                         command = self.popupPickerMenu)
        self.basicButton = DirectButton(parent = self.pickerFrame, relief = None,
                                        image = (shuffleUp, shuffleDown, shuffleUp), image_scale = (-0.8, 0.6, 0.6),
                                        image1_scale = (-0.83, 0.6, 0.6), image2_scale = (-0.83, 0.6, 0.6),
                                        text = TTLocalizer.ColorShopBasic, scale = 1.4,
                                        text_font = ToontownGlobals.getInterfaceFont(),
                                        text_scale = 0.06, text_pos = (0, -0.02),
                                        text_fg = (1, 1, 1, 1), text_shadow = (0, 0, 0, 1), pos = (0, 0, -1.2),
                                        command = self.popupBasicMenu)
        self.rgbDisplay = OnscreenText(parent = self.pickerFrame, pos = (-.8, .5), scale = 0.1, style = 3,
                                       align = TextNode.ALeft)
        self.partsFrame = DirectFrame(parent = self.pickerFrame, image = shuffleFrame,
                                      image_scale = halfButtonInvertScale, relief = None, pos = (0, 0, -.5),
                                      hpr = (0, 0, -2), scale = 0.9, frameColor = (1, 1, 1, 1),
                                      text = TTLocalizer.ColorShopToon, text_scale = 0.0625,
                                      text_pos = (-0.001, -0.015), text_fg = (1, 1, 1, 1))
        self.partLButton = DirectButton(parent = self.partsFrame, relief = None, image = shuffleImage,
                                        image_scale = halfButtonScale, image1_scale = halfButtonHoverScale,
                                        image2_scale = halfButtonHoverScale, pos = (-0.2, 0, 0), state = DGG.DISABLED,
                                        command = self.__swapPart, extraArgs = [-1])
        self.partRButton = DirectButton(parent = self.partsFrame, relief = None, image = shuffleImage,
                                        image_scale = halfButtonInvertScale, image1_scale = halfButtonInvertHoverScale,
                                        image2_scale = halfButtonInvertHoverScale, pos = (0.2, 0, 0),
                                        command = self.__swapPart, extraArgs = [1])
        self.parentFrame.hide()
        self.pickerFrame.hide()
        self.shuffleFetchMsg = 'ColorShopShuffle'
        self.shuffleButton = ShuffleButton.ShuffleButton(self, self.shuffleFetchMsg)

    def unload(self):
        self.gui.removeNode()
        del self.gui
        self.parentFrame.destroy()
        self.pickerFrame.destroy()
        self.toonFrame.destroy()
        self.headFrame.destroy()
        self.eyeModeFrame.destroy()
        self.earFrame.destroy()
        self.bodyFrame.destroy()
        self.legsFrame.destroy()
        self.headLButton.destroy()
        self.headRButton.destroy()
        self.armLButton.destroy()
        self.armRButton.destroy()
        self.legLButton.destroy()
        self.legRButton.destroy()
        self.allLButton.destroy()
        self.allRButton.destroy()
        self.pickerButton.destroy()
        self.basicButton.destroy()
        self.rgbDisplay.destroy()
        self.partsFrame.destroy()
        self.partLButton.destroy()
        self.partRButton.destroy()
        del self.parentFrame
        del self.pickerFrame
        del self.toonFrame
        del self.headFrame
        del self.earFrame
        del self.bodyFrame
        del self.legsFrame
        del self.headLButton
        del self.headRButton
        del self.armLButton
        del self.armRButton
        del self.legLButton
        del self.legRButton
        del self.allLButton
        del self.allRButton
        del self.pickerButton
        del self.basicButton
        del self.rgbDisplay
        del self.partsFrame
        del self.partLButton
        del self.partRButton
        self.shuffleButton.unload()
        self.ignore('colorPicked')

    def getNewFrame(self):
        frame = DirectFrame(relief = DGG.RAISED, frameColor = (1, 0, 0, 0))
        frame.setPos(-0.36, 0, -0.5)
        frame.reparentTo(base.a2dTopRight)
        return frame

    def popupPickerMenu(self):
        self.parentFrame.hide()
        self.pickerFrame.show()

    def popupBasicMenu(self):
        self.parentFrame.show()
        self.pickerFrame.hide()

    def __pickColor(self):
        rgb = self.colorPicker.rgb

        self.rgbDisplay['text'] = ("\1TextRed\1R %s\2\n\1TextGreen\1G %s\2\n\1TextBlue\1B %s\2" % (
            int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)))

        rgb = tuple([float('%.2f' % x) for x in rgb])

        if self.partChoice in (0, 1):
            self.dna.headColor = rgb
        if self.partChoice in (0, 2):
            self.dna.earColor = rgb
        if self.partChoice in (0, 3):
            self.dna.armColor = rgb
        if self.partChoice in (0, 4):
            self.dna.legColor = rgb

        self.toon.swapToonColor(self.dna)

    def __swapPart(self, offset):
        self.partChoice += offset
        if self.dna.getAnimal() not in self.dna.AnimalsWithColoredEars and self.partChoice == 2: # Checks if toon has colorable ears.
            self.partChoice += offset # Offset it by one more.
        if self.dna.getAnimal() == 'kiwi' and self.partChoice == 3: # This freak doesn't have arms, GET HIM!
            self.partChoice += offset
            if self.partChoice == 2: # Thought you could pull a fast one on me? HA! You still don't have ears!
                self.partChoice += offset
        self.partLButton['state'] = DGG.DISABLED if self.partChoice <= 0 else DGG.NORMAL
        self.partRButton['state'] = DGG.DISABLED if self.partChoice >= len(self.allParts) - 1 else DGG.NORMAL
        self.partsFrame['text'] = self.allParts[self.partChoice]

    def __swapAllColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        choice = (self.headChoice + offset) % length
        self.__updateScrollButtons(choice, length, self.allLButton, self.allRButton)
        self.__swapHeadColor(offset)
        try:
            oldEarColorIndex = colorList.index(self.toon.style.earColor)
            oldArmColorIndex = colorList.index(self.toon.style.armColor)
            oldLegColorIndex = colorList.index(self.toon.style.legColor)
            self.__swapEarColor(choice - oldEarColorIndex)
            self.__swapArmColor(choice - oldArmColorIndex)
            self.__swapLegColor(choice - oldLegColorIndex)
        except:
            self.__swapEarColor(offset)
            self.__swapArmColor(offset)
            self.__swapLegColor(offset)

    def __swapHeadColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        self.headChoice = (self.headChoice + offset) % length
        self.__updateScrollButtons(self.headChoice, length, self.headLButton, self.headRButton)
        newColor = colorList[self.headChoice]
        self.dna.headColor = newColor
        self.toon.swapToonColor(self.dna)
        
    def __swapEarColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        self.earChoice = (self.earChoice + offset) % length
        self.__updateScrollButtons(self.earChoice, length, self.earLButton, self.earRButton)
        newColor = colorList[self.earChoice]
        self.dna.earColor = newColor
        self.toon.swapToonColor(self.dna)
        
    def __cycleEyeMode(self, offset = 1):
        modes = ('both', 'left', 'right')
        index = modes.index(self.eyeMode)
        self.eyeMode = modes[(index + offset) % len(modes)]
        if self.eyeMode == 'left':
            self.eyeModeButton['text'] = 'Left Eye'
            self.eyeChoice = self.leftEyeChoice
        elif self.eyeMode == 'right':
            self.eyeModeButton['text'] = 'Right Eye'
            self.eyeChoice = self.rightEyeChoice
        else:
            self.eyeModeButton['text'] = 'Both Eyes'
            self.eyeChoice = self.leftEyeChoice
        self.__updateScrollButtons(self.eyeChoice, len(self.getEyeColorList()), self.eyeLButton, self.eyeRButton)

    def __swapEyeColor(self, offset):
        colorList = self.getEyeColorList()
        length = len(colorList)
        self.eyeChoice = (self.eyeChoice + offset) % length
        if self.eyeMode == 'left':
            self.leftEyeChoice = self.eyeChoice
        elif self.eyeMode == 'right':
            self.rightEyeChoice = self.eyeChoice
        else:
            self.leftEyeChoice = self.eyeChoice
            self.rightEyeChoice = self.eyeChoice
        self.__updateScrollButtons(self.eyeChoice, length, self.eyeLButton, self.eyeRButton)
        self.dna.eyeColor = ToonDNA.encodeEyeColors(self.leftEyeChoice, self.rightEyeChoice)
        self.toon.swapToonColor(self.dna)

    def __swapArmColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        self.armChoice = (self.armChoice + offset) % length
        self.__updateScrollButtons(self.armChoice, length, self.armLButton, self.armRButton)
        newColor = colorList[self.armChoice]
        self.dna.armColor = newColor
        self.toon.swapToonColor(self.dna)

    def __swapLegColor(self, offset):
        colorList = self.getGenderColorList(self.dna)
        length = len(colorList)
        self.legChoice = (self.legChoice + offset) % length
        self.__updateScrollButtons(self.legChoice, length, self.legLButton, self.legRButton)
        newColor = colorList[self.legChoice]
        self.dna.legColor = newColor
        self.toon.swapToonColor(self.dna)

    def __updateScrollButtons(self, choice, length, lButton, rButton):
        if choice == (self.startColor - 1) % length:
            rButton['state'] = DGG.DISABLED
        else:
            rButton['state'] = DGG.NORMAL
        if choice == self.startColor % length:
            lButton['state'] = DGG.DISABLED
        else:
            lButton['state'] = DGG.NORMAL

    def __handleForward(self):
        self.doneStatus = 'next'
        messenger.send(self.doneEvent)

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)

    def indexOf(self, itemList, item, default):
        try:
            return itemList.index(item)
        except:
            return default

    def changeColor(self):
        self.notify.debug('Entering changeColor')
        colorList = self.getGenderColorList(self.dna)
        newChoice = self.shuffleButton.getCurrChoice()
        indexedColor = 0
        for color in newChoice:
            if color in colorList and type(color) is int:
                indexedColor = 1
                break
        if indexedColor:
            newHeadColorIndex = colorList.index(newChoice[0])
            newEarColorIndex = colorList.index(newChoice[1])
            newArmColorIndex = colorList.index(newChoice[2])
            newLegColorIndex = colorList.index(newChoice[3])
            self.__swapHeadColor(newHeadColorIndex - self.headChoice)
            if self.colorAll:
                self.__swapArmColor(newHeadColorIndex - self.armChoice)
                self.__swapEarColor(newHeadColorIndex - self.earChoice)
                self.__swapLegColor(newHeadColorIndex - self.legChoice)
            else:
                self.__swapArmColor(newArmColorIndex - self.armChoice)
                self.__swapEarColor(newEarColorIndex - self.earChoice)
                self.__swapLegColor(newLegColorIndex - self.legChoice)
        else:
            self.dna.headColor = newChoice[0]
            self.dna.earColor = newChoice[1]
            self.dna.armColor = newChoice[2]
            self.dna.legColor = newChoice[3]
            self.toon.swapToonColor(self.dna)
            return

    def getCurrToonSetting(self):
        return [self.dna.headColor, self.dna.earColor, self.dna.armColor, self.dna.legColor]
