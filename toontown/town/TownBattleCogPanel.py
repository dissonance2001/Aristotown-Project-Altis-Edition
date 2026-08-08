from panda3d.core import *
from panda3d.direct import *
import random
from toontown.toonbase import ToontownGlobals
from toontown.suit import Suit
from toontown.toonbase.ToontownBattleGlobals import *
from direct.directnotify import DirectNotifyGlobal
import string
from toontown.toon import LaffMeter
from toontown.battle import BattleBase
from direct.actor.Actor import Actor
from toontown.battle import DistributedBattleBase
from toontown.battle import BattleProps
from toontown.suit import SuitDNA
from direct.task.Task import Task
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from panda3d.direct import *
from toontown.toonbase import TTLocalizer
from toontown.battle import SuitBattleGlobals
from toontown.quest.QuestPoster import QuestPoster
from panda3d.core import TextProperties
from panda3d.core import TextPropertiesManager

mgr = TextPropertiesManager.getGlobalPtr()

red = TextProperties()
red.setTextColor(1, 0.2, 0.2, 1)
mgr.setProperties("red", red)

green = TextProperties()
green.setTextColor(0.4, 1, 0.4, 1)
mgr.setProperties("green", green)

yellow = TextProperties()
yellow.setTextColor(1, 1, 0.2, 1)
mgr.setProperties("yellow", yellow)

