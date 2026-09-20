if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    # base.initCR()  # defines base.cr
    # base.startHeadlessShow()
    # base.initTalkAssistant()

from toontown.quest3.questlines.KudosQuestLine import KudosSafezoneIdToTier
from toontown.quest3.kudos import KudosConstants
from toontown.gui.TTGui import kwargsToOptionDefs
from toontown.gui.EasyManagedItem import EasyManagedItem
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from toontown.toonbase import ToontownGlobals, TTLocalizer
from direct.showbase import PythonUtil
from direct.gui.DirectGui import *


@DirectNotifyCategory()
class KudosDetailProgressPaperGUI(EasyManagedItem):
    """
    Has a paper for the progress of Kudos in a given playground.
    Gives detailed progress information.
    """

    left_x = -2.2816
    right_x = 0.115
    top_z = 0.25279
    down_z = -0.3057

    @InjectorTarget
    def __init__(self, zoneId: int, parent, **kw):
        # GUI boilerplate.
        boardModel = loader.loadModel('phase_3.5/models/gui/kudos/kudos_board_gui')
        optiondefs = kwargsToOptionDefs(
            relief=None,
            pos=(0.0, 0.0, 0.035),
            image=boardModel.find('**/LongPaper'),
            image_scale=(5.15294, 1.0, 1.0),
        )
        boardModel.removeNode()
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(KudosDetailProgressPaperGUI)

        self.zoneId = zoneId
        self.rankFrames = []

        # Load elements of this GUI.
        self.load()

        if base.localAvatar:
            self.setKudos(base.localAvatar.getKudos())
        self.accept('kudosUpdated', self.setKudos)

    """
    Loading methods
    """

    def load(self):
        for i, text in enumerate(TTLocalizer.KudoRewardDescriptions):
            # Make the text prefix.
            prefix = f'Rank {i + 2}'
            if i == 9:
                prefix = 'Post Rank 10'
            text = TTLocalizer.getKudosRewardFromRank(rank=i + 2, zoneId=self.zoneId)

            # Calculate the positions.
            x = self.left_x if i < 5 else self.right_x
            z = PythonUtil.lerp(v0=self.top_z, v1=self.down_z, t=(i % 5) / 4)

            # Spawn the frame.
            frame = DirectFrame(
                parent=self, relief=None,
                text=f'{prefix}: {text}', text_align=TextNode.ALeft,
                text_pos=(x, z), text_scale=0.135,
            )
            self.rankFrames.append(frame)

    def destroy(self):
        super().destroy()

    def setKudos(self, kudos: dict):
        totalKudosXp = kudos.get(self.zoneId, 0)
        if not base.localAvatar:
            return
        kudosRank = KudosConstants.getKudosRank(base.localAvatar, self.zoneId)

        # Reset all rank colors.
        for frame in self.rankFrames:
            frame['text_fg'] = (0, 0, 0, 1)
            frame['text_shadow'] = (0, 0, 0, 0)

        if kudosRank >= 2:
            # Update all relevant ranks.
            for frame in self.rankFrames[0:kudosRank - 1]:
                frame['text_fg'] = (0.439, 0.584, 0.282, 1.0)
                frame['text_shadow'] = (0, 0, 0, 1)

            # Set the last rank color if we're maxed.
            # if kudosRank == 10:
            #     frame = self.rankFrames[-1]
            #     frame['text_fg'] = (0.439, 0.584, 0.282, 1.0)
            #     frame['text_shadow'] = (0, 0, 0, 1)


if __name__ == "__main__":
    gui = KudosDetailProgressPaperGUI(
        zoneId=ToontownGlobals.ToontownCentral,
        parent=aspect2d,
        pos=(0, 0, -0.2),
        scale=0.5,
    )
    # gui.setKudosRank(5)
    # GUITemplateSliders(
    #     guiAffected=gui.rightText,
    #     guiKeys=('text_pos', 'text_scale'),
    # )
    base.run()
