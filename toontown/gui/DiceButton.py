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
from toontown.gui.EasyManagedItem import EasyManagedItem
from toontown.gui.EasyManagedButton import EasyManagedButton
from toontown.gui.EasyScrolledFrame import EasyScrolledFrame
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *


@DirectNotifyCategory()
class DiceButton(EasyManagedButton):
    """
    A generic button... that is a dice!
    """

    @InjectorTarget
    def __init__(self, parent, **kw):
        # GUI boilerplate.
        optiondefs = kwargsToOptionDefs(
            pos=(0, 0, 0),
            scale=1.0,
            pip=[1, self.setPip],
            alwaysDefault=False,

            easyHeight=-1.2,
            easyWidth=1.2,

            frameSize=(-0.5, 0.5, -0.5, 0.5),
            image_scale=1.07,
            image_pos=(0.021, 0, -0.021),
            relief=None,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(DiceButton)

    @staticmethod
    def getModel():
        return loader.loadModel('phase_4/models/gui/cc_m_gui_gen_dice')

    def setPip(self):
        gui = self.getModel()
        pip = self['pip']
        if not (1 <= pip <= 7) or not isinstance(pip, int):
            raise AttributeError(f"Bad pip given: {pip} type {type(pip)}")
        dicePrefix = 'golddice' if pip == 7 else 'dice'
        pip = min(6, pip)
        self['image'] = (
            gui.find(f'**/cc_t_gui_gen_{dicePrefix}_{pip}_up'),
            gui.find(f'**/cc_t_gui_gen_{dicePrefix}_{pip}_{"down" if not self["alwaysDefault"] else "up"}'),
            gui.find(f'**/cc_t_gui_gen_{dicePrefix}_{pip}_{"rlvr" if not self["alwaysDefault"] else "up"}'),
        )
        gui.removeNode()

    def disable(self):
        self['image_color'] = (0.7, 0.7, 0.7, 1.0)

    @staticmethod
    def getDicePipIcon(pip: int):
        gui = DiceButton.getModel()
        dicePrefix = 'golddice' if pip == 7 else 'dice'
        pip = min(6, pip)
        node = gui.find(f'**/cc_t_gui_gen_{dicePrefix}_{pip}_up')
        gui.removeNode()
        return node


if __name__ == "__main__":

    center = DirectFrame(
        parent=aspect2d,
        relief=None,
        scale=0.5,
    )
    LerpHprInterval(
        center, duration=5.0,
        hpr=(0, 0, 0), startHpr=(360, 360, 360),
    ).loop()

    dist = 0.5
    front = DiceButton(
        parent=center,
        pos=(0, dist, 0),
    )
    left = DiceButton(
        parent=center,
        pos=(-dist, 0, 0),
        hpr=(-90, 0, 0),
        pip=3
    )
    right = DiceButton(
        parent=center,
        pos=(dist, 0, 0),
        hpr=(90, 0, 0),
        pip=4
    )
    back = DiceButton(
        parent=center,
        pos=(0, -dist, 0),
        hpr=(180, 0, 0),
        pip=6
    )
    top = DiceButton(
        parent=center,
        pos=(0, 0, dist),
        hpr=(0, 90, 0),
        pip=2
    )
    bot = DiceButton(
        parent=center,
        pos=(0, 0, -dist),
        hpr=(0, -90, 0),
        pip=5
    )

    die = []
    for i in range(1, 7):
        dice = DiceButton(
            parent=aspect2d,
            pip=i,
            scale=0.35,
        )
        die.append(dice)
    UiHelpers.fillGridWithElements(die, 3, 2, scale=0.35, centering=True)
    # GUITemplateSliders(
    #     gui,
    #     'pos', 'scale'
    # )
    base.run()
