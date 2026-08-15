import time
from direct.gui.DirectGui import DirectFrame, DirectLabel
from direct.gui import DirectGuiGlobals as DGG
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
            parent=self,
            relief=None,
            pos=(0, 0, 0),
            text=' ',
            text_pos=(0.0, -0.7882),
            text_scale=(0.2462, 0.2462),
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
        self.emptyLabel = None
        self.closed = False
        self.boosterSignature = None

        meterPos = ownerMeter.getPos(base.a2dBottomLeft)
        DirectFrame.__init__(
            self,
            parent=base.a2dBottomLeft,
            relief=None,
            pos=(meterPos[0] + 0.02, 0, meterPos[2] + 0.22),
            frameColor=(1, 1, 1, 0),
            frameSize=(-0.02, 0.72, -0.02, 0.30),
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

        self.rebuild()
        taskMgr.doMethodLater(1.0, self._updateTask, self._taskName())

    def _taskName(self):
        return 'gumballBoosterBar-%s' % id(self)

    def _boostersChanged(self, boosters=None):
        if not self.closed:
            self.rebuild()

    def _getBoosters(self):
        av = getattr(base, 'localAvatar', None)
        if not av or not hasattr(av, 'getGumballBoosters'):
            return []
        try:
            return GumballGlobals.cleanupBoosters(av.getGumballBoosters())
        except:
            return []

    def _clearIcons(self):
        for icon in self.icons:
            try:
                icon.destroy()
            except:
                pass
        self.icons = []
        if self.emptyLabel:
            try:
                self.emptyLabel.destroy()
            except:
                pass
            self.emptyLabel = None

    def rebuild(self):
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
                pos=(0.02, 0, 0.02),
                sortOrder=190,
            )
            return

        maxPerRow = 6
        spacingX = 0.112
        spacingZ = 0.112
        iconScale = 0.112

        for index, data in enumerate(boosters):
            try:
                boosterType, endTimestamp, startTimestamp = data
            except:
                continue
            col = index % maxPerRow
            row = index // maxPerRow
            pos = (0.055 + col * spacingX, 0, row * spacingZ)
            icon = BoosterIcon(
                parent=self,
                boosterModel=self.boosterModel,
                boosterType=boosterType,
                endTimestamp=endTimestamp,
                pos=pos,
                scale=iconScale,
            )
            self.icons.append(icon)

    def _updateTask(self, task):
        if self.closed:
            return task.done
        boosters = self._getBoosters()
        signature = tuple([(int(x[0]), int(x[1]), int(x[2])) for x in boosters])
        if signature != self.boosterSignature:
            self.rebuild()
        return task.again

    def close(self, event=None):
        if self.closed:
            return
        self.closed = True
        taskMgr.remove(self._taskName())
        self.ignoreAll()
        if self.ownerMeter:
            try:
                self.ownerMeter.boosterPopup = None
            except:
                pass
        self.ownerMeter = None
        self._clearIcons()
        if self.boosterModel:
            try:
                self.boosterModel.removeNode()
            except:
                pass
            self.boosterModel = None
        DirectFrame.destroy(self)
