from toontown.shtiker import ShtikerPage
from direct.task.Task import Task
from toontown.shtiker import SummonCogDialog
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.suit import SuitDNA
from toontown.suit import Suit
from toontown.battle import SuitBattleGlobals
from CogPageGlobals import *
SCALE_FACTOR = 1.5
RADAR_DELAY = 0.2
BUILDING_RADAR_POS = (0.4,
 0.1,
 -0.18,
 -0.5,
 -0.51,
                      -.6)
COG_LEVEL_RANGES = [
    ((
        'f', 'bf', 'cc', 'sc', 'bgh', 'skd', 'ppb'
    ), (1, 5)),
    ((
        'pf', 'stg', 'shy', 'cn', 'ca', 'dhr', 'bsd', 
    ), (2, 8)),
    ((
        'p', 'tm', 'b', 'pp', 'pph', 'cmk', 'shb', 
    ), (2, 6)),

    ((
        'ym', 'nd', 'dt', 'tw', 'ins', 'vpr', 'gms', 
    ), (3, 10)),
                ((
        'dc', 'enf', 'sw', 'mdm', 'brn', 'sbg', 'cv', 
    ), (4, 10)),
        ((
        'gh', 'ac', 'mm', 'bc', 'cbr', 'sdb', 'hck', 
    ), (4, 12)),
            ((
        'fcs', 'txm', 'key', 'fct', 'nn', 'blh', 'ath', 
    ), (3, 14)),
            ((
        'ms', 'nc', 'ds', 'dl', 'ghw', 'bs', 'kbc', 
    ), (5, 15)),
                ((
        'ad', 'ksp', 'gld', 'asm', 'ang', 'blk', 'dcw', 
    ), (5, 20)),
                ((
        'tf', 'mb', 'hh', 'shw', 'gzt', 'sfs', 'sd', 
    ), (6, 20)),
                    ((
        'bfh2', 'ppl', 'pyc', 'trs', 'sh', 'bsht', 'wnk', 
    ), (6, 20)),
                    ((
        'm', 'cr', 'le', 'mg', 'ls', 'nsh', 'inw', 
    ), (7, 25)),
                            ((
        'br', 'txm', 'chw', 'bfh', 'cnd', 'itn', 'std', 
    ), (7, 25)),
                        ((
        'mh', 'bw', 'rb', 'tbc', 'hho', 'anc', 'rus', 
    ), (8, 50)),
    (('autocad',), (14, 15)),
     (('clubpres',), (20, 28)),
     (('supervis',), (20, 28)),
     (('foreman',), (20, 28)),
     (('clerk',), (20, 28)),
     (('derrman',), 10),
     (('derrhand', 'dold', ), 25),
     (('fires',), 20),
     (('fbed', 'sgoat', 'dopa', 'director',), 30),
     (('mplayer',), 28),
     (('choreo',), 26),
     (('chainsaw',), 50),
     (('phouse',), 38),
     (('bkeeper',), 44),
     (('wtapper',), 44),
     (('ambass',), 48),
     (('whistleb',), (14, 15)),
     (('judy',), 20),
     (('erclaim', 'whunter', 'erfit'), 20),
     (('redd',), 20),
     (('wsi',), 50),
     (('mouthp', 'rainmake',), 16),
     (('caseman', 'stenog', 'bookkeep', 'radiog',), 35),
     (('lgator', 'racket', 'liquidr', 'hustle', 'ubuster',), 40),
     (('treasure', 'safesupervis',), 45),
     (('payman',), 20),
     (('pcrat',), 38),
     (('hroller', 'hrollers', 'hroller2', 'chairman',), 100),
     (('dopr',), 15),
     (('brllring',), 13),
     (('prethink', 'dola',), 12),
     (('mslacker',), 24),
     (('psetter',), 66),
     (('cinema', 'fmaker',), 26),
     (('cdirector',), 66),
     (('dking',), 60),
     (('rkeeper',), 60),
     (('liquid',), 56),
     (('ottoman',), 72),
     (('djockey',), (3, 10)),
      (('ddiver',), 7),
      (('gatekeep',), 10),
      (('videog',), 99),


    # ...
]
MANAGER_SUITS = [
'whistleb', 'clubpres', 'ovt', 'derrman', 'derrhand', 'mplayer', 'fires', 'fbed', 'mplayer2', 'chainsaw', 'chainsaw2', 'phouse', 'bkeeper', 'wtapper', 'ambass', 'foreman', 'dopr', 'dopa',
                  'bellring', 'prethink', 'mslacker', 'videog', 'radiog', 'ubuster', 'racket', 'safesupervis', 'psetter', 'supervis', 'duckshfl', 'treek', 'styx', 'nix', 'hydra',
                  'kerberos', 'charon', 'pcrat', 'clerk', 'mouthp', 'rainmake', 'whunter', 'wsi',
                  'liquidr', 'treasure', 'hustle', 'bookkeep', 
                  'sgoat', 'caseman', 'stenog', 'lgator', 'bdirector', 'ddiver', 'gatekeep', 'dola', 'dold', 'dking', 'ottoman', 'crystal', 'chairman',
                  'sya', 'pbl', 'liquid', 'cbutcher', 'cdirector', 'rkeeper'
]
DEPT_ORDER = ['c', 'l', 'm', 's', 'g', 't', 'p']
CONTRACTOR_SUITS = [
    'erfit',
    'hroller',
    'hroller2', 'hrollers', 'erclaim', 'redd', 'videog', 'fmaker',
        'fmaker',
    'choreo',
    'cinema', 'director',
]
FACILITY_MANAGER_SUITS = []
SECRETARY_SUITS = [
    'judy',
]
CogIndexDepartments = {
    'c': ['f', 'p', 'stg', 'ym', 'enf', 'mm', 'blh', 'ds', 'ksp', 'hh', 'bsht', 'cr', 'txl', 'tbc', 'autocad', 'clubpres', 'derrman', 'derrhand', 'fires', 'fbed', 'mplayer',
           'chainsaw', 'choreo', 'phouse', 'bkeeper', 'wtapper', 'ambass'],
    's': ['cc', 'tm', 'cn', 'nd', 'dc', 'gh', 'fcs', 'ms', 'asm', 'tf', 'ppl', 'm', 'cnd', 'mh', 'foreman', 'dopr', 'dopa', 'bellring', 'prethink', 'mslacker', 
          'psetter', 'cinema', 'radiog', 'hustle', 'ubuster', 'safesupervis'],
    'l': ['bf', 'b', 'pf', 'dt', 'cv', 'ac', 'nn', 'bs', 'ad', 'sd', 'sh', 'le', 'br', 'bw', 'whistleb', 'clerk', 'judy', 'mouthp', 'rainmake', 'whunter', 'erclaim',
            'redd', 'wsi', 'sgoat', 'caseman', 'stenog', 'lgator'],
    'm': ['sc', 'pp', 'shy', 'tw', 'sw', 'bc', 'fct', 'nc', 'gld', 'mb', 'trs', 'ls', 'bfh', 'rb', 'supervis', 'duckshfl', 'treek', 'pcrat', 'erfit', 'hroller', 
          'bookkeep', 'racket', 'liquidr', 'treasure'],
    'g': ['bgh', 'pph', 'ca', 'ins', 'mdm', 'cbr', 'txm', 'dl', 'ang', 'shw', 'bfh2', 'mg', 'chw', 'hho', 'ddiver', 'gatekeep', 'dola', 'dold', 'fmaker', 'liquid', 'rkeeper', 'dking', 'cdirector', 'ottoman', 'chairman',],  # boardbots
    't': ['skd', 'cmk', 'dhr', 'vpr', 'brn', 'sdb', 'key', 'kbc', 'blk', 'sfs', 'pyc', 'inw', 'itn', 'rus', 'djockey'],  # techbots
    'p': ['ppb', 'shb', 'bsd', 'gms', 'sbg', 'hck', 'ath', 'ghw', 'dcw', 'gzt', 'wnk', 'nsh', 'std', 'anc', 'director', 'videog'],  # pressbots
}
PANEL_COLORS = (VBase4(0.839, 0.808, 0.769, 1.0),
VBase4(0.784, 0.816, 0.863, 1.0),
VBase4(0.78, 0.808, 0.796, 1.0),
VBase4(0.761, 0.714, 0.725, 1.0),
VBase4(0.675, 0.761, 0.769, 1.0),
                VBase4(0.675, 0.608, 0.69, 1.0),
                 VBase4(0.647, 0.518, 0.537, 1.0)
                )
