from pandac.PandaModules import *
from direct.gui.DirectGui import *
from toontown.building import DistributedElevator
from toontown.building import DistributedBossElevator
from toontown.building.ElevatorConstants import *
from direct.directnotify import DirectNotifyGlobal
from toontown.suit import BossSelectionGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals

SELECTED_COLOR = (0.35, 0.8, 0.35, 1)
UNSELECTED_COLOR = (0.62, 0.62, 0.68, 1)
DISABLED_COLOR = (0.42, 0.42, 0.47, 1)


class DistributedVPElevator(DistributedBossElevator.DistributedBossElevator):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedVPElevator')

    def __init__(self, cr):
        DistributedBossElevator.DistributedBossElevator.__init__(self, cr)
        self.type = ELEVATOR_VP
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.bossType = BossSelectionGlobals.DEFAULT_SELLBOT_BOSS
        self.bossSelectFrame = None
        self.bossSelectButtons = {}
        self.bossStatusLabel = None
        self.selectorLocked = False

    def setupElevator(self):
        self.elevatorModel = loader.loadModel('phase_9/models/cogHQ/cogHQ_elevator')
        icon = self.elevatorModel.find('**/big_frame/')
        icon.hide()
        self.leftDoor = self.elevatorModel.find('**/left-door')
        self.rightDoor = self.elevatorModel.find('**/right-door')
        geom = base.cr.playGame.hood.loader.geom
        locator = geom.find('**/elevator_locator')
        self.elevatorModel.reparentTo(locator)
        self.elevatorModel.setH(180)
        DistributedElevator.DistributedElevator.setupElevator(self)

    def getDestName(self):
        return TTLocalizer.ElevatorSellBotBoss

    # ---- boss selection (network) ----
    def setBossType(self, bossType):
        self.bossType = bossType
        self.refreshBossSelector()

    # ---- seat bookkeeping hooks ----
    def addToonToSlot(self, avId, index):
        DistributedBossElevator.DistributedBossElevator.addToonToSlot(self, avId, index)
        self.refreshBossSelector()

    def clearToonFromSlot(self, avId, index):
        DistributedBossElevator.DistributedBossElevator.clearToonFromSlot(self, avId, index)
        self.refreshBossSelector()

    def enterWaitEmpty(self, ts):
        self.selectorLocked = False
        DistributedBossElevator.DistributedBossElevator.enterWaitEmpty(self, ts)

    def enterWaitCountdown(self, ts):
        self.selectorLocked = False
        DistributedBossElevator.DistributedBossElevator.enterWaitCountdown(self, ts)
        self.refreshBossSelector()

    def enterClosing(self, ts):
        self.selectorLocked = True
        self.hideBossSelector()
        DistributedBossElevator.DistributedBossElevator.enterClosing(self, ts)

    def disable(self):
        self.destroyBossSelector()
        DistributedBossElevator.DistributedBossElevator.disable(self)

    def delete(self):
        self.destroyBossSelector()
        DistributedBossElevator.DistributedBossElevator.delete(self)

    # ---- selector GUI ----
    def getLeaderAvId(self):
        if not self.boardedAvIds:
            return None
        return min(self.boardedAvIds, key=lambda avId: self.boardedAvIds[avId])

    def isLocalToonAboard(self):
        av = getattr(base, 'localAvatar', None)
        return av is not None and av.doId in self.boardedAvIds

    def isLocalToonLeader(self):
        av = getattr(base, 'localAvatar', None)
        return av is not None and self.getLeaderAvId() == av.doId

    def refreshBossSelector(self):
        if self.selectorLocked or not self.isLocalToonAboard():
            self.hideBossSelector()
            return
        if self.bossSelectFrame is None:
            self.buildBossSelector()
        self.updateBossSelector()
        self.bossSelectFrame.show()

    def buildBossSelector(self):
        font = ToontownGlobals.getInterfaceFont()
        self.bossSelectFrame = DirectFrame(
            parent=base.a2dTopCenter, relief=DGG.FLAT, frameColor=(0.12, 0.1, 0.18, 0.8),
            frameSize=(-0.66, 0.66, -0.37, 0.0), pos=(0, 0, -0.1), state=DGG.NORMAL)
        DirectLabel(
            parent=self.bossSelectFrame, relief=None, text=BossSelectionGlobals.SelectTitle,
            text_font=font, text_fg=(1, 0.9, 0.3, 1), text_scale=0.07, pos=(0, 0, -0.09))
        options = BossSelectionGlobals.getSellbotOptions()
        spacing = 0.6
        startX = -(len(options) - 1) * spacing / 2.0
        self.bossSelectButtons = {}
        for i, bossType in enumerate(options):
            self.bossSelectButtons[bossType] = DirectButton(
                parent=self.bossSelectFrame, relief=DGG.RAISED, borderWidth=(0.012, 0.012),
                frameSize=(-0.27, 0.27, -0.065, 0.075), text=BossSelectionGlobals.getBossName(bossType),
                text_font=font, text_scale=0.052, text_pos=(0, -0.015),
                pos=(startX + i * spacing, 0, -0.21), command=self.handleBossButton, extraArgs=[bossType])
        self.bossStatusLabel = DirectLabel(
            parent=self.bossSelectFrame, relief=None, text='', text_font=font,
            text_fg=(1, 1, 1, 1), text_scale=0.042, text_wordwrap=28, pos=(0, 0, -0.31))

    def updateBossSelector(self):
        leader = self.isLocalToonLeader()
        for bossType, button in self.bossSelectButtons.items():
            if bossType == self.bossType:
                color = SELECTED_COLOR
            elif leader:
                color = UNSELECTED_COLOR
            else:
                color = DISABLED_COLOR
            button['frameColor'] = (color, color, color, color)
            button['state'] = DGG.NORMAL if leader else DGG.DISABLED
        if leader:
            hint = BossSelectionGlobals.SelectLeaderHint
        else:
            hint = BossSelectionGlobals.SelectCurrent % BossSelectionGlobals.getBossName(self.bossType)
            hint += '\n' + BossSelectionGlobals.SelectFollowerHint
        self.bossStatusLabel['text'] = hint

    def handleBossButton(self, bossType):
        if self.selectorLocked or not self.isLocalToonLeader():
            return
        if bossType != self.bossType:
            self.sendUpdate('requestBossType', [bossType])

    def hideBossSelector(self):
        if self.bossSelectFrame is not None:
            self.bossSelectFrame.hide()

    def destroyBossSelector(self):
        if self.bossSelectFrame is not None:
            self.bossSelectFrame.destroy()
            self.bossSelectFrame = None
        self.bossSelectButtons = {}
        self.bossStatusLabel = None
