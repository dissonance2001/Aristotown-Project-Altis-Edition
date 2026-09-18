if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    # base.initCR()  # defines base.cr
    # base.startHeadlessShow()

from toontown.gui import TTGui
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.gui.GUINode import GUINode
from toontown.gui.CornerAnchor import CornerAnchor
from toontown.gui import UiHelpers
from toontown.gui.EasyManagedItem import EasyManagedItem
from toontown.gui.EasyManagedButton import EasyManagedButton
from toontown.gui.EasyScrolledFrame import EasyScrolledFrame
from toontown.gui.Bounds import Bounds
from toontown.gui.GUIPositionGlobals import ScreenCorner
from toontown.gui.ScaledFrame import ScaledFrame
from toontown.gui.TilingScaledFrame import TilingScaledFrame
from toontown.gui.UiLerper import UILerper
from toontown.toon.gui import GuiBinGlobals
from toontown.toonbase import ToontownGlobals
from toontown.toon.Toon import Toon

from toontown.utils.InjectorTarget import InjectorTarget
from toontown.utils import ColorHelper, Nodes
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.showbase import PythonUtil
from panda3d.core import *


class BackpackToonWidget(DirectFrame, Bounds):
    """
    A widget for the left side of the backpack page that shows a toon
    """

    @InjectorTarget
    def __init__(self, parent, **kw):
        # GUI boilerplate.
        optiondefs = TTGui.kwargsToOptionDefs(
            pos=(0, 0, 0),
            scale=1.0,
            relief=None,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.postInitialized = False
        self.postInitialiseFuncList.append(lambda: setattr(self, 'postInitialized', True))
        self.initialiseoptions(BackpackToonWidget)

        # Set state here.
        self.toonNode = None
        self.toonModel = None
        self.slider = None
        self.codeEntry = None
        self.codeButton = None
        self.codeResult = None
        self.codeInstructions = None
        self.codeButtonGui = None

        # Call these two.
        self.__create()
        self.place()

    def __create(self):
        self.toonNode = GUINode(parent=self, pos=(0, 0, -0.085), scale=0.5)

        self.toonModel = Toon()
        self.toonModel.flattenStrong()
        self.toonModel.setDNAString(base.localAvatar.style.makeNetString())
        self.__equippedItemsEvent = f'EquippedInventorySet-{base.localAvatar.doId}'
        self.accept(self.__equippedItemsEvent, self.__refreshEquippedItems)
        self.__refreshEquippedItems()
        self.toonModel.getGeomNode().setDepthWrite(1)
        self.toonModel.getGeomNode().setDepthTest(1)
        self.toonModel.getGeomNode().setTwoSided(True)
        self.toonModel.loop('neutral')
        self.toonModel.reparentTo(self.toonNode)

        p1 = Point3()
        p2 = Point3()
        self.toonModel.calcTightBounds(p1, p2)
        d = p2 - p1
        biggest = max(d[0], d[2])
        dimension = 1.4
        s = dimension / biggest
        # find midpoint
        mid = (p1 + d / 2.0) * s

        self.toonModel.setPosHprScale(
            -mid[0], -mid[1] + 1, -mid[2],
            0, 0, 0,
            s, s, s
        )

        sliderGui = loader.loadModel("phase_3/models/gui/ttcc_gui_generic")
        thumb = sliderGui.find("**/gui_slider_thumb")
        self.slider = DirectSlider(
            parent=self,
            pos=(0, 0, -0.5),
            value=180,
            range=(0, 360),
            pageSize=1,
            scale=(.3, 1, .3),
            frameColor=(181. / 255., 88. / 255., 1. / 255., 1),
            orientation=DGG.HORIZONTAL,
            thumb_relief=None,
            thumb_geom=thumb,
            thumb_geom_scale=(.2, .2, .2),
            command=self.toonRotate
        )
        sliderGui.removeNode()

    def toonRotate(self):
        self.toonModel.setH(int(self.slider['value']))

    def __refreshEquippedItems(self, *args):
        if self.toonModel and base.localAvatar:
            self.toonModel.setToonEquippedItems(base.localAvatar.getEquippedItems())

    def place(self):
        if not self.postInitialized:
            return
        # self.corner_topRight.place()
        # self.text_label.setPos(self['labelPos'])
        pass

    def destroy(self):
        if hasattr(self, '_BackpackToonWidget__equippedItemsEvent'):
            self.ignore(self.__equippedItemsEvent)
        if self.toonModel:
            self.toonModel.delete()
            self.toonModel = None
        if self.codeEntry:
            self.codeEntry.destroy()
            self.codeEntry = None
        if self.codeButton:
            self.codeButton.destroy()
            self.codeButton = None
        if self.codeResult:
            self.codeResult.destroy()
            self.codeResult = None
        if self.codeInstructions:
            self.codeInstructions.destroy()
            self.codeInstructions = None
        if self.codeButtonGui:
            self.codeButtonGui.removeNode()
            self.codeButtonGui = None
        super().destroy()

    def __setCodeResult(self, text, color=(0.2, 0.1, 0, 1)):
        if self.codeResult:
            self.codeResult['text'] = text
            self.codeResult['text_fg'] = color

    def __handleCodeResult(self, result, awardMgrResult):
        resultText = {
            ToontownGlobals.CODE_SUCCESS: ('Code successfully redeemed!', (0.1, 0.55, 0.1, 1)),
            ToontownGlobals.CODE_INVALID: ('That code is invalid.', (0.75, 0.1, 0.1, 1)),
            ToontownGlobals.CODE_USED: ('You have already redeemed that code.', (0.75, 0.35, 0.05, 1)),
            ToontownGlobals.CODE_EXPIRED: ('That code has expired.', (0.75, 0.1, 0.1, 1)),
            ToontownGlobals.CODE_INELIGIBLE: ('You are not eligible for that code.', (0.75, 0.1, 0.1, 1)),
            ToontownGlobals.CODE_TOO_MANY_USES: ('That code has reached its usage limit.', (0.75, 0.1, 0.1, 1)),
            ToontownGlobals.CODE_NOT_ENOUGH_ROOM: ('There is not enough room in your inventory.', (0.75, 0.1, 0.1, 1)),
            ToontownGlobals.CODE_UNKNOWN_ERROR: ('The code could not be redeemed.', (0.75, 0.1, 0.1, 1)),
        }
        text, color = resultText.get(
            result,
            ('The code could not be redeemed.', (0.75, 0.1, 0.1, 1)),
        )
        self.__setCodeResult(text, color)
        if self.codeButton:
            self.codeButton['state'] = DGG.NORMAL

    def __redeemCode(self, enteredText=None):
        if not self.codeEntry:
            return

        code = self.codeEntry.get().strip()
        if not code:
            self.__setCodeResult('Enter a code first.', (0.75, 0.1, 0.1, 1))
            return

        codeManager = getattr(base.cr, 'codeRedemptionMgr', None)
        if not codeManager:
            self.__setCodeResult('The code redemption service is not ready.', (0.75, 0.1, 0.1, 1))
            return

        self.codeButton['state'] = DGG.DISABLED
        self.__setCodeResult('Redeeming code...')
        codeManager.redeemCode(code, self.__handleCodeResult)

    def __createCodesGui(self):
        if self.codeEntry:
            return

        # Centre the complete redemption interface on the right-hand page.
        codePageX = 0.92

        self.codeInstructions = DirectLabel(
            parent=self,
            relief=None,
            pos=(codePageX, 0, 0.25),
            text='Enter a promotional code\nto receive special items!',
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.052,
            text_fg=(0.12, 0.07, 0.02, 1),
            text_align=TextNode.ACenter,
        )

        self.codeEntry = DirectEntry(
            parent=self,
            relief=DGG.SUNKEN,
            frameColor=(0.96, 0.96, 0.96, 1),
            borderWidth=(0.035, 0.035),
            pos=(codePageX, 0, 0.08),
            scale=0.075,
            width=7.6,
            numLines=1,
            text_align=TextNode.ACenter,
            text_scale=0.72,
            text_fg=(0.15, 0.08, 0, 1),
            cursorKeys=1,
            focus=0,
            suppressMouse=1,
            autoCapitalize=0,
            command=self.__redeemCode,
        )

        # Use the standard glossy yellow Toontown button graphics.
        self.codeButtonGui = loader.loadModel('phase_3/models/gui/quit_button')
        self.codeButton = DirectButton(
            parent=self,
            relief=None,
            image=(
                self.codeButtonGui.find('**/QuitBtn_UP'),
                self.codeButtonGui.find('**/QuitBtn_DN'),
                self.codeButtonGui.find('**/QuitBtn_RLVR'),
            ),
            image_scale=(1.05, 1.0, 1.08),
            pos=(codePageX, 0, -0.08),
            scale=0.72,
            text='Redeem',
            text_font=ToontownGlobals.getSignFont(),
            text0_fg=(1, 1, 1, 1),
            text0_shadow=(0, 0, 0, 1),
            text1_fg=(1, 1, 1, 1),
            text2_fg=(1, 1, 1, 1),
            text_scale=0.085,
            text_pos=(0, -0.024),
            command=self.__redeemCode,
        )

        self.codeResult = DirectLabel(
            parent=self,
            relief=None,
            pos=(codePageX, 0, -0.22),
            text='Enter a code to get started!',
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.047,
            text_fg=(0.15, 0.35, 0.85, 1),
            text_shadow=(1, 1, 1, 0.7),
            text_align=TextNode.ACenter,
            textMayChange=1,
        )

    def enterCodesMode(self):
        self.slider.hide()
        self.toonModel.setH(180)
        self.toonNode.setX(-0.25)
        self.toonModel.pose('left', 47)
        self.toonModel.showSmileMuzzle()
        self.__createCodesGui()
        self.codeInstructions.show()
        self.codeEntry.show()
        self.codeButton.show()
        self.codeResult.show()

    def exitCodesMode(self):
        if self.codeInstructions:
            self.codeInstructions.hide()
        if self.codeEntry:
            self.codeEntry.hide()
        if self.codeButton:
            self.codeButton.hide()
        if self.codeResult:
            self.codeResult.hide()
        self.slider.show()
        self.toonModel.setH(180)
        self.toonNode.setX(0)
        self.slider['value'] = 180
        self.toonModel.loop('neutral')
        self.toonModel.hideSmileMuzzle()


if __name__ == "__main__":
    gui = BackpackToonWidget(
        parent=aspect2d,
        # any kwargs go here
    )
    GUITemplateSliders(
        gui,
        'pos', 'scale'
    )
    base.run()
