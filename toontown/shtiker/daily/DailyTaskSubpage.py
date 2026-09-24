
if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()

from toontown.shtiker.daily.DailyTaskChalkboard import DailyTaskChalkboard
from toontown.quest3.gui.DailyQuestPoster import DailyQuestPoster
from toontown.quest3.QuestEnums import QuestSource
from toontown.gui.TTGui import kwargsToOptionDefs
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.gui.GUINode import GUINode
from toontown.gui import UiHelpers
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from direct.gui.DirectGui import *


@DirectNotifyCategory()
class DailyTaskSubpage(DirectFrame):
    """
    The subpage for Daily Tasks.
    """

    @InjectorTarget
    def __init__(self, parent, **kw):
        # GUI boilerplate.
        optiondefs = kwargsToOptionDefs(
            pos=(0, 0, 0),
            scale=1.0,
            relief = None,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(DailyTaskSubpage)

        # Define objects of this GUI.
        self.node_left = GUINode(parent=self, name='dtLeft', pos=(-0.42716, 0.0, 0.02133), scale=0.73987,)
        self.node_right = GUINode(parent=self, name='dtRight', pos=(0.43757, 0.0, 0.02081), scale=1.27313)

        # Make quest posters.
        self.questPosters = [DailyQuestPoster(parent=self.node_left) for i in range(3)]
        self.text_noTask = OnscreenText(
            parent=self.node_left,
            text='No tasks available.\nCheck back tomorrow!',
            pos=(0, 0, 0), scale=0.1,
        )

        # Make the chalkboard.
        self.chalkboard = DailyTaskChalkboard(
            parent=self.node_right,
        )

        # Listen for update calls.
        self.accept('questsChanged', self.updateQuests)
        self.updateQuests()

    def destroy(self):
        self.ignoreAll()
        super().destroy()

    def updateQuests(self):
        """Update quests to match localav."""
        if not base.localAvatar:
            return
        questRefs = base.localAvatar.getQuestReferencesOfSource(QuestSource.DailyQuest)
        activePosters = []
        for index, poster in enumerate(self.questPosters):
            if index < len(questRefs):
                # Set the ref accordingly.
                poster.setQuestReference(questRefs[index])
                activePosters.append(poster)
                poster.show()
            else:
                # Clear ref
                poster.setQuestReference()
                poster.hide()

        # Vertically-align these posters.
        if activePosters:
            UiHelpers.placeElementsInVerticalLine(
                guiList=activePosters,
                startPos=(0, 0, 0),
                alignCenter=True,
            )
            self.text_noTask.hide()
        else:
            # No posters, show text that we have no quests
            self.text_noTask.show()


if __name__ == "__main__":
    gui = DailyTaskSubpage(
        parent=aspect2d,
        # any kwargs go here
    )
    GUITemplateSliders(
        guiAffected=gui.node_left,
        guiKeys=('pos', 'scale'),
    )
    from toontown.booster.BoosterBase import BoosterBase
    import time
    gui.chalkboard.populateBoosters(
        boosters=[BoosterBase.fromStruct([reward, time.time() + 120]) for reward in __BoosterDict if reward] * 2
    )
    base.run()
