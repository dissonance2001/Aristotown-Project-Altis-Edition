import time
from direct.gui.DirectGui import DirectFrame, DirectLabel
from direct.gui import DirectGuiGlobals as DGG
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.MetaInterval import Sequence, Parallel
from direct.interval.FunctionInterval import Func, Wait
from pandac.PandaModules import TextNode
from toontown.gumball import GumballGlobals
from toontown.toonbase import ToontownGlobals


class BoosterIcon(DirectFrame):
    def __init__(self, parent, boosterModel, boosterType, endTimestamp, pos, scale):
        self.boosterType = int(boosterType)
        self.endTimestamp = int(endTimestamp)
        self.hovered = False
        self.boosterModel = boosterModel
        node = self._getBoosterImage()
        kwargs = {
            'parent': parent,
            'relief': None,
            'pos': pos,
            'scale': scale,
            'state': DGG.NORMAL,
            'frameColor': (1, 1, 1, 0),
            'frameSize': (-0.62, 0.62, -0.62, 0.62),
        }
        if node is not None:
            kwargs['image'] = node
        DirectFrame.__init__(self, **kwargs)
        self.initialiseoptions(BoosterIcon)

        self.hoverText = DirectFrame(
            parent=base.a2dBottomLeft,
            relief=None,
            pos=(0.28, 0, 0.42),
            text=' ',
            text_pos=(0.0, 0.0),
            text_scale=(0.037, 0.037),
            text_align=TextNode.ACenter,
            text_fg=(1, 1, 1, 1),
            text_bg=(0, 0, 0, 0.7),
            text_shadow=(0, 0, 0, 1),
            text_wordwrap=11,
            sortOrder=200,
        )
        try:
            self.hoverText.setBin('gui-popup', 250)
        except:
            pass
        self.hoverText.hide()
        self._refreshHoverText()
        self.bind(DGG.ENTER, self._setHover, extraArgs=[True])
        self.bind(DGG.EXIT, self._setHover, extraArgs=[False])
        taskMgr.doMethodLater(1.0, self._updateHoverTask, self._taskName())

    def _taskName(self):
        return 'gumballOnscreenBooster-%s' % id(self)

    def _getBoosterImage(self):
        if not self.boosterModel or self.boosterModel.isEmpty():
            return None
        prefix = BoosterStatusPopup.boosterPrefixes.get(self.boosterType)
        if not prefix:
            return None
        node = self.boosterModel.find('**/%s' % prefix)
        if node.isEmpty():
            return None
        return node

    def _formatTime(self):
        left = max(0, int(self.endTimestamp - time.time()))
        days = left // 86400
        hours = (left % 86400) // 3600
        minutes = (left % 3600) // 60
        seconds = left % 60
        if days:
            return '%dd %dh %dm' % (days, hours, minutes)
        if hours:
            return '%dh %dm' % (hours, minutes)
        if minutes:
            return '%dm %ds' % (minutes, seconds)
        if seconds:
            return '%ds' % seconds
        return 'Expired!'

    def _refreshHoverText(self):
        name = GumballGlobals.getBoosterName(self.boosterType)
        desc = GumballGlobals.getBoosterDescription(self.boosterType)
        timeLeft = self._formatTime()
        hoverString = '%s\n\1TextShrink\1%s\2' % (name, desc)
        if timeLeft:
            hoverString += '\1TextSmaller\1\1TextSmaller\1\n\n\2\2\1TextShrink\1%s\2' % timeLeft
        self.hoverText['text'] = hoverString

    def _setHover(self, mode, event=None):
        self.hovered = bool(mode)
        if self.hovered:
            self._refreshHoverText()
            try:
                pos = self.getPos(base.a2dBottomLeft)
                hoverX = max(0.30, pos[0])
                hoverZ = max(0.28, pos[2] - 0.16)
                self.hoverText.setPos(hoverX, 0, hoverZ)
            except:
                self.hoverText.setPos(0.30, 0, 0.42)
            self.hoverText.show()
        else:
            self.hoverText.hide()

    def _updateHoverTask(self, task):
        if self.hovered:
            self._refreshHoverText()
        return task.again

    def destroy(self):
        taskMgr.remove(self._taskName())
        self.ignoreAll()
        if getattr(self, 'hoverText', None):
            self.hoverText.destroy()
            self.hoverText = None
        self.boosterModel = None
        DirectFrame.destroy(self)


