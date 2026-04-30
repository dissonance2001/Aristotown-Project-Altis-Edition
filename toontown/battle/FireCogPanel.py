from toontown.toonbase.ToontownBattleGlobals import *
from toontown.toonbase import ToontownGlobals
from direct.fsm import StateData
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BattleBase
from direct.gui.DirectGui import *
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
        gui2 = loader.loadModel('phase_3.5/models/gui/battle_gui_new')
        self.frame = DirectFrame(relief=None, image=gui.find('**/targeting_main'), text_align=TextNode.ALeft,
                                 pos=(0, 0, 0), scale=0.65)
        self.frame.hide()
        self.statusFrame = DirectFrame(parent=self.frame, relief=None, image=gui2.find('**/ToonBtl_Status_BG'),
                                       image_color=Vec4(0, 0, 0, 0), pos=(0.611, 0, 0))
        self.textFrame = DirectFrame(parent=self.frame, relief=None, image=gui2.find('**/PckMn_Select_Tab'),
                                     image_color=Vec4(1, 0, 0, 1), text='', text_fg=Vec4(1, 1, 1, 1),
                                     text_pos=(0, -0.025, -0.5), text_scale=0.08, pos=(-0.013, 0, -0.3))
        if self.toon:
            self.textFrame['text'] = TTLocalizer.TownBattleChooseAvatarToonTitle
        else:
            self.textFrame['text'] = TTLocalizer.TownBattleChooseAvatarCogTitle
        self.avatarButtons = []
        for i in xrange(7):
            button = DirectButton(parent=self.frame, relief=None, image=(
            gui.find('**/arrow_neutral'), gui.find('**/arrow_press'), gui.find('**/arrow_hover')),
                                  command=self.__handleAvatar, extraArgs=[i])
            button.setScale(.5, .5, .5)
            button.setPos(0, 0, 0.7)
            self.avatarButtons.append(button)

        self.backButton = DirectButton(parent=self.frame, relief=None, image=(
        gui.find('**/back_neutral'), gui.find('**/back_press'), gui.find('**/back_hover')), pos=(-0.847, -0.3, -0.011),
                                       scale=.5, text=TTLocalizer.TownBattleChooseAvatarBack, text_scale=0.3,
                                       text_pos=(0.01, -0.015), text_fg=Vec4(0, 0, 0, 1), command=self.__handleBack)

        gui.removeNode()
        self.loaded = 1

    def unload(self):
        if self.loaded:
            self.frame.destroy()
            del self.frame
            del self.statusFrame
            del self.textFrame
            del self.avatarButtons
            del self.backButton
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
        if numAvatars == 1:
            self.avatarButtons[0].setX(0)
        elif numAvatars == 2:
            self.avatarButtons[0].setX(0.4)
            self.avatarButtons[1].setX(-0.4)
        elif numAvatars == 3:
            self.avatarButtons[0].setX(0.75)
            self.avatarButtons[1].setX(0.0)
            self.avatarButtons[2].setX(-0.75)
        elif numAvatars == 4:
            self.avatarButtons[0].setX(1.15)
            self.avatarButtons[1].setX(0.4)
            self.avatarButtons[2].setX(-0.4)
            self.avatarButtons[3].setX(-1.15)
        elif numAvatars == 5:
            self.avatarButtons[0].setX(1.5)
            self.avatarButtons[1].setX(0.75)
            self.avatarButtons[2].setX(0.0)
            self.avatarButtons[3].setX(-0.75)
            self.avatarButtons[4].setX(-1.5)
        elif numAvatars == 6:
            self.avatarButtons[0].setX(1.9)
            self.avatarButtons[1].setX(1.15)
            self.avatarButtons[2].setX(0.4)
            self.avatarButtons[3].setX(-0.4)
            self.avatarButtons[4].setX(-1.15)
            self.avatarButtons[5].setX(-1.9)
        elif numAvatars == 7:
            self.avatarButtons[0].setX(2.25)
            self.avatarButtons[1].setX(1.5)
            self.avatarButtons[2].setX(0.75)
            self.avatarButtons[3].setX(0.0)
            self.avatarButtons[4].setX(-0.75)
            self.avatarButtons[5].setX(-1.5)
            self.avatarButtons[6].setX(-2.25)
        else:
            self.notify.error('Invalid number of avatars: %s' % numAvatars)