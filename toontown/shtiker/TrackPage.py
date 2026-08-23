from pandac.PandaModules import *
from toontown.shtiker import ShtikerPage
from direct.gui.DirectGui import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import TTLocalizer
from toontown.toontowngui import TTDialog


class TrackPage(ShtikerPage.ShtikerPage):

    TrackOrder = [
        ToontownBattleGlobals.HEAL_TRACK,
        ToontownBattleGlobals.LURE_TRACK,
        ToontownBattleGlobals.SQUIRT_TRACK,
        ToontownBattleGlobals.SOUND_TRACK,
        ToontownBattleGlobals.TRAP_TRACK,
        ToontownBattleGlobals.THROW_TRACK,
        ToontownBattleGlobals.ZAP_TRACK,
        ToontownBattleGlobals.DROP_TRACK,
    ]
    GagIconLevel = 5

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.refundMode = False
        self.infoDialog = None

    def load(self):
        self.trainingRoot = DirectFrame(
            parent=self,
            relief=None,
            pos=(0.05, 0, 0),
            scale=0.875)

        self.title = DirectLabel(
            parent=self.trainingRoot,
            relief=None,
            text=TTLocalizer.TrackPageTitle,
            text_scale=0.12,
            pos=(-0.05, 0, 0.68))

        self.pointDesc = DirectLabel(
            parent=self.trainingRoot,
            relief=None,
            text=TTLocalizer.TrackPageSubtitle,
            text_scale=0.077,
            text_align=TextNode.ARight,
            pos=(-0.08, 0, -0.695))

        self.pointLabel = DirectLabel(
            parent=self.trainingRoot,
            relief=None,
            text=str(base.localAvatar.getTrainingPoints()),
            text_font=ToontownGlobals.getBuildingNametagFont(),
            text_fg=(0, 0.75, 0.75, 1),
            text_scale=0.085,
            text_align=TextNode.ALeft,
            pos=(-0.05, 0, -0.695))

        self.menuModel = loader.loadModel('phase_3/models/gui/ttcc_menu_buttons')
        self.menuNormal = self.menuModel.find('**/menubtn')
        self.menuPressed = self.menuModel.find('**/menubtn-press')

        self.infoModel = loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')
        self.infoUp = self.infoModel.find('**/report_BtnUP')
        self.infoDown = self.infoModel.find('**/report_BtnDN')
        self.infoRollover = self.infoModel.find('**/report_BtnRLVR')

        self.gagSelectionModel = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
        self.lockGeom = self.gagSelectionModel.find('**/lock')
        self.prestigeStarEmpty = self.gagSelectionModel.find('**/prestige_star_empty')
        self.prestigeStarFilled = self.gagSelectionModel.find('**/prestige_star')

        self.inventoryIconModel = None
        self.trackFrames = {}
        self.gagFrames = {}
        self.trackLabels = {}
        self.manageButtons = {}
        self.infoButtons = {}
        self.lockImages = {}
        self.trackStars = {}
        self.trackStarFilled = {}
        self.trackStarFallback = {}

        zPositions = [0.48, 0.1866667, -0.1066667, -0.4]
        for index in range(len(self.TrackOrder)):
            track = self.TrackOrder[index]
            column = index / 4
            row = index % 4
            x = -0.79 if column == 0 else 0.22
            z = zPositions[row]

            frame = DirectFrame(
                parent=self.trainingRoot,
                relief=None,
                pos=(x, 0, z),
                scale=2.4)
            self.trackFrames[track] = frame

            gagFrame = DirectFrame(
                parent=frame,
                relief=None,
                pos=(-0.01764, 0, 0),
                scale=1.0,
                image=self.getGagGeom(track),
                image_scale=1.0)
            self.gagFrames[track] = gagFrame

            trackLabel = DirectLabel(
                parent=frame,
                relief=None,
                text=ToontownBattleGlobals.Tracks[track],
                text_scale=0.04,
                text_align=TextNode.ALeft,
                text_fg=Vec4(
                    ToontownBattleGlobals.TrackColors[track][0],
                    ToontownBattleGlobals.TrackColors[track][1],
                    ToontownBattleGlobals.TrackColors[track][2],
                    1),
                text_font=ToontownGlobals.getSignFont(),
                pos=(0.05878, 0, 0.0147))
            self.trackLabels[track] = trackLabel

            manageButton = DirectButton(
                parent=frame,
                relief=None,
                pos=(0.13522, 0, -0.02939),
                scale=(0.551768, 0.4, 0.39412),
                image=(
                    self.menuNormal,
                    self.menuPressed,
                    self.menuNormal,
                    self.menuPressed),
                image_scale=(0.3, 0.15, 0.15),
                image1_scale=(0.3, 0.15, 0.15),
                image2_scale=(0.3, 0.15, 0.15),
                image3_scale=(0.3, 0.15, 0.15),
                text='',
                text_pos=(0.00016, -0.01624),
                text_scale=(0.035714, 0.05, 0.05),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                command=self.handleManage,
                extraArgs=[track])
            self.manageButtons[track] = manageButton

            if not self.infoUp.isEmpty() and not self.infoDown.isEmpty() and not self.infoRollover.isEmpty():
                infoButton = DirectButton(
                    parent=frame,
                    relief=None,
                    pos=(0.03428, 0, -0.04417),
                    scale=0.39412,
                    image=(
                        self.infoUp,
                        self.infoDown,
                        self.infoRollover,
                        self.infoUp),
                    command=self.openInfo,
                    extraArgs=[track])
            else:
                infoButton = DirectButton(
                    parent=frame,
                    relief=DGG.RAISED,
                    borderWidth=(0.01, 0.01),
                    frameSize=(-0.035, 0.035, -0.035, 0.035),
                    pos=(0.03428, 0, -0.04417),
                    scale=0.39412,
                    text='i',
                    text_scale=0.06,
                    command=self.openInfo,
                    extraArgs=[track])
            self.infoButtons[track] = infoButton

            if not self.lockGeom.isEmpty():
                lockImage = DirectFrame(
                    parent=gagFrame,
                    relief=None,
                    pos=(0, 0, 0),
                    scale=0.06969,
                    image=self.lockGeom,
                    image_scale=(1.0, 1.0, 160.0 / 116.0))
            else:
                lockImage = DirectFrame(parent=gagFrame, relief=None)
                lockImage.hide()
            self.lockImages[track] = lockImage

            if not self.prestigeStarEmpty.isEmpty() and not self.prestigeStarFilled.isEmpty():
                trackStar = DirectFrame(
                    parent=frame,
                    relief=None,
                    pos=(0.24427, 0, -0.03053),
                    scale=0.05026,
                    image=self.prestigeStarEmpty)
                filledStar = DirectFrame(
                    parent=trackStar,
                    relief=None,
                    pos=(0, 0, 0),
                    scale=1.06,
                    image=self.prestigeStarFilled)
                filledStar.hide()
                fallbackStar = None
            else:
                trackStar = DirectFrame(parent=frame, relief=None)
                trackStar.hide()
                filledStar = None
                fallbackStar = DirectLabel(
                    parent=frame,
                    relief=None,
                    text='*',
                    text_scale=0.075,
                    text_fg=(0.45, 0.45, 0.45, 1),
                    text_shadow=(1, 1, 1, 1),
                    text_font=ToontownGlobals.getSignFont(),
                    pos=(0.24427, 0, -0.047))
            self.trackStars[track] = trackStar
            self.trackStarFilled[track] = filledStar
            self.trackStarFallback[track] = fallbackStar

        self.refundButton = DirectButton(
            parent=self.trainingRoot,
            relief=None,
            pos=(0.42, 0, -0.67566),
            scale=(1.4, 1, 1),
            image=(
                self.menuNormal,
                self.menuPressed,
                self.menuNormal,
                self.menuPressed),
            image_scale=(0.3, 0.15, 0.15),
            image1_scale=(0.3, 0.15, 0.15),
            image2_scale=(0.3, 0.15, 0.15),
            image3_scale=(0.3, 0.15, 0.15),
            image_color=(1.0, 0.45, 0.45, 1.0),
            text='Refund Point',
            text_pos=(0.00016, -0.01624),
            text_scale=(0.035714, 0.05, 0.05),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            command=self.changeRefundMode)
        self.refundButton.hide()

        self.accept('skillPointChange', self.updatePage)
        self.updatePage()

    def unload(self):
        self.cleanupDialogs()
        self.ignoreAll()
        if self.inventoryIconModel:
            self.inventoryIconModel.removeNode()
            self.inventoryIconModel = None
        if self.menuModel:
            self.menuModel.removeNode()
        if self.infoModel:
            self.infoModel.removeNode()
        if self.gagSelectionModel:
            self.gagSelectionModel.removeNode()
        del self.title
        del self.pointDesc
        del self.pointLabel
        del self.trackFrames
        del self.gagFrames
        del self.trackLabels
        del self.manageButtons
        del self.infoButtons
        del self.lockImages
        del self.trackStars
        del self.trackStarFilled
        del self.trackStarFallback
        self.trainingRoot.destroy()
        del self.trainingRoot
        ShtikerPage.ShtikerPage.unload(self)

    def clearPage(self):
        self.cleanupDialogs()

    def enter(self):
        self.refundMode = False
        self.updatePage()
        ShtikerPage.ShtikerPage.enter(self)

    def exit(self):
        self.clearPage()
        ShtikerPage.ShtikerPage.exit(self)

    def getGagGeom(self, track):
        try:
            return base.localAvatar.inventory.invModels[track][self.GagIconLevel]
        except:
            if not self.inventoryIconModel:
                self.inventoryIconModel = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            return self.inventoryIconModel.find('**/' + ToontownBattleGlobals.AvPropsNew[track][self.GagIconLevel])

    def hasBoughtTrack(self, track):
        return bool(base.localAvatar.getTrackAccess()[track])

    def hasPrestigedTrack(self, track):
        return base.localAvatar.getTrackBonusLevel(track) >= 1

    def canBuyTrack(self, track):
        return base.localAvatar.getTrainingPoints() >= 2 and not self.hasBoughtTrack(track)

    def canPrestigeTrack(self, track):
        return base.localAvatar.getTrainingPoints() >= 1 and not self.hasPrestigedTrack(track)

    def canRefundTrack(self, track):
        return self.hasBoughtTrack(track)

    def canEnterRefundMode(self):
        return sum(base.localAvatar.getTrackAccess()) > 2

    def updatePage(self, *args):
        self.pointLabel['text'] = str(base.localAvatar.getTrainingPoints())

        if self.canEnterRefundMode():
            self.refundButton.show()
            self.pointDesc.setX(-0.34)
            self.pointLabel.setX(-0.31)
        else:
            if self.refundMode:
                self.refundMode = False
            self.refundButton.hide()
            self.pointDesc.setX(-0.08)
            self.pointLabel.setX(-0.05)

        self.refundButton['text'] = 'Manage Tracks' if self.refundMode else 'Refund Track'

        for track in self.TrackOrder:
            self.updateTrack(track)

    def updateTrack(self, track):
        bought = self.hasBoughtTrack(track)
        prestiged = self.hasPrestigedTrack(track)

        if bought:
            self.gagFrames[track]['image_color'] = (1, 1, 1, 1)
            self.lockImages[track].hide()
            if self.trackStarFallback[track] is not None:
                self.trackStarFallback[track].show()
                self.trackStarFallback[track]['text_fg'] = (0.43, 0.37, 1.0, 1) if prestiged else (0.45, 0.45, 0.45, 1)
            else:
                self.trackStars[track].show()
                if prestiged:
                    self.trackStarFilled[track].show()
                else:
                    self.trackStarFilled[track].hide()
        else:
            self.gagFrames[track]['image_color'] = (0.5, 0.5, 0.5, 1)
            self.lockImages[track].show()
            if self.trackStarFallback[track] is not None:
                self.trackStarFallback[track].hide()
            else:
                self.trackStars[track].hide()

        button = self.manageButtons[track]
        button['image_color'] = (1, 1, 1, 1)
        button['image3_color'] = (0.75, 0.75, 0.75, 1)

        if not self.refundMode:
            if not bought:
                button['text'] = 'Unlock (x2)'
                button['state'] = DGG.NORMAL if self.canBuyTrack(track) else DGG.DISABLED
            elif not prestiged:
                button['text'] = 'Prestige (x1)'
                button['state'] = DGG.NORMAL if self.canPrestigeTrack(track) else DGG.DISABLED
                button['image_color'] = (0.43, 0.37, 1.0, 1)
            else:
                button['text'] = 'Unprestige'
                button['state'] = DGG.NORMAL
                button['image_color'] = (1.0, 0.26, 0.36, 1.0)
        else:
            if self.canRefundTrack(track):
                button['text'] = 'Refund Track'
                button['state'] = DGG.NORMAL
                button['image_color'] = (1.0, 0.45, 0.45, 1.0)
            else:
                button['text'] = "Can't Refund"
                button['state'] = DGG.DISABLED
                button['image_color'] = (0.75, 0.75, 0.75, 1.0)

    def changeRefundMode(self):
        self.refundMode = not self.refundMode
        self.updatePage()

    def handleManage(self, track):
        if not self.canChangeTracksHere():
            self.showChangeFailure()
            return

        av = base.localAvatar
        if self.refundMode:
            if self.canRefundTrack(track):
                av.sendUpdate('requestRefundSpend', [track])
            return

        if not self.hasBoughtTrack(track):
            if self.canBuyTrack(track):
                av.sendUpdate('requestSkillSpend', [track])
        elif not self.hasPrestigedTrack(track):
            if self.canPrestigeTrack(track):
                av.sendUpdate('requestSkillSpend', [track])
        else:
            av.sendUpdate('requestSkillReturn', [track])

    def getTrackName(self, track):
        try:
            return TTLocalizer.BattleGlobalTracks[track].upper()
        except:
            return str(ToontownBattleGlobals.Tracks[track]).upper()

    def getPrestigeHint(self, track):
        try:
            return TTLocalizer.TrackPageHints[(track * 5) + 2]
        except:
            return ''

    def canChangeTracksHere(self):
        try:
            return base.localAvatar.isRefundZoneValid()
        except:
            return True

    def showChangeFailure(self):
        try:
            base.localAvatar.sendFailedRefundNotif()
        except:
            pass

    def openInfo(self, track):
        self.cleanupInfo()
        name = self.getTrackName(track)
        prestige = self.getPrestigeHint(track)
        message = '%s\n\nUnlock Cost: 2 Training Points\nPrestige Cost: 1 Training Point\n\nPrestige Bonus:\n%s' % (name, prestige)
        self.infoDialog = TTDialog.TTGlobalDialog(
            message=message,
            doneEvent='TrackPageInfoDone',
            style=TTDialog.Acknowledge,
            okButtonText=TTLocalizer.lOK,
            text_wordwrap=21,
            text_scale=0.06)
        self.acceptOnce('TrackPageInfoDone', self.cleanupInfo)
        self.infoDialog.show()

    def cleanupInfo(self):
        self.ignore('TrackPageInfoDone')
        if self.infoDialog:
            self.infoDialog.cleanup()
            self.infoDialog = None

    def cleanupDialogs(self):
        self.cleanupInfo()
