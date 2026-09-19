"""
A template file for creating modular sub-GUIS.
Includes all of the base code necessary to properly inherit from a GUI class.

This file should not be imported. Instead, you are welcome to copy/paste
the template file into other files as a base for designing any GUI elements.

This template now includes HeadlessStart, as seen below.
Running this file as a module will open the GUI in a headless setting
for streamlined testing and development.
"""
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.instances import HighRollerGlobals

if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    # base.initCR()  # defines base.cr
    # base.startHeadlessShow()

from toontown.gui.TTGui import kwargsToOptionDefs
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.gui.GUINode import GUINode
from toontown.gui import UiHelpers
from toontown.gui.DiceButton import DiceButton
from toontown.gui.EasyManagedItem import EasyManagedItem
from toontown.gui.EasyManagedButton import EasyManagedButton
from toontown.gui.EasyScrolledFrame import EasyScrolledFrame
from toontown.gui.ScaledFrame import ScaledFrame
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

from typing import Tuple, List, Dict, Optional, Callable


@DirectNotifyCategory()
class MrDiceChoice(ScaledFrame):
    """
    Mr. Dice Choice is an excellent worker.
    Sitting on the side of the screen, he lets you pick dice abilities!

    (Do not ask what happened to Ms Dice Choice)
    """

    scale_button = 0.25

    pad_button = 0.05

    @InjectorTarget
    def __init__(self, parent=base.a2dRightCenter, **kw):
        # GUI boilerplate.
        optiondefs = kwargsToOptionDefs(
            pos = (0, 0, 0),
            scale = 1.0,

            scaledTexture='phase_3/maps/gui/ttcc_gui_scaledFrame_hr.png',

            townBattle = None,
            inventory = None,
            # relief = None,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(MrDiceChoice)

        # GUI state
        self.state: bool = False
        self.hide()

        # Define objects of this GUI.
        self.pipDict: Dict[int, DiceButton] = {}
        self.diceButtons: List[DiceButton] = []
        self.activeSeqs: List[Sequence] = []

        # Let's let townbattle decide if we can be hidden or shown as well
        self.accept('close-dice-select', self.hideFromMessenger)
        self.accept('reopen-dice-select', self.showFromMessenger)

    def destroy(self):
        self.cleanup()
        self['townBattle'] = None
        super().destroy()

    def cleanup(self):
        for seq in self.activeSeqs:
            seq.pause()
        self.activeSeqs = []
        for button in self.diceButtons:
            button.destroy()
        self.pipDict = {}
        self.diceButtons = []

    """
    State Change
    """

    def hideFromMessenger(self):
        if self.state is True:
            super().hide()

    def showFromMessenger(self):
        if self.state is True:
            super().show()

    def enableChoice(self, pips: List[int], ownedPips: int = 0):
        """
        Enables picking dice buttons.
        """
        if self.state is True:
            self.disableChoice(callback=self.enableChoice, extraArgs=[pips, ownedPips])
            return
        self.state = True

        # Cleanup, just to be sure.
        self.cleanup()

        # Create dice buttons.
        for pip in pips:
            pip += 1
            dice = DiceButton(
                parent=self,
                scale=self.scale_button,
                easyHeight=-1 - self.pad_button,
                pip=pip,
                command=self.onClick, extraArgs=[pip],
            )
            dice.bind(DGG.ENTER, lambda p, *_: self.onEnter(p), extraArgs=[pip])
            dice.bind(DGG.EXIT, lambda p, *_: self.onExit(p), extraArgs=[pip])
            if ownedPips < HighRollerGlobals.getPipCost(base.localAvatar, AttackEnum.TOON_DICE, pip - 1):
                dice.disable()
            self.clipWithinFrame(dice)

            self.pipDict[pip] = dice
            self.diceButtons.append(dice)

        # Place dice buttons.
        UiHelpers.placeElementsInVerticalLine(self.diceButtons, (0, 0, 0), alignCenter=True, scale=self.scale_button)

        # Do open sequence.
        width = self.getMisterWidth()
        height = self.getMisterHeight()
        xpos = -self.getMisterWidth() * 0.8

        self['frameSize'] = (-width / 2, width / 2, 0, 0)

        def tweakin(t: float):
            self['frameSize'] = ((-width / 2) * 1, (width / 2) * 1, t * -(height / 2), t * (height / 2))

        Sequence(
            Wait(0.35),
            Func(self.show),
            LerpPosInterval(self, duration=0.1,
                            pos=(xpos, 0, 0), startPos=(-xpos, 0, 0),
                            blendType='easeOut'),
            LerpFunctionInterval(tweakin, duration=0.1, toData=1.05, blendType='easeInOut'),
            LerpFunctionInterval(tweakin, duration=0.05, toData=1.00, fromData=1.05, blendType='easeInOut'),
        ).start()

    def disableChoice(self, callback: Optional[Callable] = None, extraArgs: Optional[list] = None):
        """
        Disables picking dice buttons.
        """
        if self.state is False:
            return
        self.state = False

        # Disable buttons.
        for button in self.diceButtons:
            button['command'] = None
            button['state'] = DGG.DISABLED
            button.unbind(DGG.ENTER)
            button.unbind(DGG.EXIT)

        # Do close sequence.
        def performCallback(cb, ea):
            if not cb:
                return
            if not ea:
                ea = []
            cb(*ea)

        xpos = -self.getMisterWidth() * 0.8
        Sequence(
            Wait(0.01),
            LerpPosInterval(self, duration=0.1,
                            pos=(xpos * 1.2, 0, 0), startPos=(xpos, 0, 0),
                            blendType='easeOut'),
            LerpPosInterval(self, duration=0.2,
                            pos=(-xpos, 0, 0), startPos=(xpos * 1.2, 0, 0),
                            blendType='easeIn'),
            Func(self.hide),
            Func(performCallback, callback, extraArgs),
        ).start()

    """
    Cute Height Getters
    "WHY IS EVERYTHING YOU SAY CUTE" ~Huck 2023 and 2024 and 2025 and 2026
    """

    def getMisterHeight(self) -> float:
        return 0.8

    def getMisterWidth(self) -> float:
        return 0.27

    """
    Button Callbacks
    """

    def onEnter(self, pip):
        inventory = self['inventory']
        if inventory:
            inventory.showDetail(AttackEnum.TOON_DICE, pip - 1)

    def onExit(self, pip):
        inventory = self['inventory']
        if inventory:
            inventory.hideDetail()

    def onClick(self, pip):
        messenger.send('dice-selection', [pip - 1])

    def disablePip(self, pip: int, remainingPips: int):
        diceButton = self.pipDict.get(pip)
        if diceButton:
            diceButton.disable()
            x, y, z = diceButton.getPos()
            seq = Sequence(
                LerpPosInterval(diceButton, duration=0.25,
                                pos=(x + 1.0, 0, z), startPos=(x, 0, z),
                                blendType='easeIn')
            )
            seq.start()
            self.activeSeqs.append(seq)
        for pip, diceButton in self.pipDict.items():
            if HighRollerGlobals.getPipCost(base.localAvatar, AttackEnum.TOON_DICE, pip - 1) > remainingPips:
                diceButton.disable()


if __name__ == "__main__":
    gui = MrDiceChoice()
    gui.enableChoice([1, 2, 3])

    def a():
        gui.enableChoice([1, 2, 3])

    def s():
        gui.disableChoice()

    gui.accept('a', a)
    gui.accept('s', s)

    GUITemplateSliders(
        gui,
        'pos', 'scale', 'frameSize',
    )
    base.run()
