from toontown.gui.PositionedGUI import PositionedGUI, OnscreenPositionData
from toontown.quest3.gui.Quest3Poster import QuestPoster
from toontown.suit import SuitDNA
from direct.gui.DirectGui import DirectLabel, DirectFrame, DirectWaitBar, DGG, OnscreenText
from direct.interval.IntervalGlobal import Sequence, Parallel, Func, LerpFunctionInterval, LerpPosInterval
from toontown.toonbase.ToontownGlobals import getSuitFont
from toontown.suit.BossCog import ModelDict
from toontown.suit import SuitHealthMeter
from toontown.toonbase import TTLocalizer
from panda3d.core import TextNode, Vec4, NodePath


class BossHealthBar(DirectFrame, PositionedGUI):
    conditionThresholds = [0.95, 0.9, 0.8, 0.7, 0.6, 0.5, 0.3, 0.15, 0.0]
    onScreenPos = (-0.458, 0, 0)
    offScreenPos = (1.0, 0, 0)

    SCREEN_INDEX = 10
    GUI_BOUNDS = OnscreenPositionData(
        top=0.25, down=0.15, width=2,
    )
    EXTEND_VERTICAL = True

    def __init__(self, dept, maxHp, hp):
        DirectFrame.__init__(self, parent=base.a2dTopRight, relief=None)
        self.dept = dept
        self.head = None
        self.maxHp = maxHp
        self.hp = hp
        self.track = None
        self.moveTrack = None
        self.bossName = ''
        self.nameLabel = None
        self.stunCountText = None
        self.damageDealtText = None
        self.speedDamageDealtText = None
        self.cogDestructionText = None
        self.goonsStompedText = None
        self.damageDealt = 0
        self.speedDamageDealt = 0
        self.stunCount = 0
        self.cogDestruction = 0
        self.goonsStomped = 0
        self.accept(base.TOGGLE_PERSONAL_BOSS_STATS, self.toggleBossStats)

    def load(self):
        gui = loader.loadModel('phase_5/models/cogdominium/tt_m_gui_csa_flyThru')
        self.background = gui.find('**/*background')
        gui.removeNode()
        self.gui = DirectFrame(parent=self, relief=None, image=self.background, image_scale=(2, 1, 2),
                               pos=self.offScreenPos, sortOrder=40)
        gui = loader.loadModel('phase_3/models/gui/cog_icons')
        self.deptLabel = gui.find(SuitDNA.suitDeptModelPaths.get(self.dept))
        gui.removeNode()
        self.nameLabel = DirectLabel(parent=self.gui, relief=None, text=self.bossName, pos=(0.05, 0, 0.03),
                                     text_fg=(1, 1, 1, 1), text_style=3, text_scale=0.075, text_align=TextNode.ACenter,
                                     text_font=getSuitFont())
        self.deptFrame = DirectFrame(parent=self.gui, relief=None, image=self.deptLabel, image_scale=(0.25),
                                     pos=(-0.35, 1, 0), sortOrder=48)
        self.backgroundBar = DirectWaitBar(parent=self.gui, relief=DGG.SUNKEN, text='', sortOrder=45,
                                           text_align=TextNode.ACenter, text_scale=0.15, text_font=getSuitFont(),
                                           text_fg=(0, 0, 0, 1), text_pos=(0, -0.05), scale=(0.5), pos=(0.05, 0, -0.03),
                                           frameSize=(-0.5, 0.5, -0.1, 0.1), borderWidth=(0.01, 0.01), range=self.maxHp,
                                           value=self.hp, frameColor=(0.5, 0.5, 0.5, 0.5),
                                           barColor=(1.0, 1.0, 1.0, 1.0))
        self.healthBar = DirectWaitBar(parent=self.gui, relief=None,
                                       text=TTLocalizer.BossBarHealth % (self.hp, self.maxHp), sortOrder=50,
                                       text_align=TextNode.ACenter, text_scale=0.15, text_font=getSuitFont(),
                                       text_fg=(0, 0, 0, 1), text_pos=(0, -0.035), scale=(0.5), pos=(0.05, 0, -0.03),
                                       frameSize=(-0.5, 0.5, -0.1, 0.1), borderWidth=(0.01, 0.01), range=self.maxHp,
                                       value=self.hp, frameColor=(0.0, 0.0, 0.0, 0.0),
                                       barColor=SuitHealthMeter.HEALTH_COLORS[0])
        self.damageDealtText = OnscreenText(parent=self.gui, text=TTLocalizer.BossBarDamage % self.damageDealt, style=3,
                                            fg=(1, 1, 1, 1), align=TextNode.ALeft, scale=0.07, pos=(-0.474, -0.187))
        self.stunCountText = OnscreenText(parent=self.gui, text=TTLocalizer.BossBarStuns % self.stunCount, style=3,
                                          fg=(1, 1, 1, 1), align=TextNode.ALeft, scale=0.07, pos=(-0.474, -0.25))
        if self.dept == 'c':
            self.speedDamageDealtText = OnscreenText(parent=self.gui,
                                                     text=TTLocalizer.BossBarGolf % self.speedDamageDealt, style=3,
                                                     fg=(1, 1, 1, 1), align=TextNode.ALeft, scale=0.07,
                                                     pos=(-0.474, -0.32))
        if self.dept == 'l':
            self.cogDestructionText = OnscreenText(parent=self.gui,
                                                   text=TTLocalizer.BossBarCogDestruction % self.cogDestruction,
                                                   style=3, fg=(1, 1, 1, 1), align=TextNode.ALeft, scale=0.07,
                                                   pos=(-0.474, -0.31))
        if self.dept == 'm':
            self.goonsStompedText = OnscreenText(parent=self.gui,
                                                 text=TTLocalizer.BossBarGoonsStomped % self.goonsStomped, style=3,
                                                 fg=(1, 1, 1, 1), align=TextNode.ALeft, scale=0.07, pos=(-0.474, -0.31))
        self.updateHealth(self.hp)
        # self.accept('avPanelCreated', self.moveForAvPanel)
        # self.accept('avPanelClosed', self.moveBackFromAvPanel)

    def show(self):
        super().show()
        self.startPositionManagement()

    def hide(self):
        super().hide()
        self.stopPositionManagement()

    def updateHealth(self, hp):
        oldHp = self.hp
        if hp < 0:
            hp = 0
        self.hp = hp
        if self.track:
            self.track.pause()
            self.track = None
        self.track = Sequence(
            Parallel(
                Sequence(
                    LerpFunctionInterval(self.__lerpHealth, fromData=oldHp, toData=self.hp, duration=0.5,
                                         blendType='easeOut'),
                    LerpFunctionInterval(self.__lerpBackground, fromData=oldHp, toData=self.hp, duration=0.1,
                                         blendType='easeOut')
                ),
                Sequence(
                    LerpFunctionInterval(self.__lerpColor, fromData=oldHp, toData=self.hp, duration=0.5,
                                         blendType='easeOut')
                )
            )
        )
        self.track.start()

    def __lerpHealth(self, health):
        self.healthBar['value'] = int(health)
        if self.dept != 's':
            self.healthBar['text'] = TTLocalizer.BossBarHealth % (int(health), self.maxHp)
        else:
            self.healthBar['text'] = f"{int(health / 10)}%"

    def __lerpBackground(self, health):
        self.backgroundBar['value'] = int(health)

    def __lerpColor(self, health):
        if not self.healthBar:
            return
        healthRatio = health / self.maxHp
        if healthRatio <= 0:
            return
        if healthRatio > self.conditionThresholds[0]:
            condition = 0
        elif healthRatio > self.conditionThresholds[1]:
            condition = 1
        elif healthRatio > self.conditionThresholds[2]:
            condition = 2
        elif healthRatio > self.conditionThresholds[3]:
            condition = 3
        elif healthRatio > self.conditionThresholds[4]:
            condition = 4
        elif healthRatio > self.conditionThresholds[5]:
            condition = 5
        elif healthRatio > self.conditionThresholds[6]:
            condition = 6
        elif healthRatio > self.conditionThresholds[7]:
            condition = 7
        else:
            condition = 8

        if condition > 0:
            numeratorRatioAmt = self.conditionThresholds[condition - 1]
        else:
            numeratorRatioAmt = 1
        denominatorRatioAmt = self.conditionThresholds[condition]
        numeratorColorAmt = SuitHealthMeter.HEALTH_COLORS[condition]
        denominatorColorAmt = SuitHealthMeter.HEALTH_COLORS[condition + 1]
        currentRatioAmt = numeratorRatioAmt - healthRatio
        totalRatioAmt = numeratorRatioAmt - denominatorRatioAmt
        ratioRatio = currentRatioAmt / totalRatioAmt
        differenceColorAmt = denominatorColorAmt - numeratorColorAmt
        ratioColorToAdd = differenceColorAmt * ratioRatio
        totalColorAmt = SuitHealthMeter.HEALTH_COLORS[condition] + ratioColorToAdd
        self.healthBar['barColor'] = totalColorAmt

    def destroy(self):
        self.ignoreAll()
        if self.track:
            self.track.finish()
            self.track = None
        self.clearMoveTrack()
        self.stopPositionManagement()
        DirectFrame.destroy(self)

    def setMaxHp(self, maxHp):
        self.maxHp = maxHp
        self.hp = maxHp
        self.healthBar['range'] = maxHp
        self.healthBar['value'] = maxHp
        self.backgroundBar['range'] = maxHp
        self.backgroundBar['value'] = maxHp
        self.healthBar['text'] = TTLocalizer.BossBarHealth % (self.hp, self.maxHp)

    def setHead(self, head):
        self.gui['geom'] = head
        self.gui['geom_scale'] = 0.025
        # CEO head too fat
        self.gui['geom_pos'] = (-0.5, 0, -0.02 if self.dept == 'c' else 0.05)
        self.gui['geom_hpr'] = (-90, 0, 270)

    def setBossName(self, name):
        self.nameLabel['text'] = name

    def createBossCogHead(self):
        filePrefix = ModelDict[self.dept]
        head = loader.loadModel(filePrefix + '-head-zero')
        head.setDepthTest(True)
        head.setDepthWrite(True)
        self.setHead(head)

    def moveForAvPanel(self, type='s'):
        if self.moveTrack and self.moveTrack.getName() == 'movingOut':
            return
        self.clearMoveTrack()
        x = -0.95 if type == 's' else -1.05
        self.moveTrack = Sequence(LerpPosInterval(self.gui, 0.3, (x, 0, -0.25), blendType='easeInOut'))
        self.moveTrack.start()

    def moveBackFromAvPanel(self):
        if self.moveTrack and self.moveTrack.getName() == 'movingOut':
            return
        self.clearMoveTrack()
        self.moveTrack = Sequence(LerpPosInterval(self.gui, 0.3, (-0.458, 0, -0.25), blendType='easeInOut'))
        self.moveTrack.start()

    def moveInInitial(self):
        self.clearMoveTrack()
        self.moveTrack = Sequence(Func(self.show), LerpPosInterval(self.gui, 1.0, self.onScreenPos, self.offScreenPos,
                                                                   blendType='easeInOut'), name='movingIn')
        self.moveTrack.start()

    def moveOutEnd(self):
        self.clearMoveTrack()
        self.moveTrack = Sequence(
            LerpPosInterval(self.gui, 1.0, self.offScreenPos, self.onScreenPos, blendType='easeInOut'), Func(self.hide),
            name='movingOut')
        self.moveTrack.start()

    def clearMoveTrack(self):
        if self.moveTrack:
            self.moveTrack.pause()
            self.moveTrack = None

    def toggleBossStats(self):
        if self.damageDealtText.isHidden():
            self.damageDealtText.show()
            self.stunCountText.show()
            if self.speedDamageDealtText:
                self.speedDamageDealtText.show()
            if self.cogDestructionText:
                self.cogDestructionText.show()
            if self.goonsStompedText:
                self.goonsStompedText.show()
        else:
            self.damageDealtText.hide()
            self.stunCountText.hide()
            if self.speedDamageDealtText:
                self.speedDamageDealtText.hide()
            if self.cogDestructionText:
                self.cogDestructionText.hide()
            if self.goonsStompedText:
                self.goonsStompedText.hide()

    def updateDamageDealt(self, avId, damageDealt):
        if avId == base.localAvatar.doId:
            self.damageDealt += damageDealt
            self.damageDealtText.setText(TTLocalizer.BossBarDamage % self.damageDealt)

    def updateSpeedDamageDealt(self, avId, speedDamageDealt):
        if avId == base.localAvatar.doId:
            self.speedDamageDealt += speedDamageDealt
            self.speedDamageDealtText.setText(TTLocalizer.BossBarGolf % self.speedDamageDealt)

    def updateCogDestructionCount(self, avId, cogDestroy):
        if avId == base.localAvatar.doId:
            self.cogDestruction += cogDestroy
            self.cogDestructionText.setText(TTLocalizer.BossBarCogDestruction % self.cogDestruction)

    def updateGoonsStomped(self, avId):
        if avId == base.localAvatar.doId:
            self.goonsStomped += 1
            self.goonsStompedText.setText(TTLocalizer.BossBarGoonsStomped % self.goonsStomped)

    def updateStunCount(self, avId):
        if avId == base.localAvatar.doId:
            self.stunCount += 1
            self.stunCountText.setText(TTLocalizer.BossBarStuns % self.stunCount)
