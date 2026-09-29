from panda3d.core import *
from otp.distributed.PotentialAvatar import PotentialAvatar
from toontown.toonbase import ToontownBattleGlobals as BattleGlobals
from toontown.toon import ToonDNA
from direct.fsm import StateData
from direct.gui.DirectGui import *
from .MakeAToonGlobals import *
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.gui import TTDialog
from direct.task import Task
from ..utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class StartShop(StateData.StateData):
    def __init__(self, doneEvent, avList = None, index = None):
        StateData.StateData.__init__(self, doneEvent)
        self.toon = None
        # self.index = -1
        self.gagChoices = [None, None]
        self.lastChoice = 0 #Handles which index to update in gagChoices
        self.avList = avList
        self.index = index
        self.avExists = -1

    def enter(self, toon, shopsVisited = [], tutorialEnter = False):
        self.toon = toon
        self.dna = toon.getStyle()
        self.tutorialEnter = tutorialEnter
        self.refreshButtons()
        self.acceptOnce('last', self.__handleBackward)
        self.acceptOnce('next', self.__handleForward)

    def showButtons(self):
        self.parentFrame.show()

    def hideButtons(self):
        self.parentFrame.hide()

    def exit(self):
        self.ignoreAll()
        try:
            del self.toon
        except:
            print('StartShop: toon not found')

        self.hideButtons()

    def load(self):
        self.buttons = []
        self.gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        pagGUI = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_PAGGui')
        poster = pagGUI.find('**/GagPaper')
        circle = pagGUI.find('**/circle')
        self.parentFrame = self.getNewFrame()
        self.gagFrame = DirectFrame(parent=self.parentFrame, image=poster, image_scale=(1.5, 1.5, 1.7), relief=None, pos=(-.36, 0, -0.5), scale=1)
        for trackId in range(len(BattleGlobals.Tracks)):
            gagButtonImage = pagGUI.find('**/' + TTLocalizer.BattleGlobalTracks[trackId])
            button = DirectButton(parent=self.gagFrame, image=gagButtonImage, relief=None, pos=gagSelectionButtonPos[trackId],
                                  command=self.chooseGag, extraArgs=[trackId], scale=(.33, 1, .33), text=gagSelectionDescriptions[trackId], 
                                  text_scale=(.093), frameSize=(-.475, .475, -.45, .45))
            button.circle = DirectFrame(parent=button, image=circle, relief=None)
            if trackId in (0,):
                button['text_pos'] = (0.01, -.28)
            else:
                button['text_pos'] = (0.01, -.21)
            self.buttons.append(button)
        self.parentFrame.hide()

    def unload(self):
        self.gui.removeNode()
        del self.gui
        self.parentFrame.destroy()
        del self.parentFrame
        self.ignore('MAT-newToonCreated')
    
    def getNewFrame(self):
        frame = DirectFrame(relief=DGG.RAISED, pos=(0.98, 0, 0.416), frameColor=(1, 0, 0, 0))
        frame.setPos(-0.36, 0, -0.5)
        frame.reparentTo(base.a2dTopRight)
        return frame

    def chooseGag(self, index):
        if index in self.gagChoices: #If clicking a gag that has already been selected clear it from selection
            if self.gagChoices[0] == index:
                self.gagChoices[0] = None
                self.toon.choiceAlpha = None
                self.lastChoice = 0 #Switch lastChoice to the index that was cleared
            else:
                self.gagChoices[1] = None
                self.toon.choiceBeta = None
                self.lastChoice = 1 #Switch lastChoice to the index that was cleared

        else: #Else assign the chosen gag using lastChoice as index
            self.gagChoices[self.lastChoice] = index
            if self.lastChoice == 0:
                self.toon.choiceAlpha = index
                self.lastChoice = 1
            else:
                self.toon.choiceBeta = index
                self.lastChoice = 0

        self.refreshButtons()

    def refreshButtons(self): #Check all buttons for whether they should be circled or not then update the text at the top of screen
        for count, button in enumerate(self.buttons):
            if count in self.gagChoices:
                button.circle.show()
            else:
                button.circle.hide()
        self.updateTopBar()

    def updateTopBar(self): #Function called by send also updates nextButton based on choicesRemaining
        choicesRemaining = self.gagChoices.count(None)
        messenger.send('updateTopBar', [choicesRemaining])

    def badGags(self): #Checks if gags selected aren't "beginner friendly" and displays appropriate warning
        self.notify.debug("bad gag")
        if 0 in self.gagChoices and 2 in self.gagChoices: #Tu + Lure
            self.promptGags(0)
            return 1
        if 5 in self.gagChoices and 4 not in self.gagChoices: #Zap w/o splash
            self.promptGags(1)
            return 1
        if 1 in self.gagChoices and 2 not in self.gagChoices: #Trap w/o Lure
            self.promptGags(2)
            return 1
        return 0

    def promptGags(self, promptIndex): #Creates dialogue box for badGag warning
        self.notify.debug("prompt bad gag")
        self.promptGagsDialog = TTDialog.TTDialog(
            parent=aspect2d, text=TTLocalizer.PromptBadGags[promptIndex], text_scale=0.06, text_align=TextNode.ACenter, 
            text_wordwrap=22, command=self.confirmBadGags, fadeScreen=0.5, 
            style=TTDialog.TwoChoice, buttonTextList=[TTLocalizer.PromptBadGagsYes, TTLocalizer.PromptBadGagsNo], 
            button_text_scale=0.06, buttonPadSF=5.5, sortOrder=NO_FADE_SORT_INDEX)
        self.promptGagsDialog.show()

    def confirmBadGags(self, choice = 0):
        #Pressing yes emulates a successful __handleDone event and deletes dialogue box
        if choice == 1: 
            self.promptGagsDialog.destroy()
            self.serverCreateAvatar()
        #Pressing no destroys dialogue box and prepares PAG/StartShop for another next button press
        else: 
            self.promptGagsDialog.destroy()
            self.acceptOnce('next', self.__handleForward)

    def __handleForward(self):
        if not self.badGags():
            self.serverCreateAvatar()

    def __handleBackward(self):
        self.doneStatus = 'last'
        messenger.send(self.doneEvent)

    def __handleDone(self):
        self.notify.debug('Ending Make A Toon: %s' % self.toon.style)
        self.doneStatus = 'done'
        self.cleanupToonVars()
        messenger.send(self.doneEvent)

    def checkNameTyped(self, justCheck = False):
        self.notify.debug(f'checkNameTyped: {self.toon.potName}')
        if justCheck:
            avId = 0
        else:
            avId = self.avId
        base.cr.csm.sendSetNameTyped(avId, self.toon.potName[0], self.handleSetNameTypedResp)
        self.waitForServer()

    def checkNamePattern(self, justCheck=False):
        self.notify.debug('checkNamePattern')

        if justCheck:
            avId = 0
        else:
            avId = self.avId

        base.cr.csm.sendSetNamePattern(avId,
                                       self.toon.nameIndices[0], self.toon.nameFlags[0],
                                       self.toon.nameIndices[1], self.toon.nameFlags[1],
                                       self.toon.nameIndices[2], self.toon.nameFlags[2],
                                       self.toon.nameIndices[3], self.toon.nameFlags[3],
                                       self.handleSetNamePatternResp)
        self.waitForServer()

    def waitForServer(self):
        self.waitForServerDialog = TTDialog.TTDialog(text=TTLocalizer.WaitingForNameSubmission, style=TTDialog.NoButtons)
        self.waitForServerDialog.show()

    def cleanupWaitForServer(self):
        if self.waitForServerDialog is not None:
            self.waitForServerDialog.cleanup()
            self.waitForServerDialog = None

    def handleSetNameTypedResp(self, avId, status):
        self.notify.debug('handleSetNameTypedResp')
        self.cleanupWaitForServer()

        # if the judgeName status is clear and the av allocated, populate main menu
        if status and avId:
            self.makePotentialAvatar()

        # somethings gone wrong
        else:
            self.reject(TTLocalizer.NameError)

    def handleSetNamePatternResp(self, avId, status):
        self.notify.debug('handleSetNamePatternResp')
        self.cleanupWaitForServer()

        if status and avId:
            self.makePotentialAvatar()
        else:
            self.reject(TTLocalizer.NameError)


    def serverCreateAvatar(self):
        self.notify.debug(f'serverCreateAvatar {self.index} {self.avList}')
        if self.index is not None and self.avList is not None:
            style = self.toon.getStyle()
            self.newDNA = style.makeNetString()
            trackChoices = [self.toon.choiceAlpha, self.toon.choiceBeta]
            startingPg = self.toon.startingPg
            base.cr.csm.sendCreateAvatar(style, '', self.index, self.toon.uberType, trackChoices, startingPg, skipTutorial=1)
            self.accept('makeAToonCreateAvatarDone', self.handleCreateAvatarResponse)
        # accessing from tutorial, no need to make an av, tutinstance will handle setting gags
        elif self.tutorialEnter:
            self.__handleDone()
        else:
            self.notify.warning("serverCreateAvatar from unknown location")

    def handleCreateAvatarResponse(self, avId):
        self.notify.debug('handleCreateAvatarResponse')
        self.avId = avId
        self.avExists = 1
        if self.toon.typedName:
            self.checkNameTyped()
        else:
            self.checkNamePattern()

    def makePotentialAvatar(self):
        self.toon.potName[1] = self.toon.potName[0]
        self.toon.setName(self.toon.potName[0])
        newPotAv = PotentialAvatar(self.avId, self.toon.potName, self.newDNA, self.index, 1)
        self.avList.append(newPotAv)
        self.__handleDone()

    def reject(self, str):
        self.notify.debug('reject')
        self.toon.potName[0] = ''
        self.rejectDialog = TTDialog.TTGlobalDialog(doneEvent='rejectDone', message=str, style=TTDialog.Acknowledge)
        self.rejectDialog.show()
        self.acceptOnce('rejectDone', self.__handleReject)

    def __handleReject(self):
        self.notify.debug("__handleReject")
        self.rejectDialog.cleanup()
        # self.nameEntry['focus'] = 1
        # self.typeANameButton.show()
        # self.acceptOnce('next', self.__handleDone)

    # these vars were temporary to get the name change done across NameShop and StartShop
    def cleanupToonVars(self):
        if hasattr(self.toon, "typedName"):
            del self.toon.typedName
        if hasattr(self.toon, "nameIndices"):
            del self.toon.nameIndices
        if hasattr(self.toon, "nameFlags"):
            del self.toon.nameFlags
