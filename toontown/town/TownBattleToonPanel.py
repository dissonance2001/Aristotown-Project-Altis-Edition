from panda3d.core import *
from panda3d.direct import *
from toontown.battle.BattleGlobals import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownBattleGlobals import *
from direct.directnotify import DirectNotifyGlobal
import string
import math
from toontown.toon import LaffMeter
from toontown.toon import IOURegistry
from toontown.toon import NPCToons
from toontown.toon import ToonHead
from toontown.toon import ToonDNA
from toontown.battle import BattleBase
from toontown.toonbase import ToontownBattleGlobals
from direct.task.Task import Task
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from panda3d.direct import *
from toontown.toonbase import TTLocalizer

class ToonStatusInformationPanel(DirectFrame):
    def __init__(self, toon, statusEffects, closeCommand=None):
        DirectFrame.__init__(
            self,
            parent=aspect2d,
            relief=None
        )

        self.toon = toon
        self.statusEffects = statusEffects or []
        self.closeCommand = closeCommand

        self.statusCards = []
        self.showTrack = None

        tooltipGui = loader.loadModel(
            'phase_3.5/models/gui/battlegui/info_panels'
        )

        keybindsGui = loader.loadModel(
            'phase_3.5/models/gui/optionspage/keybinds_gui.bam'
        )

        self.background = DirectFrame(
            parent=self,
            relief=None,
            image=tooltipGui.find('**/info_panel_main_toon'),
            image_scale=(1, 1, 0.5),
            frameSize=(-0.485, 0.485, -0.235, 0.235)
        )

        # Stops clicks from passing through the panel.
        self.background['state'] = DGG.NORMAL

        self.titleText = DirectLabel(
            parent=self.background,
            relief=None,
            text=self._getToonName(),
            text_font=ToontownGlobals.getMinnieFont(),
            text_fg=(0.976, 0.788, 0.165, 1),
            text_shadow=(0, 0, 0, 1),
            text_scale=0.035,
            text_pos=(0, 0.203)
        )

        self.statusEffectsFrame = DirectScrolledFrame(
            parent=self.background,
            relief=None,

            frameSize=(-0.22, 0.25, -0.2315, 0.1425),
            canvasSize=(-0.22, 0.1, -0.0425, 0.048),

            pos=(0.226, 0, 0),

            scrollBarWidth=0.018,

            verticalScroll_relief=None,
            verticalScroll_thumb_relief=None,

            verticalScroll_thumb_image=tooltipGui.find(
                '**/scroll_thumb_toon'
            ),
            verticalScroll_thumb_image_scale=(0.25, 1, 0.125),

            verticalScroll_resizeThumb=False
        )

        self.statusEffectsFrame.horizontalScroll.hide()
        self.statusEffectsFrame.verticalScroll.incButton.hide()
        self.statusEffectsFrame.verticalScroll.decButton.hide()

        self.exitButton = DirectButton(
            parent=self.background,
            relief=None,
            image=(
                keybindsGui.find('**/button_neutral'),
                keybindsGui.find('**/button_click'),
                keybindsGui.find('**/button_highlight')
            ),
            pos=(0.46, 0, 0.21),
            scale=0.05,
            command=self.close
        )

        tooltipGui.removeNode()
        keybindsGui.removeNode()

        self.setBin('gui-popup', 200)

        self.rebuildStatusEffects()

    def _getToonName(self):
        if not self.toon:
            return 'Toon Information'

        try:
            return self.toon.getName()
        except:
            return 'Toon Information'

    def show(self):
        if self.showTrack:
            self.showTrack.finish()
            self.showTrack = None

        DirectFrame.show(self)

        self.showTrack = Sequence(
            LerpScaleInterval(
                self,
                0.2,
                2.2,
                startScale=0.02,
                blendType='easeInOut'
            ),
            LerpScaleInterval(
                self,
                0.09,
                2.0,
                blendType='easeInOut'
            )
        )

        self.showTrack.start()

    def rebuildStatusEffects(self, effects=None):
        if effects is not None:
            self.statusEffects = effects

        self._clearStatusCards()

        canvas = self.statusEffectsFrame.getCanvas()

        if not self.statusEffects:
            emptyLabel = DirectLabel(
                parent=canvas,
                relief=None,
                text='No status effects are active.',
                text_font=ToontownGlobals.getInterfaceFont(),
                text_fg=(0, 0, 0, 1),
                text_scale=0.025,
                text_wordwrap=16,
                pos=(0, 0, 0.02)
            )

            self.statusCards.append(emptyLabel)

            self.statusEffectsFrame['canvasSize'] = (
                -0.22,
                0.1,
                -0.0425,
                0.048
            )

            self.statusEffectsFrame.verticalScroll.hide()
            return

        for index, effectData in enumerate(self.statusEffects):
            card = self._createStatusCard(
                canvas,
                effectData,
                index
            )

            self.statusCards.append(card)

        self.statusEffectsFrame['canvasSize'] = (
            -0.22,
            0.1,
            -0.0425 + (len(self.statusEffects) - 1) * -0.095,
            0.048
        )

        if len(self.statusEffects) <= 4:
            self.statusEffectsFrame.verticalScroll.hide()
        else:
            self.statusEffectsFrame.verticalScroll.show()

        self.statusEffectsFrame.verticalScroll['value'] = 0

    def _createStatusCard(self, parent, effectData, index):
        isBuff = effectData.get('buff', True)

        tooltipGui = loader.loadModel(
            'phase_3.5/models/gui/battlegui/info_panels'
        )

        if isBuff:
            cardImage = tooltipGui.find(
                '**/info_panel_buff_toon'
            )
        else:
            cardImage = tooltipGui.find(
                '**/info_panel_debuff_toon'
            )

        if cardImage.isEmpty():
            if isBuff:
                cardImage = tooltipGui.find('**/tooltip_buff')
            else:
                cardImage = tooltipGui.find('**/tooltip_debuff')

        card = DirectFrame(
            parent=parent,
            relief=None,
            image=cardImage,
            image_scale=(1, 1, 0.25),
            pos=(0, 0, 0.003 + index * -0.095),
            scale=0.495
        )

        iconRoot = card.attachNewNode('toon-status-card-icon')
        iconRoot.setPos(-0.33, 0, 0.001)
        iconRoot.setScale(0.12)

        # Copy the original Toon status-slot background.
        sourceBackground = effectData.get('background')

        if (
                sourceBackground is not None
                and not sourceBackground.isEmpty()
        ):
            backgroundCopy = sourceBackground.copyTo(iconRoot)

            # Remove the original battle-panel transform.
            backgroundCopy.setPos(0, 0.01, 0)
            backgroundCopy.setHpr(0, 0, 0)
            backgroundCopy.setScale(1.25)
            backgroundCopy.show()

        # Copy the status icon, including attached turn-count text.
        sourceNode = effectData.get('node')

        if (
                sourceNode is not None
                and not sourceNode.isEmpty()
        ):
            iconCopy = sourceNode.copyTo(iconRoot)

            # Put it slightly in front of the background.
            iconCopy.setPos(0, -0.01, 0)
            iconCopy.setHpr(0, 0, 0)
            iconCopy.setScale(1.25)
            iconCopy.show()

        DirectLabel(
            parent=card,
            relief=None,
            text=effectData.get(
                'title',
                'Status Effect'
            ),
            text_font=ToontownGlobals.getMinnieFont(),
            text_fg=(0, 0, 0, 1),
            text_align=TextNode.ALeft,
            text_scale=0.052,
            text_wordwrap=12,
            pos=(-0.215, 0, 0.025)
        )

        DirectLabel(
            parent=card,
            relief=None,
            text=effectData.get(
                'description',
                'No description available.'
            ),
            text_font=ToontownGlobals.getInterfaceFont(),
            text_fg=(0.1, 0.1, 0.1, 1),
            text_align=TextNode.ALeft,
            text_scale=0.032,
            text_wordwrap=19,
            pos=(-0.215, 0, -0.016)
        )

        tooltipGui.removeNode()

        return card

    def _clearStatusCards(self):
        for node in self.statusCards:
            try:
                node.destroy()
            except:
                try:
                    node.removeNode()
                except:
                    pass

        self.statusCards = []

    def close(self):
        callback = self.closeCommand
        self.closeCommand = None

        self.destroy()

        if callback:
            callback()

    def destroy(self):
        if self.showTrack:
            self.showTrack.finish()
            self.showTrack = None

        self._clearStatusCards()

        DirectFrame.destroy(self)

        self.toon = None
        self.statusEffects = []
        self.closeCommand = None

class ToonStatusEffectTooltip(DirectFrame):
    def __init__(self, parent=None):
        DirectFrame.__init__(
            self,
            parent=parent,
            relief=None
        )

        self.showTrack = None

        tooltipGui = loader.loadModel(
            'phase_3.5/models/gui/battlegui/info_panels'
        )

        self.buffImage = tooltipGui.find('**/tooltip_buff')
        self.debuffImage = tooltipGui.find('**/tooltip_debuff')
        self.buffIcon = tooltipGui.find('**/buff_icon_toon')
        self.debuffIcon = tooltipGui.find('**/debuff_icon_toon')

        self.background = DirectFrame(
            parent=self,
            relief=None,
            image=self.buffImage,
            image_scale=(1, 1, 0.5),
            geom=self.buffIcon,
            geom_pos=(0, 0, 0.13),
            geom_scale=0.125
        )

        self.titleLabel = DirectLabel(
            parent=self.background,
            relief=None,
            pos=(0, 0, 0.039),
            text='',
            text_scale=0.053,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_fg=(0, 0, 0, 1),
            text_wordwrap=18
        )

        self.descriptionLabel = DirectLabel(
            parent=self.background,
            relief=None,
            pos=(0, 0, -0.01),
            text='',
            text_scale=0.0375,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_fg=(0, 0, 0, 1),
            text_wordwrap=23
        )

        tooltipGui.removeNode()

        self.setBin('gui-popup', 100)
        self.hide()

    def setEffect(self, title, description, isBuff=True):
        if isBuff:
            self.background['image'] = self.buffImage
            self.background['geom'] = self.buffIcon
        else:
            self.background['image'] = self.debuffImage
            self.background['geom'] = self.debuffIcon

        self.titleLabel['text'] = title
        self.descriptionLabel['text'] = description

    def show(self):
        if self.showTrack:
            self.showTrack.finish()
            self.showTrack = None

        DirectFrame.show(self)

        self.showTrack = Sequence(
            LerpScaleInterval(
                self,
                0.15,
                2.25,
                startScale=0.05,
                blendType='easeOut'
            ),
            LerpScaleInterval(
                self,
                0.08,
                2.0,
                blendType='easeInOut'
            )
        )
        self.showTrack.start()

    def destroy(self):
        if self.showTrack:
            self.showTrack.finish()
            self.showTrack = None

        DirectFrame.destroy(self)

