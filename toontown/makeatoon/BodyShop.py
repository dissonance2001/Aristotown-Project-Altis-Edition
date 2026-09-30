from panda3d.core import *
from toontown.toon import ToonDNA
from direct.fsm import StateData
from direct.gui.DirectGui import *
from toontown.makeatoon.MakeAToonGlobals import *
import random
from datetime import datetime, timedelta
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.makeatoon import ShuffleButton
from toontown.menu.MainMenuGui import MainMenuButton
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class BodyShop(StateData.StateData):
    def __init__(self, mat, doneEvent, restoration=False):
        StateData.StateData.__init__(self, doneEvent)
        self.mat = mat
        self.toon = None
        self.torsoChoice = 0
        self.legChoice = 0
        self.headChoice = 0
        self.speciesChoice = 0
        self.eyelashChoice = 0
        self.speciesButtons = []
        self.wantTurkey = False
        self.__restoration = True if restoration else False

    def enter(self, toon, shopsVisited=[]):
        base.disableMouse()
        self.toon = toon
        self.dna = self.toon.getStyle()
        gender = self.toon.style.getGender()
        self.speciesStart = self.getSpeciesStart()
        self.speciesChoice = self.speciesStart
        self.headStart = 0
        self.headChoice = ToonDNA.toonHeadTypes.index(self.dna.head) - ToonDNA.getHeadStartIndex(self.species)
        self.torsoStart = 0
        self.torsoChoice = ToonDNA.toonTorsoTypes.index(self.dna.torso) % 3
        self.legStart = 0
        self.legChoice = ToonDNA.toonLegTypes.index(self.dna.legs)
        self.eyelashStart = 0
        self.eyelashChoice = ToonDNA.toonEyelashTypes.index(self.dna.eyelashes)

        if CLOTHESSHOP in shopsVisited:
            self.clothesPicked = 1
        else:
            self.clothesPicked = 0
        self.clothesPicked = 1
        if ToonDNA.getBottomType(gender, self.dna.botTex) == ToonDNA.SHORTS:
            torsoPool = ToonDNA.toonTorsoTypes[:3]
        else:
            torsoPool = ToonDNA.toonTorsoTypes[3:6]
        self.__setSpecies(self.speciesStart)
        self.__swapHead(0)
        self.__swapTorso(0)
        self.__swapLegs(0)
        self.__swapEyelashes(0)

        choicePool = [ToonDNA.toonHeadTypes, torsoPool, ToonDNA.toonLegTypes, ToonDNA.toonEyelashTypes]
        self.shuffleButton.setChoicePool(choicePool)
        self.accept(self.shuffleFetchMsg, self.changeBody)
        self.acceptOnce('last', self.__handleBackward)
        self.accept('next', self.__handleForward)
        self.acceptOnce('MAT-newToonCreated', self.shuffleButton.cleanHistory)

    def getSpeciesStart(self):
        for species in ToonDNA.toonSpeciesTypes:
            if species == self.dna.head[0]:
                self.species = species
                return ToonDNA.toonSpeciesTypes.index(species)

    def showButtons(self):
        self.parentFrame.show()
        for btn in self.speciesButtons:
            btn['image_color'] = (self.toon.style.getHeadColor())
            btn['image3_color'] = (Vec4(self.toon.style.getHeadColor()) - Vec4(0, 0, 0, .4))

            hType = ToonDNA.getSpeciesName(ToonDNA.toonSpeciesTypes[btn['extraArgs'][0]])

            # See if turkey is allowed
            if hType == 'turkey':
                # allow turkey if either holiday or old head was turkey (in restoration mode)
                if (self.__restoration and base.localAvatar.style.getAnimal() == 'turkey') or \
                    (base.cr.newsManager and base.cr.newsManager.isHolidayRunning(ToontownGlobals.APRIL_FOOLS_COSTUMES)):
                    # Altis has no Thanksgiving holiday defined (unlike Clash's THANKSGIVING),
                    # so turkey is only offered during restoration or April Fools.
                    self.wantTurkey = True
                    btn.show()
                else:
                    btn.hide()
            else:
                btn.show()

    def hideButtons(self):
        self.parentFrame.hide()
        for btn in self.speciesButtons:
            btn.hide()

    def exit(self):
        try:
            del self.toon
        except Exception:
            self.notify.warning('BodyShop: toon not found')

        self.hideButtons()
        self.ignore('last')
        self.ignore('next')
        self.ignore('enter')
        self.ignore(self.shuffleFetchMsg)

    def load(self):
        self.gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        shuffleFrame = self.gui.find('**/tt_t_gui_mat_shuffleFrame')
        shuffleArrowUp = self.gui.find('**/tt_t_gui_mat_shuffleArrowUp')
        shuffleArrowDown = self.gui.find('**/tt_t_gui_mat_shuffleArrowDown')
        shuffleArrowRollover = self.gui.find('**/tt_t_gui_mat_shuffleArrowUp')
        shuffleArrowDisabled = self.gui.find('**/tt_t_gui_mat_shuffleArrowDisabled')
        self.parentFrame = DirectFrame(relief=DGG.RAISED, pos=(0.98, 0, 0.416), frameColor=(1, 0, 0, 0))
        self.parentFrame.setPos(-0.36, 0, -0.5)
        self.parentFrame.reparentTo(base.a2dTopRight)
        self.createSpeciesButtons()
        self.headFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonScale, relief=None, pos=(0, 0, -0.1), hpr=(0, 0, 2), scale=0.9, frameColor=(1, 1, 1, 1), text=TTLocalizer.BodyShopHead, text_scale=0.0625, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
        self.headLButton = DirectButton(parent=self.headFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.__swapHead, extraArgs=[-1])
        self.headRButton = DirectButton(parent=self.headFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.__swapHead, extraArgs=[1])

        self.eyelashFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonInvertScale, relief=None, pos=(0, 0, -0.3), hpr=(0, 0, -3), scale=0.9, frameColor=(1, 1, 1, 1), text=TTLocalizer.BodyShopEyelashes, text_scale=0.0625, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
        self.eyelashLButton = DirectButton(parent=self.eyelashFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.__swapEyelashes, extraArgs=[-1])
        self.eyelashRButton = DirectButton(parent=self.eyelashFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.__swapEyelashes, extraArgs=[1])

        self.bodyFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonScale, relief=None, pos=(0, 0, -0.5), hpr=(0, 0, -2), scale=0.9, frameColor=(1, 1, 1, 1), text=TTLocalizer.BodyShopBody, text_scale=0.0625, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
        self.torsoLButton = DirectButton(parent=self.bodyFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.__swapTorso, extraArgs=[-1])
        self.torsoRButton = DirectButton(parent=self.bodyFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.__swapTorso, extraArgs=[1])

        self.legsFrame = DirectFrame(parent=self.parentFrame, image=shuffleFrame, image_scale=halfButtonInvertScale, relief=None, pos=(0, 0, -0.7), hpr=(0, 0, 3), scale=0.9, frameColor=(1, 1, 1, 1), text=TTLocalizer.BodyShopLegs, text_scale=0.0625, text_pos=(-0.001, -0.015), text_fg=(1, 1, 1, 1))
        self.legLButton = DirectButton(parent=self.legsFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=halfButtonScale, image1_scale=halfButtonHoverScale, image2_scale=halfButtonHoverScale, pos=(-0.2, 0, 0), command=self.__swapLegs, extraArgs=[-1])
        self.legRButton = DirectButton(parent=self.legsFrame, relief=None, image=(shuffleArrowUp,
         shuffleArrowDown,
         shuffleArrowRollover,
         shuffleArrowDisabled), image_scale=halfButtonInvertScale, image1_scale=halfButtonInvertHoverScale, image2_scale=halfButtonInvertHoverScale, pos=(0.2, 0, 0), command=self.__swapLegs, extraArgs=[1])


        self.parentFrame.hide()
        self.shuffleFetchMsg = 'BodyShopShuffle'
        self.shuffleButton = ShuffleButton.ShuffleButton(self, self.shuffleFetchMsg)
        return

    def unload(self):
        self.gui.removeNode()
        del self.gui
        self.parentFrame.destroy()
        self.headFrame.destroy()
        self.bodyFrame.destroy()
        self.legsFrame.destroy()
        self.eyelashFrame.destroy()
        self.headLButton.destroy()
        self.headRButton.destroy()
        self.torsoLButton.destroy()
        self.torsoRButton.destroy()
        self.legLButton.destroy()
        self.legRButton.destroy()
        self.eyelashLButton.destroy()
        self.eyelashRButton.destroy()
        del self.parentFrame
        del self.headFrame
        del self.bodyFrame
        del self.legsFrame
        del self.eyelashFrame
        del self.headLButton
        del self.headRButton
        del self.torsoLButton
        del self.torsoRButton
        del self.legLButton
        del self.legRButton
        del self.eyelashLButton
        del self.eyelashRButton
        for button in self.speciesButtons:
            button.destroy()
            del button
        self.speciesButtons = []
        self.shuffleButton.unload()
        self.ignore('MAT-newToonCreated')

    def __swapTorso(self, offset):
        gender = self.toon.style.getGender()
        if not self.clothesPicked:
            length = len(ToonDNA.toonTorsoTypes[6:])
            torsoOffset = 6
        elif gender == 'm':
            length = len(ToonDNA.toonTorsoTypes[:3])
            torsoOffset = 0
            if self.toon.style.topTex not in (ToonDNA.MakeAToonBoyShirts if gender == 'm' else ToonDNA.MakeAToonGirlShirts) and not self.__restoration: #Don't want to randomize new shirt if here for restoration
                randomShirt = ToonDNA.getRandomTop(gender, ToonDNA.MAKE_A_TOON)
                shirtTex, shirtColor, sleeveTex, sleeveColor = randomShirt
                self.toon.style.topTex = shirtTex
                self.toon.style.topTexColor = shirtColor
                self.toon.style.sleeveTex = sleeveTex
                self.toon.style.sleeveTexColor = sleeveColor
            if self.toon.style.botTex not in (ToonDNA.MakeAToonBoyBottoms if gender == 'm' else ToonDNA.MakeAToonGirlBottoms) and not self.__restoration:
                botTex, botTexColor = ToonDNA.getRandomBottom(gender, ToonDNA.MAKE_A_TOON)
                self.toon.style.botTex = botTex
                self.toon.style.botTexColor = botTexColor
        else:
            length = len(ToonDNA.toonTorsoTypes[3:6])
            if self.toon.style.torso[1] == 'd':
                torsoOffset = 3
            else:
                torsoOffset = 0
            if self.toon.style.topTex not in (ToonDNA.MakeAToonBoyShirts if gender == 'm' else ToonDNA.MakeAToonGirlShirts) and not self.__restoration:
                randomShirt = ToonDNA.getRandomTop(gender, ToonDNA.MAKE_A_TOON)
                shirtTex, shirtColor, sleeveTex, sleeveColor = randomShirt
                self.toon.style.topTex = shirtTex
                self.toon.style.topTexColor = shirtColor
                self.toon.style.sleeveTex = sleeveTex
                self.toon.style.sleeveTexColor = sleeveColor
            if self.toon.style.botTex not in (ToonDNA.MakeAToonBoyBottoms if gender == 'm' else ToonDNA.MakeAToonGirlBottoms) and not self.__restoration:
                if self.toon.style.torso[1] == 'd':
                    botTex, botTexColor = ToonDNA.getRandomBottom(gender, ToonDNA.MAKE_A_TOON, girlBottomType=ToonDNA.SKIRT)
                    self.toon.style.botTex = botTex
                    self.toon.style.botTexColor = botTexColor
                    torsoOffset = 3
                else:
                    botTex, botTexColor = ToonDNA.getRandomBottom(gender, ToonDNA.MAKE_A_TOON, girlBottomType=ToonDNA.SHORTS)
                    self.toon.style.botTex = botTex
                    self.toon.style.botTexColor = botTexColor
                    torsoOffset = 0
        self.torsoChoice = (self.torsoChoice + offset) % length
        self.__updateScrollButtons(self.torsoChoice, length, self.torsoStart, self.torsoLButton, self.torsoRButton)
        torso = ToonDNA.toonTorsoTypes[torsoOffset + self.torsoChoice]
        self.dna.torso = torso
        self.toon.swapToonTorso(torso)
        self.toon.loop('neutral', 0)
        self.toon.swapToonColor(self.dna)
        self.toon.setBlend(frameBlend=settings['smoothanimations'])
        # if self.__restoration: #Need to reapply accessories each time a body part is changed
        #     avatar = base.localAvatar
        #     backpack = avatar.getBackpack()
        #     avatar.setBackpack(*backpack)
        self.mat.moveCamera()

    def __swapLegs(self, offset):
        length = len(ToonDNA.toonLegTypes)
        self.legChoice = (self.legChoice + offset) % length
        self.notify.debug('self.legChoice=%d, length=%d, self.legStart=%d' % (self.legChoice, length, self.legStart))
        self.__updateScrollButtons(self.legChoice, length, self.legStart, self.legLButton, self.legRButton)
        newLeg = ToonDNA.toonLegTypes[self.legChoice]
        self.dna.legs = newLeg
        self.toon.swapToonLegs(newLeg)
        self.toon.loop('neutral', 0)
        self.toon.swapToonColor(self.dna)
        self.toon.setBlend(frameBlend=settings['smoothanimations'])
        # if self.__restoration:
        #     avatar = base.localAvatar
        #     shoes = avatar.getShoes()
        #     avatar.setShoes(*shoes)
        self.mat.moveCamera()

    def __swapHead(self, offset):
        self.headList = ToonDNA.getHeadList(self.species)
        length = len(self.headList)
        self.headChoice = (self.headChoice + offset) % length
        self.__updateHead()
        self.mat.moveCamera()

    def __swapSpecies(self, offset):
        length = len(ToonDNA.toonSpeciesTypes)
        self.speciesChoice = (self.speciesChoice + offset) % length
        self.__updateScrollButtons(self.speciesChoice, length, self.speciesStart, self.speciesLButton, self.speciesRButton)
        self.species = ToonDNA.toonSpeciesTypes[self.speciesChoice]
        self.headList = ToonDNA.getHeadList(self.species)
        maxHeadChoice = len(self.headList) - 1
        if self.headChoice > maxHeadChoice:
            self.headChoice = maxHeadChoice
        self.__updateHead()
        self.mat.moveCamera()

    def createSpeciesButtons(self):
        gui = loader.loadModel('phase_3/models/gui/laff_o_meter')
        pos = (
            (.3, 0, .6), # Dog
            (.6, 0, .6), # Cat
            (.9, 0, .6), # Horse
            (.3, 0, .4), # Mouse
            (.6, 0, .4), # Rabbit
            (.9, 0, .4), # Duck
            (.3, 0, .2), # Monkey
            (.6, 0, .2), # Bear
            (.9, 0, .2), # Pig
            (.3, 0, 0), # Deer
            (.6, 0, 0), # Beaver
            (.9, 0, 0), # Alligator
            (.3, 0, -.2), # Fox
            (.6, 0, -.2), # Bat
            (.9, 0, -.2), # Raccoon
            (.6, 0, -.6), # Turkey
            (.3, 0, -.4), # Kiwi
            (.6, 0, -.4), # Kangaroo
            (.9, 0, -.4), # Koala
            (.3, 0, -.6) # Armadillo

              )

        for x in range(len(ToonDNA.toonSpeciesTypes)): # Loop through all species

            # Get their basic information
            hType = ToonDNA.getSpeciesName(ToonDNA.toonSpeciesTypes[x])
            name = TTLocalizer.AllSpecies[x]

            # Find the Laff Meter
            try:
                headIcon = gui.find('**/laffMeter_%s' % hType)
            except Exception:
                raise Exception('unknown toon species: ', hType)

            btn = MainMenuButton(relief = None, text_style = 3, image = headIcon, image_pos = (0, 0, 0),
            image_scale = (0.06, 0.06, 0.06), image1_scale = (0.06, 0.06, 0.06), image2_scale = (0.06, 0.06, 0.06),
            text_fg = (1, 1, 1, 1), text = ('', name, name, name), text_scale = .08,
            scale = 0.95, command = self.__setSpecies, extraArgs = [x])
            btn.reparentTo(base.a2dLeftCenter)
            btn.setPos(pos[x])
            btn.hide()
            self.speciesButtons.append(btn)

    def __setSpecies(self, offset):
        for btn in self.speciesButtons:
            btn['state'] = DGG.NORMAL

        self.speciesButtons[offset]['state'] = DGG.DISABLED

        length = len(ToonDNA.toonSpeciesTypes)
        self.speciesChoice = (offset) % length
        self.species = ToonDNA.toonSpeciesTypes[self.speciesChoice]
        self.headList = ToonDNA.getHeadList(self.species)
        maxHeadChoice = len(self.headList) - 1
        if self.headChoice > maxHeadChoice:
            self.headChoice = maxHeadChoice
        self.__updateHead()
        self.mat.moveCamera()

    def __updateHead(self):
        self.__updateScrollButtons(self.headChoice, len(self.headList), self.headStart, self.headLButton, self.headRButton)
        headIndex = ToonDNA.getHeadStartIndex(self.species) + self.headChoice
        newHead = ToonDNA.toonHeadTypes[headIndex]
        self.dna.head = newHead
        self.toon.swapToonHead(newHead)
        for lodName in self.toon.getLODNames():
            thisPart = self.toon.getPart('torso', lodName)
            if thisPart:
                thisPart.find('**/sleeves').show()
        self.toon.loop('neutral', 0)
        self.toon.swapToonColor(self.dna)
        self.toon.setBlend(frameBlend=settings['smoothanimations'])
        # if self.__restoration:
        #     avatar = base.localAvatar
        #     hat = avatar.getHat()
        #     avatar.setHat(*hat)
        #     glasses = avatar.getGlasses()
        #     avatar.setGlasses(*glasses)

    def __updateScrollButtons(self, choice, length, start, lButton, rButton):
        if choice == (start - 1) % length:
            rButton['state'] = DGG.DISABLED
        elif choice != (start - 1) % length:
            rButton['state'] = DGG.NORMAL
        if choice == start % length:
            lButton['state'] = DGG.DISABLED
        elif choice != start % length:
            lButton['state'] = DGG.NORMAL
        if lButton['state'] == DGG.DISABLED and rButton['state'] == DGG.DISABLED:
            self.notify.info('Both buttons got disabled! Doing fallback code. choice%d, length=%d, start=%d, lButton=%s, rButton=%s' % (choice,
             length,
             start,
             lButton,
             rButton))
            if choice == start % length:
                lButton['state'] = DGG.DISABLED
                rButton['state'] = DGG.NORMAL
            elif choice == (start - 1) % length:
                lButton['state'] = DGG.NORMAL
                rButton['state'] = DGG.DISABLED
            else:
                lButton['state'] = DGG.NORMAL
                rButton['state'] = DGG.NORMAL

    def __swapEyelashes(self, offset):
        length = len(ToonDNA.toonEyelashTypes)
        self.eyelashChoice = (self.eyelashChoice + offset) % length
        self.notify.debug('self.eyelashChoice=%d, length=%d, self.eyelashStart=%d' % (self.eyelashChoice, length, self.eyelashStart))
        self.__updateScrollButtons(self.eyelashChoice, length, self.eyelashStart, self.eyelashLButton, self.eyelashRButton)
        newEyelash = ToonDNA.toonEyelashTypes[self.eyelashChoice]
        self.dna.eyelashes = newEyelash
        self.toon.swapToonHead(self.dna.head)
        self.mat.moveCamera()

    def __handleForward(self):
        self.doneStatus = 'next'
        messenger.send(self.doneEvent)

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)

    def changeBody(self):
        newChoice = self.shuffleButton.getCurrChoice()
        newHead = newChoice[0]
        newHeadIndex = ToonDNA.toonHeadTypes.index(newHead) - ToonDNA.getHeadStartIndex(ToonDNA.getSpecies(newHead))
        newTorsoIndex = ToonDNA.toonTorsoTypes.index(newChoice[1])
        newLegsIndex = ToonDNA.toonLegTypes.index(newChoice[2])
        newEyelashIndex = ToonDNA.toonEyelashTypes.index(newChoice[3])
        oldHead = self.toon.style.head
        oldHeadIndex = ToonDNA.toonHeadTypes.index(oldHead) - ToonDNA.getHeadStartIndex(ToonDNA.getSpecies(oldHead))
        oldTorsoIndex = ToonDNA.toonTorsoTypes.index(self.toon.style.torso)
        oldLegsIndex = ToonDNA.toonLegTypes.index(self.toon.style.legs)
        oldEyelashIndex = ToonDNA.toonEyelashTypes.index(self.toon.style.eyelashes)

        while True:
            sIndex = random.randrange(0, len(ToonDNA.toonSpeciesTypes))
            if sIndex != 15 or self.wantTurkey: #15 is turkey
                break
        self.__setSpecies(sIndex)
        self.__swapHead(newHeadIndex - oldHeadIndex)
        self.__swapTorso(newTorsoIndex - oldTorsoIndex)
        self.__swapLegs(newLegsIndex - oldLegsIndex)
        self.__swapEyelashes(newEyelashIndex - oldEyelashIndex)

    def getCurrToonSetting(self):
        return [self.toon.style.head, self.toon.style.torso, self.toon.style.legs, self.toon.style.eyelashes]

