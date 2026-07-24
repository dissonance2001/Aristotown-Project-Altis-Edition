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
DEPARTMENT_CODES = ['c', 'l', 'm', 's', 'g', 't', 'p']

DEPARTMENT_ICON_PATHS = {
    'c': '**/CorpIcon',
    'l': '**/LegalIcon',
    'm': '**/MoneyIcon',
    's': '**/SalesIcon',
    'g': '**/LegalIcon',
    't': '**/LegalIcon',
    'p': '**/LegalIcon',
}

DEPARTMENT_SPLASH_POSITIONS = {
    'c': (-0.52, 0, 0.0),
    'l': (0.0, 0, 0.0),
    'm': (0.52, 0, 0.0),

    's': (-0.52, 0, -0.15),
    'g': (0.0, 0, -0.15),
    't': (0.52, 0, -0.15),

    'p': (0.0, 0, -0.3),
}
MANAGER_SUITS = [
'clubpres', 'ovt', 'derrman', 'derrhand', 'mplayer', 'fires', 'fbed', 'mplayer2', 'chainsaw', 'chainsaw2', 'phouse', 'bkeeper', 'wtapper', 'ambass', 'foreman', 'dopr', 'dopa',
                  'bellring', 'prethink', 'mslacker', 'videog', 'radiog', 'ubuster', 'racket', 'safesupervis', 'psetter', 'supervis', 'duckshfl', 'treek', 'styx', 'nix', 'hydra',
                  'kerberos', 'charon', 'pcrat', 'clerk', 'mouthp', 'rainmake', 'whunter', 'wsi',
                  'liquidr', 'treasure', 'hustle', 'bookkeep', 
                  'sgoat', 'caseman', 'stenog', 'lgator', 'bdirector', 'ddiver', 'gatekeep', 'dola', 'dold', 'dking',
                  'sya', 'pbl', 'liquid', 'cbutcher', 'cdirector', 'rkeeper'
]
COG_BIO_QUOTES = {
    'bkeeper': 'Every cent must be accounted for.',
    'wtapper': 'Your call may be monitored.',
    'ambass': 'Let us discuss the terms.',
}
DEPT_ORDER = ['c', 'l', 'm', 's', 'g', 't', 'p']
BOSS_COGS = ['ceo', 'cj', 'clo', 'cfo', 'vp', 'cio', 'hocn', 'chairman', 'chairman2', 'ottoman']
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
CogNameAbbreviations = {
    'dold': 'D.O.L.D.',
    'dopa': 'D.O.P.A.',
    'dopr': 'D.O.P.R.',
    'dola': 'D.O.L.A.',
    'wsi': 'W.S.I.',
    'redd': 'Redd Heir Wing',
    'ceo': 'C.E.O.',
    'clo': 'C.L.O.',
    'vp': 'Senior V.P.',
    'cio': 'C.I.O.',
    'hocn': 'H.O.C.N.',
    'cfo': 'C.F.O.',
    'chairman': 'Chairman',
    'ottoman': 'C.O.O.',
}
CogIndexDepartments = {
    'c': ['f', 'p', 'stg', 'ym', 'enf', 'psh', 'mm', 'ds', 'blh', 'stck', 'hh', 'bsht', 'ppg', 'mldr', 'cr', 'wnk', 'drk', 'ksp', 'txl', 'tbc', 'autocad', 'clubpres', 'derrman', 'derrhand', 'fires', 'fbed', 'mplayer', 'chainsaw',
          'choreo', 'phouse', 'bkeeper', 'wtapper', 'ambass', 'ceo'],
    's': ['cc', 'tm', 'sbg', 'nd', 'dc', 'gh', 'mad', 'ms', 'lvw', 'bam', 'tf', 'fcs', 'ppl', 'm', 'cnd', 'std', 'mh', 'foreman', 'dopr', 'dopa', 'bellring', 'prethink', 'mslacker', 'psetter', 'cinema', 'hustle', 
    'radiog', 'ubuster', 'safesupervis', 'vp'],
    'l': ['bf', 'bf2', 'b', 'b2', 'bsd', 'pf', 'dt', 'dt2', 'nn', 'dcr', 'cv', 'ac', 'ac2', 'bs', 'bs2', 'ad', 'dcw', 'bck', 'sd', 'sd2', 'sh', 'surg', 'rat', 'le', 'le2', 'magi', 'whistleb', 'br', 'bw', 'bw2',
          'clerk', 'judy', 'mouthp', 'rainmake', 'whunter', 'erclaim', 'redd', 'wsi', 'sgoat', 'caseman', 'stenog', 'lgator', 'cj', 'clo'],
    'm': ['sc', 'pp', 'nb', 'qc', 'shy', 'tw', 'trs', 'pwn', 'bc', 'nc', 'cow', 'brck', 'mb', 'aud', 'ls', 'gld', 'fct', 'bfh', 'rb', 'supervis', 'duckshfl', 'treek', 'pcrat', 'erfit', 'hroller', 'bookkeep', 'racket',
          'liquidr', 'treasure', 'cfo'],
    'g': ['bgh', 'ca', 'pph', 'cn', 'ins', 'sw', 'cbr', 'mdm', 'shrp', 'dl', 'txm', 'neg', 'shw', 'rng', 'cor', 'sab', 'mg', 'bfh2', 'chw', 'ang', 'hho', 'dola', 'dold', 'ddiver', 'gatekeep', 'fmaker', 'liquid',
        'rkeeper', 'dking', 'cdirector', 'ottoman', 'chairman'],  # boardbots
    't': ['skd', 'cmk', 'dhr', 'vpr', 'brn', 'sdb', 'key', 'kbc', 'blk', 'sfs', 'pyc', 'inw', 'itn', 'rus', 'djockey', 'videog', 'cio'],  # techbots
    'p': ['ppb', 'shb', 'gms', 'hck', 'ghw', 'gzt', 'nsh', 'anc', 'director', 'hocn'],  # pressbots
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
        self.currentDept = None
        self.rowIndex = 0

        self.cogsPerRow = 6
        self.visibleRows = 3
        self.cogsPerPage = (
            self.cogsPerRow * self.visibleRows
        )

    def load(self):
        ShtikerPage.ShtikerPage.load(self)

        self.currentDept = None
        self.rowIndex = 0
        self.cogHeadCache = {}
        self.cogHeads = []
        auxGui = loader.loadModel(
            'phase_3/models/gui/ttcc_gui_generalButtons'
        )

        suitPageButtons = loader.loadModel(
            'phase_3.5/models/gui/suitpage_buttons'
        )

        suitPageStatic = loader.loadModel(
            'phase_3.5/models/gui/suitpage_static'
        )

        suitPageSplash = loader.loadModel(
            'phase_3.5/models/gui/suitpage_splash'
        )

        icons = loader.loadModel(
            'phase_3/models/gui/cog_icons'
        )
        # self.homePageNode = NodePath(
        #     'homePageNode'
        # )
        #self.homePageNode.reparentTo(self.guiTop)
        border = suitPageSplash.find('**/border')
        logo = suitPageSplash.find('**/cogs_logo')

        self.guiTop = DirectFrame(
            parent=self,
            relief=None
        )
        self.guiTop.setZ(0.625)

        # Home page root.
        self.homePageNode = NodePath('homePageNode')
        self.homePageNode.reparentTo(self.guiTop)

        # Department page root.
        self.departmentPageNode = NodePath(
            'departmentPageNode'
        )
        self.departmentPageNode.reparentTo(
            self.guiTop
        )
        self.bioPageNode = NodePath('bioPageNode')
        self.bioPageNode.reparentTo(self.guiTop)

        self.currentBioSuit = None
        self.suitModel = None
        self.bioPageNode.hide()
        bio = suitPageStatic.find('**/bio')

        self.bioFrame = DirectFrame(
            parent=self.bioPageNode,
            relief=None,
            image=bio,
            image_scale=(1.7, 1, 1.2),
            pos=(0, 0, -0.58)
        )

        self.bioFrame.setBin('gui-popup', 0)
        self.bioFrame.setDepthTest(False)
        self.bioFrame.setDepthWrite(False)

        self.bioBackButton = DirectButton(
            parent=self.bioFrame,
            relief=None,
            state=DGG.NORMAL,
            geom=(
                suitPageButtons.find('**/back_neutral'),
                suitPageButtons.find('**/back_press'),
                suitPageButtons.find('**/back_hover'),
                suitPageButtons.find('**/back_press')
            ),
            geom_scale=(0.4, 1, 0.2),
            pos=(-0.39, 1, -0.6),
            frameSize=(-0.19, 0.19, -0.09, 0.09),
            command=self.leaveCogBio
        )

        self.bioCogNameLabel = DirectLabel(
            parent=self.bioFrame,
            relief=None,
            text='',
            text_scale=0.0545,
            text_fg=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont(),
            text_align=TextNode.ACenter,
            text_wordwrap=12,
            pos=(-0.02, 0, 0.325)
        )

        self.bioCogQuoteLabel = DirectLabel(
            parent=self.bioFrame,
            relief=None,
            text='',
            text_scale=0.038,
            text_fg=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont(),
            text_align=TextNode.ACenter,
            text_wordwrap=16,
            pos=(-0.36, 0, 0.17)
        )

        self.bioCogLevelLabel = DirectLabel(
            parent=self.bioFrame,
            relief=None,
            text='',
            text_scale=0.04,
            text_fg=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont(),
            text_align=TextNode.ALeft,
            pos=(-0.675, 0, 0.01)
        )

        self.bioCogDamageLabel = DirectLabel(
            parent=self.bioFrame,
            relief=None,
            text='',
            text_scale=0.04,
            text_fg=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont(),
            text_align=TextNode.ALeft,
            pos=(-0.675, 0, -0.04)
        )

        self.bioCogStatusLabel = DirectLabel(
            parent=self.bioFrame,
            relief=None,
            text='',
            text_scale=0.04,
            text_fg=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont(),
            text_align=TextNode.ALeft,
            pos=(-0.675, 0, -0.09)
        )

        self.bioCogAttacksLabel = DirectLabel(
            parent=self.bioFrame,
            relief=None,
            text='',
            text_scale=0.035,
            text_fg=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont(),
            text_align=TextNode.ALeft,
            text_wordwrap=18,
            pos=(-0.675, 0, -0.13)
        )

        self.bioBackButton.setBin('gui-popup', 100)

        # All Cog panels belong to departmentPageNode.
        self.panelNode = NodePath('panelNode')
        self.panelNode.reparentTo(
            self.departmentPageNode
        )

        self.enlargedPanelNode = NodePath(
            'enlargedPanelNode'
        )
        self.enlargedPanelNode.reparentTo(
            self.departmentPageNode
        )

        # Home icons belong to homePageNode.
        self.iconNode = NodePath('iconNode')
        self.iconNode.reparentTo(
            self.homePageNode
        )

        self.splashFrame = DirectFrame(
            parent=self.homePageNode,
            relief=None,
            image=border,
            image_scale=(1.9, 0, 0.95),
            pos=(0.018, 0, -0.77)
        )

        self.splashLogo = DirectFrame(
            parent=self.homePageNode,
            relief=None,
            image=logo,
            image_scale=(0.7, 0, 0.35),
            pos=(0.018, 0, -0.11)
        )
        departments = [
            ('c', -0.52,  0.22),
            ('l',  0.00,  0.22),
            ('m',  0.52,  0.0),

            ('s', -0.52, -0.0),
            ('g',  0.00, -0.0),
            ('t',  0.52, -0.0),

            ('p',  0.00, -0.22),
        ]


        # self.panelNode = NodePath('suitPagePanelNode')
        # self.panelNode.reparentTo(self.departmentNode)
        self.rowFrames = []
        # Department page background.
        background = suitPageStatic.find('**/base_boardbot')

        # Fallback if the custom background isn't present.
        if background.isEmpty():
            background = suitPageStatic.find('**/bg')

        # Final fallback so it never crashes.
        if background.isEmpty():
            self.backgroundFrame = DirectFrame(
                parent=self.departmentPageNode,
                relief=None,
                frameColor=(0.85, 0.85, 0.85, 1),
                frameSize=(-0.8, 0.8, -0.55, 0.55),
                pos=(0, 0, -.7)
            )
        else:
            self.backgroundFrame = DirectFrame(
                parent=self.departmentPageNode,
                relief=None,
                image=background,
                image_scale=1.65,
                pos=(0, 0, -.7)
            )
        self.backgroundFrame.setBin('gui-popup', 0)
        self.backgroundFrame.setDepthTest(False)
        self.backgroundFrame.setDepthWrite(False)
        # Everything on the department page sits on top of this.
        self.panelNode.reparentTo(self.backgroundFrame)
        self.enlargedPanelNode.reparentTo(self.backgroundFrame)
        rowGeom = suitPageStatic.find('**/row')

        if rowGeom.isEmpty():
            print 'SuitPage: could not find **/row'
        else:
            for rowIndex in xrange(self.visibleRows):
                rowFrame = DirectFrame(
                    parent=self.backgroundFrame,
                    relief=None,
                    image=rowGeom,
                    image_scale=(1.6, 1, .6),
                    pos=(
                        -0.01,
                        0,
                        0.3 - rowIndex * 0.35
                    )
                )

                # Keep the rows behind the Cog contents.
                rowFrame.setBin('gui-popup', 10)
                rowFrame.setDepthTest(False)
                rowFrame.setDepthWrite(False)

                self.rowFrames.append(rowFrame)
        self.panelNode.setBin('gui-popup', 10)
        self.enlargedPanelNode.setBin('gui-popup', 20)
        self.pageUpButton = DirectButton(
            parent=self.departmentPageNode,
            relief=None,
            state=DGG.DISABLED,
            geom=(
                suitPageButtons.find(
                    '**/arrow_neutral'
                ),
                suitPageButtons.find(
                    '**/arrow_press'
                ),
                suitPageButtons.find(
                    '**/arrow_hover'
                ),
                suitPageButtons.find(
                    '**/arrow_press'
                )
            ),
            geom_scale=(0.08, 1, 0.08),
            pos=(0.8, 0, -0.5),
            frameSize=(-0.04, 0.04, -0.04, 0.04),
            command=self.changeRowIndex,
            extraArgs=[-1]
        )
        self.pageUpButton.setBin('gui-popup', 10)
        self.pageDownButton = DirectButton(
            parent=self.departmentPageNode,
            relief=None,
            state=DGG.DISABLED,
            geom=(
                suitPageButtons.find(
                    '**/arrow_neutral'
                ),
                suitPageButtons.find(
                    '**/arrow_press'
                ),
                suitPageButtons.find(
                    '**/arrow_hover'
                ),
                suitPageButtons.find(
                    '**/arrow_press'
                )
            ),
            geom_scale=(0.08, 1, 0.08),
            pos=(0.8, 0, -0.58),
            hpr=(0, 180, 0),
            frameSize=(-0.04, 0.04, -0.04, 0.04),
            command=self.changeRowIndex,
            extraArgs=[1]
        )
        self.pageDownButton.setBin('gui-popup', 10)
        # Department page background.
        background = suitPageStatic.find('**/base_boardbot')

        if background.isEmpty():
            background = suitPageStatic.find('**/bg')

        self.backgroundFrame = DirectFrame(
            parent=self.departmentPageNode,
            relief=None,
            image=background,
            image_scale=1.65,
            pos=(0, 0, -0.7)
        )
        # Reparent panel nodes to the visible background.
        self.panelNode.reparentTo(self.backgroundFrame)
        self.enlargedPanelNode.reparentTo(
            self.backgroundFrame
        )


        self.departmentButtons = []

        self.makeDepartmentButtons()

        # Close/back button from SuitPage(9).
        self.backButton = DirectButton(
            parent=self.backgroundFrame,
            relief=None,
            state=DGG.NORMAL,
            image=(
                auxGui.find('**/CloseBtn_UP'),
                auxGui.find('**/CloseBtn_DN'),
                auxGui.find('**/CloseBtn_Rllvr')
            ),
            pos=(0.69, 0, 0.47),
            command=self.showDepartmentHome
        )
        self.backButton.setBin('gui-popup', 200)
        self.backButton.setDepthTest(False)
        self.backButton.setDepthWrite(False)

        # Department title.
        self.departmentTitle = DirectLabel(
            parent=self.backgroundFrame,
            relief=None,
            text='',
            text_scale=0.08,
            text_fg=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont(),
            text_align=TextNode.ACenter,
            pos=(0, 0, 0.5875)
        )
        self.departmentTitle.setBin('gui-popup', 50)
        self.departmentTitle.setDepthTest(False)
        self.departmentTitle.setDepthWrite(False)

        # Keep SuitPage(10)'s Cog card models and functionality.
        gui = loader.loadModel(
            'phase_3.5/models/gui/suitpage_gui'
        )

        #self.panelModel = gui.find('**/card')
        self.shadowModels = []

        for index in xrange(
            1,
            len(SuitDNA.suitHeadTypes) + 1
        ):
            self.shadowModels.append(
                gui.find('**/shadow' + str(index))
            )

        #self.loadCogHeads()
        self.makePanels()

        gui.removeNode()

        self.radarOn = [0, 0, 0, 0, 0, 0, 0]

        self.bigPanel = None
        self.nextPanel = None

        self.makeHoverInfo()

        self.showDepartmentHome()

        suitPageButtons.removeNode()
        suitPageStatic.removeNode()
        suitPageSplash.removeNode()
        icons.removeNode()
        auxGui.removeNode()

    def getDepartmentSplashImage(
            self,
            suitPageSplash,
            dept):

        splashPaths = {
            'c': '**/boss_2',
            'l': '**/law_2',
            'm': '**/cash_2',
            's': '**/sell_2',

            # Change these to your actual custom node names.
            'g': '**/board_2',
            't': '**/board_2',
            'p': '**/board_2',
        }

        path = splashPaths.get(dept)
        image = suitPageSplash.find(path)

        if image.isEmpty():
            print (
                'Missing department splash image:',
                dept,
                path
            )
            return None

        return image

    def makeHoverInfo(self):
        gui = loader.loadModel(
            'phase_3.5/models/gui/suit_detail_panel'
        )

        shadow = gui.find('**/shadow')

        if not shadow.isEmpty():
            shadow.setTransparency(
                TransparencyAttrib.MAlpha
            )
            shadow.setColor(1, 1, 1, 0.4)

        self.hoverInfo = DirectFrame(
            parent=base.a2dTopRight,
            relief=None,
            geom=gui.find('**/avatar_panel'),
            geom_scale=(0.5, 0.25, 0.175),
            geom_color=(0.69, 0.706, 0.718, 1),
            geom_pos=(-1.275, -0.5, -1),
            pos=(0, 0, 0)
        )

        self.hoverInfo.setBin('gui-popup', 100)

        self.hoverInfoText = DirectLabel(
            parent=self.hoverInfo,
            relief=None,
            text='',
            text_scale=0.045,
            text_fg=(0, 0, 0, 1),
            text_align=TextNode.ACenter,
            text_wordwrap=22,
            pos=(-1.275, -0.5, -0.75),
            text_font=ToontownGlobals.getSuitFont()
        )

        self.hoverInfoText.setBin('gui-popup', 100)
        self.hoverInfo.hide()

        gui.removeNode()
    
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
    
    def getCogBioQuote(self, suitName):
        return COG_BIO_QUOTES.get(
            suitName,
            'Business is business.'
        )
        
    def showCogDetails(self, panel, extra=None):
        suitName = getattr(panel, 'suitName', None)

        if suitName is None:
            index = self.panels.index(panel)
            suitName = SuitDNA.suitHeadTypes[index]

        attrs = SuitBattleGlobals.SuitAttributes.get(
            suitName,
            {}
        )

        name = attrs.get('name', suitName)
        levelText = self.getCogLevelText(suitName)

        text = '%s\n%s' % (
            name,
            levelText
        )

        attacks = attrs.get('attacks', ())

        if attacks:
            attackNames = []

            for attack in attacks:
                if isinstance(attack, (tuple, list)):
                    attackNames.append(str(attack[0]))
                else:
                    attackNames.append(str(attack))

            text += '\nAttacks:\n' + ', '.join(
                attackNames
            )

        self.showInfo(panel, text, None)
    
    def showDepartmentHome(self):
        self.resetEnlargedPanel()

        self.currentDept = None
        self.rowIndex = 0

        self.cleanupBioSuitModel()

        self.bioPageNode.hide()
        self.departmentPageNode.hide()
        self.homePageNode.show()

        self.backButton.hide()

        for panel in self.panels:
            panel.hide()

        if hasattr(self, 'rolloverFrame'):
            self.rolloverFrame.hide()

        if hasattr(self, 'hoverInfo'):
            self.hoverInfo.hide()

    def changeRowIndex(self, amount):
        if self.currentDept is None:
            return

        cogList = CogIndexDepartments.get(
            self.currentDept,
            []
        )

        totalRows = (
            len(cogList) + self.cogsPerRow - 1
        ) // self.cogsPerRow

        maxRowIndex = max(
            0,
            totalRows - self.visibleRows
        )

        newIndex = self.rowIndex + amount

        if newIndex < 0:
            newIndex = 0
        elif newIndex > maxRowIndex:
            newIndex = maxRowIndex

        if newIndex == self.rowIndex:
            return

        self.resetEnlargedPanel()

        self.rowIndex = newIndex
        self.refreshDepartmentPanels()

    def getCogDisplayName(self, suitName, abbreviate=False):
        attrs = SuitBattleGlobals.SuitAttributes.get(suitName)

        # Failsafe if the suit doesn't exist
        if attrs is None:
            return "???"

        fullName = attrs.get('name', suitName)

        if suitName in CogNameAbbreviations:
            if abbreviate:
                return CogNameAbbreviations[suitName]

        return fullName

    def refreshDepartmentPanels(self):
        for panel in self.panels:
            panel.hide()

            if panel.head:
                panel.head.hide()

        if self.currentDept is None:
            self.pageUpButton['state'] = DGG.DISABLED
            self.pageDownButton['state'] = DGG.DISABLED
            return

        cogList = CogIndexDepartments.get(
            self.currentDept,
            []
        )

        firstCogIndex = (
            self.rowIndex * self.cogsPerRow
        )

        lastCogIndex = min(
            firstCogIndex + self.cogsPerPage,
            len(cogList)
        )

        visibleCogs = cogList[
            firstCogIndex:lastCogIndex
        ]

        xStart = -0.555
        zStart = 0.3

        xSpacing = 0.219
        zSpacing = 0.35

        for visibleIndex, suitName in enumerate(
            visibleCogs
        ):
            panel = self.getPanelForSuit(suitName)

            if panel is None:
                print 'No panel for suit:', suitName
                continue

            column = (
                visibleIndex % self.cogsPerRow
            )

            row = (
                visibleIndex // self.cogsPerRow
            )

            panel.reparentTo(self.panelNode)

            panel.setPos(
                xStart + (column * xSpacing),
                0,
                zStart - (row * zSpacing)
            )

            panel.setScale(panel.scale)
            panel.show()
            self.ensurePanelHead(panel)

        totalRows = (
            len(cogList) + self.cogsPerRow - 1
        ) // self.cogsPerRow

        maxRowIndex = max(
            0,
            totalRows - self.visibleRows
        )

        if self.rowIndex <= 0:
            self.pageUpButton['state'] = DGG.DISABLED
        else:
            self.pageUpButton['state'] = DGG.NORMAL

        if self.rowIndex >= maxRowIndex:
            self.pageDownButton['state'] = DGG.DISABLED
        else:
            self.pageDownButton['state'] = DGG.NORMAL

    def ensurePanelHead(self, panel):
        if panel is None:
            return

        if panel.head is not None:
            panel.head.show()
            return

        suitName = panel.suitName

        try:
            sourceHead = self.getCogHead(suitName)

            panel.head = sourceHead.copyTo(panel)
            panel.head.setPos(0, 0, 0)
            panel.head.setScale(1)
            panel.head.show()

        except Exception as error:
            print (
                'Could not create visible Cog head %s: %s'
                % (suitName, error)
            )

    def resetEnlargedPanel(self):
        if not self.bigPanel:
            self.nextPanel = None
            return

        panel = self.bigPanel

        self.bigPanel = None
        self.nextPanel = None

        panel.setScale(panel.scale)
        panel.reparentTo(self.panelNode)

        if panel.summonButton:
            panel.summonButton.hide()
            panel.summonButton[
                'state'
            ] = DGG.DISABLED

        panel.hide()

        if hasattr(self, 'rolloverFrame'):
            self.rolloverFrame.hide()

        if hasattr(self, 'hoverInfo'):
            self.hoverInfo.hide()


    def showDepartment(self, dept):
        self.cleanupBioSuitModel()

        self.currentDept = dept
        self.rowIndex = 0
        self.backButton.show()

        self.homePageNode.hide()
        self.bioPageNode.hide()
        self.departmentPageNode.show()

        self.departmentTitle['text'] = (
            SuitDNA.getDeptFullname(dept)
        )

        self.refreshDepartmentPanels()

    def getPanelForSuit(self, suitName):
        return self.panelBySuitName.get(suitName)

    def unload(self):
        self.ignoreAll()
        self.cleanupBioSuitModel()
        if hasattr(self, 'hoverInfo'):
            self.hoverInfo.destroy()

        if hasattr(self, 'rolloverFrame'):
            self.rolloverFrame.destroy()

        if hasattr(self, 'panels'):
            for panel in self.panels:
                panel.destroy()
            self.panels = []

        if hasattr(self, 'departmentButtons'):
            for button in self.departmentButtons:
                button.destroy()
            self.departmentButtons = []

        if hasattr(self, 'guiTop'):
            self.guiTop.destroy()

        self.cogHeadCache = {}
        self.cogHeads = []

        ShtikerPage.ShtikerPage.unload(self)

    def makeDepartmentButtons(self):
        self.departmentButtons = []
        self.departmentFrames = []

        icons = loader.loadModel(
            'phase_3/models/gui/cog_icons'
        )

        suitPageSplash = loader.loadModel(
            'phase_3.5/models/gui/suitpage_splash'
        )

        departments = [
            ('c', -0.52,  0.22),
            ('l',  0.00,  0.22),
            ('m',  0.52,  0.22),
            ('s', -0.52, -0.0),
            ('g',  0.00, -0.0),
            ('t',  0.52, -0.0),
            ('p',  0.00, -0.22),
        ]

        for dept, x, z in departments:
            departmentFrame = DirectFrame(
                parent=self.splashFrame,
                relief=None,
                frameColor=(
                    0.8,
                    0.8,
                    0.8,
                    0.7
                ),
                frameSize=(
                    -0.22,
                    0.22,
                    -0.17,
                    0.17
                ),
                pos=(x, 0, z)
            )

            geom = self.getDepartmentIcon(
                icons,
                dept
            )

            button = DirectButton(
                parent=departmentFrame,
                relief=None,
                geom=geom,
                geom_scale=0.16,
                pos=(0, 0, 0.02),
                command=self.showDepartment,
                extraArgs=[dept]
            )

            button.nameLabel = DirectLabel(
                parent=button,
                relief=None,
                text='',
                text_scale=0.22,
                text_fg=(0, 0, 0, 1),
                text_font=(
                    ToontownGlobals.getSuitFont()
                ),
                text_align=TextNode.ACenter,
                pos=(0, 0, 0)
            )

            self.departmentFrames.append(
                departmentFrame
            )
            self.departmentButtons.append(button)

        icons.removeNode()
        suitPageSplash.removeNode()

    def enter(self):
        self.updatePage()
        self.bigPanel = None
        self.nextPanel = None
        ShtikerPage.ShtikerPage.enter(self)
        return

    def exit(self):
        self.resetEnlargedPanel()
        self.showDepartmentHome()

        taskMgr.remove(
            'buildingListResponseTimeout-later'
        )
        taskMgr.remove(
            'suitListResponseTimeout-later'
        )
        taskMgr.remove('showCogRadarLater')
        taskMgr.remove('showBuildingRadarLater')

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
                    pos=(
                        xStart + typeIndex * xOffset,
                        0.0,
                        yStart - deptIndex * yOffset
                    ),
                    relief=None,
                    state=DGG.NORMAL,

                    # No card image.
                    text='???',
                    text_scale=0.0375,
                    text_fg=(0, 0, 0, 1),
                    text_pos=(0, 0.1875),
                    text_font=ToontownGlobals.getSuitFont(),
                    text_align=TextNode.ACenter,
                    text_wordwrap=6
                )

                panel.suitName = suitName

                panel['text'] = self.getCogDisplayName(
                    suitName,
                    abbreviate=True
                )
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
                    frameColor=(0, 0, 0, 0),
                    frameSize=(-0.10, 0.10, -0.18, 0.13),
                    pressEffect=0
                )
                panel.hoverButton['command'] = self.openCogBio
                panel.hoverButton['extraArgs'] = [panel]
                panel.hoverButton.setTransparency(
                    TransparencyAttrib.MAlpha
                )
                panel.hoverButton.panel = panel
                self.panelBySuitName[suitName] = panel

                self.addCogRadarLabel(panel)
                self.addQuotaLabel(panel)
                self.panels.append(panel)
                base.panels.append(panel)

                # panel.hoverButton.bind(DGG.ENTER, self.showCogHoverInfo, [panel])
                # panel.hoverButton.bind(DGG.EXIT, self.hideCogHoverInfo)

    def openCogBio(self, panel):
        self.currentBioSuit = panel.suitName

        self.homePageNode.hide()
        self.departmentPageNode.hide()
        self.bioPageNode.show()
        self.backButton.hide()

        self.updateCogBio(panel.suitName)

    def leaveCogBio(self):
        self.cleanupBioSuitModel()

        self.bioPageNode.hide()
        self.homePageNode.hide()
        self.backButton.show()
        self.departmentPageNode.show()

        self.refreshDepartmentPanels()

    def createBioSuitModel(self, suitName):
        self.cleanupBioSuitModel()

        dna = SuitDNA.SuitDNA()
        dna.newSuit(suitName)

        suit = Suit.Suit()
        suit.setDNA(dna)
        suit.hideNametag3d()
        suit.hideNametag2d()

        suit.reparentTo(self.bioFrame)
        suit.setPos(0.35, 0, -0.4)
        suit.setH(180)
        suit.setScale(0.055)

        try:
            if suitName == 'mplayer':
                suit.loop('neutral')
            elif suitName == 'psetter':
                suit.loop('neutral')
            else:
                suit.loop('neutral2')
        except:
            suit.loop('neutral')

        suit.setBin('gui-popup', 50)
        suit.setDepthTest(True)
        suit.setDepthWrite(True)

        self.suitModel = suit

    def getCogPosition(self, suitName):
        attrs = SuitBattleGlobals.SuitAttributes.get(
            suitName,
            {}
        )

        # Keep your existing managers unchanged.
        if suitName in MANAGER_SUITS:
            return 'Manager'

        if suitName in BOSS_COGS:
            return 'Boss'

        # Keep contractors unchanged too, if you still use them.
        if suitName in CONTRACTOR_SUITS:
            return 'Contractor'
        
        if suitName in SECRETARY_SUITS:
            return 'Secretary'

        hpType = attrs.get('hp', 'normal')

        if isinstance(hpType, basestring):
            hpType = hpType.lower()

            if hpType == 'field':
                return 'Field Specialist'

            if hpType == 'operations':
                return 'Operations Analyst'

        return 'Employee'
    
    def getCogPositionShort(self, suitName):
        attrs = SuitBattleGlobals.SuitAttributes.get(
            suitName,
            {}
        )

        # Keep your existing managers unchanged.
        if suitName in MANAGER_SUITS:
            return 'Manager'
        
        if suitName in BOSS_COGS:
            return 'Boss'
        
        if suitName in SECRETARY_SUITS:
            return 'Secretary'

        # Keep contractors unchanged too, if you still use them.
        if suitName in CONTRACTOR_SUITS:
            return 'Contractor'

        hpType = attrs.get('hp', 'normal')

        if isinstance(hpType, basestring):
            hpType = hpType.lower()

            if hpType == 'field':
                return 'Specialist'

            if hpType == 'operations':
                return 'Specialist'

        return 'Employee'

    def updateCogBio(self, suitName):
        attrs = SuitBattleGlobals.SuitAttributes.get(suitName, {})
        attacks = attrs.get('attacks', ())

        minimumLevel = SuitBattleGlobals.getSuitMinLevel(
            suitName
        )

        maximumLevel = SuitBattleGlobals.getSuitMaxLevel(
            suitName
        )

        minimumRelativeLevel = (
            SuitBattleGlobals.getRelativeFromActualLevel(
                suitName,
                minimumLevel
            )
        )

        maximumRelativeLevel = (
            SuitBattleGlobals.getRelativeFromActualLevel(
                suitName,
                maximumLevel
            )
        )

        if minimumLevel == maximumLevel:
            self.bioCogLevelLabel['text'] = (
                'Level: %s' % minimumLevel
            )
        else:
            self.bioCogLevelLabel['text'] = (
                'Level Range: %s-%s'
                % (minimumLevel, maximumLevel)
            )

        if suitName in MANAGER_SUITS or suitName in CONTRACTOR_SUITS or suitName in SECRETARY_SUITS:
            self.bioCogLevelLabel['text'] += '.mgr'

        if suitName in BOSS_COGS:
            self.bioCogLevelLabel['text'] = 'Level: [CLASSIFIED]'

        hasNoNormalAttacks = False
        minimumDamage = None
        maximumDamage = None
        attackLines = []
        seenAttackNames = set()

        for attack in attacks:
            attackName = attack.name

            # Do not display the same attack more than once.
            if attackName in seenAttackNames:
                continue

            seenAttackNames.add(attackName)

            if attackName == 'HighRollerNoAttack':
                hasNoNormalAttacks = True
                break

            attackMinimumDamage = (
                SuitBattleGlobals._getOverlevelValue(
                    attack.hp,
                    minimumRelativeLevel,
                    addPerLevel=1
                )
            )

            attackMaximumDamage = (
                SuitBattleGlobals._getOverlevelValue(
                    attack.hp,
                    maximumRelativeLevel,
                    addPerLevel=1
                )
            )

            if minimumDamage is None:
                minimumDamage = attackMinimumDamage
            else:
                minimumDamage = min(
                    minimumDamage,
                    attackMinimumDamage
                )

            if maximumDamage is None:
                maximumDamage = attackMaximumDamage
            else:
                maximumDamage = max(
                    maximumDamage,
                    attackMaximumDamage
                )

            displayName = TTLocalizer.SuitAttackNames.get(
                attackName,
                attackName
            ).rstrip('!')

            if attackMinimumDamage == attackMaximumDamage:
                attackLines.append(
                    '%s: %s' % (
                        displayName,
                        attackMinimumDamage
                    )
                )
            else:
                attackLines.append(
                    '%s: %s-%s' % (
                        displayName,
                        attackMinimumDamage,
                        attackMaximumDamage
                    )
                )


        if hasNoNormalAttacks:
            self.bioCogDamageLabel['text'] = (
                'Damage Range: [CLASSIFIED]'
            )
            if suitName in BOSS_COGS:
                self.bioCogAttacksLabel['text'] = (
                    ''
                )
            else:
                self.bioCogAttacksLabel['text'] = (
                    'There are no normal suit attacks for this Cog, outside of their abilities.'
                )

        elif minimumDamage is not None:
            if minimumDamage == maximumDamage:
                damageText = str(minimumDamage)
            else:
                damageText = '%s-%s' % (
                    minimumDamage,
                    maximumDamage
                )

            self.bioCogDamageLabel['text'] = (
                'Damage Range: %s' % damageText
            )

            self.bioCogAttacksLabel['text'] = (
                'Attacks:\n%s'
                % '\n'.join(attackLines)
            )

        else:
            self.bioCogDamageLabel['text'] = (
                'Damage Range: [CLASSIFIED]'
            )

            if suitName in BOSS_COGS:
                self.bioCogAttacksLabel['text'] = (
                    ''
                )
            else:
                self.bioCogAttacksLabel['text'] = (
                    'There are no normal suit attacks for this Cog, outside of their abilities.'
                )

        self.bioCogStatusLabel['text'] = ('Position: %s') % self.getCogPosition(suitName)

        self.bioCogNameLabel['text'] = self.getCogDisplayName(
                suitName,
                abbreviate=False
            )

        import random

        if suitName in TTLocalizer.SuitFaceoffTaunts:
            taunts = TTLocalizer.SuitFaceoffTaunts[suitName]
        else:
            taunts = TTLocalizer.SuitFaceoffDefaultTaunts

        quote = random.choice(taunts)

        self.bioCogQuoteLabel['text'] = '"%s"' % quote

        self.createBioSuitModel(suitName)

    def cleanupBioSuitModel(self):
        if not getattr(self, 'suitModel', None):
            return

        try:
            self.suitModel.cleanup()
        except:
            pass

        try:
            self.suitModel.removeNode()
        except:
            pass

        self.suitModel = None

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
                return ': %s-%s Damage' % (hp[0], hp[-1])
            elif len(hp) == 1:
                return ': %s Damage' % hp[0]

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
            ).rstrip('!')

            damageText = self.getAttackDamageText(attack)

            line = '%s%s' % (displayName, damageText)

            if line not in attackNames:
                attackNames.append(line)

        text += '\n'.join(attackNames)

        return text

    def showInfo(self, panel, text, extra):
        self.rolloverFrame.reparentTo(panel)
        self.rolloverFrame.hide()
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

        status = self.getCogPositionShort(suitName)

        quotaLabel = DirectLabel(
            parent=panel,
            pos=(0.0, 0.0, -0.16),
            relief=None,
            state=DGG.DISABLED,
            text=status,
            text_scale=0.035,
            text_fg=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont()
        )

        quotaLabel.setBin('gui-popup', 50)
        panel.quotaLabel = quotaLabel
        return
    
    def getCombinedHeadParts(self, suit):
        allParts = []
        seenNodes = set()

        partGroups = (
            suit.getHeadParts(),
            suit.getAnimatedHeadParts()
        )

        for partGroup in partGroups:
            for part in partGroup:
                if not part or part.isEmpty():
                    continue

                node = part.node()

                if node in seenNodes:
                    continue

                seenNodes.add(node)
                allParts.append(part)

        return allParts
    
    def createSuitHead(
        self,
        suitName,
        panel,
        dimension=0.25,
        setH=180):

        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit(suitName)

        suit = Suit.Suit()
        suit.setDNA(suitDNA)

        head = panel.attachNewNode(
            'head-%s' % suitName
        )
        head.setBin('gui-popup', 50)

        animatedParts = list(
            suit.getAnimatedHeadParts()
        )

        animatedNodes = set()

        for part in animatedParts:
            if part and not part.isEmpty():
                animatedNodes.add(part.node())

        allHeadParts = self.getCombinedHeadParts(suit)

        for part in allHeadParts:
            isAnimated = part.node() in animatedNodes

            if (
                isAnimated
                and suitName in
                    ToontownGlobals.animSuitHeadsPosedNeutral
            ):
                try:
                    if 'neutral' in part.getAnimNames():
                        part.pose('neutral', 1)
                except:
                    pass

            part.setTwoSided(True)
            part.setDepthTest(True)
            part.setDepthWrite(True)
            part.reparentTo(head)

        self.fitGeometry(
            head,
            fFlip=1,
            dimension=dimension,
            setH=setH
        )

        suit.delete()

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

        for suitName in SuitDNA.suitHeadTypes:
            headNode = NodePath(
                'headNode-%s' % suitName
            )

            try:
                self.createSuitHead(
                    suitName,
                    headNode,
                    dimension=0.22
                )

                self.cogHeads.append(headNode)

            except Exception as error:
                print (
                    'Could not load cog head %s: %s'
                    % (suitName, error)
                )

                headNode.removeNode()
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

    def setPanelStatus(self, panel, status):
        if panel is None:
            print 'SuitPage.setPanelStatus: panel is None'
            return

        suitName = getattr(panel, 'suitName', None)

        if not suitName:
            print 'SuitPage.setPanelStatus: panel has no suitName'
            return

        attrs = SuitBattleGlobals.SuitAttributes.get(suitName)

        if attrs is None:
            print 'SuitPage.setPanelStatus: missing attributes for', suitName
            panel['text'] = '???'
            return

        panel['text'] = self.getCogDisplayName(
            suitName,
            abbreviate=True
        )

        if panel.quotaLabel:
            panel.quotaLabel.show()
        else:
            self.addQuotaLabel(panel)
    
    def updateAllCogs(self, status):
        for index in xrange(0, len(base.localAvatar.cogs)):
            base.localAvatar.cogs[index] = status
        self.updatePage()

    def updatePage(self):
        avatarCogs = getattr(base.localAvatar, 'cogs', [])
        suitHeadTypes = SuitDNA.suitHeadTypes

        for deptIndex, deptName in enumerate(DEPT_ORDER):
            cogList = CogIndexDepartments.get(deptName, [])

            for typeIndex, suitName in enumerate(cogList):
                try:
                    index = suitHeadTypes.index(suitName)
                except ValueError:
                    print 'SuitPage: suit not in suitHeadTypes:', suitName
                    continue

                if index < 0 or index >= len(avatarCogs):
                    print (
                        'SuitPage: avatar cog index out of range: '
                        'suit=%s index=%s cogsLength=%s'
                        % (suitName, index, len(avatarCogs))
                    )
                    continue

                self.updateCogStatus(
                    deptIndex,
                    typeIndex,
                    avatarCogs[index]
                )

    def updateCogStatus(self, dept, type, status):
        if dept < 0 or dept >= len(DEPT_ORDER):
            print 'ucs: bad cog dept:', dept
            return

        deptName = DEPT_ORDER[dept]
        cogList = CogIndexDepartments.get(deptName, [])

        if type < 0 or type >= len(cogList):
            print (
                'ucs: bad cog type: %s for department %s, size %s'
                % (type, deptName, len(cogList))
            )
            return

        if status < COG_UNSEEN or status > COG_COMPLETE2:
            print 'ucs: bad status:', status
            return

        suitName = cogList[type]
        panel = self.panelBySuitName.get(suitName)

        if panel is None:
            print (
                'SuitPage: no panel for suit %s in department %s'
                % (suitName, deptName)
            )
            return

        self.resetPanel(dept, type)
        self.setPanelStatus(panel, status)

    def updateCogRadarButtons(self, radars):
       pass

    def updateCogRadar(self, deptNum, panels, timeout = 0):
        taskMgr.remove('suitListResponseTimeout-later')
        if not timeout and hasattr(base.cr, 'currSuitPlanner') and base.cr.currSuitPlanner != None:
            cogList = base.cr.currSuitPlanner.suitList
        else:
            cogList = []
        for panel in panels:
            panel.count = 0
        for cogIndex in cogList:
            if cogIndex < 0 or cogIndex >= len(SuitDNA.suitHeadTypes):
                print 'SuitPage radar: bad suitHeadTypes index:', cogIndex
                continue

            suitName = SuitDNA.suitHeadTypes[cogIndex]
            panel = self.panelBySuitName.get(suitName)

            if panel is None:
                print 'SuitPage radar: no panel for:', suitName
                continue

            panel.count += 1
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
        pass

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
