from direct.fsm import ClassicFSM, State, StateData
from direct.gui.DirectGui import *
from direct.showbase.MessengerGlobal import messenger
from direct.task import Task

from toontown.battle.BattleGlobals import *
from toontown.hood import ZoneUtil
from toontown.shtiker.PurchaseManagerConstants import *
from toontown.toon.QuickShopper import QuickShopper
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.toonbase.ToontownGlobals import dnaMap, HoodHierarchy



class PurchaseBase(StateData.StateData):
    """
    PurchaseBase(StateData)
    """

    activateMode = 'purchase'
    resizeEvent = 'aspectRatioChanged'

    def __init__(self, toon, doneEvent):
        """
        Create and display a purchase screen for the given Toon with the given amount of points to spend on items.
        Throw the given event name when user is finished

        :type toon: Toon
        """
        StateData.StateData.__init__(self, doneEvent)
        self.toon = toon
        self.fsm = ClassicFSM.ClassicFSM('Purchase', [
            State.State('purchase', self.enterPurchase, self.exitPurchase,
                        ['done']),

            State.State('done', self.enterDone, self.exitDone,
                        ['purchase'])

        ], 'done', 'done')

        self.fsm.enterInitialState()
        self.costMultiplier = 1
        self.quickShopper = QuickShopper(isIncrement=True)

    def load(self, purchaseModels = None):
        # These get passed in from Purchase.py
        if purchaseModels is None:
            purchaseModels = loader.loadModel('phase_4/models/gui/purchase_gui')

        self.music = dnaMap.get(base.cr.playGame.hood.hoodId) + '_gagshop'

        self.jarImage = purchaseModels.find('**/Jar')
        self.jarImage.reparentTo(hidden)

        self.frame = DirectFrame(relief = None)
        self.frame.hide()

        text = TTLocalizer.GagAndGoName if (
            base.localAvatar.zoneId - (base.localAvatar.zoneId % 100)) in [value for values in HoodHierarchy.values() for value in values] \
            else TTLocalizer.GagShopYottName

        self.title = DirectLabel(
            parent = self.frame,
            relief = None,
            pos = (0.0, 0.0, 0.83),
            scale = 1,
            image = purchaseModels.find('**/Goofys_Sign'),
            text = text,
            text_fg = (0.6, 0.2, 0, 1),
            text_scale = 0.09,
            text_wordwrap = 20,
            text_pos = (0, -0.02, 0),
            text_font = ToontownGlobals.getSignFont()
        )

        self.pointDisplay = DirectLabel(
            parent = self.frame,
            relief = None,
            scale = 0.75,
            pos = (-1.01, 0.0, 0.15),
            text = str(self.toon.getMoney()),
            text_scale = 0.2,
            text_fg = (0.95, 0.95, 0, 1),
            text_shadow = (0, 0, 0, 1),
            text_pos = (0, -0.1, 0),
            image = self.jarImage,
            text_font = ToontownGlobals.getSignFont()
        )
        self.isBroke = 0
        self.quickShopper.load()

    def unload(self):
        self.quickShopper.unload()
        self.jarImage.removeNode()
        del self.jarImage
        self.frame.destroy()
        del self.frame
        del self.title
        del self.pointDisplay
        del self.music
        del self.fsm

    def __handleSelection(self, track, level):
        """
        If item level accessible, add purchase button to detail inv menu.

        :type track: int
        :type level: int
        """
        self.handlePurchase(track, level)

    def handlePurchase(self, track, level):
        """
        Subtract points and add item to inv if successful. Print appropriate reject message otherwise.

        :type track: int
        :type level: int
        """
        # TODO: god someone please make this server sided at some point
        # i really hate how it's all handled on the client.

        # Set the base price.
        price = (level + 1) * self.costMultiplier

        # Find out if they have a discount in their
        # current safezone.
        safezoneId = ZoneUtil.getSafeZoneId(self.toon.zoneId)
        if self.toon.zoneId >= 61000:  # Trolley
            safezoneId = ZoneUtil.getSafeZoneId(base.cr.playGame.hood.hoodId)
        discount = self.toon.getPlaygroundGagDiscount(safezoneId)
        if discount:
            price *= discount

        currMoney = self.toon.getMoney()
        deltaMoney = math.ceil(currMoney - price)

        # They can't afford it. (poor + ratio + stinky)
        if deltaMoney < 0:
            return

        returnCode = self.toon.inventory.addItem(track, level)
        if returnCode > 0:
            self.toon.setMoney(deltaMoney)

            # update the inventory display
            self.toon.inventory.updateGUI(track, level)
            self.toon.inventory.showDetail(track, level)

            # Also send a message to the AI for each gag purchased.
            # We didn't always do it this way, but in the presence of
            # resistance chat phrases (in particular, jellybean
            # boosts), we need to keep the AI more in-sync with the
            # client.
            messenger.send('boughtGag')
        return returnCode

    def __handleSelectionAlt(self, track, level):
        self.quickShopper.activate(lambda: self.handlePurchase(track, level))

    def resetStatusText(self, task):
        self.statusLabel['text'] = ''
        return Task.done

    def checkForBroke(self):
        money = self.toon.getMoney()
        self.pointDisplay['text'] = str(money)
        if money == 0:
            if not self.isBroke:
                # no money, no props!
                self.toon.inventory.setActivateModeBroke()
                # set the confirmation text
                taskMgr.doMethodLater(2.25, self.showBrokeMsg, 'showBrokeMsgTask')
                self.isBroke = 1
        else:
            if self.isBroke:
                self.toon.inventory.setActivateMode(self.activateMode)
                taskMgr.remove('showBrokeMsgTask')
                self.isBroke = 0

    def showBrokeMsg(self, task):
        return Task.done

    def handleDone(self, playAgain):
        messenger.send(self.doneEvent, [playAgain])

    # wrapper functions

    def enter(self):
        self.fsm.request('purchase')

    def exit(self):
        self.fsm.request('done')

    ### Purchase state functions ###

    def enterPurchase(self, costMultiplier = 1):
        self.costMultiplier = costMultiplier
        self.frame.show()
        self.toon.inventory.enableUberGags(0)
        self.toon.inventory.show()
        self.toon.inventory.reparentTo(self.frame)
        self.toon.inventory.setActivateMode(self.activateMode)
        self.checkForBroke()
        self.updateInventoryOnResize()
        self.acceptOnce('purchaseOver', self.handleDone)
        self.accept('inventory-selection', self.__handleSelection)
        self.accept('inventory-selection-alt', self.__handleSelectionAlt)
        self.accept(self.resizeEvent, self.updateInventoryOnResize)
        self.accept(self.toon.uniqueName('moneyChange'), self.__moneyChange)

    def exitPurchase(self):
        self.frame.hide()
        self.toon.inventory.enableUberGags(1)
        self.toon.inventory.reparentTo(hidden)
        self.toon.inventory.hide()
        self.ignore('purchaseOver')
        self.ignore('inventory-selection')
        self.ignore('inventory-selection-alt')
        self.ignore(self.resizeEvent)
        self.ignore(self.toon.uniqueName('moneyChange'))
        taskMgr.remove('resetStatusText')
        taskMgr.remove('showBrokeMsgTask')

    @staticmethod
    def updateInventoryOnResize():
        maxScale = (16. / 9.)
        userScale = base.getAspectRatio() / maxScale
        minScale = (3. / 3.)
        minScaleFactor = minScale / maxScale
        maxScaleFactor = 1.0
        scaleFactor = max(min(userScale, maxScaleFactor), minScaleFactor)

        # Make sure the inventory fits within the bounds of the screen on terrible aspect ratios.
        minInvScale = 0.8
        maxInvScale = 1.0
        userDiff = maxScaleFactor - scaleFactor

        # Make our own scale factor here, with 3:3 (or 1.0) as the minimum.
        minInvScaleFactor = (3. / 3.) / maxScale
        invMaxDiff = maxScaleFactor - minInvScaleFactor
        invDiffRatio = min(userDiff / invMaxDiff, 1.0)
        invScale = lerp(maxInvScale, minInvScale, invDiffRatio)
        base.localAvatar.inventory.setScale(invScale)

    def __moneyChange(self, money):
        self.checkForBroke()

    ### Done state functions ###

    def enterDone(self):
        pass

    def exitDone(self):
        pass
