from __future__ import absolute_import
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
from toontown.quest import Quests
from toontown.quest import QuestPoster


class KudosBoardGui(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('KudosBoardGui')

    def __init__(self, offers=None):
        DirectFrame.__init__(
            self,
            parent=aspect2d,
            relief=None,
            frameSize=(-1.33, 1.33, -0.95, 0.95),
            sortOrder=100
        )
        self.initialiseoptions(KudosBoardGui)
        self.setBin('gui-popup', 100)
        self.cards = []
        self.offers = offers or []
        self.refreshTaskName = 'kudos-board-refresh-%s' % id(self)
        self.timerTaskName = 'kudos-board-timer-%s' % id(self)
        self.refreshDeadline = globalClock.getFrameTime() + 10.0

        self.boardModel = loader.loadModel(
            'phase_3.5/models/gui/kudos/kudos_board'
        )
        if not self.boardModel.isEmpty():
            self.boardModel.reparentTo(self)
            minPoint, maxPoint = self.boardModel.getTightBounds()
            center = (minPoint + maxPoint) * 0.5
            size = maxPoint - minPoint
            width = max(size.getX(), 0.001)
            height = max(size.getZ(), 0.001)
            targetWidth = 2.73
            targetHeight = 1.98
            scaleX = targetWidth / width
            scaleZ = targetHeight / height
            self.boardModel.setScale(scaleX, 1.0, scaleZ)
            self.boardModel.setPos(
                -center.getX() * scaleX,
                0,
                -center.getZ() * scaleZ
            )

        self.partsModel = loader.loadModel(
            'phase_3.5/models/gui/kudos/kudos_board_gui'
        )

        self.statusLabel = DirectLabel(
            parent=self,
            relief=None,
            text='',
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.04,
            text_fg=(0.18, 0.08, 0.02, 1),
            pos=(0, 0, -0.88)
        )

        self.resetTimerLabel = DirectLabel(
            parent=self,
            relief=None,
            text='Resets in: 0:10',
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.045,
            text_fg=(0.18, 0.08, 0.02, 1),
            pos=(0, 0, -0.95)
        )

        self._makeCards()
        self._makeExitButton()

        self.accept('escape', self.close)
        taskMgr.doMethodLater(
            10.0,
            self._refreshOffers,
            self.refreshTaskName
        )
        taskMgr.add(self._updateResetTimer, self.timerTaskName)

        base.setCellsActive(base.leftCells, 0)
        if hasattr(base, 'bottomCells') and base.bottomCells:
            base.setCellsActive(base.bottomCells[:2], 0)

    def _refreshOffers(self, task):
        self.refreshTaskName = None
        if hasattr(base, 'localAvatar') and base.localAvatar:
            if getattr(base.localAvatar, 'kudosBoardGui', None) is self:
                base.localAvatar.requestKudosBoard()
        return task.done

    def _updateResetTimer(self, task):
        remaining = int(max(
            0,
            self.refreshDeadline - globalClock.getFrameTime() + 0.999
        ))
        minutes = remaining / 60
        seconds = remaining % 60
        self.resetTimerLabel['text'] = 'Resets in: %d:%02d' % (
            minutes,
            seconds
        )
        return task.cont

    def _makeCards(self):
        xPositions = (-0.93, -0.31, 0.31, 0.93)
        zPositions = (0.326, -0.144, -0.614)

        if not self.offers:
            self.statusLabel['text'] = 'No ToonTasks are available.'
            return

        for index, offer in enumerate(self.offers[:12]):
            row = index / 4
            column = index % 4
            questId = offer[0]
            toNpcId = offer[1]
            rewardId = offer[2]

            poster = QuestPoster.QuestPoster()
            poster.reparentTo(self)
            poster.showChoicePoster(
                questId,
                Quests.ToonHQ,
                toNpcId,
                rewardId,
                self._chooseQuest
            )
            reward = Quests.getReward(rewardId)
            if isinstance(reward, Quests.MoneyReward):
                poster.rewardCircle.hide()
                poster.jbCircle['text'] = str(reward.getAmount())
                poster.jbCircle.show()
            poster.setScale(0.78)
            poster.setPos(
                xPositions[column],
                0,
                zPositions[row]
            )

            self.cards.append(poster)

    def _chooseQuest(self, questId):
        if hasattr(base, 'localAvatar') and base.localAvatar:
            base.localAvatar.chooseKudosBoardQuest(questId)

    def showResult(self, resultCode):
        if resultCode == 1:
            self.close()
            return
        if resultCode == 2:
            self.statusLabel['text'] = 'Your ToonTask list is full.'
        elif resultCode == 3:
            self.statusLabel['text'] = 'That ToonTask is no longer available.'
        elif resultCode == 4:
            self.statusLabel['text'] = 'No ToonTasks are available.'
        else:
            self.statusLabel['text'] = 'The ToonTask could not be added.'

    def _makeExitButton(self):
        normal = NodePath()
        pressed = NodePath()
        rollover = NodePath()

        if not self.partsModel.isEmpty():
            normal = self.partsModel.find('**/Kudos_Exit_N')
            pressed = self.partsModel.find('**/Kudos_Exit_P')
            rollover = self.partsModel.find('**/Kudos_Exit_H')

        if not normal.isEmpty():
            if pressed.isEmpty():
                pressed = normal
            if rollover.isEmpty():
                rollover = normal

            self.exitButton = DirectButton(
                parent=self,
                relief=None,
                geom=(normal, pressed, rollover, normal),
                geom_scale=0.09,
                pos=(1.27, 0, -0.86),
                command=self.close
            )
        else:
            quitModel = loader.loadModel('phase_3/models/gui/quit_button')
            self.exitButton = DirectButton(
                parent=self,
                relief=None,
                image=(
                    quitModel.find('**/QuitBtn_UP'),
                    quitModel.find('**/QuitBtn_DN'),
                    quitModel.find('**/QuitBtn_RLVR')
                ),
                image_scale=0.7,
                pos=(1.27, 0, -0.86),
                command=self.close
            )
            quitModel.removeNode()

    def close(self):
        if hasattr(base, 'localAvatar') and base.localAvatar:
            if getattr(base.localAvatar, 'kudosBoardGui', None) is self:
                base.localAvatar.kudosBoardGui = None
        messenger.send('kudosBoardGuiClosed')
        self.destroy()

    def destroy(self):
        self.ignoreAll()

        if getattr(self, 'refreshTaskName', None):
            taskMgr.remove(self.refreshTaskName)
            self.refreshTaskName = None

        if getattr(self, 'timerTaskName', None):
            taskMgr.remove(self.timerTaskName)
            self.timerTaskName = None

        base.setCellsActive(base.leftCells, 1)
        if hasattr(base, 'bottomCells') and base.bottomCells:
            base.setCellsActive(base.bottomCells[:2], 1)

        for card in self.cards:
            card.destroy()
        self.cards = []

        if hasattr(self, 'exitButton') and self.exitButton:
            self.exitButton.destroy()
            self.exitButton = None

        if hasattr(self, 'statusLabel') and self.statusLabel:
            self.statusLabel.destroy()
            self.statusLabel = None

        if hasattr(self, 'resetTimerLabel') and self.resetTimerLabel:
            self.resetTimerLabel.destroy()
            self.resetTimerLabel = None

        if hasattr(self, 'boardModel') and self.boardModel:
            self.boardModel.removeNode()
            self.boardModel = None

        if hasattr(self, 'partsModel') and self.partsModel:
            self.partsModel.removeNode()
            self.partsModel = None

        DirectFrame.destroy(self)
