import decimal
from operator import itemgetter
from direct.gui.DirectGui import *
from direct.directnotify import DirectNotifyGlobal
from pandac.PandaModules import *
from toontown.toon import IOURegistry
from toontown.toon import NPCToons
from toontown.toon import ToonHead
from toontown.toon import ToonDNA
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals

SORT_NONE = 0
SORT_TRACK = 1
SORT_USES = 2


class NPCFriendPanel(DirectScrolledFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('NPCFriendPanel')

    def __init__(self, parent=aspect2d, battle=False, **kw):
        optiondefs = (
            ('relief', None, None),
            ('doneEvent', None, None),
            ('manageScrollBars', 1, self.setManageScrollBars),
            ('autoHideScrollBars', 1, self.setAutoHideScrollBars),
        )
        self.defineoptions(kw, optiondefs)
        sosPanelGui = loader.loadModel('phase_3.5/models/gui/battlegui/sos_panel')
        DirectScrolledFrame.__init__(
            self,
            parent=parent,
            relief=None,
            frameSize=(-0.985, 0.95, -0.595, 0.625),
            canvasSize=self.defaultCanvasSize,
            manageScrollBars=1,
            autoHideScrollBars=1
        )
        self.initialiseoptions(NPCFriendPanel)
        self['verticalScroll_thumb_image'] = sosPanelGui.find('**/sos_thumb')
        self['verticalScroll_resizeThumb'] = 0
        self['verticalScroll_relief'] = None
        self['verticalScroll_thumb_relief'] = None
        self['verticalScroll_thumb_frameSize'] = (-1, 1, -2, 2)
        self['verticalScroll_thumb_image_scale'] = 0.15
        self.verticalScroll.incButton.hide()
        self.verticalScroll.decButton.hide()
        self.horizontalScroll.hide()
        self.battle = battle
        self.rewardsDisabled = self.__rewardsDisabled()
        self.filtersFrame = DirectFrame(
            parent=self,
            relief=None,
            pos=(0.415, 0, 0.31),
            scale=3.33
        )
        searchText = getattr(TTLocalizer, 'FriendsListSearchBarDefaultText', 'Search')
        self.searchBar = DirectEntry(
            parent=self.filtersFrame,
            relief=None,
            width=9,
            frameSize=(-0.43, 0.4, -0.07, 0.07),
            image=sosPanelGui.find('**/sos_search_bar'),
            image_scale=(1, 1, 0.25),
            initialText=searchText,
            text_align=TextNode.ARight,
            text_pos=(0.31, -0.02),
            text_scale=0.08,
            pos=(0.035, 0, 0.16),
            scale=0.25,
            command=self.finishSearch
        )
        self.searchBar.bind(DGG.B1PRESS, self.updateSearch)
        filterImages = (
            sosPanelGui.find('**/filter_neutral'),
            sosPanelGui.find('**/filter_press'),
            sosPanelGui.find('**/filter_hover')
        )
        self.usesButton = DirectButton(
            parent=self.filtersFrame,
            relief=None,
            frameSize=(-0.3, 0.29, -0.10, 0.105),
            image=filterImages,
            image_scale=(1, 1, 0.5),
            text='USES',
            text_pos=(-0.017, -0.035),
            text_scale=0.16,
            pos=(-0.304, 0, 0.16),
            scale=0.25,
            command=self.handlePressedSortButton,
            extraArgs=[SORT_USES]
        )
        self.usesButton.component('text1').setPos(-0.005, -0.055)
        self.trackButton = DirectButton(
            parent=self.filtersFrame,
            relief=None,
            frameSize=(-0.3, 0.29, -0.10, 0.105),
            image=filterImages,
            image_scale=(1, 1, 0.5),
            text='TRACK',
            text_pos=(-0.017, -0.035),
            text_scale=0.16,
            pos=(-0.15, 0, 0.16),
            scale=0.25,
            command=self.handlePressedSortButton,
            extraArgs=[SORT_TRACK]
        )
        self.trackButton.component('text1').setPos(-0.005, -0.055)
        sosPanelGui.removeNode()
        self.xStartOffset = 0.35
        self.cardScale = 0.125
        self.spacingPerCard = 0.0675
        self.spacingPerRow = 0.455
        self.canvasBottomOffset = 0.23
        self.cardList = []
        self.friendDict = {}
        self.fCallable = 0
        self.__lastFriendCardCount = 0
        self.sortMode = SORT_TRACK
        self.sortReverse = False
        self.wantedNPCIDs = []
        self.updateLayout()
        self.accept('wheel_up', self.__scrollWheel, [-1])
        self.accept('wheel_down', self.__scrollWheel, [1])

    def __rewardsDisabled(self):
        conditions = getattr(base.localAvatar, 'battleConditions', {})
        return 'noSOS' in conditions or bool(getattr(base.localAvatar, 'cooldown', 0))

    def __scrollWheel(self, direction):
        if self.canScroll:
            self.verticalScroll.scrollStep(direction * 4)

    def cleanupExit(self):
        self.searchBar['focus'] = 0

    def unload(self):
        self.ignoreAll()
        DirectScrolledFrame.destroy(self)

    def destroy(self):
        self.unload()

    def updateSearch(self, event=None):
        prompt = getattr(TTLocalizer, 'FriendsListSearchBarDefaultText', 'Search')
        if self.searchBar.get() == prompt:
            self.searchBar.set('')

    def finishSearch(self, text=None):
        self.searchBar['focus'] = 0
        self.updateLayoutForSearch()

    def updateLayoutForSearch(self):
        self.wantedNPCIDs = []
        searchText = self.searchBar.get()
        prompt = getattr(TTLocalizer, 'FriendsListSearchBarDefaultText', 'Search')
        if searchText in (prompt, ''):
            self.searchBar.set(prompt)
        else:
            searchText = searchText.lower().replace(' ', '')
            for npcId in self.friendDict.keys():
                definition = IOURegistry.getIOUByNPCId(npcId)
                if definition is None:
                    continue
                nameText = (NPCToons.getNPCName(npcId) or str(npcId)).lower().replace(' ', '')
                trackText = IOURegistry.getTrackName(definition.getGagTrack()).lower().replace(' ', '')
                descriptionText = IOURegistry.getDescription(definition).lower().replace(' ', '')
                if searchText in nameText or searchText in trackText or searchText in descriptionText:
                    self.wantedNPCIDs.append(npcId)
        self.update(self.friendDict, self.fCallable)

    def handlePressedSortButton(self, sortType=SORT_TRACK):
        if self.sortMode == sortType:
            self.sortReverse = not self.sortReverse
        else:
            self.sortReverse = False
        self.sortMode = sortType
        messenger.send('wakeup')
        self.update(self.friendDict, self.fCallable)

    def update(self, friendDict, fCallable=0):
        self.friendDict = dict(friendDict)
        self.fCallable = fCallable
        definitions = []
        for npcId in self.friendDict.keys():
            definition = IOURegistry.getIOUByNPCId(npcId)
            if definition is not None:
                definitions.append(definition)
        if self.wantedNPCIDs:
            definitions = [definition for definition in definitions if definition.getNpcId() in self.wantedNPCIDs]
        wantedCount = len(definitions)
        if wantedCount != self.friendCount:
            self.__lastFriendCardCount = wantedCount
            self.updateLayout()
        if self.sortMode == SORT_TRACK:
            definitions.sort(
                key=lambda definition: (
                    definition.getGagTrack(),
                    10 - definition.getUses()
                ),
                reverse=self.sortReverse
            )
        elif self.sortMode == SORT_USES:
            definitions.sort(key=lambda definition: definition.getUses(), reverse=not self.sortReverse)
        self.rewardsDisabled = self.__rewardsDisabled()
        for i, card in enumerate(self.cardList):
            if i < len(definitions):
                definition = definitions[i]
                count = self.friendDict.get(definition.getNpcId(), 0)
            else:
                definition = None
                count = 0
            card.update(definition, count, fCallable)

    def updateLayout(self):
        for card in self.cardList:
            card.destroy()
        self.cardList = []
        friendCount = self.friendCount
        cardCount = friendCount + (-friendCount % self.cardsPerRow)
        if cardCount:
            xStart = self.defaultCanvasSize[0] + self.xStartOffset
            xOffset = xStart
            yOffset = 0.4
            frameLength = abs(self.defaultCanvasSize[0] - self.defaultCanvasSize[1])
            xSpacing = (frameLength / self.cardsPerRow) + self.spacingPerCard
            for idx in xrange(cardCount):
                card = NPCFriendCard(
                    parent=self.getCanvas(),
                    doneEvent=self['doneEvent'],
                    battle=self.battle,
                    holder=self
                )
                self.cardList.append(card)
                card.setPos(xOffset, 1, yOffset)
                card.setScale(self.cardScale)
                xOffset += xSpacing
                if idx != 0 and (idx + 1) % self.cardsPerRow == 0:
                    xOffset = xStart
                    yOffset -= self.spacingPerRow
            if self.canScroll:
                self['canvasSize'] = (
                    self.defaultCanvasSize[0],
                    self.defaultCanvasSize[1],
                    yOffset + self.canvasBottomOffset,
                    self.defaultCanvasSize[3]
                )
            else:
                self['canvasSize'] = self.defaultCanvasSize
        else:
            self['canvasSize'] = self.defaultCanvasSize
        self.setCanvasSize()
        if self.canScroll:
            self.verticalScroll.thumb.show()
        else:
            self.verticalScroll['value'] = 0
            self.verticalScroll.thumb.hide()

    @property
    def cardsPerRow(self):
        return 3

    @property
    def canScroll(self):
        cardCount = self.friendCount + (-self.friendCount % self.cardsPerRow)
        return cardCount > self.cardsPerRow * 2

    @property
    def friendCount(self):
        return self.__lastFriendCardCount

    @property
    def defaultCanvasSize(self):
        return -0.8, 0.8, -0.625, 0.625


class NPCFriendCard(DirectFrame):
    normalTextColor = (0.3, 0.25, 0.2, 1)
    maxRarity = 5

    def __init__(self, parent=aspect2dp, battle=False, holder=None, functional=True, **kw):
        optiondefs = (
            ('NPCID', None, None),
            ('relief', None, None),
            ('doneEvent', None, None)
        )
        self.defineoptions(kw, optiondefs)
        self.holder = holder
        self.functional = functional
        DirectFrame.__init__(self, parent=parent)
        self.initialiseoptions(NPCFriendCard)
        cardModel = loader.loadModel('phase_3.5/models/gui/battlegui/sos_card')
        gearModel = loader.loadModel('phase_3/models/gui/Gear_icon')
        logo = gearModel.find('**/Gear_icon')
        self.front = DirectFrame(
            parent=self,
            relief=None,
            image=cardModel.find('**/sos_card_bottom'),
            image_scale=5
        )
        self.front.hide()
        self.top = DirectFrame(
            parent=self.front,
            relief=None,
            image=cardModel.find('**/sos_card_top'),
            image_scale=5,
            sortOrder=-1
        )
        self.back = DirectFrame(
            parent=self,
            relief=None,
            image=cardModel.find('**/sos_card_back'),
            image_scale=5,
            geom=logo,
            geom_scale=2,
            geom_pos=(0, 0, 0)
        )
        self.battle = battle
        self.sosTypeInfo = DirectLabel(
            parent=self.front,
            relief=None,
            text='',
            text_font=ToontownGlobals.getBuildingNametagFont(),
            text_fg=(1, 1, 1, 1),
            text_scale=0.5,
            text_align=TextNode.ACenter,
            text_wordwrap=16,
            pos=(0, 0, 1.15)
        )
        self.effectDescription = DirectLabel(
            parent=self.front,
            relief=None,
            text='',
            text_font=ToontownGlobals.getBuildingNametagFont(),
            text_fg=(1, 1, 1, 1),
            text_scale=0.5,
            text_wordwrap=16,
            pos=(0, 0, -1.5)
        )
        self.NPCHead = None
        self.NPCName = DirectLabel(
            parent=self.front,
            relief=None,
            text='',
            text_fg=self.normalTextColor,
            text_scale=0.4,
            text_align=TextNode.ACenter,
            text_wordwrap=8.0,
            pos=(0, 0, -0.75)
        )
        buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**/InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')
        self.sosCallButton = DirectButton(
            parent=self.front,
            relief=None,
            text=TTLocalizer.NPCCallButtonLabel,
            text_fg=self.normalTextColor,
            text_scale=0.28,
            text_align=TextNode.ACenter,
            image=(upButton, downButton, rolloverButton, upButton),
            image_color=(1.0, 0.2, 0.2, 1),
            image0_color=Vec4(1.0, 0.4, 0.4, 1),
            image3_color=Vec4(1.0, 0.4, 0.4, 0.4),
            image_scale=(4.4, 1, 3.6),
            image_pos=Vec3(0, 0, 0.08),
            pos=(1.72, 0, 0.22),
            scale=1.25,
            command=self.__chooseNPCFriend
        )
        self.sosCallButton.hide()
        self.sosCountInfo = DirectLabel(
            parent=self.front,
            relief=None,
            text='',
            text_fg=self.normalTextColor,
            text_scale=0.37,
            text_align=TextNode.ALeft,
            textMayChange=1,
            pos=(-2.23, 0, 0.56),
            sortOrder=100
        )
        self.numGagLabel = DirectLabel(
            parent=self.front,
            relief=None,
            text='Next Gag',
            text_fg=self.normalTextColor,
            text_scale=0.37,
            text_align=TextNode.ARight,
            textMayChange=1,
            pos=(2.165, 0, 0.56),
            sortOrder=100
        )
        cardModel.removeNode()
        gearModel.removeNode()
        buttonModels.removeNode()

    def __chooseNPCFriend(self):
        if self['NPCID'] and self['doneEvent'] and self.sosCallButton['state'] != DGG.DISABLED:
            messenger.send(self['doneEvent'], [{'mode': 'NPCFriend', 'friend': self['NPCID']}])

    def destroy(self):
        if self.NPCHead:
            self.NPCHead.detachNode()
            self.NPCHead.delete()
            self.NPCHead = None
        DirectFrame.destroy(self)

    def update(self, definition, count=0, fCallable=0):
        npcId = definition.getNpcId() if definition is not None else None
        oldNpcId = self['NPCID']
        self['NPCID'] = npcId
        if npcId is None:
            self.showBack()
            self.sosCallButton.hide()
            return
        if oldNpcId != npcId:
            if self.NPCHead:
                self.NPCHead.detachNode()
                self.NPCHead.delete()
                self.NPCHead = None
            self.showFront()
            self.NPCName['text'] = NPCToons.getNPCName(npcId) or str(npcId)
            self.NPCHead = self.createNPCToonHead(npcId, dimension=1.2)
            self.NPCHead.reparentTo(self.front)
            self.NPCHead.setZ(0.15)
            uses = definition.getUses()
            self.numGagLabel['text'] = '%d Gag%s' % (uses, 's' if uses > 1 else '')
            gagTrack = definition.getGagTrack()
            descriptionText = IOURegistry.getDescription(definition).upper()
            if gagTrack == -1:
                color = (1, 1, 1, 1)
                sosText = 'ALL GAGS'
            else:
                color = (
                    ToontownBattleGlobals.TrackColors[gagTrack][0],
                    ToontownBattleGlobals.TrackColors[gagTrack][1],
                    ToontownBattleGlobals.TrackColors[gagTrack][2],
                    1
                )
                sosText = IOURegistry.getTrackName(gagTrack)
            self.top['image_color'] = color
            self.sosTypeInfo['text'] = sosText.upper()
            self.effectDescription['text'] = descriptionText
        if fCallable:
            self.sosCallButton.show()
        else:
            self.sosCallButton.hide()
        if count > 0:
            newCount = count
            countMod = ''
            if count >= 1000000000:
                newCount = count / 1000000000.0
                countMod = 'b'
            elif count >= 1000000:
                newCount = count / 1000000.0
                countMod = 'm'
            elif count >= 1000:
                newCount = count / 1000.0
                countMod = 'k'
            if countMod:
                value = decimal.Decimal(str(newCount)).quantize(decimal.Decimal('0.1'), rounding=decimal.ROUND_DOWN)
                countValue = ('%s' % value).rstrip('0').rstrip('.') + countMod
            else:
                countValue = str(count)
            countText = '%s Left' % countValue
            self.sosCallButton['state'] = DGG.DISABLED if self.holder.rewardsDisabled else DGG.NORMAL
        else:
            countText = 'Unavailable'
            self.sosCallButton['state'] = DGG.DISABLED
        self.sosCountInfo['text'] = countText

    def showFront(self):
        self.front.show()
        self.back.hide()

    def showBack(self):
        self.front.hide()
        self.back.show()

    def createNPCToonHead(self, npcId, dimension=0.5):
        npcInfo = NPCToons.NPCToonDict[npcId]
        dnaList = npcInfo[2]
        gender = npcInfo[3]
        if dnaList == 'r':
            dnaList = NPCToons.getRandomDNA(npcId, gender)
        dna = ToonDNA.ToonDNA()
        dna.newToonFromProperties(*dnaList)
        head = ToonHead.ToonHead()
        head.setupHead(dna, forGui=1)
        self.fitGeometry(head, fFlip=1, dimension=dimension)
        return head

    def fitGeometry(self, geom, fFlip=0, dimension=0.5):
        p1 = Point3()
        p2 = Point3()
        geom.calcTightBounds(p1, p2)
        if fFlip:
            t = p1[0]
            p1.setX(-p2[0])
            p2.setX(-t)
        d = p2 - p1
        biggest = max(d[0], d[2])
        s = dimension / biggest
        mid = (p1 + d / 2.0) * s
        geomXform = hidden.attachNewNode('geomXform')
        for child in geom.getChildren():
            child.reparentTo(geomXform)
        geomXform.setPosHprScale(-mid[0], -mid[1] + 1, -mid[2], 180, 0, 0, s, s, s)
        geomXform.reparentTo(geom)
