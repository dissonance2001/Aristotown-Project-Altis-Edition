import math
import time
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from direct.gui.OnscreenText import OnscreenText
from direct.gui import DirectGuiGlobals as DGG
from pandac.PandaModules import TextNode, TransparencyAttrib
from toontown.gumball import GumballGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownTimer import ToontownTimer
from toontown.toontowngui import TTDialog

class OutlineText(object):
    def __init__(self, parent, text='', pos=(0, 0), scale=0.05, fg=(1, 1, 1, 1), outline=(0, 0, 0, 1), dist=0.003, precision=8, font=None, align=TextNode.ACenter, wordwrap=None):
        self.parent = parent
        self.precision = precision
        self.dist = dist
        self.outline = []
        kwargs = {'parent': parent, 'text': text, 'pos': pos, 'scale': scale, 'fg': outline, 'align': align, 'mayChange': 1}
        if font:
            kwargs['font'] = font
        if wordwrap:
            kwargs['wordwrap'] = wordwrap
        for index in xrange(precision):
            angle = math.radians((float(index) / precision) * 360.0)
            item = OnscreenText(**kwargs)
            item.setPos(pos[0] + math.cos(angle) * dist, pos[1] + math.sin(angle) * dist)
            self.outline.append(item)
        kwargs['fg'] = fg
        self.text = OnscreenText(**kwargs)

    def setText(self, text):
        self.text.setText(text)
        for item in self.outline:
            item.setText(text)

    def setFg(self, fg):
        self.text.setFg(fg)

    def show(self):
        self.text.show()
        for item in self.outline:
            item.show()

    def hide(self):
        self.text.hide()
        for item in self.outline:
            item.hide()

    def destroy(self):
        self.text.destroy()
        for item in self.outline:
            item.destroy()
        self.outline = []

