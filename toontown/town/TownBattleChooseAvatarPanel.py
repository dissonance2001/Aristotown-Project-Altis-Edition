from toontown.toonbase.ToontownBattleGlobals import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals
from direct.fsm import StateData
import random
from panda3d.core import TextureStage, CardMaker
from direct.interval.IntervalGlobal import *
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BattleBase
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from toontown.toonbase import TTLocalizer

class TownBattleChooseAvatarPanel(StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('ChooseAvatarPanel')

    def __init__(self, doneEvent, toon):
        self.notify.debug('Init choose panel...')
        StateData.StateData.__init__(self, doneEvent)
        self.numAvatars = 0
        self.chosenAvatar = 0
        self.track = None
        self.level = None
        self.toon = toon

    def load(self):
        gui = loader.loadModel('phase_3.5/models/gui/battlegui/targeting')
        self.rowModels = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
        self.frame = DirectFrame(relief=None, image=gui.find('**/targeting_main'), text_align=TextNode.ALeft, pos=(0, 0, -0.025), scale=0.425)
        self.frame.hide()
        self.textFrame = DirectFrame(parent=self.frame, relief=None, text='', text_fg=Vec4(1, 1, 1, 1), text_font=getSignFont(), text_scale=0.1, pos=(0, 0, -0.325))
        if self.toon:
            self.textFrame['text'] = TTLocalizer.TownBattleChooseAvatarToonTitle
        else:
            self.textFrame['text'] = TTLocalizer.TownBattleChooseAvatarCogTitle
        self.avatarButtons = []
        for i in xrange(7):
            button = DirectButton(parent=self.frame, relief=None, image=(gui.find('**/arrow_neutral'), gui.find('**/arrow_press'), gui.find('**/arrow_hover')), command=self.__handleAvatar, extraArgs=[i])
            if self.toon:
                button.setScale(.675, .675, -.675)
                button.setPos(0, 0, -1)
            else:
                button.setScale(.675, .675, .675)
                button.setPos(0, 0, 1)
            self.avatarButtons.append(button)

        self.backButton = DirectButton(parent=self.frame, relief=None, image=(gui.find('**/back_neutral'), gui.find('**/back_press'), gui.find('**/back_hover')), pos=(0, 0, -0.6),
                                        scale=(.75, .5, .5), text="BACK", text_scale=(.175, .25, .25), text_pos=(0.05, -0.1), text_fg=Vec4(0.973, 1, 0, 1), text_font=getSignFont(), command=self.__handleBack)
        self.backButton.setBin('fixed', 0) 
        self.gagEmblem = DirectFrame(
            parent=self.frame,
            image=self.rowModels.find('**/emblem_gag'),
            pos=(0, 0, 0.15),
            scale=1,
            relief=None
        )
        self.gagEmblem.setBin('fixed', 0) 
        self.gagEmblemOrganicTex = loader.loadTexture('phase_3.5/maps/battlegui/pres_scroll_bg.png')
        self.gagEmblemOrganicTex.setWrapU(Texture.WMRepeat)
        self.gagEmblemOrganicTex.setWrapV(Texture.WMRepeat)

        self.gagEmblemScrollStage = TextureStage('choose-gag-emblem-scroll')

        self.gagEmblemScrollIval = LerpFunctionInterval(
            self.updateGagEmblemScroll,
            duration=3.0,
            fromData=0.0,
            toData=1.0
        )
        self.gagEmblemScrollIval.loop()
        invModel = loader.loadModel('phase_3.5/models/gui/inventory_icons')
        self.invModels = []
        for track in range(len(AvPropsNew)):
            itemList = []
            for item in range(len(AvPropsNew[track])):
                itemList.append(invModel.find('**/' + AvPropsNew[track][item]))

            self.invModels.append(itemList)


        self.gagIcon = DirectFrame(
                parent=self.frame,
                relief=None,
                image=None,
                scale=3,
                pos=(0, 0, 0.15)
        )
        self.gagIcon.setBin('fixed', 20) 
        self.invModel = invModel
        gui.removeNode()

    def setGagEmblemOrganic(self, organic):
        imageNode = self.gagEmblem.component('image0')

        if organic:
            imageNode.setTexture(self.gagEmblemScrollStage, self.gagEmblemOrganicTex, 1)
            imageNode.setTexScale(self.gagEmblemScrollStage, 6, 6)
            imageNode.setTransparency(1)
        else:
            imageNode.clearTexture(self.gagEmblemScrollStage)


    def updateGagEmblemScroll(self, t):
        if not hasattr(self, 'gagEmblem') or self.gagEmblem is None:
            return

        imageNode = self.gagEmblem.component('image0')
        imageNode.setTexOffset(self.gagEmblemScrollStage, t, -t)

    def unload(self):
        if getattr(self, 'gagEmblemScrollIval', None):
            self.gagEmblemScrollIval.finish()
            self.gagEmblemScrollIval = None

        if getattr(self, 'gagIcon', None):
            self.gagIcon.destroy()
            del self.gagIcon

        if getattr(self, 'gagEmblem', None):
            self.gagEmblem.destroy()
            del self.gagEmblem

        if getattr(self, 'textFrame', None):
            self.textFrame.destroy()
            del self.textFrame

        for button in self.avatarButtons:
            button.destroy()

        self.backButton.destroy()

        self.frame.destroy()

        self.invModel.removeNode()
        self.rowModels.removeNode()

        del self.avatarButtons
        del self.backButton
        del self.frame
        del self.invModels
        del self.invModel
        del self.rowModels
        del self.gagEmblemOrganicTex
        del self.gagEmblemScrollStage

    def enter(self, numAvatars, localNum = None, luredIndices = None, trappedIndices = None, track = None, level = None):
        self.track = track
        self.level = level
        organicBonus = False

        if self.track is not None and self.level is not None:
            organicBonus = base.localAvatar.checkGagBonus(self.track, self.level)

        self.setGagEmblemOrganic(organicBonus)
        trackColor = Vec4(
            TrackColors[track][0],
            TrackColors[track][1],
            TrackColors[track][2],
            1
        )

        self.gagEmblem['image_color'] = trackColor
        self.frame.show()
        self.gagIcon.show()
        self.gagIcon['image'] = self.invModels[self.track][self.level]
        invalidTargets = []
        if not self.toon:
            if len(luredIndices) > 0:
                if track == BattleBase.TRAP or track == BattleBase.LURE:
                    invalidTargets += luredIndices
            if len(trappedIndices) > 0:
                if track == BattleBase.TRAP:
                    invalidTargets += trappedIndices
        self.__placeButtons(numAvatars, invalidTargets, localNum)

    def exit(self):
        self.frame.hide()

    def __handleBack(self):
        doneStatus = {'mode': 'Back'}
        messenger.send(self.doneEvent, [doneStatus])

    def __handleAvatar(self, avatar):
        doneStatus = {'mode': 'Avatar',
         'avatar': avatar}
        messenger.send(self.doneEvent, [doneStatus])

    def adjustCogs(self, numAvatars, luredIndices, trappedIndices, track, level=None):
        self.track = track
        self.level = level
        invalidTargets = []
        if len(luredIndices) > 0:
            if track == BattleBase.TRAP or track == BattleBase.LURE:
                invalidTargets += luredIndices
        if len(trappedIndices) > 0:
            if track == BattleBase.TRAP:
                invalidTargets += trappedIndices
        self.__placeButtons(numAvatars, invalidTargets, None)

    def adjustToons(self, numToons, localNum, track=None, level=None):
        self.track = track
        self.level = level
        self.__placeButtons(numToons, [], localNum)

    def __placeButtons(self, numAvatars, invalidTargets, localNum):
        for i in xrange(7):
            if numAvatars > i and i not in invalidTargets and i != localNum:
                self.avatarButtons[i].show()
            else:
                self.avatarButtons[i].hide()

        # for i in xrange(7):
        #     self.gagIcons[i].hide()

        # if self.track is not None and self.level is not None and self.track >= 0 and self.level >= 0:
        #     gagNodeName = AvPropsNew[self.track][self.level]
        #     gagNode = self.invModel.find('**/' + gagNodeName)

        #     for i in xrange(7):
        #         if not self.avatarButtons[i].isHidden():
        #             self.gagIcons[i].configure(image=gagNode)
        #             self.gagIcons[i].show()

        confused = False
        if 'confused' in base.localAvatar.battleConditions:
            confused = True

        positions = self.__getAvatarPositions(numAvatars)

        if positions is None:
            self.notify.error('Invalid number of avatars: %s' % numAvatars)
            return None

        indices = range(numAvatars)

        if confused:
            random.shuffle(indices)

        for posIndex in range(numAvatars):
            avatarIndex = indices[posIndex]
            self.avatarButtons[avatarIndex].setX(positions[posIndex])
        return None
    
    def __getAvatarPositions(self, numAvatars):
        positionsByCount = {
            1: [0],
            2: [0.61, -0.61],
            3: [1.14, 0.0, -1.14],
            4: [1.748, 0.61, -0.61, -1.748],
            5: [2.28, 1.14, 0.0, -1.14, -2.28],
            6: [2.888, 1.748, 0.61, -0.61, -1.748, -2.888],
            7: [3.42, 2.28, 1.14, 0.0, -1.14, -2.28, -3.42],
        }

        return positionsByCount.get(numAvatars)
