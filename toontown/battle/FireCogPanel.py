from toontown.toonbase.ToontownBattleGlobals import *
from toontown.toonbase import ToontownGlobals
from direct.fsm import StateData
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BattleBase
from direct.gui.DirectGui import *
import random
from pandac.PandaModules import *
from toontown.toonbase import TTLocalizer

class FireCogPanel(StateData.StateData):
    notify = DirectNotifyGlobal.directNotify.newCategory('ChooseAvatarPanel')

    def __init__(self, doneEvent):
        self.notify.debug('Init choose panel...')
        StateData.StateData.__init__(self, doneEvent)
        self.numAvatars = 0
        self.chosenAvatar = 0
        self.toon = 0
        self.loaded = 0

    def load(self):
        gui = loader.loadModel('phase_3.5/models/gui/battlegui/targeting')
        self.rowModels = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
        self.invModel = loader.loadModel('phase_3.5/models/gui/inventory_icons')
        self.status = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.passIcon = self.rowModels.find('**/pass_icon')
        self.fireIcon = self.status.find('**/pinkslip_icon')
        self.sueIcon = self.status.find('**/sued_icon')
        self.sosIcon = self.status.find('**/energized_icon')
        self.invModels = []
        for track in range(len(AvPropsNew)):
            itemList = []
            for item in range(len(AvPropsNew[track])):
                itemList.append(self.invModel.find('**/' + AvPropsNew[track][item]))
            self.invModels.append(itemList)

        self.frame = DirectFrame(
            relief=None,
            image=gui.find('**/targeting_main'),
            text_align=TextNode.ALeft,
            pos=(0, 0, -0.025),
            scale=0.425
        )
        self.frame.hide()
        self.textFrame = DirectFrame(parent=self.frame, relief=None, text='', text_fg=Vec4(0.973, 1, 0, 1), text_font=getMinnieFont(), text_scale=0.075, pos=(0, 0, -0.275))
        self.avatarButtons = []
        for i in xrange(7):
            button = DirectButton(parent=self.frame, relief=None, image=(
            gui.find('**/arrow_neutral'), gui.find('**/arrow_press'), gui.find('**/arrow_hover')),
                                  command=self.__handleAvatar, extraArgs=[i])
            button.setScale(.675, .675, .675)
            button.setPos(0, 0, 1)
            self.avatarButtons.append(button)

        self.backButton = DirectButton(parent=self.frame, relief=None, image=(gui.find('**/back_neutral'), gui.find('**/back_press'), gui.find('**/back_hover')), pos=(0, 0, -0.6),
                                        scale=(.75, .5, .5), text="BACK", text_scale=(.175, .25, .25), text_pos=(0.05, -0.1), text_fg=Vec4(0.973, 1, 0, 1), text_font=getMinnieFont(), command=self.__handleBack)
        self.backButton.setBin('fixed', 0) 
        gui.removeNode()
        self.rowModels = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')

        self.fireIcon = self.status.find('**/pinkslip_icon')

        self.gagEmblem = DirectFrame(
            parent=self.frame,
            image=self.rowModels.find('**/emblem_gag'),
            pos=(0, 0, 0.145),
            scale=1,
            relief=None
        )
        self.gagEmblem['image_color'] = Vec4(0.937, 0.718, 0.816, 1)
        self.gagEmblem.setBin('fixed', 0)

        self.gagIcon = DirectFrame(
            parent=self.frame,
            relief=None,
            image=self.fireIcon,
            scale=1,
            pos=(0, 0, 0.145)
        )
        self.gagIcon['image'] = self.fireIcon
        self.gagIcon.setScale(.75)
        self.gagIcon['image_scale'] = .75
        self.gagIcon.setBin('fixed', 20)
        self.loaded = 1

    def unload(self):
        if self.loaded:
            self.frame.destroy()
            del self.frame
            del self.avatarButtons
            del self.backButton
            self.gagIcon.destroy()
            self.gagEmblem.destroy()
            self.textFrame.destroy()

            self.invModel.removeNode()
            self.rowModels.removeNode()
            self.status.removeNode()
            del self.status

            del self.gagIcon
            del self.gagEmblem
            del self.textFrame
            del self.invModels
            del self.invModel
            del self.rowModels
        self.loaded = 0

    def enter(self, numAvatars, localNum = None, luredIndices = None, trappedIndices = None, track = None, fireCosts = None):
        if not self.loaded:
            self.load()
        self.frame.show()
        invalidTargets = []
        if not self.toon:
            if len(luredIndices) > 0:
                if track == BattleBase.TRAP or track == BattleBase.LURE:
                    invalidTargets += luredIndices
            if len(trappedIndices) > 0:
                if track == BattleBase.TRAP:
                    invalidTargets += trappedIndices
        self.__placeButtons(numAvatars, invalidTargets, localNum, fireCosts)

    def exit(self):
        self.frame.hide()

    def __handleBack(self):
        doneStatus = {'mode': 'Back'}
        messenger.send(self.doneEvent, [doneStatus])

    def __handleAvatar(self, avatar):
        doneStatus = {'mode': 'Avatar',
         'avatar': avatar}
        messenger.send(self.doneEvent, [doneStatus])

    def adjustCogs(self, numAvatars, luredIndices, trappedIndices, track):
        invalidTargets = []
        if len(luredIndices) > 0:
            if track == BattleBase.TRAP or track == BattleBase.LURE:
                invalidTargets += luredIndices
        if len(trappedIndices) > 0:
            if track == BattleBase.TRAP:
                invalidTargets += trappedIndices
        self.__placeButtons(numAvatars, invalidTargets, None)
        return

    def adjustToons(self, numToons, localNum):
        self.__placeButtons(numToons, [], localNum)

    def __placeButtons(self, numAvatars, invalidTargets, localNum, fireCosts):
        canfire = 0
        for i in xrange(7):
            if numAvatars > i and i not in invalidTargets and i != localNum:
                self.avatarButtons[i].show()
                self.avatarButtons[i]['text'] = ''
                if fireCosts[i] <= localAvatar.getPinkSlips():
                    self.avatarButtons[i]['state'] = DGG.NORMAL
                    self.avatarButtons[i]['text_fg'] = (0, 0, 0, 1)
                    canfire = 1
                else:
                    self.avatarButtons[i]['state'] = DGG.DISABLED
                    self.avatarButtons[i]['text_fg'] = (1.0, 0, 0, 1)
            else:
                self.avatarButtons[i].hide()

        if canfire:
            self.textFrame['text'] = TTLocalizer.FireCogTitle % localAvatar.getPinkSlips()
        else:
            self.textFrame['text'] = TTLocalizer.FireCogLowTitle % localAvatar.getPinkSlips()
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