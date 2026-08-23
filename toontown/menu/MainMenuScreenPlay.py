from direct.task import Task
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *

from toontown.toon import ToonDNA, Toon, ToonHead, LaffMeter
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toontowngui.TTDialog import *
from toontown.toontowngui import TTDialog
from toontown.menu import MainMenuGui, MainMenuGlobals
from toontown.menu.MainMenuGui import MainMenuButton
from toontown.menu.MainMenuScreen import MainMenuScreen


class MainMenuScreenPlay(MainMenuScreen):
    def __init__(self, avatarList, parentFSM, doneEvent):
        self.toonList = dict((i, i in [x.position for x in avatarList]) for i in range(6))
        self.avatarList = avatarList
        self.selectedToon = 0
        self.prevSelectedToon = -1
        self.doneEvent = doneEvent
        self.buttonList = [None, None, None, None, None, None]
        self.buttonScales = [None, None, None, None, None, None]
        self.labelList = [None, None, None, None, None, None]
        self.deleteButtonList = [None, None, None, None, None, None]
        self.jumpIn = None
        self.afk = None
        self.confirmQuit = None
        self.ignoreHoverOut = False
        self.laffMeter = None
        self.optionsButton = None
        self.quitButton = None
        self.creditsButton = None
        self.continueButton = None
        self.changeName = None
        self.toon = None
        self.selectToonAnim = None
        self.TEXTTILT = [-8.75, -349.7, 0, -354.5, -5, -354.29]
        MainMenuScreen.__init__(self)

    def createUI(self):
        if hasattr(base, 'discord'):
            try:
                base.discord.applyPreset('pick_a_toon')
            except:
                pass

        self.title = DirectLabel(
            parent=aspect2d,
            relief=None,
            text=TTLocalizer.AvatarChooserPickAToon,
            text_font=ToontownGlobals.getSignFont(),
            text_scale=TTLocalizer.ACtitle,
            text_fg=(1, 0.9, 0.1, 1),
            pos=(0.0, 0.0, 0.82)
        )
        self.uiItems.append(self.title)

        guimodel = loader.loadModel('phase_3/models/gui/ttcc_menu_buttons')

        self.optionsButton = MainMenuButton(
            parent=base.a2dTopLeft,
            text='Options',
            pos=(.2, 0, -.1),
            command=lambda: base.cr.mainmenu.request('Options')
        )
        self.uiItems.append(self.optionsButton)

        self.quitButton = MainMenuButton(
            parent=base.a2dBottomRight,
            text=getattr(TTLocalizer, 'AvatarChooserQuit', 'Quit'),
            pos=(-.2, 0, .1),
            command=self.showQuitDialog
        )
        self.uiItems.append(self.quitButton)

        self.creditsButton = MainMenuButton(
            parent=base.a2dTopRight,
            text=getattr(TTLocalizer, 'CreditsButton', 'Credits'),
            pos=(-.2, 0, -.1),
            command=self.__handleCredits
        )
        self.uiItems.append(self.creditsButton)

        self.toon = Toon.Toon()
        self.toon.setPosHpr(0.9, 32, 4, 180, 0, 0)
        try:
            self.toon.nametag.getNametag2d().setContents(0)
        except:
            pass
        base.camera.setPosHpr(-1.5, 18, 8, 0, -3, 0)
        self.toon.reparentTo(render)

        self.continueButton = DirectButton(
            relief=None,
            image=(
                guimodel.find('**/menubtn'),
                guimodel.find('**/menubtn-press'),
                guimodel.find('**/menubtn'),
                guimodel.find('**/menubtn-press')
            ),
            image_scale=(.5, .17, .17),
            text=TTLocalizer.AvatarChoicePlayThisToon,
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_pos=(0, .006),
            text_scale=.045,
            scale=1.4,
            pos=(-0.538889, 0, 0.341667),
            parent=base.a2dBottomCenter
        )
        self.continueButton.bind(DGG.ENTER, MainMenuGui.hoverButton, [self.continueButton, 1.5])
        self.continueButton.bind(DGG.EXIT, MainMenuGui.hoverButton, [self.continueButton, 1.4])

        self.changeName = DirectButton(
            relief=None,
            image=(
                guimodel.find('**/menubtn'),
                guimodel.find('**/menubtn-press'),
                guimodel.find('**/menubtn'),
                guimodel.find('**/menubtn-press')
            ),
            image_scale=(.6, .18, .18),
            text=TTLocalizer.AvatarChoiceNameYourToon,
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(0.977, 0.816, 0.133, 1),
            text_pos=(0, -.016),
            text_scale=.045,
            scale=.8,
            pos=(0.501255, 0, -0.788618),
            command=self.__handleNameYourToon,
            parent=aspect2d
        )
        self.changeName.bind(DGG.ENTER, MainMenuGui.hoverButton, [self.changeName, .9])
        self.changeName.bind(DGG.EXIT, MainMenuGui.hoverButton, [self.changeName, .8])

        self.uiItems.append(self.continueButton)
        self.uiItems.append(self.changeName)

        pickAToonGui = loader.loadModel('phase_3/models/gui/tt_m_gui_pat_mainGui')
        self.buttonBgs = [
            pickAToonGui.find('**/tt_t_gui_pat_squareRed'),
            pickAToonGui.find('**/tt_t_gui_pat_squareGreen'),
            pickAToonGui.find('**/tt_t_gui_pat_squarePurple'),
            pickAToonGui.find('**/tt_t_gui_pat_squareBlue'),
            pickAToonGui.find('**/tt_t_gui_pat_squarePink'),
            pickAToonGui.find('**/tt_t_gui_pat_squareYellow')
        ]

        buttonIndex = []
        for av in self.avatarList:
            self.setupButtons(av, av.position)
            buttonIndex.append(av.position)
        for pos in range(6):
            if pos not in buttonIndex:
                self.setupButtons(position=pos)

        self.selectToon(0)
        MainMenuGui.staggeredFadeUp(self.uiItems)
        MainMenuGui.staggeredFadePopin(self.buttonList, self.buttonScales)

        guimodel.removeNode()
        pickAToonGui.removeNode()
        base.cr.avChoice = self

    def setupButtons(self, av=None, position=0):
        button = DirectButton(
            relief=None,
            image=self.buttonBgs[position],
            image_scale=1,
            image3_scale=1.2,
            command=self.selectToon,
            extraArgs=[position]
        )
        label = DirectLabel(
            text=TTLocalizer.AvatarChoiceMakeAToon,
            relief=None,
            text_font=ToontownGlobals.getToonFont(),
            text_scale=.1,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            activeState=1
        )
        button.reparentTo(self)
        label.reparentTo(button)
        button.setPos(MainMenuGlobals.TT_PLAY_AV_BOX_POSITIONS[position])
        button.setScale(.5)

        if av:
            headmod = ToonHead.ToonHead()
            dna = ToonDNA.ToonDNA()
            dna.makeFromNetString(av.dna)
            headmod.setupHead(dna, forGui=1)
            headmod.setPosHprScale(0, 5, -.1, 180, 0, 0, .24, .24, .24)
            headmod.reparentTo(button)
            label.setBin('fixed', 1)
            button.setBin('fixed', 0)
            headmod.startBlink()
            headmod.startLookAround()
            label['text'] = av.name
            label['text_pos'] = (0, .22)
            label['text_wordwrap'] = 12
            label['text_scale'] = .09
            label['text_roll'] = self.TEXTTILT[position]

            trashcanGui = loader.loadModel('phase_3/models/gui/trashcan_gui')
            deleteButton = DirectButton(
                parent=button,
                geom=(
                    trashcanGui.find('**/TrashCan_CLSD'),
                    trashcanGui.find('**/TrashCan_OPEN'),
                    trashcanGui.find('**/TrashCan_RLVR')
                ),
                text=('', TTLocalizer.AvatarChoiceDelete, TTLocalizer.AvatarChoiceDelete, ''),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                text_scale=.15,
                text_pos=(0, -.1),
                relief=None,
                scale=.5,
                command=self.__handleDelete,
                extraArgs=[position],
                pos=(.2, 0, -.2)
            )
            self.deleteButtonList[position] = deleteButton
            trashcanGui.removeNode()
        else:
            label['text_scale'] = .135
            label['text_pos'] = (-.01, .08)
            label['text_shadow'] = (1, 1, 1, 1)
            label['text_fg'] = (.498, 1, .921, 1)
            label['text_font'] = ToontownGlobals.getSignFont()

        button.bind(DGG.WITHIN, self.__setNameVisibility, [label, 0, button, .6])
        button.bind(DGG.WITHOUT, self.__setNameVisibility, [label, 1, button, .5])
        self.buttonList[position] = button
        self.buttonScales[position] = button.getScale()
        self.labelList[position] = label

    def __setNameVisibility(self, label, state, button=None, size=None, event=None):
        if self.ignoreHoverOut:
            label['activeState'] = 0
            self.ignoreHoverOut = False
        else:
            label['activeState'] = state
        if button:
            MainMenuGui.hoverButton(button, size, event)

    def selectToon(self, slot):
        prevSelectCheck = self.prevSelectedToon
        self.prevSelectedToon = self.selectedToon
        self.selectedToon = slot
        self.buttonList[self.selectedToon]['state'] = DGG.DISABLED
        if prevSelectCheck != -1:
            self.__setNameVisibility(self.labelList[self.selectedToon], 0, self.buttonList[self.selectedToon], .6)
            self.buttonList[self.prevSelectedToon]['state'] = DGG.NORMAL
            self.__setNameVisibility(self.labelList[self.prevSelectedToon], 1, self.buttonList[self.prevSelectedToon], .5)
            self.ignoreHoverOut = True
        else:
            self.__setNameVisibility(self.labelList[self.selectedToon], 0, self.buttonList[self.selectedToon], .6)
        self.updateFunc()

    def turnHead(self, task):
        def clampRotation(value, minimum, maximum):
            return min(max(value, minimum), maximum)
        if base.mouseWatcherNode.hasMouse() and self.toon:
            mpos = base.mouseWatcherNode.getMouse()
            scale = 4.78
            toonHeight = self.toon.getHeight()
            headHeight = toonHeight - self.toon.shoulderHeight
            starePos = mpos - (0.32, -0.73) - (0, (toonHeight - headHeight / 2.0) / scale)
            head = self.toon.getGeomNode().find('**/__Actor_head')
            head.setP(clampRotation(starePos.getY(), -.2, .5) * 80)
            head.setH(clampRotation(starePos.getX(), -.4, .2) * 120)
        return Task.cont

    def __resetHead(self):
        if self.toon:
            try:
                head = self.toon.getGeomNode().find('**/__Actor_head')
                head.setP(0)
                head.setH(0)
            except:
                pass
        taskMgr.remove('turnHead')

    def updateFunc(self):
        self.haveToon = self.toonList[self.selectedToon]
        if self.laffMeter:
            self.laffMeter.destroy()
            self.laffMeter = None
        if self.jumpIn:
            self.jumpIn.finish()
            self.jumpIn = None
        if self.haveToon:
            self.cleanUpToon()
            self.showToon()
        else:
            self.changeName.hide()
            self.__hideToon()
            taskMgr.remove('turnHead')
        self.checkPlayButton()

    def showToon(self):
        self.toon = Toon.Toon()
        self.toon.setPosHpr(.9, 32, 4, 180, 0, 0)
        self.toon.reparentTo(render)
        try:
            self.toon.nametag.getNametag2d().setContents(0)
        except:
            pass

        av = [x for x in self.avatarList if x.position == self.selectedToon][0]
        dnaString = av.dna
        if av.allowedName == 1:
            self.toon.setName(av.name + TTLocalizer.AvatarChoiceNameRejected)
            self.changeName.show()
        elif av.wantName != '':
            self.toon.setName(av.name + TTLocalizer.AvatarChoiceNameReview)
            self.changeName.hide()
        else:
            self.toon.setName(av.name)
            self.changeName.hide()

        self.toon.setPickable(0)
        self.toon.setDNAString(dnaString)
        try:
            self.toon.setHat(av.hat[0], av.hat[1], av.hat[2])
            self.toon.setGlasses(av.glasses[0], av.glasses[1], av.glasses[2])
            self.toon.setBackpack(av.backpack[0], av.backpack[1], av.backpack[2])
            self.toon.setShoes(av.shoes[0], av.shoes[1], av.shoes[2])
        except:
            pass
        try:
            self.toon.animFSM.request('neutral')
        except:
            self.toon.loop('neutral')
        self.toon.startBlink()
        self.toon.stopLookAround()

        dna = ToonDNA.ToonDNA()
        dna.makeFromNetString(dnaString)
        hp = getattr(av, 'hp', 1)
        maxHp = getattr(av, 'maxHp', hp)
        self.laffMeter = LaffMeter.LaffMeter(dna, hp, maxHp)
        self.laffMeter.reparentTo(base.a2dRightCenter)
        self.laffMeter.setPos(-.4, 0, 0)
        self.laffMeter.start()
        self.toon.show()

        if hp > 0:
            self.jumpIn = Sequence(
                Func(self.toon.loop, 'wave'),
                Func(self.__resetHead),
                Wait(self.toon.getDuration('wave')),
                Func(self.toon.animFSM.request, 'neutral'),
                Func(taskMgr.add, self.turnHead, 'turnHead')
            )
            self.afk = Sequence(
                Wait(10), Func(self.toon.loop, 'bored'), Func(self.__resetHead), Wait(self.toon.getDuration('bored')), Func(self.toon.animFSM.request, 'neutral'), Func(taskMgr.add, self.turnHead, 'turnHead'),
                Wait(15), Func(self.toon.loop, 'shrug'), Func(self.__resetHead), Wait(self.toon.getDuration('shrug')), Func(self.toon.animFSM.request, 'neutral'), Func(taskMgr.add, self.turnHead, 'turnHead'),
                Wait(15), Func(self.toon.loop, 'confused'), Func(self.__resetHead), Wait(self.toon.getDuration('confused')), Func(self.toon.animFSM.request, 'neutral'), Func(taskMgr.add, self.turnHead, 'turnHead'),
                Wait(15), Func(self.toon.loop, 'taunt'), Func(self.__resetHead), Wait(self.toon.getDuration('taunt')), Func(self.toon.animFSM.request, 'neutral'), Func(taskMgr.add, self.turnHead, 'turnHead')
            )
        else:
            self.jumpIn = Func(self.toon.loop, 'sad-neutral')
            self.afk = Sequence()

        self.afk.loop()
        self.jumpIn.start()

    def __hideToon(self):
        if self.toon:
            self.toon.hide()
        if self.afk:
            self.afk.finish()

    def cleanUpToon(self):
        if self.jumpIn:
            self.jumpIn.finish()
            self.jumpIn = None
        if self.afk:
            self.afk.finish()
            self.afk = None
        if self.toon:
            self.toon.delete()
            self.toon = None

    def checkPlayButton(self):
        if self.toonList[self.selectedToon]:
            self.continueButton['text'] = TTLocalizer.AvatarChoicePlayThisToon
            self.continueButton['text_pos'] = (0, .006)
            self.continueButton['command'] = self.doPlayAsToon
        else:
            self.continueButton['text'] = getattr(TTLocalizer, 'AvatarChoiceMakeAToonRegular', 'Make A Toon')
            self.continueButton['text_pos'] = (0, -.016)
            self.continueButton['command'] = self.makeToon

    def __handleCredits(self):
        import webbrowser
        webbrowser.open('https://corporateclash.net/help/credits', new=2)

    def doPlayAsToon(self):
        if hasattr(base, 'discord'):
            try:
                base.discord.applyPreset('loading_game')
            except:
                pass
        if self.afk:
            self.afk.finish()
        self.disableButtons()
        self.posInterval(.2, Point3(-3, 0, 0), blendType='easeInOut').start()
        self.selectToonAnim = Sequence(
            ActorInterval(self.toon, 'victory', startFrame=0, endFrame=9),
            ActorInterval(self.toon, 'victory', startFrame=9, endFrame=0),
            Func(self.toon.loop, 'run'),
            self.toon.hprInterval(.1, Vec3(0, 0, 0), blendType='easeIn'),
            Parallel(
                Sequence(
                    self.toon.posHprInterval(1, Point3(.9, 42, 4), Point3(-30, 0, 0)),
                    Func(self.toon.loop, 'run'),
                    self.toon.posHprInterval(1, Point3(4, 45, 4), Point3(-90, 0, 0))
                ),
                Func(base.transitions.fadeOut, 1)
            ),
            Wait(1),
            Func(base.camLens.setMinFov, settings['fieldofview'] / (4.0 / 3.0)),
            Func(self.playGame)
        )
        self.selectToonAnim.start()

    def playGame(self):
        base.transitions.noFade()
        messenger.send(self.doneEvent, [{'mode': 'chose', 'choice': self.selectedToon}])

    def makeToon(self):
        messenger.send(self.doneEvent, [{'mode': 'create', 'choice': self.selectedToon}])

    def __handleNameYourToon(self):
        self.disableButtons()
        messenger.send(self.doneEvent, [{'mode': 'nameIt', 'choice': self.selectedToon}])

    def __handleDelete(self, position):
        if self.selectedToon != position:
            self.selectToon(position)
        av = [x for x in self.avatarList if x.position == position][0]

        def doDelete(arg=None):
            if self.passwordEntry.get().lower() == TTLocalizer.AvatarChoiceDeleteConfirmUserTypes:
                self.deleteWithPasswordFrame.destroy()
                delDialog.cleanup()
                base.transitions.noFade()
                messenger.send(self.doneEvent, [{'mode': 'delete', 'choice': self.selectedToon}])
            else:
                self.passwordEntry.enterText('')

        def cancel(arg=None):
            self.deleteWithPasswordFrame.destroy()
            delDialog.cleanup()
            base.transitions.noFade()

        def diagDone():
            if delDialog.doneStatus == 'ok':
                buttons = loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')
                buttons.flattenMedium()
                try:
                    gui = loader.loadModel('phase_3/models/gui/ttcc_gui_generic')
                except:
                    gui = loader.loadModel('phase_3/models/props/chatbox_input')
                okButtonImage = (
                    buttons.find('**/ChtBx_OKBtn_UP'),
                    buttons.find('**/ChtBx_OKBtn_DN'),
                    buttons.find('**/ChtBx_OKBtn_Rllvr')
                )
                cancelButtonImage = (
                    buttons.find('**/CloseBtn_UP'),
                    buttons.find('**/CloseBtn_DN'),
                    buttons.find('**/CloseBtn_Rllvr')
                )
                deleteText = TTLocalizer.AvatarChoiceDeleteConfirmText % {
                    'name': av.name,
                    'confirm': TTLocalizer.AvatarChoiceDeleteConfirmUserTypes
                }
                self.deleteWithPasswordFrame = DirectFrame(
                    pos=(0.0, 0.1, 0.2),
                    parent=aspect2d,
                    relief=None,
                    image=DGG.getDefaultDialogGeom(),
                    image_color=ToontownGlobals.GlobalDialogColor,
                    image_scale=(1.4, 1.0, 1.0),
                    text=deleteText,
                    text_wordwrap=19,
                    text_scale=TTLocalizer.ACdeleteWithPasswordFrame,
                    text_pos=(0, 0.25),
                    textMayChange=1,
                    sortOrder=NO_FADE_SORT_INDEX
                )
                inputImage = gui.find('**/gui_input_box')
                if inputImage.isEmpty():
                    inputImage = gui
                self.passwordEntry = DirectEntry(
                    parent=self.deleteWithPasswordFrame,
                    relief=None,
                    image=inputImage,
                    scale=.064,
                    pos=(-.14, 0, -.2),
                    width=4,
                    numLines=1,
                    focus=1,
                    cursorKeys=1,
                    command=doDelete
                )
                self.passwordEntry.flattenMedium()
                self.passwordEntry.setTransparency(1)
                DirectButton(parent=self.deleteWithPasswordFrame, image=okButtonImage, relief=None, text=getattr(TTLocalizer, 'AvatarChoiceDeleteOK', TTLocalizer.lOK), text_scale=.05, text_pos=(0, -.1), pos=(-.22, 0, -.35), command=doDelete)
                DirectButton(parent=self.deleteWithPasswordFrame, image=cancelButtonImage, relief=None, text=getattr(TTLocalizer, 'AvatarChoiceDeleteCancel', TTLocalizer.lCancel), text_scale=.05, text_pos=(0, -.1), pos=(.2, 0, -.35), command=cancel)
                gui.removeNode()
                buttons.removeNode()
            else:
                delDialog.cleanup()
                base.transitions.noFade()

        base.acceptOnce('pat-del-diag-done', diagDone)
        delDialog = TTGlobalDialog(
            message=TTLocalizer.PhotoPageDelete + ' %s?' % av.name,
            style=YesNo,
            doneEvent='pat-del-diag-done'
        )
        delDialog.show()

    def getChoice(self):
        return self.selectedToon

    def exit(self):
        pass

    def unload(self):
        pass

    def destroy(self):
        taskMgr.remove('turnHead')
        if self.jumpIn:
            self.jumpIn.finish()
            self.jumpIn = None
        if self.afk:
            self.afk.finish()
            self.afk = None
        if self.laffMeter:
            self.laffMeter.destroy()
            self.laffMeter = None
        if self.confirmQuit:
            self.confirmQuit.cleanup()
            self.confirmQuit = None
        if self.selectToonAnim:
            self.selectToonAnim.finish()
            self.selectToonAnim = None
        if self.toon:
            self.toon.delete()
            self.toon = None
        self.ignoreAll()
        MainMenuScreen.destroy(self)

    def disableButtons(self):
        for button in (self.optionsButton, self.quitButton, self.creditsButton, self.continueButton, self.changeName):
            if button:
                button['state'] = DGG.DISABLED

    def enableButtons(self):
        for button in (self.optionsButton, self.quitButton, self.creditsButton, self.continueButton, self.changeName):
            if button:
                button['state'] = DGG.NORMAL

    def showQuitDialog(self):
        self.accept('handleQuit', self.__handleQuit)
        self.confirmQuit = TTDialog.TTGlobalDialog(
            doneEvent='handleQuit',
            message=TTLocalizer.OptionsPageExitConfirm,
            style=TTDialog.TwoChoice
        )
        self.confirmQuit.show()

    def __handleQuit(self):
        status = self.confirmQuit.doneStatus
        self.confirmQuit.cleanup()
        self.confirmQuit = None
        self.ignore('handleQuit')
        if status == 'ok':
            messenger.send(self.doneEvent, [{'mode': 'exit', 'choice': self.selectedToon}])
