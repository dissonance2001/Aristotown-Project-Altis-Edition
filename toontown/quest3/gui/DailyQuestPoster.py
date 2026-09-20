"""
The module containing the GUI element for QuestPosters.
"""
import math

from toontown.ai import HolidayGlobals
from toontown.inventory.enums.ItemEnums import BoosterItemType
from toontown.quest3.daily.DailyConstants import DailyGumballReward

if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()

from toontown.gui import UiHelpers
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.gui.TTGui import kwargsToOptionDefs
from toontown.gui.GumballBank import GumballBank
from toontown.toonbase import ToontownGlobals
from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.gui.Quest3Poster import QuestPoster
from toontown.utils.InjectorTarget import InjectorTarget
from direct.gui.DirectGui import *


class DailyQuestPoster(QuestPoster):
    """
    The QuestPoster class for daily tasks.
    """

    @InjectorTarget
    def __init__(self, parent, questReference: QuestReference = None, **kw):
        # GUI boilerplate.
        assert not questReference, "This class breaks when initializing with a questReference. Please set it in post."
        self.initialized = False
        optiondefs = kwargsToOptionDefs(
            onscreen=False,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, questReference, **kw)
        self.initialiseoptions(DailyQuestPoster)
        self.initialized = True

        self.gumballReward = GumballBank(
            parent=self,
            pos=(0.35861, 0.0, -0.24103),
            scale=0.09465,
            prefix='+',
            money=base.localAvatar.applyBoosters(BoosterItemType.Gumballs_Global, DailyGumballReward, applyRound=True),
        )
        model = loader.loadModel('phase_3.5/models/gui/daily_tasks_new')
        self.rerollButton = DirectButton(
            parent=self, relief=None,
            pos=(0.36273, 0.0, 0.2328),
            scale=0.1652,
            image=UiHelpers.generateButtonImages(model, 'DailyTask_Die_', 'N', 'P', 'H'),
            image_scale=UiHelpers.calculateImageScale(81, 72),
            text='Reroll',
            text_pos=(0.01176, -0.15285),
            text_scale=0.42334,
            text_fg=(1, 1, 1, 1),
            text_font=ToontownGlobals.getSignFont(),
            command=self.attemptReroll,
        )
        self.completeButton = DirectButton(
            parent=self, relief=None,
            pos=(-0.00017, 0.0, -0.13909),
            scale=0.26455,
            image=UiHelpers.generateButtonImages(model, 'Button_Claim_', 'N', 'P', 'H'),
            image_scale=UiHelpers.calculateImageScale(270, 137),
            command=self.attemptCompletion,
        )
        self.booster = None
        model.removeNode()

        # Hide everything initially.
        self.rerollButton.hide()
        self.gumballReward.hide()
        self.completeButton.hide()

        self.accept('dailyQuestRerollsChanged', self.rerollsUpdated)
        # Also listen to this message so that the page can adjust the gumball reward label
        self.accept(HolidayGlobals.GumballHolidayStatusMessage, self.__gumballHolidayChanged)

    def setQuestReference(self, questReference: QuestReference = None, resetIndex: bool = True):
        super().setQuestReference(questReference=questReference, resetIndex=resetIndex)

        if not self.initialized:
            return
        if questReference is None:
            self.completeButton.hide()
        if questReference is None or self['onscreen']:
            self.rerollButton.hide()
            self.gumballReward.hide()
        else:
            self.rerollsUpdated()
            self.gumballReward.show()

        # Booster time? ()
        # if questReference:
        #     if not self.booster:
        #         questChain = self.getQuestChain()
        #         rewards = questChain.getQuestRewards()
        #         for reward in rewards:
        #             if not isinstance(reward, BoosterReward):
        #                 continue
        #             self.booster = OnscreenBooster(
        #                 parent=self,
        #                 pos=(0.35861, 0.0, -0.24691),
        #                 scale=0.18871,
        #                 boosterType=reward.getBoosterType(), hasRollover=True,
        #             )
        #             break
        # else:
        #     if self.booster:
        #         self.booster.destroy()

        # who cares
        self.label_debugQuestId.hide()

    def setQuestPostProperties(self, questReference: QuestReference):
        super().setQuestPostProperties(questReference=questReference)

        # Override the name.
        self.label_headLine['text'] = 'Daily Task'

        # If complete, place the complete button.
        if self.isComplete():
            self.text_questInfo.hide()
            self.waitbar_questProgress.hide()
            # self.completeButton.show()
            self.rerollButton.hide()
        else:
            self.text_questInfo.show()
            self.completeButton.hide()

    def attemptReroll(self):
        base.localAvatar.requestDailyReroll(self.questReference)

    def attemptCompletion(self):
        base.localAvatar.requestDailyCompletion(self.questReference)

    def rerollsUpdated(self):
        if self.questReference is None or self['onscreen']:
            return
        if not self.isComplete() and self.canReroll():
            self.rerollButton.show()
        else:
            self.rerollButton.hide()

    def canReroll(self):
        if not base.localAvatar:
            return False
        return base.localAvatar.getDailyQuestRerolls() > 0

    def _getTaskImage(self):
        # Load models and stuff
        posterModel = loader.loadModel('phase_3.5/models/gui/quests/ttcc_quest_posters')
        questCard = posterModel.find('**/complete_task_scroll' if self.isComplete() else '**/daily_task_scroll')
        posterModel.removeNode()
        return questCard

    def __gumballHolidayChanged(self):
        if not self.questReference:
            # Do not do the stinky with quest posters that don't actually exist
            return

        self.gumballReward.setMoney(base.localAvatar.applyBoosters(BoosterItemType.Gumballs_Global, DailyGumballReward, applyRound=True))
        self.showRewardLabels()


if __name__ == "__main__":
    gui = DailyQuestPoster(
        parent=aspect2d,
        pos=(0, 0, 0),
        scale=1.0,
        # any kwargs go here
    )
    from toontown.quest3.base.QuestReference import QuestReference, QuestId
    from toontown.quest3.QuestEnums import *
    from toontown.quest3.questlines import *
    gui.setQuestReference(QuestReference(
        questId=(
            QuestId(
                QuestSource.DailyQuest,
                chainId=1111111,
                objectiveId=1,
            )
        ),
        progress=[2],
    ))
    GUITemplateSliders(
        guiAffected=gui.gumballReward,
        guiKeys=('pos', 'scale',),
    )
    # GUITemplateSliders(
    #     guiAffected=gui.gumballReward,
    #     guiKeys=('text_pos',),
    # )
    base.run()