SUIT_STATUS_TOOLTIPS = {
    'soaked': {
        'title': 'SOAKING WET!!!!!!!',
        'description': 'This cog got absolutely soaked.',
        'buff': True,
    },
}
class CogStatusInformationPanel(DirectFrame):
    def __init__(
            self,
            cog,
            statusEffects,
            modifiers=None,
            closeCommand=None):

        DirectFrame.__init__(
            self,
            parent=aspect2d,
            relief=None
        )

        self.cog = cog
        self.statusEffects = statusEffects or []
        self.modifiers = modifiers or []
        self.closeCommand = closeCommand

        self.statusCards = []
        self.modifierLabels = []
        self.showTrack = None

        tooltipGui = loader.loadModel(
            'phase_3.5/models/gui/battlegui/info_panels'
        )

        keybindsGui = loader.loadModel(
            'phase_3.5/models/gui/optionspage/keybinds_gui.bam'
        )

        # Same main panel image as the reference SuitInformationPanel.
        self.background = DirectFrame(
            parent=self,
            relief=None,
            image=tooltipGui.find('**/info_panel_main_suit'),
            image_scale=(1, 1, 0.5),
            frameSize=(-0.485, 0.485, -0.235, 0.235)
        )

        # Prevent clicking GUI objects behind this panel.
        self.background['state'] = DGG.NORMAL

        self.titleText = DirectLabel(
            parent=self.background,
            relief=None,
            text=self._getCogName(),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont(),
            text_scale=0.035,
            text_pos=(0, 0.203)
        )

        # -------------------------
        # LEFT: COG MODIFIERS
        # -------------------------

        self.modifiersTitleText = DirectLabel(
            parent=self.background,
            relief=None,
            text='Modifiers',
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont(),
            text_scale=0.035,
            text_pos=(-0.238, 0.157)
        )

        self.modifiersFrame = DirectScrolledFrame(
            parent=self.background,
            relief=None,

            frameSize=(-0.205, 0.205, -0.225, 0.125),
            canvasSize=(-0.195, 0.195, -0.225, 0.125),

            pos=(-0.238, 0, 0),

            scrollBarWidth=0.018,

            verticalScroll_relief=None,
            verticalScroll_thumb_relief=None,

            verticalScroll_thumb_image=tooltipGui.find(
                '**/scroll_thumb_suit'
            ),
            verticalScroll_thumb_image_scale=(0.25, 1, 0.125),

            verticalScroll_resizeThumb=False
        )

        self.modifiersFrame.horizontalScroll.hide()
        self.modifiersFrame.verticalScroll.incButton.hide()
        self.modifiersFrame.verticalScroll.decButton.hide()

        # -------------------------
        # RIGHT: STATUS EFFECTS
        # -------------------------

        self.effectsTitleText = DirectLabel(
            parent=self.background,
            relief=None,
            text='Status Effects',
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont(),
            text_scale=0.035,
            text_pos=(0.248, 0.157)
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
                '**/scroll_thumb_suit'
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

        self.rebuildModifiers()
        self.rebuildStatusEffects()

    def _getCogName(self):
        if not self.cog:
            return 'Cog'

        try:
            return self.cog.getName()
        except:
            pass

        try:
            return self.cog.getStyleName()
        except:
            return 'Cog'

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

    def rebuildModifiers(self, modifiers=None):
        if modifiers is not None:
            self.modifiers = modifiers

        self._clearModifierLabels()

        canvas = self.modifiersFrame.getCanvas()

        if not self.modifiers:
            label = DirectLabel(
                parent=canvas,
                relief=None,
                text='No special modifications have been made to this Cog.',
                text_font=ToontownGlobals.getInterfaceFont(),
                text_fg=(0.1, 0.1, 0.1, 1),
                text_align=TextNode.ACenter,
                text_scale=0.025,
                text_wordwrap=15,
                pos=(0, 0, 0.065)
            )

            self.modifierLabels.append(label)

            self.modifiersFrame['canvasSize'] = (
                -0.195, 0.195,
                -0.225, 0.125
            )

            self.modifiersFrame.verticalScroll.hide()
            return

        rowHeight = 0.092
        startZ = 0.09

        for index, modifier in enumerate(self.modifiers):
            z = startZ - index * rowHeight

            row = self._createModifierRow(
                canvas,
                modifier,
                z
            )

            self.modifierLabels.append(row)

        minimumBottom = -0.225
        contentBottom = startZ - len(self.modifiers) * rowHeight - 0.025
        bottom = min(minimumBottom, contentBottom)

        self.modifiersFrame['canvasSize'] = (
            -0.195, 0.195,
            bottom, 0.125
        )

        if len(self.modifiers) <= 4:
            self.modifiersFrame.verticalScroll.hide()
        else:
            self.modifiersFrame.verticalScroll.show()

        self.modifiersFrame.verticalScroll['value'] = 0


    def _createModifierRow(self, parent, modifier, z):
        positive = modifier.get('positive', True)

        titleColor = (0, 0, 0, 1)

        row = DirectFrame(
            parent=parent,
            relief=None,
            pos=(0, 0, z)
        )

        title = modifier.get('title', 'Modifier')
        description = modifier.get('description', '')
        value = modifier.get('value')

        if value:
            title = '%s: %s' % (title, value)

        DirectLabel(
            parent=row,
            relief=None,
            text=title,
            text_font=ToontownGlobals.getSuitFont(),
            text_fg=titleColor,
            text_shadow=(1, 1, 1, 0.35),
            text_align=TextNode.ACenter,
            text_scale=0.026,
            text_wordwrap=14,
            pos=(0, 0, 0.0175)
        )

        DirectLabel(
            parent=row,
            relief=None,
            text=description,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_fg=(0.1, 0.1, 0.1, 1),
            text_align=TextNode.ACenter,
            text_scale=0.018,
            text_wordwrap=20,
            pos=(0, 0, -0.008)
        )

        return row

    # def generateSuitModifierText(av):
    #     text = ''
    #     name = av.style.name

    #     # Find the suit's specialization, if they have one
    #     if 'specialization' in SuitBattleGlobals.SuitAttributes[name]:
    #         specialization = SuitBattleGlobals.SuitAttributes[name]['specialization']
    #     else:
    #         specialization = SuitBattleGlobals.NORMAL

    #     # Function that adds new lines as needed.
    #     def addText(currentText, newText):
    #         # New line if there is a line already
    #         if currentText != '':
    #             currentText = currentText + '\n\n'

    #         # Return combined string
    #         return currentText + newText

    #     # # Add text for specialization
    #     # if specialization != SuitBattleGlobals.NORMAL:
    #     #     specializationName = SuitBattleGlobals.SuitSpecialization2Name[specialization]
    #     #     text = addText(text,
    #     #                 f'\1TextSubtitle\1{specializationName}:\2\n{TTLocalizer.SuitAttributeDescriptions[specializationName]}')
            
    #     if av.dna.name in ['pf', 'stg', 'shy', 'cn', 'ca', 'dhr', 'bsd', 'ad', 'ksp', 'gld', 'asm', 'ang', 'blk', 'dcw', 'dc', 'enf', 'sw', 'mdm', 'brn', 'sbg', 'cv']:
    #         text = addText(text,
    #                     '\1TextSubtitle\1{SuitAttributeDefense}:\2\n{TTLocalizer.SuitAttributeDescriptions[SuitAttributeDefense]}')
    #     if av.dna.name in ['fcs', 'txm', 'key', 'fct', 'nn', 'blh', 'ath',  'bfh2', 'ppl', 'pyc', 'trs', 'sh', 'bsht', 'wnk', 'br', 'txm', 'chw', 'bfh', 'cnd', 'itn', 'std', 'std2']:
    #         text = addText(text,
    #                     '\1TextSubtitle\1{SuitAttributeAttack}:\2\n{TTLocalizer.SuitAttributeDescriptions[SuitAttributeAttack]}')

    #     # Add text for miniboss or executive. (miniboss has priority)
    #     if av.getManager():
    #         text = addText(text,
    #                     '\1TextSubtitle\1{'Manager'}:\2\n{TTLocalizer.SuitAttributeDescriptions[TTLocalizer.SuitAttributeManager]}')
    #     elif av.getExecutive():
    #         text = addText(text,
    #                     '\1TextSubtitle\1{'Executive'}:\2\n{TTLocalizer.SuitAttributeDescriptions[TTLocalizer.SuitAttributeExecutive]}')
    #     elif av.getGovernaught():
    #         text = addText(text,
    #                     '\1TextSubtitle\1{'Advanced'}:\2\n{TTLocalizer.SuitAttributeDescriptions[TTLocalizer.SuitAttributeGovernaught]}')

    #     # Add text for v2.0s
    #     if av.getSkeleRevives() >= 2:
    #         text = addText(text,
    #                     '\1TextSubtitle\1{TTLocalizer.SuitAttributeRevive2}:\2\n{TTLocalizer.SuitAttributeDescriptions[TTLocalizer.SuitAttributeRevive2]}')
    #     elif av.getSkeleRevives() >= 1:
    #         text = addText(text,
    #                     '\1TextSubtitle\1{TTLocalizer.SuitAttributeRevive}:\2\n{TTLocalizer.SuitAttributeDescriptions[TTLocalizer.SuitAttributeRevive]}')

    #     # Use default text if there were no special modifications to this suit
    #     if text == '':
    #         text = TTLocalizer.SuitAttributeDescriptions[TTLocalizer.SuitAttributeNormal]

    #     return text
    
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
                text_fg=(0.1, 0.1, 0.1, 1),
                text_scale=0.025,
                text_wordwrap=16,
                pos=(0, 0, 0.02)
            )

            self.statusCards.append(emptyLabel)

            self.statusEffectsFrame['canvasSize'] = (
                -0.22, 0.1,
                -0.0425, 0.048
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
            cardImage = tooltipGui.find('**/info_panel_buff_suit')
        else:
            cardImage = tooltipGui.find('**/info_panel_debuff_suit')

        # Some versions may use alternate node names.
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

        iconRoot = card.attachNewNode('status-card-icon')
        iconRoot.setPos(-0.33, 0, 0.001)
        iconRoot.setScale(0.12)

        # Copy the original status-slot background.
        sourceBackground = effectData.get('background')

        if sourceBackground and not sourceBackground.isEmpty():
            backgroundCopy = sourceBackground.copyTo(iconRoot)

            # Reset the position/scale inherited from the battle panel slot.
            backgroundCopy.setPos(0, 0.01, 0)
            backgroundCopy.setHpr(0, 0, 0)
            backgroundCopy.setScale(1.25)
            backgroundCopy.show()

        # Copy the icon and any layered icon children.
        sourceNode = effectData.get('node')

        if sourceNode and not sourceNode.isEmpty():
            iconCopy = sourceNode.copyTo(iconRoot)

            iconCopy.setPos(0, -0.01, 0)
            iconCopy.setHpr(0, 0, 0)
            iconCopy.setScale(1.25)
            iconCopy.show()

        DirectLabel(
            parent=card,
            relief=None,
            text=effectData.get('title', 'Status Effect'),
            text_font=ToontownGlobals.getSuitFont(),
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


    def _getCogTitle(self):
        if not self.cog:
            return 'Cog Information'

        try:
            return self.cog.getName()
        except:
            pass

        try:
            return self.cog.getStyleName()
        except:
            return 'Cog Information'
        
    def _clearModifierLabels(self):
        for node in self.modifierLabels:
            try:
                node.destroy()
            except:
                try:
                    node.removeNode()
                except:
                    pass

        self.modifierLabels = []


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

        self._clearModifierLabels()
        self._clearStatusCards()

        DirectFrame.destroy(self)

        self.cog = None
        self.statusEffects = []
        self.modifiers = []
        self.closeCommand = None
        
class CogStatusEffectTooltip(DirectFrame):
    def __init__(self, parent=None):
        DirectFrame.__init__(
            self,
            parent=parent,
            relief=None
        )

        self.baseScale = 1.0
        self.showTrack = None

        # This creates the tooltip without depending on BattleGUI.py.
        tooltipGui = loader.loadModel(
            'phase_3.5/models/gui/battlegui/info_panels'
        )

        self.buffImage = tooltipGui.find('**/tooltip_buff')
        self.debuffImage = tooltipGui.find('**/tooltip_debuff')
        self.buffIcon = tooltipGui.find('**/buff_icon_suit')
        self.debuffIcon = tooltipGui.find('**/debuff_icon_suit')

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


class TownBattleCogPanel(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('TownBattleCogPanel')
    healthColors = (Vec4(0, 1, 0.078, 1),
                    Vec4(0.388, 1, 0, 1),
                    Vec4(0.686, 1, 0, 1),
                    Vec4(0.882, 1, 0, 1),
                    Vec4(0.988, 1, 0, 1),
                    Vec4(1, 0.831, 0, 1),
                    Vec4(1, 0.714, 0, 1),
                    Vec4(1, 0.533, 0, 1.0),
                    Vec4(1, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0.431, 0.431, 0.431, 1),  # out
                    Vec4(1, 0, 0, 1),
                    Vec4(0.0, 1.0, 1.0, 1),  # overheal
                    Vec4(0.553, 0, 1, 1),  # overcharge
                    Vec4(1, 0.416, 0.937, 1),  # 14 pink silhouette
                    Vec4(0, 0.361, 1, 1),
                    Vec4(1, 1, 1, 1),  # 15 blue silhouette
                    Vec4(186 / 255, 82 / 255, 1, 1),
                    Vec4(0.702, 0, 1, 1))  # 17 purple puls
    healthGlowColors = (Vec4(0, 1, 0.078, 1),
                        Vec4(0.388, 1, 0, 1),
                        Vec4(0.686, 1, 0, 1),
                        Vec4(0.882, 1, 0, 1),
                        Vec4(0.988, 1, 0, 1),
                        Vec4(1, 0.831, 0, 1),
                        Vec4(1, 0.714, 0, 1),
                        Vec4(1, 0.533, 0, 1.0),
                        Vec4(1, 0, 0, 1),
                        Vec4(1, 0, 0, 1),
                        Vec4(0.431, 0.431, 0.431, 1),  # out
                        Vec4(1, 0, 0, 1),
                        Vec4(0.0, 1.0, 1.0, 1),  # overheal
                        Vec4(0.553, 0, 1, 1),  # overcharge
                        Vec4(1, 0.416, 0.937, 1),  # 14 pink silhouette
                        Vec4(0, 0.361, 1, 1),
                        Vec4(1, 1, 1, 1),  # 15 blue silhouette
                        Vec4(186 / 255, 82 / 255, 1, 1),
                        Vec4(0.702, 0, 1, 1))  # 17 purple pulse
    bossBarColors = (Vec4(0.169, 1, 0, 1),
                    Vec4(0.5, 1, 0, 1),
                    Vec4(0.75, 1, 0, 1),
                    Vec4(1, 1, 0, 1),
                    Vec4(1, 0.866, 0, 1),
                    Vec4(1, 0.6, 0, 1),
                    Vec4(1, 0.5, 0, 1),
                    Vec4(1, 0.25, 0, 1.0),
                    Vec4(1, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0, 0, 0, 1),
                    Vec4(1, 0, 0, 1),
                    Vec4(0.0, 1.0, 1.0, 1),  # overheal
                    Vec4(0.741, 0, 1, 1))
    colorThresholds = (0.65, 0.4, 0.2, 0.1, 0.05)
    bossBarStartPosZ = 1.5
    bossBarEndPosZ = 0.88
    bossBarIncrementAmt = 2

    def __init__(self, id):
        if settings['newGui'] == True:
            gui = loader.loadModel('phase_3.5/models/gui/suit_panel')
        else:
            gui = loader.loadModel('phase_3.5/models/gui/suit_panel')

        DirectFrame.__init__(self, relief=None, image=gui.find('**/suit_panel_main'))
        self.initialiseoptions(TownBattleCogPanel)
        self.hidden = False
        self.cog = None
        self.statusInformationPanel = None
        self.suit = None
        self.sued = None
        self.suedRoundsText = None
        self.sued2RoundsText = None
        self.insuredText = None
        self.luredText = None
        self.dazedText = None
        self.extraAttacksText = None
        self.luredManagerText = None
        self.soakedRoundsText = None
        self.markedRoundsText = None
        self.zappedRoundsText = None
        self.vulnerabilityText = None
        self.damageReductionText = None
        self.damageMultText2 = None
        self.damageMultText = None
        self.rageBuildingText = None
        self.enrageCountText = None
        self.statusOffset = 0
        self.statusIconNodes = []
        self.statusEffectTooltip = None
        self.hoveredStatusSlot = None
        self.isLoaded = 0
        self.notify.info("Loading Cog Battle Panel!")
        self.healthText = DirectLabel(
        parent=self,
        relief=None,
        text='Level 50.exe V2.0',
        text_font=ToontownGlobals.getInterfaceFont(),
        text_scale=0.063,
        text_pos=(0.105, 0.245)
        )
        healthBarModel = loader.loadModel('phase_3.5/models/gui/suit_panel')
        self.healthNode = self.attachNewNode('health')
        self.healthNode.setPos(0, 0, 0)
        self.healthNode.setTransparency(1)
        healthGui = loader.loadModel('phase_3.5/models/gui/suit_panel')
        self.statuseffectslot = healthGui.find('**/status_effect_slot')
        self.cycleBackButton = DirectButton(
        parent=self,
        relief=None,
        image=(
            healthBarModel.find('**/Arrow_Nuetral'),
            healthBarModel.find('**/Arrow_Press'),
            healthBarModel.find('**/arrow_hover')
        ),
        frameSize=(-0.3, 0.3, -0.15, 0.2),
        pos=(-0.236, 0, 0.03),
        scale=(-0.242, 1, 0.22),
        command=self.changeStatusOffset,
        extraArgs=[-1]
        )

        self.cycleForwardButton = DirectButton(
            parent=self,
            relief=None,
            image=(
                healthBarModel.find('**/Arrow_Nuetral'),
                healthBarModel.find('**/Arrow_Press'),
                healthBarModel.find('**/arrow_hover')
            ),
            frameSize=(-0.3, 0.3, -0.15, 0.2),
            pos=(0.236, 0, 0.03),
            scale=(0.242, 1, 0.22),
            command=self.changeStatusOffset,
            extraArgs=[1]
        )
        # button = healthGui.find('**/status_effect_slot')
        # button.setScale(0.63)
        # button.setH(0)
        # button.setR(0)
        # button.setColor(Vec4(0, 0, 0, 0))
        # healthBar = healthBarModel.find('**/status_effect_slot')
        # self.healthBar = healthBar
        # healthBar.setScale(0.63)
        # healthBar.setH(0)
        # healthBar.setR(0)
        # healthBar.reparentTo(self.healthNode)
        self.healthBarBackground = DirectFrame(
        parent=self,
        relief=None,
        image=healthBarModel.find('**/suit_panel_health'),
        pos=(0.097, 0, 0.16),
        scale=(0.5, 1, 0.125)
    )
        self.healthBar2 = DirectFrame(
        parent=self,
        relief=None,
        image=healthBarModel.find('**/suit_panel_health'),
        pos=(0.097, 0, 0.16),
        scale=(0.5, 1, 0.125)
    )
        self.healthBarClippingPlane = PlaneNode('clippingPlane')
        self.healthBarClippingPlane.setPlane(Plane(Vec3(-1, 0, 0), Point3(0, 0, 0)))
        clipNP = self.healthBar2.attachNewNode(self.healthBarClippingPlane)
        self.healthBar2.setClipPlane(clipNP)
        self.infoButton = DirectButton(
        parent=self,
        relief=None,
        image=(
            healthBarModel.find('**/Info_Nuetral'),
            healthBarModel.find('**/Info_Press'),
            healthBarModel.find('**/Info_Hover')
        ),
        frameSize=(-0.17, 0.12, -0.22, 0.22),
        pos=(0.36, 0, 0.161),
        scale=0.25,
        command=self.activateInfoButton
    )
       # infoButton.reparentTo(self.healthNode)
       # self.infoButton = infoButton
        # self.infoButton.setScale(0.275)
        # self.infoButton.setH(0)
        # self.infoButton.setR(0)
        # self.infoButton.setPos(.235, 0, -.035)
        self.accept('inventory-levels', self.__handleToggle)
       # button.reparentTo(self.healthNode)
        #self.healthBar2.reparentTo(self.healthNode)
       # infoButton.reparentTo(self.healthNode)
        self.hpText = DirectLabel(
        parent=self,
        relief=None,
        text='99999/99999',
        text_font=ToontownGlobals.getInterfaceFont(),
        text_scale=0.0685,
        text_pos=(0.09, 0.1425)
    )
        self.setScale(0.525)
        #self.button = button
        self.head = None
        self.suitHead = None
        self.blinkTask = None
        self.hide()
        self.statusEffectTooltip = CogStatusEffectTooltip(parent=self)
        self.statusEffectTooltip.setPos(0, 0, -0.34)
        self.statusEffectTooltip.setScale(2)
        self.statusEffectTooltip.hide()
        healthGui.removeNode()
        gui.removeNode()
    

    def rebuild(self, effects=None):
        if effects is not None:
            self.effects = effects

        self._clearRows()

        canvas = self.scrolledFrame.getCanvas()

        if not self.effects:
            emptyLabel = DirectLabel(
                parent=canvas,
                relief=None,
                text='This Cog has no visible status effects.',
                text_font=ToontownGlobals.getInterfaceFont(),
                text_fg=(0.1, 0.1, 0.1, 1),
                text_scale=0.038,
                text_wordwrap=24,
                pos=(0, 0, 0.035)
            )

            self.effectRows.append(emptyLabel)
            self.scrolledFrame['canvasSize'] = (
                -0.39, 0.39, -0.18, 0.105
            )
            return

        rowHeight = 0.14
        firstRowZ = 0.045

        for index, effectData in enumerate(self.effects):
            rowZ = firstRowZ - (index * rowHeight)

            row = self._createEffectRow(
                canvas,
                effectData,
                rowZ
            )

            self.effectRows.append(row)

        requiredHeight = max(
            0.285,
            len(self.effects) * rowHeight
        )

        self.scrolledFrame['canvasSize'] = (
            -0.39,
            0.39,
            -requiredHeight + 0.105,
            0.105
        )

        # Reset scrolling to the top.
        self.scrolledFrame.verticalScroll['value'] = 0

    def _getCogInformationModifiers(self):
        modifiers = []
        attributes = SuitBattleGlobals.SuitAttributes[self.cog.dna.name]
        hpType = attributes.get('hp', 'normal')

        if hpType == 'operations':
            modifiers.append({
                'title': 'Operations Analyst',
                'value': '',
                'description': (
                    'Has high health and dodge chance, but deals low damage.'
                ),
                'positive': True,
            })
        if hpType == 'field':
            modifiers.append({
                'title': 'Field Specialist',
                'value': '',
                'description': (
                    'Deals high damage, but has low health and dodge chance.'
                ),
                'positive': True,
            })
    #         text = addText(text,
    #                     '\1TextSubtitle\1{SuitAttributeDefense}:\2\n{TTLocalizer.SuitAttributeDescriptions[SuitAttributeDefense]}')
    #     if av.dna.name in ['fcs', 'txm', 'key', 'fct', 'nn', 'blh', 'ath',  'bfh2', 'ppl', 'pyc', 'trs', 'sh', 'bsht', 'wnk', 'br', 'txm', 'chw', 'bfh', 'cnd', 'itn', 'std', 'std2']:
    #         text = addText(text,
    #                     '\1TextSubtitle\1{SuitAttributeAttack}:\2\n{TTLocalizer.SuitAttributeDescriptions[SuitAttributeAttack]}')

        if self.cog.getGovernaught() and not self.cog.dna.name in ['std2', 'mh2', 'cnd2']:
            modifiers.append({
                'title': 'Advanced',
                'value': '',
                'description': (
                    'Has increased health, cannot be fired or sued. Defeating this cog will grant a damage boost.'
                ),
                'positive': True,
            })

        if self.cog.getManager():
            modifiers.append({
                'title': 'Manager',
                'value': '',
                'description': (
                     'Cannot be fired or sued. Has dangerous special abilities.'
                ),
                'positive': True,
            })

        if self.cog.getExecutive() or self.cog.dna.name in ['std2', 'mh2', 'cnd2']:
            modifiers.append({
                'title': 'Executive',
                'value': '',
                'description': (
                     'Has increased health and damage.'
                ),
                'positive': True,
            })

        if self.cog.getSkeleRevives() >= 2:
            modifiers.append({
                'title': 'v3.0',
                'value': '',
                'description': (
                     'Has 2 layers with less health, but increased damage.'
                ),
                'positive': True,
            })
        elif self.cog.getSkeleRevives() >= 1:
            modifiers.append({
                'title': 'v2.0',
                'value': '',
                'description': (
                     'Has a second layer with less health, but increased damage.',
                ),
                'positive': True,
            })

        if not self.cog.getExecutive() and not self.cog.getSkeleRevives() > 1 and not self.cog.getManager() and not self.cog.getGovernaught() and not hpType == 'operations' and not hpType == 'field':
            modifiers.append({
                'title': 'Employee',
                'value': '',
                'description': (
                     'No special modifications have been made to this Cog.'
                ),
                'positive': True,
            })

        return modifiers

    def _createEffectRow(self, parent, effectData, z):
        isBuff = effectData.get('buff', True)

        if isBuff:
            rowColor = (0.75, 1.0, 0.75, 0.5)
        else:
            rowColor = (1.0, 0.75, 0.75, 0.5)

        row = DirectFrame(
            parent=parent,
            relief=DGG.FLAT,
            frameColor=rowColor,
            frameSize=(-0.375, 0.345, -0.058, 0.058),
            pos=(0, 0, z)
        )

        iconHolder = row.attachNewNode('effect-icon-holder')
        iconHolder.setPos(-0.31, 0, 0)
        iconHolder.setScale(0.07)

        sourceNode = effectData.get('node')

        if sourceNode and not sourceNode.isEmpty():
            iconCopy = sourceNode.copyTo(iconHolder)
            iconCopy.setPos(0, 0, 0)
            iconCopy.setScale(1)
            iconCopy.show()

        title = effectData.get('title', 'Status Effect')
        description = effectData.get(
            'description',
            'No description available.'
        )

        DirectLabel(
            parent=row,
            relief=None,
            text=title,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_fg=(0, 0, 0, 1),
            text_align=TextNode.ALeft,
            text_scale=0.035,
            text_wordwrap=20,
            pos=(-0.255, 0, 0.021)
        )

        DirectLabel(
            parent=row,
            relief=None,
            text=description,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_fg=(0.1, 0.1, 0.1, 1),
            text_align=TextNode.ALeft,
            text_scale=0.025,
            text_wordwrap=33,
            pos=(-0.255, 0, -0.012)
        )

        return row

    def _clearRows(self):
        for row in self.effectRows:
            try:
                row.destroy()
            except:
                try:
                    row.removeNode()
                except:
                    pass

        self.effectRows = []

    def close(self):
        callback = self.closeCommand
        self.closeCommand = None

        self.destroy()

        if callback:
            callback()

    def destroy(self):
        self._clearRows()

        DirectFrame.destroy(self)

        self.cog = None
        self.effects = []
        self.closeCommand = None

    def activateInfoButton(self):
        if self.statusInformationPanel:
            self.closeStatusInformationPanel()
            return

        if not self.cog:
            return

        self.statusInformationPanel = CogStatusInformationPanel(
            cog=self.cog,
            statusEffects=list(self.statusIconNodes),
            modifiers=self._getCogInformationModifiers(),
            closeCommand=self._statusInformationPanelClosed
        )

        self.statusInformationPanel.show()


    def _statusInformationPanelClosed(self):
        self.statusInformationPanel = None


    def closeStatusInformationPanel(self):
        panel = self.statusInformationPanel
        self.statusInformationPanel = None

        if panel:
            try:
                panel.destroy()
            except:
                pass

    def setCogInformation(self, cog):
        self.cleanupHead()
        self.cog = cog
        self.updateHealthBar()
        # if self.healthBar2:
        #     self.healthBar2.setProp('range', self.cog.getMaxHP())

        self.generateSuitHead(cog.getStyleName())
       # self.setLevelText()

    def _clear_status_node(self, attrName):
        node = getattr(self, attrName, None)
        if node is not None:
            try:
                node.removeNode()
            except:
                pass
            setattr(self, attrName, None)

    def _clear_status_interval(self, attrName):
        interval = getattr(self, attrName, None)
        if interval is not None:
            try:
                interval.finish()
            except:
                pass
            setattr(self, attrName, None)

    def _cleanupStatusDisplay(self):
        self.statusEffects = 0
        self.statusOffset = 0
        self.statusIconNodes = []
        self.statusSlotColors = []
        self.statusSlotPulses = []
        self.statusSlotPulseTypes = []
        taskMgr.remove(self.uniqueName('overcharge-pulse-task'))
        if self.statusEffectTooltip:
            self.statusEffectTooltip.hide()

        self.hoveredStatusSlot = None

        if hasattr(self, 'statusSlots'):
            for slot in self.statusSlots:
                if not slot:
                    continue

                iconRotations = slot.get('iconRotations', [])

                for rotation in iconRotations:
                    try:
                        rotation.finish()
                    except:
                        pass

                slot['iconRotations'] = []

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
                'attackIcon', 'attackIcon1', 'attackIcon2', 'attackIcon3',
                'attackIcon4', 'attackIcon5', 'attackIcon6', 'attackIcon7',
                'status', 'status2', 'status3', 'status4', 'attackIcon8', 'attackIcon9',
                'status5', 'status6', 'status7', 'status8', 'status9', 'status10',
                'statusFrame', 'desperationText', 'desperation', 'collectcall',
                'collectcallText', 'luredText', 'damageMultText', 'damageMultText2',
                'extraAttacks', 'sued', 'sued2', 'suedRoundsText', 'sued2RoundsText',
                'extraAttacksText', 'dazed', 'dazedText', 'enrageCountText',
                'soakedRoundsText', 'soaked', 'marked', 'zapped', 'insuredRoundsText', 'contractedRoundsText',
                'zappedRoundsText', 'markedRoundsText', 'enraged', 'shielding',
                'skeleton', 'virtual', 'damageUp', 'overcharged', 'insured',
                'insuredText', 'vulnerabilityText', 'damageReductionText',
                'luredCog', 'luredManagerText', 'rageBuildingText', 'immortal',
                'luredManager', 'syphon', 'vulnerable', 'soakResist', 'extraText', 'statusIcon', 'statusIcon2',
                'absorbing', 'damageReduction', 'lureImmune', 'rainbow',
                'hollywoods', 'sharkwatcher', 'statusFramePanel'
        ):
            self._clear_status_node(name)

        if hasattr(self, 'statusSlots'):
            for slot in self.statusSlots:
                try:
                    slot['bgModel'].removeNode()
                except:
                    pass
                try:
                    slot['iconRoot'].removeNode()
                except:
                    pass

        self.statusSlots = []
        self.statusEffects = 0

    def _buildStatusSlots(self):
        slotLayouts = [
            (-0.21, 0, -0.068),  # 1
            (-0.081, 0, -0.166),  # 2
            (0.081, 0, -0.166),  # 3
            (0.21, 0, -0.068),  # 4
            (-0.37, 0.4, 0.23),  # 5
            (-0.21, 0.4, 0.23),  # 6
            (-0.05, 0.4, 0.23),  # 7
            (0.11, 0.4, 0.23),  # 8
            (0.27, 0.4, 0.23),  # 9
            (-0.53, 0.4, 0.23),  # 10
        ]

        self.statusSlots = [None] * len(slotLayouts)

        for i in reversed(range(len(slotLayouts))):
            x, y, z = slotLayouts[i]

            bgModel = loader.loadModel('phase_3.5/models/gui/status_effects')
            bgNode = bgModel.find('**/default_background')
            bgNode.reparentTo(self.healthNode)
            bgNode.setPosHprScale(x, y, z, 0, 0, 0, .16, .16, .16)
            bgNode.setColor(1, 1, 1, 1)

            iconRoot = self.healthNode.attachNewNode('statusIconRoot-%d' % i)
            iconRoot.setPosHprScale(x, y, z, 0, 0, 0, .15, .15, .15)
            hoverButton = DirectButton(
                    parent=self.healthNode,
                    relief=DGG.FLAT,
                    frameColor=(0, 0, 0, 0),
                    frameSize=(-0.5, 0.5, -0.5, 0.5),
                    pos=(x, -0.05, z),
                    scale=0.16,
                    state=DGG.NORMAL
                )

            hoverButton.bind(
                    DGG.WITHIN,
                    self._enterStatusSlot,
                    extraArgs=[i]
                )

            hoverButton.bind(
                    DGG.WITHOUT,
                    self._exitStatusSlot,
                    extraArgs=[i]
                )

            if i >= 4:
                bgNode.hide()
                iconRoot.hide()
                hoverButton.hide()

            self.statusSlots[i] = {
                'bgModel': bgModel,
                'bg': bgNode,
                'iconRoot': iconRoot,
                'hoverButton': hoverButton,
                'effectIndex': None,
                'pulse': None,
                'iconRotations': [],
            }

        # self.status = self.statusSlots[0]['bgModel']
        # self.status2 = self.statusSlots[1]['bgModel']
        # self.status3 = self.statusSlots[2]['bgModel']
        # self.status4 = self.statusSlots[3]['bgModel']
        # self.status5 = self.statusSlots[4]['bgModel']
        # self.status6 = self.statusSlots[5]['bgModel']
        # self.status7 = self.statusSlots[6]['bgModel']
        # self.status8 = self.statusSlots[7]['bgModel']
        # self.status9 = self.statusSlots[8]['bgModel']
        # self.status10 = self.statusSlots[9]['bgModel']

        # self.attackIcon = self.statusSlots[0]['bg']
        # self.attackIcon1 = self.statusSlots[1]['bg']
        # self.attackIcon2 = self.statusSlots[2]['bg']
        # self.attackIcon3 = self.statusSlots[3]['bg']
        # self.attackIcon4 = self.statusSlots[4]['bg']
        # self.attackIcon5 = self.statusSlots[5]['bg']
        # self.attackIcon6 = self.statusSlots[6]['bg']
        # self.attackIcon7 = self.statusSlots[7]['bg']
        # self.attackIcon8 = self.statusSlots[8]['bg']
        # self.attackIcon9 = self.statusSlots[9]['bg']

    def _rotateStatusIcon(
            self,
            slot,
            iconNode,
            duration=4.0,
            clockwise=True):

        if slot is None:
            return

        if iconNode is None or iconNode.isEmpty():
            return

        endRoll = -360 if clockwise else 360

        rotation = LerpHprInterval(
            iconNode,
            duration,
            Vec3(0, 0, endRoll),
            startHpr=Vec3(0, 0, 0)
        )

        rotation.loop()

        slot['iconRotations'].append(rotation)

    def _stopSlotPulse(self, slot):
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

    def _claimNextStatusSlot(self):
        if self.statusEffects >= len(self.statusSlots):
            return None

        slot = self.statusSlots[self.statusEffects]
        self.statusEffects += 1
        return slot
    
    def _attachStatusIcons(
        self,
        iconNodes,
        slot,
        tooltipKey=None,
        tooltipTitle=None,
        tooltipDescription=None,
        tooltipBuff=True,
        slotColor=(1, 1, 1, 1),
        layerSettings=None):

        if slot is None:
            return

        if not isinstance(iconNodes, (list, tuple)):
            iconNodes = [iconNodes]

        if layerSettings is None:
            layerSettings = []

        slot['bg'].setColor(*slotColor)
        slot['bg'].setColorScale(1, 1, 1, 1)

        layerRoot = slot['iconRoot'].attachNewNode(
            'status-effect-layers-%d' % self.statusEffects
        )

        validIcons = []

        for index, iconNode in enumerate(iconNodes):
            if iconNode is None or iconNode.isEmpty():
                continue

            settings = (
                layerSettings[index]
                if index < len(layerSettings)
                else {}
            )

            scale = settings.get('scale', (1, 1, 1))
            pos = settings.get('pos', (0, 0, 0))
            hpr = settings.get('hpr', (0, 0, 0))
            color = settings.get('color', (1, 1, 1, 1))

            if isinstance(scale, (int, float)):
                scale = (scale, scale, scale)

            iconNode.reparentTo(layerRoot)
            iconNode.setPos(*pos)
            iconNode.setHpr(*hpr)
            iconNode.setScale(*scale)
            iconNode.setColor(*color)
            iconNode.show()

            validIcons.append(iconNode)

        tooltipData = SUIT_STATUS_TOOLTIPS.get(
            tooltipKey,
            {}
        )

        effectData = {
        'node': layerRoot,
        'background': slot['bg'],
        'slotColor': slotColor,
        'icons': validIcons,
        'tooltipKey': tooltipKey,
        'title': tooltipTitle or tooltipData.get(
            'title',
            self._formatStatusName(tooltipKey)
        ),
        'description': tooltipDescription or tooltipData.get(
            'description',
            'No description available.'
        ),
        'buff': tooltipData.get(
            'buff',
            tooltipBuff
        ),
    }

        self.statusIconNodes.append(effectData)
        self.statusSlotColors.append(slotColor)
        self.statusSlotPulses.append(None)
        self.statusSlotPulseTypes.append(None)

    def _attachStatusIcon(
        self,
        iconNode,
        slot,
        tooltipKey=None,
        tooltipTitle=None,
        tooltipDescription=None,
        tooltipBuff=True,
        slotColor=(1, 1, 1, 1),
        scale=(1, 1, 1)):

        self._attachStatusIcons(
        [iconNode],
        slot,
        tooltipKey=tooltipKey,
        tooltipTitle=tooltipTitle,
        tooltipDescription=tooltipDescription,
        tooltipBuff=tooltipBuff,
        slotColor=slotColor,
        layerSettings=[
            {
                'scale': scale,
            }
        ]
    )

    def _formatStatusName(self, name):
        if not name:
            return 'Status Effect'

        text = ''

        for character in name:
            if character.isupper() and text:
                text += ' '
            text += character

        return text[:1].upper() + text[1:]
    
    def _enterStatusSlot(self, slotIndex, event=None):
        if not self.statusEffectTooltip:
            return

        if slotIndex < 0 or slotIndex >= len(self.statusSlots):
            return

        slot = self.statusSlots[slotIndex]
        effectIndex = slot.get('effectIndex')

        if effectIndex is None:
            self.statusEffectTooltip.hide()
            return

        if effectIndex < 0 or effectIndex >= len(self.statusIconNodes):
            self.statusEffectTooltip.hide()
            return

        effectData = self.statusIconNodes[effectIndex]

        title = effectData.get('title', 'Status Effect')
        description = effectData.get('description', 'No available description.')
        isBuff = effectData.get('buff', True)

        if not description:
            description = 'This Cog is affected by %s.' % title

        self.statusEffectTooltip.setEffect(
            title,
            description,
            isBuff
        )

        self.hoveredStatusSlot = slotIndex
        self.statusEffectTooltip.show()

    def _exitStatusSlot(self, slotIndex, event=None):
        if self.hoveredStatusSlot == slotIndex:
            self.hoveredStatusSlot = None

            if self.statusEffectTooltip:
                self.statusEffectTooltip.hide()

    def _pulseRainbowStatusSlot(self, slot, duration=0.35):
        if slot is None:
            return

        index = self.statusEffects - 1

        if index >= 0 and index < len(self.statusSlotPulses):
            self.statusSlotPulseTypes[index] = 'rainbow'
            self.statusSlotPulses[index] = (duration,)

        self._pulseRainbowStatusSlotVisible(slot, duration)

    def _pulseStatusSlot(self, slot, fromColor, toColor=(1, 1, 1, 1), duration=1.0):
        if slot is None:
            return

        index = self.statusEffects - 1

        if index >= 0 and index < len(self.statusSlotPulses):
            self.statusSlotPulseTypes[index] = 'normal'
            self.statusSlotPulses[index] = (fromColor, toColor, duration)

        self._pulseStatusSlotVisible(slot, fromColor, toColor, duration)

    def _pulseRainbowStatusSlotVisible(self, slot, duration=0.35):
        self._stopSlotPulse(slot)

        slot['pulse'] = Sequence(
            LerpColorScaleInterval(slot['bg'], duration, (1, 0, 0, 1), blendType='easeInOut'),
            LerpColorScaleInterval(slot['bg'], duration, (1, 0.5, 0, 1), blendType='easeInOut'),
            LerpColorScaleInterval(slot['bg'], duration, (1, 1, 0, 1), blendType='easeInOut'),
            LerpColorScaleInterval(slot['bg'], duration, (0, 1, 0, 1), blendType='easeInOut'),
            LerpColorScaleInterval(slot['bg'], duration, (0, 0, 1, 1), blendType='easeInOut'),
            LerpColorScaleInterval(slot['bg'], duration, (0.29, 0, 0.51, 1), blendType='easeInOut'),
            LerpColorScaleInterval(slot['bg'], duration, (0.56, 0, 1, 1), blendType='easeInOut')
        )
        slot['pulse'].loop()

    def setLevelText(self):
        for taskName in (
                'overcharge-pulse-task',
                'rainbow-pulse-task',
        ):
            taskMgr.remove(self.uniqueName(taskName))
        self._cleanupStatusDisplay()
        self._buildStatusSlots()

        # Shark Watcher and Leveling Information
        if self.cog.dna.name == 'hrollers':
            t = 'Level 25'
        elif self.cog.isShadow:
            t = 'Level 30'
        elif self.cog.dna.name == 'clubpres':
            if self.cog.getActualLevel() == 20:
                t = 'Level 21'
            elif self.cog.getActualLevel() == 26:
                t = 'Level 21'
            elif self.cog.getActualLevel() == 27:
                t = 'Level 26'
            else:
                t = 'Level ' + str(self.cog.getActualLevel())
        elif self.cog.dna.name == 'supervis':
            if self.cog.getActualLevel() == 24:
                t = 'Level 28'
            elif self.cog.getActualLevel() == 23:
                t = 'Level 24'
            elif self.cog.getActualLevel() == 27:
                t = 'Level 23'
            elif self.cog.getActualLevel() == 28:
                t = 'Level 24'
            elif self.cog.getActualLevel() == 29:
                t = 'Level 27'
            elif self.cog.getActualLevel() == 30:
                t = 'Level 25'
            else:
                t = 'Level ' + str(self.cog.getActualLevel())
        elif self.cog.dna.name == 'clerk':
            if self.cog.getActualLevel() == 27:
                t = 'Level 24'
            elif self.cog.getActualLevel() == 28:
                t = 'Level 21'
            elif self.cog.getActualLevel() == 24:
                t = 'Level 25'
            elif self.cog.getActualLevel() == 25:
                t = 'Level 26'
            elif self.cog.getActualLevel() == 21:
                t = 'Level 23'
            elif self.cog.getActualLevel() == 23:
                t = 'Level 24'
            else:
                t = 'Level ' + str(self.cog.getActualLevel())
        elif self.cog.dna.name == 'foreman':
            if self.cog.getActualLevel() == 27:
                t = 'Level 21'
            elif self.cog.getActualLevel() == 27:
                t = 'Level 25'
            elif self.cog.getActualLevel() == 28:
                t = 'Level 26'
            elif self.cog.getActualLevel() == 29:
                t = 'Level 28'
            else:
                t = 'Level ' + str(self.cog.getActualLevel())
        else:
            t = 'Level ' + str(self.cog.getActualLevel())
        if self.cog.getExecutive() or self.cog.getManager() or self.cog.getGovernaught():
            if self.cog.getManager():
                t += TTLocalizer.ManagerPostFix
            elif self.cog.getExecutive() or self.cog.dna.name in ['std2', 'mh2', 'cnd2']:
                t += TTLocalizer.ExecutivePostFix
            elif self.cog.dna.name not in ['std2', 'cnd2', 'mh2']:
                t += TTLocalizer.GovernaughtPostFix
            else:
                t += '.str'
        if self.cog.getSkeleRevives() > 0:
            t += TTLocalizer.SkeleRevivePostFix % (self.cog.getSkeleRevives() + 1)

        # Status Effects
        if self.cog.isVirtual:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/virtual_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Virtualized', 
                                   tooltipDescription="This Cog's hardware has been virtualized! Due to their abstract nature, negative effects applied by Toons will last -2 less rounds.", 
                                   tooltipBuff=True, 
                                   slotColor=(0.361, 0.361, 0.361, 1))

        if self.cog.isSkeleton:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/skelecog_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Skeletal Structure', 
                                   tooltipDescription='Due to their reduced volume, this Cog has a varied amount of their max HP and negative effects applied by Toons will last for -1 less round!', 
                                   tooltipBuff=True, 
                                   slotColor=(0.722, 0.722, 0.722, 1))

        if self.cog.getManager() or self.cog.getGovernaught() or self.cog.hasSuitStatusEffect('lureResist') or self.cog.hasSuitStatusEffect('insured') or self.cog.hasSuitStatusEffect('insured2') or self.cog.healthCondition == 13:
            if (self.cog.isDesperation and (self.cog.hasSuitStatusEffect('enraged') and self.cog.dna.name == 'sgoat')) or self.cog.hasSuitStatusEffect('videographerImmune') or self.cog.hasSuitStatusEffect('silhouetteImmune') or self.cog.hasSuitStatusEffect('lureImmune') or self.cog.hasSuitStatusEffect('highRollerImmune') or self.cog.hasSuitStatusEffect('immune') or (self.cog.getActualLevel() == 25 and self.cog.dna.name == 'hrollers') or self.cog.hasSuitStatusEffect('lureResist'):
                status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status2.find('**/lured_prestige_icon')
                status = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
                self.statusIcon2 = status.find('**/minnieX')
                self.statusIcon2.setColorScale(1, 0, 0, 1)
                slot = self._claimNextStatusSlot()
                self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Lure Resistance', 
                                    tooltipDescription="This Cog is entirely immune to being LURED.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                             'scale': (2.75, 2.75, 2.75),
                                            'pos': (0, 0, -0.05),
                                        },
                                    ])
                self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))
            elif (self.cog.hasSuitStatusEffect('desperation') and not self.cog.hasSuitStatusEffect('unionBusterNoAttack')) or self.cog.hasSuitStatusEffect('closedSession') or self.cog.dna.name in ('bcaster', 'chainsaw', 'psetter', 'mslacker', 'pcrat', 'whunter', 'prethink', 'mplayer', 'hroller', 'hroller2', 'videog', 'fires', 'fbed', 'mouthp', 'rainmake', 'whunter', 'wsi', 'redd', 'duckshfl', 'treek', 'director', 'bellring', 'ddiver', 'gatekeep')\
                    or (self.cog.isVulnerable and self.cog.dna.name == 'wtapper') or self.cog.hasSuitStatusEffect('silhouetteShielding') or (self.cog.healthCondition == 13 and self.cog.isSkeleton) or (self.cog.hasSuitStatusEffect('enraged') and self.cog.dna.name == 'sgoat'):
                status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status2.find('**/lured_prestige_icon')
                status = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
                self.statusIcon2 = status.find('**/minnieX')
                self.statusIcon2.setColorScale(1, 0, 0, 1)
                slot = self._claimNextStatusSlot()
                self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Lure Resistance', 
                                    tooltipDescription="This Cog will stay lured for 1 round.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                             'scale': (2.75, 2.75, 2.75),
                                             'pos': (0, 0, -0.05),
                                        },
                                    ])
            else:
                status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status2.find('**/lured_prestige_icon')    
                status = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
                self.statusIcon2 = status.find('**/minnieX')
                self.statusIcon2.setColorScale(1, 0, 0, 1)
                slot = self._claimNextStatusSlot()
                self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Lure Resistance', 
                                    tooltipDescription="This Cog will stay lured for 2 rounds.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                             'scale': (2.75, 2.75, 2.75),
                                             'pos': (0, 0, -0.05),
                                        },
                                    ])

        if self.cog.healthCondition == 13:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/overcharge_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                slot, 
                                tooltipTitle='Overcharged', 
                                tooltipDescription="This Cog is Overcharged! While Overcharged, they have high Lure resistance, deal +50% more damage, and receive the same benefits as Manager Cogs.", 
                                tooltipBuff=True, 
                                slotColor=(1, 1, 1, 1), scale=(.9, .9, .9))
            self._pulseStatusSlot(slot, fromColor=(0.992, 0.227, 1, 1), toColor=(self.healthColors[13]))

        if self.cog.healthCondition == 12:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/schadenfreude_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                slot, 
                                tooltipTitle='Overhealed', 
                                tooltipDescription="This Cog is Overhealed! While Overhealed, they will deal +25% more damage.", 
                                tooltipBuff=True, 
                                slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('highRollerImmune') and not self.cog.hasSuitStatusEffect('highRollerHijinks'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/insured_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                slot, 
                                tooltipTitle='Minigame Host', 
                                tooltipDescription="The High Roller is entirely immune to all Gags! Destroy his contestants to damage him.", 
                                tooltipBuff=True, 
                                slotColor=(1, 0.984, 0, 1))
            
        if self.cog.hasSuitStatusEffect('videographerImmune'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/insured_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                slot, 
                                tooltipTitle="Producer's Cuts", 
                                tooltipDescription="The Videographer will be immune to all Gags until the Producers are defeated! He will also not attack during this phase.",  
                                tooltipBuff=True, 
                                slotColor=(1, 0.984, 0, 1))
            
        if self.cog.hasSuitStatusEffect('videoStatic'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/videoStatic.png')
            self.statusIcon.setTexture(texture, 1)
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                slot, 
                                tooltipTitle='Video Static', 
                                tooltipDescription="The Videographer's broadcast is being interrupted! He is dealing and taking +%s%% more damage." % self.cog.getSuitStatusModifier('videoStatic'),  
                                tooltipBuff=True, 
                                slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('highRollerHijinks'):
            status2 = loader.loadModel('phase_3.5/models/props/ttcc_gen_starburst')
            self.statusIcon = status2.find('**/starburst')
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon2 = status.find('**/hollywood_hijinks_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                   slot, 
                                   tooltipTitle='Videographer Hijinks', 
                                   tooltipDescription="High Roller is on his last commercial break! Defeat the Videographer and his associates to progress.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1),
                                   layerSettings=[
                                        {
                                            'scale': (.5, .5, .5),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (1, 1, 1),
                                            'pos': (0, 0, 0),
                                        },])
            self._rotateStatusIcon(slot, self.statusIcon, duration=4.0)

        if self.cog.hasSuitStatusEffect('refractionBarrier'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/shield_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Refraction Barrier', 
                                   tooltipDescription="This Silhouette is a strange being of light! Attacks will do -%s%% less damage on it!" % self.cog.getSuitStatusModifier('refractionBarrier'),  
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1), scale=(.9, .9, .9))

        if self.cog.hasSuitStatusEffect('silhouetteShielding'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/harmonious_colors_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                slot, 
                                tooltipTitle='Harmonious Colors', 
                                tooltipDescription="The colors, they are so pretty... High Roller's Silhouettes are causing him to take 90% less damage!", 
                                tooltipBuff=True, 
                                slotColor=(1, 0.984, 0, 1))
            self._pulseRainbowStatusSlot(slot, duration=2.0)

        if self.cog.hasSuitStatusEffect('silhouetteImmune'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/harmonious_colors_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                slot, 
                                tooltipTitle='Harmonious Colors', 
                                tooltipDescription="The colors, they are so pretty... High Roller is currently INVINCIBLE!!", 
                                tooltipBuff=True, 
                                slotColor=(1, 0.984, 0, 1))
            self._pulseRainbowStatusSlot(slot, duration=2.0)

        # if self.cog.dna.name == 'hustle':
        #     status = loader.loadModel('phase_3.5/models/gui/status_effects')
        #     self.enraged = status.find('**/last_tap_icon')
        #     texture = loader.loadTexture(
        #         'phase_3.5/maps/battlegui/status_effects_palette_4allc_12.png'
        #     )

        #     self.enraged.clearTexture()
        #     self.enraged.setTexture(texture, 1)
        #     slot = self._claimNextStatusSlot()
        #     self._attachStatusIcon(self.enraged, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.dna.name == 'hrollers':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            if self.cog.getActualLevel() == 36:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/confusion_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle='0RD3R 5W4P', 
                                    tooltipDescription="This Silhouette keeps reorganizing the office! Don't get too comfortable with your Gag Order, it won't stay that way for long.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1))
                self._pulseRainbowStatusSlot(slot, duration=2.0)
            if self.cog.getActualLevel() == 35:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/damage_absorb_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle='5H13LD W4LL', 
                                    tooltipDescription="This Silhouette refuses to let it's friends take the fall! It will intercept and reduce damage dealt to nearby Silhouettes.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1))
                self._pulseRainbowStatusSlot(slot, duration=2.0)
            if self.cog.getActualLevel() == 34:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/ink_drain_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle='L1F3 5YPH0N', 
                                    tooltipDescription="This Silhouette is collecting mandatory Laff deductions! The healthier you are, the healhier it becomes.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1))
                self._pulseRainbowStatusSlot(slot, duration=2.0)
            if self.cog.getActualLevel() == 33:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/unite_cooldown_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle='C45H 1NFU510N', 
                                    tooltipDescription="This Silhouette is making a generous corporate donation! It will gladly give it's own Health to keep the High Roller in business.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1))
                self._pulseRainbowStatusSlot(slot, duration=2.0)
            if self.cog.getActualLevel() == 32:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/cashback_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle='C45HB4CK', 
                                    tooltipDescription="This Silhouette is making sure the Toons don't get too cheery! It will retaliate against the Toons you heal.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1))
                self._pulseRainbowStatusSlot(slot, duration=2.0)
            if self.cog.getActualLevel() == 31:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/duck_drop_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle='J0K3R', 
                                    tooltipDescription="This Silhouette is messing with your Gags?? Your Gags will occasionally get demoted or promoted. He ESPECIALLY loves messing with Drop Gags...", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), scale=(.8, .8, .8))
                self._pulseRainbowStatusSlot(slot, duration=2.0)
            if self.cog.getActualLevel() == 30:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/backfire_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle='SPL45HB4CK', 
                                    tooltipDescription="This Silhouette loves water parks! It's reflective properties will cause your Squirt Gags to bounce back to you! Silhouettes will receive a 50% damage resistance effect when Soaked.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), scale=(1.1, 1.1, 1.1))
                self._pulseRainbowStatusSlot(slot, duration=2.0)
            if self.cog.getActualLevel() == 29:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/trap_card_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle='TR4P-C4RD', 
                                    tooltipDescription="This Silhouette is eager to play it's Trap Card! It will use a powerful group attack if left unlured or if Trap Gags are placed on the field.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1))
                self._pulseRainbowStatusSlot(slot, duration=2.0)
            if self.cog.getActualLevel() == 28:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/singing_blues_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle="S1NG1N' BLU35", 
                                    tooltipDescription="This Silhouette takes the wind out of your sails! It will knock the wind of you for a small amount of time.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1))
                self._pulseRainbowStatusSlot(slot, duration=2.0)
            if self.cog.getActualLevel() == 27:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/fizzle_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle="F1ZZL3", 
                                    tooltipDescription="This Silhouette wore a rubber suit to work today! It will reduce your Zap damage by a lot.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1))
                self._pulseRainbowStatusSlot(slot, duration=2.0)
            if self.cog.getActualLevel() == 26:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/full_deck_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle="F4C3 V4LU3", 
                                    tooltipDescription="This Silhouette HATES teamwork! It refuses to let it or it's friends deal with your combo damage.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1))
                self._pulseRainbowStatusSlot(slot, duration=2.0)
            if self.cog.getActualLevel() == 25:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/no_green_light_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle="GR33NL1GHT3R", 
                                    tooltipDescription="This Silhouette is practicing persuasion prevention! It will make different Silhouettes lure immune every round, and refuses to let it or it's friend deal with your knockback damage.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1))
                self._pulseRainbowStatusSlot(slot, duration=2.0)

        if self.cog.dna.name == 'ubuster':
            status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status2.find('**/attack_icon')
            self.statusIcon2 = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/tax_collector.png')
            self.statusIcon2.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon2.reparentTo(iconRoot)
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, iconRoot], 
                                    slot, 
                                    tooltipTitle='Collection Agent', 
                                   tooltipDescription="The Union Buster is after his long overdue bonus! He will collect Union Dues every round he is attacked.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1),
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                    ])

        if self.cog.hasSuitStatusEffect('ambassadorOverconfidence'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/overconfidence_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('ambassadorOverconfidence'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Overconfidence', 
                                   tooltipDescription="The Ambassador is extremely confident in his ability to take down the Toons, he will deal 25% less damage in this mode.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1), scale=(1.1, 1.1, 1.1))
            
        if self.cog.hasSuitStatusEffect('immune') and not self.cog.dna.name == 'hroller2':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/mental_math.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % self.cog.getSuitStatusTurns('immune'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Immune', 
                                   tooltipDescription="The Cog is entirely immune to all Gags!", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('brokenConnection'):
            status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status2.find('**/attack_icon')
            self.statusIcon2 = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/brokenConnection.png')
            self.statusIcon2.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon2.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % self.cog.getSuitStatusTurns('brokenConnection'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, iconRoot], 
                                    slot, 
                                    tooltipTitle='Broken Connection', 
                                   tooltipDescription="The Wiretapper has lost signal! She will be dealing and taking 30% more damage in this mode.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1),
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                    ])

        if self.cog.hasSuitStatusEffect('ambassadorPhase'):
            status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status2.find('**/attack_icon')
            self.statusIcon2 = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/leverage.png')
            self.statusIcon2.setTexture(texture, 1)
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Leverage', 
                                   tooltipDescription="The Ambassador has had enough of the Toon's antics and has blown right through his suit! " \
                                   "He will deal 50% more damage in this mode, and has access to a new ability.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1),
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                    ])

        if self.cog.hasSuitStatusEffect('contingencyOverride'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/chain_linked_icon')
            # self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('phantomRecordkeeper'),
            #                              text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
            #                              text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
            #                              pos=(0.25, 0, -0.45),
            #                              text_scale=.6)
            # self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Contingency Protocol', 
                                   tooltipDescription="The Contingency Director has entered his Override phase, and as such, he will be dealing and taking +10% more damage!", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('phantomRecordkeeper'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/worker_management_icon')
            # self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('phantomRecordkeeper'),
            #                              text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
            #                              text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
            #                              pos=(0.25, 0, -0.45),
            #                              text_scale=.6)
            # self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Phantom Entry', 
                                   tooltipDescription="The Recordkeeper has made a clone of herself! This clone will cause the permanent record to inflate, and apply debuffs to the Toons, defeating it will directly damage the Recordkeeper.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('greenLight'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/green_light.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % self.cog.getSuitStatusTurns('greenLight'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(iconRoot, 
                                   slot, 
                                   tooltipTitle='Green Light', 
                                   tooltipDescription="The Traffic Manager has given you the right of way! Toons who do not target him this round will be harshly punished!", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('redLight'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/red_light.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % self.cog.getSuitStatusTurns('redLight'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(iconRoot, 
                                   slot, 
                                   tooltipTitle='Red Light', 
                                   tooltipDescription="The Traffic Manager has halted traffic! Toons that target him this round will be harshly punished!", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('enraged'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/rage_mode_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('enraged'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Enraged!', 
                                   tooltipDescription="The Scapegoat is enraged! Scapegoat will deal +30% more damage while in this mode!", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))
            
        if self.cog.hasSuitStatusEffect('toleranceBuilding'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/sparkplug_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Charging Up: %s%%' % self.cog.getSuitStatusModifier('toleranceBuilding'), 
                                   tooltipDescription="The Powerhouse is charging himself up, he will change his current condition upon fully charging.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('powerhouseGeneration'):
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/generation.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(iconRoot, 
                                   slot, 
                                   tooltipTitle='Power Generation', 
                                   tooltipDescription="The Powerhouse will generate power whenever he is Soaked, Zapped, or when he transitions. He is currently dealing and taking +%s%% more damage." % self.cog.getSuitStatusModifier('powerhouseGeneration'), 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('rageBuilding'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/defense_mode_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Rage Building: %s%%' % self.cog.getSuitStatusModifier('rageBuilding'), 
                                   tooltipDescription="Scapegoat's rage is building... Scapegoat will absorb +30% of the damage dealt to other Cogs while in this mode!", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('absorbing'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/damage_absorb_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Damage Absorption', 
                                   tooltipDescription="This Cog will absorb 30% of damage dealt to other Cogs.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('dropImmune'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/duck_drop_icon')
            status = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
            self.statusIcon2 = status.find('**/minnieX')
            self.statusIcon2.setColorScale(1, 0, 0, 1)
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Drop Resistance', 
                                    tooltipDescription="This Cog is entirely immune to DROP Gags.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (5.5, 5.5, 5.5),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                             'scale': (2.75, 2.75, 2.75),
                                             'pos': (0, 0, -0.05),
                                        },
                                    ])
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('zapImmune'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/fizzle_icon')
            status = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
            self.statusIcon2 = status.find('**/minnieX')
            self.statusIcon2.setColorScale(1, 0, 0, 1)
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Zap Resistance', 
                                    tooltipDescription="This Cog is entirely immune to ZAP Gags.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                             'scale': (2.75, 2.75, 2.75),
                                             'pos': (0, 0, -0.05),
                                        },
                                    ])
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('soakResist'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/soak_shield_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Soak Resistance', 
                                   tooltipDescription="This Cog will take -60% less damage whenever it is Soaked.", 
                                   tooltipBuff=False, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('lureImmune'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/cashback_icon')
            status = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
            self.statusIcon2 = status.find('**/minnieX')
            self.statusIcon2.setColorScale(1, 0, 0, 1)
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Lure Resistance', 
                                    tooltipDescription="This Cog is entirely immune to LURE Gags.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                             'scale': (2.75, 2.75, 2.75),
                                             'pos': (0, 0, -0.05),
                                        },
                                    ])
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('soundImmune'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/encore_icon')
            status = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
            self.statusIcon2 = status.find('**/minnieX')
            self.statusIcon2.setColorScale(1, 0, 0, 1)
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Sound Resistance', 
                                    tooltipDescription="This Cog is entirely immune to SOUND Gags.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                             'scale': (2.75, 2.75, 2.75),
                                             'pos': (0, 0, -0.05),
                                        },
                                    ])
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('throwImmune'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/marked_icon')
            status = loader.loadModel('phase_3.5/models/gui/matching_game_gui')
            self.statusIcon2 = status.find('**/minnieX')
            self.statusIcon2.setColorScale(1, 0, 0, 1)
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Throw Resistance', 
                                    tooltipDescription="This Cog is entirely immune to THROW Gags.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                             'scale': (2.75, 2.75, 2.75),
                                             'pos': (0, 0, -0.05),
                                        },
                                    ])
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('closedSession'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/asset_protection.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % self.cog.getSuitStatusTurns('closedSession'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(iconRoot, 
                                   slot, 
                                   tooltipTitle='Closed Session', 
                                   tooltipDescription="The Commissioner is currently focusing, he will severely punish the Toons who attack him in this mode! If left unattacked, he will gain a +10% attack damage boost.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('rushHour'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/counterfeit_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Rush Hour', 
                                   tooltipDescription="The Tollmaster has doubled the entry fee! Attacking the Tollmaster while in this phase will increase your Toll by +16.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        # if self.cog.getGovernaught():
        #     status = loader.loadModel('phase_3.5/models/gui/status_effects')
        #     self.statusIcon = status.find('**/tie_icon')
        #     slot = self._claimNextStatusSlot()
        #     self._attachStatusIcon(self.statusIcon, 
        #                            slot, 
        #                            tooltipTitle='Advanced Upgrade', 
        #                            tooltipDescription="This Cog's reinforced system grants them immunity to Fires and Cease And Desists, and have double their max HP. " \
        #                            "Destroying this Cog will supply the Toons with a permanent 5% Gag damage boost for the duration of the battle.", 
        #                            tooltipBuff=True, 
        #                            slotColor=(1, 0.984, 0, 1))

        if self.cog.dna.name in ['choreo', 'cinema', 'director', 'fmaker']:
            status2 = loader.loadModel('phase_3.5/models/props/ttcc_gen_starburst')
            self.statusIcon = status2.find('**/starburst')
            status = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
            self.statusIcon2 = status.find('**/prestige_star')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                   slot, 
                                   tooltipTitle='Producer Cuts', 
                                   tooltipDescription="The Videographer has called upon his Producers! Defeat this Cog to interrupt the Videographer's broadcast!", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1),
                                   layerSettings=[
                                        {
                                            'scale': (.5, .5, .5),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (0.9, 0.9, 0.9),
                                            'pos': (0, 0, 0),
                                        },])
            self._rotateStatusIcon(slot, self.statusIcon, duration=4.0)

        if self.cog.dna.name == 'mh2' or self.cog.dna.name == 'std2' or self.cog.dna.name == 'cnd2':
            status2 = loader.loadModel('phase_3.5/models/props/ttcc_gen_starburst')
            self.statusIcon = status2.find('**/starburst')
            status = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
            self.statusIcon2 = status.find('**/prestige_star')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                   slot, 
                                   tooltipTitle='Videographer Hijinks', 
                                   tooltipDescription="Defeating this Cog will grant Toons with a +5% Gag damage boost for the duration of the battle.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1),
                                   layerSettings=[
                                        {
                                            'scale': (.5, .5, .5),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (0.9, 0.9, 0.9),
                                            'pos': (0, 0, 0),
                                        },])
            self._rotateStatusIcon(slot, self.statusIcon, duration=4.0)
            
        if self.cog.hasSuitStatusEffect('ambassadorTarget'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/tenure.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % self.cog.getSuitStatusTurns('ambassadorTarget'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(iconRoot, 
                                   slot, 
                                   tooltipTitle='Targeted for Termination', 
                                   tooltipDescription="The Ambassador has marked this Cog for termination! If this Cog is not destroyed, at the end of the round, the Ambassador will sacrifice it and steal it's HP!", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('overpressured'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/union_bust_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Overpressured', 
                                   tooltipDescription="The Pressurizer has pushed this Cog to it's limit! Upon defeating this cog, it will self-destruct, causing damage to both Cogs and Toons!", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        # if self.cog.isTarget or self.cog.isExplosive or self.cog.isOverpressured:
        #     status = loader.loadModel('phase_3.5/models/gui/status_effects')
        #     self.immortal = status.find('**/union_bust_icon')
        #     if self.cog.isExplosive:
        #         self.damageMultText = DirectLabel(parent=self.immortal, relief=None, text="%s" % (self.cog.getExplosiveCondition() - 1), text_fg=(1, 0, 0, 1),
        #                                           text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
        #                                           pos=(0.25, 0, -.5),
        #                                           text_scale=.5)
        #         self.damageMultText.show()
        #     else:
        #         if not self.cog.isOverpressured:
        #             self.damageMultText = DirectLabel(parent=self.immortal, relief=None, text="1", text_fg=(1, 0, 0, 1),
        #                                             text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
        #                                             pos=(0.25, 0, -.5),
        #                                             text_scale=.5)
        #             self.damageMultText.show()
        #     slot = self._claimNextStatusSlot()
        #     self._attachStatusIcon(self.immortal, slot, slotColor=(1, 0.984, 0, 1))
        #     self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('desperation'):
            status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status2.find('**/attack_icon')
            # status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon2 = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/attentive.png')
            self.statusIcon2.setTexture(texture, 1)
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Desperation', 
                                    tooltipDescription="This Cog is in Desperation! Their attacks will deal +%s%% more damage, and have stronger Lure Resistance." % self.cog.getSuitStatusModifier('desperation'), 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                    ])

        if self.cog.hasSuitStatusEffect('overseer'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
            texture = loader.loadTexture('phase_5/maps/effects/sturdy.png')
            self.statusIcon.setTexture(texture, 1)
            iconRoot = NodePath('immuneIcon')
            self.statusIcon.reparentTo(iconRoot)
            self.extraText = DirectLabel(parent=iconRoot, relief=None, text="%s" % self.cog.getSuitStatusTurns('overseer'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Oversight', 
                                   tooltipDescription="This Cog will heal if knockback and/or combo damage is applied.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        # if self.cog.isCollectCall:
        #     status = loader.loadModel('phase_3.5/models/gui/status_effects')
        #     self.collectcall = status.find('**/cashback_icon')
        #     self.collectcallText = DirectLabel(parent=self.collectcall, relief=None, text="%s" % self.cog.getCollectCall(), text_fg=(1, 0, 0, 1),
        #                                        text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
        #                                        pos=(0.25, 0, -.5),
        #                                        text_scale=.4)
        #     self.collectcallText.show()
        #     slot = self._claimNextStatusSlot()
        #     self._attachStatusIcon(self.collectcall, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('protectionRacket'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/cashback_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Protection Racket', 
                                   tooltipDescription="The Racketeer will increase the Racket based on how many Cogs are on the field. The more inflated the Racket is, the more abilities he can use." \
                                   " Using Gags against the Racketeer will decrease the value of the Racket.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('insured'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/heal_over_time_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('insured'),
                                        text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Insurance', 
                                   tooltipDescription="This Cog is insured! While insured, they have high Lure resistance, heal +50 health every round, and receive the same benefits as Manager Cogs.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))
            
        if self.cog.hasSuitStatusEffect('insured2'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/heal_over_time_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('insured2'),
                                        text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Insurance', 
                                   tooltipDescription="This Cog is insured! While insured, they have high Lure resistance, heal +85 health every round, and receive the same benefits as Manager Cogs.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.dna.name == 'supervis' or self.cog.dna.name == 'ovt':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/heal_over_time_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Insured', 
                                   tooltipDescription="While the Cogs are alive, the Supervisor is insured. At the end of every round that he is insured, he will heal 225 health and gain a damage boost.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('oilRain'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/oilrain_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('oilRain'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Prestige Polish', 
                                   tooltipDescription="This Cog has been polished! For the duration they have this effect, they will be entire immune to SQUIRT and ZAP Gags, and will deal and take -10% less damage.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))


        if self.cog.battleSpeed and self.cog.dna.name == 'clerk' and self.cog.getActualLevel() == 24:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/mileaminute_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Mile-a-Minute', 
                                   tooltipDescription='The battle is playing back at %sx speed.' % self.cog.getBattleSpeed(), 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.battleSpeed and self.cog.dna.name == 'psetter':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/mileaminute_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Mile-a-Minute', 
                                   tooltipDescription='The battle is playing back at %sx speed.' % self.cog.getBattleSpeed(), 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('overclocked'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon2 = status.find('**/attack_icon')
            self.statusIcon = status.find('**/toofast4you_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon2, self.statusIcon], 
                                   slot, 
                                   tooltipTitle='Overclocked!', 
                                   tooltipDescription="Reading this doesn't seem like the best use of your time.", 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        # if self.cog.battleSpeed and self.cog.dna.name == 'hustle':
        #     status = loader.loadModel('phase_3.5/models/gui/status_effects')
        #     self.insured = status.find('**/mileaminute_icon')
        #     self.insuredText = DirectLabel(parent=self.insured, relief=None, text="x%s" % (self.cog.getBattleSpeed()),
        #                                    text_fg=(1, 1, 1, 1),
        #                                    text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
        #                                    pos=(0.25, 0, -.5),
        #                                    text_scale=.4)
        #     self.insuredText.show()
        #     slot = self._claimNextStatusSlot()
        #     self._attachStatusIcon(self.insured, slot, slotColor=(1, 0.984, 0, 1))

        # if self.cog.isDeepFrozen:
        #     status = loader.loadModel('phase_3.5/models/gui/status_effects')
        #     self.insured = status.find('**/frozen_icon')
        #     self.insuredText = DirectLabel(parent=self.insured, relief=None, text="%s" % (self.cog.getDeepFrozenRounds() - 1),
        #                                    text_fg=(1, 1, 1, 1),
        #                                    text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
        #                                    pos=(0.25, 0, -.5),
        #                                    text_scale=.5)
        #     self.insuredText.show()
        #     slot = self._claimNextStatusSlot()
        #     self._attachStatusIcon(self.insured, slot, slotColor=(1, 0.984, 0, 1))


        if self.cog.hasSuitStatusEffect('extraAttacks'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/extra_attacks_icon')
            slot = self._claimNextStatusSlot()
            if self.cog.getSuitStatusModifier('extraAttacks') == 1:
                self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Additional Attack', 
                                   tooltipDescription='This Cog has gained %s extra attack!' % self.cog.getSuitStatusModifier('extraAttacks'), 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))
            else:
                self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Additional Attack', 
                                   tooltipDescription='This Cog has gained %s extra attacks!' % self.cog.getSuitStatusModifier('extraAttacks'), 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('contingencyAbilities'):
            if self.cog.getSuitStatusModifier('contingencyAbilities') == 1:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/chainsaw_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle='Escalation Meter', 
                                    tooltipDescription="The Contingency Director will rev up his Chainsaw whenever he reaches certain HP thresholds! In doing this he will gain a new ability." \
                                    " The Contingency Director currently has %s ability."
                                    % self.cog.getSuitStatusModifier('contingencyAbilities'), 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1))
            else:
                status = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status.find('**/chainsaw_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle='Escalation Meter', 
                                    tooltipDescription="The Contingency Director will rev up his Chainsaw whenever he reaches certain HP thresholds! In doing this he will gain a new ability." \
                                    " The Contingency Director currently has %s abilities."
                                    % self.cog.getSuitStatusModifier('contingencyAbilities'), 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('damageUp'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon2 = status.find('**/attack_icon')
            self.statusIcon = status.find('**/suit_damage_up_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon2, self.statusIcon], 
                                   slot, 
                                   tooltipTitle='Damage Boost', 
                                   tooltipDescription='Attacks from this Cog will be +%s%% more powerful.' % self.cog.getSuitStatusModifier('damageUp'), 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('ripped'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/ripped_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Ripped', 
                                   tooltipDescription='Count Erfit is getting ripped! All of his attacks will deal +%s%% more damage.' % self.cog.getSuitStatusModifier('ripped'), 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('shielding'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/shield_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Damage Reduction', 
                                   tooltipDescription="This Cog will take -%s%% less damage from each Gag!" % self.cog.getSuitStatusModifier('shielding'),  
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1), scale=(.9, .9, .9))

        if self.cog.hasSuitStatusEffect('scopeCreep'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/scope_creep_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Scope Creep', 
                                   tooltipDescription="The Count's damage resistance is creeping up, taking -%s%% less damage." % self.cog.getSuitStatusModifier('ripped'),  
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('syphon'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/ink_drain_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Syphon', 
                                   tooltipDescription='This Cog is ready to syphon your Laff! It will heal for the damage it deals!', 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('rushJob'):
            if self.cog.getSuitStatusModifier('rushJob') == 1:
                status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status2.find('**/attack_icon')
                status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
                self.statusIcon2 = status.find('**/inventory_wreckingball')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Rush Job', 
                                    tooltipDescription="ALL Toons will be punished if TRAP is not used on this Cog!! " \
                                    "This Cog cannot be fired, but the right Gag used against this Cog will be much more likely to hit. The wrong Gag will deal 40% less damage.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (5.5, 5.5, 5.5),
                                            'pos': (0, 0, 0),
                                        },
                                    ])
            if self.cog.getSuitStatusModifier('rushJob') == 2:
                status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status2.find('**/attack_icon')
                status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
                self.statusIcon2 = status.find('**/inventory_hypno_goggles')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Rush Job', 
                                    tooltipDescription="ALL Toons will be punished if LURE is not used on this Cog!!" \
                                    "This Cog cannot be fired, but the right Gag used against this Cog will be much more likely to hit. The wrong Gag will deal 40% less damage.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (5.5, 5.5, 5.5),
                                            'pos': (0, 0, 0),
                                        },
                                    ])
            if self.cog.getSuitStatusModifier('rushJob') == 3:
                status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status2.find('**/attack_icon')
                status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
                self.statusIcon2 = status.find('**/inventory_cake')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Rush Job', 
                                    tooltipDescription="ALL Toons will be punished if THROW is not used on this Cog!!" \
                                    "This Cog cannot be fired, but the right Gag used against this Cog will be much more likely to hit. The wrong Gag will deal 40% less damage.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (5.5, 5.5, 5.5),
                                            'pos': (0, 0, 0),
                                        },
                                    ])
            if self.cog.getSuitStatusModifier('rushJob') == 4:
                status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status2.find('**/attack_icon')
                status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
                self.statusIcon2 = status.find('**/inventory_storm_cloud')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcons([self.statusIcon, self.statusIcon2],  
                                    slot, 
                                    tooltipTitle='Rush Job', 
                                    tooltipDescription="ALL Toons will be punished if SQUIRT is not used on this Cog!!" \
                                    "This Cog cannot be fired, but the right Gag used against this Cog will be much more likely to hit. The wrong Gag will deal 40% less damage.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (5.5, 5.5, 5.5),
                                            'pos': (0, 0, 0),
                                        },
                                    ])
            if self.cog.getSuitStatusModifier('rushJob') == 5:
                status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status2.find('**/attack_icon')
                status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
                self.statusIcon2 = status.find('**/inventory_tesla_coil')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Rush Job', 
                                    tooltipDescription="ALL Toons will be punished if ZAP is not used on this Cog!!" \
                                    "This Cog cannot be fired, but the right Gag used against this Cog will be much more likely to hit. The wrong Gag will deal 40% less damage.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (5.5, 5.5, 5.5),
                                            'pos': (0, 0, 0),
                                        },
                                    ])
            if self.cog.getSuitStatusModifier('rushJob') == 6:
                status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status2.find('**/attack_icon')
                status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
                self.statusIcon2 = status.find('**/inventory_fog_horn')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Rush Job', 
                                    tooltipDescription="ALL Toons will be punished if SOUND is not used on this Cog!!" \
                                    "This Cog cannot be fired, but the right Gag used against this Cog will be much more likely to hit. The wrong Gag will deal 40% less damage.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (5.5, 5.5, 5.5),
                                            'pos': (0, 0, 0),
                                        },
                                    ])
            if self.cog.getSuitStatusModifier('rushJob') == 7:
                status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
                self.statusIcon = status2.find('**/attack_icon')
                status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
                self.statusIcon2 = status.find('**/inventory_boulder')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Rush Job', 
                                    tooltipDescription="ALL Toons will be punished if DROP is not used on this Cog!!" \
                                    "This Cog cannot be fired, but the right Gag used against this Cog will be much more likely to hit. The wrong Gag will deal 40% less damage.", 
                                    tooltipBuff=True, 
                                    slotColor=(1, 0.984, 0, 1), 
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (5.5, 5.5, 5.5),
                                            'pos': (0, 0, 0),
                                        },
                                    ])

        if self.cog.hasSuitStatusEffect('damageDown'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon2 = status.find('**/attack_icon')
            self.statusIcon = status.find('**/suit_damage_down_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                   slot, 
                                   tooltipTitle='Damage Down', 
                                   tooltipDescription='Attacks from this Cog will be -%s%% less powerful!' % self.cog.getSuitStatusModifier('damagedown'), 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if self.cog.hasSuitStatusEffect('contingencyOverrideBroken'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/kickback_icon')
            # self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('phantomRecordkeeper'),
            #                              text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
            #                              text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
            #                              pos=(0.25, 0, -0.45),
            #                              text_scale=.6)
            # self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Protocol Breach', 
                                   tooltipDescription="The Contingency Director's override has malfunctioned! He is now taking and dealing -25% less damage.", 
                                   tooltipBuff=False, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('unionBusterNoAttack'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/hands_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('unionBusterNoAttack'),
                                        text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Under Investigation', 
                                   tooltipDescription='The Union Buster is under investigation, and as such, he will not be able to attack this turn!', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if self.cog.hasSuitStatusEffect('compensationClaims'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/worker_management_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Compensation Claims', 
                                   tooltipDescription="The Union Buster has been punished for cutting off too many of his employees! He is now taking +%s%% more damage as a result." % self.cog.getSuitStatusModifier('compensationClaims'), 
                                   tooltipBuff=True, 
                                   slotColor=(1, 0.984, 0, 1))

        if self.cog.hasSuitStatusEffect('vulnerable') and not self.cog.dna.name == 'hroller2':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/broken_shield_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Vulnerable', 
                                   tooltipDescription='This Cog is taking +%s%% more damage from Gags!' % self.cog.getSuitStatusModifier('vulnerable'), 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1), scale=(.9, .9, .9))

        if self.cog.hasSuitStatusEffect('marketMeltdown'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/backburner_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('marketMeltdown'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Market Meltdown', 
                                   tooltipDescription='This Cog will take -100 damage per round while the Meltdown is in effect!', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if self.cog.hasSuitStatusEffect('sued'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/sued_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('sued'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Sued', 
                                   tooltipDescription='This Cog will take %s damage per round and cannot attack! Each Gag used against this Cog increases the effect duration up to 3 rounds.'
                                   % int(self.cog.getMaxHP() / 4), 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if self.cog.hasSuitStatusEffect('lured'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            if self.cog.isLured == 1:
                self.statusIcon = status.find('**/lured_icon')
                self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('lured'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
                self.extraText.show()
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle='Lured (Unrestige)', 
                                    tooltipDescription="LURED Cogs cannot attack and take more damage from each THROW or SQUIRT Gag that's used.",
                                    tooltipBuff=False, 
                                    slotColor=(0, 0.902, 1, 1))
            else:
                self.statusIcon = status.find('**/lured_prestige_icon')
                self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('lured'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
                self.extraText.show()
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                    slot, 
                                    tooltipTitle='Lured (Prestige)', 
                                    tooltipDescription="LURED Cogs cannot attack and take more damage from each THROW or SQUIRT Gag that's used.",
                                    tooltipBuff=False, 
                                    slotColor=(0, 0.902, 1, 1))

        if self.cog.hasSuitStatusEffect('zapped'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/sparkplug_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('zapped'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Aftershock', 
                                   tooltipDescription='This Cog has been shocked due to being affected by a ZAP gag, and as such will take %s damage at the start of the round!' % self.cog.getSuitStatusModifier('zapped'),
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if self.cog.hasSuitStatusEffect('marked'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/marked_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('marked'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Marked for Laugh', 
                                   tooltipDescription='This cog is more vulnerable, and will take 10% more damage.', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if self.cog.hasSuitStatusEffect('dazed'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/confusion_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('dazed'),
                                        text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Dazed', 
                                   tooltipDescription='This Cog is dazed due to a TRAP activation, and as such has a -10% dodge chance reduction!', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))

        if self.cog.hasSuitStatusEffect('soaked'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/soaked_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('soaked'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Soaked', 
                                   tooltipDescription='Soaked Cogs have a -10% dodge chance and are vulnerable to ZAP Gags. Removed if this Cog is hit by ZAP Gags.', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1))
            
        if self.cog.hasSuitStatusEffect('drenched'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status.find('**/soaked_icon')
            self.extraText = DirectLabel(parent=self.statusIcon, relief=None, text="%s" % self.cog.getSuitStatusTurns('drenched'),
                                         text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
                                         text_font=ToontownGlobals.getInterfaceFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -0.45),
                                         text_scale=.6)
            self.extraText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Drenched', 
                                   tooltipDescription='Soaked Cogs have a -20% dodge chance, deal -15% less damage, and are vulnerable to ZAP Gags. One drenched round is removed if this Cog is hit by ZAP Gags.',
                                   tooltipBuff=False, 
                                   slotColor=(0.012, 0, 1))
            
        if self.cog.hasSuitStatusEffect('drenched'):
            status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status2.find('**/attack_icon')
            self.statusIcon2 = status2.find('**/suit_damage_down_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Damage Down', 
                                   tooltipDescription='While Drenched, attacks from this Cog will be -15% less powerful!', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1),
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                    ])
            
        if self.cog.hasSuitStatusEffect('drenched') and self.cog.dna.name == 'safesupervis':
            status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status2.find('**/attack_icon')
            self.statusIcon2 = status2.find('**/suit_damage_down_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Burnt Out', 
                                   tooltipDescription='While the Pressurizer is drenched, he will deal -25% less damage and gain an extra attack.', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1),
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                    ])
            
        if self.cog.hasSuitStatusEffect('soaked') and self.cog.dna.name == 'safesupervis':
            status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.statusIcon = status2.find('**/attack_icon')
            self.statusIcon2 = status2.find('**/suit_damage_down_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcons([self.statusIcon, self.statusIcon2], 
                                    slot, 
                                    tooltipTitle='Burnt Out', 
                                   tooltipDescription='While the Pressurizer is soaked, he will deal -25% less damage and gain an extra attack.', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1),
                                    layerSettings=[
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                        {
                                            'scale': (1.0, 1.0, 1.0),
                                            'pos': (0, 0, 0),
                                        },
                                    ])
            
        if self.cog.hasSuitStatusEffect('trapped'):
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            if self.cog.getSuitStatusModifier('trapped') == 8:
                self.statusIcon = status.find('**/inventory_tnt')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Trapped', 
                                   tooltipDescription='This Cog is TRAPPED by a TNT! LURE gags are +20% more accurate against this Cog. Once LURED, they will take damage.', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1), scale=(5.5, 5.5, 5.5))
            elif self.cog.getSuitStatusModifier('trapped') == 7:
                self.statusIcon = status.find('**/inventory_wreckingball')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Trapped', 
                                   tooltipDescription='This Cog is TRAPPED by a Wrecking Ball! LURE gags are +20% more accurate against this Cog. Once LURED, they will take damage.', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1), scale=(5.5, 5.5, 5.5))
            elif self.cog.getSuitStatusModifier('trapped') == 6:
                self.statusIcon = status.find('**/inventory_trapdoor')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Trapped', 
                                   tooltipDescription='This Cog is TRAPPED by a Trap Door! LURE gags are +20% more accurate against this Cog. Once LURED, they will take damage.', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1), scale=(5.5, 5.5, 5.5))
            elif self.cog.getSuitStatusModifier('trapped') == 5:
                self.statusIcon = status.find('**/inventory_quicksand_icon')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Trapped', 
                                   tooltipDescription='This Cog is TRAPPED by a Quicksand! LURE gags are +20% more accurate against this Cog. Once LURED, they will take damage.', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1), scale=(5.5, 5.5, 5.5))
            elif self.cog.getSuitStatusModifier('trapped') == 4:
                self.statusIcon = status.find('**/inventory_springboard')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Trapped', 
                                   tooltipDescription='This Cog is TRAPPED by a Springboard! LURE gags are +20% more accurate against this Cog. Once LURED, they will take damage.', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1), scale=(5.5, 5.5, 5.5))
            elif self.cog.getSuitStatusModifier('trapped') == 3:
                self.statusIcon = status.find('**/inventory_marbles')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Trapped', 
                                   tooltipDescription='This Cog is TRAPPED by Marbles! LURE gags are +20% more accurate against this Cog. Once LURED, they will take damage.', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1), scale=(5.5, 5.5, 5.5))
            elif self.cog.getSuitStatusModifier('trapped') == 2:
                self.statusIcon = status.find('**/inventory_rake')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Trapped', 
                                   tooltipDescription='This Cog is TRAPPED by a Rake! LURE gags are +20% more accurate against this Cog. Once LURED, they will take damage.', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1), scale=(5.5, 5.5, 5.5))
            else:
                self.statusIcon = status.find('**/inventory_banana_peel')
                slot = self._claimNextStatusSlot()
                self._attachStatusIcon(self.statusIcon, 
                                   slot, 
                                   tooltipTitle='Trapped', 
                                   tooltipDescription='This Cog is TRAPPED by a Banana Peel! LURE gags are +20% more accurate against this Cog. Once LURED, they will take damage.', 
                                   tooltipBuff=False, 
                                   slotColor=(0, 0.902, 1, 1), scale=(5.5, 5.5, 5.5))

        # if self.cog.isTrapped:
        #     status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
        #     if self.cog.isTrapped == 8:
        #         self.dazed = status.find('**/inventory_tnt')
        #     elif self.cog.isTrapped == 7:
        #         self.dazed = status.find('**/inventory_wreckingball')
        #     elif self.cog.isTrapped == 6:
        #         self.dazed = status.find('**/inventory_trapdoor')
        #     elif self.cog.isTrapped == 5:
        #         self.dazed = status.find('**/inventory_quicksand_icon')
        #     elif self.cog.isTrapped == 4:
        #         self.dazed = status.find('**/inventory_springboard')
        #     elif self.cog.isTrapped == 3:
        #         self.dazed = status.find('**/inventory_marbles')
        #     elif self.cog.isTrapped == 2:
        #         self.dazed = status.find('**/inventory_rake')
        #     else:
        #         self.dazed = status.find('**/inventory_banana_peel')
        #     slot = self._claimNextStatusSlot()
        #     self._attachStatusIcon(self.dazed, slot, slotColor=(0, 0.902, 1, 1), scale=(5.5, 5.5, 5.5))

        self._applyStatusOffset()
        if self.statusInformationPanel:
            self.statusInformationPanel.rebuildStatusEffects(
                list(self.statusIconNodes)
            )

            self.statusInformationPanel.rebuildModifiers(
                self._getCogInformationModifiers()
            )
        self.healthText['text'] = t

    def _pulseStatusSlotVisible(self, slot, fromColor, toColor=(1, 1, 1, 1), duration=1.0):
        self._stopSlotPulse(slot)

        slot['pulse'] = Sequence(
            LerpColorScaleInterval(slot['bg'], duration, fromColor, blendType='easeInOut'),
            LerpColorScaleInterval(slot['bg'], duration, toColor, blendType='easeInOut'),
            Wait(1.0)
        )
        slot['pulse'].loop()

    def _applyStatusOffset(self):
        visibleSlots = 4

        if self.statusEffectTooltip:
            self.statusEffectTooltip.hide()

        self.hoveredStatusSlot = None

        for slotIndex in xrange(visibleSlots):
            slot = self.statusSlots[slotIndex]

            self._stopSlotPulse(slot)

            slot['bg'].show()
            slot['bg'].setColor(1, 1, 1, 1)
            slot['bg'].setColorScale(1, 1, 1, 1)
            slot['iconRoot'].show()
            slot['hoverButton'].show()
            slot['effectIndex'] = None

            for child in slot['iconRoot'].getChildren():
                child.detachNode()

        for slotIndex in xrange(visibleSlots):
            effectIndex = self.statusOffset + slotIndex

            if effectIndex >= len(self.statusIconNodes):
                continue

            effectData = self.statusIconNodes[effectIndex]
            icon = effectData.get('node')

            if icon is None or icon.isEmpty():
                continue

            slot = self.statusSlots[slotIndex]

            icon.reparentTo(slot['iconRoot'])
            icon.setPos(0, 0, 0)
            icon.show()

            slot['effectIndex'] = effectIndex

            if effectIndex < len(self.statusSlotColors):
                slot['bg'].setColor(
                    *self.statusSlotColors[effectIndex]
                )

            pulseType = self.statusSlotPulseTypes[effectIndex]
            pulseData = self.statusSlotPulses[effectIndex]

            if pulseType == 'normal' and pulseData:
                fromColor, toColor, duration = pulseData

                self._pulseStatusSlotVisible(
                    slot,
                    fromColor,
                    toColor,
                    duration
                )

            elif pulseType == 'rainbow' and pulseData:
                self._pulseRainbowStatusSlotVisible(
                    slot,
                    pulseData[0]
                )

        maxOffset = max(
            0,
            len(self.statusIconNodes) - visibleSlots
        )

        self.cycleBackButton['state'] = (
            DGG.NORMAL
            if self.statusOffset > 0
            else DGG.DISABLED
        )

        self.cycleForwardButton['state'] = (
            DGG.NORMAL
            if self.statusOffset < maxOffset
            else DGG.DISABLED
    )


    def changeStatusOffset(self, amount):
        maxOffset = max(0, self.statusEffects - 4)

        newOffset = self.statusOffset + amount
        newOffset = max(0, min(newOffset, maxOffset))

        if newOffset != self.statusOffset:
            self.statusOffset = newOffset
            self._applyStatusOffset()

    def updateHealthBar(self):
        self.setLevelText()
        condition = self.cog.healthCondition
        healthPercentage = float(self.cog.getHP()) / float(max(self.cog.getMaxHP(), 1))
        healthPercentage = max(0.0, min(1.0, healthPercentage))
        if self.cog.getHP() >= 0:
            self.hp = self.cog.getHP()
        else:
            self.hp = 0
        self.maxHp = self.cog.getMaxHP()
        if (self.cog.hasSuitStatusEffect('immune') or self.cog.hasSuitStatusEffect('videographerImmune')) and not self.cog.dna.name == 'hroller' and not self.cog.dna.name == 'hroller2':
            self.hp = 'Immune'
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setColor(1, 1, 1, 1)
                self.__changeColor()
                #self.healthBar2.setProp('value', self.cog.getMaxHP())
                taskMgr.remove(self.uniqueName('blink-task2'))
        elif condition == 9:
            taskMgr.remove(self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setColor(1, 1, 1, 1)
                self.__changeColor()
                #self.healthBar2.setProp('value', self.cog.getHP())
                taskMgr.remove(self.uniqueName('blink-task2'))
        elif condition == 10:
            taskMgr.remove(self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setColor(1, 1, 1, 1)
                self.__changeColor()
                #self.healthBar2.setProp('value', self.cog.getHP())
                blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task2'))
        elif condition == 11:
            taskMgr.remove(self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setColor(1, 1, 1, 1)
                self.__changeColor()
                #s#elf.healthBar2.setProp('value', self.cog.getHP())
                blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.25), Task(self.__pulseGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task2'))
        elif condition == 13:
            taskMgr.remove(self.uniqueName('blink-task2'))
            if self.healthBar2:
                self.healthBar2.setColor(1, 1, 1, 1)
                #self.healthBar2.setProp('value', self.cog.getHP())
                blinkTask = Task.loop(Task(self.__blinkPurple), Task.pause(1), Task(self.__blinkPurpleColor),
                                      Task.pause(3))
                taskMgr.add(blinkTask, self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(1, 1, 1, 1.0)
        else:
            taskMgr.remove(self.uniqueName('blink-task'))
            if self.healthBar2:
                self.healthBar2.setColor(1, 1, 1, 1)
                self.__changeColor()
               # self.healthBar2.setProp('value', self.cog.getHP())
                taskMgr.remove(self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
        if (self.cog.hasSuitStatusEffect('immune') or self.cog.hasSuitStatusEffect('videographerImmune')) and not self.cog.dna.name == 'hroller' and not self.cog.dna.name == 'hroller2':
            self.hpText['text'] = str(self.hp)
        else:
            self.hpText['text'] = str(self.hp) + '/' + str(self.maxHp)
        self.healthBarClippingPlane.setPlane(Plane(Vec3(-1, 0, 0), Point3(self.__lerp(-0.49, 0.49, healthPercentage), 0, 0)))

    def __lerp(self, x, y, lerpAmount):
        '''
        Returns a float linearly interpolated from 0 to 1
        For lerpAmount, 0 = x and 1 = y. 0.5 would be the midpoint.
        '''
        return x - lerpAmount * (x - y)

    def __pulsePurple(self, num):
        if num == 1:
            x = self.attackIcon
        if num == 2:
            x = self.attackIcon1
        if num == 3:
            x = self.attackIcon2
        if num == 4:
            x = self.attackIcon3
        if num == 5:
            x = self.attackIcon4
        if num == 6:
            x = self.attackIcon5
        if num == 7:
            x = self.attackIcon6
        if num == 8:
            x = self.attackIcon7
        self.interval = Parallel(LerpColorScaleInterval(x, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                   blendType='easeInOut'))
        self.interval.start()

    def __pulsePurpleColor(self, num):
        if num == 1:
            x = self.attackIcon
        if num == 2:
            x = self.attackIcon1
        if num == 3:
            x = self.attackIcon2
        if num == 4:
            x = self.attackIcon3
        if num == 5:
            x = self.attackIcon4
        if num == 6:
            x = self.attackIcon5
        if num == 7:
            x = self.attackIcon6
        if num == 8:
            x = self.attackIcon7
        self.interval = Parallel(LerpColorScaleInterval(x, duration=1, colorScale=(self.healthColors[13]),
                                   blendType='easeInOut'))
        self.interval.start()

    def updateStatusIcons(self, cog, battle):
        if battle.isSuitLured(cog):
            self.lured.show()
        else:
            self.lured.hide()

    def __changeColor(self):
        if (self.cog.hasSuitStatusEffect('immune') or self.cog.hasSuitStatusEffect('videographerImmune')) and not self.cog.dna.name == 'hroller' and not self.cog.dna.name == 'hroller2':
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar2, duration=1, colorScale=(1, 1, 1, 1),
                                   blendType='easeInOut'))
            self.interval.start()
        else:
            self.interval = Parallel(LerpColorScaleInterval(self.healthBar2, duration=1,
                                                            colorScale=(self.healthColors[self.cog.healthCondition]),
                                                            blendType='easeInOut'))
            self.interval.start()

    def __pulseRed(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.healthBar2, duration=0, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
        self.interval.start()

    def __pulseGray(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.healthBar2, duration=0, colorScale=(0.431, 0.431, 0.431, 1),
                                   blendType='easeInOut'))
        self.interval.start()

    def __blinkPurple(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.healthBar2, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                                        blendType='easeInOut'))
        self.interval.start()

    def __blinkPurpleColor(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.healthBar2, duration=1, colorScale=(self.healthColors[13]),
                                                        blendType='easeInOut'))
        self.interval.start()

    def __blinkRed(self, task):
        self.healthBar2.setProp('barColor', self.healthColors[9])

    def __blinkGray(self, task):
        self.healthBar2.setProp('barColor', self.healthColors[10])

    def createSuitHead(self, suitName, dimension=.7, setH=180):
        suitDNA = SuitDNA.SuitDNA()
        suitDNA.newSuit(suitName)
        suit = Suit.Suit()
        suit.setDNA(suitDNA)
        headParts = suit.getHeadParts()
        animatedHeadParts = suit.getAnimatedHeadParts()
        head = hidden.attachNewNode('head')
        hasAnimatedHead = False
        for part in headParts:
            for part in animatedHeadParts:
                hasAnimatedHead = True
            if hasAnimatedHead:
                if 'neutral' in part.getAnimNames() and suitName in ToontownGlobals.animSuitHeadsPosedNeutral:
                    part.pose('neutral', 1)

            if self.cog.dna.name in (
                'mh',
                'mh2',
                'std2',
                'ds',
                'cv'
                ):
                copyPart = part.copyTo(head)
                copyPart.setDepthTest(1)
                copyPart.setDepthWrite(1)
            else:
                part.setTwoSided(True)
                part.setDepthTest(1)
                part.setDepthWrite(1)

                part.reparentTo(head)
        self.fitGeometry(head, fFlip=1, dimension=dimension, setH=setH)
        suit.delete()
        suit = None
        return head
    
    def fitGeometry(self, geom, fFlip = 0, dimension = 0.7, setH=180):
        p1 = Point3()
        p2 = Point3()
        geom.calcTightBounds(p1, p2)
        if fFlip:
            t = p1[0]
            p1.setX(-p2[0])
            p2.setX(-t)
        d = p2 - p1
        biggest = max(d[0], d[2])
        s = dimension / biggest
        mid = (p1 + d / 2.0) * s
        geomXform = hidden.attachNewNode('geomXform')
        for child in geom.getChildren():
            child.reparentTo(geomXform)

        geomXform.setPosHprScale(-mid[0], -mid[1] + 1, -mid[2], setH, 0, 0, s, s, s)
        geomXform.reparentTo(geom)


    def generateSuitHead(self, name):
        self.suitHead = self.attachNewNode('head')

        if self.cog.dna.name == 'ls':
            head = self.createSuitHead(name, .6, 270)
        elif self.cog.dna.name == 'bfh2':
            head = self.createSuitHead(name, .7, 270)
        else:
            head = self.createSuitHead(name, .7, 180)
        head.copyTo(self.suitHead)

        if self.cog.dna.name == 'shw':
            self.suitHead.setPos(-0.265, 0.5, 0.205)
        elif self.cog.dna.name == 'ls':
            self.suitHead.setPos(-0.265, 0.5, 0.205)
        else:
            self.suitHead.setPos(-0.27, 0.5, 0.205)
        if self.cog.dna.name == 'ls':
            self.suitHead.setScale(.25)
        else:
            self.suitHead.setScale(.2675)

    def show(self):
        if settings.get('show-cog-levels', True):
            if self.cog:
                self.updateHealthBar()
            self.hidden = False
            self.healthNode.show()
           # self.button.show()
            DirectFrame.show(self)
        else:
            self.notify.debug('Tried to unhide Cog levels when settings have not been updated!')

    def __handleToggle(self):
        if self.cog:
            if self.hidden:
                self.show()
            else:
                self.hide()

    def hide(self):
        if self.blinkTask:
            taskMgr.remove(self.blinkTask)
            self.blinkTask = None

        self.hidden = True
        self.healthNode.hide()
    #    self.button.hide()
        DirectFrame.hide(self)

    def unload(self):
        if self.isLoaded == 0:
            return
        self.isLoaded = 0
        self.exit()
        DirectFrame.destroy(self)

    def cleanup(self):
        self.ignoreAll()
        self.cleanupHead()
        self.statusIconNodes = []
        if self.statusInformationPanel:
            try:
                self.statusInformationPanel.destroy()
            except:
                pass

            self.statusInformationPanel = None
        if self.statusEffectTooltip:
            self.statusEffectTooltip.destroy()
            self.statusEffectTooltip = None

        if self.blinkTask:
            taskMgr.remove(self.blinkTask)
            self.blinkTask = None

        del self.blinkTask
        taskMgr.remove(self.uniqueName('blink-task2'))
        DirectFrame.destroy(self)

    def cleanupHead(self):
        if self.suitHead:
            self.suitHead.removeNode()
            del self.suitHead

    def showPanel(self, inside, status):
        if inside:
            if self.statusFramePanel != None:
                self.statusFramePanel.show()

    def hidePanel(self, inside, status):
        if inside:
            if self.statusFramePanel != None:
                self.statusFramePanel.hide()

