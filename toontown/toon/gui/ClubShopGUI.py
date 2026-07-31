import math

from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from direct.gui import DirectGuiGlobals as DGG
from pandac.PandaModules import CullBinAttrib, LineSegs, NodePath, TextNode, TransparencyAttrib

from toontown.club import ClubGlobals
from toontown.club.ClubClasses import ClubIcon
from toontown.club.ClubIconGUI import ClubIconGUI
from toontown.toonbase import ToontownGlobals
from toontown.toon.socialpanel.clubs.general.ClubLevelShield import ClubLevelShield


class ClubShopGUI(DirectFrame):
    """Corporate Clash Club Shop catalogue build for Project Altis/Python 2."""

    doneEvent = 'club-shop-gui-done'

    CATEGORY_ITEMS = 'items'
    CATEGORY_BOOSTERS = 'boosters'
    CATEGORY_CUSTOMIZATION = 'customization'

    # The ClubShop_Base model is the large central board only.  The bank is
    # positioned separately, as it is in Corporate Clash.
    BOARD_WIDTH = 1.93
    BOARD_HEIGHT = 1.52
    BOARD_POS = (-0.02, 0, 0.005)

    TAB_POSITIONS = {
        CATEGORY_ITEMS: (-0.49, 0, 0.438),
        CATEGORY_BOOSTERS: (-0.02, 0, 0.438),
        CATEGORY_CUSTOMIZATION: (0.49, 0, 0.438),
    }

    UPGRADE_ENTRIES = (
        {
            'kind': 'upgrade',
            'id': 10001,
            'name': 'Member Capacity +5',
            'category': 'upgrade-members',
            'cost': 10000,
            'level': 15,
            'payload': 5,
            'description': 'Increase the maximum number of members in your Club by 5.',
        },
        {
            'kind': 'upgrade',
            'id': 10002,
            'name': 'Booster Slot +1',
            'category': 'upgrade-booster-slot',
            'cost': 100000,
            'level': 100,
            'payload': 1,
            'description': 'Increase the number of Club Boosters that can run at the same time by 1.',
        },
        {
            'kind': 'upgrade',
            'id': 10003,
            'name': 'Name Rewrite',
            'category': 'upgrade-name-rewrite',
            'cost': 30000,
            'level': 25,
            'payload': 1,
            'description': 'Purchase a rewrite for your Club name.',
        },
    )

    BOOSTER_SUBCATEGORIES = (
        ('Gags', ('booster-gag',)),
        ('Activities', ('booster-activity',)),
        ('Merits', ('booster-merit',)),
        ('Department Exp.', ('booster-department',)),
        ('Boss Rewards', ('booster-reward',)),
        ('Universal', ('booster-universal',)),
    )

    CUSTOMIZATION_SUBCATEGORIES = (
        ('Icon Images', ('icon',)),
        ('Icon Detail', ('background',)),
        ('Theme Colors', ('theme',)),
        ('Detail Colors', ('detail-color',)),
    )

    def __init__(self, npc=None):
        DirectFrame.__init__(
            self,
            parent=aspect2d,
            relief=None,
            frameSize=(-1.42, 1.42, -0.89, 0.89),
            frameColor=(0, 0, 0, 0),
        )
        self.initialiseoptions(ClubShopGUI)
        self.setBin('sorted-gui-popup', 690)
        self.setTransparency(TransparencyAttrib.MAlpha)

        # Match the on-screen proportions of the Corporate Clash reference.
        # The source board is authored for a wider UI and otherwise fills nearly
        # the entire Altis window.  Keep X/Z independent so the attached bank and
        # board retain the exact reference footprint on 4:3 and widescreen.
        self.setScale(1.20, 1, 1.18)
        self.setPos(-0.10, 0, -0.027)

        self.npc = npc
        self.gui = loader.loadModel('phase_3.5/models/gui/clubs/club_shop')
        self.creationGui = loader.loadModel('phase_3.5/models/gui/clubs/club_creation')
        self.jarGui = loader.loadModel('phase_3.5/models/gui/jar_gui')
        self.boosterGui = loader.loadModel('phase_3.5/models/gui/boosters')
        for model in (self.gui, self.creationGui, self.jarGui, self.boosterGui):
            try:
                model.setTransparency(TransparencyAttrib.MAlpha)
            except:
                pass

        self._nodeCache = {}
        self._assetLog = {}
        self._destroyed = False

        self.category = self.CATEGORY_ITEMS
        self.subcategoryIndexes = {
            self.CATEGORY_ITEMS: 0,
            self.CATEGORY_BOOSTERS: 0,
            self.CATEGORY_CUSTOMIZATION: 0,
        }
        self.page = 0
        self.selectedEntry = None
        self.itemButtons = []
        self.previewNodes = []
        self.tabButtons = {}
        self._colorPulseVisuals = []
        self._colorPulseTaskName = 'ClubShopGUI-colorPulse-%s' % id(self)

        self._makeBackground()
        self._makeTitleAndTabs()
        self._makeItemArea()
        self._makeInformationArea()
        self._makeClubBank()
        self._makeCloseButton()
        taskMgr.doMethodLater(0.05, self._updateColorPulseVisuals,
                              self._colorPulseTaskName)

        self.accept('club-state-updated', self._stateUpdated)
        self.accept('club-notification', self._notification)
        self.acceptOnce('escape', self.destroy)

        mapHotkey = getattr(base, 'MAP_PAGE_HOTKEY', None)
        if mapHotkey and mapHotkey != 'escape':
            self.acceptOnce(mapHotkey, self.destroy)

        try:
            self.accept(base.localAvatar.uniqueName('moneyChange'), self._moneyChanged)
        except:
            pass

        self._refreshHeader()
        self.setCategory(self.CATEGORY_ITEMS)

        try:
            base.localAvatar.disableControls()
        except:
            pass

        print('[Clubs] Club Shop GUI Build 27 opened.')

    # ------------------------------------------------------------------
    # Model searching and fitting
    # ------------------------------------------------------------------
    def _normaliseName(self, name):
        return str(name).lower().replace('-', '').replace('_', '').replace(' ', '')

    def _allNodes(self, model):
        key = id(model)
        cached = self._nodeCache.get(key)
        if cached is not None:
            return cached
        nodes = []
        try:
            matches = model.findAllMatches('**/*')
            for index in xrange(matches.getNumPaths()):
                nodes.append(matches.getPath(index))
        except:
            pass
        self._nodeCache[key] = nodes
        return nodes

    def _nodeBounds(self, node):
        if node is None or node.isEmpty():
            return None
        try:
            bounds = node.getTightBounds()
        except:
            return None
        if not bounds or bounds[0] is None or bounds[1] is None:
            return None
        low, high = bounds
        width = high.getX() - low.getX()
        height = high.getZ() - low.getZ()
        if width <= 0.00001 or height <= 0.00001:
            return None
        return (
            width,
            height,
            (low.getX() + high.getX()) * 0.5,
            (low.getZ() + high.getZ()) * 0.5,
        )

    def _isGeomNode(self, node):
        try:
            return node.node().getType().getName() == 'GeomNode'
        except:
            return False

    def _candidateScore(self, node, words, excluded, preferredAspect=None,
                        preferGeom=False, preferContainer=False):
        name = self._normaliseName(node.getName())
        wanted = tuple(self._normaliseName(word) for word in words)
        blocked = tuple(self._normaliseName(word) for word in excluded)

        if not all(word in name for word in wanted):
            return None
        if any(word in name for word in blocked):
            return None

        bounds = self._nodeBounds(node)
        if bounds is None:
            return None
        width, height, centerX, centerZ = bounds

        score = 200.0 + (len(wanted) * 90.0)
        joined = ''.join(wanted)
        if joined and joined in name:
            score += 80.0
        if name == joined:
            score += 90.0

        isGeom = self._isGeomNode(node)
        if preferGeom:
            score += 50.0 if isGeom else -20.0
        if preferContainer:
            try:
                score += 35.0 if node.getNumChildren() else -10.0
            except:
                pass

        area = max(0.000001, width * height)
        score += min(75.0, math.log(area + 1.0) * 15.0)

        if preferredAspect is not None:
            aspect = width / float(height)
            score += max(-70.0, 60.0 - abs(aspect - preferredAspect) * 42.0)

        # Avoid accidentally taking the whole shop or a full bank portrait when
        # a smaller, correctly named leaf is present.
        if name in ('root', 'modelroot', 'clubshop', 'clubshopbase', 'base'):
            score -= 120.0
        if 'portrait' in name or 'picture' in name:
            score -= 60.0

        return score

    def _findBest(self, model, groups, excluded=(), preferredAspect=None,
                  preferGeom=False, preferContainer=False):
        bestNode = None
        bestScore = None
        for words in groups:
            for node in self._allNodes(model):
                score = self._candidateScore(
                    node,
                    words,
                    excluded,
                    preferredAspect=preferredAspect,
                    preferGeom=preferGeom,
                    preferContainer=preferContainer,
                )
                if score is not None and (bestScore is None or score > bestScore):
                    bestNode = node
                    bestScore = score
        return bestNode

    def _findExact(self, model, names):
        for name in names:
            node = model.find('**/%s' % name)
            if node is not None and not node.isEmpty() and self._nodeBounds(node) is not None:
                return node
        return None

    def _findStateNode(self, model, groups, states, excluded=(),
                       preferredAspect=None, preferContainer=True):
        stateGroups = []
        for words in groups:
            for state in states:
                stateGroups.append(tuple(words) + (state,))
        node = self._findBest(
            model,
            stateGroups,
            excluded=excluded,
            preferredAspect=preferredAspect,
            preferContainer=preferContainer,
        )
        if node is None:
            node = self._findBest(
                model,
                groups,
                excluded=excluded,
                preferredAspect=preferredAspect,
                preferContainer=preferContainer,
            )
        return node

    def _findStateSet(self, model, groups, excluded=(), preferredAspect=None):
        normal = self._findStateNode(
            model, groups,
            ('neutral', 'normal', 'up', 'idle', 'n'),
            excluded=tuple(excluded) + ('press', 'hover', 'down', 'selected', 'active'),
            preferredAspect=preferredAspect,
        )
        if normal is None:
            return None

        pressed = self._findStateNode(
            model, groups,
            ('press', 'pressed', 'down', 'p'),
            excluded=tuple(excluded) + ('hover', 'selected', 'active'),
            preferredAspect=preferredAspect,
        )
        hover = self._findStateNode(
            model, groups,
            ('hover', 'rollover', 'over', 'h'),
            excluded=tuple(excluded) + ('press', 'selected', 'active'),
            preferredAspect=preferredAspect,
        )
        disabled = self._findStateNode(
            model, groups,
            ('disabled', 'disable', 'd'),
            excluded=tuple(excluded) + ('press', 'hover', 'selected', 'active'),
            preferredAspect=preferredAspect,
        )
        return (normal, pressed or normal, hover or normal, disabled or normal)

    def _fitTransform(self, node, targetWidth, targetHeight, preserveAspect=True):
        bounds = self._nodeBounds(node)
        if bounds is None:
            return ((1, 1, 1), (0, 0, 0))
        width, height, centerX, centerZ = bounds
        scaleX = targetWidth / float(width)
        scaleZ = targetHeight / float(height)
        if preserveAspect:
            uniform = min(scaleX, scaleZ)
            scaleX = uniform
            scaleZ = uniform
        imagePos = (-centerX * scaleX, 0, -centerZ * scaleZ)
        return ((scaleX, 1, scaleZ), imagePos)

    def _copyFittedNode(self, node, parent, targetWidth, targetHeight,
                        pos=(0, 0, 0), preserveAspect=True):
        if node is None or node.isEmpty():
            return None
        copy = node.copyTo(parent)
        scale, localPos = self._fitTransform(node, targetWidth, targetHeight, preserveAspect)
        copy.setScale(*scale)
        copy.setPos(pos[0] + localPos[0], pos[1], pos[2] + localPos[2])
        copy.setTransparency(TransparencyAttrib.MAlpha)
        return copy

    def _setGuiLayer(self, node, sortOrder, priority=100):
        """Force a GUI bin/depth state onto a node and every copied child.

        Altis keeps render-state data on the GeomNodes inside BAM models, so
        setting the bin on only the copied root is not enough.  Applying the
        state recursively keeps CurrencyExtension behind ClubShop_Base without
        relying on NodePath.setSort(), which is unavailable in this runtime.
        """
        if node is None or node.isEmpty():
            return

        targets = [node]
        try:
            matches = node.findAllMatches('**/*')
            for index in xrange(matches.getNumPaths()):
                targets.append(matches.getPath(index))
        except:
            pass

        for target in targets:
            # Project Altis' older Panda build does not reliably preserve a
            # child NodePath.setBin() over render states embedded in BAM
            # GeomNodes.  Install the CullBinAttrib itself at a deliberately
            # high priority, then keep setBin as a compatibility fallback.
            try:
                target.setAttrib(
                    CullBinAttrib.make('sorted-gui-popup', sortOrder),
                    priority
                )
            except:
                try:
                    target.setBin('sorted-gui-popup', sortOrder)
                except:
                    pass

            try:
                target.setDepthTest(False, priority)
            except:
                try:
                    target.setDepthTest(False)
                except:
                    pass

            try:
                target.setDepthWrite(False, priority)
            except:
                try:
                    target.setDepthWrite(False)
                except:
                    pass

    def _findLevelTagNode(self):
        """Return Badge_Icon_Orange from the Social Panel BAM."""
        from toontown.toon.socialpanel.SocialPanelGlobals import sp_gui
        return self._findExact(sp_gui, ('Badge_Icon_Orange',))

    def _logAsset(self, label, node):
        if label in self._assetLog:
            return
        self._assetLog[label] = True
        name = '<fallback>' if node is None else node.getName()
        print('[Clubs] Club Shop asset %s: %s' % (label, name))

    # ------------------------------------------------------------------
    # Main layout
    # ------------------------------------------------------------------
    def _makeBackground(self):
        board = self._findExact(self.gui, ('ClubShop_Base', 'ClubShopBase', 'Shop_Base'))
        if board is None:
            board = self._findBest(
                self.gui,
                (('club', 'shop', 'base'), ('shop', 'base'), ('chalkboard',), ('board', 'base')),
                excluded=('bank', 'item', 'tab', 'button'),
                preferredAspect=1.35,
                preferContainer=True,
            )
        self._logAsset('main-board', board)

        if board is not None:
            boardScale, boardImagePos = self._fitTransform(
                board,
                self.BOARD_WIDTH,
                self.BOARD_HEIGHT,
                preserveAspect=False,
            )
            self.board = DirectFrame(
                parent=self,
                relief=None,
                image=board,
                image_scale=boardScale,
                image_pos=boardImagePos,
                pos=self.BOARD_POS,
            )
            self.board.setTransparency(TransparencyAttrib.MAlpha)
        else:
            self.board = DirectFrame(
                parent=self,
                relief=DGG.RIDGE,
                frameSize=(-1.18, 1.18, -0.78, 0.78),
                frameColor=(0.27, 0.58, 0.50, 1),
                borderWidth=(0.045, 0.045),
                pos=self.BOARD_POS,
            )

        # Corporate Clash renders ClubShop_Base at ClubShopBin (690).
        self.board.setBin('sorted-gui-popup', 690)

    def _makeTitleAndTabs(self):
        # Corporate Clash uses the narrow, hand-drawn Minnie lettering in
        # uppercase.  The font already contains its painted edge; stacking
        # extra copies produced Build 11's hollow/blurred title.
        self.titleOutline = []
        self.title = DirectLabel(
            parent=self,
            relief=None,
            text='CLUB SHOP',
            text_font=ToontownGlobals.getMinnieFont(),
            text_scale=0.078,
            text_fg=(0.31, 0.16, 0.085, 1),
            pos=(-0.02, 0, 0.642),
        )

        tabDefinitions = (
            (
                self.CATEGORY_ITEMS,
                'ITEMS\n& UPGRADES',
                (('items', 'upgrades'), ('item', 'upgrade'), ('items',), ('upgrade',)),
                1.18,
                0.49,
            ),
            (
                self.CATEGORY_BOOSTERS,
                'CLUB\nBOOSTERS',
                (('club', 'boosters'), ('club', 'booster'), ('boosters',), ('booster',)),
                1.12,
                0.49,
            ),
            (
                self.CATEGORY_CUSTOMIZATION,
                'CUSTOMIZATION',
                (('customization',), ('customisation',), ('custom',)),
                1.14,
                0.47,
            ),
        )

        for category, fallbackText, groups, width, height in tabDefinitions:
            images = self._findStateSet(
                self.gui,
                groups,
                excluded=('itempaper', 'itemcard', 'base', 'bank', 'coin', 'iconimage'),
                preferredAspect=2.1,
            )
            self._logAsset('%s-tab' % category, images[0] if images else None)

            kwargs = {
                'parent': self,
                'relief': None,
                'frameSize': (-0.255, 0.255, -0.125, 0.125),
                'pos': self.TAB_POSITIONS[category],
                'command': self.setCategory,
                'extraArgs': [category],
                'pressEffect': 0,
            }
            if images is not None:
                imageScale, imagePos = self._fitTransform(images[0], width, height, preserveAspect=True)
                kwargs['image'] = images
                kwargs['image_scale'] = imageScale
                kwargs['image_pos'] = imagePos
            else:
                kwargs.update({
                    'text': fallbackText,
                    'text_font': ToontownGlobals.getSignFont(),
                    'text_scale': 0.047 if category != self.CATEGORY_CUSTOMIZATION else 0.039,
                    'text_fg': (1.0, 0.84, 0.25, 1),
                    'text_shadow': (0.18, 0.06, 0.02, 1),
                    'text_align': TextNode.ACenter,
                })

            button = DirectButton(**kwargs)
            button.setTransparency(TransparencyAttrib.MAlpha)
            self.tabButtons[category] = button

        self.tabIndicator = self._makeTabScribble()

    def _makeTabScribble(self):
        # Use Corporate Clash's actual painted selection scribble from
        # club_shop.bam.  Earlier builds drew replacement LineSegs, which did
        # not match the source artwork.
        indicatorNode = self._findExact(self.gui, ('CategorySelectIndicator',))
        self._logAsset('category-select-indicator', indicatorNode)

        if indicatorNode is not None:
            indicator = DirectLabel(
                parent=self,
                relief=None,
                frameSize=(0, 0, 0, 0),
                geom=indicatorNode,
                geom_scale=(0.4, 1, 0.4),
                geom_pos=(0, 0, 0.01),
                geom_color=(1, 1, 1, 0.85),
            )
            indicator.setTransparency(TransparencyAttrib.MAlpha)
            indicator.setBin('sorted-gui-popup', 694)
            return indicator

        # Compatibility fallback for an incomplete/repacked Club Shop BAM.
        root = self.attachNewNode('clubShopTabScribbleFallback')
        root.setBin('sorted-gui-popup', 694)
        root.setDepthTest(False)
        root.setDepthWrite(False)
        lines = LineSegs('clubShopTabScribbleFallbackRing')
        lines.setColor(0.94, 0.12, 0.08, 0.76)
        lines.setThickness(2.7)
        pointCount = 48
        for index in xrange(pointCount + 1):
            angle = (math.pi * 2.0 * index) / float(pointCount)
            x = math.cos(angle) * 0.205
            z = math.sin(angle) * 0.088
            if index == 0:
                lines.moveTo(x, -0.002, z)
            else:
                lines.drawTo(x, -0.002, z)
        root.attachNewNode(lines.create())
        return root

    def _makeChalkArrow(self, direction=1):
        root = NodePath('clubShopChalkArrow')
        lines = LineSegs('clubShopChalkArrowLines')
        lines.setColor(0.91, 0.95, 0.91, 0.82)
        lines.setThickness(3.0)

        points = (
            (-0.10, 0.040),
            (0.018, 0.040),
            (0.018, 0.085),
            (0.105, 0.000),
            (0.018, -0.085),
            (0.018, -0.040),
            (-0.10, -0.040),
            (-0.10, 0.040),
        )
        for index, point in enumerate(points):
            x = point[0] * direction
            z = point[1]
            if index == 0:
                lines.moveTo(x, 0, z)
            else:
                lines.drawTo(x, 0, z)
        root.attachNewNode(lines.create())

        faint = LineSegs('clubShopChalkArrowFaint')
        faint.setColor(1, 1, 1, 0.28)
        faint.setThickness(1.5)
        for index, point in enumerate(points):
            x = (point[0] + 0.006) * direction
            z = point[1] - 0.005
            if index == 0:
                faint.moveTo(x, -0.001, z)
            else:
                faint.drawTo(x, -0.001, z)
        root.attachNewNode(faint.create())
        root.setTransparency(TransparencyAttrib.MAlpha)
        return root

    def _getChalkArrowStates(self):
        """Return the original Corporate Clash chalk-arrow button states."""
        neutral = self._findExact(self.gui, ('Arrow_Neutral',))
        hover = self._findExact(self.gui, ('Arrow_Hover',))
        if neutral is None or hover is None:
            return None
        # DirectButton state order: normal, pressed, rollover, disabled.
        return (neutral, neutral, hover, neutral)

    def _makeArrowButton(self, direction, position, imageScale, frameSize,
                         command, extraArgs):
        states = self._getChalkArrowStates()
        kwargs = {
            'parent': self,
            'relief': None,
            'frameSize': frameSize,
            'pos': position,
            'command': command,
            'extraArgs': extraArgs,
            'pressEffect': 0,
        }

        if states is not None:
            # Use the authored Arrow_Neutral and Arrow_Hover textures from
            # club_shop.bam, exactly as Corporate Clash does.  The source
            # arrow points left, so rotate only the right-facing buttons.
            kwargs.update({
                'image': states,
                'image_scale': imageScale,
                'image_color': (0.7, 0.7, 0.7, 1.0),
            })
            if direction > 0:
                kwargs['image_hpr'] = (0, 0, 180)
        else:
            # Compatibility fallback for a repacked/incomplete Club Shop BAM.
            kwargs.update({
                'geom': self._makeChalkArrow(direction),
                'geom_scale': 0.43 if imageScale <= 0.08 else 0.47,
            })

        button = DirectButton(**kwargs)
        button.setTransparency(TransparencyAttrib.MAlpha)
        return button

    def _makeItemArea(self):
        self.categoryPreviousButton = self._makeArrowButton(
            -1,
            (-0.675, 0, 0.205),
            0.075,
            (-0.105, 0.105, -0.085, 0.085),
            self.changeSubcategory,
            [-1],
        )
        self.categoryNextButton = self._makeArrowButton(
            1,
            (0.025, 0, 0.205),
            0.075,
            (-0.105, 0.105, -0.085, 0.085),
            self.changeSubcategory,
            [1],
        )

        self.categoryTitle = DirectLabel(
            parent=self,
            relief=None,
            text='',
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.052,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0.10, 0.25, 0.22, 1),
            pos=(-0.310, 0, 0.188),
        )

        self.previousButton = self._makeArrowButton(
            -1,
            (-0.650, 0, -0.455),
            0.12,
            (-0.115, 0.115, -0.095, 0.095),
            self.changePage,
            [-1],
        )
        self.nextButton = self._makeArrowButton(
            1,
            (0.010, 0, -0.455),
            0.12,
            (-0.115, 0.115, -0.095, 0.095),
            self.changePage,
            [1],
        )

        self.pageLabel = DirectLabel(
            parent=self,
            relief=None,
            text='1 / 1',
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.070,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0.10, 0.25, 0.22, 1),
            pos=(-0.335, 0, -0.480),
        )

    def _findWoodTitleNode(self):
        node = self._findExact(self.gui, (
            'No_Item_Selected', 'NoItemSelected', 'Selection_Title',
            'Selected_Title', 'Title_Board', 'Wooden_Title',
        ))
        if node is None:
            node = self._findBest(
                self.gui,
                (
                    ('no', 'item', 'selected'),
                    ('selection', 'title'),
                    ('selected', 'title'),
                    ('wood', 'title'),
                    ('title', 'board'),
                ),
                excluded=('tab', 'bank', 'base'),
                preferredAspect=5.0,
                preferContainer=True,
            )
        return node

    def _findCoinNode(self):
        node = self._findExact(self.gui, (
            'ClubCoin', 'Club_Coin', 'clubCoin', 'club_coin',
            'Choc_Coin', 'Coin', 'coin', 'choc',
        ))
        if node is not None:
            bounds = self._nodeBounds(node)
            if bounds is not None and bounds[0] / float(bounds[1]) < 2.2:
                return node
        return self._findBest(
            self.gui,
            (
                ('club', 'coin'),
                ('choc', 'coin'),
                ('currency', 'coin'),
                ('coin',),
                ('choc',),
            ),
            excluded=('bank', 'portrait', 'picture', 'frame', 'title', 'text', 'jar'),
            preferredAspect=1.0,
            preferGeom=True,
        )

    def _makeInformationArea(self):
        # Title_Board belongs to the Club Creation sheet, not club_shop.bam.
        # Using it here reproduces the painted wooden selection header from
        # Corporate Clash instead of the temporary DirectGUI brown rectangle.
        titleNode = self._findExact(self.creationGui, ('Title_Board',))
        if titleNode is None:
            titleNode = self._findBest(
                self.creationGui,
                (('title', 'board'), ('wood', 'title'), ('selection', 'title')),
                excluded=('button', 'confirm', 'cancel', 'arrow'),
                preferredAspect=5.0,
                preferGeom=True,
            )
        self._logAsset('selection-title', titleNode)

        titleKwargs = {
            'parent': self,
            'relief': None,
            'text': 'No Item Selected',
            'text_font': ToontownGlobals.getToonFont(),
            'text_scale': 0.038,
            'text_fg': (1.0, 0.91, 0.76, 1),
            'text_shadow': (0.28, 0.16, 0.09, 1),
            'text_pos': (0, -0.013),
            'pos': (0.520, 0, 0.205),
        }
        if titleNode is not None:
            titleScale, titlePos = self._fitTransform(
                titleNode, 1.11, 0.165, preserveAspect=False)
            titleKwargs['image'] = titleNode
            titleKwargs['image_scale'] = titleScale
            titleKwargs['image_pos'] = titlePos
        else:
            titleKwargs.update({
                'relief': DGG.RIDGE,
                'frameColor': (0.48, 0.27, 0.16, 1),
                'frameSize': (-0.555, 0.555, -0.078, 0.078),
                'borderWidth': (0.009, 0.009),
            })
        self.selectionTitle = DirectFrame(**titleKwargs)
        self.selectionTitle.setTransparency(TransparencyAttrib.MAlpha)

        self.previewFrame = DirectFrame(
            parent=self,
            relief=None,
            frameSize=(-0.21, 0.21, -0.21, 0.21),
            pos=(0.455, 0, -0.025),
        )

        self.description = DirectLabel(
            parent=self,
            relief=None,
            text='Select an item for more info.',
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.029,
            text_wordwrap=19,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0.10, 0.25, 0.22, 1),
            pos=(0.475, 0, -0.285),
        )

        coinNode = self._findCoinNode()
        self._logAsset('club-coin', coinNode)
        coinScale = (0.085, 1, 0.085)
        coinPos = (0, 0, 0)
        if coinNode is not None:
            coinScale, coinPos = self._fitTransform(coinNode, 0.15, 0.15, preserveAspect=True)

        self.priceIcon = DirectLabel(
            parent=self,
            relief=None,
            image=coinNode,
            image_scale=coinScale,
            image_pos=coinPos,
            pos=(0.265, 0, -0.455),
        )
        self.priceIcon.setTransparency(TransparencyAttrib.MAlpha)

        self.priceLabel = DirectLabel(
            parent=self,
            relief=None,
            text='x0',
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.058,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0.10, 0.25, 0.22, 1),
            pos=(0.350, 0, -0.475),
        )

        confirmStates = self._findStateSet(
            self.creationGui,
            (('confirm',), ('check',), ('accept',)),
            preferredAspect=1.0,
        )
        if confirmStates is None:
            confirmStates = self._findStateSet(
                self.gui,
                (('confirm',), ('check',), ('purchase',)),
                excluded=('item', 'title'),
                preferredAspect=1.0,
            )
        self._logAsset('purchase-button', confirmStates[0] if confirmStates else None)

        purchaseKwargs = {
            'parent': self,
            'relief': None,
            'frameSize': (-0.18, 0.18, -0.15, 0.15),
            'pos': (0.620, 0, -0.455),
            'command': self.performSelectedAction,
            'pressEffect': 0,
            'state': DGG.DISABLED,
        }
        if confirmStates is not None:
            imageScale, imagePos = self._fitTransform(confirmStates[0], 0.23, 0.20, preserveAspect=True)
            purchaseKwargs['image'] = confirmStates
            purchaseKwargs['image_scale'] = imageScale
            purchaseKwargs['image_pos'] = imagePos
        else:
            purchaseKwargs.update({
                'text': 'OK',
                'text_font': ToontownGlobals.getToonFont(),
                'text_scale': 0.062,
                'text_fg': (0.12, 0.34, 0.12, 1),
                'frameColor': (0.64, 0.86, 0.60, 1),
                'borderWidth': (0.010, 0.010),
            })
        self.purchaseButton = DirectButton(**purchaseKwargs)
        self.purchaseButton.setTransparency(TransparencyAttrib.MAlpha)
        self.purchaseButton.setColorScale(0.62, 0.62, 0.62, 0.75)

        self.actionLabel = DirectLabel(
            parent=self,
            relief=None,
            text='',
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.026,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0.10, 0.25, 0.22, 1),
            pos=(0.620, 0, -0.555),
        )

        self.status = DirectLabel(
            parent=self,
            relief=None,
            text='',
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.023,
            text_wordwrap=31,
            text_fg=(1, 0.88, 0.28, 1),
            text_shadow=(0.10, 0.25, 0.22, 1),
            pos=(0.455, 0, -0.595),
        )

    def _bankSearchText(self, node):
        parts = [self._normaliseName(node.getName())]

        # Some versions of the Club Shop BAM put the useful name on a child
        # beneath an otherwise generic parent.  Include a shallow descendant
        # scan so the complete painted panel is selected instead of one plank.
        try:
            children = node.findAllMatches('**/*')
            childLimit = min(children.getNumPaths(), 48)
            for index in xrange(childLimit):
                parts.append(self._normaliseName(children.getPath(index).getName()))
        except:
            pass

        # Texture names are also useful with older/repacked BAMs whose node
        # names were flattened during conversion.
        try:
            textures = node.findAllTextures()
            for index in xrange(textures.getNumTextures()):
                texture = textures.getTexture(index)
                parts.append(self._normaliseName(texture.getName()))
                try:
                    parts.append(self._normaliseName(texture.getFullpath()))
                except:
                    pass
        except:
            pass

        return ' '.join(parts)

    def _bankCandidateScore(self, node):
        bounds = self._nodeBounds(node)
        if bounds is None:
            return None
        width, height, centerX, centerZ = bounds
        aspect = width / float(height)

        # The reference panel is a tall, narrow wooden frame.  This removes
        # tabs, item papers, icons and the full ClubShop_Base before names are
        # considered.
        if aspect < 0.34 or aspect > 0.82:
            return None

        nodeName = self._normaliseName(node.getName())
        searchText = self._bankSearchText(node)
        blocked = (
            'portrait', 'picture', 'itempaper', 'itemcard', 'shopitem',
            'tab', 'button', 'arrow', 'cancel', 'close', 'iconimage',
            'iconbackground', 'booster', 'customization', 'customisation',
            'clubshopbase', 'titleboard', 'selecteditem', 'choc', 'coin',
            'jar',
        )
        for token in blocked:
            if token in nodeName:
                return None

        positive = (
            ('clubshopbank', 460.0),
            ('clubbankpanel', 450.0),
            ('clubbank', 420.0),
            ('bankpanel', 390.0),
            ('clubstatspanel', 360.0),
            ('clubstats', 340.0),
            ('clubcurrencypanel', 330.0),
            ('clubcurrency', 310.0),
            ('clublevelpanel', 300.0),
            ('sidepanel', 250.0),
            ('bankbase', 235.0),
            ('bank', 180.0),
            ('stats', 150.0),
            ('currency', 135.0),
        )
        score = 0.0
        matched = False
        for token, amount in positive:
            if token in searchText:
                score += amount
                matched = True

        if not matched:
            return None

        # Prefer one complete container over a single border strip.
        try:
            score += 85.0 if node.getNumChildren() else 0.0
        except:
            pass
        score += max(-80.0, 85.0 - abs(aspect - 0.60) * 160.0)
        area = max(0.000001, width * height)
        score += min(110.0, math.log(area + 1.0) * 24.0)
        return score

    def _findBankNode(self):
        # The supplied Corporate Clash club_shop.bam names the complete painted
        # right-hand currency panel CurrencyExtension.  Check that exact node
        # before the compatibility names used by older asset revisions.
        node = self._findExact(self.gui, ('CurrencyExtension',))
        if node is not None:
            return node

        # Node spelling changed between Club Shop asset revisions, so check the
        # known complete-panel names next and then use the guarded hierarchy /
        # texture search above.  All results still come from the real
        # phase_3.5/models/gui/clubs/club_shop BAM.
        node = self._findExact(self.gui, (
            'ClubShopBank_Base', 'ClubShop_Bank_Base',
            'ClubShopBank', 'ClubShop_Bank',
            'ClubBankPanel_Base', 'ClubBank_Panel_Base',
            'ClubBankPanel', 'ClubBank_Panel',
            'ClubBank_Base', 'Club_Bank_Base',
            'ClubBank', 'Club_Bank',
            'BankPanel_Base', 'Bank_Panel_Base',
            'BankPanel', 'Bank_Panel',
            'ClubStatsPanel_Base', 'ClubStats_Panel_Base',
            'ClubStatsPanel', 'ClubStats_Panel',
            'ClubStats_Base', 'Club_Stats_Base',
            'ClubStats', 'Club_Stats',
            'ClubCurrencyPanel_Base', 'ClubCurrency_Panel_Base',
            'ClubCurrencyPanel', 'ClubCurrency_Panel',
            'ClubLevelPanel_Base', 'ClubLevel_Panel_Base',
            'ClubLevelPanel', 'ClubLevel_Panel',
            'ShopBank_Base', 'Shop_Bank_Base',
            'ShopBank', 'Shop_Bank',
        ))
        if node is not None:
            return node

        bestNode = None
        bestScore = None
        for candidate in self._allNodes(self.gui):
            score = self._bankCandidateScore(candidate)
            if score is not None and (bestScore is None or score > bestScore):
                bestNode = candidate
                bestScore = score
        return bestNode

    def _makeFallbackClubBank(self):
        # Kept only for an incomplete asset pack.  Normal installations use the
        # real painted panel found above.
        self.bankVisual = DirectFrame(
            parent=self.bankVisualRoot,
            relief=DGG.RIDGE,
            frameSize=(-0.205, 0.205, -0.35, 0.35),
            frameColor=(0.36, 0.18, 0.095, 1),
            borderWidth=(0.016, 0.016),
            sortOrder=-3,
        )
        DirectFrame(
            parent=self.bankVisualRoot,
            relief=DGG.SUNKEN,
            frameSize=(-0.164, 0.164, -0.31, 0.31),
            frameColor=(0.26, 0.57, 0.49, 1),
            borderWidth=(0.010, 0.010),
            sortOrder=-2,
        )

    def _makeClubBank(self):
        bankNode = self._findBankNode()
        self._logAsset('club-bank', bankNode)

        # Keep the latest reference dimensions, but use the exact Clash
        # DirectFrame sort relationship: CurrencyExtension is 689 and the
        # main ClubShop_Base is 690.
        bankPos = (0.965, 0, -0.175)
        self.bankVisualRoot = DirectFrame(
            parent=self,
            relief=None,
            frameSize=(-0.245, 0.245, -0.43, 0.43),
            pos=bankPos,
        )
        self.bankVisualRoot.setBin('sorted-gui-popup', 689)

        if bankNode is not None:
            bankScale, bankImagePos = self._fitTransform(
                bankNode,
                0.475,
                0.82,
                preserveAspect=False,
            )
            self.bankVisual = DirectFrame(
                parent=self.bankVisualRoot,
                relief=None,
                image=bankNode,
                image_scale=bankScale,
                image_pos=bankImagePos,
            )
            self.bankVisual.setTransparency(TransparencyAttrib.MAlpha)
            self.bankVisual.setBin('sorted-gui-popup', 689)
        else:
            self._makeFallbackClubBank()

        # The main frame is explicitly one sort above the extension.
        self.board.setBin('sorted-gui-popup', 690)

        self.bankRoot = DirectFrame(
            parent=self,
            relief=None,
            frameSize=(-0.245, 0.245, -0.43, 0.43),
            pos=bankPos,
        )
        self.bankRoot.setBin('sorted-gui-popup', 691)

        self.clubLevelLabel = DirectLabel(
            parent=self.bankRoot,
            relief=None,
            text='Club Level 1',
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.030,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0.14, 0.24, 0.20, 1),
            # Keep the label centred on the jellybean jar axis and move it
            # upward by roughly 2 cm from the Build 20 position.
            pos=(0.040, 0, 0.205),
        )

        # Keep the Build 14 icon sizes, which matched the reference closely,
        # and move both widgets slightly farther right inside the extension.
        # Reusing the raw Clash widget scales here made them too small because
        # this Altis port does not parent them under the source GUI's 0.4 scale.
        jarNode = self._findExact(self.jarGui, ('Jar', 'jar'))
        self._logAsset('jellybean-jar', jarNode)
        jarScale = (0.14, 1, 0.14)
        jarImagePos = (0, 0, 0)
        if jarNode is not None:
            jarScale, jarImagePos = self._fitTransform(
                jarNode, 0.225, 0.255, preserveAspect=True)

        self.jellybeanJar = DirectLabel(
            parent=self.bankRoot,
            relief=None,
            image=jarNode,
            image_scale=jarScale,
            image_pos=jarImagePos,
            text='0',
            text_font=ToontownGlobals.getSignFont(),
            text_scale=0.052,
            text_pos=(0, -0.015),
            text_fg=(0.96, 0.95, 0.02, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(0.040, 0, 0.035),
        )
        self.jellybeanJar.setTransparency(TransparencyAttrib.MAlpha)

        coinNode = self._findExact(self.gui, ('choc',))
        if coinNode is None:
            coinNode = self._findCoinNode()
        self._logAsset('club-coin', coinNode)
        coinScale = (0.085, 1, 0.085)
        coinImagePos = (0, 0, 0)
        if coinNode is not None:
            coinScale, coinImagePos = self._fitTransform(
                coinNode, 0.155, 0.155, preserveAspect=True)

        self.clubCoinIcon = DirectLabel(
            parent=self.bankRoot,
            relief=None,
            image=coinNode,
            image_scale=coinScale,
            image_pos=coinImagePos,
            # Use the exact same horizontal centre axis as the jellybean jar.
            pos=(0.040, 0, -0.225),
        )
        self.clubCoinIcon.setTransparency(TransparencyAttrib.MAlpha)

        self.clubCoinsLabel = DirectLabel(
            parent=self.bankRoot,
            relief=None,
            text='0',
            text_font=ToontownGlobals.getSignFont(),
            text_scale=0.050,
            text_align=TextNode.ACenter,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            # Keep the amount centred on the same jar/coin axis.
            pos=(0.040, 0, -0.274),
        )
        self.bankRoot.setBin('sorted-gui-popup', 691)

    def _makeCloseButton(self):
        closeStates = None
        exactNames = (
            ('Cancel_Neutral', 'Cancel_Press', 'Cancel_Hover', 'Cancel_Neutral'),
            ('Close_Neutral', 'Close_Press', 'Close_Hover', 'Close_Neutral'),
        )
        for names in exactNames:
            nodes = []
            for name in names:
                node = self._findExact(self.creationGui, (name,))
                if node is None:
                    nodes = []
                    break
                nodes.append(node)
            if nodes:
                closeStates = tuple(nodes)
                break
        if closeStates is None:
            closeStates = self._findStateSet(
                self.creationGui,
                (('cancel',), ('close',)),
                preferredAspect=1.0,
            )
        if closeStates is None:
            closeStates = self._findStateSet(
                self.gui,
                (('cancel',), ('close',)),
                excluded=('title', 'bank'),
                preferredAspect=1.0,
            )
        self._logAsset('close-button', closeStates[0] if closeStates else None)

        kwargs = {
            'parent': self,
            'relief': None,
            'frameSize': (-0.14, 0.14, -0.14, 0.14),
            'pos': (0.820, 0, 0.575),
            'command': self.destroy,
            'pressEffect': 0,
        }
        if closeStates is not None:
            imageScale, imagePos = self._fitTransform(closeStates[0], 0.20, 0.20, preserveAspect=True)
            kwargs['image'] = closeStates
            kwargs['image_scale'] = imageScale
            kwargs['image_pos'] = imagePos
        else:
            kwargs.update({
                'text': 'X',
                'text_font': ToontownGlobals.getToonFont(),
                'text_scale': 0.11,
                'text_fg': (1, 1, 1, 1),
                'text_shadow': (0.25, 0, 0, 1),
                'frameColor': (0.85, 0.16, 0.13, 1),
                'borderWidth': (0.010, 0.010),
            })
        self.closeButton = DirectButton(**kwargs)
        self.closeButton.setTransparency(TransparencyAttrib.MAlpha)

    # ------------------------------------------------------------------
    # Categories and paging
    # ------------------------------------------------------------------
    def _subcategoryDefinitions(self):
        if self.category == self.CATEGORY_BOOSTERS:
            return self.BOOSTER_SUBCATEGORIES
        if self.category == self.CATEGORY_CUSTOMIZATION:
            return self.CUSTOMIZATION_SUBCATEGORIES
        return ()

    def _currentSubcategory(self):
        definitions = self._subcategoryDefinitions()
        if not definitions:
            return ('', ())
        index = self.subcategoryIndexes.get(self.category, 0) % len(definitions)
        return definitions[index]

    def setCategory(self, category):
        if category not in (self.CATEGORY_ITEMS, self.CATEGORY_BOOSTERS, self.CATEGORY_CUSTOMIZATION):
            return
        self.category = category
        self.page = 0
        self.selectedEntry = None
        self.status['text'] = ''
        self._updateTabIndicator()
        self._refreshCategoryHeader()
        self.refreshItems()
        self._showNoSelection()

    def _updateTabIndicator(self):
        button = self.tabButtons.get(self.category)
        if button is None:
            return
        self.tabIndicator.setPos(button.getX(), -0.02, button.getZ())
        if self.category == self.CATEGORY_CUSTOMIZATION:
            self.tabIndicator.setScale(1.08, 1, 1.0)
        elif self.category == self.CATEGORY_BOOSTERS:
            self.tabIndicator.setScale(1.02, 1, 1.0)
        else:
            self.tabIndicator.setScale(1.0)
        self.tabIndicator.show()

    def _refreshCategoryHeader(self):
        definitions = self._subcategoryDefinitions()
        if not definitions:
            self.categoryTitle.hide()
            self.categoryPreviousButton.hide()
            self.categoryNextButton.hide()
            return

        self.categoryTitle.show()
        self.categoryPreviousButton.show()
        self.categoryNextButton.show()
        title, categories = self._currentSubcategory()
        self.categoryTitle['text'] = title

        enabled = len(definitions) > 1
        self.categoryPreviousButton['state'] = DGG.NORMAL if enabled else DGG.DISABLED
        self.categoryNextButton['state'] = DGG.NORMAL if enabled else DGG.DISABLED
        alpha = 1.0 if enabled else 0.45
        self.categoryPreviousButton.setColorScale(1, 1, 1, alpha)
        self.categoryNextButton.setColorScale(1, 1, 1, alpha)

    def changeSubcategory(self, amount):
        definitions = self._subcategoryDefinitions()
        if len(definitions) <= 1:
            return
        index = self.subcategoryIndexes.get(self.category, 0)
        index = (index + int(amount)) % len(definitions)
        self.subcategoryIndexes[self.category] = index
        self.page = 0
        self.selectedEntry = None
        self.status['text'] = ''
        self._refreshCategoryHeader()
        self.refreshItems()
        self._showNoSelection()

    def _entriesForCategory(self):
        if self.category == self.CATEGORY_ITEMS:
            return [dict(entry) for entry in self.UPGRADE_ENTRIES]

        entries = []
        title, allowedCategories = self._currentSubcategory()
        for itemId, item in sorted(ClubGlobals.SHOP_ITEMS.items()):
            name, category, cost, level, payload, currency, description = (
                ClubGlobals.unpackShopItem(item)
            )
            isBooster = str(category).startswith('booster-')
            if self.category == self.CATEGORY_BOOSTERS and not isBooster:
                continue
            if self.category == self.CATEGORY_CUSTOMIZATION and isBooster:
                continue
            if allowedCategories and category not in allowedCategories:
                continue
            entries.append({
                'kind': 'item',
                'id': int(itemId),
                'name': name,
                'category': category,
                'cost': int(cost),
                'level': int(level),
                'payload': payload,
                'currency': currency,
                'description': description,
            })
        return entries

    def _itemsPerPage(self):
        if self.category == self.CATEGORY_ITEMS:
            return 3
        if self.category == self.CATEGORY_BOOSTERS:
            return 4
        return 8

    def _itemPositions(self):
        if self.category == self.CATEGORY_ITEMS:
            return (
                (-0.675, 0, 0.105),
                (-0.335, 0, 0.105),
                (0.005, 0, 0.105),
            )
        if self.category == self.CATEGORY_BOOSTERS:
            return (
                (-0.675, 0, 0.025),
                (-0.435, 0, 0.025),
                (-0.195, 0, 0.025),
                (0.045, 0, 0.025),
            )
        return (
            (-0.655, 0, -0.005),
            (-0.430, 0, -0.005),
            (-0.205, 0, -0.005),
            (0.020, 0, -0.005),
            (-0.655, 0, -0.245),
            (-0.430, 0, -0.245),
            (-0.205, 0, -0.245),
            (0.020, 0, -0.245),
        )

    def _clearItems(self):
        for button in self.itemButtons:
            try:
                button.destroy()
            except:
                pass
        self.itemButtons = []

    def refreshItems(self):
        self._clearItems()
        entries = self._entriesForCategory()
        perPage = self._itemsPerPage()
        pageCount = max(1, (len(entries) + perPage - 1) // perPage)
        self.page = max(0, min(pageCount - 1, self.page))
        begin = self.page * perPage
        visibleEntries = entries[begin:begin + perPage]
        positions = self._itemPositions()

        for index, entry in enumerate(visibleEntries):
            if index >= len(positions):
                break
            button = ClubShopItem(
                parent=self,
                owner=self,
                entry=entry,
                pos=positions[index],
                compact=(self.category == self.CATEGORY_CUSTOMIZATION),
            )
            self.itemButtons.append(button)

        self.pageLabel['text'] = '%s / %s' % (self.page + 1, pageCount)
        previousEnabled = self.page > 0
        nextEnabled = self.page < pageCount - 1
        self.previousButton['state'] = DGG.NORMAL if previousEnabled else DGG.DISABLED
        self.nextButton['state'] = DGG.NORMAL if nextEnabled else DGG.DISABLED
        self.previousButton.setColorScale(1, 1, 1, 1.0 if previousEnabled else 0.42)
        self.nextButton.setColorScale(1, 1, 1, 1.0 if nextEnabled else 0.42)

    def changePage(self, amount):
        entries = self._entriesForCategory()
        perPage = self._itemsPerPage()
        pageCount = max(1, (len(entries) + perPage - 1) // perPage)
        newPage = max(0, min(pageCount - 1, self.page + int(amount)))
        if newPage == self.page:
            return
        self.page = newPage
        self.selectedEntry = None
        self.status['text'] = ''
        self.refreshItems()
        self._showNoSelection()

    # ------------------------------------------------------------------
    # Item visuals
    # ------------------------------------------------------------------
    def _findUpgradeVisual(self, category):
        """Return the exact Corporate Clash upgrade artwork node."""
        nodeName = {
            'upgrade-members': 'item_member_cap',
            'upgrade-booster-slot': 'item_booster_slots',
            'upgrade-name-rewrite': 'item_name_rewrite',
        }.get(category)
        if not nodeName:
            return None
        node = ClubIconGUI.backgrounds.find('**/%s' % nodeName)
        if node.isEmpty():
            return None
        return node

    def _boosterPrefixForEntry(self, entry):
        """Map the ported shop item ID to the node used by boosters.bam."""
        itemId = int(entry.get('id', 0) or 0)
        if 2100 <= itemId < 2200:
            itemId -= 100
        return {
            2000: 'gag_support',
            2001: 'gag_power',
            2002: 'gag_all',
            2003: 'racing',
            2004: 'trolley',
            2005: 'golf',
            2006: 'fishing',
            2007: 'jellybean',
            2008: 'jellybean2',
            2009: 'merit_sell',
            2010: 'merit_cash',
            2011: 'merit_law',
            2012: 'merit_boss',
            2014: 'merit',
            2015: 'sellboss',
            2016: 'cashboss',
            2017: 'lawboss',
            2018: 'bossboss',
            2020: 'eyes',
            2021: 'sellbot',
            2022: 'cashbot',
            2023: 'lawbot',
            2024: 'bossbot',
            2026: 'cog',
            2027: 'mainwashere',
        }.get(itemId)

    def _findBoosterVisual(self, entry):
        prefix = self._boosterPrefixForEntry(entry)
        if prefix and self.boosterGui is not None and not self.boosterGui.isEmpty():
            node = self.boosterGui.find('**/%s' % prefix)
            if not node.isEmpty():
                return node

        # Fallback for installations using an older booster model.
        category = entry.get('category', '')
        booster = category.split('-', 1)[1] if '-' in category else category
        exactByType = {
            'gag': ('gag_all', 'gag_support', 'gag_power'),
            'activity': ('racing', 'trolley', 'golf', 'fishing'),
            'merit': ('merit', 'merit_sell', 'merit_cash', 'merit_law', 'merit_boss'),
            'department': ('cog', 'sellbot', 'cashbot', 'lawbot', 'bossbot'),
            'reward': ('eyes', 'sellboss', 'cashboss', 'lawboss', 'bossboss'),
            'universal': ('mainwashere', 'gag_all', 'jellybean'),
        }
        for name in exactByType.get(booster, ()):
            node = self.boosterGui.find('**/%s' % name)
            if not node.isEmpty():
                return node
        return None

    def _registerColorPulseVisual(self, visual, colorId):
        if visual is None or not ClubIconGUI.isAnimatedColor(colorId):
            return
        self._colorPulseVisuals.append((visual, int(colorId)))

    def _updateColorPulseVisuals(self, task):
        if self._destroyed:
            return task.done

        activeVisuals = []
        for visual, colorId in self._colorPulseVisuals:
            try:
                if visual is None or visual.isEmpty():
                    continue
                visual['geom_color'] = ClubIconGUI.getColor(colorId)
                activeVisuals.append((visual, colorId))
            except:
                pass
        self._colorPulseVisuals = activeVisuals
        task.delayTime = 0.05
        return task.again

    def _makeItemVisual(self, parent, entry, size=0.16, preview=False):
        """Create an item visual using the original Clash card origin/transforms."""
        category = entry.get('category', '')
        payload = entry.get('payload')
        visual = None

        if category == 'icon':
            node = self._findExact(ClubIconGUI.icons, (
                'icon_%s' % int(payload),
                'Icon_%s' % int(payload),
            ))
            if preview:
                club = getattr(base.cr.clubMgr, 'club', None) or {}
                current = club.get('icon', {}) or {}
                icon = ClubIcon(
                    int(payload),
                    int(current.get('backgroundId', 1) or 1),
                    int(current.get('themeId', 0) or 0),
                    int(current.get('backgroundColorId', 1) or 1),
                )
                visual = ClubIconGUI(parent=parent, clubIcon=icon, scale=size * 1.25)
            elif node is not None:
                visual = DirectFrame(
                    parent=parent,
                    relief=None,
                    geom=node,
                    geom_scale=0.09,
                    geom_pos=(0, 0, 0.0095),
                    geom_color=(1, 1, 1, 1),
                )

        elif category == 'background':
            detail = self._findExact(ClubIconGUI.backgrounds, (
                'bg_%s' % int(payload),
                'background_%s' % int(payload),
            ))
            if preview:
                baseNode = self._findExact(
                    ClubIconGUI.backgrounds, ('base', 'Base', 'background_base'))
                visual = DirectFrame(
                    parent=parent,
                    relief=None,
                    image=baseNode,
                    image_scale=size * 0.72,
                    image_color=(0.48, 0.82, 0.94, 1),
                    geom=detail,
                    geom_scale=size * 0.72,
                    geom_color=(1, 1, 1, 1),
                )
            elif detail is not None:
                visual = DirectFrame(
                    parent=parent,
                    relief=None,
                    geom=detail,
                    geom_scale=0.09,
                    geom_pos=(0, 0, 0.0098),
                    geom_color=(0.2, 0.2, 0.2, 1),
                )

        elif category in ('theme', 'detail-color'):
            color = ClubIconGUI.getColor(int(payload))
            paintBase = self._findExact(self.creationGui, ('PaintCan_Base',))
            paintColor = self._findExact(self.creationGui, ('PaintCan_Color',))
            if paintBase is None:
                paintBase = self._findBest(
                    self.creationGui,
                    (('paint', 'can', 'base'), ('paintcan',), ('paint', 'base')),
                    excluded=('color',), preferredAspect=1.0, preferContainer=True)
            if paintColor is None:
                paintColor = self._findBest(
                    self.creationGui,
                    (('paint', 'can', 'color'), ('paint', 'color')),
                    preferredAspect=1.0, preferGeom=True)
            if paintBase is not None:
                canScale = size * 0.72 if preview else 0.1
                canPos = (0, 0, 0) if preview else (0, 0, 0.0095)
                visual = DirectFrame(
                    parent=parent,
                    relief=None,
                    image=paintBase,
                    image_scale=canScale,
                    image_pos=canPos,
                    image_color=(1, 1, 1, 1),
                    geom=paintColor,
                    geom_scale=canScale,
                    geom_pos=canPos,
                    geom_color=color,
                )

        elif category.startswith('booster-'):
            node = self._findBoosterVisual(entry)
            if node is not None:
                boosterScale = size if preview else 0.09
                boosterPos = (0, 0, 0) if preview else (0, 0, 0.0095)
                visual = DirectFrame(
                    parent=parent,
                    relief=None,
                    image=node,
                    image_scale=boosterScale,
                    image_pos=boosterPos,
                )
            else:
                booster = category.split('-', 1)[1]
                badgeText = {
                    'gag': 'XP', 'activity': 'ACT', 'merit': 'MER',
                    'department': 'DEPT', 'reward': 'RWD', 'universal': 'ALL',
                }.get(booster, booster[:3].upper())
                visual = DirectLabel(
                    parent=parent,
                    relief=None,
                    text=badgeText,
                    text_font=ToontownGlobals.getSignFont(),
                    text_scale=0.050 if not preview else size * 0.27,
                    text_fg=(1, 1, 1, 1),
                    text_shadow=(0.42, 0.08, 0.12, 1),
                    pos=(0, 0, 0.0095 if not preview else 0),
                )

        elif category.startswith('upgrade-'):
            node = self._findUpgradeVisual(category)
            if node is not None:
                upgradeScale = size if preview else 0.09
                upgradePos = (0, 0, 0) if preview else (0, 0, 0.0098)
                visual = DirectFrame(
                    parent=parent,
                    relief=None,
                    geom=node,
                    geom_scale=upgradeScale,
                    geom_pos=upgradePos,
                    geom_color=(1, 1, 1, 1),
                )
            else:
                fallback = {
                    'upgrade-members': '+5',
                    'upgrade-booster-slot': '+1',
                    'upgrade-name-rewrite': 'Name\nRewrite',
                }.get(category, '+')
                visual = DirectLabel(
                    parent=parent,
                    relief=None,
                    text=fallback,
                    text_font=ToontownGlobals.getSignFont(),
                    text_scale=0.050 if '\n' not in fallback else 0.036,
                    text_fg=(0.24, 0.15, 0.10, 1),
                    text_shadow=(1, 1, 1, 1),
                    pos=(0, 0, 0.0098 if not preview else 0),
                )

        if visual is not None:
            visual.setTransparency(TransparencyAttrib.MAlpha)
            if category in ('theme', 'detail-color'):
                self._registerColorPulseVisual(visual, int(payload))
        return visual

    def _entryUsesJellybeans(self, entry):
        return entry.get('currency') == ClubGlobals.CURRENCY_JELLYBEANS

    def _getAvailableJellybeans(self):
        try:
            return int(base.cr.clubMgr.getClubJellybeans())
        except:
            return 0

    def _setPriceCurrency(self, entry):
        if self._entryUsesJellybeans(entry):
            node = self.jarGui.find('**/Jar')
            targetWidth = 0.155
            targetHeight = 0.155
        else:
            node = self._findCoinNode()
            targetWidth = 0.150
            targetHeight = 0.150

        if node is None or node.isEmpty():
            return
        scale, imagePos = self._fitTransform(
            node, targetWidth, targetHeight, preserveAspect=True)
        self.priceIcon['image'] = node
        self.priceIcon['image_scale'] = scale
        self.priceIcon['image_pos'] = imagePos
        self.priceIcon.setTransparency(TransparencyAttrib.MAlpha)

    def selectEntry(self, entry):
        self.selectedEntry = entry
        self.status['text'] = ''
        for button in self.itemButtons:
            button.setSelected(
                button.entry.get('kind') == entry.get('kind') and
                button.entry.get('id') == entry.get('id')
            )

        self._clearPreview()
        self.selectionTitle['text'] = entry.get('name', 'Selected Item')
        self.description['text'] = self._descriptionForEntry(entry)
        visual = self._makeItemVisual(self.previewFrame, entry, size=0.26, preview=True)
        if visual is not None:
            visual.setPos(0, 0, 0)
            self.previewNodes.append(visual)

        self._setPriceCurrency(entry)
        self.priceLabel['text'] = 'x%s' % self._compactNumber(entry.get('cost', 0))
        self._updateActionButton()

    def _clearPreview(self):
        for node in self.previewNodes:
            try:
                node.destroy()
            except:
                try:
                    node.removeNode()
                except:
                    pass
        self.previewNodes = []

    def _showNoSelection(self):
        self.selectedEntry = None
        self.selectionTitle['text'] = 'No Item Selected'
        self.description['text'] = 'Select an item for more info.'
        self._setPriceCurrency({
            'currency': ClubGlobals.CURRENCY_CLUB_COINS,
        })
        self.priceLabel['text'] = 'x0'
        self.actionLabel['text'] = ''
        self.status['text'] = ''
        self.purchaseButton['state'] = DGG.DISABLED
        self.purchaseButton.setColorScale(0.62, 0.62, 0.62, 0.75)
        self._clearPreview()
        for button in self.itemButtons:
            button.setSelected(False)

    def _descriptionForEntry(self, entry):
        if entry.get('description'):
            return entry['description']
        category = entry.get('category', '')
        if category.startswith('booster-'):
            duration = int(entry.get('payload', 0))
            hours = max(1, duration // 3600)
            return '%s\nActivates for %s hour%s.' % (
                entry['name'], hours, '' if hours == 1 else 's')
        if category == 'icon':
            return 'Unlock and equip this image on your Club icon.'
        if category == 'background':
            return 'Unlock and equip this detail on your Club icon.'
        if category == 'theme':
            return 'Unlock and equip this theme color for your Club icon.'
        if category == 'detail-color':
            return 'Unlock and equip this detail color for your Club icon.'
        return entry.get('name', '')

    def _isOwned(self, entry):
        if entry.get('kind') != 'item' or entry.get('category', '').startswith('booster-'):
            return False
        club = getattr(base.cr.clubMgr, 'club', None) or {}
        return int(entry.get('id', -1)) in club.get('itemsOwned', [])

    def _isEquipped(self, entry):
        if not self._isOwned(entry):
            return False
        club = getattr(base.cr.clubMgr, 'club', None) or {}
        icon = club.get('icon', {}) or {}
        category = entry.get('category')
        payload = int(entry.get('payload', 0))
        if category == 'icon':
            return int(icon.get('iconId', 0)) == payload
        if category == 'background':
            return int(icon.get('backgroundId', 0)) == payload
        if category == 'theme':
            return int(icon.get('themeId', 0)) == payload
        if category == 'detail-color':
            return int(icon.get('backgroundColorId', 0)) == payload
        return False

    def _updateActionButton(self):
        entry = self.selectedEntry
        if not entry:
            self.purchaseButton['state'] = DGG.DISABLED
            self.purchaseButton.setColorScale(0.62, 0.62, 0.62, 0.75)
            self.actionLabel['text'] = ''
            self.status['text'] = ''
            return

        manager = base.cr.clubMgr
        clubLevel = manager.getClubLevel()
        clubCoins = manager.getClubCoins()
        cost = int(entry.get('cost', 0))
        requiredLevel = int(entry.get('level', 1))
        category = entry.get('category', '')

        enabled = True
        label = 'Purchase'
        message = ''

        if entry.get('kind') == 'upgrade':
            enabled = False
            label = ''
            message = ''
        elif category.startswith('booster-'):
            label = 'Activate'
            if not manager.localAvHasPermission(ClubGlobals.PERMISSION_PURCHASE_ITEMS):
                enabled = False
                message = 'You do not have permission to purchase Club items.'
        elif self._isEquipped(entry):
            label = 'Equipped'
            enabled = False
        elif self._isOwned(entry):
            label = 'Equip'
            if not manager.localAvHasPermission(ClubGlobals.PERMISSION_CUSTOMIZE):
                enabled = False
                message = 'You do not have permission to customize this Club.'
        else:
            label = 'Purchase'
            if not manager.localAvHasPermission(ClubGlobals.PERMISSION_PURCHASE_ITEMS):
                enabled = False
                message = 'You do not have permission to purchase Club items.'

        if enabled and clubLevel < requiredLevel:
            enabled = False
            message = 'Your Club must be Level %s to purchase this item.' % requiredLevel

        if enabled and label not in ('Equip', 'Equipped'):
            available = (
                self._getAvailableJellybeans()
                if self._entryUsesJellybeans(entry)
                else clubCoins
            )
            if available < cost:
                enabled = False
                if self._entryUsesJellybeans(entry):
                    message = 'Your Club does not have enough Jellybeans.'
                else:
                    message = 'Your Club does not have enough Club Coins.'

        self.purchaseButton['state'] = DGG.NORMAL if enabled else DGG.DISABLED
        self.purchaseButton.setColorScale(
            1, 1, 1, 1 if enabled else 0.60
        )
        self.actionLabel['text'] = label
        self.status['text'] = message

    def performSelectedAction(self):
        entry = self.selectedEntry
        if not entry or entry.get('kind') == 'upgrade':
            return

        category = entry.get('category', '')
        if category.startswith('booster-') or not self._isOwned(entry):
            self.status['text'] = 'Purchasing...'
            base.cr.clubMgr.requestPurchaseItem(entry['id'])
            return

        club = base.cr.clubMgr.club or {}
        icon = club.get('icon', {}) or {}
        iconId = int(icon.get('iconId', 0))
        backgroundId = int(icon.get('backgroundId', 0))
        themeId = int(icon.get('themeId', 0))
        backgroundColorId = int(icon.get('backgroundColorId', themeId))
        payload = int(entry.get('payload', 0))

        if category == 'icon':
            iconId = payload
        elif category == 'background':
            backgroundId = payload
        elif category == 'theme':
            themeId = payload
        elif category == 'detail-color':
            backgroundColorId = payload

        self.status['text'] = 'Equipping Club customization...'
        base.cr.clubMgr.requestUpdateIcon(
            iconId, backgroundId, themeId, backgroundColorId)

    def _moneyChanged(self, *args):
        self._refreshHeader()

    def _refreshHeader(self):
        manager = base.cr.clubMgr
        self.clubLevelLabel['text'] = 'Club Level %s' % manager.getClubLevel()
        self.clubCoinsLabel['text'] = self._compactNumber(manager.getClubCoins())

        clubJellybeans = 0
        try:
            clubJellybeans = int(manager.getClubJellybeans())
        except:
            pass
        self.jellybeanJar['text'] = self._compactNumber(clubJellybeans)
        self._updateActionButton()

    def _compactNumber(self, value):
        value = int(value)
        absolute = abs(value)
        if absolute >= 1000000:
            text = '%.1fM' % (value / 1000000.0)
        elif absolute >= 1000:
            text = '%.1fK' % (value / 1000.0)
        else:
            return str(value)
        return text.replace('.0', '')

    def _stateUpdated(self, club):
        if not club:
            self.destroy()
            return

        selectedKind = None
        selectedId = None
        if self.selectedEntry:
            selectedKind = self.selectedEntry.get('kind')
            selectedId = self.selectedEntry.get('id')

        self._refreshHeader()
        self.refreshItems()

        if selectedId is not None:
            for entry in self._entriesForCategory():
                if entry.get('kind') == selectedKind and entry.get('id') == selectedId:
                    self.selectEntry(entry)
                    return
        self._showNoSelection()

    def _notification(self, notifyType, message):
        self.status['text'] = message
        self._refreshHeader()

    def destroy(self):
        if self._destroyed:
            return
        self._destroyed = True
        taskMgr.remove(self._colorPulseTaskName)
        self._colorPulseVisuals = []
        self.ignoreAll()
        self._clearItems()
        self._clearPreview()

        try:
            base.localAvatar.enableControls()
        except:
            pass

        for model in (self.gui, self.creationGui, self.jarGui, self.boosterGui):
            try:
                model.removeNode()
            except:
                pass

        DirectFrame.destroy(self)
        messenger.send(self.doneEvent)
        print('[Clubs] Club Shop GUI Build 24 closed.')


class ClubShopItem(DirectButton):
    """Paper Club Shop card used by all three shop tabs."""

    def __init__(self, parent, owner, entry, pos, compact=False):
        self.owner = owner
        self.entry = entry
        self.visual = None
        self.selectedFrame = None
        self.compact = compact

        cardWidth = 0.305 if compact else 0.345
        cardHeight = 0.300 if compact else 0.345
        paperNode = owner._findExact(owner.gui, (
            'Item_Paper', 'ItemPaper', 'Shop_Item', 'ShopItem',
            'Item_Base', 'Paper_Base', 'Item_Card', 'ItemCard',
        ))
        if paperNode is None:
            paperNode = owner._findBest(
                owner.gui,
                (
                    ('item', 'paper'),
                    ('shop', 'item'),
                    ('item', 'card'),
                    ('paper', 'base'),
                    ('paper',),
                ),
                excluded=('tab', 'title', 'bank', 'icon', 'selected'),
                preferredAspect=0.82,
                preferContainer=True,
            )
        owner._logAsset('item-paper', paperNode)

        kwargs = {
            'parent': parent,
            'relief': None if paperNode is not None else DGG.RIDGE,
            'frameSize': (-cardWidth * 0.5, cardWidth * 0.5, -cardHeight * 0.5, cardHeight * 0.5),
            'frameColor': (0.92, 0.92, 0.88, 1),
            'borderWidth': (0.007, 0.007),
            'pos': pos,
            'command': owner.selectEntry,
            'extraArgs': [entry],
            'pressEffect': 0,
        }
        if paperNode is not None:
            imageScale, imagePos = owner._fitTransform(
                paperNode,
                cardWidth,
                cardHeight,
                preserveAspect=False,
            )
            kwargs['image'] = paperNode
            kwargs['image_scale'] = imageScale
            kwargs['image_pos'] = imagePos

        DirectButton.__init__(self, **kwargs)
        self.initialiseoptions(ClubShopItem)
        self.setTransparency(TransparencyAttrib.MAlpha)

        if paperNode is None:
            DirectFrame(
                parent=self,
                relief=None,
                frameSize=(-cardWidth * 0.48, cardWidth * 0.48, -cardHeight * 0.48, cardHeight * 0.48),
                frameColor=(0.10, 0.10, 0.10, 0.20),
                pos=(0.009, 0.01, -0.010),
                sortOrder=-1,
            )
            DirectFrame(
                parent=self,
                relief=DGG.GROOVE,
                frameSize=(-cardWidth * 0.42, cardWidth * 0.42, cardHeight * 0.27, cardHeight * 0.34),
                frameColor=(0.85, 0.85, 0.82, 1),
                borderWidth=(0.003, 0.003),
            )

        # Corporate Clash reuses the real CategorySelectIndicator scribble
        # for selected shop cards.  It is the same BAM node used by the tab
        # selector, only with the original smaller item-card transform.
        itemSelectorNode = owner._findExact(owner.gui, ('CategorySelectIndicator',))
        if itemSelectorNode is not None:
            self.selectedFrame = DirectLabel(
                parent=self,
                relief=None,
                frameSize=(0, 0, 0, 0),
                geom=itemSelectorNode,
                geom_scale=(0.21, 1, 0.35),
                geom_pos=(0, 0, 0.01),
                geom_color=(1, 1, 1, 0.85),
            )
            self.selectedFrame.setTransparency(TransparencyAttrib.MAlpha)
        else:
            # Keep a harmless fallback for incomplete/repacked resources.
            self.selectedFrame = DirectFrame(
                parent=self,
                relief=DGG.RIDGE,
                frameSize=(-cardWidth * 0.53, cardWidth * 0.53, -cardHeight * 0.53, cardHeight * 0.53),
                frameColor=(1, 0.18, 0.12, 0.05),
                borderWidth=(0.009, 0.009),
            )
        self.selectedFrame.hide()

        self.visualHolder = DirectFrame(
            parent=self,
            relief=None,
            pos=(0, 0, 0),
        )
        visualSize = 0.160 if compact else 0.185
        self.visual = owner._makeItemVisual(self.visualHolder, entry, size=visualSize)

        costText = 'x%s' % owner._compactNumber(entry.get('cost', 0))
        if owner._isOwned(entry):
            costText = 'OWNED'
        self.cost = DirectLabel(
            parent=self,
            relief=None,
            text=costText,
            text_font=ToontownGlobals.getSignFont(),
            text_scale=0.034 if compact else 0.036,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            pos=(-cardWidth * 0.045, 0, -cardHeight * 0.39),
        )

        self.currencyIcon = None
        if not owner._isOwned(entry):
            if owner._entryUsesJellybeans(entry):
                currencyNode = owner.jarGui.find('**/Jar')
                iconSize = 0.070 if compact else 0.075
            else:
                currencyNode = owner._findCoinNode()
                iconSize = 0.050 if compact else 0.055

            if currencyNode is not None and not currencyNode.isEmpty():
                currencyScale, currencyImagePos = owner._fitTransform(
                    currencyNode,
                    iconSize,
                    iconSize,
                    preserveAspect=True,
                )
                self.currencyIcon = DirectLabel(
                    parent=self,
                    relief=None,
                    image=currencyNode,
                    image_scale=currencyScale,
                    image_pos=currencyImagePos,
                    pos=(cardWidth * 0.30, 0, -cardHeight * 0.365),
                )
                self.currencyIcon.setTransparency(TransparencyAttrib.MAlpha)

        requiredLevel = int(entry.get('level', 1))
        self.level = ClubLevelShield(
            parent=self,
            pos=(-0.067, 0.0, 0.074),
            scale=0.166,
        )
        self.level.setClubLevel(requiredLevel)
        if requiredLevel <= 1:
            self.level.hide()

        tooltip = entry.get('name', '')
        self.bind(DGG.ENTER, self._showTooltip, extraArgs=[tooltip])
        self.bind(DGG.EXIT, self._hideTooltip)

    def _showTooltip(self, text, event=None):
        self.owner.status['text'] = text

    def _hideTooltip(self, event=None):
        if self.owner.selectedEntry is None:
            self.owner.status['text'] = ''
        else:
            self.owner._updateActionButton()

    def setSelected(self, selected):
        if selected:
            self.selectedFrame.show()
        else:
            self.selectedFrame.hide()

    def destroy(self):
        try:
            if self.visual is not None:
                self.visual.destroy()
        except:
            pass
        DirectButton.destroy(self)
