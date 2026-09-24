from toontown.inventory.enums.ItemEnums import MaterialItemType
from toontown.toon.ToonStatsGlobals import ToonStats

if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()

from toontown.gui.OnscreenBooster import OnscreenBooster
from toontown.gui.EasyScrolledFrame import EasyScrolledFrame
from toontown.gui.TTGui import kwargsToOptionDefs, ExtendedOnscreenText
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.gui.GUINode import GUINode
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from toontown.toonbase import ToontownGlobals
from direct.gui.DirectGui import *


@DirectNotifyCategory()
class DailyTaskChalkboard(DirectFrame):
    """
    The chalkboard showing daily task values.
    """

    @InjectorTarget
    def __init__(self, parent, **kw):
        # GUI boilerplate.
        model = loader.loadModel('phase_3.5/models/gui/daily_tasks_new')
        optiondefs = kwargsToOptionDefs(
            relief = None,
            image=model.find('**/DailyTask_main'),
            image_scale=(667 / 1020, 1, 1),
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(self.__class__)

        # Define objects of this GUI.
        self.text_taskLabel = OnscreenText(
            parent=self,
            text='0',
            pos=(0.20294, 0.2512),
            scale=0.038,
            fg=(1, 1, 1, 1),
        )
        self.text_taskCount = OnscreenText(
            parent=self,
            text='Daily Tasks Completed:',
            pos=(-0.07055, 0.25279),
            scale=0.038,
            fg=(1, 1, 1, 1),
        )
        self.text_noBoosters = OnscreenText(
            parent=self,
            text='You have no active boosters.',
            scale=(0.035, 0.038),
            fg=(1, 1, 1, 1),
        )
        self.text_boosterHelp = OnscreenText(
            parent=self,
            text='Hover over a Booster to learn more about its effect and duration!',
            scale=0.028,
            pos=(0.0, -0.17167),
            wordwrap=15.90829,
            fg=(1, 1, 1, 1),
        )
        self.text_boosterLabel = ExtendedOnscreenText(
            parent=self,
            text='All-Star Booster',
            pos=(0.0, -0.14786),
            scale=(0.03135, 0.03135),
            fg=(1, 1, 1, 1),
        )
        self.text_boosterLabel.hide()
        self.text_boosterDesc = ExtendedOnscreenText(
            parent=self,
            text='',
            pos=(0.0, -0.20118),
            scale=(0.02011, 0.02011),
            wordwrap=26.17285,
            fg=(1, 1, 1, 1),
        )
        self.text_boosterDesc.hide()
        self.text_tokenTitle = DirectLabel(
            parent=self, relief=None,
            text='Total Gumballs',
            text_pos=(-0.15285, -0.28851),
            text_scale=(0.036, 0.036),
            text_fg=(1, 1, 1, 1),
        )
        self.text_rerollTitle = DirectLabel(
            parent=self, relief=None,
            text='Rerolls Left',
            text_pos=(0.15215, -0.28851),
            text_scale=(0.036, 0.036),
            text_fg=(1, 1, 1, 1),
        )
        self.text_tokenCount = DirectLabel(
            parent=self, relief=None,
            text='0',
            text_pos=(-0.15355, -0.40021),
            text_scale=0.07,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSignFont(),
        )
        self.text_rerollCount = DirectLabel(
            parent=self, relief=None,
            text='2/2',
            text_pos=(0.15662, -0.40021),
            text_scale=0.07,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSignFont(),
        )
        self.boosterScroll = EasyScrolledFrame(
            parent=self, relief=None,
            pos=(0, 0, 0), scale=1.0,

            frameSize=(-0.23045, 0.2572, -0.10611, 0.14609),
            itemStartPosition=(0.00559, 0.0, 0.08274),
            horizontalCentering=True,
            thumbHeight=0.025,
            scrollBarWidth=0.03647,
            hideScroll=True,

            verticalScroll_relief=None,

            verticalScroll_thumb_relief=None,
            verticalScroll_thumb_image=model.find('**/DailyTask_scrollbar '),
            verticalScroll_thumb_image_pos=(-0.00147, 0.0, 0.00705),
            verticalScroll_thumb_image_scale=(0.04088, 1.0, 0.04088),
        )
        self.boosterGuis = []
        model.removeNode()

        # Set booster update.
        self.accept('boostsUpdated', self.updateBoosters)
        self.accept('statsChanged', self.updateCompletionText)
        self.accept('gumballs-updated', self.updateGumballs)
        self.accept('dailyQuestRerollsChanged', self.updateRerolls)
        self.updateBoosters()
        self.updateCompletionText()
        self.updateRerolls()

    def destroy(self) -> None:
        super().destroy()
        self.ignoreAll()

    def updateBoosters(self):
        if not base.localAvatar:
            return
        self.populateBoosters(base.localAvatar.getAllBoosters())

    def populateBoosters(self, boosters: list = None):
        """Populates the boosters in the vertical scroll."""
        # Clear out items.
        self.boosterScroll.removeAllItems()
        self.boosterGuis = []

        # Add boosters in.
        for booster in boosters:
            booster: BoosterBase
            boosterGui = OnscreenBooster(
                parent=None, scale=0.12,
                textCallback=self.updateDescriptionText,
                boosterInstance=booster,
                hasRollover=True,
                easyHeight=-0.125,
                easyWidth=0.125,
                easyXMax=3,
                easyScrolledFrame=self.boosterScroll,
            )
            self.boosterGuis.append(boosterGui)

        # Update positions, finally.
        self.boosterScroll.updateItemPositions()

        # Show the help text if necessary.
        self.text_noBoosters.show()
        if self.boosterGuis:
            self.text_noBoosters.hide()

    def updateDescriptionText(self, onscreenBooster: OnscreenBooster, boosterName: str, boosterDesc: str, boosterEndStr: str):
        if boosterName is None:
            # Revert values to default.
            self.text_boosterHelp.show()
            self.text_boosterLabel.hide()
            self.text_boosterDesc.hide()
        else:
            # Make em visible.
            self.text_boosterHelp.hide()
            self.text_boosterLabel.show()
            self.text_boosterDesc.show()

            # Set the text.
            self.text_boosterLabel.setText(boosterName)
            self.text_boosterDesc.setTextWithVerticalAlignment(
                boosterDesc.replace('\n', ', ') + f'\n{boosterEndStr}'
            )

    def updateCompletionText(self):
        if not base.localAvatar:
            return
        tasksCompleted = base.localAvatar.getStat(ToonStats.DAILY_TASKS)
        self.text_taskLabel.setText(str(tasksCompleted))

    def updateGumballs(self):
        if not base.localAvatar:
            return
        gumballs = base.localAvatar.getMoney(currencyType=MaterialItemType.Gumballs)
        self.text_tokenCount.setText(str(gumballs))
        self.text_tokenCount['text_fg'] = (1.0, 1.0, 1.0, 1.0)
        if gumballs == ToontownGlobals.MaxGumballs:
            self.text_tokenCount['text_fg'] = (1, 0.25, 0.25, 1)

    def updateRerolls(self):
        if not base.localAvatar:
            return
        rerolls = base.localAvatar.getDailyQuestRerolls()
        self.text_rerollCount.setText(str(rerolls) + '/2')


if __name__ == "__main__":
    gui = DailyTaskChalkboard(
        parent=aspect2d,
        scale=2.0,
        # any kwargs go here
    )
    from toontown.booster.BoosterBase import BoosterBase
    import time
    # gui.populateBoosters(
    #     boosters=[
    #         BoosterBase.fromStruct([reward, time.time() + 120]) for reward in __BoosterDict if reward
    #     ] * 2
    # )
    GUITemplateSliders(
        guiAffected=gui.text_noBoosters,
        guiKeys=('text_pos', 'text_scale',),
    )
    base.run()
