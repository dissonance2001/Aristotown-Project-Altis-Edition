"""
The module containing the GUI element for QuestPosters.
"""
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame

from toontown.club import ClubTaskPricing
from toontown.gui.TTGui import kwargsToOptionDefs
from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.gui.Quest3Poster import QuestPoster
from toontown.utils import text
from toontown.utils.InjectorTarget import InjectorTarget


class ClubQuestPoster(QuestPoster):
    """
    The new QuestPoster GUI for the Quest3 system.
    Quack qu ack Quack qkc  quak  qua c k Quack
    """
    @InjectorTarget
    def __init__(self, parent, questReference: QuestReference = None, **kw):

        ################# THE FIRST PART OF THE __INIT__ METHOD #################

        optiondefs = kwargsToOptionDefs()
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, questReference, **kw)
        self.initialiseoptions(ClubQuestPoster)

        ################# THE SECOND PART OF THE __INIT__ METHOD #################

        self.text_reward = DirectFrame(
            parent=self, relief=None,
            pos=(0, 0, -0.33817), scale=0.06837,
            text='bread',
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        )
        m = loader.loadModel('phase_3.5/models/gui/clothingpage/clothing_page')
        self.button_rerollTasks = DirectButton(
            parent=self,
            relief=None,
            pos=(0.34857, 0.0, -0.23184),
            scale=0.12183,
            text=('', '', 'Reroll Tasks'),
            text_align=TextNode.ARight,
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0.75),
            text_shadow=(0, 0, 0, 1),
            text_pos=(-0.68154, 0.05203),
            text_scale=0.57859,
            image=(
                m.find('**/Refresh_N'),
                m.find('**/Refresh_P'),
                m.find('**/Refresh_H'),
            ),
            command=self.onReroll,
        )
        m.removeNode()

    def _getTaskImage(self):
        posterModel = loader.loadModel('phase_3.5/models/gui/quests/ttcc_quest_posters')
        questCard = posterModel.find('**/side_task_scroll')
        posterModel.removeNode()
        return questCard

    def bindToScroll(self, easyScrolledFrame):
        super().bindToScroll(easyScrolledFrame)
        easyScrolledFrame.bindToScroll(self.button_rerollTasks)

    def setQuestPostProperties(self, questReference: QuestReference):
        super().setQuestPostProperties(questReference)

        # Update stuff (I'm stuf)
        clubContainer = base.cr.clubMgr.getLocalClub()
        if not clubContainer:
            return
        rewardAmount = ClubTaskPricing.calculateTaskReward(questReference.getChainId())
        rerollPrice = ClubTaskPricing.calculateRerollCost(questReference.getChainId())
        self.text_reward.setText('Reward: \1white\1\5reward_clubCoin\5\2 %s Club Coins' % rewardAmount)
        self.button_rerollTasks.setText(
            ('', '', 'Reroll Task\n\1white\1\5reward_beanJarIcon\5\2 %s' % text.formatNumberWithCommas(rerollPrice))
        )

    def onReroll(self):
        pass
