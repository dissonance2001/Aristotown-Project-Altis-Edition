from __future__ import absolute_import
from pandac.PandaModules import *
from toontown.shtiker import ShtikerPage
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from toontown.quest import Quests
from toontown.toon import NPCToons
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.quest import QuestBookPoster
from toontown.quest.QuestPoster import QuestPoster
from toontown.club import ClubGlobals
from direct.gui import DirectGuiGlobals as DGG
from direct.directnotify import DirectNotifyGlobal
import six
from six.moves import range

class QuestPage(ShtikerPage.ShtikerPage):
    notify = DirectNotifyGlobal.directNotify.newCategory('QuestPage')

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.quests = {0: None,
         1: None,
         2: None,
         3: None}
        self.textRolloverColor = Vec4(1, 1, 0, 1)
        self.textDownColor = Vec4(0.5, 0.9, 1, 1)
        self.textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
        self.onscreen = 0
        self.lastQuestTime = globalClock.getRealTime()

        # The Club Task tab remains the main management view. These fields
        # provide an additional read-only Clash-style display beside ToonTasks.
        self.clubTaskObjects = []
        self.clubTaskGui = None
        self.clubTaskCogGui = None
        self.clubTaskSosGui = None
        self.normalQuestFramePlaceList = (
            (-0.45, 0, 0.25, 0, 0, 0),
            (-0.45, 0, -0.35, 0, 0, 0),
            (0.45, 0, 0.25, 0, 0, 0),
            (0.45, 0, -0.35, 0, 0, 0),
        )
        # Preserve the original ToonTask poster size. The two columns are
        # shifted left only while Club Tasks are displayed beside them.
        self.clubQuestFramePlaceList = (
            (-0.84, 0, 0.25, 0, 0, 0),
            (-0.84, 0, -0.35, 0, 0, 0),
            (0.06, 0, 0.25, 0, 0, 0),
            (0.06, 0, -0.35, 0, 0, 0),
        )
        return

    def load(self):
        self.title = DirectLabel(parent=self, relief=None, text=TTLocalizer.QuestPageToonTasks, text_scale=0.12, textMayChange=0, pos=(0, 0, 0.6))
        self.questFrames = []
        for i in range(ToontownGlobals.MaxQuestCarryLimit):
            frame = QuestBookPoster.QuestBookPoster(reverse=i > 1, mapIndex=i + 1)
            frame.reparentTo(self)
            frame.setPosHpr(*self.normalQuestFramePlaceList[i])
            frame.setScale(1.06)
            self.questFrames.append(frame)

        # Use the same authored objective artwork as the Social Panel's
        # existing Club Task tab. Nothing in that tab is removed or replaced.
        try:
            self.clubTaskGui = loader.loadModel(
                'phase_3.5/models/gui/stickerbook_gui')
        except:
            self.clubTaskGui = None
        try:
            self.clubTaskCogGui = loader.loadModel(
                'phase_3/models/gui/cog_icons')
        except:
            self.clubTaskCogGui = None
        try:
            self.clubTaskSosGui = loader.loadModel(
                'phase_3.5/models/gui/sos_textures')
        except:
            self.clubTaskSosGui = None

        self.accept('questsChanged', self.updatePage)
        self.accept('club-state-updated', self._clubStateUpdated)
        return

    # ------------------------------------------------------------------
    # Clash-style Club Tasks beside the normal ToonTasks
    # ------------------------------------------------------------------
    def _clubStateUpdated(self, club=None):
        self.updateClubTasks(club)

    def _destroyClubTaskObjects(self):
        for obj in self.clubTaskObjects:
            try:
                obj.destroy()
            except:
                try:
                    obj.removeNode()
                except:
                    pass
        self.clubTaskObjects = []

    def _modelNode(self, model, name):
        if model is None:
            return None
        try:
            node = model.find('**/%s' % name)
            if node.isEmpty():
                return None
            return node
        except:
            return None

    def _clubTaskIcon(self, progressType):
        model = None
        nodeName = None

        if progressType == 'buildings':
            model = self.clubTaskGui
            nodeName = 'COG_building'
        elif progressType == 'trolley':
            model = self.clubTaskGui
            nodeName = 'trolley'
        elif progressType == 'fish':
            model = self.clubTaskSosGui
            nodeName = 'fish'
        elif progressType in ('cogs', 'bosses'):
            model = self.clubTaskCogGui
            nodeName = 'cog'

        return self._modelNode(model, nodeName) if nodeName else None

    def _clubTaskProgressText(self, progressType, progress, goal):
        if progressType == 'fish':
            return '%s of %s caught' % (progress, goal)
        if progressType in ('trolley', 'buildings'):
            return '%s of %s completed' % (progress, goal)
        return '%s of %s defeated' % (progress, goal)

    def _setQuestFrameLayout(self, showClubTasks):
        if showClubTasks:
            positions = self.clubQuestFramePlaceList
        else:
            positions = self.normalQuestFramePlaceList

        for index, frame in enumerate(self.questFrames):
            frame.setPosHpr(*positions[index])
            # Always retain Altis's original ToonTask poster size.
            frame.setScale(1.06)

    def _makeClubTaskPoster(self, task, index):
        zPositions = (0.36, 0.0, -0.36)
        holder = DirectFrame(
            parent=self,
            relief=None,
            pos=(0.79, 0, zPositions[index]),
        )
        self.clubTaskObjects.append(holder)

        poster = QuestPoster()
        poster.reparentTo(holder)
        poster.setScale(0.57)
        poster.setTransparency(TransparencyAttrib.MAlpha)
        poster.setAntialias(AntialiasAttrib.MAuto)
        poster['image_color'] = Vec4(0.42, 0.671, 1.0, 1.0)
        poster.questFrame.hide()

        textColor = (0.20, 0.16, 0.12, 1)
        progressType = str(task.get('progressType', ''))
        progress = max(0, int(task.get('progress', 0)))
        goal = max(1, int(task.get('goal', 1)))
        progress = min(progress, goal)

        DirectLabel(
            parent=holder,
            relief=None,
            text='CLUB TASK',
            text_font=ToontownGlobals.getMinnieFont(),
            # Fit the title cleanly inside the rolled top banner.
            text_scale=0.029,
            text_fg=textColor,
            pos=(0, 0, 0.127),
        )

        pictureFrame = self._modelNode(
            self.clubTaskGui, 'questPictureFrame')
        if pictureFrame is not None:
            DirectFrame(
                parent=holder,
                relief=None,
                image=pictureFrame,
                image_color=Vec4(0.42, 0.671, 1.0, 1.0),
                image_scale=0.069,
                pos=(0, 0, 0.062),
            )

        icon = self._clubTaskIcon(progressType)
        if icon is not None:
            DirectFrame(
                parent=holder,
                relief=None,
                geom=icon,
                geom_scale=0.069,
                pos=(0, 0, 0.062),
            )

        DirectLabel(
            parent=holder,
            relief=None,
            text=task.get('name', 'Club Task'),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.031,
            text_wordwrap=12.0,
            text_align=TextNode.ACenter,
            text_fg=textColor,
            text_shadow=(1, 1, 1, 0.30),
            pos=(0, 0, -0.018),
        )
        DirectLabel(
            parent=holder,
            relief=None,
            text='Anywhere',
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.022,
            text_fg=textColor,
            pos=(0, 0, -0.091),
        )

        DirectWaitBar(
            parent=holder,
            relief=DGG.SUNKEN,
            borderWidth=(0.004, 0.004),
            # Restore the original bar size, but keep it raised inside
            # the blue task paper above the rolled bottom edge.
            frameSize=(-0.150, 0.150, -0.013, 0.014),
            frameColor=(0.945, 0.875, 0.706, 1),
            barColor=(0.5, 0.7, 0.5, 1),
            range=goal,
            value=progress,
            text=self._clubTaskProgressText(
                progressType, progress, goal),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_scale=0.018,
            text_fg=(0.05, 0.14, 0.4, 1),
            text_shadow=(1, 1, 1, 0.35),
            text_pos=(0, -0.005),
            pos=(0, 0, -0.120),
        )

    def updateClubTasks(self, club=None):
        self._destroyClubTaskObjects()

        if club is None:
            manager = getattr(base.cr, 'clubMgr', None)
            if manager is not None:
                try:
                    if manager.isInClub():
                        club = manager.club
                except:
                    club = getattr(manager, 'club', None)

        if not isinstance(club, dict):
            club = {}

        tasks = club.get('tasks', [])[:ClubGlobals.MAX_ACTIVE_TASKS]
        self._setQuestFrameLayout(bool(tasks))

        for index, task in enumerate(tasks):
            self._makeClubTaskPoster(task, index)

    def acceptOnscreenHooks(self):
        self.accept(ToontownGlobals.QuestsHotkeyOn, self.showQuestsOnscreen)
        self.accept(ToontownGlobals.QuestsHotkeyOff, self.hideQuestsOnscreen)

    def ignoreOnscreenHooks(self):
        self.ignore(ToontownGlobals.QuestsHotkeyOn)
        self.ignore(ToontownGlobals.QuestsHotkeyOff)

    def unload(self):
        self.ignore('questsChanged')
        self.ignore('club-state-updated')
        self._destroyClubTaskObjects()
        del self.title
        del self.quests
        del self.questFrames

        for modelName in (
                'clubTaskGui', 'clubTaskCogGui', 'clubTaskSosGui'):
            model = getattr(self, modelName, None)
            if model is not None:
                try:
                    model.removeNode()
                except:
                    pass
                setattr(self, modelName, None)

        loader.unloadModel('phase_3.5/models/gui/stickerbook_gui')
        ShtikerPage.ShtikerPage.unload(self)

    def clearQuestFrame(self, index):
        self.questFrames[index].clear()
        self.quests[index] = None
        return

    def fillQuestFrame(self, questDesc, index):
        self.questFrames[index].update(questDesc)
        self.quests[index] = questDesc

    def getLowestUnusedIndex(self):
        for i in range(ToontownGlobals.MaxQuestCarryLimit):
            if self.quests[i] == None:
                return i

        return -1

    def updatePage(self):
        self.notify.debug('updatePage()')
        newQuests = base.localAvatar.quests
        carryLimit = base.localAvatar.getQuestCarryLimit()
        for i in range(ToontownGlobals.MaxQuestCarryLimit):
            if i < carryLimit:
                self.questFrames[i].show()
            else:
                self.questFrames[i].hide()

        for index, questDesc in self.quests.items():
            if questDesc is not None and list(questDesc) not in newQuests:
                self.clearQuestFrame(index)

        for questDesc in newQuests:
            newQuestDesc = tuple(questDesc)
            if newQuestDesc not in list(self.quests.values()):
                index = self.getLowestUnusedIndex()
                self.fillQuestFrame(newQuestDesc, index)

        for i, questDesc in six.iteritems(self.quests):
            if questDesc:
                if self.canDeleteQuest(questDesc):
                    self.questFrames[i].setDeleteCallback(self.__deleteQuest)
                else:
                    self.questFrames[i].setDeleteCallback(None)
                self.questFrames[i].update(questDesc)
            else:
                self.questFrames[i].unbindMouseEnter()

        self.updateClubTasks()
        messenger.send('questPageUpdated')
        return

    def enter(self):
        self.updatePage()
        ShtikerPage.ShtikerPage.enter(self)

    def exit(self):
        ShtikerPage.ShtikerPage.exit(self)

    def showQuestsOnscreenTutorial(self):
        self.setPos(0, 0, -0.2)
        self.showQuestsOnscreen()

    def showQuestsOnscreen(self):
        messenger.send('wakeup')
        timedif = globalClock.getRealTime() - self.lastQuestTime
        if timedif < 0.7:
            return
        self.lastQuestTime = globalClock.getRealTime()
        if self.onscreen or base.localAvatar.invPage.onscreen:
            return
        self.onscreen = 1
        for i in range(ToontownGlobals.MaxQuestCarryLimit):
            if hasattr(self.questFrames[i], 'mapIndex'):
                self.questFrames[i].mapIndex.show()

        self.updatePage()
        self.reparentTo(aspect2d)
        self.title.hide()
        self.show()

    def hideQuestsOnscreenTutorial(self):
        self.setPos(0, 0, 0)
        self.hideQuestsOnscreen()

    def hideQuestsOnscreen(self):
        if not self.onscreen:
            return
        self.onscreen = 0
        for i in range(ToontownGlobals.MaxQuestCarryLimit):
            if hasattr(self.questFrames[i], 'mapIndex'):
                self.questFrames[i].mapIndex.hide()

        self.reparentTo(self.book)
        self.title.show()
        self.hide()

    def canDeleteQuest(self, questDesc):
        return Quests.isQuestJustForFun(questDesc[0], questDesc[3]) and self.onscreen == 0

    def __deleteQuest(self, questDesc):
        base.localAvatar.d_requestDeleteQuest(questDesc)