class BoosterStatusPopup(DirectFrame):
    boosterPrefixes = {
        GumballGlobals.MERIT_SELLBOT: 'merit_sell',
        GumballGlobals.MERIT_CASHBOT: 'merit_cash',
        GumballGlobals.MERIT_LAWBOT: 'merit_law',
        GumballGlobals.MERIT_BOSSBOT: 'merit_boss',
        GumballGlobals.MERIT_BOARDBOT: 'merit_board',
        GumballGlobals.MERIT_GLOBAL: 'merit',
        GumballGlobals.JELLYBEANS_GLOBAL: 'jellybean2',
        GumballGlobals.EXP_GAGS_GLOBAL: 'gag_all',
        GumballGlobals.EXP_GAGS_SUPPORT: 'gag_support',
        GumballGlobals.EXP_GAGS_POWER: 'gag_power',
        GumballGlobals.REWARD_BOSS_GLOBAL: 'eyes',
        GumballGlobals.REWARD_BOSS_SELLBOT: 'sellboss',
        GumballGlobals.REWARD_BOSS_CASHBOT: 'cashboss',
        GumballGlobals.REWARD_BOSS_LAWBOT: 'lawboss',
        GumballGlobals.REWARD_BOSS_BOSSBOT: 'bossboss',
        GumballGlobals.REWARD_BOSS_BOARDBOT: 'boardboss',
        GumballGlobals.ALL_STAR: 'mainwashere',
        GumballGlobals.RANDOM: 'random',
        GumballGlobals.GUMBALLS_GLOBAL: 'gumball',
    }

    def __init__(self, ownerMeter):
        self.ownerMeter = ownerMeter
        self.boosterModel = None
        self.icons = []
        self.iconTargets = []
        self.emptyLabel = None
        self.closed = False
        self.closing = False
        self.boosterSignature = None
        self.openIval = None
        self.closeIval = None
        self.slideDuration = 0.32
        self.slideStagger = 0.045
        self.holdDuration = 7.0
        self.collapsedPos = (0.0, 0, -0.22)

        meterPos = ownerMeter.getPos(base.a2dBottomLeft)
        DirectFrame.__init__(
            self,
            parent=base.a2dBottomLeft,
            relief=None,
            pos=(meterPos[0], 0, meterPos[2] + 0.22),
            frameColor=(1, 1, 1, 0),
            frameSize=(-0.02, 0.72, -0.22, 0.30),
            sortOrder=100,
        )
        self.initialiseoptions(BoosterStatusPopup)
        try:
            self.setBin('gui-popup', 180)
        except:
            pass

        try:
            self.boosterModel = loader.loadModel('phase_3.5/models/gui/boosters')
        except:
            self.boosterModel = None

        self.accept('escape', self.close)
        if getattr(base, 'localAvatar', None):
            self.accept(base.localAvatar.uniqueName('gumballBoostersChange'), self._boostersChanged)

        self.rebuild(True)
        taskMgr.doMethodLater(1.0, self._updateTask, self._taskName())

    def _taskName(self):
        return 'gumballBoosterBar-%s' % id(self)

    def _autoCloseTaskName(self):
        return 'gumballBoosterAutoClose-%s' % id(self)

    def _boostersChanged(self, boosters=None):
        if not self.closed and not self.closing:
            self.rebuild(True)

    def _getBoosters(self):
        av = getattr(base, 'localAvatar', None)
        if not av or not hasattr(av, 'getGumballBoosters'):
            return []
        try:
            return GumballGlobals.cleanupBoosters(av.getGumballBoosters())
        except:
            return []

    def _stopIntervals(self):
        if self.openIval:
            try:
                self.openIval.pause()
            except:
                pass
            self.openIval = None
        if self.closeIval:
            try:
                self.closeIval.pause()
            except:
                pass
            self.closeIval = None

    def _clearIcons(self):
        self._stopIntervals()
        taskMgr.remove(self._autoCloseTaskName())
        for icon in self.icons:
            try:
                icon.destroy()
            except:
                pass
        self.icons = []
        self.iconTargets = []
        if self.emptyLabel:
            try:
                self.emptyLabel.destroy()
            except:
                pass
            self.emptyLabel = None

    def rebuild(self, animate=False):
        self._clearIcons()
        boosters = self._getBoosters()
        self.boosterSignature = tuple([(int(x[0]), int(x[1]), int(x[2])) for x in boosters])

        if not boosters:
            self.emptyLabel = DirectLabel(
                parent=self,
                relief=None,
                text='You have no active boosters.',
                text_font=ToontownGlobals.getInterfaceFont(),
                text_align=TextNode.ALeft,
                text_scale=0.035,
                text_fg=(1, 1, 1, 1),
                text_bg=(0, 0, 0, 0.7),
                pos=(0.02, 0, -0.02),
                sortOrder=190,
            )
            taskMgr.doMethodLater(self.holdDuration, self._autoClose, self._autoCloseTaskName())
            return

        maxPerRow = 6
        spacingX = 0.205
        spacingZ = 0.205
        iconScale = 0.19

        for index, data in enumerate(boosters):
            try:
                boosterType, endTimestamp, startTimestamp = data
            except:
                continue
            col = index % maxPerRow
            row = index // maxPerRow
            rowStart = row * maxPerRow
            rowCount = min(maxPerRow, len(boosters) - rowStart)
            centeredCol = col - ((rowCount - 1) * 0.5)
            targetPos = (centeredCol * spacingX, 0, row * spacingZ)
            startPos = self.collapsedPos if animate else targetPos
            icon = BoosterIcon(
                parent=self,
                boosterModel=self.boosterModel,
                boosterType=boosterType,
                endTimestamp=endTimestamp,
                pos=startPos,
                scale=iconScale,
            )
            self.icons.append(icon)
            self.iconTargets.append(targetPos)

        if animate:
            self._slideOut()
        else:
            taskMgr.doMethodLater(self.holdDuration, self._autoClose, self._autoCloseTaskName())

    def _slideOut(self):
        if self.closed or self.closing or not self.icons:
            return
        taskMgr.remove(self._autoCloseTaskName())
        intervals = []
        for index, icon in enumerate(self.icons):
            targetPos = self.iconTargets[index]
            intervals.append(Sequence(
                Wait(index * self.slideStagger),
                LerpPosInterval(icon, self.slideDuration, targetPos, startPos=icon.getPos(), blendType='easeOut')
            ))
        totalDuration = self.slideDuration + max(0, len(self.icons) - 1) * self.slideStagger
        self.openIval = Sequence(
            Parallel(*intervals),
            Func(self._openFinished, totalDuration)
        )
        self.openIval.start()

    def _openFinished(self, totalDuration=0.0):
        self.openIval = None
        if self.closed or self.closing:
            return
        taskMgr.remove(self._autoCloseTaskName())
        taskMgr.doMethodLater(self.holdDuration, self._autoClose, self._autoCloseTaskName())

    def _autoClose(self, task):
        self.close()
        return task.done

    def _slideIn(self):
        self._stopIntervals()
        intervals = []
        count = len(self.icons)
        for reverseIndex, icon in enumerate(reversed(self.icons)):
            delay = reverseIndex * self.slideStagger
            intervals.append(Sequence(
                Wait(delay),
                LerpPosInterval(icon, self.slideDuration, self.collapsedPos, startPos=icon.getPos(), blendType='easeIn')
            ))
            try:
                icon.hoverText.hide()
            except:
                pass
        if not intervals:
            self._finishClose()
            return
        self.closeIval = Sequence(
            Parallel(*intervals),
            Func(self._finishClose)
        )
        self.closeIval.start()

    def _updateTask(self, task):
        if self.closed:
            return task.done
        if self.closing:
            return task.cont
        boosters = self._getBoosters()
        signature = tuple([(int(x[0]), int(x[1]), int(x[2])) for x in boosters])
        if signature != self.boosterSignature:
            self.rebuild(True)
        return task.again

    def close(self, event=None):
        if self.closed or self.closing:
            return
        self.closing = True
        taskMgr.remove(self._autoCloseTaskName())
        self.ignore('escape')
        if self.ownerMeter:
            try:
                if self.ownerMeter.boosterPopup is self:
                    self.ownerMeter.boosterPopup = None
            except:
                pass
        if self.emptyLabel:
            self._finishClose()
            return
        self._slideIn()

    def _finishClose(self):
        if self.closed:
            return
        self.closed = True
        self.closing = False
        taskMgr.remove(self._taskName())
        taskMgr.remove(self._autoCloseTaskName())
        self._stopIntervals()
        self.ignoreAll()
        self.ownerMeter = None
        self._clearIcons()
        if self.boosterModel:
            try:
                self.boosterModel.removeNode()
            except:
                pass
            self.boosterModel = None
        DirectFrame.destroy(self)
