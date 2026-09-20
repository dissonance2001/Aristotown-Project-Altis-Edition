from direct.gui.DirectGui import *
from panda3d.core import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.events.halloween.TextureWaitBar import TextureWaitBar
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

itemCosts = ToontownGlobals.BatcoinThreshholds


@DirectNotifyCategory()
class HalloweenPass(DirectFrame):
    def __init__(self, passNPC, *args, **kwargs):
        opts = {'relief': None}
        opts.update(kwargs)
        DirectFrame.__init__(self, *args, **opts)
        self.initialiseoptions(self.__class__)
        self.passNPC = passNPC  # Store the NPC instance so we can call the AI
        self.assets = self.passNPC.storeAssets
        self.batcoins = base.localAvatar.getBatcoins()
        self.createGui()

        # run wakeup calls to make sure the toon doesn't fall asleep
        self.keepAliveTaskName = self.uniqueName('keepAlive')
        self.__startKeepAlive()

    def __keepAlive(self, task):
        """Keeps the localAvatar awake while they are using this UI."""
        if base.localAvatar:
            base.localAvatar.wakeUp()
        task.delayTime = 30
        return task.again

    def __startKeepAlive(self):
        taskMgr.add(self.__keepAlive, self.keepAliveTaskName, 30)

    def __endKeepAlive(self):
        taskMgr.remove(self.keepAliveTaskName)

    def createGui(self):
        SO_PB = 6   # sort order for the progress bar (behind base, in the transparent area)
        SO_BG = 7   # sort order for the base GUI
        SO_HAX = 8  # sort order to hide the transparent bit of the progress bar (since that's baked into the images)
        SO_BTN = 9  # sort order for the buttons and text (above the base)
        # TODO: set up shifting the lights in a task later
        # Note: store any args that'll be the same for all BG frames here, so that we can just add a **bg_opts to the
        #  init call on all of them
        bg_opts = {
            'parent': self,
            'relief': None,
            'scale': (1.345, 1.0, 1.35),
            'sortOrder': SO_BG,    # at least make sure this is in front of the progress bar frame, but below buttons
        }
        self.__bgOff = DirectFrame(geom=self.assets.find('**/bg_off'), **bg_opts)
        self.__bgOn = DirectFrame(geom=self.assets.find('**/bg_on'), **bg_opts)
        self.__bgShuffle1 = DirectFrame(geom=self.assets.find('**/bg_shuffle_1'), **bg_opts)
        self.__bgShuffle2 = DirectFrame(geom=self.assets.find('**/bg_shuffle_2'), **bg_opts)
        # hide the other BG frames
        self.__bgOff.hide()
        self.__bgShuffle1.hide()
        self.__bgShuffle2.hide()
        # store these in a tuple to make life easier in task
        self.bgList = (
            self.__bgOff,
            self.__bgOn,
            self.__bgShuffle1,
            self.__bgShuffle2
        )
        # and store the current 'showing' index
        self.bgIdx = 1
        # create the background light task
        self.__bgLightTaskName = "HalloweenPassGUI-LightChange"
        self.__bgLightTaskTime = 0.4    # how long between light changes
        self.__bgLightIterNo = 0    # the current iteration count, which will determine what background index to show

        self.__claimPrizeTaskName = "HalloweenPassGUI-ClaimFlash"
        self.__claimPrizeTaskTime = 0.75
        self.__claimPrizeFlash = 1

        # Note: buttons are as follows (in egg/bam):
        #   rewards: rewards-[neutral/hover/pressed]
        #   how 2 play: h2p-[neutral/hover/pressed]
        #   what's this?: whatthis-[neutral/hover/pressed]
        #   claim prize: claim-[neutral/hover/pressed]
        # Progress bar stuff are: pb_base, pb_bats
        # Background stuff is: bg_off, bg_on, bg_shuffle_1, bg_shuffle_2
        # Note: Since the gui doesn't have a quit button in the mockup, nor the creative drive, going to borrow one
        # from another gui (we don't want to hold players hostage, right?... right???)

        # quit button
        quitBtn = loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')
        quitBtnList = (quitBtn.find('**/CloseBtn_UP'),
                         quitBtn.find('**/CloseBtn_DN'),
                         quitBtn.find('**/CloseBtn_Rllvr'))
        self.closeButton = DirectButton(parent=self, image=quitBtnList, image_scale=(1.35, 1.0, 1.35),
                                        pos=(0.725, 0, 0.557), relief=None, command=self.handleClose, sortOrder=SO_BTN)
        quitBtn.removeNode()
        del quitBtn

        text_color = (0.8, 0.8, 0.8, 1.0)

        # The Poggress bar (yes, I intentionally mis-spelt 'progress' :P)
        # edit: Okay, *screw* DirectWaitBar for textured progress bars. I'll do it myself.
        self.progressBar = TextureWaitBar(parent=self, relief=None, background=self.assets.find('**/pb_base'),
                                          fillIn=self.assets.find('**/pb_bats'), sortOrder=SO_PB,
                                          backgroundScale=(0.815, 1, 0.23), fillInScale=(0.965, 1, 0.235),
                                          fillInStartOffset=0.1, fillInClipLeft=False,
                                          fillInClipBounds=(0.325, -0.605), pos=(0, 0, -0.025))
        # self.progressBarFrame.setBin("gui-popup", 50)
        self.progressText = DirectLabel(parent=self, relief=None, text=TTLocalizer.BatcoinsTo,
                                        text_font=ToontownGlobals.getToonFont(), text_scale=0.045,
                                        text_align=TextNode.ACenter, text_wordwrap=24.0, textMayChange=1,
                                        text_fg=text_color, pos=(0, 0, 0.145), sortOrder=SO_BTN)
        # this one is to hide the transparent bit of the 'poggress' bar, so that text doesn't look ugly on it
        # Note: for a simple colored frame, do *not* put a relief=None, or you're going to dread life trying to figure
        #  out why nothing's showing up
        self.progressHider = DirectFrame(parent=self, frameColor=(0.349, 0.333, 0.365, 1.0), pos=(0, 0, 0.012),
                                         frameSize=(-0.4125, 0.4125, -0.0745, 0.0745), sortOrder=SO_HAX)
        # because I'm lazy, have this automagically generates the image arg bit *for me*!

        def btnLookup(prefix):
            return (
                self.assets.find(f'**/{prefix}-neutral'),
                self.assets.find(f'**/{prefix}-pressed'),
                self.assets.find(f'**/{prefix}-hover'),
            )

        self.claimButton = DirectButton(parent=self, relief=None, pos=(0, 0, -0.225), sortOrder=SO_BTN,
                                        image=btnLookup('claim'), image_scale=(0.648, 1.0, 0.352),
                                        command=self.handleClaim)
        # So the button doesn't flash if we are hovering over it.
        self.claimButton.bind(DGG.WITHIN, self.setFlashOff, [])
        self.claimButton.bind(DGG.WITHOUT, self.setFlashOn, [])


        self.claimFlashingButton = DirectButton(parent=self, relief=None, pos=(0, 0, -0.225), sortOrder=SO_BTN,
                                        image=self.assets.find('**/claim-pressed'), image_scale=(0.648, 1.0, 0.352),
                                        command=self.handleClaim)

        # these vars are specifically for the rewards, whats this and how to buttons
        btnRowY = -0.525
        btnRowSidesX = 0.36
        btnScale = (0.3, 1.0, 0.135)
        self.rewardsButton = DirectButton(parent=self, relief=None, pos=(-btnRowSidesX, 0, btnRowY), sortOrder=SO_BTN,
                                          image=btnLookup('rewards'), image_scale=btnScale,
                                          command=self.switchToRewards)
        self.whatsThisButton = DirectButton(parent=self, relief=None, pos=(0, 0, btnRowY - 0.005), sortOrder=SO_BTN,
                                            image=btnLookup('whatthis'), image_scale=(0.36, 1.0, 0.155),
                                            command=self.switchToWhatsThis)
        self.howToButton = DirectButton(parent=self, relief=None, pos=(btnRowSidesX, 0, btnRowY), sortOrder=SO_BTN,
                                        image=btnLookup('h2p'), image_scale=btnScale, command=self.switchToHowTo)

        # text for the how to play and what's this parts:
        # P.S. I'm going to hell for the default title...
        self.tabTitle = DirectLabel(parent=self, relief=None, text="OwO What's this?",
                                    text_font=ToontownGlobals.getToonFont(), text_scale=0.065,
                                    text_align=TextNode.ACenter, text_wordwrap=28.0, textMayChange=1,
                                    text_fg=text_color, pos=(0, 0, 0.135), sortOrder=SO_BTN)

        self.tabDesc = DirectLabel(parent=self, relief=None, text="A" * 510,
                                   text_font=ToontownGlobals.getToonFont(), text_scale=0.035,
                                   text_align=TextNode.ACenter, text_wordwrap=25.0, textMayChange=1,
                                   text_fg=text_color, pos=(0, 0, 0.055), sortOrder=SO_BTN)

        # run the claim button task now
        taskMgr.doMethodLater(self.__claimPrizeTaskTime, self.__claimButtonFlashTask, self.__claimPrizeTaskName, appendTask=True)

        # run the light task now, since everything is now set up
        taskMgr.doMethodLater(self.__bgLightTaskTime, self.__ultimaLightTask, self.__bgLightTaskName, appendTask=True)

        # and go ahead and switch to rewards
        self.switchToRewards()

    # Button Methods

    def handleClose(self):
        taskMgr.remove(self.__bgLightTaskName)
        self.__endKeepAlive()
        self.bgList = None  # clear this out so we don't store any more references to the BG DirectFrames
        self.removeNode()
        self.passNPC.runCleanup()

    def switchToRewards(self):
        # hide the 'transparency progress bar hider' and tab texts
        self.progressHider.hide()
        self.tabTitle.hide()
        self.tabDesc.hide()
        self.claimFlashingButton.hide()
        # update values
        pointsUntil, percent = self.calculatePointsTill(self.batcoins)
        txt = TTLocalizer.BatcoinsTo.format(**{'playerCoins': self.batcoins, 'toGo': pointsUntil})
        self.progressText['text'] = txt
        self.progressBar.value = percent
        # show stuff
        self.progressText.show()
        self.progressBar.show()
        self.claimButton.show()
        self.__claimPrizeFlash = 0

    def switchToWhatsThis(self):
        # hide stuff
        self.progressBar.hide()
        self.progressText.hide()
        self.claimButton.hide()
        self.claimFlashingButton.hide()
        self.__claimPrizeFlash = -1
        # update values
        self.tabTitle['text'] = TTLocalizer.HalloweenPassWhatsThisTitle
        self.tabDesc['text'] = TTLocalizer.HalloweenPassWhatsThisDesc
        # show text and 'transparency progress bar hider'
        self.progressHider.show()
        self.tabTitle.show()
        self.tabDesc.show()

    def switchToHowTo(self):
        # hide stuff
        self.progressBar.hide()
        self.progressText.hide()
        self.claimButton.hide()
        self.claimFlashingButton.hide()
        self.__claimPrizeFlash = -1
        # update values
        self.tabTitle['text'] = TTLocalizer.HalloweenPassHow2PlayTitle
        self.tabDesc['text'] = TTLocalizer.HalloweenPassHow2PlayDesc
        if base.cr.newsManager:
            if base.cr.newsManager.isHolidayRunning(ToontownGlobals.APRIL_FOOLS) or base.cr.newsManager.isHolidayRunning(ToontownGlobals.HALLOWEEN_MIX_WINTER_HOLIDAY):
                self.tabDesc['text'] = TTLocalizer.HalloweenPassHow2PlayDescAprilToons
        # show text and 'transparency progress bar hider'
        self.progressHider.show()
        self.tabTitle.show()
        self.tabDesc.show()

    def handleClaim(self):
        self.passNPC.claimItems()

    # Helper Methods

    def calculatePointsTill(self, points):
        for cost in itemCosts:
            if points >= cost:  # If the points owned are equal or higher than current cost being checked
                continue  # Keep checking
            else:  # Once we hit a cost we haven't reached, return values for string and prog. bar
                return cost - points, (float(points) / cost) * 100
        return 0, 100  # If we hit no costs, we have everything. Set string to 0 and prog. bar to full.

    def __claimButtonFlashTask(self, task):
        if not self.passNPC.hasItemsToClaim:
            return
        if self.__claimPrizeFlash > -1:
            self.claimFlashingButton.hide()
            self.claimButton.hide()
            if self.__claimPrizeFlash == 1:
                self.claimButton.show()
                self.__claimPrizeFlash = 0
            else:
                self.claimFlashingButton.show()
                self.__claimPrizeFlash = 1
        return task.again

    def setFlashOff(self, dummy):
        self.__claimPrizeFlash = -1
        self.claimFlashingButton.hide()
        self.claimButton.show()

    def setFlashOn(self, dummy):
        self.__claimPrizeFlash = 0
        self.claimButton.show()

    def __ultimaLightTask(self, task):
        # currently set up the rotation as the following:
        #   1. on
        #   2. shuffle_1
        #   3. shuffle_2
        #   4. shuffle_1
        #   5. shuffle_2
        #   6. on
        #   7. off
        #   8. on
        #   9. off
        #   10. on
        #
        # To repeat the bgList,
        #   Index 0 == off, 1 == on, 2 == shuffle_1, 3 == shuffle_2
        #
        # first, hide the current background
        self.bgList[self.bgIdx].hide()
        # determine the next background to show
        if self.__bgLightIterNo in (0, 5, 7, 9):
            # state 'on'
            self.bgIdx = 1
        elif self.__bgLightIterNo in (6, 8):
            # state 'off'
            self.bgIdx = 0
        elif self.__bgLightIterNo in (1, 3):
            # state 'shuffle_1'
            self.bgIdx = 2
        elif self.__bgLightIterNo in (2, 4):
            # state 'shuffle_2
            self.bgIdx = 3
        else:
            # *shouldn't* be an issue, unless someone (probably me) forgets about some part of a rotation
            self.notify.error(f'Unknown light iteration {self.__bgLightIterNo}!', exception=ValueError)
        # show the new frame
        self.bgList[self.bgIdx].show()
        # update the iteration count, making sure to mod it by the # of rotations
        self.__bgLightIterNo = (self.__bgLightIterNo + 1) % 10
        # finally, repeat task
        return task.again
