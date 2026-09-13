from .PurchaseBase import *
from toontown.toonbase import ToontownTimer

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.toon.Toon import Toon

COUNT_UP_RATE = 0.15
DELAY_BEFORE_COUNT_UP = 1.25
DELAY_AFTER_COUNT_UP = 1.75
COUNT_DOWN_RATE = 0.075
DELAY_AFTER_COUNT_DOWN = 0.0
DELAY_AFTER_CELEBRATE = 3.0


class ClerkPurchase(PurchaseBase):
    """
    ClerkPurchase(PurchaseBase)
    """

    activateMode = 'storePurchase'

    def __init__(self, toon, remain, doneEvent):
        """
        Create and display a purchase screen for
        the given Toon with the given amount of points to spend on items.
        Throw the given event name when user is finished

        :type toon: Toon
        :type remain: int
        :type doneEvent: str
        """
        PurchaseBase.__init__(self, toon, doneEvent)
        self.remain = remain
        self.costMultiplier = 1

    def load(self):
        purchaseModels = loader.loadModel('phase_4/models/gui/purchase_gui')

        PurchaseBase.load(self, purchaseModels)

        self.backToPlayground = DirectButton(
            parent = self.frame,
            relief = None,
            scale = 1.04,
            pos = (0.984, 0, -0.295),
            image = (
                purchaseModels.find('**/PurchScrn_BTN_UP'),
                purchaseModels.find('**/PurchScrn_BTN_DN'),
                purchaseModels.find('**/PurchScrn_BTN_RLVR')
            ),
            text = TTLocalizer.GagShopDoneShopping,
            text_fg = (0, 0.1, 0.7, 1),
            text_scale = 0.05,
            text_pos = (0, 0.015, 0),
            command = self.__handleBackToPlayground
        )

        # The timer
        self.timer = ToontownTimer.ToontownTimer()
        self.timer.reparentTo(self.frame)
        self.timer.posInTopRightCorner()
        purchaseModels.removeNode()

    def unload(self):
        PurchaseBase.unload(self)
        del self.backToPlayground
        self.timer.removeNode()
        del self.timer

    def setCostMultiplier(self, costMultiplier):
        self.costMultiplier = costMultiplier

    def __handleBackToPlayground(self):
        self.toon.inventory.reparentTo(hidden)
        self.toon.inventory.hide()
        self.handleDone(0)

    def __timerExpired(self):
        self.handleDone(2)

    ### Purchase state functions ###

    def enterPurchase(self):
        PurchaseBase.enterPurchase(self, costMultiplier = self.costMultiplier)
        self.backToPlayground.reparentTo(self.toon.inventory.storePurchaseFrame)
        self.pointDisplay.reparentTo(self.toon.inventory.storePurchaseFrame)#

        # Start the timer countdown
        self.timer.countdown(self.remain, self.__timerExpired)

    def exitPurchase(self):
        PurchaseBase.exitPurchase(self)
        self.backToPlayground.reparentTo(self.frame)
        self.pointDisplay.reparentTo(self.frame)
        self.ignore('purchaseStateChange')