class TownBattleToonPanel(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('TownBattleToonPanel')

    def __init__(self, id):
        if settings['newGui'] == True:
            gui = loader.loadModel('phase_3.5/models/gui/battle_gui_new')
        else:
            gui = loader.loadModel('phase_3.5/models/gui//battlegui/toon_panel')
        
        DirectFrame.__init__(self, relief=None)
        self.panelFrame = DirectFrame(
            parent=self,
            relief=None,
            image=gui.find('**/toon_panel_frame'),
            pos=(0, 0.1, 0),
            scale=1
        )
        self.panelFrame.setBin('fixed', 10)
        self.setScale(0.5)
        self.initialiseoptions(TownBattleToonPanel)
        self.status = None
        self.liquidated = None
        self.liquidatedText = None
        self.governaughtDamageUp = None
        self.toonStatusIconNodes = []
        self.toonStatusEffectTooltip = None
        self.hoveredToonStatusSlot = None
        self.toonStatusInformationPanel = None
        self.raisedAnte = None
        self.raisedAnteText = None
        self.govDamageText = None
        self.noDodge = None
        self.nodDodgeRoundsText = None
        self.cheer = None
        self.cheerRounds = None
        self.inkDrain = None
        self.inkDrainRoundsText = None
        self.inkDrainText = None
        self.gagBoost = None
        self.gagBoostText = None
        self.gagBoostRoundsText = None
        self.gagBan = None
        self.status2 = None
        self.status3 = None
        self.status4 = None
        self.status5 = None
        self.status6 = None
        self.status7 = None
        self.status8 = None
        self.attackIcon = None
        self.attackIcon1 = None
        self.attackIcon2 = None
        self.attackIcon3 = None
        self.attackIcon4 = None
        self.attackIcon5 = None
        self.attackIcon6 = None
        self.attackIcon7 = None
        self.attackIcon8 = None
        self.attackIcon9 = None
        self.status9 = None
        self.status10 = None
        self.collectCall = None
        self.collectCallRoundsText = None
        self.mandatoryToll = None
        self.mandatoryTollNumberText = None
        self.toonStatusOffset = 0
        self.toonStatusSlotColors = []
        self.toonStatusSlotPulses = []
        self.toonStatusSlotPulseTypes = []
        self.avatar = None
        self.groupDamageDown = None
        self.groupDamageDownText = None
        self.groupDamageDownRoundsText = None
        self.snapped = None
        self.snappedText = None
        self.snappedRoundsText = None
        self.bombed = None
        self.bombedText = None
        self.bombedRoundsText = None
        self.vulnerable = None
        self.vulnerableText = None
        self.vulnerableRoundsText = None
        self.encore = None
        self.encoreText = None
        self.winded = None
        self.windedText = None
        self.encoreRounds = None
        self.windedRounds = None
        self.damageDown = None
        self.damageDownRounds = None
        self.damageDownText = None
        self.damageUp = None
        self.damageUpRounds = None
        self.damageUpText = None
        self.confused = None
        self.confusedRounds = None
        self.hidden = None
        self.hiddenRounds = None
        self.markedWood = None
        self.markedWoodRounds = None
        self.markedWoodText = None
        self.damageOvertime = None
        self.damageOvertimeRounds = None
        self.cooldown = None
        self.cooldownRounds = None
        self.burned = None
        self.burnedRounds = None
        self.zapped = None
        self.zappedRounds = None
        self.choiceOrganicStage = None
        self.iouChoiceHead = None
        self.extraDamageTextLeft = DirectLabel(parent=self, relief=None, pos=(-0.275, 0.05, 0.25), text='', text_scale=0.1, text_fg=(0.871, 0.827, 1, 1), text_align=TextNode.ACenter, text_font=getSignFont())
        self.extraDamageTextMid = DirectLabel(parent=self, relief=None, pos=(0, 0.05, 0.35), text='', text_scale=0.1, text_fg=(0.871, 0.827, 1, 1), text_align=TextNode.ACenter, text_font=getSignFont())
        self.extraDamageTextRight = DirectLabel(parent=self, relief=None, pos=(0.275, 0.05, 0.25), text='', text_scale=0.1, text_fg=(0.871, 0.827, 1, 1), text_align=TextNode.ACenter, text_font=getSignFont())

        self.extraDamageTextLeft.hide()
        self.extraDamageTextMid.hide()
        self.extraDamageTextRight.hide()
        # self.extraDamageText = DirectLabel(parent=self, relief=None, pos=(0.3, 0.05, 0.25), text='', text_scale=0.08, text_fg=(0.871, 0.827, 1, 1), text_align=TextNode.ALeft, text_font=getSignFont())
        # self.extraDamageText.hide()
        # self.snapped = status.find('**/vulnerable_icon')
        # self.snapped.setPosHprScale(-0.25, 0, 0.03, -180, 0, 0, .125, .125, .125)
        # self.snapped.reparentTo(self)
        # self.snapped.hide()
        # self.vulnerable = status.find('**/broken_shield_icon')
        # self.vulnerable.setPosHprScale(0.22, 0, 0.03, -180, 0, 0, .125, .125, .125)
        # self.vulnerable.reparentTo(self)
        # self.vulnerable.hide()
        gagSelectGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
        toonPanelGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/toon_panel')
        self.sosText = DirectLabel(parent=self, relief=None, pos=(0.22, 0, 0.03), text=TTLocalizer.TownBattleToonSOS, text_fg=(0.176, 1, 0, 1), text_scale=0.1, text_font=getSignFont())
        self.sosText.hide()
        self.fireText = DirectLabel(parent=self, relief=None, pos=(0.22, 0, 0.03), text=TTLocalizer.TownBattleToonFire, text_fg=(1, 0, 0, 1), text_scale=0.1, text_font=getSignFont())
        self.fireText.hide()
        self.sueText = DirectLabel(parent=self, relief=None, pos=(0.22, 0, 0.03), text=TTLocalizer.TownBattleToonSue, text_fg=(0.75, 0.75, 0.95, 1), text_scale=0.1, text_font=getSignFont())
        self.sueText.hide()
        self.roundsText = DirectLabel(parent=self, relief=None, pos=(0, 0.05, 0.25), text='', text_scale=0.1, text_fg=(0.176, 1, 0, 1), text_font=getSignFont())
        self.roundsText.hide()
        self.damageText = DirectLabel(parent=self, relief=None, pos=(0, 0.05, 0.25), text='', text_scale=0.15, text_fg=(1, 0, 0, 1), text_font=getSignFont())
        self.damageText.hide()
        self.selfHealText = DirectLabel(parent=self, relief=None, pos=(0, 0.05, 0.25), text='', text_scale=0.15, text_fg=(0.176, 1, 0, 1), text_font=getSignFont())
        self.selfHealText.hide()
        self.exeDamageText = DirectLabel(parent=self, relief=None, pos=(0, 0.05, 0.25), text='', text_scale=0.15, text_fg=(1, 0, 0, 1), text_font=getSignFont())
        self.exeDamageText.hide()
        self.soakedRoundsText = DirectLabel(parent=self, relief=None, pos=(0, 0.05, 0.25), text='', text_scale=0.15, text_fg=(0.176, 1, 0, 1), text_font=getSignFont())
        self.soakedRoundsText.hide()
        self.soakedDamageText = DirectLabel(parent=self, relief=None, pos=(0, 0.05, 0.25), text='', text_scale=0.15, text_fg=(1, 0, 0, 1), text_font=getSignFont())
        self.soakedDamageText.hide()
        self.knockbackText = DirectLabel(parent=self, relief=None, pos=(0, 0.05, 0.25), text='', text_scale=0.15, text_fg=(1, 0, 0, 1), text_font=getSignFont())
        self.knockbackText.hide()
        self.undecidedText = DirectLabel(parent=self, relief=None, pos=(0.22, 0.05, -0.03), text=TTLocalizer.TownBattleUndecided, text_scale=0.3, text_fg=(1, 1, 1, 1), text_font=getSignFont())
        self.undecidedText.hide()
        self.passText = DirectLabel(parent=self, relief=None, pos=(0.2, 0, 0.03),
                                    text='', text_scale=0.1, text_fg=(1, 0, 0, 1), text_font=getSignFont())
        self.passText.hide()
        self.choiceRoot = self.attachNewNode('choiceRoot')
        self.choiceRoot.setPos(0, 0, 0)
        self.choicePanelModels = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
        self.choiceStatusModels = loader.loadModel('phase_3.5/models/gui/status_effects')

        self.choiceEmblem = DirectFrame(
            parent=self.choiceRoot,
            relief=None,
            image=self.choicePanelModels.find('**/emblem_gag'),
            pos=(0.21, 0, 0.075),
            scale=.5
        )
        self.choiceEmblem.setBin('gui-popup', 100)
        self.toonPanelFrame = DirectFrame(
            parent=self,
        relief=None
        )

        self.toonPanelBackground = DirectFrame(
            parent=self,
            relief=None,
            image=toonPanelGui.find('**/toon_panel_background')
        )
        #self.toonPanelBackground.reparentTo(aspect2d)
        self.toonPanelBackground.setBin('fixed', -100)
        self.toonPanelBorder = DirectFrame(
            parent=self,
            relief=None,
            image=toonPanelGui.find('**/toon_panel_frame')
        )

        self.laffMeterNode = DirectFrame(
            parent=self,
            relief=None
        )
        self.toonCycleBackButton = DirectButton(
        parent=self,
        relief=None,
        image=(
            toonPanelGui.find('**/arrow_neutral'),
            toonPanelGui.find('**/arrow_press'),
            toonPanelGui.find('**/arrow_hover')
        ),
            pos=(-0.384, 0, 0.175),
            scale=.15,
    command=self.changeToonStatusOffset,
    extraArgs=[-1]
    )

        self.toonCycleForwardButton = DirectButton(
        parent=self,
        relief=None,
        image=(
            toonPanelGui.find('**/arrow_neutral'),
            toonPanelGui.find('**/arrow_press'),
            toonPanelGui.find('**/arrow_hover')
        ),
            pos=(-0.082, 0, -0.205),
            scale=.15,
    command=self.changeToonStatusOffset,
    extraArgs=[1]
    )
        self.toonCycleBackButton.setR(-90)
        self.toonCycleBackButton['state'] = DGG.DISABLED
        self.toonCycleForwardButton['state'] = DGG.DISABLED
        self.infoButton = DirectButton(
        parent=self,
        relief=None,
        image=(
            toonPanelGui.find('**/info_neutral'),
            toonPanelGui.find('**/info_press'),
            toonPanelGui.find('**/info_hover')
        ),
            pos=(0, 0, -0.06),
            scale=.15, command=self.activateToonInfoButton
        )

        self.gagLock = DirectFrame(
            parent=self,
            relief=None,
            image=toonPanelGui.find('**/lock_unlocked'),
            pos=(0.345, 0, -0.04),
            scale=(0.13, 1, 0.26),
        )
        self.gagLocked = DirectFrame(
            parent=self,
            relief=None,
            image=toonPanelGui.find('**/lock_locked'),
            pos=(0.345, 0, -0.04),
            scale=(0.13, 1, 0.26),
        )
        self.gagLocked.hide()
        surrenderFlagImage = toonPanelGui.find('**/surrender_flag')
        if surrenderFlagImage.isEmpty():
            surrenderGui = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
            surrenderFlagImage = surrenderGui.find('**/tab_surrender_tab')
        self.surrenderFlag = DirectFrame(parent=self, relief=None, image=surrenderFlagImage, scale=0.3, frameSize=(-0.53, 0.4, -0.34, 0.34), pos=(-0.45, 0, 0.28))
        self.surrenderFlag.setBin('gui-popup', 1000)
        self.surrenderFlag.hide()
        self.surrenderSeq = None
        self.surrenderState = False
        self.choiceEmblem.hide()
        self.choiceOrganicTex = loader.loadTexture('phase_3.5/maps/battlegui/pres_scroll_bg.png')
        self.choiceOrganicTex.setWrapU(Texture.WMRepeat)
        self.choiceOrganicTex.setWrapV(Texture.WMRepeat)

        self.choiceOrganicStage = TextureStage('toon-panel-choice-organic')
        self.setChoiceOrganic(False)
        self.choiceOrganicIval = LerpFunctionInterval(
            self.updateChoiceOrganicScroll,
            duration=3.0,
            fromData=0.0,
            toData=1.0
        )
        self.choiceOrganicIval.loop()
        gagSelectGui.removeNode()
        toonPanelGui.removeNode()
        self.laffMeterNode.setPos(-0.15, 0, 0.06)
        self.laffMeterNode.setScale(1.1)
        self.undecidedIcon = DirectFrame(parent=self.choiceRoot, relief=None, image=self.choicePanelModels.find('**/emblem_question'), pos=(0.21, 0, 0.075), scale=.5)
        self.passIcon = DirectFrame(parent=self.choiceRoot, relief=None, image=self.choicePanelModels.find('**/pass_icon'), pos=(0.21, 0, 0.075), scale=.25)
        self.fireIcon = DirectFrame(parent=self.choiceRoot, relief=None, image=self.choiceStatusModels.find('**/pinkslip_icon'), pos=(0.21, 0, 0.075), scale=.25)
        self.sueIcon = DirectFrame(parent=self.choiceRoot, relief=None, image=self.choiceStatusModels.find('**/sued_icon'), pos=(0.21, 0, 0.05), scale=.25)
        self.sosIcon = DirectFrame(parent=self.choiceRoot, relief=None, image=self.choiceStatusModels.find('**/energized_icon'), pos=(0.21, 0, 0.075), scale=.25)
        self.undecidedIcon.show()
        self.undecidedIcon.setBin('fixed', 0)
        for icon in (self.passIcon, self.fireIcon, self.sueIcon, self.sosIcon):
            icon.setBin('fixed', 0)
            icon.hide()

        self.choiceEmblem.setBin('fixed', 0)
        self.hpChangeEvent = None
        self.gagNode = self.attachNewNode('gag')
        self.gagNode.setScale(2.0)
        self.hasGag = 0
        passGui = gui.find('**/lock_locked')
        passGui.detachNode()
        self.passNode = self.attachNewNode('pass')
        self.passNode.setPos(0.22, 0, -0.0)
        passGui.setScale(0.2)
        passGui.reparentTo(self.passNode)
        self.passNode.hide()
        self.laffMeter = None
        self.whichText = DirectLabel(parent=self, text='', pos=(0.22, 0.1, -0.23), text_scale=0.09, text_fg=(1, 1, 1, 1))
        self.iouChoiceName = DirectLabel(
            parent=self,
            relief=None,
            pos=(0, 0.05, 0.27),
            text='',
            text_align=TextNode.ACenter,
            text_scale=0.12,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_font=getSignFont()
        )
        self.iouChoiceName.hide()
        self.hide()
        self.toonStatusEffectTooltip = ToonStatusEffectTooltip(parent=self)
        self.toonStatusEffectTooltip.setPos(0, 0, 0.45)
        self.toonStatusEffectTooltip.setScale(2.0)
        self.toonStatusEffectTooltip.hide()
        gui.removeNode()

    def getColoredText(self, text, propertyName, color, font=None):
        manager = TextPropertiesManager.getGlobalPtr()

        properties = TextProperties()
        properties.setTextColor(
            color[0],
            color[1],
            color[2],
            color[3]
        )

        if font is not None:
            properties.setFont(font)

        manager.setProperties(propertyName, properties)

        return '\x01%s\x01%s\x02' % (propertyName, text)

    def activateToonInfoButton(self):
        if self.toonStatusInformationPanel:
            self.closeToonStatusInformationPanel()
            return

        if not self.avatar:
            return

        self.toonStatusInformationPanel = ToonStatusInformationPanel(
            toon=self.avatar,
            statusEffects=list(self.toonStatusIconNodes),
            closeCommand=self._toonInformationPanelClosed
        )

        self.toonStatusInformationPanel.show()


    def _toonInformationPanelClosed(self):
        self.toonStatusInformationPanel = None


    def closeToonStatusInformationPanel(self):
        panel = self.toonStatusInformationPanel
        self.toonStatusInformationPanel = None

        if panel:
            try:
                panel.destroy()
            except:
                pass

    def setChoiceOrganic(self, organic):
        if not getattr(self, 'choiceOrganicStage', None):
            return

        if not getattr(self, 'choiceEmblem', None):
            return

        imageNode = self.choiceEmblem.component('image0')

        if organic:
            imageNode.setTexture(self.choiceOrganicStage, self.choiceOrganicTex, 1)
            imageNode.setTexScale(self.choiceOrganicStage, 6, 6)
            imageNode.setTransparency(1)
        else:
            imageNode.clearTexture(self.choiceOrganicStage)


    def updateChoiceOrganicScroll(self, t):
        if not getattr(self, 'choiceEmblem', None):
            return

        if getattr(self.choiceEmblem, 'isEmpty', None) and self.choiceEmblem.isEmpty():
            return

        if not getattr(self, 'choiceOrganicStage', None):
            return

        try:
            imageNode = self.choiceEmblem.component('image0')
        except:
            return

        imageNode.setTexOffset(self.choiceOrganicStage, t, -t)

    def hideChoiceIcons(self):
        self.__clearIOUChoiceHead()
        self.iouChoiceName.hide()
        self.choiceEmblem.hide()
        self.undecidedIcon.hide()
        self.passIcon.hide()
        self.fireIcon.hide()
        self.sueIcon.hide()
        self.sosIcon.hide()

    def __clearIOUChoiceHead(self):
        if self.iouChoiceHead:
            self.iouChoiceHead.detachNode()
            self.iouChoiceHead.delete()
            self.iouChoiceHead = None

    def __createIOUChoiceHead(self, npcId, dimension):
        npcInfo = NPCToons.NPCToonDict[npcId]
        dnaList = npcInfo[2]
        gender = npcInfo[3]
        if dnaList == 'r':
            dnaList = NPCToons.getRandomDNA(npcId, gender)
        dna = ToonDNA.ToonDNA()
        dna.newToonFromProperties(*dnaList)
        head = ToonHead.ToonHead()
        head.setupHead(dna, forGui=1)
        p1 = Point3()
        p2 = Point3()
        head.calcTightBounds(p1, p2)
        t = p1[0]
        p1.setX(-p2[0])
        p2.setX(-t)
        d = p2 - p1
        biggest = max(d[0], d[2])
        scale = dimension / biggest
        mid = (p1 + d / 2.0) * scale
        geomXform = hidden.attachNewNode('iouChoiceHeadXform')
        for child in head.getChildren():
            child.reparentTo(geomXform)
        geomXform.setPosHprScale(-mid[0], -mid[1] + 1, -mid[2], 180, 0, 0, scale, scale, scale)
        geomXform.reparentTo(head)
        return head

    def showChoiceIcon(self, icon, color, organic=False):
        self.hideChoiceIcons()
        self.choiceEmblem['image_color'] = color
        self.setChoiceOrganic(organic)
        self.choiceEmblem.show()
        icon.show()

    def _attachToonStatusIcon(
            self,
            iconNode,
            slot,
            tooltipKey=None,
            tooltipTitle=None,
            tooltipDescription=None,
            tooltipBuff=True,
            slotColor=(1, 1, 1, 1),
            scale=(1, 1, 1)):

        if slot is None or iconNode is None or iconNode.isEmpty():
            return

        if isinstance(scale, (int, float)):
            scale = (scale, scale, scale)

        sx, sy, sz = scale

        slot['bg'].setColor(*slotColor)
        slot['bg'].setColorScale(1, 1, 1, 1)
        slotIndex = self.toonStatusSlots.index(slot)

        if slotIndex < 4:
            slot['bg'].show()
            slot['iconRoot'].show()
            slot['hoverButton'].show()
        else:
            slot['bg'].hide()
            slot['iconRoot'].hide()
            slot['hoverButton'].hide()

        iconNode.reparentTo(slot['iconRoot'])
        iconNode.setPosHprScale(
            0, 0, 0,
            0, 0, 0,
            sx, sy, sz
        )
        iconNode.setColor(1, 1, 1, 1)
        iconNode.setColorScale(1, 1, 1, 1)
        iconNode.show()

        effectData = {
            'node': iconNode,

            # Keep the original status-slot background.
            'background': slot['bg'],
            'slotColor': slotColor,

            'tooltipKey': tooltipKey,
            'title': tooltipTitle or self._formatToonStatusName(tooltipKey),
            'description': tooltipDescription or 'No description available.',
            'buff': tooltipBuff
        }

        self.toonStatusIconNodes.append(effectData)
        self.toonStatusSlotColors.append(slotColor)
        self.toonStatusSlotPulses.append(None)
        self.toonStatusSlotPulseTypes.append(None)

        # The slot initially corresponds to the effect just added.
        slot['effectIndex'] = len(self.toonStatusIconNodes) - 1

    def _formatToonStatusName(self, name):
        if not name:
            return 'Status Effect'

        result = ''

        for character in name:
            if character.isupper() and result:
                result += ' '

            result += character

        return result[:1].upper() + result[1:]

    def _clear_toon_status_interval(self, attrName):
        interval = getattr(self, attrName, None)
        if interval is not None:
            try:
                interval.finish()
            except:
                pass
            setattr(self, attrName, None)

    def _clear_toon_status_node(self, attrName):
        node = getattr(self, attrName, None)
        if node is not None:
            try:
                node.removeNode()
            except:
                pass
            setattr(self, attrName, None)

    def _cleanupToonStatusDisplay(self):
        self.toonStatusOffset = 0
        self.toonStatusIconNodes = []
        self.toonStatusSlotColors = []
        self.toonStatusSlotPulses = []
        self.toonStatusSlotPulseTypes = []

        if self.toonStatusEffectTooltip:
            self.toonStatusEffectTooltip.hide()

        self.hoveredToonStatusSlot = None
        self._clear_toon_status_interval('pulseTask')
        self._clear_toon_status_interval('rainbowPulseTask')

        if hasattr(self, 'toonStatusSlots'):
            for slot in self.toonStatusSlots:
                if not slot:
                    continue

                pulse = slot.get('pulse')
                if pulse:
                    try:
                        pulse.finish()
                    except:
                        pass
                    slot['pulse'] = None

                hoverButton = slot.get('hoverButton')
                if hoverButton:
                    try:
                        hoverButton.destroy()
                    except:
                        pass
                    slot['hoverButton'] = None

                bgNode = slot.get('bg')
                if bgNode and not bgNode.isEmpty():
                    try:
                        bgNode.removeNode()
                    except:
                        pass
                    slot['bg'] = None

                iconRoot = slot.get('iconRoot')
                if iconRoot and not iconRoot.isEmpty():
                    try:
                        iconRoot.removeNode()
                    except:
                        pass
                    slot['iconRoot'] = None

                bgModel = slot.get('bgModel')
                if bgModel and not bgModel.isEmpty():
                    try:
                        bgModel.removeNode()
                    except:
                        pass
                    slot['bgModel'] = None

        for name in (
                'gagBoost', 'gagBoostRoundsText', 'gagBoostText',
                'collectCall', 'collectCallRoundsText',
                'noDodge', 'nodDodgeRoundsText',
                'mandatoryToll', 'mandatoryTollNumberText',
                'attackIcon', 'attackIcon1', 'attackIcon2', 'attackIcon3',
                'attackIcon4', 'attackIcon5', 'attackIcon6', 'attackIcon7',
                'status', 'status2', 'status3', 'status4', 'attackIcon8', 'attackIcon9',
                'status5', 'status6', 'status7', 'status8', 'status9', 'status10',
                'encore', 'govDamageText', 'governaughtDamageUp', 'encoreRounds', 'toonupGagBoost', 'trapGagBoost', 'lureGagBoost', 'throwGagBoost', 'squirtGagBoost', 'soundGagBoost', 'dropGagBoost', 'zapGagBoost',
                'winded', 'gagBan', 'raisedAnte', 'raisedAnteText',
                'windedRounds', 'damageUpRounds', 'damageUp',
                'cheerRounds', 'cheer', 'burnedRounds', 'burned', 'zapped', 'zappedRounds', 'extraText', 'statusIcon', 'statusIcon2',
                'liquidatedText', 'liquidated', 'damageDownRounds',
                'damageDown', 'groupDamageDown', 'groupDamageDownText',
                'groupDamageDownRoundsText', 'bombed', 'bombedText',
                'bombedRoundsText', 'damageOvertime', 'damageOvertimeRounds',
                'cooldown', 'cooldownRounds', 'confused', 'confusedRounds',
                'hidden', 'hiddenRounds', 'markedWood', 'markedWoodRounds',
                'markedWoodText', 'inkDrain', 'inkDrainRoundsText',
                'inkDrainText', 'snapped', 'snappedText', 'snappedRoundsText',
                'vulnerable', 'vulnerableText', 'vulnerableRoundsText',
                'damageDownText', 'encoreText', 'windedText', 'damageUpText'
        ):
            self._clear_toon_status_node(name)

        if hasattr(self, 'toonStatusSlots'):
            for slot in self.toonStatusSlots:
                try:
                    slot['bgModel'].removeNode()
                except:
                    pass
                try:
                    slot['iconRoot'].removeNode()
                except:
                    pass

        self.toonStatusSlots = []
        self.statusEffects = 0

    def _claimNextToonStatusSlot(self):
        if self.statusEffects >= len(self.toonStatusSlots):
            i = len(self.toonStatusSlots)
            x, y, z = (0, 0, -0.355)

            bgModel = loader.loadModel('phase_3.5/models/gui/status_effects')
            bgNode = bgModel.find('**/default_background')
            bgNode.reparentTo(self)
            bgNode.setPosHprScale(x, y, z, 0, 0, 0, .13, .13, .13)
            bgNode.setColor(0.525, 0.133, 0.122, 1)
            bgNode.hide()

            iconRoot = self.attachNewNode('toonStatusIconRoot-%d' % i)
            iconRoot.setPosHprScale(x, y, z, 0, 0, 0, .12, .12, .12)
            iconRoot.hide()

            hoverButton = DirectButton(
                parent=self,
                relief=DGG.FLAT,
                frameColor=(0, 0, 0, 0),
                frameSize=(-0.5, 0.5, -0.5, 0.5),
                pos=(x, -0.05, z),
                scale=0.125,
                state=DGG.NORMAL
            )
            hoverButton.bind(
                DGG.WITHIN,
                self._enterToonStatusSlot,
                extraArgs=[i]
            )
            hoverButton.bind(
                DGG.WITHOUT,
                self._exitToonStatusSlot,
                extraArgs=[i]
            )
            hoverButton.hide()

            self.toonStatusSlots.append({
                'bgModel': bgModel,
                'bg': bgNode,
                'iconRoot': iconRoot,
                'hoverButton': hoverButton,
                'effectIndex': None,
                'pulse': None,
            })

        slot = self.toonStatusSlots[self.statusEffects]
        self.statusEffects += 1

        if self.statusEffects > 4:
            slot['bg'].hide()
            slot['iconRoot'].hide()
            slot['hoverButton'].hide()

        return slot

    def _stopToonStatusPulse(self, slot):
        if slot is None:
            return

        pulse = slot.get('pulse')
        if pulse is not None:
            try:
                pulse.finish()
            except:
                pass
            slot['pulse'] = None

        slot['bg'].setColorScale(1, 1, 1, 1)

    def _pulseToonStatusSlot(self, slot, fromColor,
                                toColor=(1, 1, 1, 1), duration=1.0):
            if slot is None:
                return

            index = self.statusEffects - 1

            if 0 <= index < len(self.toonStatusSlotPulses):
                self.toonStatusSlotPulseTypes[index] = 'normal'
                self.toonStatusSlotPulses[index] = (
                    fromColor,
                    toColor,
                    duration
                )

            self._pulseToonStatusSlotVisible(
                slot,
                fromColor,
                toColor,
                duration
            )

    def _pulseRainbowToonStatusSlot(self, slot, duration=0.35):
        if slot is None:
            return

        index = self.statusEffects - 1

        if 0 <= index < len(self.toonStatusSlotPulses):
            self.toonStatusSlotPulseTypes[index] = 'rainbow'
            self.toonStatusSlotPulses[index] = (duration,)

        self._pulseRainbowToonStatusSlotVisible(slot, duration)

    def _pulseRainbowToonStatusSlotVisible(self, slot, duration=0.35):
        self._stopToonStatusPulse(slot)

        slot['pulse'] = Sequence(
            LerpColorScaleInterval(slot['bg'], duration, (1, 0, 0, 1)),
            LerpColorScaleInterval(slot['bg'], duration, (1, 0.5, 0, 1)),
            LerpColorScaleInterval(slot['bg'], duration, (1, 1, 0, 1)),
            LerpColorScaleInterval(slot['bg'], duration, (0, 1, 0, 1)),
            LerpColorScaleInterval(slot['bg'], duration, (0, 0, 1, 1)),
            LerpColorScaleInterval(slot['bg'], duration, (0.29, 0, 0.51, 1)),
            LerpColorScaleInterval(slot['bg'], duration, (0.56, 0, 1, 1))
        )
        slot['pulse'].loop()

    def _pulseToonStatusSlotVisible(
            self,
            slot,
            fromColor,
            toColor=(1, 1, 1, 1),
            duration=1.0):

        self._stopToonStatusPulse(slot)

        slot['pulse'] = Sequence(
            LerpColorScaleInterval(
                slot['bg'],
                duration,
                fromColor,
                blendType='easeInOut'
            ),
            LerpColorScaleInterval(
                slot['bg'],
                duration,
                toColor,
                blendType='easeInOut'
            ),
            Wait(1.0)
        )
        slot['pulse'].loop()

    def _applyToonStatusOffset(self):
        visibleSlots = 4

        if self.toonStatusEffectTooltip:
            self.toonStatusEffectTooltip.hide()

        self.hoveredToonStatusSlot = None

        for slotIndex in xrange(visibleSlots):
            slot = self.toonStatusSlots[slotIndex]

            self._stopToonStatusPulse(slot)

            slot['bg'].show()
            slot['bg'].setColor(0.525, 0.133, 0.122, 1)
            slot['bg'].setColorScale(1, 1, 1, 1)

            slot['iconRoot'].show()
            slot['hoverButton'].show()
            slot['effectIndex'] = None

            for child in slot['iconRoot'].getChildren():
                child.detachNode()

        for slotIndex in xrange(visibleSlots):
            effectIndex = self.toonStatusOffset + slotIndex

            if effectIndex >= len(self.toonStatusIconNodes):
                continue

            effectData = self.toonStatusIconNodes[effectIndex]
            icon = effectData.get('node')

            if icon is None or icon.isEmpty():
                continue

            slot = self.toonStatusSlots[slotIndex]

            icon.reparentTo(slot['iconRoot'])
            icon.setPos(0, 0, 0)
            icon.show()

            slot['effectIndex'] = effectIndex

            if effectIndex < len(self.toonStatusSlotColors):
                slot['bg'].setColor(
                    *self.toonStatusSlotColors[effectIndex]
                )

            pulseType = self.toonStatusSlotPulseTypes[effectIndex]
            pulseData = self.toonStatusSlotPulses[effectIndex]

            if pulseType == 'normal' and pulseData:
                fromColor, toColor, duration = pulseData

                self._pulseToonStatusSlotVisible(
                    slot,
                    fromColor,
                    toColor,
                    duration
                )

            elif pulseType == 'rainbow' and pulseData:
                self._pulseRainbowToonStatusSlotVisible(
                    slot,
                    pulseData[0]
                )

        maxOffset = max(
            0,
            len(self.toonStatusIconNodes) - visibleSlots
        )

        if maxOffset > 0:

            self.toonCycleBackButton['state'] = (
                DGG.NORMAL
                if self.toonStatusOffset > 0
                else DGG.DISABLED
            )

            self.toonCycleForwardButton['state'] = (
                DGG.NORMAL
                if self.toonStatusOffset < maxOffset
                else DGG.DISABLED
            )
        else:
            self.toonCycleBackButton['state'] = DGG.DISABLED
            self.toonCycleForwardButton['state'] = DGG.DISABLED

    def changeToonStatusOffset(self, amount):
        maxOffset = max(
            0,
            len(self.toonStatusIconNodes) - 4
        )

        newOffset = self.toonStatusOffset + amount
        newOffset = max(0, min(newOffset, maxOffset))

        if newOffset != self.toonStatusOffset:
            self.toonStatusOffset = newOffset
            self._applyToonStatusOffset()

    def _buildToonStatusSlots(self):
        slotLayouts = [
            (-0.39, 0, 0.083),  # 1
            (-0.374, 0, -0.044),  # 2
            (-0.294, 0, -0.147),  # 3
            (-0.175, 0, -0.195),  # 4
            (0.12, 0, -0.355),  # 5
            (0.24, 0, -0.355),  # 6
            (0.36, 0, -0.355), # 7
            (0.48, 0, -0.355),# 8
            (-0.12, 0, -0.355),  # 9
            (0, 0, -0.355),  # 10
        ]

        self.toonStatusSlots = [None] * len(slotLayouts)

        for i in reversed(range(len(slotLayouts))):
            x, y, z = slotLayouts[i]

            bgModel = loader.loadModel('phase_3.5/models/gui/status_effects')
            bgNode = bgModel.find('**/default_background')
            bgNode.reparentTo(self)
            bgNode.setPosHprScale(x, y, z, 0, 0, 0, .13, .13, .13)
            bgNode.setColor(0.525, 0.133, 0.122, 1)

            iconRoot = self.attachNewNode('toonStatusIconRoot-%d' % i)
            iconRoot.setPosHprScale(x, y, z, 0, 0, 0, .12, .12, .12)


            hoverButton = DirectButton(
                parent=self,
                relief=DGG.FLAT,
                frameColor=(0, 0, 0, 0),
                frameSize=(-0.5, 0.5, -0.5, 0.5),
                pos=(x, -0.05, z),
                scale=0.125,
                state=DGG.NORMAL
            )

            hoverButton.bind(
                DGG.WITHIN,
                self._enterToonStatusSlot,
                extraArgs=[i]
            )

            hoverButton.bind(
                DGG.WITHOUT,
                self._exitToonStatusSlot,
                extraArgs=[i]
            )

            self.toonStatusSlots[i] = {
                'bgModel': bgModel,
                'bg': bgNode,
                'iconRoot': iconRoot,
                'hoverButton': hoverButton,
                'effectIndex': None,
                'pulse': None,
            }
            if i >= 4:
                bgNode.hide()
                iconRoot.hide()
                hoverButton.hide()

        # # backward compatibility names
        # self.status = self.toonStatusSlots[0]['bgModel']
        # self.status2 = self.toonStatusSlots[1]['bgModel']
        # self.status3 = self.toonStatusSlots[2]['bgModel']
        # self.status4 = self.toonStatusSlots[3]['bgModel']
        # self.status5 = self.toonStatusSlots[4]['bgModel']
        # self.status6 = self.toonStatusSlots[5]['bgModel']
        # self.status7 = self.toonStatusSlots[6]['bgModel']
        # self.status8 = self.toonStatusSlots[7]['bgModel']
        # self.status9 = self.toonStatusSlots[8]['bgModel']
        # self.status10 = self.toonStatusSlots[9]['bgModel']

        # self.attackIcon = self.toonStatusSlots[0]['bg']
        # self.attackIcon1 = self.toonStatusSlots[1]['bg']
        # self.attackIcon2 = self.toonStatusSlots[2]['bg']
        # self.attackIcon3 = self.toonStatusSlots[3]['bg']
        # self.attackIcon4 = self.toonStatusSlots[4]['bg']
        # self.attackIcon5 = self.toonStatusSlots[5]['bg']
        # self.attackIcon6 = self.toonStatusSlots[6]['bg']
        # self.attackIcon7 = self.toonStatusSlots[7]['bg']
        # self.attackIcon8 = self.toonStatusSlots[8]['bg']
        # self.attackIcon9 = self.toonStatusSlots[9]['bg']

    def _enterToonStatusSlot(self, slotIndex, event=None):
        if not self.toonStatusEffectTooltip:
            return

        if slotIndex < 0 or slotIndex >= len(self.toonStatusSlots):
            return

        slot = self.toonStatusSlots[slotIndex]
        effectIndex = slot.get('effectIndex')

        if effectIndex is None:
            self.toonStatusEffectTooltip.hide()
            return

        if effectIndex < 0 or effectIndex >= len(self.toonStatusIconNodes):
            self.toonStatusEffectTooltip.hide()
            return

        effectData = self.toonStatusIconNodes[effectIndex]

        self.toonStatusEffectTooltip.setEffect(
            effectData.get('title', 'Status Effect'),
            effectData.get('description', 'No description available.'),
            effectData.get('buff', True)
        )

        self.hoveredToonStatusSlot = slotIndex
        self.toonStatusEffectTooltip.show()


    def _exitToonStatusSlot(self, slotIndex, event=None):
        if self.hoveredToonStatusSlot != slotIndex:
            return

        self.hoveredToonStatusSlot = None

        if self.toonStatusEffectTooltip:
            self.toonStatusEffectTooltip.hide()

    def _getBattleConditionsForToon(self, avatar):
        conditions = getattr(avatar, 'battleConditions', None)
        if conditions is None and avatar == base.localAvatar:
            conditions = getattr(base.localAvatar, 'battleConditions', None)
        return conditions or {}

    def _attachIOUBattleStatusEffects(self, avatar):
        conditions = self._getBattleConditionsForToon(avatar)
        bestByTrack = {}
        for conditionName, conditionData in conditions.items():
            parsed = IOURegistry.parseConditionName(conditionName)
            if parsed is None or len(conditionData) < 2:
                continue
            gagTrack, boost = parsed
            uses = conditionData[1]
            if uses is None or uses <= 0:
                continue
            current = bestByTrack.get(gagTrack)
            if current is None or boost > current[0]:
                bestByTrack[gagTrack] = (boost, uses)

        for gagTrack in sorted(bestByTrack.keys()):
            boost, uses = bestByTrack[gagTrack]
            iconRoot = NodePath('iouStatusIconRoot')
            if gagTrack == -1:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                icon = status.find('**/toon_damage_up_icon')
                icon.reparentTo(iconRoot)
            else:
                inventory = getattr(base.localAvatar, 'inventory', None)
                if inventory is not None and hasattr(inventory, 'invModels') and gagTrack < len(inventory.invModels) and len(inventory.invModels[gagTrack]) > 6:
                    icon = inventory.invModels[gagTrack][6].copyTo(iconRoot)
                    icon.setScale(5)
                else:
                    status = loader.loadModel('phase_3.5/models/gui/status_effects')
                    icon = status.find('**/toon_damage_up_icon')
                    icon.reparentTo(iconRoot)
            # DirectLabel(
            #     parent=iconRoot,
            #     relief=None,
            #     text='%s' % uses,
            #     text_fg=(1, 1, 1, 1),
            #     text_shadow=(0, 0, 0, 1),
            #     text_font=ToontownGlobals.getInterfaceFont(),
            #     text_bg=Vec4(0, 0, 0, 0),
            #     pos=(0.25, 0, -0.45),
            #     text_scale=0.6
            # )
            slot = self._claimNextToonStatusSlot()
            manager = TextPropertiesManager.getGlobalPtr()
            boostProperties = TextProperties()
            boostProperties.setTextColor(0.176, 1.0, 0.0, 1.0)
            manager.setProperties('iouTooltipBoost', boostProperties)
            boostText = '\x01iouTooltipBoost\x01+%d\x02' % boost
            plural = '' if uses == 1 else 's'
            if gagTrack == -1:
                title = 'Global IOU'
                gagText = 'Gag'
            else:
                trackName = IOURegistry.getTrackName(gagTrack)
                title = '%s IOU' % trackName
                trackColor = TrackColors[gagTrack]
                trackProperties = TextProperties()
                trackProperties.setTextColor(trackColor[0], trackColor[1], trackColor[2], 1.0)
                trackProperties.setFont(getSignFont())
                propertyName = 'iouTooltipTrack%d' % gagTrack
                manager.setProperties(propertyName, trackProperties)
                gagText = '\x01%s\x01%s\x02 Gag' % (propertyName, trackName)
            if gagTrack == HEAL_TRACK:
                description = 'The next %d %s%s will restore %s more Laff.' % (uses, gagText, plural, boostText)
            elif gagTrack == LURE_TRACK:
                description = 'The next %d %s%s will deal %s more knockback damage.' % (uses, gagText, plural, boostText)
            else:
                description = 'The next %d %s%s will deal %s more damage.' % (uses, gagText, plural, boostText)
            self._attachToonStatusIcon(
                iconRoot,
                slot,
                tooltipTitle=title,
                tooltipDescription=description,
                tooltipBuff=True,
                slotColor=(1, 0.984, 0, 1)
            )

        cooldownTurns = 0
        for conditionName in ('noSOS', 'noFires', 'noSues', 'noUnites', 'noForges'):
            conditionData = conditions.get(conditionName)
            if conditionData is None or len(conditionData) < 2:
                continue
            turns = conditionData[1]
            if turns is not None:
                cooldownTurns = max(cooldownTurns, turns)

        if cooldownTurns > 0 and not avatar.hasToonStatusEffect('cooldown'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            icon = status.find('**/reward_cooldown_icon')
            if icon.isEmpty():
                icon = status.find('**/unite_cooldown_icon')
            iconRoot = NodePath('rewardCooldownIconRoot')
            icon.reparentTo(iconRoot)
            DirectLabel(
                parent=iconRoot,
                relief=None,
                text='%s' % cooldownTurns,
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                text_font=ToontownGlobals.getInterfaceFont(),
                text_bg=Vec4(0, 0, 0, 0),
                pos=(0.25, 0, -0.45),
                text_scale=0.6
            )
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(
                iconRoot,
                slot,
                tooltipTitle='Reward Cooldown',
                tooltipDescription='Boss Rewards cannot be used for %d more round%s.' % (cooldownTurns, '' if cooldownTurns == 1 else 's'),
                tooltipBuff=False,
                slotColor=(0, 0.902, 1, 1)
            )

    def setStatusEffects(self, avatar):
        self.avatar = avatar
        self._cleanupToonStatusDisplay()
        self._buildToonStatusSlots()
        self._attachIOUBattleStatusEffects(avatar)

        if avatar.hasToonStatusEffect('raisedAnte'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/raise_the_ante_icon')
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Raising The Ante', 
                                   tooltipDescription="The stakes are much higher, and so are your Gag damage! Gags are +%s%% more powerful." % avatar.getToonStatusModifier('raisedAnte'), 
                                   tooltipBuff=True, 
                                   slotColor=(1, 1, 1, 1))
            self.rainbowPulseTask = self._pulseRainbowToonStatusSlot(slot, duration=2.0)

        if avatar.hasToonStatusEffect('hydrated'):
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.statusIcon = status.find('**/inventory_glass_of_water')
            iconRoot = NodePath('hydratedIconRoot')

            self.statusIcon.reparentTo(iconRoot)
            self.statusIcon.setScale(5.5)

            self.extraText = DirectLabel(
                parent=iconRoot,
                relief=None,
                text="%s" % avatar.getToonStatusTurns('hydrated'),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                text_font=ToontownGlobals.getInterfaceFont(),
                text_bg=Vec4(0, 0, 0, 0),
                pos=(0.25, 0, -0.45),
                text_scale=0.6
            )

            slot = self._claimNextToonStatusSlot()

            self._attachToonStatusIcon(
                iconRoot,
                slot,
                tooltipTitle='Hydrated',
                tooltipDescription="This Toon is Hydrated, and their Gag accuracy is increased by 20%",
                tooltipBuff=True,
                slotColor=(1, 0.984, 0, 1),
                scale=(1, 1, 1)
            )

        if avatar.hasToonStatusEffect('energized'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/energized_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('energized'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Energized', 
                                   tooltipDescription="This Toon's Gags will deal +50% damage, but will take 15% more damage from Cog attacks!", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if avatar.hasToonStatusEffect('damageUpGov'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/toon_damage_up_icon')
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Advanced Boost', 
                                   tooltipDescription="This Toon's Gags will deal +%s%% more damage." % avatar.getToonStatusModifier('damageUpGov'),  
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if avatar.hasToonStatusEffect('damageUp'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/toon_damage_up_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('damageUp'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            damageText = self.getColoredText(
                '+%s%%' % avatar.getToonStatusModifier('damageUp'),
                'positiveText',
                (0, 1, 0.016, 1),
                ToontownGlobals.getInterfaceFont()
            )
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Damage Up', 
                                   tooltipDescription="This Toon's Gags will deal %s more damage." % damageText,  
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if avatar.hasToonStatusEffect('bombedDamage'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/trap_card_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('bombedDamage'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Hot Take', 
                                   tooltipDescription="This Toon is dealing +%s%% more damage." % avatar.getToonStatusModifier('bombedDamage'), 
                                   tooltipBuff=True, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('viralSensation'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/singing_blues_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('viralSensation'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Viral Sensation', 
                                   tooltipDescription="This Toon's Gags will deal +%s%% more damage." % avatar.getToonStatusModifier('viralSensation'),  
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))
            
        if avatar.hasToonStatusEffect('toonupBoost'):
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.statusIcon = status.find('**/inventory_cannon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('toonupBoost'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Toon-Up Boost', 
                                   tooltipDescription="This Toon's TOON-UP Gags will deal +%s%% more damage." % avatar.getToonStatusModifier('toonupBoost'),  
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if avatar.hasToonStatusEffect('trapBoost'):
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.statusIcon = status.find('**/inventory_wreckingball')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('trapBoost'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Trap Boost', 
                                   tooltipDescription="This Toon's TRAP Gags will deal +%s%% more damage." % avatar.getToonStatusModifier('trapBoost'),  
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if avatar.hasToonStatusEffect('lureBoost'):
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.statusIcon = status.find('**/inventory_hypno_goggles')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('lureBoost'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Lure Boost', 
                                   tooltipDescription="This Toon's LURE Gags will deal +%s%% more damage." % avatar.getToonStatusModifier('lureBoost'),  
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if avatar.hasToonStatusEffect('throwBoost'):
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.statusIcon = status.find('**/inventory_cake')
            iconRoot = NodePath('hydratedIconRoot')

            self.statusIcon.reparentTo(iconRoot)
            self.statusIcon.setScale(5.5)

            self.extraText = DirectLabel(
                parent=iconRoot,
                relief=None,
                text="%s" % avatar.getToonStatusTurns('throwBoost'),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                text_font=ToontownGlobals.getInterfaceFont(),
                text_bg=Vec4(0, 0, 0, 0),
                pos=(0.25, 0, -0.45),
                text_scale=0.6
            )

            slot = self._claimNextToonStatusSlot()

            self._attachToonStatusIcon(
                iconRoot,
                slot,
                tooltipTitle='Throw Boost', 
                tooltipDescription="This Toon's THROW Gags will deal +%s%% more damage." % avatar.getToonStatusModifier('throwBoost'),  
                tooltipBuff=True,
                slotColor=(1, 0.984, 0, 1),
                scale=(1, 1, 1)
            )

        if avatar.hasToonStatusEffect('squirtBoost'):
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.statusIcon = status.find('**/inventory_storm_cloud')
            iconRoot = NodePath('hydratedIconRoot')
            
            self.statusIcon.reparentTo(iconRoot)
            self.statusIcon.setScale(5.5)

            self.extraText = DirectLabel(
                parent=iconRoot,
                relief=None,
                text="%s" % avatar.getToonStatusTurns('squirtBoost'),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                text_font=ToontownGlobals.getInterfaceFont(),
                text_bg=Vec4(0, 0, 0, 0),
                pos=(0.25, 0, -0.45),
                text_scale=0.6
            )

            slot = self._claimNextToonStatusSlot()

            self._attachToonStatusIcon(
                iconRoot,
                slot,
                tooltipTitle='Squirt Boost', 
                tooltipDescription="This Toon's SQUIRT Gags will deal +%s%% more damage." % avatar.getToonStatusModifier('squirtBoost'),  
                tooltipBuff=True,
                slotColor=(1, 0.984, 0, 1),
                scale=(1, 1, 1)
            )

        if avatar.hasToonStatusEffect('zapBoost'):
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.statusIcon = status.find('**/inventory_tesla_coil')
            iconRoot = NodePath('hydratedIconRoot')
                        
            self.statusIcon.reparentTo(iconRoot)
            self.statusIcon.setScale(5.5)

            self.extraText = DirectLabel(
                parent=iconRoot,
                relief=None,
                text="%s" % avatar.getToonStatusTurns('zapBoost'),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                text_font=ToontownGlobals.getInterfaceFont(),
                text_bg=Vec4(0, 0, 0, 0),
                pos=(0.25, 0, -0.45),
                text_scale=0.6
            )

            slot = self._claimNextToonStatusSlot()

            self._attachToonStatusIcon(
                iconRoot,
                slot,
                tooltipTitle='Zap Boost', 
                tooltipDescription="This Toon's ZAP Gags will deal +%s%% more damage." % avatar.getToonStatusModifier('zapBoost'),  
                tooltipBuff=True,
                slotColor=(1, 0.984, 0, 1),
                scale=(1, 1, 1)
            )

        if avatar.hasToonStatusEffect('soundBoost'):
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.statusIcon = status.find('**/inventory_fog_horn')
            iconRoot = NodePath('hydratedIconRoot')
                                    
            self.statusIcon.reparentTo(iconRoot)
            self.statusIcon.setScale(5.5)

            self.extraText = DirectLabel(
                parent=iconRoot,
                relief=None,
                text="%s" % avatar.getToonStatusTurns('soundBoost'),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                text_font=ToontownGlobals.getInterfaceFont(),
                text_bg=Vec4(0, 0, 0, 0),
                pos=(0.25, 0, -0.45),
                text_scale=0.6
            )

            slot = self._claimNextToonStatusSlot()

            self._attachToonStatusIcon(
                iconRoot,
                slot,
                tooltipTitle='Sound Boost', 
                tooltipDescription="This Toon's SOUND Gags will deal +%s%% more damage." % avatar.getToonStatusModifier('soundBoost'),   
                tooltipBuff=True,
                slotColor=(1, 0.984, 0, 1),
                scale=(1, 1, 1)
            )

        if avatar.hasToonStatusEffect('dropBoost'):
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.statusIcon = status.find('**/inventory_boulder')
            iconRoot = NodePath('hydratedIconRoot')
                                                
            self.statusIcon.reparentTo(iconRoot)
            self.statusIcon.setScale(5.5)

            self.extraText = DirectLabel(
                parent=iconRoot,
                relief=None,
                text="%s" % avatar.getToonStatusTurns('dropBoost'),
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                text_font=ToontownGlobals.getInterfaceFont(),
                text_bg=Vec4(0, 0, 0, 0),
                pos=(0.25, 0, -0.45),
                text_scale=0.6
            )

            slot = self._claimNextToonStatusSlot()

            self._attachToonStatusIcon(
                iconRoot,
                slot,
                tooltipTitle='Drop Boost', 
                tooltipDescription="This Toon's DROP Gags will deal +%s%% more damage." % avatar.getToonStatusModifier('dropBoost'),  
                tooltipBuff=True,
                slotColor=(1, 0.984, 0, 1),
                scale=(1, 1, 1)
            )

        if avatar.hasToonStatusEffect('cheer'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/cheer_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('cheer'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Cheer', 
                                   tooltipDescription="This Toon's attack accuracy is increased by +10%",  
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if avatar.hasToonStatusEffect('encore'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/encore_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('encore'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            gagText = self.getColoredText(
                'SOUND',
                'soundText',
                (0.043, 0, 1, 1),
                ToontownGlobals.getSignFont()
            )
            damageText = self.getColoredText(
                '+%s%%' % avatar.getToonStatusModifier('encore'),
                'positiveText',
                (0, 1, 0.016, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Encore', 
                                   tooltipDescription="All Gags have a %s effectiveness boost. By using %s again, you'll become Winded." % (damageText, gagText),  
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if avatar.hasToonStatusEffect('gagBan'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/backfire_icon')
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Gag Ban', 
                                   tooltipDescription="Using any banned Gags will result in a harsh punishment.",  
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1), scale=(1.1, 1.1, 1.1))
            
        if avatar.hasToonStatusEffect('contaminated'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/worker_management_icon')
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Contaminated', 
                                   tooltipDescription="This Toon's Gags have been contaminated, using them will result in a harsh punishment.",  
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        # if avatar.isDancePartner:
        #     status = loader.loadModel('phase_3.5/models/gui/status_effects')
        #     self.gagBan = status.find('**/singing_blues_icon')
        #     slot = self._claimNextToonStatusSlot()
        #     self._attachToonStatusIcon(self.gagBan, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('snapped'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/vulnerable_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('snapped'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            damageText = self.getColoredText(
                '+%s%%' % avatar.getToonStatusModifier('snapped'),
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Snapped', 
                                   tooltipDescription="This Toon takes %s more damage while snapped." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))
            
        if avatar.hasToonStatusEffect('hemmorage'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/broken_shield_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('hemmorage'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            damageText = self.getColoredText(
                '+%s%%' % avatar.getToonStatusModifier('hemmorage'),
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Hemmorage', 
                                   tooltipDescription="This Toon takes %s more damage." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('driedOut'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/dried_out_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('driedOut'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            damageText = self.getColoredText(
                '-50%',
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Dried Out', 
                                   tooltipDescription="This Toon has been wrung dry and has %s accuracy!" % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('bombed2'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/trap_card_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('bombed2'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '+%s%%' % avatar.getToonStatusModifier('bombed2'),
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Hot Take', 
                                   tooltipDescription="This Toon is now taking %s more damage." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))
            
        if avatar.hasToonStatusEffect('highStakes'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/highStakes.png')
            self.statusIcon.setTexture(texture, 1)
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Gag Damage Randomizer', 
                                   tooltipDescription="At the beginning of every turn, the Contingency Director has a 50% change to randomize your Gag damage!", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))
            
        if avatar.hasToonStatusEffect('bombed'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/trap_card_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('bombed'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Hot Take', 
                                   tooltipDescription="If this Toon takes damage from any Cog attack this turn, they will receive a dangerous vulnerability.", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))
            
        if avatar.hasToonStatusEffect('wiretapped'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/brokenConnection.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % avatar.getToonStatusTurns('wiretapped'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '+%s%%' % avatar.getToonStatusModifier('wiretapped'),
                'positiveText',
                (0, 1, 0.016, 1),
                ToontownGlobals.getInterfaceFont()
            )

            damageText2 = self.getColoredText(
                '-%s%%' % avatar.getToonStatusModifier('wiretapped'),
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            if avatar.getToonStatusModifier('wiretapped') > 0:
                self._attachToonStatusIcon(iconRoot, 
                                   slot, 
                                   tooltipTitle='Wiretapped', 
                                   tooltipDescription="This Toon is dealing %s more damage this round." % damageText, 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))
            else:
                self._attachToonStatusIcon(iconRoot, 
                                   slot, 
                                   tooltipTitle='Wiretapped', 
                                   tooltipDescription="This Toon is dealing %s less damage this round." % damageText2, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if getattr(avatar, 'markedWood', 0):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/marked_wood_icon')
            rounds = avatar.getMarkedWoodRounds()
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text='%s' % rounds,
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45), text_scale=.6)
            self.extraText.show()
            modifier = int(round((avatar.getMarkedWood() - 1.0) * 100.0))
            damageText = self.getColoredText(
                '+%s%%' % modifier,
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon,
                                   slot,
                                   tooltipTitle='Marked Wood',
                                   tooltipDescription='The Chainsaw Consultant deals %s damage to this Toon.' % damageText,
                                   tooltipBuff=False,
                                   slotColor=(0, 0.902, 1, 1))

        if (not avatar.hasToonStatusEffect('vulnerable') and
                getattr(avatar, 'isVulnerable', 0) and avatar.getVulnerability() > 1.0):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/broken_shield_icon')
            rounds = avatar.getVulnerabilityRounds()
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text='%s' % rounds,
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45), text_scale=.6)
            self.extraText.show()
            modifier = int(round((avatar.getVulnerability() - 1.0) * 100.0))
            damageText = self.getColoredText(
                '+%s%%' % modifier,
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon,
                                   slot,
                                   tooltipTitle='Vulnerable',
                                   tooltipDescription='This Toon takes %s more damage while vulnerable.' % damageText,
                                   tooltipBuff=False,
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('vulnerable'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/broken_shield_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('vulnerable'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '+%s%%' % avatar.getToonStatusModifier('vulnerable'),
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Vulnerable', 
                                   tooltipDescription="This Toon takes %s more damage while vulnerable." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))
            
        if avatar.hasToonStatusEffect('aceInTheHole'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/broken_shield_icon')
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '+%s%%' % avatar.getToonStatusModifier('aceInTheHole'),
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Vulnerable', 
                                   tooltipDescription="The ace up the High Roller's sleeve causes this Toon to take %s more damage from attacks." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('commissionerMarked'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/liability_waiver.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % avatar.getToonStatusTurns('commissionerMarked'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(iconRoot, 
                                   slot, 
                                   tooltipTitle='Liability Flag', 
                                   tooltipDescription="This Toon has been marked by the Commissioner as a liability! The Commissioner will deal extra damage to this Toon if they are attacked by other Cogs.", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('contingencyMarked'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/marked_wood_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('contingencyMarked'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Targeted Audit', 
                                   tooltipDescription="This Toon has been marked by the Contingency Director! The Contingency Director will deal extra damage to this Toon if they are attacked by other Cogs.", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('inkDrain'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/toon_damage_down_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('inkDrain'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '-%s%%' % avatar.getToonStatusModifier('inkDrain'),
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Ink Drain', 
                                   tooltipDescription="All Gags are %s less effective." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('damageDown'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/toon_damage_down_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('damageDown'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '-%s%%' % avatar.getToonStatusModifier('damageDown'),
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Damage Down', 
                                   tooltipDescription="This Toon's Gags are %s less effective." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('hurrySicknessAttorney'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/hurry_sickness_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('hurrySicknessAttorney'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '-%s%%' % avatar.getToonStatusModifier('hurrySicknessAttorney'),
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Hurry Sickness', 
                                   tooltipDescription="This Toon couldn't keep up with the Head Attorney and thus will deal %s less damage." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('hurrySickness'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/hurry_sickness_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('hurrySickness'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '-%s%%' % avatar.getToonStatusModifier('hurrySickness'),
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Hurry Sickness', 
                                   tooltipDescription="This Toon couldn't keep up with the Pacesetter and thus will deal %s less damage." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('hurrySicknessBan'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/hurry_sickness_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('hurrySicknessBan'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '-%s%%' % avatar.getToonStatusModifier('hurrySicknessBan'),
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Hurry Sickness', 
                                   tooltipDescription="This Toon couldn't keep up with the Pacesetter and thus will deal %s less damage." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))
            
        if avatar.hasToonStatusEffect('sanctioned'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/toon_damage_down_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('sanctioned'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            damageText = self.getColoredText(
                '-%s%%' % avatar.getToonStatusModifier('sanctioned'),
                'damageText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Sanctioned', 
                                   tooltipDescription="This Toon's Gags are %s less effective while sanctioned." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))
            
        if avatar.hasToonStatusEffect('breached'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/toon_damage_down_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('breached'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '-%s%%' % avatar.getToonStatusModifier('breached'),
                'damageText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Breached', 
                                   tooltipDescription="This Toon's Gags are %s less effective while Breached." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('hotShot'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/trialbyfire_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('hotShot'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            damageText = self.getColoredText(
                '+%s%%' % avatar.getToonStatusModifier('hotShot'),
                'positiveText',
                (0, 1, 0.016, 1),
                ToontownGlobals.getInterfaceFont()
            )
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Hot Shot', 
                                   tooltipDescription="This Toon takes %s more damage." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))
            
        if avatar.hasToonStatusEffect('marketMeltdown'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/trialbyfire_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('marketMeltdown'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '+%s%%' % avatar.getToonStatusModifier('marketMeltdown'),
                'positiveText',
                (0, 1, 0.016, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Market Meltdown', 
                                   tooltipDescription="The Dividend King has locked half of your Gag choices, while buffing the other half of them by %s. This Toon will take 25 per round for the duration of the Meltdown." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))
            
        if avatar.hasToonStatusEffect('phantomDebuff'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/worker_management_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('phantomDebuff'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Phantom Entry', 
                                   tooltipDescription="Cogs are more likely to attack this Toon.", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))
            
        if avatar.hasToonStatusEffect('revisedFiling'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/cooked.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % avatar.getToonStatusTurns('revisedFiling'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '+%s%%' % avatar.getToonStatusModifier('revisedFiling'),
                'negativeText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(iconRoot, 
                                   slot, 
                                   tooltipTitle='Revised Filing', 
                                   tooltipDescription="This Toon is taking %s more damage." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        # if avatar.frozen:
        #     status = loader.loadModel('phase_3.5/models/gui/status_effects')
        #     self.liquidated = status.find('**/disruptive_advertisement_icon')
        #     self.liquidatedText = DirectLabel(parent=self.liquidated, relief=None, text="%s" % avatar.getFrozenRounds(), text_fg=(1, 1, 1, 1),
        #                                       text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
        #                                       pos=(0.25, 0, -.5),
        #                                       text_scale=.6)
        #     self.liquidatedText.show()
        #     slot = self._claimNextToonStatusSlot()
        #     self._attachToonStatusIcon(self.liquidated, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('zapped'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/sparkplug_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('zapped'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            damageText = self.getColoredText(
                '-25 Damage',
                'damageText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Power Surged', 
                                   tooltipDescription="This Toon has been zapped! They will take %s at the beginning of the round." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('liquidated'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/monsoon_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('liquidated'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            damageText = self.getColoredText(
                '-30 Damage',
                'damageText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Liquidated', 
                                   tooltipDescription="This Toon has been Liquidated, and as such they will take %s per round." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('employed'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/aftershock_dot.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % avatar.getToonStatusTurns('employed'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '-25 Damage',
                'damageText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(iconRoot, 
                                   slot, 
                                   tooltipTitle='At-Will Employment', 
                                   tooltipDescription="This Toon has been employed against their will by the Union Buster! They will take %s per round." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('bound'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/damage_over_time_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('bound'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '-20 Damage',
                'damageText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Legally Bound', 
                                   tooltipDescription="While legally bound, this Toon will take %s per round." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('wrapped'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/damage_over_time_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('wrapped'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Wrapped In The Film', 
                                   tooltipDescription="While wrapped, this Toon will not be able to dodge any incoming cog attacks.", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('confused'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/interference.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % avatar.getToonStatusTurns('confused'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(iconRoot, 
                                   slot, 
                                   tooltipTitle='Confused', 
                                   tooltipDescription="This Toon is Confused! Group target Gags are disabled, and this Toon's target choice will be randomized.", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('yellowLight'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/yellow_light.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % avatar.getToonStatusTurns('yellowLight'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            damageText = self.getColoredText(
                '-25% Damage',
                'damageText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(iconRoot, 
                                   slot, 
                                   tooltipTitle='Yellow Light', 
                                   tooltipDescription="This Toon is dealing %s less damage." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1), scale=(0.9, 0.9, 0.9))

        if avatar.hasToonStatusEffect('soaked'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/soaked_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('soaked'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Soaked?', 
                                   tooltipDescription="This Toon must have used a defective gag or something...", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('cooldown'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/unite_cooldown_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('cooldown'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Reward Cooldown', 
                                   tooltipDescription='Your Boss Rewards are currently on cooldown.', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('groundbroken'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/fog_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('groundbroken'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Groundbroken', 
                                   tooltipDescription="This Toon has been Groundbroken! They will not take damage from any incoming Cog attacks or be able to use Gags this round.", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))
            
        if avatar.hasToonStatusEffect('suppressed'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/contract_limit.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % avatar.getToonStatusTurns('suppressed'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(iconRoot, 
                                   slot, 
                                   tooltipTitle='Evidence Supression', 
                                   tooltipDescription="This Toon has been removed from battle! They will not take damage from any incoming Cog attacks or be able to use Gags this round.", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('noDodge'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/confusion_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('noDodge'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle="Can't Dodge", 
                                   tooltipDescription="This Toon will not be able to dodge any incoming Cog attacks.", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('target'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/worker_management_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('target'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle="In Focus", 
                                   tooltipDescription="Cogs are more likely to attack this Toon.", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('actionPartner'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/encore_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="1",
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle="Action", 
                                   tooltipDescription="The Director has put this Toon on the spot! They will deal more damage to each other, if either don't attack each other, they will take severe damage.", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('collectCalled'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/counterfeit_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('collectCalled'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle="Collect Call", 
                                   tooltipDescription="The Wiretapper has started a Collect Call with you! You will both deal more damage to each other, not attacking her will result in a harsh punishment.", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))
            
        if avatar.hasToonStatusEffect('mandatoryToll'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/counterfeit_icon')
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle="Mandatory Toll: %s" % avatar.getToonStatusModifier('mandatoryToll'), 
                                   tooltipDescription="The Tollmaster will increase the Toll for you everytime you attack him! He will collect this Toll upon reaching a lower HP threshold.", 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('groupDamageDown'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/toon_damage_down_icon')
            slot = self._claimNextToonStatusSlot()
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('groupDamageDown'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            damageText = self.getColoredText(
                '-%s%%' % avatar.getToonStatusModifier('groupDamageDown'),
                'damageText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle="Radio Infrequency", 
                                   tooltipDescription="Your group Gags will deal %s less damage." % damageText, 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if avatar.hasToonStatusEffect('winded'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/encore_icon')
            slot = self._claimNextToonStatusSlot()
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % avatar.getToonStatusTurns('winded'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            gagText = self.getColoredText(
                'SOUND',
                'soundText',
                (0.043, 0, 1, 1),
                ToontownGlobals.getSignFont()
            )
            damageText = self.getColoredText(
                '-50%',
                'damageText',
                (1, 0, 0, 1),
                ToontownGlobals.getInterfaceFont()
            )
            self._attachToonStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle="Winded", 
                                   tooltipDescription="Your %s Gags will deal %s less damage." % (gagText, damageText), 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        self._applyToonStatusOffset()
        if self.toonStatusInformationPanel:
            self.toonStatusInformationPanel.rebuildStatusEffects(
                list(self.toonStatusIconNodes)
            )


    def setLaffMeter(self, avatar):
        self.notify.debug('setLaffMeter: new avatar %s' % avatar.doId)
        if self.avatar == avatar:
            messenger.send(self.avatar.uniqueName('hpChange'), [avatar.hp, avatar.maxHp, 1])
        else:
            if self.avatar:
                self.cleanupLaffMeter()
            self.avatar = avatar
            self.laffMeter = LaffMeter.LaffMeter(avatar.style, avatar.hp, avatar.maxHp)
            self.laffMeter.setAvatar(self.avatar)
            self.laffMeter.reparentTo(self.laffMeterNode)
            self.laffMeter.setScale(0.11)
            self.laffMeter.start()

        self.setStatusEffects(avatar)

    def setHealthText(self, hp, maxHp, quietly = 0):
        self.healthText['text'] = TTLocalizer.TownBattleHealthText % {'hitPoints': hp,
         'maxHit': maxHp}

    def show(self):
        DirectFrame.show(self)
        if self.laffMeter:
            self.laffMeter.start()

    def hide(self):
        DirectFrame.hide(self)
        if self.laffMeter:
            self.laffMeter.stop()

    def updateLaffMeter(self, hp):
        if self.laffMeter:
            self.laffMeter.adjustFace(hp, self.avatar.maxHp)
        self.setHealthText(hp, maxHp)
        self.setStatusEffects(self.avatar)

    def getConditionCount(self, targetSuit, conds):
        return sum(1 for cond in conds if targetSuit.hasSuitStatusEffect(cond))

    def getTargetDamage(self, damage, targetSuit, track):
        if targetSuit is None:
            return damage

        result = damage

        if targetSuit.hasSuitStatusEffect('videoStatic'):
            result *= (1.0 + self.avatar.getToonStatusModifier('videoStatic') * 0.01)

        if targetSuit.hasSuitStatusEffect('contingencyOverride'):
            result *= (1.0 + self.avatar.getToonStatusModifier('contingencyOverride') * 0.01)

        if targetSuit.hasSuitStatusEffect('powerhouseGeneration'):
            result *= (1.0 + self.avatar.getToonStatusModifier('powerhouseGeneration') * 0.01)

        if targetSuit.hasSuitStatusEffect('silhouetteShielding'):
            result *= .1

        if targetSuit.hasSuitStatusEffect('soakResist') and (targetSuit.hasSuitStatusEffect('soaked') or targetSuit.hasSuitStatusEffect('drenched')):
            result *= .4

        if targetSuit.hasSuitStatusEffect('directorShielding'):
            result *= .5

        if targetSuit.hasSuitStatusEffect('refractionBarrier'):
            result *= (1.0 + self.avatar.getToonStatusModifier('refractionBarrier') * 0.01)

        if targetSuit.hasSuitStatusEffect('brokenConnection'):
            result *= (1.0 + self.avatar.getToonStatusModifier('brokenConnection') * 0.01)

        if targetSuit.hasSuitStatusEffect('shielding'):
            result *= (1.0 + self.avatar.getToonStatusModifier('shielding') * 0.01)

        if targetSuit.hasSuitStatusEffect('scopeCreep'):
            result *= (1.0 + self.avatar.getToonStatusModifier('scopeCreep') * 0.01)

        if targetSuit.hasSuitStatusEffect('directorShielding'):
            result *= (1.0 + self.avatar.getToonStatusModifier('directorShielding') * 0.01)

        if targetSuit.hasSuitStatusEffect('compensationClaims'):
            result *= (1.0 + self.avatar.getToonStatusModifier('compensationClaims') * 0.01)

        if targetSuit.hasSuitStatusEffect('vulnerable'):
            result *= (1.0 + self.avatar.getToonStatusModifier('vulnerable') * 0.01)

        if targetSuit.hasSuitStatusEffect('oilRain'):
            result *= .9

        if targetSuit.hasSuitStatusEffect('marked') and track != THROW_TRACK:
            result *= 1.1

        if targetSuit.hasSuitStatusEffect('contingencyOverrideBroken'):
            result *= .75

        if targetSuit.hasSuitStatusEffect('rushJob'):
            if targetSuit.getSuitStatusModifier('rushJob') == 1 and track != TRAP_TRACK:
                result *= .6
            if targetSuit.getSuitStatusModifier('rushJob') == 2 and track != LURE_TRACK:
                result *= .6
            if targetSuit.getSuitStatusModifier('rushJob') == 3 and track != THROW_TRACK:
                result *= .6
            if targetSuit.getSuitStatusModifier('rushJob') == 4 and track != SQUIRT_TRACK:
                result *= .6
            if targetSuit.getSuitStatusModifier('rushJob') == 5 and track != ZAP_TRACK:
                result *= .6
            if targetSuit.getSuitStatusModifier('rushJob') == 6 and track != SOUND_TRACK:
                result *= .6
            if targetSuit.getSuitStatusModifier('rushJob') == 7 and track != DROP_TRACK:
                result *= .6

        if (targetSuit.getManager() or targetSuit.getGovernaught() or targetSuit.getExecutive()) and track == TRAP_TRACK:
            result *= 1.3

        return int(math.ceil(result))

    def setValues(self, index, track, level=None, numTargets=None, targetIndex=None, localNum=None, targetSuit=None, comboMultiplier=1.0, comboCount=0, dropThrowMultiplier=1.0, wetTargets=None, targetSuits=None, incomingThrowTargets=None, trapTargets=None):
        self.notify.debug('Toon Panel setValues: index=%s track=%s level=%s numTargets=%s targetIndex=%s localNum=%s' % (index, track, level, numTargets, targetIndex, localNum))

        if wetTargets is None:
            wetTargets = set()

        if incomingThrowTargets is None:
            incomingThrowTargets = set()

        if trapTargets is None:
            trapTargets = set()

        extraTargets = []

        zapJumpTargets = []

        if track == ZAP_TRACK and isinstance(targetIndex, int) and targetIndex >= 0:
            if targetIndex in wetTargets:
                # Check every Cog to the LEFT first, nearest to farthest.
                for cogIndex in range(targetIndex - 1, -1, -1):
                    if cogIndex in wetTargets:
                        extraTargets.append(cogIndex)

                        if len(extraTargets) >= 3:
                            break

                # Only after exhausting wet Cogs on the left,
                # continue looking to the RIGHT.
                if len(extraTargets) < 3:
                    for cogIndex in range(targetIndex + 1, numTargets):
                        if cogIndex in wetTargets:
                            extraTargets.append(cogIndex)

                            if len(extraTargets) >= 3:
                                break

        elif track == SQUIRT_TRACK and isinstance(targetIndex, int) and targetIndex >= 0:
            leftIndex = targetIndex - 1
            rightIndex = targetIndex + 1

            if leftIndex >= 0:
                extraTargets.append(leftIndex)

            if rightIndex < numTargets:
                extraTargets.append(rightIndex)
            
        self.hideChoiceIcons()
        self.roundsText.hide()
        self.damageText.hide()
        self.exeDamageText.hide()
        self.soakedDamageText.hide()
        self.extraDamageTextMid.hide()
        self.soakedRoundsText.hide()
        self.knockbackText.hide()
        self.selfHealText.hide()
        self.gagNode.hide()
        self.whichText.hide()
        self.undecidedText.hide()
        self.passNode.hide()
        for extraText in (self.extraDamageTextLeft, self.extraDamageTextMid, self.extraDamageTextRight):
            extraText.hide()
            extraText['text'] = ''
        if self.hasGag:
            self.gag.removeNode()
            self.hasGag = 0
        if track == BattleBase.NO_ATTACK or track == BattleBase.UN_ATTACK:
            self.showChoiceIcon(self.undecidedIcon, Vec4(0.6, 0.6, 0.6, 1))
            self.gagLock.hide()
            self.gagLocked.show()

        elif track == BattleBase.PASS_ATTACK:
            self.showChoiceIcon(self.passIcon, Vec4(1, 0, 0, 1))
            self.gagLock.hide()
            self.gagLocked.show()

        elif track == BattleBase.FIRE:
            self.showChoiceIcon(self.fireIcon, Vec4(0.937, 0.718, 0.816, 1))
            self.gagLock.hide()
            self.gagLocked.show()
            self.whichText.show()
            self.whichText['text'] = self.determineWhichText(numTargets, targetIndex, localNum, index, track)

        elif track == BattleBase.SUE:
            self.showChoiceIcon(self.sueIcon, Vec4(0.682, 0.714, 0.824, 1))
            self.whichText.show()
            self.whichText['text'] = self.determineWhichText(numTargets, targetIndex, localNum, index, track)

        elif track == BattleBase.NPCSOS:
            if numTargets is not None:
                self.whichText.show()
                self.whichText['text'] = self.determineWhichText(numTargets, targetIndex, localNum, index, track)
            definition = IOURegistry.getIOU(level)
            if definition is None:
                self.showChoiceIcon(self.sosIcon, Vec4(0, 1, 0.031, 1))
            else:
                self.hideChoiceIcons()
                gagTrack = definition.getGagTrack()
                if gagTrack == -1:
                    color = Vec4(1, 1, 1, 1)
                else:
                    color = Vec4(TrackColors[gagTrack][0], TrackColors[gagTrack][1], TrackColors[gagTrack][2], 1)
                self.choiceEmblem['image_color'] = color
                self.setChoiceOrganic(False)
                self.choiceEmblem.show()
                self.iouChoiceHead = self.__createIOUChoiceHead(definition.getNpcId(), 0.23)
                self.iouChoiceHead.reparentTo(self.choiceRoot)
                self.iouChoiceHead.setPos(0.21, -0.2, 0.075)
                npcName = NPCToons.getNPCName(definition.getNpcId())
                if npcName:
                    self.iouChoiceName['text'] = npcName.upper()
                    self.iouChoiceName.show()
        elif track == BattleBase.SOS or track == BattleBase.PETSOS:
            self.showChoiceIcon(self.sosIcon, Vec4(0, 1, 0.031, 1))
        elif track >= MIN_TRACK_INDEX and track <= MAX_TRACK_INDEX:
            organic = self.avatar.trackBonusLevel[track] >= 1

            self.choiceEmblem['image_color'] = Vec4(
                TrackColors[track][0],
                TrackColors[track][1],
                TrackColors[track][2],
                1
            )
            self.choiceEmblem.show()
            self.setChoiceOrganic(organic)
            self.passText.hide()
            self.gagLock.hide()
            self.gagLocked.show()
            self.gagNode.show()
            invButton = base.localAvatar.inventory.buttonLookup(track, level)
            self.gag = invButton.instanceUnderNode(self.gagNode, 'gag')
            self.gag.setScale(0.8)
            self.gag.setPos(0.105, -0.2, 0.035)
            self.gag.setColor(1, 1, 1, 1)
            self.hasGag = 1
            allGagBoost = False
            if 'allGagBoost' in self.avatar.battleConditions:
                allGagBoost = True
            raisedAnte = False
            if 'raisedAnte' in self.avatar.battleConditions:
                raisedAnte = True
            damage = int(math.ceil(getAvPropDamage(track, level, self.avatar.experience.getExp(track))))
            if self.avatar.trackBonusLevel[track] >= 1 and track == TRAP_TRACK:
                damage = int(math.ceil(math.ceil(getAvPropDamage(track, level, self.avatar.experience.getExp(track))) * 1.15))
            if track == ZAP_TRACK and isinstance(targetIndex, int) and targetIndex >= 0:
                if targetIndex not in wetTargets:
                    damage *= 0
            lureValue = int(
                ((ToontownBattleGlobals.AvLureKnockback[level] * 100)))
            if targetSuit:
                if self.avatar.trackBonusLevel[track] >= 1 and track == DROP_TRACK:
                    conditionCount = 0

                    if targetSuit.hasSuitStatusEffect('dazed'):
                        conditionCount += 1

                    if targetSuit.hasSuitStatusEffect('soaked') or targetSuit.hasSuitStatusEffect('drenched'):
                        conditionCount += 1

                    if targetSuit.hasSuitStatusEffect('zapped'):
                        conditionCount += 1

                    if targetSuit.hasSuitStatusEffect('trapped'):
                        conditionCount += 1

                    totalCount = conditionCount + comboCount

                    if totalCount > 0:
                        mult = 1.1 + ((totalCount - 1) * 0.05)
                        damage *= mult

                    if targetSuit.hasSuitStatusEffect('marked'):
                        damage *= 1.1
                    else:
                        damage *= dropThrowMultiplier
            if self.avatar.hasToonStatusEffect('toonupBoost') and track == HEAL_TRACK:
                damage *= (1.0 + self.avatar.getToonStatusModifier('toonupBoost') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('toonupBoost') * 0.01)
            if self.avatar.hasToonStatusEffect('trapBoost') and track == TRAP_TRACK:
                damage *= (1.0 + self.avatar.getToonStatusModifier('trapBoost') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('trapBoost') * 0.01)
            if self.avatar.hasToonStatusEffect('lureBoost') and track == LURE_TRACK:
                damage *= (1.0 + self.avatar.getToonStatusModifier('trapBoost') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('trapBoost') * 0.01)
            if self.avatar.hasToonStatusEffect('throwBoost') and track == THROW_TRACK:
                damage *= (1.0 + self.avatar.getToonStatusModifier('throwBoost') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('throwBoost') * 0.01)
            if self.avatar.hasToonStatusEffect('squirtBoost') and track == SQUIRT_TRACK:
                damage *= (1.0 + self.avatar.getToonStatusModifier('squirtBoost') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('squirtBoost') * 0.01)
            if self.avatar.hasToonStatusEffect('zapBoost') and track == ZAP_TRACK:
                damage *= (1.0 + self.avatar.getToonStatusModifier('zapBoost') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('zapBoost') * 0.01)
            if self.avatar.hasToonStatusEffect('soundBoost') and track == SOUND_TRACK:
                damage *= (1.0 + self.avatar.getToonStatusModifier('soundBoost') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('soundBoost') * 0.01)
            if self.avatar.hasToonStatusEffect('dropBoost') and track == DROP_TRACK:
                damage *= (1.0 + self.avatar.getToonStatusModifier('dropBoost') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('dropBoost') * 0.01)
            if self.avatar.hasToonStatusEffect('damageUp'):
                damage *= (1.0 + self.avatar.getToonStatusModifier('damageUp') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('damageUp') * 0.01)
            if self.avatar.hasToonStatusEffect('marketMeltdown'):
                damage *= (1.0 + self.avatar.getToonStatusModifier('marketMeltdown') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('marketMeltdown') * 0.01)
            if self.avatar.hasToonStatusEffect('damageDown'):
                damage *= (1.0 - self.avatar.getToonStatusModifier('damageDown') * 0.01)
                lureValue *= (1.0 - self.avatar.getToonStatusModifier('damageDown') * 0.01)
            if self.avatar.hasToonStatusEffect('yellowLight'):
                damage *= (1.0 - self.avatar.getToonStatusModifier('yellowLight') * 0.01)
                lureValue *= (1.0 - self.avatar.getToonStatusModifier('yellowLight') * 0.01)
            if self.avatar.hasToonStatusEffect('sanctioned'):
                damage *= (1.0 - self.avatar.getToonStatusModifier('sanctioned') * 0.01)
                lureValue *= (1.0 - self.avatar.getToonStatusModifier('sanctioned') * 0.01)
            if self.avatar.hasToonStatusEffect('bombed2'):
                damage *= (1.0 + self.avatar.getToonStatusModifier('bombed2') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('bombed2') * 0.01)
            if self.avatar.hasToonStatusEffect('breached'):
                damage *= (1.0 - self.avatar.getToonStatusModifier('breached') * 0.01)
                lureValue *= (1.0 - self.avatar.getToonStatusModifier('breached') * 0.01)
            if self.avatar.hasToonStatusEffect('wiretapped'):
                damage *= (1.0 + self.avatar.getToonStatusModifier('wiretapped') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('wiretapped') * 0.01)
            if self.avatar.hasToonStatusEffect('encore'):
                damage *= (1.0 + self.avatar.getToonStatusModifier('encore') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('encore') * 0.01)
            if self.avatar.hasToonStatusEffect('winded') and track == SOUND_TRACK:
                damage *= (1.0 - self.avatar.getToonStatusModifier('winded') * 0.01)
                lureValue *= (1.0 - self.avatar.getToonStatusModifier('winded') * 0.01)
            if self.avatar.hasToonStatusEffect('damageUpGov'):
                damage *= (1.0 + self.avatar.getToonStatusModifier('damageUpGov') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('damageUpGov') * 0.01)
            if self.avatar.hasToonStatusEffect('markedMeltdown'):
                damage *= (1.0 + self.avatar.getToonStatusModifier('markedMeltdown') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('markedMeltdown') * 0.01)
            # if self.avatar.hasToonStatusEffect('phantomDebuff'):
            #     damage *= (1.0 - self.avatar.getToonStatusModifier('phantomDebuff') * 0.01)
            # #     lureValue *= (1.0 -self.avatar.getToonStatusModifier('phantomDebuff') * 0.01)
            # if self.avatar.hasToonStatusEffect('revisedFiling'):
            #     damage *= (1.0 + self.avatar.getToonStatusModifier('revisedFiling') * 0.01)
            #     lureValue *= (1.0 + self.avatar.getToonStatusModifier('revisedFiling') * 0.01)
            if self.avatar.hasToonStatusEffect('raisedAnte'):
                damage *= (1.0 + self.avatar.getToonStatusModifier('raisedAnte') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('raisedAnte') * 0.01)
            if self.avatar.hasToonStatusEffect('inkDrain'):
                damage *= (1.0 - self.avatar.getToonStatusModifier('inkDrain') * 0.01)
                lureValue *= (1.0 - self.avatar.getToonStatusModifier('inkDrain') * 0.01)
            if self.avatar.hasToonStatusEffect('hurrySickness'):
                damage *= (1.0 - self.avatar.getToonStatusModifier('hurrySickness') * 0.01)
                lureValue *= (1.0 - self.avatar.getToonStatusModifier('hurrySickness') * 0.01)
            if self.avatar.hasToonStatusEffect('hurrySicknessBan'):
                damage *= (1.0 - self.avatar.getToonStatusModifier('hurrySicknessBan') * 0.01)
                lureValue *= (1.0 - self.avatar.getToonStatusModifier('hurrySicknessBan') * 0.01)
            if self.avatar.hasToonStatusEffect('viralSensation'):
                damage *= (1.0 + self.avatar.getToonStatusModifier('viralSensation') * 0.01)
                lureValue *= (1.0 + self.avatar.getToonStatusModifier('viralSensation') * 0.01)
            if self.avatar.hasToonStatusEffect('energized'):
                damage *= 1.5
                lureValue *= 1.5
            if self.avatar.hasToonStatusEffect('commissionerMarked'):
                damage *= 1.25
                lureValue *= 1.25
            if self.avatar.hasToonStatusEffect('groupDamageDown') and ((track == LURE_TRACK and level == 1) or (track == LURE_TRACK and level == 3) or (track == LURE_TRACK and level == 5) or (track == LURE_TRACK and level == 7) or (track == SOUND_TRACK)\
                    or (track == ZAP_TRACK) or (track == HEAL_TRACK and level == 1) or (track == HEAL_TRACK and level == 3) or (track == HEAL_TRACK and level == 5) or (track == HEAL_TRACK and level == 7) or (track == SQUIRT_TRACK)):
                damage *= (1.0 + -50 * 0.01)
                lureValue *= (1.0 + -50 * 0.01)
            baseTargetDamage = damage
            if targetSuit != None:
                if targetSuit.hasSuitStatusEffect('videoStatic'):
                    damage *= (1.0 + self.avatar.getToonStatusModifier('videoStatic') * 0.01)
                    lureValue *= (1.0 + self.avatar.getToonStatusModifier('videoStatic') * 0.01)
                if targetSuit.hasSuitStatusEffect('contingencyOverride'):
                    damage *= (1.0 + self.avatar.getToonStatusModifier('contingencyOverride') * 0.01)
                    lureValue *= (1.0 + self.avatar.getToonStatusModifier('contingencyOverride') * 0.01)
                if targetSuit.hasSuitStatusEffect('powerhouseGeneration'):
                    damage *= (1.0 + self.avatar.getToonStatusModifier('powerhouseGeneration') * 0.01)
                    lureValue *= (1.0 + self.avatar.getToonStatusModifier('powerhouseGeneration') * 0.01)
                if targetSuit.hasSuitStatusEffect('silhouetteShielding'):
                    damage *= .1
                    lureValue *= .1
                if targetSuit.hasSuitStatusEffect('soakResist') and (targetSuit.hasSuitStatusEffect('soaked') or targetSuit.hasSuitStatusEffect('drenched')):
                    damage *= .4
                    lureValue *= .4
                if targetSuit.hasSuitStatusEffect('refractionBarrier'):
                    damage *= (1.0 + self.avatar.getToonStatusModifier('refractionBarrier') * 0.01)
                    lureValue *= (1.0 + self.avatar.getToonStatusModifier('refractionBarrier') * 0.01)
                if targetSuit.hasSuitStatusEffect('brokenConnection'):
                    damage *= (1.0 + self.avatar.getToonStatusModifier('brokenConnection') * 0.01)
                    lureValue *= (1.0 + self.avatar.getToonStatusModifier('brokenConnection') * 0.01)
                if targetSuit.hasSuitStatusEffect('shielding'):
                    damage *= (1.0 + self.avatar.getToonStatusModifier('shielding') * 0.01)
                    lureValue *= (1.0 + self.avatar.getToonStatusModifier('shielding') * 0.01)
                if targetSuit.hasSuitStatusEffect('directorShielding'):
                    damage *= .5
                    lureValue *= .5
                if targetSuit.hasSuitStatusEffect('scopeCreep'):
                    damage *= (1.0 + self.avatar.getToonStatusModifier('scopeCreep') * 0.01)
                    lureValue *= (1.0 + self.avatar.getToonStatusModifier('scopeCreep') * 0.01)
                if targetSuit.hasSuitStatusEffect('directorShielding'):
                    damage *= (1.0 + self.avatar.getToonStatusModifier('directorShielding') * 0.01)
                    lureValue *= (1.0 + self.avatar.getToonStatusModifier('directorShielding') * 0.01)
                if targetSuit.hasSuitStatusEffect('compensationClaims'):
                    damage *= (1.0 + self.avatar.getToonStatusModifier('compensationClaims') * 0.01)
                    lureValue *= (1.0 + self.avatar.getToonStatusModifier('compensationClaims') * 0.01)
                if targetSuit.hasSuitStatusEffect('vulnerable'):
                    damage *= (1.0 + self.avatar.getToonStatusModifier('vulnerable') * 0.01)
                    lureValue *= (1.0 + self.avatar.getToonStatusModifier('vulnerable') * 0.01)
                if targetSuit.hasSuitStatusEffect('oilRain'):
                    damage *= .9
                    lureValue *= .9
                if targetSuit.hasSuitStatusEffect('marked') and not track == THROW_TRACK:
                    damage *= 1.1
                    lureValue *= 1.1
                if targetSuit.hasSuitStatusEffect('contingencyOverrideBroken'):
                    damage *= .75
                    lureValue *= .75
                if targetSuit.hasSuitStatusEffect('enraged') and not targetSuit.hasSuitStatusEffect('desperation'):
                    damage *= .7
                    lureValue *= .7
                if targetSuit.hasSuitStatusEffect('rushJob'):
                    if targetSuit.getSuitStatusModifier('rushJob') == 1 and track != TRAP_TRACK:
                        damage *= .6
                        lureValue *= .6
                    if targetSuit.getSuitStatusModifier('rushJob') == 2 and track != LURE_TRACK:
                        damage *= .6
                        lureValue *= .6
                    if targetSuit.getSuitStatusModifier('rushJob') == 3 and track != THROW_TRACK:
                        damage *= .6
                        lureValue *= .6
                    if targetSuit.getSuitStatusModifier('rushJob') == 4 and track != SQUIRT_TRACK:
                        damage *= .6
                        lureValue *= .6
                    if targetSuit.getSuitStatusModifier('rushJob') == 5 and track != ZAP_TRACK:
                        damage *= .6
                        lureValue *= .6
                    if targetSuit.getSuitStatusModifier('rushJob') == 6 and track != SOUND_TRACK:
                        damage *= .6
                        lureValue *= .6
                    if targetSuit.getSuitStatusModifier('rushJob') == 7 and track != DROP_TRACK:
                        damage *= .6
                        lureValue *= .6
                if (targetSuit.getManager() or targetSuit.getGovernaught() or targetSuit.getExecutive()) and track == TRAP_TRACK:
                    damage *= 1.3
                    lureValue *= 1.3
            damage *= comboMultiplier
            if numTargets is not None and targetIndex is not None and localNum is not None:
                self.whichText.show()
                self.whichText['text'] = self.determineWhichText(numTargets, targetIndex, localNum, index, track, extraTargets=extraTargets)
            if track == LURE_TRACK:
                self.roundsText.show()
                self.extraDamageTextMid.show()
                self.damageText.setPos(0, 0.05, 0.25)
                if self.avatar.trackBonusLevel[track] >= 1:
                    self.roundsText['text'] = "Knockback: " + str(int(math.ceil(lureValue * 1.2))) + '%'
                else:
                    self.roundsText['text'] = "Knockback: " + str(int(math.ceil(lureValue))) + '%'
                self.extraDamageTextMid['text'] = "Rounds: " + str(NumRoundsLured[level] + 1)
                # self.knockbackText.show()
                # self.knockbackText['text'] = 'Knockback: ' + str(lureValue)+'%'
            if track == HEAL_TRACK:
                self.roundsText.show()
                self.damageText.setPos(0, 0.05, 0.25)
                if self.avatar.trackBonusLevel[track] >= 1:
                    self.roundsText['text'] = '+' + str(int(math.ceil(damage))) + '/' + str(int(math.ceil(damage / 2.22)))
                else:
                    self.roundsText['text'] = '+' + str(int(math.ceil(damage))) + '/' + str(int(math.ceil(damage / 4)))
                self.roundsText.setColor(0.176, 1, 0, 1)
                # self.selfHealText.show()
                # self.selfHealText['text'] = 'Self Heal: ' + str(damage / 2.5)
                # self.selfHealText.setColor(0.176, 1, 0, 1)
            if track == TRAP_TRACK:
                self.damageText.show()
                self.damageText.setPos(0, 0.05, 0.25)
                self.damageText['text'] = '-' + str(int(math.ceil(damage)))
                # self.exeDamageText.show()
                # self.exeDamageText['text'] = 'Exe./Gov.: ' + str(damage * 1.3)
            if track == SQUIRT_TRACK and extraTargets and targetSuits:
                for extraIndex in extraTargets:
                    if extraIndex < 0 or extraIndex >= len(targetSuits):
                        continue

                    extraSuit = targetSuits[extraIndex]

                    if self.avatar.trackBonusLevel[track] >= 1:
                        splashDamage = (baseTargetDamage * comboMultiplier) * 0.75
                    else:
                        splashDamage = (baseTargetDamage * comboMultiplier) * 0.33

                    if extraIndex in incomingThrowTargets and not extraSuit.hasSuitStatusEffect('marked'):
                        splashDamage *= 1.1

                    splashDamage = self.getTargetDamage(splashDamage, extraSuit, track)

                    splashText = '-' + str(int(math.ceil(splashDamage)))

                    # Splash Cog is to the left of the primary target.
                    if extraIndex > targetIndex:
                        self.damageText.setPos(0, 0.05, 0.32)
                        self.extraDamageTextLeft['text'] = splashText
                        self.extraDamageTextLeft.show()

                    # Splash Cog is to the right of the primary target.
                    elif extraIndex < targetIndex:
                        self.damageText.setPos(0, 0.05, 0.32)
                        self.extraDamageTextRight['text'] = splashText
                        self.extraDamageTextRight.show()

                    else:
                        self.damageText.setPos(-0.17, 0.05, 0.32)
                        
            if track == SOUND_TRACK:
                self.damageText.show()
                self.damageText['text'] = '-' + str(int(math.ceil(damage)))
                self.damageText.setPos(0, 0.05, 0.25)
            if track == THROW_TRACK:
                self.damageText.show()
                self.damageText['text'] = '-' + str(int(math.ceil(damage)))
                self.damageText.setPos(0, 0.05, 0.25)
            if track == DROP_TRACK:
                self.damageText.show()
                self.damageText['text'] = '-' + str(int(math.ceil(damage)))
                self.damageText.setPos(0, 0.05, 0.25)
            if track == SQUIRT_TRACK:
                self.damageText.show()
                self.damageText['text'] = '-' + str(int(math.ceil(damage)))
            if track == ZAP_TRACK:
                self.damageText.show()
                self.damageText['text'] = '-' + str(int(math.ceil(damage)))
            if track == ZAP_TRACK and extraTargets and targetSuits:
                jumpMultipliers = (0.9, 0.8, 0.7)

                leftDamageParts = []
                rightDamageParts = []

                for jumpIndex, extraIndex in enumerate(extraTargets):
                    if jumpIndex >= len(jumpMultipliers):
                        break

                    if extraIndex < 0 or extraIndex >= len(targetSuits):
                        continue

                    extraSuit = targetSuits[extraIndex]

                    jumpDamage = (baseTargetDamage * comboMultiplier) * jumpMultipliers[jumpIndex]

                    if extraIndex in incomingThrowTargets and not extraSuit.hasSuitStatusEffect('marked'):
                        jumpDamage *= 1.1

                    jumpDamage = self.getTargetDamage(jumpDamage, extraSuit, track)

                    jumpText = '-' + str(int(math.ceil(jumpDamage)))

                    if extraIndex > targetIndex:
                        leftDamageParts.append(jumpText)

                    elif extraIndex < targetIndex:
                        rightDamageParts.append(jumpText)

                leftCount = len(leftDamageParts)
                rightCount = len(rightDamageParts)

                if leftDamageParts:
                    self.extraDamageTextLeft['text'] = '/'.join(leftDamageParts)

                    if leftCount > 0:
                        self.damageText.setPos(0, 0.05, 0.32)

                    self.extraDamageTextLeft.show()

                if rightDamageParts:
                    self.extraDamageTextRight['text'] = '/'.join(rightDamageParts)

                    if rightCount > 0:
                        self.damageText.setPos(0, 0.05, 0.32)

                    self.extraDamageTextRight.show()

                if not rightDamageParts and not leftDamageParts:
                    self.damageText.setPos(0, 0.05, 0.25)
        else:
            self.notify.error('Bad track value: %s' % track)

    def determineWhichText(self, numTargets, targetIndex, localNum, index, track, immuneTargets=None, extraTargets=None):
        if immuneTargets is None:
            immuneTargets = []

        if extraTargets is None:
            extraTargets = []

        returnStr = ''
        targetList = range(numTargets)
        targetList.reverse()

        try:
            if self.avatar.hasToonStatusEffect('confused'):
                marker = '-'
                extraMarker = '-'
            elif self.avatar.trackBonusLevel[track] >= 1:
                marker = 'O'
                extraMarker = 'o'
            else:
                marker = 'X'
                extraMarker = 'x'
        except:
            marker = 'X'
            extraMarker = 'x'

        # =====================================================
        # LIST / TUPLE TARGETS
        # Used for things like Toon targeting: [0], [0, 1], etc.
        # =====================================================
        if isinstance(targetIndex, (list, tuple)):
            for i in targetList:
                if i in immuneTargets:
                    returnStr += '-'
                elif i in extraTargets:
                    returnStr += extraMarker
                elif i in targetIndex:
                    returnStr += marker
                else:
                    returnStr += '-'

            return returnStr

        # =====================================================
        # NORMAL INTEGER TARGETS
        # =====================================================
        for i in targetList:
            if i in immuneTargets:
                returnStr += '-'
                continue

            if i in extraTargets:
                returnStr += extraMarker
                continue

            if targetIndex == -1:
                returnStr += marker

            elif targetIndex == -2:
                if i == index:
                    returnStr += '-'
                else:
                    returnStr += marker

            elif isinstance(targetIndex, int) and 0 <= targetIndex <= 6:
                if i == targetIndex:
                    returnStr += marker
                else:
                    returnStr += '-'

            else:
                self.notify.error('Bad target index: %s' % targetIndex)

        return returnStr

    def updateSurrenderState(self, surrenderState, instant=False):
        changeState = self.surrenderState != surrenderState
        self.surrenderState = surrenderState
        if not changeState:
            return
        if self.surrenderSeq:
            self.surrenderSeq.finish()
            self.surrenderSeq = None
        if instant:
            if surrenderState:
                self.surrenderFlag.show()
            else:
                self.surrenderFlag.hide()
            return
        if surrenderState:
            self.surrenderSeq = Sequence(
                Func(self.surrenderFlag.setPos, (-0.17, 0, 0.0)),
                Func(self.surrenderFlag.setScale, 0.01),
                Func(self.surrenderFlag.show),
                Parallel(
                    LerpScaleInterval(self.surrenderFlag, 0.2, 0.3, blendType='easeOut'),
                    LerpPosInterval(self.surrenderFlag, 0.2, (-0.45, 0, 0.28), blendType='easeOut')
                )
            )
        else:
            self.surrenderSeq = Sequence(
                Func(self.surrenderFlag.setPos, (-0.45, 0, 0.28)),
                Func(self.surrenderFlag.setScale, 0.3),
                Parallel(
                    LerpScaleInterval(self.surrenderFlag, 0.2, 0.01, blendType='easeIn'),
                    LerpPosInterval(self.surrenderFlag, 0.2, (-0.17, 0, 0.0), blendType='easeIn')
                ),
                Func(self.surrenderFlag.hide)
            )
        self.surrenderSeq.start()

    def cleanup(self):
        self.ignoreAll()

        if getattr(self, 'surrenderSeq', None):
            self.surrenderSeq.finish()
            self.surrenderSeq = None

        if getattr(self, 'choiceOrganicIval', None):
            self.choiceOrganicIval.finish()
            self.choiceOrganicIval = None

        self.cleanupLaffMeter()
        self._cleanupToonStatusDisplay()

        if self.hasGag:
            self.gag.removeNode()
            self.hasGag = 0

        for nodeName in (
            'panelFrame',
            'choiceEmblem',
            'undecidedIcon',
            'passIcon',
            'fireIcon',
            'sueIcon',
            'sosIcon',
            'surrenderFlag',
            'iouChoiceName'
        ):
            node = getattr(self, nodeName, None)
            if node:
                try:
                    node.destroy()
                except:
                    node.removeNode()
                setattr(self, nodeName, None)

        if getattr(self, 'choiceRoot', None):
            self.choiceRoot.removeNode()
            self.choiceRoot = None

        if getattr(self, 'gagNode', None):
            self.gagNode.removeNode()
            self.gagNode = None

        if getattr(self, 'passNode', None):
            self.passNode.removeNode()
            self.passNode = None

        if getattr(self, 'choicePanelModels', None):
            self.choicePanelModels.removeNode()
            self.choicePanelModels = None

        if getattr(self, 'choiceStatusModels', None):
            self.choiceStatusModels.removeNode()
            self.choiceStatusModels = None

        self.choiceOrganicTex = None
        self.choiceOrganicStage = None
        if self.toonStatusEffectTooltip:
            self.toonStatusEffectTooltip.destroy()
            self.toonStatusEffectTooltip = None

        if getattr(self, 'infoButton', None):
            self.infoButton.destroy()
            self.infoButton = None

        if self.toonStatusInformationPanel:
            try:
                self.toonStatusInformationPanel.destroy()
            except:
                pass

            self.toonStatusInformationPanel = None

        if self.toonStatusEffectTooltip:
            try:
                self.toonStatusEffectTooltip.destroy()
            except:
                pass

            self.toonStatusEffectTooltip = None

        DirectFrame.destroy(self)

    def cleanupLaffMeter(self):
        self.notify.debug('Cleaning up laffmeter!')
        self.ignore(self.hpChangeEvent)
        # if self.laffMeterNode:
        #     self.laffMeterNode.destroy()
        #     self.laffMeterNode = None
        if self.laffMeter:
            self.laffMeter.destroy()
            self.laffMeter = None