PANEL_COLORS_COMPLETE1 = (VBase4(0.839, 0.808, 0.769, 1.0),
VBase4(0.784, 0.816, 0.863, 1.0),
VBase4(0.78, 0.808, 0.796, 1.0),
VBase4(0.761, 0.714, 0.725, 1.0),
VBase4(0.675, 0.761, 0.769, 1.0),
                VBase4(0.675, 0.608, 0.69, 1.0),
                 VBase4(0.647, 0.518, 0.537, 1.0)
                )
PANEL_COLORS_COMPLETE2 = (VBase4(0.839, 0.808, 0.769, 1.0),
VBase4(0.784, 0.816, 0.863, 1.0),
VBase4(0.78, 0.808, 0.796, 1.0),
VBase4(0.761, 0.714, 0.725, 1.0),
VBase4(0.675, 0.761, 0.769, 1.0),
                VBase4(0.675, 0.608, 0.69, 1.0),
                 VBase4(0.647, 0.518, 0.537, 1.0)
                )

class SuitPage(ShtikerPage.ShtikerPage):

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        frameModel = loader.loadModel('phase_3.5/models/gui/suitpage_frame')
        frameModel.setScale(0.0253125, 0.03, 0.045)
        frameModel.setPos(0, 10, -0.575)
        self.guiTop = NodePath('guiTop')
        self.guiTop.reparentTo(self)
        self.frameNode = NodePath('frameNode')
        self.frameNode.reparentTo(self.guiTop)
        self.panelNode = NodePath('panelNode')
        self.panelNode.reparentTo(self.guiTop)
        self.iconNode = NodePath('iconNode')
        self.iconNode.reparentTo(self.guiTop)
        self.enlargedPanelNode = NodePath('enlargedPanelNode')
        self.enlargedPanelNode.reparentTo(self.guiTop)
        frame = frameModel.find('**/frame')
        frame.wrtReparentTo(self.frameNode)
        screws = frameModel.find('**/screws')
        screws.wrtReparentTo(self.iconNode)
        icons = frameModel.find('**/icons')
        self.cogHeadCache = {}
        del frameModel
        self.title = DirectLabel(parent=self.iconNode, relief=None, text=TTLocalizer.SuitPageTitle, text_scale=0.1, text_pos=(0.04, 0), textMayChange=0)
        # self.radarButtons = []
        # icon = icons.find('**/corp_icon')
        # self.corpRadarButton = DirectButton(parent=self.iconNode, relief=None, state=DGG.DISABLED, image=icon, image_scale=(0.03375, 1, 0.045), image2_color=Vec4(1.0, 1.0, 1.0, 0.75), pos=(-0.2, 10, -0.575), command=self.toggleRadar, extraArgs=[0])
        # self.radarButtons.append(self.corpRadarButton)
        # icon = icons.find('**/legal_icon')
        # self.legalRadarButton = DirectButton(parent=self.iconNode, relief=None, state=DGG.DISABLED, image=icon, image_scale=(0.03375, 1, 0.045), image2_color=Vec4(1.0, 1.0, 1.0, 0.75), pos=(-0.2, 10, -0.525), command=self.toggleRadar, extraArgs=[1])
        # self.radarButtons.append(self.legalRadarButton)
        # icon = icons.find('**/money_icon')
        # self.moneyRadarButton = DirectButton(parent=self.iconNode, relief=None, state=DGG.DISABLED, image=(icon, icon, icon), image_scale=(0.03375, 1, 0.045), image2_color=Vec4(1.0, 1.0, 1.0, 0.75), pos=(-0.2, 10, -0.460), command=self.toggleRadar, extraArgs=[2])
        # self.radarButtons.append(self.moneyRadarButton)
        # icon = icons.find('**/sales_icon')
        # self.salesRadarButton = DirectButton(parent=self.iconNode, relief=None, state=DGG.DISABLED, image=(icon, icon, icon), image_scale=(0.03375, 1, 0.045), image2_color=Vec4(1.0, 1.0, 1.0, 0.75), pos=(-0.2, 10, -0.385), command=self.toggleRadar, extraArgs=[3])
        # self.radarButtons.append(self.salesRadarButton)
        # icon = icons.find('**/board_icon')
        # self.boardRadarButton = DirectButton(parent=self.iconNode, relief=None, state=DGG.DISABLED, image=(icon, icon, icon), image_scale=(0.03375, 1, 0.045), image2_color=Vec4(1.0, 1.0, 1.0, 0.75), pos=(-0.2, 10, -0.615), command=self.toggleRadar, extraArgs=[4])
        # self.radarButtons.append(self.boardRadarButton)
        # icon = icons.find('**/sales_icon')
        # self.techRadarButton = DirectButton(parent=self.iconNode, relief=None, state=DGG.DISABLED,
        #                                      image=(icon, icon, icon), image_scale=(0.03375, 1, 0.045),
        #                                      image2_color=Vec4(1.0, 1.0, 1.0, 0.75), pos=(-0.2, 10, -0.715),
        #                                      command=self.toggleRadar, extraArgs=[4])
        # self.radarButtons.append(self.techRadarButton)
        # icon = icons.find('**/sales_icon')
        # self.pressRadarButton = DirectButton(parent=self.iconNode, relief=None, state=DGG.DISABLED,
        #                                     image=(icon, icon, icon), image_scale=(0.03375, 1, 0.045),
        #                                     image2_color=Vec4(1.0, 1.0, 1.0, 0.75), pos=(-0.2, 10, -0.715),
        #                                     command=self.toggleRadar, extraArgs=[4])
        # self.radarButtons.append(self.pressRadarButton)
        # for radarButton in self.radarButtons:
        #     radarButton.building = 0
        #     radarButton.buildingRadarLabel = None
        self.backButton = DirectButton(
            parent=self.iconNode,
            relief=None,
            text='Back',
            text_scale=0.06,
            text_fg=(0, 0, 0, 1),
            pos=(-.875, 10, -0.68),
            command=self.showDepartmentHome
        )
        self.backButton.hide()

        self.makeDepartmentButtons()
        gui = loader.loadModel('phase_3.5/models/gui/suitpage_gui')
        self.panelModel = gui.find('**/card')
        self.shadowModels = []
        for index in xrange(1, len(SuitDNA.suitHeadTypes) + 1):
            self.shadowModels.append(gui.find('**/shadow' + str(index)))
        del gui
        self.loadCogHeads()
        self.makePanels()
        self.radarOn = [0,
         0,
         0,
         0,
         0,
         0,
         0]
        priceScale = 0.1
        emblemIcon = loader.loadModel('phase_3.5/models/gui/tt_m_gui_gen_emblemIcons')
        silverModel = emblemIcon.find('**/tt_t_gui_gen_emblemSilver')
        goldModel = emblemIcon.find('**/tt_t_gui_gen_emblemGold')
        self.silverLabel = DirectLabel(parent=self, relief=None, pos=(-0.25, 0, -0.69), scale=priceScale, image=silverModel, image_pos=(-0.4, 0, 0.4), text=str(localAvatar.emblems[ToontownGlobals.EmblemTypes.Silver]), text_fg=(0.95, 0.95, 0, 1), text_shadow=(0, 0, 0, 1), text_font=ToontownGlobals.getSignFont(), text_align=TextNode.ALeft)
        self.goldLabel = DirectLabel(parent=self, relief=None, pos=(0.25, 0, -0.69), scale=priceScale, image=goldModel, image_pos=(-0.4, 0, 0.4), text=str(localAvatar.emblems[ToontownGlobals.EmblemTypes.Gold]), text_fg=(0.95, 0.95, 0, 1), text_shadow=(0, 0, 0, 1), text_font=ToontownGlobals.getSignFont(), text_align=TextNode.ALeft)
        if not base.cr.wantEmblems:
            self.silverLabel.hide()
            self.goldLabel.hide()
        self.accept(localAvatar.uniqueName('emblemsChange'), self.__emblemChange)
        self.guiTop.setZ(0.625)
        gui2 = loader.loadModel('phase_3.5/models/gui/suit_detail_panel')
        gui2.find('**/shadow').setTransparency(TransparencyAttrib.MAlpha)
        gui2.find('**/shadow').setColor(1, 1, 1, 0.4)
        self.hoverInfo = DirectFrame(geom=gui2.find('**/avatar_panel'), geom_scale=(.5, .25, .175), geom_color=(0.69, 0.706, 0.718, 1), geom_pos=(-1.275, -0.5, -1), relief=None, pos=(0, 0, 0), parent=base.a2dTopRight)
        self.hoverInfo.setBin('gui-popup', 100)

        self.hoverInfoPanel = DirectFrame(
            parent=self.hoverInfo,
            relief=None,
            frameColor=(0.45, 0.45, 0.45, 1),
            frameSize=(-0.55, 0.55, -0.38, 0.38)
        )
        self.hoverInfoPanel.setBin('gui-popup', 100)    
        self.hoverInfoText = DirectLabel(
            parent=self.hoverInfoPanel,
            relief=None,
            text='',
            text_scale=0.045,
            text_fg=(0, 0, 0, 1),
            text_align=TextNode.ACenter,
            text_wordwrap=22,
            pos=(-1.275, -0.5, -.75),
            text_font=ToontownGlobals.getSuitFont()
        )
        self.hoverInfoText.setBin('gui-popup', 100)
        self.hoverInfo.hide()
        self.showDepartmentHome()
        return
    
    def getCogHead(self, suitName):
        if suitName not in self.cogHeadCache:
            headNode = NodePath('headNode')
            head = self.createSuitHead(suitName, headNode, dimension=0.22)
            self.cogHeadCache[suitName] = headNode

        return self.cogHeadCache[suitName]
    
    def getDepartmentIcon(self, icons, dept):
        if dept == 'c':
            return icons.find('**/CorpIcon')

        elif dept == 's':
            return icons.find('**/SalesIcon')

        elif dept == 'l':
            return icons.find('**/LegalIcon')

        elif dept == 'm':
            return icons.find('**/MoneyIcon')

        elif dept == 'g':
            icon = icons.find('**/LegalIcon').copyTo(hidden)
            icon.setTexture(
                loader.loadTexture(
                    'phase_3/maps/ttcc_suit_insignias_palette4.png'
                ),
                1
            )
            return icon

        elif dept == 't':
            icon = icons.find('**/LegalIcon').copyTo(hidden)
            icon.setTexture(
                loader.loadTexture(
                    'phase_3/maps/ttcc_suit_insignias_palette2.png'
                ),
                1
            )
            return icon

        elif dept == 'p':
            icon = icons.find('**/LegalIcon').copyTo(hidden)
            icon.setTexture(
                loader.loadTexture(
                    'phase_3/maps/ttcc_suit_insignias_palette3.png'
                ),
                1
            )
            return icon
        
    def getCogLevelRange(self, suitName):
        if suitName in CUSTOM_LEVEL_RANGES:
            return CUSTOM_LEVEL_RANGES[suitName]

        attrs = SuitBattleGlobals.SuitAttributes.get(suitName)
        if not attrs:
            return ('?', '?')

        relLevel = attrs.get('level', None)

        if relLevel is None:
            return ('?', '?')

        try:
            if isinstance(relLevel, tuple) or isinstance(relLevel, list):
                low = SuitBattleGlobals.getActualFromRelativeLevel(relLevel[0])
                high = SuitBattleGlobals.getActualFromRelativeLevel(relLevel[-1])
                return (low, high)
            else:
                actual = SuitBattleGlobals.getActualFromRelativeLevel(relLevel)
                return (actual, actual)

        except:
            return (relLevel, relLevel)
        
    def getCogLevelText(self, suitName):
        for suitList, levelInfo in COG_LEVEL_RANGES:
            if suitName in suitList:
                if isinstance(levelInfo, tuple):
                    return 'Level Range: %d-%d' % levelInfo
                else:
                    return 'Level: %d' % levelInfo

        return 'Level: 0'
    
    def showCogDetails(self, panel, extra=None):
        index = self.panels.index(panel)
        suitName = SuitDNA.suitHeadTypes[index]
        attrs = SuitBattleGlobals.SuitAttributes[suitName]

        name = attrs.get('name', suitName)

        levelText = self.getCogLevelText(suitName)

        text = '%s\n%s' % (name, levelText)

        if attacks:
            text += '\nAttacks:\n' + ', '.join([atk[0] for atk in attacks])

        self.showInfo(panel, text, None)
    
    def showDepartmentHome(self):
        self.currentDept = None

        for button in self.departmentButtons:
            button.show()

        self.backButton.hide()

        for panel in self.panels:
            panel.hide()

        self.rolloverFrame.hide()


    def showDepartment(self, dept):
        self.currentDept = dept

        for button in self.departmentButtons:
            button.hide()

        self.backButton.show()

        cogList = CogIndexDepartments.get(dept, [])

        for panel in self.panels:
            panel.hide()

        columns = 7

        xStart = -0.72
        zStart = -.2

        xSpacing = 0.24
        zSpacing = 0.28

        visibleIndex = 0

        for visibleIndex, suitName in enumerate(cogList):
            panel = self.getPanelForSuit(suitName)

            if not panel:
                print 'No panel for suit:', suitName
                continue

            col = visibleIndex % columns
            row = visibleIndex / columns

            panel.setPos(xStart + col * xSpacing, 0, zStart - row * zSpacing)
            panel.show()

    def getPanelForSuit(self, suitName):
        return self.panelBySuitName.get(suitName)

    def unload(self):
        if hasattr(self, 'cogHeads'):
            for node in self.cogHeads:
                if node:
                    node.removeNode()
            self.cogHeads = []
        self.ignoreAll()
        self.title.destroy()
        self.rolloverFrame.destroy()
        for panel in self.panels:
            panel.destroy()
        for button in self.departmentButtons:
            button.destroy()
        self.backButton.destroy()
        del self.panels

        self.panelModel.removeNode()
        ShtikerPage.ShtikerPage.unload(self)

    def makeDepartmentButtons(self):
        self.departmentButtons = []

        icons = loader.loadModel('phase_3/models/gui/cog_icons')

        departments = [
            ('c', -0.5, -0.2),
            ('l',  0.0, -0.2),
            ('m',  0.5, -0.2),
            ('s', -0.5,-0.625),
            ('g',  0.0,-0.625),
            ('t',  0.5,-0.625),
            ('p',  0.0,-1.05),
        ]

        for dept, x, z in departments:
            geom = self.getDepartmentIcon(icons, dept)

            button = DirectButton(
                parent=self.iconNode,
                relief=None,
                geom=geom,
                geom_scale=.25,
                pos=(x, 0, z),
                command=self.showDepartment,
                extraArgs=[dept]
            )

            self.departmentButtons.append(button)

        icons.removeNode()

    def enter(self):
        self.updatePage()
        self.bigPanel = None
        self.nextPanel = None
        ShtikerPage.ShtikerPage.enter(self)
        return

    def exit(self):
        taskMgr.remove('buildingListResponseTimeout-later')
        taskMgr.remove('suitListResponseTimeout-later')
        taskMgr.remove('showCogRadarLater')
        taskMgr.remove('showBuildingRadarLater')
        # for index in xrange(0, len(self.radarOn)):
        #     if self.radarOn[index]:
        #         self.toggleRadar(index)
        #         self.radarButtons[index]['state'] = DGG.NORMAL

        ShtikerPage.ShtikerPage.exit(self)

    def __emblemChange(self, newEmblems):
        self.silverLabel['text'] = str(newEmblems[0])
        self.goldLabel['text'] = str(newEmblems[1])

    def grow(self, panel, pos):
        if self.bigPanel:
            print 'setting next panel - ' + str(panel)
            self.nextPanel = panel
            self.nextPanelPos = pos
            return
        print 'big panel - ' + str(panel)
        self.bigPanel = panel
        panel.reparentTo(self.enlargedPanelNode)
        panel.setScale(panel.getScale() * SCALE_FACTOR)
        if panel.summonButton:
            panel.summonButton.show()
            panel.summonButton['state'] = DGG.NORMAL

    def shrink(self, panel, pos):
        print 'trying to shrink - ' + str(panel)
        if panel != self.bigPanel:
            self.nextPanel = None
            return
        print 'shrink panel - ' + str(panel)
        self.bigPanel = None
        panel.setScale(panel.scale)
        panel.reparentTo(self.panelNode)
        if panel.summonButton:
            panel.summonButton.hide()
            panel.summonButton['state'] = DGG.DISABLED
        if self.nextPanel:
            self.grow(self.nextPanel, self.nextPanelPos)
        return

    # def toggleRadar(self, deptNum):
    #     messenger.send('wakeup')
    #     if self.radarOn[deptNum]:
    #         self.radarOn[deptNum] = 0
    #     else:
    #         self.radarOn[deptNum] = 1
    #     deptSize = SuitDNA.suitsPerDept
    #     panels = self.panels[deptSize * deptNum:SuitDNA.suitsPerDept * (deptNum + 1)]
    #     if self.radarOn[deptNum]:
    #         if hasattr(base.cr, 'currSuitPlanner'):
    #             if base.cr.currSuitPlanner != None:
    #                 base.cr.currSuitPlanner.d_suitListQuery()
    #                 self.acceptOnce('suitListResponse', self.updateCogRadar, extraArgs=[deptNum, panels])
    #                 taskMgr.doMethodLater(1.0, self.suitListResponseTimeout, 'suitListResponseTimeout-later', extraArgs=(deptNum, panels))
    #                 if self.radarButtons[deptNum].building:
    #                     base.cr.currSuitPlanner.d_buildingListQuery()
    #                     self.acceptOnce('buildingListResponse', self.updateBuildingRadar, extraArgs=[deptNum])
    #                     taskMgr.doMethodLater(1.0, self.buildingListResponseTimeout, 'buildingListResponseTimeout-later', extraArgs=(deptNum,))
    #             else:
    #                 self.updateCogRadar(deptNum, panels)
    #                 self.updateBuildingRadar(deptNum)
    #         else:
    #             self.updateCogRadar(deptNum, panels)
    #             self.updateBuildingRadar(deptNum)
    #         self.radarButtons[deptNum]['state'] = DGG.DISABLED
    #     else:
    #         self.updateCogRadar(deptNum, panels)
    #         self.updateBuildingRadar(deptNum)
    #     return

    def suitListResponseTimeout(self, deptNum, panels):
        self.updateCogRadar(deptNum, panels, 1)

    def buildingListResponseTimeout(self, deptNum):
        self.updateBuildingRadar(deptNum, 1)

    def makePanels(self):
        self.panels = []
        base.panels = []
        self.panelBySuitName = {}
        xStart = -1.66
        yStart = -0.18
        xOffset = 0.199
        yOffset = 0.2272
        gui = loader.loadModel('phase_3.5/models/gui/suit_detail_panel')
        gui.find('**/avatar_panel/shadow').setColor(1, 1, 1, 0.5)
        self.rolloverFrame = DirectFrame(parent=self.panelNode, relief=None, geom=gui.find('**/avatar_panel'), geom_color=(0.5, 0.5, 0.5, 1), geom_scale=(0.59, 0, 0.21), text_scale=0.06, text_pos=(0, 0.35), text='', text_fg=(1, 1, 1, 1), text_font=ToontownGlobals.getSuitFont(), pos=(0.8, 0, 0))
        self.rolloverFrame.setBin('gui-popup', 0)
        self.rolloverFrame.hide()
        gui.removeNode()
        for deptIndex, dept in enumerate(('c', 'l', 'm', 's', 'g', 't', 'p')):
            color = PANEL_COLORS[deptIndex]
            cogList = CogIndexDepartments.get(dept, [])

            for typeIndex, suitName in enumerate(cogList):
                panel = DirectLabel(
                parent=self.panelNode,
                pos=(xStart + typeIndex * xOffset, 0.0, yStart - deptIndex * yOffset),
                relief=None,
                state=DGG.NORMAL,
                image=self.panelModel,
                image_scale=(1, 1, 0.8),
                image_color=color,
                text=TTLocalizer.SuitPageMystery,
                text_scale=0.045,
                text_fg=(0, 0, 0, 1),
                text_pos=(0, 0.148, 0),
                text_font=ToontownGlobals.getSuitFont(),
                text_wordwrap=8
                )

                panel.suitName = suitName
                panel.dept = dept
                panel.deptIndex = deptIndex
                panel.typeIndex = typeIndex

                panel.scale = 0.7
                panel.setScale(panel.scale)
                panel.quotaLabel = None
                panel.head = None
                panel.shadow = None
                panel.count = 0
                panel.summonButton = None

                panel.hoverButton = DirectButton(
                    parent=panel,
                    relief=None,
                    image_scale=(.1, .1, .1),
                    image='phase_3/maps/invisible.png',
                    pressEffect=0
                )
                panel.hoverButton.setTransparency(True)
                panel.hoverButton.panel = panel
                self.panelBySuitName[suitName] = panel

                self.addCogRadarLabel(panel)

                self.panels.append(panel)
                base.panels.append(panel)

                panel.hoverButton.bind(DGG.ENTER, self.showCogHoverInfo, [panel])
                panel.hoverButton.bind(DGG.EXIT, self.hideCogHoverInfo)

    def showCogHoverInfo(self, panel, extra=None):
        suitName = panel.suitName

        text = self.getCogHoverText(suitName)

        pos = panel.getPos(aspect2d)

        x = pos.getX() + 0.028
        z = pos.getZ()

        # keep it from going off right side
        if x > 0.9:
            x = pos.getX() - 0.028

        self.hoverInfoText['text'] = text
        self.hoverInfo.setPos(x, -0.5, z)
        self.hoverInfo.show()


    def hideCogHoverInfo(self, extra=None):
        self.hoverInfo.hide()

    def getAttackDamageText(self, attack):
        hp = getattr(attack, 'hp', None)

        if hp is None:
            return ''

        if isinstance(hp, tuple) or isinstance(hp, list):
            if len(hp) >= 2:
                return 'Damage Range: %s-%s' % (hp[0], hp[-1])
            elif len(hp) == 1:
                return 'Damage: %s' % hp[0]

        return 'Damage Range: %s' % hp

    def getCogHoverText(self, suitName):
        attrs = SuitBattleGlobals.SuitAttributes.get(suitName, {})

        name = attrs.get('name', suitName)
        levelText = self.getCogLevelText(suitName)
        attacks = attrs.get('attacks', [])

        text = 'Suit Name: %s\n\n' % name
        text += '%s\n\n' % levelText
        text += 'Suit Attacks:\n\n'

        attackNames = []

        for attack in attacks:
            displayName = TTLocalizer.SuitAttackNames.get(
                attack.name,
                attack.name
            ).rstrip('!') + '-'

            damageText = self.getAttackDamageText(attack)

            line = '%s%s' % (displayName, damageText)

            if line not in attackNames:
                attackNames.append(line)

        text += '\n'.join(attackNames)

        return text

    def showInfo(self, panel, text, extra):
        self.rolloverFrame.reparentTo(panel)
        self.rolloverFrame.show()
        self.rolloverFrame['text'] = text

    def hideInfo(self, extra):
        self.rolloverFrame.hide()

    def getCogStatus(self, suitName):
        if suitName in FACILITY_MANAGER_SUITS:
            return 'Facility Manager'
        elif suitName in CONTRACTOR_SUITS:
            return 'Contractor'
        elif suitName in SECRETARY_SUITS:
            return 'Secretary'
        elif suitName in MANAGER_SUITS:
            return 'Manager'
        else:
            return 'Employee'

    def addQuotaLabel(self, panel):
        suitName = panel.suitName

        status = self.getCogStatus(suitName)

        quotaLabel = DirectLabel(
            parent=panel,
            pos=(0.0, 0.0, -0.172),
            relief=None,
            state=DGG.DISABLED,
            text=status,
            text_scale=0.045,
            text_fg=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont()
        )

        quotaLabel.setBin('gui-popup', 50)
        panel.quotaLabel = quotaLabel
        return
    
    def createSuitHead(self, suitName, panel, dimension=.25, setH=180):
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit(suitName)
        suit = Suit.Suit()
        suit.setDNA(suitDNA)
        headParts = suit.getHeadParts()
        animatedHeadParts = suit.getAnimatedHeadParts()
        head = panel.attachNewNode('head')
        head.setBin("gui-popup", 50)
        hasAnimatedHead = False
        for part in headParts:
            for part in animatedHeadParts:
                hasAnimatedHead = True
            if hasAnimatedHead:
                if 'neutral' in part.getAnimNames() and suitName in ToontownGlobals.animSuitHeadsPosedNeutral:
                    part.pose('neutral', 1)

            if suitName in (
                'mh',
                'mh2',
                'std2',
                'ds',
                'cv'
                ):
                copyPart = part.copyTo(head)
                copyPart.setDepthTest(1)
                copyPart.setDepthWrite(1)
            else:
                part.setTwoSided(True)
                part.setDepthTest(1)
                part.setDepthWrite(1)

                part.reparentTo(head)
        self.fitGeometry(head, fFlip=1, dimension=dimension, setH=setH)
        suit.delete()
        suit = None
        return head
    
    def fitGeometry(self, geom, fFlip = 0, dimension = 0.25, setH=180):
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

        geomXform.setPosHprScale(-mid[0], -mid[1] + 1, -mid[2], setH, 0, 0, s, s, s)
        geomXform.reparentTo(geom)

    def addSuitHead(self, panel, suitName):
        if panel.head:
            panel.head.removeNode()
            panel.head = None

        sourceHead = self.getCogHead(suitName)
        panel.head = sourceHead.copyTo(panel)
        panel.head.setPos(0, 0, 0)
        panel.head.setScale(1)

    def addCogRadarLabel(self, panel):
        cogRadarLabel = DirectLabel(parent=panel, pos=(0.0, 0.0, -0.172), relief=None, state=DGG.DISABLED, text='', text_scale=0.05, text_fg=(0, 0, 0, 1), text_font=ToontownGlobals.getSuitFont())
        panel.cogRadarLabel = cogRadarLabel
        return

    def addSummonButton(self, panel):
        buttons = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')
        okButtonList = (buttons.find('**/ChtBx_OKBtn_UP'), buttons.find('**/ChtBx_OKBtn_DN'), buttons.find('**/ChtBx_OKBtn_Rllvr'))
        gui = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        iconGeom = gui.find('**/summons')
        summonButton = DirectButton(parent=panel, pos=(0.1, 0.0, -0.104), scale=0.1, relief=None, state=DGG.NORMAL, image=okButtonList, image_scale=13.0, geom=iconGeom, geom_scale=0.7, text=('',
         TTLocalizer.IssueSummons,
         TTLocalizer.IssueSummons,
         ''), text_scale=0.4, text_pos=(-1.1, -0.32), command=self.summonButtonPressed, extraArgs=[panel])
        panel.summonButton = summonButton
        return

    def summonButtonPressed(self, panel):
        panelIndex = self.panels.index(panel)
        self.summonDialog = SummonCogDialog.SummonCogDialog(panelIndex)
        self.summonDialog.load()
        self.accept(self.summonDialog.doneEvent, self.summonDone, extraArgs=[panel])
        self.summonDialog.enter()

    def summonDone(self, panel):
        if self.summonDialog:
            self.summonDialog.unload()
            self.summonDialog = None
        index = self.panels.index(panel)
        if not base.localAvatar.hasCogSummons(index):
            panel.summonButton.hide()

    def addBuildingRadarLabel(self, button):
        gui = loader.loadModel('phase_3.5/models/gui/suit_detail_panel')
        zPos = BUILDING_RADAR_POS[self.radarButtons.index(button)]
        buildingRadarLabel = DirectLabel(parent=button, relief=None, pos=(0.225, 0.0, zPos), state=DGG.DISABLED, image=gui.find('**/avatar_panel'), image_hpr=(0, 0, 90), image_scale=(0.05, 1, 0.1), image_pos=(0, 0, 0.015), text=TTLocalizer.SuitPageBuildingRadarP % '0', text_scale=0.05, text_fg=(1, 0, 0, 1), text_font=ToontownGlobals.getSuitFont())
        gui.removeNode()
        button.buildingRadarLabel = buildingRadarLabel

    def loadCogHeads(self):
        if hasattr(self, 'cogHeads'):
            for node in self.cogHeads:
                if node:
                    node.removeNode()

        self.cogHeads = []

        for index in xrange(len(SuitDNA.suitHeadTypes)):
            suitName = SuitDNA.suitHeadTypes[index]

            headNode = NodePath('headNode')

            try:
                # Use YOUR existing working head creation logic here.
                # This is the method from the uploaded file's style:
                head = self.createSuitHead(suitName, dimension=0.22)
                head.reparentTo(headNode)

                headNode.setScale(1.0)
                headNode.setPos(0, 0, 0)

                self.cogHeads.append(headNode)

            except Exception as e:
                print 'Could not load cog head %s: %s' % (suitName, e)
                self.cogHeads.append(None)

    def resetPanel(self, dept, type):
        DEPT_ORDER = ['c', 'l', 'm', 's', 'g', 't', 'p']

        cogList = CogIndexDepartments.get(DEPT_ORDER[dept], [])

        if type >= len(cogList):
            return

        suitName = cogList[type]
        panel = self.panelBySuitName.get(suitName)

        if not panel:
            return


        panel['text'] = TTLocalizer.SuitPageMystery

        if panel.cogRadarLabel:
            panel.cogRadarLabel.hide()
        if panel.quotaLabel:
            panel.quotaLabel.hide()
        if panel.shadow:
            panel.shadow.hide()
        if panel.summonButton:
            panel.summonButton.hide()

        self.rolloverFrame.hide()

        # panel.hoverButton.unbind(DGG.ENTER)
        # panel.hoverButton.unbind(DGG.EXIT)

        color = PANEL_COLORS[panel.deptIndex]
        panel['image_color'] = color

    def setPanelStatus(self, panel, status):
        suitName = panel.suitName
        index = SuitDNA.suitHeadTypes.index(suitName)

        if status == COG_UNSEEN:
            panel['text'] = TTLocalizer.SuitPageMystery

        elif status == COG_BATTLED:
            suitFullName = SuitBattleGlobals.SuitAttributes[suitName]['name']
            panel['text'] = suitFullName

            if panel.quotaLabel:
                panel.quotaLabel.show()
            else:
                self.addQuotaLabel(panel)

            if panel.head:
                panel.head.show()
            else:
                self.addSuitHead(panel, suitName)

        elif status == COG_DEFEATED:
            # Remove this if you no longer want quota/count text.
            if panel.quotaLabel:
                panel.quotaLabel.show()

        elif status == COG_COMPLETE1:
            panel['image_color'] = PANEL_COLORS_COMPLETE1[panel.deptIndex]

        elif status == COG_COMPLETE2:
            panel['image_color'] = PANEL_COLORS_COMPLETE2[panel.deptIndex]
    
    def updateAllCogs(self, status):
        for index in xrange(0, len(base.localAvatar.cogs)):
            base.localAvatar.cogs[index] = status
        self.updatePage()

    def updatePage(self):
        DEPT_ORDER = ['c', 'l', 'm', 's', 'g', 't', 'p']

        for deptIndex, deptName in enumerate(DEPT_ORDER):
            cogList = CogIndexDepartments.get(deptName, [])

            for typeIndex, suitName in enumerate(cogList):
                try:
                    index = SuitDNA.suitHeadTypes.index(suitName)
                except ValueError:
                    continue

                self.updateCogStatus(deptIndex, typeIndex, base.localAvatar.cogs[index])

    def updateCogStatus(self, dept, type, status):
        if dept == 5:
            pass 
        if dept < 0 or dept > len(SuitDNA.suitDepts):
            print 'ucs: bad cog dept: ', dept
        elif type < 0 or type > SuitDNA.suitsPerDept:
            print 'ucs: bad cog type: ', type
        elif status < COG_UNSEEN or status > COG_COMPLETE2:
            print 'ucs: bad status: ', status
        else:
            self.resetPanel(dept, type)
            suitName = CogIndexDepartments[DEPT_ORDER[dept]][type]
            panel = self.panelBySuitName.get(suitName)
            if status == COG_UNSEEN:
                self.setPanelStatus(panel, COG_UNSEEN)
            elif status == COG_BATTLED:
                self.setPanelStatus(panel, COG_BATTLED)
            elif status == COG_DEFEATED:
                self.setPanelStatus(panel, COG_BATTLED)
                self.setPanelStatus(panel, COG_DEFEATED)
            elif status == COG_COMPLETE1:
                self.setPanelStatus(panel, COG_BATTLED)
                self.setPanelStatus(panel, COG_DEFEATED)
                self.setPanelStatus(panel, COG_COMPLETE1)
            elif status == COG_COMPLETE2:
                self.setPanelStatus(panel, COG_BATTLED)
                self.setPanelStatus(panel, COG_DEFEATED)
                self.setPanelStatus(panel, COG_COMPLETE2)

    def updateCogRadarButtons(self, radars):
        for index in xrange(0, len(radars)):
            if radars[index] == 1:
                self.radarButtons[index]['state'] = DGG.NORMAL

    def updateCogRadar(self, deptNum, panels, timeout = 0):
        taskMgr.remove('suitListResponseTimeout-later')
        if not timeout and hasattr(base.cr, 'currSuitPlanner') and base.cr.currSuitPlanner != None:
            cogList = base.cr.currSuitPlanner.suitList
        else:
            cogList = []
        for panel in panels:
            panel.count = 0
        for cog in cogList:
            if cog - ((len(SuitDNA.suitDepts)) * SuitDNA.suitsPerDept - 1) > 0: 
                pass 
            else:
                self.panels[cog].count += 1
        for panel in panels:
            panel.cogRadarLabel['text'] = TTLocalizer.SuitPageCogRadar % panel.count
            if self.radarOn[deptNum]:
                panel.quotaLabel.hide()
                def showLabel(label):
                    label.show()
                taskMgr.doMethodLater(RADAR_DELAY * panels.index(panel), showLabel, 'showCogRadarLater', extraArgs=(panel.cogRadarLabel,))
                def activateButton(s = self, index = deptNum):
                    self.radarButtons[index]['state'] = DGG.NORMAL
                    return Task.done
                if not self.radarButtons[deptNum].building:
                    taskMgr.doMethodLater(RADAR_DELAY * len(panels), activateButton, 'activateButtonLater')
            else:
                panel.cogRadarLabel.hide()
                panel.quotaLabel.show()
        return

    def updateBuildingRadarButtons(self, radars):
        for index in xrange(0, len(radars)):
            if radars[index] == 1:
                self.radarButtons[index].building = 1

    def updateBuildingRadar(self, deptNum, timeout = 0):
        taskMgr.remove('buildingListResponseTimeout-later')
        if not timeout and hasattr(base.cr, 'currSuitPlanner') and base.cr.currSuitPlanner != None:
            buildingList = base.cr.currSuitPlanner.buildingList
        else:
            buildingList = [0,
             0,
             0,
             0,
             0,
             0]
        # button = self.radarButtons[deptNum]
        # if button.building:
        #     if not button.buildingRadarLabel:
        #         self.addBuildingRadarLabel(button)
        #     if self.radarOn[deptNum]:
        #         num = buildingList[deptNum]
        #         if num == 1:
        #             button.buildingRadarLabel['text'] = TTLocalizer.SuitPageBuildingRadarS % num
        #         else:
        #             button.buildingRadarLabel['text'] = TTLocalizer.SuitPageBuildingRadarP % num
        #         def showLabel(button):
        #             button.buildingRadarLabel.show()
        #             button['state'] = DGG.NORMAL

        #         taskMgr.doMethodLater(RADAR_DELAY * SuitDNA.suitsPerDept, showLabel, 'showBuildingRadarLater', extraArgs=(button,))
        #     else:
        #         button.buildingRadarLabel.hide()
