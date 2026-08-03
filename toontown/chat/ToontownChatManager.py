import sys
from direct.showbase import DirectObject
from toontown.toonbase.ToonPythonUtil import traceFunctionCall
from otp.otpbase import OTPGlobals
from otp.otpbase import OTPLocalizer
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toontowngui import TeaserPanel
from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from otp.chat import ChatManager
from TTChatInputSpeedChat import TTChatInputSpeedChat
from TTChatInputUnites import TTChatInputUnites
from TTChatInputNormal import TTChatInputNormal
from TTChatInputWhiteList import TTChatInputWhiteList
from toontown.toon.AltisCommandShortcuts import translateCommandText

class HackedDirectRadioButton(DirectCheckButton):

    def __init__(self, parent = None, **kw):
        optiondefs = ()
        self.defineoptions(kw, optiondefs)
        DirectCheckButton.__init__(self, parent)
        self.initialiseoptions(HackedDirectRadioButton)

    def commandFunc(self, event):
        if self['indicatorValue']:
            self['indicatorValue'] = 0
        DirectCheckButton.commandFunc(self, event)


class ToontownChatManager(ChatManager.ChatManager):
    notify = DirectNotifyGlobal.directNotify.newCategory('ToontownChatManager')

    def __init__(self, cr, localAvatar):
        gui = loader.loadModel('phase_3.5/models/gui/chat_input_gui')
        self.normalButton = DirectButton(image=(gui.find('**/ChtBx_ChtBtn_UP'), gui.find('**/ChtBx_ChtBtn_DN'), gui.find('**/ChtBx_ChtBtn_RLVR')), pos=(0.0683, 0, -0.072), parent=base.a2dTopLeft, scale=1.179, relief=None, image_color=Vec4(1, 1, 1, 1), text=('', OTPLocalizer.ChatManagerChat, OTPLocalizer.ChatManagerChat), text_align=TextNode.ALeft, text_scale=TTLocalizer.TCMnormalButton, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(-0.0525, -0.09), textMayChange=0, sortOrder=DGG.FOREGROUND_SORT_INDEX, command=self.__normalButtonPressed)
        self.normalButton.hide()
        self.openScSfx = loader.loadSfx('phase_3.5/audio/sfx/GUI_quicktalker.ogg')
        self.magicWordSfx = loader.loadSfx('phase_3/audio/sfx/clock03.ogg')
        self.openScSfx.setVolume(0.6)
        self.scButton = DirectButton(image=(gui.find('**/ChtBx_ChtBtn_UP'), gui.find('**/ChtBx_ChtBtn_DN'), gui.find('**/ChtBx_ChtBtn_RLVR')), pos=TTLocalizer.TCMscButtonPos, parent=base.a2dTopLeft, scale=1.179, relief=None, image_color=Vec4(0.75, 1, 0.6, 1), text=('', OTPLocalizer.GlobalSpeedChatName, OTPLocalizer.GlobalSpeedChatName), text_scale=TTLocalizer.TCMscButton, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(0, -0.09), textMayChange=0, sortOrder=DGG.FOREGROUND_SORT_INDEX, command=self.__scButtonPressed, clickSound=self.openScSfx)
        self.scButton.hide()
        self.clButton = DirectButton(image=(gui.find('**/ChtBx_ChtBtn_UP'), gui.find('**/ChtBx_ChtBtn_DN'), gui.find('**/ChtBx_ChtBtn_RLVR')), pos=TTLocalizer.TCMclButtonPos, parent=base.a2dTopLeft, scale=1.179, relief=None, image_color=Vec4(1, 0.6, 0.75, 1), text=('', OTPLocalizer.GlobalChatLogName, OTPLocalizer.GlobalChatLogName), text_scale=TTLocalizer.TCMclButton, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1), text_pos=(0, -0.09), textMayChange=0, sortOrder=DGG.FOREGROUND_SORT_INDEX, command=self.__clButtonPressed)
        self.clButton.hide()
        self.whisperFrame = DirectFrame(parent=base.a2dTopLeft, relief=None, image=DGG.getDefaultDialogGeom(), image_scale=(0.45, 0.45, 0.45), image_color=OTPGlobals.GlobalDialogColor, pos=(1.25, 0, -0.269), text=OTPLocalizer.ChatManagerWhisperTo, text_wordwrap=7.0, text_scale=TTLocalizer.TCMwhisperFrame, text_fg=Vec4(0, 0, 0, 1), text_pos=(0, 0.14), textMayChange=1, sortOrder=DGG.FOREGROUND_SORT_INDEX)
        self.whisperFrame.hide()
        self.whisperButton = DirectButton(parent=self.whisperFrame, image=(gui.find('**/ChtBx_ChtBtn_UP'), gui.find('**/ChtBx_ChtBtn_DN'), gui.find('**/ChtBx_ChtBtn_RLVR')), pos=(-0.125, 0, -0.1), scale=1.179, relief=None, image_color=Vec4(1, 1, 1, 1), text=('',
         OTPLocalizer.ChatManagerChat,
         OTPLocalizer.ChatManagerChat,
         ''), image3_color=Vec4(0.6, 0.6, 0.6, 0.6), text_scale=TTLocalizer.TCMwhisperButton, text_fg=(0, 0, 0, 1), text_pos=(0, -0.09), textMayChange=0, command=self.__whisperButtonPressed)
        self.whisperScButton = DirectButton(parent=self.whisperFrame, image=(gui.find('**/ChtBx_ChtBtn_UP'), gui.find('**/ChtBx_ChtBtn_DN'), gui.find('**/ChtBx_ChtBtn_RLVR')), pos=(0.0, 0, -0.1), scale=1.179, relief=None, image_color=Vec4(0.75, 1, 0.6, 1), text=('',
         OTPLocalizer.GlobalSpeedChatName,
         OTPLocalizer.GlobalSpeedChatName,
         ''), image3_color=Vec4(0.6, 0.6, 0.6, 0.6), text_scale=TTLocalizer.TCMwhisperScButton, text_fg=(0, 0, 0, 1), text_pos=(0, -0.09), textMayChange=0, command=self.__whisperScButtonPressed)
        self.whisperCancelButton = DirectButton(parent=self.whisperFrame, image=(gui.find('**/CloseBtn_UP'), gui.find('**/CloseBtn_DN'), gui.find('**/CloseBtn_Rllvr')), pos=(0.125, 0, -0.1), scale=1.179, relief=None, text=('', OTPLocalizer.ChatManagerCancel, OTPLocalizer.ChatManagerCancel), text_scale=0.05, text_fg=(0, 0, 0, 1), text_pos=(0, -0.09), textMayChange=0, command=self.__whisperCancelPressed)
        gui.removeNode()
        ChatManager.ChatManager.__init__(self, cr, localAvatar)
        self.defaultToWhiteList = base.config.GetBool('white-list-is-default', 1)
        self.chatInputSpeedChat = TTChatInputSpeedChat(self)
        self.chatInputUnites = TTChatInputUnites(self)
        self.panelClubSpeedChat = False
        self.normalPos = Vec3(0.25, 0, -0.196)
        self.whisperPos = Vec3(0, 0, -0.296)
        self.speedChatPlusPos = Vec3(-0.35, 0, 0.71)
        self.SCWhisperPos = Vec3(0, 0, 0)
        self.chatInputWhiteList = TTChatInputWhiteList()
        if self.defaultToWhiteList:
            self.chatInputNormal = self.chatInputWhiteList
            self.chatInputNormal.setPos(self.normalPos)
            self.chatInputNormal.desc = 'chatInputNormal'
        else:
            self.chatInputNormal = TTChatInputNormal(self)
        self.chatInputWhiteList.setPos(self.speedChatPlusPos)
        self.chatInputWhiteList.reparentTo(base.a2dTopLeft)
        self.chatInputWhiteList.desc = 'chatInputWhiteList'

        # Keep the legacy widgets alive for old quest/tutorial references, but
        # parent them under hidden so no old Altis chat button or entry can
        # reappear over the replacement panel.
        self.normalButton.reparentTo(hidden)
        self.scButton.reparentTo(hidden)
        self.clButton.reparentTo(hidden)
        self.whisperFrame.reparentTo(hidden)
        self.chatInputWhiteList.reparentTo(hidden)
        if self.chatInputNormal is not self.chatInputWhiteList:
            self.chatInputNormal.reparentTo(hidden)
        return

    def delete(self):
        self.chatInputUnites.delete()
        del self.chatInputUnites
        ChatManager.ChatManager.delete(self)
        loader.unloadModel('phase_3.5/models/gui/chat_input_gui')
        self.normalButton.destroy()
        del self.normalButton
        self.scButton.destroy()
        del self.scButton
        self.clButton.destroy()
        del self.clButton
        del self.openScSfx
        del self.magicWordSfx
        self.whisperFrame.destroy()
        del self.whisperFrame
        self.whisperButton.destroy()
        del self.whisperButton
        self.whisperScButton.destroy()
        del self.whisperScButton
        self.whisperCancelButton.destroy()
        del self.whisperCancelButton
        self.chatInputWhiteList.destroy()
        del self.chatInputWhiteList

    def sendSCResistanceChatMessage(self, textId):
        messenger.send('chatUpdateSCResistance', [textId])
        self.announceSCChat()

    def sendSCSingingChatMessage(self, textId):
        messenger.send('chatUpdateSCSinging', [textId])
        self.announceSCChat()

    def sendSCSingingWhisperMessage(self, textId):
        pass

    def sendSCToontaskChatMessage(self, taskId, toNpcId, toonProgress, msgIndex):
        messenger.send('chatUpdateSCToontask', [taskId,
         toNpcId,
         toonProgress,
         msgIndex])
        self.announceSCChat()

    def sendSCToontaskWhisperMessage(self, taskId, toNpcId, toonProgress, msgIndex, whisperAvatarId, toPlayer):
        if toPlayer:
            base.talkAssistant.sendPlayerWhisperToonTaskSpeedChat(taskId, toNpcId, toonProgress, msgIndex, whisperAvatarId)
        else:
            messenger.send('whisperUpdateSCToontask', [taskId,
             toNpcId,
             toonProgress,
             msgIndex,
             whisperAvatarId])

    def enterOpenChatWarning(self):
        if self.openChatWarning == None:
            buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
            buttonImage = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
            self.openChatWarning = DirectFrame(parent=aspect2dp, pos=(0.0, 0.1, 0.2), relief=None, image=DGG.getDefaultDialogGeom(), image_color=OTPGlobals.GlobalDialogColor, image_scale=(1.2, 1.0, 1.4), text=OTPLocalizer.OpenChatWarning, text_wordwrap=19, text_scale=TTLocalizer.TCMopenChatWarning, text_pos=(0.0, 0.575), textMayChange=0)
            DirectButton(self.openChatWarning, image=buttonImage, relief=None, text=OTPLocalizer.OpenChatWarningOK, text_scale=0.05, text_pos=(0.0, -0.1), textMayChange=0, pos=(0.0, 0.0, -0.55), command=self.__handleOpenChatWarningOK)
            buttons.removeNode()
        self.openChatWarning.show()
        # The replacement panel owns every visible chat control.  The classic
        # buttons stay hidden while this account warning is displayed.
        self.normalButton.hide()
        self.scButton.hide()
        self.clButton.hide()

    def enterMainMenu(self):
        # The three classic Altis buttons are retained only as hidden
        # compatibility objects for quests and older code.  The visible
        # interface is the Clash-style ChatLog replacement.
        self.normalButton.hide()
        self.scButton.hide()
        self.clButton.hide()
        self.whisperFrame.hide()
        self.chatInputNormal.deactivate()
        self.chatInputNormal.chatEntry['backgroundFocus'] = 0
        chatLog = self.__getChatLog()
        if chatLog:
            normal, speedChat, chatLogObscured = self.isObscured()
            chatLog.setObscured(normal, speedChat, chatLogObscured)

    def exitMainMenu(self):
        self.normalButton.hide()
        self.scButton.hide()
        self.clButton.hide()
        self.ignore('enterNormalChat')
        self.chatInputNormal.chatEntry['backgroundFocus'] = 0

    def enterOff(self):
        self.normalButton.hide()
        self.scButton.hide()
        self.clButton.hide()
        self.whisperFrame.hide()
        self.ignoreAll()
        chatLog = self.__getChatLog()
        if chatLog:
            chatLog.disableInterface()

    def obscure(self, normal, sc, cl=False):
        ChatManager.ChatManager.obscure(self, normal, sc, cl)
        chatLog = self.__getChatLog()
        if chatLog:
            normalState, speedChatState, chatLogState = self.isObscured()
            chatLog.setObscured(normalState, speedChatState, chatLogState)

    def __getChatLog(self):
        if hasattr(base, 'localAvatar') and base.localAvatar:
            chatLog = getattr(base.localAvatar, 'chatLog', None)
            if chatLog:
                return chatLog
        return getattr(base.cr, 'chatLog', None)

    def exitOpenChatWarning(self):
        self.openChatWarning.hide()
        self.scButton.hide()
        self.clButton.hide()

    def enterUnpaidChatWarning(self):
        self.forceHidePayButton = False
        if base.cr.productName in ['DisneyOnline-UK',
         'JP',
         'DE',
         'BR',
         'FR']:
            directFrameText = OTPLocalizer.PaidParentPasswordUKWarning
            payButtonText = OTPLocalizer.PaidParentPasswordUKWarningSet
            directButtonText = OTPLocalizer.PaidParentPasswordUKWarningContinue
        else:
            directFrameText = OTPLocalizer.PaidNoParentPasswordWarning
            payButtonText = OTPLocalizer.PaidNoParentPasswordWarningSet
            directButtonText = OTPLocalizer.PaidNoParentPasswordWarningContinue
            if 'QuickLauncher' not in str(base.cr.launcher.__class__) and not base.cr.isPaid():
                directFrameText = OTPLocalizer.UnpaidNoParentPasswordWarning
                self.forceHidePayButton = True
        if self.unpaidChatWarning == None:
            guiButton = loader.loadModel('phase_3/models/gui/quit_button')
            buttonImage = (guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR'))
            self.unpaidChatWarning = DirectFrame(parent=aspect2dp, pos=(0.0, 0.1, 0.4), relief=None, image=DGG.getDefaultDialogGeom(), image_color=OTPGlobals.GlobalDialogColor, image_scale=(1.2, 1.0, 0.8), text=directFrameText, text_wordwrap=TTLocalizer.TCMunpaidChatWarningWordwrap, text_scale=TTLocalizer.TCMunpaidChatWarning, text_pos=TTLocalizer.TCMunpaidChatWarningPos, textMayChange=0)
            self.payButton = DirectButton(self.unpaidChatWarning, image=buttonImage, relief=None, text=payButtonText, image_scale=(1.75, 1, 1.15), text_scale=TTLocalizer.TCMpayButton, text_pos=(0, -0.02), textMayChange=0, pos=TTLocalizer.TCMpayButtonPos, command=self.__handleUnpaidChatWarningPay)
            DirectButton(self.unpaidChatWarning, image=buttonImage, relief=None, text=directButtonText, textMayChange=0, image_scale=(1.75, 1, 1.15), text_scale=0.06, text_pos=(0, -0.02), pos=TTLocalizer.TCMdirectButtonTextPos, command=self.__handleUnpaidChatWarningContinue)
            guiButton.removeNode()
        if base.localAvatar.cantLeaveGame or self.forceHidePayButton:
            self.payButton.hide()
        else:
            self.payButton.show()
        if base.cr.productName not in ['ES',
         'JP',
         'DE',
         'BR',
         'FR']:
            self.unpaidChatWarning.show()
        else:
            place = base.cr.playGame.getPlace()
            if place:
                place.fsm.request('stopped')
            self.teaser = TeaserPanel.TeaserPanel('secretChat', self.__handleUnpaidChatWarningDone)
            if base.localAvatar.inTutorial:
                self.teaser.hidePay()
        # Keep the replacement chat as the only visible chat interface.
        self.normalButton.hide()
        self.scButton.hide()
        self.clButton.hide()

    def exitUnpaidChatWarning(self):
        if self.unpaidChatWarning:
            self.unpaidChatWarning.hide()
        self.scButton.hide()
        self.clButton.hide()

    def enterNoSecretChatAtAll(self):
        if self.noSecretChatAtAll == None:
            buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
            okButtonImage = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
            self.noSecretChatAtAll = DirectFrame(parent=aspect2dp, pos=(0.0, 0.1, 0.2), relief=None, image=DGG.getDefaultDialogGeom(), image_color=OTPGlobals.GlobalDialogColor, image_scale=(1.4, 1.0, 1.1), text=OTPLocalizer.NoSecretChatAtAll, text_wordwrap=20, textMayChange=0, text_scale=0.06, text_pos=(0, 0.3))
            DirectLabel(parent=self.noSecretChatAtAll, relief=None, pos=(0, 0, 0.4), text=OTPLocalizer.NoSecretChatAtAllTitle, textMayChange=0, text_scale=0.08)
            DirectButton(self.noSecretChatAtAll, image=okButtonImage, relief=None, text=OTPLocalizer.NoSecretChatAtAllOK, text_scale=0.05, text_pos=(0.0, -0.1), textMayChange=0, pos=(0.0, 0.0, -0.4), command=self.__handleNoSecretChatAtAllOK)
            buttons.removeNode()
        self.noSecretChatAtAll.show()
        return

    def exitNoSecretChatAtAll(self):
        self.noSecretChatAtAll.hide()

    def enterNoSecretChatWarning(self, passwordOnly = 0):
        if not passwordOnly:
            warningText = OTPLocalizer.NoSecretChatWarning
        else:
            warningText = OTPLocalizer.ChangeSecretFriendsOptionsWarning
        if self.noSecretChatWarning == None:
            buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
            nameBalloon = loader.loadModel('phase_3/models/props/chatbox_input')
            okButtonImage = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
            cancelButtonImage = (buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'), buttons.find('**/CloseBtn_Rllvr'))
            if base.cr.productName != 'Terra-DMC':
                okPos = (-0.22, 0.0, -0.35)
                textPos = (0, 0.25)
                okCommand = self.__handleNoSecretChatWarningOK
            else:
                self.passwordEntry = None
                okPos = (0, 0, -0.35)
                textPos = (0, 0.125)
                okCommand = self.__handleNoSecretChatWarningCancel
            self.noSecretChatWarning = DirectFrame(parent=aspect2dp, pos=(0.0, 0.1, 0.2), relief=None, image=DGG.getDefaultDialogGeom(), image_color=OTPGlobals.GlobalDialogColor, image_scale=(1.4, 1.0, 1.0), text=warningText, text_wordwrap=20, text_scale=0.055, text_pos=textPos, textMayChange=1)
            DirectButton(self.noSecretChatWarning, image=okButtonImage, relief=None, text=OTPLocalizer.NoSecretChatWarningOK, text_scale=0.05, text_pos=(0.0, -0.1), textMayChange=0, pos=okPos, command=okCommand)
            DirectLabel(parent=self.noSecretChatWarning, relief=None, pos=(0, 0, 0.35), text=OTPLocalizer.NoSecretChatWarningTitle, textMayChange=0, text_scale=0.08)
            if base.cr.productName != 'Terra-DMC':
                self.passwordLabel = DirectLabel(parent=self.noSecretChatWarning, relief=None, pos=(-0.07, 0.0, -0.2), text=OTPLocalizer.ParentPassword, text_scale=0.06, text_align=TextNode.ARight, textMayChange=0)
                self.passwordEntry = DirectEntry(parent=self.noSecretChatWarning, relief=None, image=nameBalloon, image1_color=(0.8, 0.8, 0.8, 1.0), scale=0.064, pos=(0.0, 0.0, -0.2), width=OTPGlobals.maxLoginWidth, numLines=1, focus=1, cursorKeys=1, obscured=1, command=self.__handleNoSecretChatWarningOK)
                DirectButton(self.noSecretChatWarning, image=cancelButtonImage, relief=None, text=OTPLocalizer.NoSecretChatWarningCancel, text_scale=0.05, text_pos=(0.0, -0.1), textMayChange=1, pos=(0.2, 0.0, -0.35), command=self.__handleNoSecretChatWarningCancel)
            buttons.removeNode()
            nameBalloon.removeNode()
        else:
            self.noSecretChatWarning['text'] = warningText
            if self.passwordEntry:
                self.passwordEntry['focus'] = 1
                self.passwordEntry.enterText('')
        self.noSecretChatWarning.show()

    def exitNoSecretChatWarning(self):
        self.noSecretChatWarning.hide()

    def enterActivateChat(self):
        if self.activateChatGui == None:
            guiButton = loader.loadModel('phase_3/models/gui/quit_button')
            buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
            okButtonImage = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
            cancelButtonImage = (buttons.find('**/CloseBtn_UP'), buttons.find('**/CloseBtn_DN'), buttons.find('**/CloseBtn_Rllvr'))
            moreButtonImage = (guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR'))
            nameShopGui = loader.loadModel('phase_3/models/gui/nameshop_gui')
            circle = nameShopGui.find('**/namePanelCircle')
            self.activateChatGui = DirectFrame(parent=aspect2dp, pos=(0.0, 0.1, 0.2), relief=None, image=DGG.getDefaultDialogGeom(), image_color=OTPGlobals.GlobalDialogColor, image_scale=(1.8, 1.0, 1.6), text=OTPLocalizer.ActivateChat, text_align=TextNode.ALeft, text_wordwrap=33, text_scale=TTLocalizer.TCMactivateChatGui, text_pos=(-0.82, 0.58), textMayChange=0)
            innerCircle = circle.copyTo(hidden)
            innerCircle.setPos(0, 0, 0.2)
            self.c1b = circle.copyTo(self.activateChatGui, -1)
            self.c1b.setColor(0, 0, 0, 1)
            self.c1b.setPos(-0.8, 0, 0.29)
            self.c1b.setScale(0.4)
            c1f = circle.copyTo(self.c1b)
            c1f.setColor(1, 1, 1, 1)
            c1f.setScale(0.8)
            self.c2b = circle.copyTo(self.activateChatGui, -2)
            self.c2b.setColor(0, 0, 0, 1)
            self.c2b.setPos(-0.8, 0, 0.14)
            self.c2b.setScale(0.4)
            c2f = circle.copyTo(self.c2b)
            c2f.setColor(1, 1, 1, 1)
            c2f.setScale(0.8)
            self.c3b = circle.copyTo(self.activateChatGui, -2)
            self.c3b.setColor(0, 0, 0, 1)
            self.c3b.setPos(-0.8, 0, -0.01)
            self.c3b.setScale(0.4)
            c3f = circle.copyTo(self.c3b)
            c3f.setColor(1, 1, 1, 1)
            c3f.setScale(0.8)
            DirectLabel(self.activateChatGui, relief=None, text=OTPLocalizer.ActivateChatTitle, text_align=TextNode.ACenter, text_scale=0.07, text_pos=(0, 0.7), textMayChange=0)
            if base.cr.productName != 'JP':
                DirectButton(self.activateChatGui, image=moreButtonImage, image_scale=(1.25, 1.0, 1.0), relief=None, text=OTPLocalizer.ActivateChatMoreInfo, text_scale=0.06, text_pos=(0, -0.02), textMayChange=0, pos=(0.0, 0.0, -0.7), command=self.__handleActivateChatMoreInfo)
            self.dcb1 = HackedDirectRadioButton(parent=self.activateChatGui, relief=None, scale=0.1, boxImage=innerCircle, boxImageScale=2.5, boxImageColor=VBase4(0, 0.25, 0.5, 1), boxRelief=None, pos=(-0.745, 0, 0.297), command=self.__updateCheckBoxen, extraArgs=[1])
            self.dcb2 = HackedDirectRadioButton(parent=self.activateChatGui, relief=None, scale=0.1, boxImage=innerCircle, boxImageScale=2.5, boxImageColor=VBase4(0, 0.25, 0.5, 1), boxRelief=None, pos=(-0.745, 0, 0.147), command=self.__updateCheckBoxen, extraArgs=[2])
            self.dcb3 = HackedDirectRadioButton(parent=self.activateChatGui, relief=None, scale=0.1, boxImage=innerCircle, boxImageScale=2.5, boxImageColor=VBase4(0, 0.25, 0.5, 1), boxRelief=None, pos=(-0.745, 0, -0.003), command=self.__updateCheckBoxen, extraArgs=[3])
            DirectButton(self.activateChatGui, image=okButtonImage, relief=None, text=OTPLocalizer.ActivateChatYes, text_scale=0.05, text_pos=(0.0, -0.1), textMayChange=0, pos=(-0.35, 0.0, -0.27), command=self.__handleActivateChatYes)
            DirectButton(self.activateChatGui, image=cancelButtonImage, relief=None, text=OTPLocalizer.ActivateChatNo, text_scale=0.05, text_pos=(0.0, -0.1), textMayChange=0, pos=(0.35, 0.0, -0.27), command=self.__handleActivateChatNo)
            guiButton.removeNode()
            buttons.removeNode()
            nameShopGui.removeNode()
            innerCircle.removeNode()
        self.__initializeCheckBoxen()
        self.activateChatGui.show()

    def __initializeCheckBoxen(self):
        if base.cr.secretChatAllowed and not base.cr.secretChatNeedsParentPassword:
            self.dcb1['indicatorValue'] = 0
            self.dcb2['indicatorValue'] = 0
            self.dcb3['indicatorValue'] = 1
        elif base.cr.secretChatAllowed and base.cr.secretChatNeedsParentPassword:
            self.dcb1['indicatorValue'] = 0
            self.dcb2['indicatorValue'] = 1
            self.dcb3['indicatorValue'] = 0
        else:
            self.dcb1['indicatorValue'] = 1
            self.dcb2['indicatorValue'] = 0
            self.dcb3['indicatorValue'] = 0

    def __updateCheckBoxen(self, value, checkBox):
        if value == 0:
            return
        if checkBox == 1:
            self.dcb2['indicatorValue'] = 0
            self.dcb3['indicatorValue'] = 0
        elif checkBox == 2:
            self.dcb1['indicatorValue'] = 0
            self.dcb3['indicatorValue'] = 0
        else:
            self.dcb1['indicatorValue'] = 0
            self.dcb2['indicatorValue'] = 0

    def exitActivateChat(self):
        self.activateChatGui.hide()

    def enterSecretChatActivated(self, mode = 2):
        if mode == 0:
            modeText = OTPLocalizer.SecretChatDeactivated
        elif mode == 1:
            modeText = OTPLocalizer.RestrictedSecretChatActivated
        else:
            modeText = OTPLocalizer.SecretChatActivated
        if self.secretChatActivated == None:
            guiButton = loader.loadModel('phase_3/models/gui/quit_button')
            optionsButtonImage = (guiButton.find('**/QuitBtn_UP'), guiButton.find('**/QuitBtn_DN'), guiButton.find('**/QuitBtn_RLVR'))
            buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
            buttonImage = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
            self.secretChatActivated = DirectFrame(parent=aspect2dp, pos=(0.0, 0.1, 0.4), relief=None, image=DGG.getDefaultDialogGeom(), image_color=OTPGlobals.GlobalDialogColor, image_scale=(1.0, 1.0, 0.8), text=modeText, text_align=TextNode.ACenter, text_wordwrap=14, text_scale=TTLocalizer.TCMsecretChatActivated, text_pos=(0, 0.25))
            DirectButton(self.secretChatActivated, image=buttonImage, relief=None, text=OTPLocalizer.SecretChatActivatedOK, text_scale=0.05, text_pos=(0.0, -0.1), textMayChange=0, pos=(0.0, 0.0, -0.1), command=self.__handleSecretChatActivatedOK)
            buttons.removeNode()
            guiButton.removeNode()
        else:
            self.secretChatActivated['text'] = modeText
        self.secretChatActivated.show()

    def exitSecretChatActivated(self):
        self.secretChatActivated.hide()

    def enterProblemActivatingChat(self):
        if self.problemActivatingChat == None:
            buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
            buttonImage = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
            self.problemActivatingChat = DirectFrame(parent=aspect2dp, pos=(0.0, 0.1, 0.4), relief=None, image=DGG.getDefaultDialogGeom(), image_color=OTPGlobals.GlobalDialogColor, image_scale=(1.2, 1.0, 0.9), text='', text_align=TextNode.ALeft, text_wordwrap=18, text_scale=0.06, text_pos=(-0.5, 0.28), textMayChange=1)
            DirectButton(self.problemActivatingChat, image=buttonImage, relief=None, text=OTPLocalizer.ProblemActivatingChatOK, text_scale=0.05, text_pos=(0.0, -0.1), textMayChange=0, pos=(0.0, 0.0, -0.28), command=self.__handleProblemActivatingChatOK)
            buttons.removeNode()
        self.problemActivatingChat.show()

    def exitProblemActivatingChat(self):
        self.problemActivatingChat.hide()

    def __normalButtonPressed(self):
        messenger.send('wakeup')
        chatLog = self.__getChatLog()
        if chatLog:
            chatLog.open(focus=True)

    def __scButtonPressed(self):
        if base.config.GetBool('want-qa-regression', 0):
            self.notify.info('QA-REGRESSION: CHAT: Speedchat')
        messenger.send('wakeup')
        if self.fsm.getCurrentState().getName() == 'speedChat':
            self.fsm.request('mainMenu')
        else:
            self.fsm.request('speedChat')

    def whisperTo(self, avatarName, avatarId, playerId=None):
        messenger.send('wakeup')
        chatLog = self.__getChatLog()
        if chatLog:
            chatLog.setWhisperTarget(avatarName, avatarId, playerId or 0)
            return
        ChatManager.ChatManager.whisperTo(self, avatarName, avatarId, playerId)

    def noWhisper(self):
        chatLog = self.__getChatLog()
        if chatLog:
            chatLog.clearWhisperTarget()
        if self.fsm.getCurrentState().getName() != 'mainMenu':
            self.fsm.request('mainMenu')

    def __whisperButtonPressed(self, avatarName, avatarId, playerId):
        messenger.send('wakeup')
        if playerId:
            playerInfo = base.cr.playerFriendsManager.getFriendInfo(playerId)
        if avatarId:
            self.enterWhisperChat(avatarName, avatarId)
        self.whisperFrame.hide()
        return
		
    def __clButtonPressed(self):
        if base.localAvatar.chatLog:
            base.localAvatar.chatLog.toggle()

    def __getNamedMagicWordTargets(self):
        targets = []
        seen = set()
        try:
            from toontown.toon.DistributedToon import DistributedToon
            try:
                objects = base.cr.getObjectsOfExactClass(DistributedToon)
                try:
                    iterator = objects.itervalues()
                except:
                    iterator = objects.values()
            except:
                try:
                    iterator = base.cr.doId2do.itervalues()
                except:
                    iterator = base.cr.doId2do.values()

            for toon in iterator:
                if toon is None or toon is getattr(base, 'localAvatar', None):
                    continue
                if toon.__class__ is not DistributedToon:
                    continue
                try:
                    doId = toon.getDoId()
                except:
                    doId = getattr(toon, 'doId', 0)
                if not doId or doId in seen:
                    continue
                try:
                    name = toon.getName().strip()
                except:
                    name = ''
                if not name:
                    continue
                seen.add(doId)
                targets.append((name, toon))
        except:
            pass
        targets.sort(key=lambda item: len(item[0]), reverse=True)
        return targets

    def __extractNamedMagicWordTarget(self, commandText):
        splitCommand = commandText.split(None, 1)
        if len(splitCommand) < 2:
            return (None, commandText)

        invokeWord = splitCommand[0]
        enteredArguments = splitCommand[1].lstrip()
        if not enteredArguments:
            return (None, commandText)

        targetToon = None
        remainingArguments = ''
        loweredArguments = enteredArguments.lower()

        for name, toon in self.__getNamedMagicWordTargets():
            loweredName = name.lower()
            if loweredArguments == loweredName:
                targetToon = toon
                remainingArguments = ''
                break
            if (loweredArguments.startswith(loweredName) and
                    len(enteredArguments) > len(name) and
                    enteredArguments[len(name)].isspace()):
                targetToon = toon
                remainingArguments = enteredArguments[len(name):].lstrip()
                break

        if targetToon is None:
            return (None, commandText)

        strippedCommand = invokeWord
        if remainingArguments:
            strippedCommand += ' ' + remainingArguments
        return (targetToon, strippedCommand)

    def __sendNamedTargetMagicWord(self, targetToon, targetPrefix, commandText):
        try:
            from otp.ai import MagicWordManager as MagicWordManagerModule
            previousTarget = getattr(MagicWordManagerModule, 'lastClickedNametag', None)
            MagicWordManagerModule.lastClickedNametag = targetToon
            try:
                base.talkAssistant.sendOpenTalk(targetPrefix + commandText)
            finally:
                MagicWordManagerModule.lastClickedNametag = previousTarget
        except:
            oldPrefix = getattr(ToontownGlobals, 'MagicWordInvokerPrefix', '~')
            base.talkAssistant.sendOpenTalk(oldPrefix + commandText)

    def __addShortcutError(self, chatLog, message):
        if chatLog:
            chatLog.addToLog('\1playerGreen\1System Message\2: ' + message, category=chatLog.TAB_ALERTS)

    def __handleClashLocalShortcut(self, commandText, targetToon, chatLog):
        pieces = commandText.split(None, 1)
        if not pieces:
            return None
        command = pieces[0].lower()
        arguments = pieces[1].strip() if len(pieces) > 1 else ''

        if command == 'friend':
            if targetToon is None:
                self.__addShortcutError(chatLog, 'Choose a nearby Toon: /friend ToonName')
                return False
            try:
                name = targetToon.getName()
                messenger.send('friendAvatar', [targetToon.doId, name, name])
                return True
            except:
                self.__addShortcutError(chatLog, 'That Toon is no longer nearby.')
                return False

        if command == 'ftp':
            if targetToon is None:
                self.__addShortcutError(chatLog, 'Choose a nearby Toon: /ftp ToonName')
                return False
            if not base.localAvatar.isTeleportAllowed():
                self.__addShortcutError(chatLog, 'Teleporting is not available right now.')
                return False
            try:
                name = targetToon.getName()
                messenger.send('gotoAvatar', [targetToon.doId, name, name])
                return True
            except:
                self.__addShortcutError(chatLog, 'That Toon is no longer nearby.')
                return False

        if command == 'whisper':
            if targetToon is None:
                self.__addShortcutError(chatLog, 'Choose a nearby Toon: /whisper ToonName message')
                return False
            if not arguments:
                self.__addShortcutError(chatLog, 'Enter a message after the Toon name.')
                return False
            try:
                check = getattr(base.talkAssistant, 'checkWhisperTypedChatAvatar', None)
                if check and not check(targetToon.doId):
                    self.__addShortcutError(chatLog, 'Typed whispers are not available for that Toon.')
                    return False
                base.talkAssistant.sendWhisperTalk(arguments, targetToon.doId)
                return True
            except:
                self.__addShortcutError(chatLog, 'That Toon is no longer nearby.')
                return False

        if command == 'reply':
            if targetToon is not None:
                self.__addShortcutError(chatLog, '/reply does not use a Toon target.')
                return False
            if not arguments:
                self.__addShortcutError(chatLog, 'Enter a message after /reply.')
                return False
            try:
                replyId, toPlayer = base.talkAssistant.getWhisperReplyId()
            except:
                replyId, toPlayer = (0, 0)
            if not replyId:
                self.__addShortcutError(chatLog, 'There is no whisper to reply to.')
                return False
            try:
                if toPlayer:
                    check = getattr(base.talkAssistant, 'checkWhisperTypedChatPlayer', None)
                    if check and not check(replyId):
                        self.__addShortcutError(chatLog, 'Typed replies are not available for that player.')
                        return False
                    base.talkAssistant.sendAccountTalk(arguments, replyId)
                else:
                    check = getattr(base.talkAssistant, 'checkWhisperTypedChatAvatar', None)
                    if check and not check(replyId):
                        self.__addShortcutError(chatLog, 'Typed replies are not available for that Toon.')
                        return False
                    base.talkAssistant.sendWhisperTalk(arguments, replyId)
                return True
            except:
                self.__addShortcutError(chatLog, 'The previous whisper target is no longer available.')
                return False

        if command == 'emote':
            if targetToon is not None:
                self.__addShortcutError(chatLog, '/emote does not use a Toon target.')
                return False
            try:
                emoteId = int(arguments)
            except:
                self.__addShortcutError(chatLog, 'Use /emote followed by an emote ID.')
                return False
            try:
                self.sendSCEmoteChatMessage(emoteId)
                return True
            except:
                self.__addShortcutError(chatLog, 'That emote is not available.')
                return False

        return None

    def sendPanelMessage(self, message):
        message = message.strip()
        if not message:
            return False
        message = message[:100]
        chatLog = self.__getChatLog()
        targetName = None
        targetAvatarId = 0
        targetPlayerId = 0
        activeTab = None
        if chatLog:
            targetName, targetAvatarId, targetPlayerId = chatLog.getWhisperTarget()
            activeTab = chatLog.currentTab

        oldPrefix = getattr(ToontownGlobals, 'MagicWordInvokerPrefix', '~')
        targetPrefix = getattr(ToontownGlobals, 'MagicWordTargetPrefix', '~~')
        if message.startswith('/'):
            try:
                base.playSfx(self.magicWordSfx)
            except:
                try:
                    self.magicWordSfx.play()
                except:
                    pass
        if message.startswith(oldPrefix):
            if chatLog:
                chatLog.addToLog('\1playerGreen\1System Message\2: Use /command instead of ~command.', category=chatLog.TAB_ALERTS)
            return False
        elif message.startswith('//'):
            if chatLog:
                chatLog.addToLog('\1playerGreen\1System Message\2: Use /command ToonName instead of //command.', category=chatLog.TAB_ALERTS)
            return False
        elif message.startswith('/'):
            commandText = message[1:].strip()
            if not commandText:
                if chatLog:
                    chatLog.addToLog('\1playerGreen\1System Message\2: Select a command before sending it.', category=chatLog.TAB_ALERTS)
                return False
            commandText = translateCommandText(commandText)
            targetToon, translatedCommand = self.__extractNamedMagicWordTarget(commandText)
            handled = self.__handleClashLocalShortcut(translatedCommand, targetToon, chatLog)
            if handled is False:
                return False
            if handled is None:
                if targetToon is not None:
                    self.__sendNamedTargetMagicWord(targetToon, targetPrefix, translatedCommand)
                else:
                    base.talkAssistant.sendOpenTalk(oldPrefix + translatedCommand)
        elif chatLog and activeTab == chatLog.TAB_WHISPERS and targetAvatarId:
            check = getattr(base.talkAssistant, 'checkWhisperTypedChatAvatar', None)
            if check and not check(targetAvatarId):
                chatLog.addToLog('\1playerGreen\1System Message\2: Typed whispers are not available for that Toon.', category=chatLog.TAB_ALERTS)
                return False
            base.talkAssistant.sendWhisperTalk(message, targetAvatarId)
        elif chatLog and activeTab == chatLog.TAB_WHISPERS and targetPlayerId:
            check = getattr(base.talkAssistant, 'checkWhisperTypedChatPlayer', None)
            if check and not check(targetPlayerId):
                chatLog.addToLog('\1playerGreen\1System Message\2: Typed whispers are not available for that player.', category=chatLog.TAB_ALERTS)
                return False
            base.talkAssistant.sendAccountTalk(message, targetPlayerId)
        elif chatLog and activeTab == chatLog.TAB_CLUBS:
            check = getattr(base.talkAssistant, 'checkGuildTypedChat', None)
            if check and not check():
                chatLog.addToLog('\1playerGreen\1System Message\2: You are not in a Club.', category=chatLog.TAB_ALERTS)
                return False
            error = base.talkAssistant.sendGuildTalk(message)
            if error:
                chatLog.addToLog('\1playerGreen\1System Message\2: Club chat is not available.', category=chatLog.TAB_ALERTS)
                return False
        else:
            check = getattr(base.talkAssistant, 'checkAnyTypedChat', None)
            if check and not check():
                if chatLog:
                    chatLog.addToLog('\1playerGreen\1System Message\2: Typed chat is not available.', category=chatLog.TAB_ALERTS)
                return False
            base.talkAssistant.sendOpenTalk(message)

        messenger.send('sentRegularChat')
        self.messageSent()
        return True

    def openPanelSpeedChat(self):
        messenger.send('wakeup')
        self.chatInputUnites.hide()
        chatLog = self.__getChatLog()
        targetName = None
        targetAvatarId = 0
        targetPlayerId = 0
        activeTab = None
        if chatLog:
            targetName, targetAvatarId, targetPlayerId = chatLog.getWhisperTarget()
            activeTab = chatLog.currentTab
        stateName = self.fsm.getCurrentState().getName()
        if chatLog and activeTab == chatLog.TAB_WHISPERS and targetAvatarId:
            self.panelClubSpeedChat = False
            if stateName == 'whisperSpeedChat':
                self.fsm.request('mainMenu')
            else:
                self.fsm.request('whisperSpeedChat', [targetAvatarId])
        elif chatLog and activeTab == chatLog.TAB_WHISPERS and targetPlayerId:
            self.panelClubSpeedChat = False
            if stateName == 'whisperSpeedChatPlayer':
                self.fsm.request('mainMenu')
            else:
                self.fsm.request('whisperSpeedChatPlayer', [targetPlayerId])
        elif chatLog and activeTab == chatLog.TAB_CLUBS:
            if stateName == 'speedChat' and self.panelClubSpeedChat:
                self.fsm.request('mainMenu')
            else:
                if stateName == 'speedChat':
                    self.fsm.request('mainMenu')
                self.panelClubSpeedChat = True
                self.fsm.request('speedChat')
        elif stateName == 'speedChat':
            self.fsm.request('mainMenu')
        else:
            self.panelClubSpeedChat = False
            self.fsm.request('speedChat')

    def openPanelUnites(self):
        messenger.send('wakeup')
        stateName = self.fsm.getCurrentState().getName()
        if stateName in ('speedChat', 'whisperSpeedChat', 'whisperSpeedChatPlayer'):
            self.fsm.request('mainMenu')
        self.chatInputUnites.show()

    def closePanelMenus(self):
        self.chatInputUnites.hide()
        stateName = self.fsm.getCurrentState().getName()
        if stateName in ('speedChat', 'whisperSpeedChat', 'whisperSpeedChatPlayer'):
            self.fsm.request('mainMenu')

    def enterSpeedChat(self):
        messenger.send('enterSpeedChat')
        self.normalButton.hide()
        self.scButton.hide()
        self.clButton.hide()
        self.whisperFrame.hide()
        self.chatInputNormal.chatEntry['backgroundFocus'] = 0
        self.chatInputSpeedChat.show(guildMode=self.panelClubSpeedChat)

    def exitSpeedChat(self):
        self.chatInputSpeedChat.hide()
        self.panelClubSpeedChat = False
        self.normalButton.hide()
        self.scButton.hide()
        self.clButton.hide()

    def enterWhisperSpeedChat(self, avatarId):
        self.whisperFrame.hide()
        self.chatInputNormal.chatEntry['backgroundFocus'] = 0
        self.chatInputSpeedChat.show(avatarId)

    def exitWhisperSpeedChat(self):
        self.whisperFrame.hide()
        self.chatInputSpeedChat.hide()

    def enterWhisperSpeedChatPlayer(self, playerId):
        self.whisperFrame.hide()
        self.chatInputNormal.chatEntry['backgroundFocus'] = 0
        self.chatInputSpeedChat.show(playerId, 1)

    def exitWhisperSpeedChatPlayer(self):
        self.whisperFrame.hide()
        self.chatInputSpeedChat.hide()

    def enterNormalChat(self):
        chatLog = self.__getChatLog()
        if chatLog:
            chatLog.open(focus=True)
        return 1

    def exitNormalChat(self):
        return

    def enterWhisperChatPlayer(self, avatarName, playerId):
        chatLog = self.__getChatLog()
        if chatLog:
            chatLog.setWhisperTarget(avatarName, 0, playerId)
        return 1

    def exitWhisperChatPlayer(self):
        return

    def enterWhisperChat(self, avatarName, avatarId):
        chatLog = self.__getChatLog()
        if chatLog:
            chatLog.setWhisperTarget(avatarName, avatarId, 0)
        return 1

    def exitWhisperChat(self):
        return

    def enterNoSecretChatAtAllAndNoWhitelist(self):
        if self.noSecretChatAtAllAndNoWhitelist == None:
            buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
            okButtonImage = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
            self.noSecretChatAtAllAndNoWhitelist = DirectFrame(parent=aspect2dp, pos=(0.0, 0.1, 0.05), relief=None, image=DGG.getDefaultDialogGeom(), image_color=OTPGlobals.GlobalDialogColor, image_scale=(1.4, 1.0, 1.58), text=OTPLocalizer.NoSecretChatAtAllAndNoWhitelist, text_wordwrap=20, textMayChange=0, text_scale=0.06, text_pos=(0, 0.55))
            DirectLabel(parent=self.noSecretChatAtAllAndNoWhitelist, relief=None, pos=(0, 0, 0.67), text=OTPLocalizer.NoSecretChatAtAllAndNoWhitelistTitle, textMayChange=0, text_scale=0.08)
            DirectButton(self.noSecretChatAtAllAndNoWhitelist, image=okButtonImage, relief=None, text=OTPLocalizer.NoSecretChatAtAllOK, text_scale=0.05, text_pos=(0.0, -0.1), textMayChange=0, pos=(0.0, 0.0, -0.64), command=self.__handleNoSecretChatAtAllOK)
            buttons.removeNode()
        self.noSecretChatAtAllAndNoWhitelist.show()
        return

    def exitNoSecretChatAtAllAndNoWhitelist(self):
        self.noSecretChatAtAllAndNoWhitelist.hide()

    def enterTrueFriendTeaserPanel(self):
        self.previousStateBeforeTeaser = None
        place = base.cr.playGame.getPlace()
        if place:
            if place.fsm.hasStateNamed('stopped'):
                self.previousStateBeforeTeaser = place.fsm.getCurrentState().getName()
                place.fsm.request('stopped')
            else:
                self.notify.warning("Enter: %s has no 'stopped' state." % place)
        self.teaser = TeaserPanel.TeaserPanel(pageName='secretChat', doneFunc=self.handleOkTeaser)
        return

    def exitTrueFriendTeaserPanel(self):
        self.teaser.destroy()
        place = base.cr.playGame.getPlace()
        if place:
            if place.fsm.hasStateNamed('stopped'):
                if self.previousStateBeforeTeaser:
                    place.fsm.request(self.previousStateBeforeTeaser, force=1)
                else:
                    place.fsm.request('walk')
            else:
                self.notify.warning("Exit: %s has no 'stopped' state." % place)

    def handleOkTeaser(self):
        self.fsm.request('mainMenu')

    def __whisperScButtonPressed(self, avatarName, avatarId, playerId):
        if base.config.GetBool('want-qa-regression', 0):
            self.notify.info('QA-REGRESSION: CHAT: Whisper')
        messenger.send('wakeup')
        hasManager = hasattr(base.cr, 'playerFriendsManager')
        transientFriend = 0
        if hasManager:
            transientFriend = base.cr.playerFriendsManager.askTransientFriend(avatarId)
            if transientFriend:
                playerId = base.cr.playerFriendsManager.findPlayerIdFromAvId(avatarId)
        if avatarId and not transientFriend:
            if self.fsm.getCurrentState().getName() == 'whisperSpeedChat':
                self.fsm.request('whisper', [avatarName, avatarId, playerId])
            else:
                self.fsm.request('whisperSpeedChat', [avatarId])
        elif playerId:
            if self.fsm.getCurrentState().getName() == 'whisperSpeedChatPlayer':
                self.fsm.request('whisper', [avatarName, avatarId, playerId])
            else:
                self.fsm.request('whisperSpeedChatPlayer', [playerId])
        # Do more work here for position of SCWhisperpos

    def __whisperCancelPressed(self):
        self.fsm.request('mainMenu')

    def __handleOpenChatWarningOK(self):
        self.fsm.request('mainMenu')

    def __handleUnpaidChatWarningDone(self):
        place = base.cr.playGame.getPlace()
        if place:
            place.handleBookClose()
        self.fsm.request('mainMenu')

    def __handleUnpaidChatWarningContinue(self):
        self.fsm.request('mainMenu')

    def __handleUnpaidChatWarningPay(self):
        if base.cr.isWebPlayToken():
            self.fsm.request('leaveToPayDialog')
        else:
            self.fsm.request('mainMenu')

    def __handleNoSecretChatAtAllOK(self):
        self.fsm.request('mainMenu')

    def __handleNoSecretChatWarningOK(self, *args):
        password = self.passwordEntry.get()
        tt = base.cr.loginInterface
        okflag, message = tt.authenticateParentPassword(base.cr.userName, base.cr.password, password)
        if okflag:
            self.fsm.request('activateChat')
        elif message:
            self.fsm.request('problemActivatingChat')
            self.problemActivatingChat['text'] = OTPLocalizer.ProblemActivatingChat % message
        else:
            self.noSecretChatWarning['text'] = OTPLocalizer.NoSecretChatWarningWrongPassword
            self.passwordEntry['focus'] = 1
            self.passwordEntry.enterText('')

    def __handleNoSecretChatWarningCancel(self):
        self.fsm.request('mainMenu')

    def __handleActivateChatYes(self):
        password = self.passwordEntry.get()
        tt = base.cr.loginInterface
        if self.dcb1['indicatorValue']:
            base.cr.secretChatAllowed = 0
            mode = 0
        elif self.dcb2['indicatorValue']:
            base.cr.secretChatAllowed = 1
            base.cr.secretChatNeedsParentPassword = 1
            mode = 1
        else:
            base.cr.secretChatAllowed = 1
            base.cr.secretChatNeedsParentPassword = 0
            mode = 2
        okflag, message = tt.enableSecretFriends(base.cr.userName, base.cr.password, password)
        if okflag:
            tt.resendPlayToken()
            self.fsm.request('secretChatActivated', [mode])
        else:
            if message == None:
                message = 'Parent Password was invalid.'
            self.fsm.request('problemActivatingChat')
            self.problemActivatingChat['text'] = OTPLocalizer.ProblemActivatingChat % message
        return

    def __handleActivateChatMoreInfo(self):
        self.fsm.request('chatMoreInfo')

    def __handleActivateChatNo(self):
        self.fsm.request('mainMenu')

    def __handleSecretChatActivatedOK(self):
        self.fsm.request('mainMenu')

    def __handleSecretChatActivatedChangeOptions(self):
        self.fsm.request('activateChat')

    def __handleProblemActivatingChatOK(self):
        self.fsm.request('mainMenu')

    def messageSent(self):
        messenger.send('wakeup')

    def deactivateChat(self):
        chatLog = self.__getChatLog()
        if chatLog:
            chatLog.removeFocus()