class GumballMachineGUI(DirectFrame):
    timerDuration = 240
    boosterPrefixes = {
        GumballGlobals.MERIT_SELLBOT: 'merit_sell',
        GumballGlobals.MERIT_CASHBOT: 'merit_cash',
        GumballGlobals.MERIT_LAWBOT: 'merit_law',
        GumballGlobals.MERIT_BOSSBOT: 'merit_boss',
        GumballGlobals.MERIT_GLOBAL: 'merit',
        GumballGlobals.JELLYBEANS_GLOBAL: 'jellybean2',
        GumballGlobals.EXP_GAGS_GLOBAL: 'gag_all',
        GumballGlobals.EXP_GAGS_SUPPORT: 'gag_support',
        GumballGlobals.EXP_GAGS_POWER: 'gag_power',
        GumballGlobals.REWARD_BOSS_GLOBAL: 'eyes',
        GumballGlobals.REWARD_BOSS_SELLBOT: 'sellboss',
        GumballGlobals.REWARD_BOSS_CASHBOT: 'cashboss',
        GumballGlobals.REWARD_BOSS_LAWBOT: 'lawboss',
        GumballGlobals.REWARD_BOSS_BOSSBOT: 'bossboss',
        GumballGlobals.ALL_STAR: 'mainwashere',
        GumballGlobals.RANDOM: 'random',
    }

    def __init__(self, machine):
        self.machine = machine
        self.offerButtons = []
        self.offerCostTexts = []
        self.offerIcons = []
        self.selectedOffer = None
        self.confirmDialog = None
        self.model = None
        self.boosterModel = None
        self.exactModel = False
        self.destroyed = False
        self._loadModels()
        if self.exactModel:
            self._buildClashGUI()
        else:
            self._buildFallbackGUI()
        self.timer = ToontownTimer()
        self.timer.reparentTo(aspect2d)
        try:
            self.timer.posInTopLeftCorner()
        except:
            self.timer.setPos(-1.1, 0, 0.85)
        self.timer.countdown(self.timerDuration, self.close)
        self.timer.show()
        self.refresh()
        self.acceptOnce('escape', self.close)
        self.accept('gumballs-updated', self.refresh)
        if getattr(base, 'localAvatar', None):
            self.accept(base.localAvatar.uniqueName('gumballsChange'), self._gumballsChanged)
        taskMgr.doMethodLater(1.0, self._updateResetTime, self._taskName('reset'))

    def _taskName(self, suffix):
        return 'gumballMachineGUI-%s-%s' % (suffix, id(self))

    def _loadModels(self):
        try:
            self.model = loader.loadModel('phase_3.5/models/gui/gumballmachine/gumball_machine_gui')
            if self.model and not self.model.isEmpty() and not self.model.find('**/base').isEmpty():
                self.exactModel = True
        except:
            self.model = None
        try:
            self.boosterModel = loader.loadModel('phase_3.5/models/gui/boosters')
        except:
            self.boosterModel = None

    def _find(self, name):
        if not self.model or self.model.isEmpty():
            return None
        node = self.model.find('**/%s' % name)
        if node.isEmpty():
            return None
        return node

    def _buttonImages(self, prefix):
        normal = self._find(prefix + 'n')
        pressed = self._find(prefix + 'p')
        hover = self._find(prefix + 'h')
        if normal is None:
            return None
        if pressed is None:
            pressed = normal
        if hover is None:
            hover = normal
        return (normal, pressed, hover, normal)

    def _buildClashGUI(self):
        DirectFrame.__init__(self, parent=aspect2d, relief=None, pos=(0, 0, 0.0052), scale=2.16537, image=self._find('base'), image_scale=(1, 1, 876.0 / 1024.0))
        self.initialiseoptions(GumballMachineGUI)
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.setBin('gui-popup', 100)
        crt = self._find('crt_screen')
        self.scanlines = DirectFrame(parent=self, relief=None, pos=(0, 0, -0.0675), image=crt)
        self.scanlines.setColorScale(1, 1, 1, 0.25)
        self.screen = DirectFrame(parent=self, relief=None, pos=(-0.09171, 0, -0.02587), scale=0.77284, image=self._find('screen_booster'), image_scale=(1, 1, 624.0 / 787.0), text='BOOSTERS', text_pos=(-0.18136, 0.29), text_scale=0.065, text_fg=(1, 1, 1, 1))
        self.resetText = DirectLabel(parent=self.screen, relief=None, text='', text_pos=(-0.18136, 0.2642), text_scale=0.025, text_fg=(1, 1, 1, 1))
        exitImages = self._buttonImages('button_exit_')
        closeKw = {'parent': self, 'relief': None, 'pos': (0.44597, 0, 0.37507), 'scale': 0.09608, 'frameSize': (-0.72, 0.72, -0.72, 0.72), 'command': self.close, 'pressEffect': 0}
        if exitImages:
            closeKw['image'] = exitImages
        self.closeButton = DirectButton(**closeKw)
        self.closeButton.setBin('gui-popup', 120)
        self.balance = OutlineText(parent=self, pos=(-0.22105, 0.34832), scale=0.046502, fg=(1.0, 0.8549, 0.5882, 1), outline=(0.2823, 0.1411, 0.098, 1), dist=0.0036, precision=8, font=ToontownGlobals.getSignFont())
        categoryImages = self._buttonImages('category_booster_')
        self.categoryButton = DirectButton(parent=self, relief=None, pos=(0.38213, 0, -0.06702), scale=0.15344, state=DGG.DISABLED, pressEffect=0)
        if categoryImages:
            self.categoryButton['image'] = categoryImages
            self.categoryButton['image_scale'] = (1, 1, 128.0 / 124.0)
        self.listingRoot = DirectFrame(parent=self, relief=None, pos=(-0.32922, 0, 0.08437), scale=0.15344)
        slotPositions = [(0, 0, 0), (1.25, 0, 0), (0, 0, -1.0), (1.25, 0, -1.0), (0, 0, -2.0), (1.25, 0, -2.0)]
        for index in xrange(6):
            button = DirectButton(parent=self.listingRoot, relief=None, frameSize=(-0.45914, 0.45914, -0.44151, 0.47678), pos=slotPositions[index], command=self.selectOffer, extraArgs=[index], pressEffect=0)
            costText = OutlineText(parent=button, text='', pos=(-0.00588, -0.32922), scale=0.25873, fg=(1, 1, 1, 1), outline=(0, 0, 0, 1), dist=0.018, precision=8, font=ToontownGlobals.getSignFont())
            self.offerButtons.append(button)
            self.offerCostTexts.append(costText)
            self.offerIcons.append(None)
        self.itemName = DirectLabel(parent=self, relief=None, text='NO ITEM SELECTED', text_pos=(0, 0), text_scale=0.035, text_wordwrap=7.64844, text_fg=(1, 1, 1, 1), pos=(0.1227, 0, 0.15275))
        self.itemDesc = DirectLabel(parent=self, relief=None, text='Select an item on the left to purchase.', text_pos=(0, 0), text_scale=0.02, text_wordwrap=13.67725, text_fg=(1, 1, 1, 1), pos=(0.12816, 0, -0.13971))
        self.detailIcon = DirectFrame(parent=self, relief=None, pos=(0.13, 0, 0), scale=0.145)
        buyImages = self._buttonImages('button_buy_')
        buyKw = {'parent': self, 'relief': None, 'pos': (0.19486, 0, -0.23516), 'scale': 0.12404, 'frameSize': (-0.68, 0.68, -0.58, 0.58), 'command': self.buySelected, 'pressEffect': 0}
        if buyImages:
            buyKw['image'] = buyImages
        self.buyButton = DirectButton(**buyKw)
        if buyImages:
            self.buyButton['image_scale'] = (1, 1, 126.0 / 128.0)
        self.buyButton.setBin('gui-popup', 120)
        self.costLabel = DirectLabel(parent=self, relief=None, pos=(0.05879, 0, -0.23839), scale=0.1358, image=self._find('gumballs'), image_scale=(1, 1, 111.0 / 128.0))
        self.detailCost = OutlineText(parent=self.costLabel, text='', pos=(-0.00588, -0.11758), scale=0.38219, fg=(1, 1, 1, 1), outline=(0, 0, 0, 1), dist=0.018, precision=8, font=ToontownGlobals.getSignFont())
        self.pageRoot = DirectFrame(parent=self, relief=None, pos=(-0.08495, 0, -0.37684), scale=0.51148, text='1 / 1', text_scale=0.1, text_fg=(1, 1, 1, 1))
        pageImages = self._buttonImages('button_page_')
        self.pageLeft = DirectButton(parent=self.pageRoot, relief=None, pos=(-0.37625, 0, 0.04703), scale=0.12992, state=DGG.DISABLED)
        self.pageRight = DirectButton(parent=self.pageRoot, relief=None, pos=(0.3761, 0, 0.04703), scale=0.12992, state=DGG.DISABLED)
        if pageImages:
            self.pageLeft['image'] = pageImages
            self.pageLeft['image_scale'] = (-(256.0 / 143.0), 1, 1)
            self.pageRight['image'] = pageImages
            self.pageRight['image_scale'] = ((256.0 / 143.0), 1, 1)
        self.pageLeft['image_color'] = (0.4, 0.4, 0.4, 1)
        self.pageRight['image_color'] = (0.4, 0.4, 0.4, 1)
        self.costLabel.hide()
        self.buyButton.hide()

    def _buildFallbackGUI(self):
        DirectFrame.__init__(self, parent=aspect2d, relief=DGG.RAISED, frameColor=(0.10, 0.16, 0.18, 0.98), frameSize=(-1.13, 1.13, -0.84, 0.84), borderWidth=(0.012, 0.012))
        self.initialiseoptions(GumballMachineGUI)
        self.setBin('gui-popup', 100)
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.screen = DirectFrame(parent=self, relief=DGG.RAISED, frameColor=(0.12, 0.33, 0.33, 1), frameSize=(-0.95, 0.58, -0.60, 0.62), pos=(-0.08, 0, 0.0))
        self.resetText = DirectLabel(parent=self, relief=None, text='', text_scale=0.035, text_fg=(1, 1, 1, 1), pos=(-0.35, 0, 0.52))
        self.balance = OutlineText(parent=self, pos=(-0.57, 0.68), scale=0.055, fg=(1.0, 0.8549, 0.5882, 1), outline=(0.2823, 0.1411, 0.098, 1), font=ToontownGlobals.getSignFont())
        self.closeButton = DirectButton(parent=self, text='X', text_scale=0.08, pos=(0.95, 0, 0.70), command=self.close)
        slotPositions = [(-0.78, 0, 0.31), (-0.45, 0, 0.31), (-0.78, 0, 0.0), (-0.45, 0, 0.0), (-0.78, 0, -0.31), (-0.45, 0, -0.31)]
        for index in xrange(6):
            button = DirectButton(parent=self, relief=DGG.RAISED, frameSize=(-0.13, 0.13, -0.12, 0.12), pos=slotPositions[index], command=self.selectOffer, extraArgs=[index])
            costText = OutlineText(parent=button, text='', pos=(0, -0.16), scale=0.05, fg=(1, 1, 1, 1), outline=(0, 0, 0, 1), font=ToontownGlobals.getSignFont())
            self.offerButtons.append(button)
            self.offerCostTexts.append(costText)
            self.offerIcons.append(None)
        self.itemName = DirectLabel(parent=self, relief=None, text='NO ITEM SELECTED', text_scale=0.055, text_wordwrap=12, pos=(0.46, 0, 0.30))
        self.itemDesc = DirectLabel(parent=self, relief=None, text='Select an item on the left to purchase.', text_scale=0.04, text_wordwrap=12, pos=(0.46, 0, -0.03))
        self.detailIcon = DirectFrame(parent=self, relief=None, pos=(0.46, 0, 0.13), scale=0.12)
        self.buyButton = DirectButton(parent=self, text='BUY', text_scale=0.05, pos=(0.55, 0, -0.37), command=self.buySelected)
        self.costLabel = DirectLabel(parent=self, relief=None, pos=(0.30, 0, -0.37))
        self.detailCost = OutlineText(parent=self.costLabel, text='', pos=(0, 0), scale=0.055, fg=(1, 1, 1, 1), outline=(0, 0, 0, 1), font=ToontownGlobals.getSignFont())
        self.costLabel.hide()
        self.buyButton.hide()

    def _boosterNode(self, boosterType):
        if not self.boosterModel or self.boosterModel.isEmpty():
            return None
        prefix = self.boosterPrefixes.get(int(boosterType))
        if not prefix:
            return None
        node = self.boosterModel.find('**/%s' % prefix)
        if node.isEmpty():
            return None
        return node

    def _offerDescription(self, boosterType, hours, kind):
        descriptions = {
            GumballGlobals.MERIT_SELLBOT: 'Earn extra Invoices for %s hours!',
            GumballGlobals.MERIT_CASHBOT: 'Earn extra Cogbucks for %s hours!',
            GumballGlobals.MERIT_LAWBOT: 'Earn extra Patents for %s hours!',
            GumballGlobals.MERIT_BOSSBOT: 'Earn extra Stock Options\nfor %s hours!',
            GumballGlobals.MERIT_GLOBAL: 'Earn extra Invoices, Cogbucks, Patents, and Stock Options for %s hours!',
            GumballGlobals.JELLYBEANS_GLOBAL: 'Earn additional Jellybeans for %s hours!',
            GumballGlobals.EXP_GAGS_GLOBAL: 'Earn extra Gag Experience for %s hours!',
            GumballGlobals.EXP_GAGS_POWER: 'Earn additional Trap, Zap, Throw, and Drop Gag Experience for %s hours!',
            GumballGlobals.EXP_GAGS_SUPPORT: 'Earn additional Squirt, Sound, Toon-Up, and Lure Gag Experience for %s hours!',
            GumballGlobals.REWARD_BOSS_GLOBAL: 'Earn extra Boss Rewards for %s hours!',
            GumballGlobals.REWARD_BOSS_SELLBOT: 'Earn additional I.O.U.s from the V.P. for %s hours!',
            GumballGlobals.REWARD_BOSS_CASHBOT: 'Earn additional C.F.O. rewards for %s hours!',
            GumballGlobals.REWARD_BOSS_LAWBOT: 'Earn additional Cog Summons from the C.L.O. for %s hours!',
            GumballGlobals.REWARD_BOSS_BOSSBOT: 'Earn additional Pink Slips from the C.E.O. for %s hours!',
            GumballGlobals.ALL_STAR: 'The All-Star Booster boosts EVERYTHING for %s hours!',
            GumballGlobals.RANDOM: 'Earn a random, useful Booster for %s hours! (Includes Daily Boosters and All-Star)',
        }
        text = descriptions.get(int(boosterType), GumballGlobals.getBoosterDescription(boosterType) + ' for %s hours!') % hours
        if kind == 1:
            day = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')[time.localtime().tm_wday]
            text = text.rstrip('!') + '! (%s Only)' % day
        return text

    def _gumballsChanged(self, value=None):
        self.refresh()

    def refresh(self, *args):
        if self.destroyed:
            return
        av = getattr(base, 'localAvatar', None)
        gumballs = av.getGumballs() if av and hasattr(av, 'getGumballs') else 0
        self.balance.setText(str(gumballs))
        offers = self.machine.getOffers() if self.machine else []
        for index in xrange(6):
            button = self.offerButtons[index]
            costText = self.offerCostTexts[index]
            if index >= len(offers):
                button.hide()
                costText.hide()
                continue
            button.show()
            costText.show()
            offer = offers[index]
            offerId, boosterType, cost, hours, kind = offer
            costText.setText('x%s' % cost)
            poor = gumballs < cost
            costText.setFg((1, 0.3, 0.3, 1) if poor else (1, 1, 1, 1))
            node = self._boosterNode(boosterType)
            if node is not None:
                if self.exactModel:
                    button['image'] = node
                    button['image_scale'] = 0.74
                else:
                    button['image'] = node
                    button['image_scale'] = 0.12
                button['image_color'] = (0.35, 0.35, 0.35, 1) if poor else (1, 1, 1, 1)
                button['text'] = ''
            else:
                button['image'] = None
                button['text'] = GumballGlobals.getBoosterName(boosterType)
                button['text_scale'] = 0.08 if self.exactModel else 0.035
                button['text_wordwrap'] = 10
        if self.selectedOffer is not None:
            selectedIndex = self.selectedOffer
            if selectedIndex < len(offers):
                self._setDetail(offers[selectedIndex])
            else:
                self._clearDetail()
        else:
            self._clearDetail()

    def selectOffer(self, index):
        offers = self.machine.getOffers() if self.machine else []
        if not 0 <= int(index) < len(offers):
            return
        self.selectedOffer = int(index)
        self._setDetail(offers[self.selectedOffer])

    def _clearDetail(self):
        self.itemName['text'] = 'NO ITEM SELECTED'
        self.itemDesc['text'] = 'Select an item on the left to purchase.'
        self.detailIcon['image'] = None
        self.costLabel.hide()
        self.buyButton.hide()

    def _setDetail(self, offer):
        offerId, boosterType, cost, hours, kind = offer
        av = getattr(base, 'localAvatar', None)
        gumballs = av.getGumballs() if av and hasattr(av, 'getGumballs') else 0
        name = GumballGlobals.getBoosterName(boosterType)
        self.itemName['text'] = name.upper()
        self.itemDesc['text'] = self._offerDescription(boosterType, hours, kind)
        node = self._boosterNode(boosterType)
        if node is not None:
            self.detailIcon['image'] = node
            self.detailIcon['image_scale'] = 1.0
            self.detailIcon['image_color'] = (1, 1, 1, 1)
        else:
            self.detailIcon['image'] = None
        self.detailCost.setText('x%s' % cost)
        self.detailCost.setFg((1, 0.3, 0.3, 1) if gumballs < cost else (1, 1, 1, 1))
        self.costLabel.show()
        self.buyButton.show()
        if gumballs < cost:
            self.buyButton['state'] = DGG.DISABLED
            self.buyButton['image_color'] = (0.4, 0.4, 0.4, 1)
        else:
            self.buyButton['state'] = DGG.NORMAL
            self.buyButton['image_color'] = (1, 1, 1, 1)

    def buySelected(self):
        if self.selectedOffer is None or not self.machine:
            return
        offers = self.machine.getOffers()
        if not 0 <= self.selectedOffer < len(offers):
            return
        offerId, boosterType, cost, hours, kind = offers[self.selectedOffer]
        av = getattr(base, 'localAvatar', None)
        owns = av.getGumballs() if av and hasattr(av, 'getGumballs') else 0
        text = 'Would you like to purchase %s?\n\nThis will cost: %s Gumballs\nYou have: %s Gumballs' % (GumballGlobals.getBoosterName(boosterType), cost, owns)
        self.confirmDialog = TTDialog.TTDialog(parent=aspect2d, text=text, text_scale=0.06, text_align=TextNode.ACenter, text_wordwrap=25, command=self._confirmPurchase, style=TTDialog.YesNo, buttonPadSF=4)
        self.confirmDialog.setBin('gui-popup', 200)
        self.confirmDialog.show()

    def _confirmPurchase(self, result):
        if self.confirmDialog:
            self.confirmDialog.destroy()
            self.confirmDialog = None
        if result != DGG.DIALOG_OK or self.selectedOffer is None or not self.machine:
            return
        offers = self.machine.getOffers()
        if not 0 <= self.selectedOffer < len(offers):
            return
        self.buyButton['state'] = DGG.DISABLED
        self.buyButton['image_color'] = (0.4, 0.4, 0.4, 1)
        self.itemDesc['text'] = 'Purchasing...'
        self.machine.requestPurchase(offers[self.selectedOffer][0])

    def purchaseResult(self, status, offerId, resolvedType, endTimestamp):
        if status == 0:
            self.refresh()
            self.itemDesc['text'] = '%s purchased!' % GumballGlobals.getBoosterName(resolvedType)
        elif status == 1:
            self.itemDesc['text'] = 'You do not have enough Gumballs.'
        elif status == 2:
            self.itemDesc['text'] = 'That Booster is not available right now.'
        else:
            self.itemDesc['text'] = 'The purchase could not be completed.'

    def _updateResetTime(self, task):
        if self.destroyed:
            return task.done
        now = time.time()
        local = time.localtime(now)
        nextMidnight = time.mktime((local.tm_year, local.tm_mon, local.tm_mday + 1, 0, 0, 0, -1, -1, -1))
        remaining = max(0, int(nextMidnight - now))
        hours = remaining / 3600
        minutes = (remaining % 3600) / 60
        seconds = remaining % 60
        self.resetText['text'] = 'Updates in: %02d:%02d:%02d' % (hours, minutes, seconds)
        task.delayTime = 1.0
        return task.again

    def close(self, *args):
        if self.machine:
            self.machine.closeGUI()

    def destroy(self):
        if self.destroyed:
            return
        self.destroyed = True
        taskMgr.remove(self._taskName('reset'))
        self.ignoreAll()
        if self.confirmDialog:
            self.confirmDialog.destroy()
            self.confirmDialog = None
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
            self.timer.destroy()
            self.timer = None
        for text in self.offerCostTexts:
            text.destroy()
        self.offerCostTexts = []
        if hasattr(self, 'detailCost'):
            self.detailCost.destroy()
        if hasattr(self, 'balance'):
            self.balance.destroy()
        if self.model:
            try:
                self.model.removeNode()
            except:
                pass
            self.model = None
        if self.boosterModel:
            try:
                self.boosterModel.removeNode()
            except:
                pass
            self.boosterModel = None
        self.machine = None
        DirectFrame.destroy(self)
