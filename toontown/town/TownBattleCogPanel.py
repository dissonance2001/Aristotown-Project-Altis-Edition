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
from toontown.battle import DistributedBattleBase
from toontown.battle import BattleProps
from direct.task.Task import Task
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from panda3d.direct import *
from toontown.toonbase import TTLocalizer

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
        self.isLoaded = 0
        self.notify.info("Loading Cog Battle Panel!")
        self.healthText = DirectLabel(parent=self, text='', pos=(0.11, 1.0, 0.244), text_scale=0.065)
        healthBarModel = loader.loadModel('phase_3.5/models/gui/suit_panel')
        self.healthNode = self.attachNewNode('health')
        self.healthNode.setPos(0.125, 0.0, 0.19)
        self.healthNode.setTransparency(1)
        healthGui = loader.loadModel('phase_3.5/models/gui/suit_panel')
        self.statuseffectslot = healthGui.find('**/status_effect_slot')
        button = healthGui.find('**/status_effect_slot')
        button.setScale(0.63)
        button.setH(0)
        button.setR(0)
        button.setColor(Vec4(0, 0, 0, 0))
        healthBar = healthBarModel.find('**/status_effect_slot')
        self.healthBar = healthBar
        healthBar.setScale(0.63)
        healthBar.setH(0)
        healthBar.setR(0)
        healthBar.reparentTo(self.healthNode)
        self.healthBar2 = DirectWaitBar(parent=self, pos=(-0.026, -0.11, -0.035), relief=DGG.SUNKEN, value=100,
                                        frameSize=(-2.5, 2.75, -0.6, 0.6),
                                        barTexture='phase_3.5/maps/battlegui/healthbar.png',
                                        borderWidth=(0.02, 0.02), scale=0.1, sortOrder=50,
                                        frameColor=(0, 0, 0, 0), barColor=(1, 1, 1.0, 1))
        infoButton = healthBarModel.find('**/Info_Nuetral')
        infoButton.reparentTo(self.healthNode)
        self.infoButton = infoButton
        self.infoButton.setScale(0.275)
        self.infoButton.setH(0)
        self.infoButton.setR(0)
        self.infoButton.setPos(.235, 0, -.035)
        self.accept('inventory-levels', self.__handleToggle)
        button.reparentTo(self.healthNode)
        self.healthBar2.reparentTo(self.healthNode)
        infoButton.reparentTo(self.healthNode)
        self.hpText = DirectLabel(parent=self, text='', text_fg=Vec4(0, 0, 0, 1), pos=(0.09, 0.125, 0.1335),
                                  text_scale=0.072)
        self.setScale(0.525)
        self.button = button
        self.head = None
        self.suitHead = None
        self.blinkTask = None
        self.hide()
        healthGui.removeNode()
        gui.removeNode()

    def setCogInformation(self, cog):
        self.cleanupHead()
        self.cog = cog
        self.updateHealthBar()
        if self.healthBar2:
            self.healthBar2.setProp('range', self.cog.getMaxHP())

        self.generateSuitHead(cog.getStyleName())
        self.setLevelText()

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
        taskMgr.remove(self.uniqueName('overcharge-pulse-task'))

        if hasattr(self, 'statusSlots'):
            for slot in self.statusSlots:
                pulse = slot.get('pulse')
                if pulse:
                    try:
                        pulse.finish()
                    except:
                        pass
                    slot['pulse'] = None

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
                'luredManager', 'syphon', 'vulnerable', 'soakResist',
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
            (-0.335, 0.4, -0.26),  # 1
            (-0.2075, 0.5, -0.355),  # 2
            (-0.045, 0.5, -0.355),  # 3
            (0.085, 0.4, -0.26),  # 4
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
            bgNode.setPosHprScale(x, y, z, 0, 0, 0, .165, .165, .165)
            bgNode.setColor(1, 1, 1, 1)

            iconRoot = self.healthNode.attachNewNode('statusIconRoot-%d' % i)
            iconRoot.setPosHprScale(x, y, z, 0, 0, 0, .165, .165, .165)

            if i >= 4:
                bgNode.hide()
                iconRoot.hide()

            self.statusSlots[i] = {
                'bgModel': bgModel,
                'bg': bgNode,
                'iconRoot': iconRoot,
                'pulse': None,
            }

        self.status = self.statusSlots[0]['bgModel']
        self.status2 = self.statusSlots[1]['bgModel']
        self.status3 = self.statusSlots[2]['bgModel']
        self.status4 = self.statusSlots[3]['bgModel']
        self.status5 = self.statusSlots[4]['bgModel']
        self.status6 = self.statusSlots[5]['bgModel']
        self.status7 = self.statusSlots[6]['bgModel']
        self.status8 = self.statusSlots[7]['bgModel']
        self.status9 = self.statusSlots[8]['bgModel']
        self.status10 = self.statusSlots[9]['bgModel']

        self.attackIcon = self.statusSlots[0]['bg']
        self.attackIcon1 = self.statusSlots[1]['bg']
        self.attackIcon2 = self.statusSlots[2]['bg']
        self.attackIcon3 = self.statusSlots[3]['bg']
        self.attackIcon4 = self.statusSlots[4]['bg']
        self.attackIcon5 = self.statusSlots[5]['bg']
        self.attackIcon6 = self.statusSlots[6]['bg']
        self.attackIcon7 = self.statusSlots[7]['bg']
        self.attackIcon8 = self.statusSlots[8]['bg']
        self.attackIcon9 = self.statusSlots[9]['bg']

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

        if self.statusEffects > 4:
            slot['bg'].show()
            slot['iconRoot'].show()

        return slot

    def _attachStatusIcon(self, iconNode, slot, slotColor=(1, 1, 1, 1), scale=(1, 1, 1)):
        if slot is None:
            return

        if isinstance(scale, (int, float)):
            scale = (scale, scale, scale)

        slot['bg'].setColor(*slotColor)
        slot['bg'].setColorScale(1, 1, 1, 1)

        iconNode.reparentTo(slot['iconRoot'])
        sx, sy, sz = scale
        iconNode.setPosHprScale(0, 0, 0, 0, 0, 0, sx, sy, sz)
        iconNode.setColor(1, 1, 1, 1)

    def _pulseStatusSlot(self, slot, fromColor, toColor=(1, 1, 1, 1), duration=1.0):
        if slot is None:
            return

        self._stopSlotPulse(slot)

        slot['pulse'] = Sequence(
            LerpColorScaleInterval(slot['bg'], duration, fromColor, blendType='easeInOut'),
            LerpColorScaleInterval(slot['bg'], duration, toColor, blendType='easeInOut'), Wait(1.0)
        )
        slot['pulse'].loop()

    def _pulseRainbowStatusSlot(self, slot, duration=0.35):
        if slot is None:
            return

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
        if self.cog.dna.name == 'shw':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.sharkwatcher = status.find('**/ripped_icon')
            self.sharkwatcher.reparentTo(self.healthNode)
            self.sharkwatcher.setPosHprScale(-0.3925, 0.5, 0.025, 0, 0, 0, .24, .24, .24)
        if self.cog.dna.name == 'hrollers':
            t = 'Level 25'
        else:
            t = 'Level ' + str(self.cog.getActualLevel())
        if self.cog.getExecutive() or self.cog.getManager() or self.cog.getGovernaught():
            if self.cog.getExecutive():
                t += TTLocalizer.ExecutivePostFix
            elif self.cog.getManager():
                t += TTLocalizer.ManagerPostFix
            else:
                t += TTLocalizer.GovernaughtPostFix
        if self.cog.getSkeleRevives() > 0:
            t += TTLocalizer.SkeleRevivePostFix % (self.cog.getSkeleRevives() + 1)

        # Status Effects
        if self.cog.isVirtual:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.virtual, slot, slotColor=(0.361, 0.361, 0.361, 1))

        if self.cog.isSkeleton and not self.cog.isVirtual:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.skeleton, slot, slotColor=(0.722, 0.722, 0.722, 1))

        if self.cog.getManager() or self.cog.isLureResist or self.cog.isInsured or self.cog.isInsured2 or self.cog.isContracted or self.cog.healthCondition == 13:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/hands_icon')
            if (self.cog.isDesperation and (self.cog.isAngry and self.cog.dna.name == 'sgoat')) or self.cog.dna.name == 'hroller' or self.cog.isImmortal or (self.cog.getActualLevel() == 25 and self.cog.dna.name == 'hrollers') or self.cog.isLureImmune:
                self.luredManagerText = DirectLabel(parent=self.luredManager, relief=None,
                                                    text="0",
                                                    text_fg=(1, 0, 0, 1),
                                                    text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                    pos=(0.25, 0, -.5),
                                                    text_scale=.5)
            elif self.cog.isDesperation or self.cog.isBookkeeping or self.cog.dna.name in ('bcaster', 'hroller', 'hroller2', 'videog', 'fires', 'fbed', 'mouthp', 'rainmake', 'whunter', 'wsi', 'redd', 'duckshfl', 'treek', 'bellring', 'ddiver', 'gatekeep')\
                    or (self.cog.isVulnerable and self.cog.dna.name == 'wtapper')  or (self.cog.healthCondition == 13 and self.cog.isSkeleton) or (self.cog.isAngry and self.cog.dna.name == 'sgoat'):
                self.luredManagerText = DirectLabel(parent=self.luredManager, relief=None,
                                                text="1",
                                                text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            else:
                self.luredManagerText = DirectLabel(parent=self.luredManager, relief=None,
                                                    text="2",
                                                    text_fg=(1, 0, 0, 1),
                                                    text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                    pos=(0.25, 0, -.5),
                                                    text_scale=.5)
            self.luredManagerText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.luredManager, slot)
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.healthCondition == 13:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.overcharged, slot, scale=(.8, .8, .8))
            self._pulseStatusSlot(slot, fromColor=(0.992, 0.227, 1, 1), toColor=(self.healthColors[13]))

        if self.cog.isImmortal and self.cog.dna.name == 'videog':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.hollywoods = status.find('**/marked_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.hollywoods, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.dna.name == 'hroller2' and not self.cog.isPhase3:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.hollywoods = status.find('**/marked_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.hollywoods, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.dna.name == 'hroller' and self.cog.isPhase3:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.hollywoods = status.find('**/marked_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.hollywoods, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.dna.name == 'phouse':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/sparkplug_icon')
            self.rageBuildingText = DirectLabel(parent=self.extraAttacks, relief=None,
                                                text="%s" % self.cog.getPowerhouseRotation() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.4)
            self.rageBuildingText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.extraAttacks, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.dna.name == 'hroller':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/insured_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.extraAttacks, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isImmortal and self.cog.dna.name not in ('hroller', 'hroller2', 'videog'):
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/schadenfreude_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.immortal, slot)
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.dna.name == 'hroller2' and not self.cog.isVulnerable and self.cog.isPhase3:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/harmonious_colors_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.extraAttacks, slot)
            self._clear_status_interval('rainbowPulseTask')
            self._pulseRainbowStatusSlot(slot, duration=2.0)

        if self.cog.dna.name == 'hrollers':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            if self.cog.getActualLevel() == 34:
                self.rainbow = status.find('**/ink_drain_icon')
            if self.cog.getActualLevel() == 33:
                self.rainbow = status.find('**/unite_cooldown_icon')
            if self.cog.getActualLevel() == 32:
                self.rainbow = status.find('**/cashback_icon')
            if self.cog.getActualLevel() == 31:
                self.rainbow = status.find('**/duck_drop_icon')
            if self.cog.getActualLevel() == 30:
                self.rainbow = status.find('**/backfire_icon')
            if self.cog.getActualLevel() == 29:
                self.rainbow = status.find('**/trap_card_icon')
            if self.cog.getActualLevel() == 28:
                self.rainbow = status.find('**/singing_blues_icon')
            if self.cog.getActualLevel() == 27:
                self.rainbow = status.find('**/fizzle_icon')
            if self.cog.getActualLevel() == 26:
                self.rainbow = status.find('**/full_deck_icon')
            if self.cog.getActualLevel() == 25:
                self.rainbow = status.find('**/no_green_light_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.rainbow, slot)
            self._clear_status_interval('rainbowPulseTask')
            self._pulseRainbowStatusSlot(slot, duration=2.0)

        if self.cog.isAngry:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            if self.cog.dna.name == 'cbutcher':
                self.enraged = status.find('**/worker_management_icon')
            elif self.cog.dna.name == 'wtapper':
                self.enraged = status.find('**/chain_linked_icon')
            elif self.cog.dna.name == 'liquid':
                self.enraged = status.find('**/bewitched_icon')
            else:
                self.enraged = status.find('**/rage_mode_icon')
            self.enrageCountText = DirectLabel(parent=self.enraged, relief=None,
                                              text="%s" % self.cog.getEnrageCounter(), text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.enrageCountText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.enraged, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isShielding and self.cog.dna.name == 'sgoat':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing = status.find('**/defense_mode_icon')
            self.rageBuildingText = DirectLabel(parent=self.absorbing, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.4)
            self.rageBuildingText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.absorbing, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isShielding and not self.cog.dna.name == 'sgoat' and not self.cog.dna.name == 'hroller':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing = status.find('**/damage_absorb_icon')  # 3 slot absorb icon
            if self.cog.dna.name == 'ambass':
                self.extraAttacksText = DirectLabel(parent=self.absorbing, relief=None, text="1",
                                                text_fg=(1, 1, 1, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
                self.extraAttacksText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.absorbing, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isDropImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/duck_drop_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.enraged, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isZapImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/fizzle_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.enraged, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isSoakImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.soakResist = status.find('**/soaked_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.soakResist, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isLureImmune and not self.cog.dna.name == 'hrollers':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune = status.find('**/cashback_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.lureImmune, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isBookkeeping:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/backfire_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.immortal, slot)
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.getGovernaught():
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/tie_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.immortal, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isTarget or self.cog.isExplosive:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/union_bust_icon')
            if self.cog.isExplosive:
                self.damageMultText = DirectLabel(parent=self.immortal, relief=None, text="%s" % (self.cog.getExplosiveCondition() - 1), text_fg=(1, 0, 0, 1),
                                                  text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                  pos=(0.25, 0, -.5),
                                                  text_scale=.5)
                self.damageMultText.show()
            else:
                self.damageMultText = DirectLabel(parent=self.immortal, relief=None, text="1", text_fg=(1, 0, 0, 1),
                                                  text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                  pos=(0.25, 0, -.5),
                                                  text_scale=.5)
                self.damageMultText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.immortal, slot)
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.isSleepy:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/lunch_background')
            self.damageMultText = DirectLabel(parent=self.immortal, relief=None, text="%s" % (self.cog.getSleepyCondition() - 1), text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.225, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.immortal, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isDesperation:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.desperation = status.find('**/toofast4you_icon')
            self.desperationText = DirectLabel(parent=self.desperation, relief=None, text="%s" % self.cog.getDesperation() + "%", text_fg=(1, 0, 0, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.4)
            self.desperationText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.desperation, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isCollectCall:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.collectcall = status.find('**/cashback_icon')
            self.collectcallText = DirectLabel(parent=self.collectcall, relief=None, text="%s" % self.cog.getCollectCall(), text_fg=(1, 0, 0, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.4)
            self.collectcallText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.collectcall, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isInsured or self.cog.isInsured2:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')
            self.insuredRoundsText = DirectLabel(parent=self.insured, relief=None, text="%s" % (self.cog.getInsuranceRounds()),
                                         text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.insuredRoundsText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.insured, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isInsured or self.cog.isInsured2:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/heal_over_time_icon')
            if self.cog.isInsured2:
                self.insuredText = DirectLabel(parent=self.insured, relief=None, text="+85", text_fg=(0, 1, 0.047, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.4)
                self.insuredText.show()
            else:
                self.insuredText = DirectLabel(parent=self.insured, relief=None, text="+50", text_fg=(0, 1, 0.047, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.4)
                self.insuredText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.insured, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isContracted or self.cog.isContracted2 or self.cog.dna.name == 'supervis' or self.cog.dna.name == 'ovt':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')
            if not self.cog.dna.name == 'supervis':
                self.contractedRoundsText = DirectLabel(parent=self.insured, relief=None, text="%s" % (self.cog.getContractedRounds()),
                                         text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
                self.contractedRoundsText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.insured, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isContracted or self.cog.isContracted2:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/heal_over_time_icon')
            if self.cog.isContracted2:
                self.insuredText = DirectLabel(parent=self.insured, relief=None, text="+125", text_fg=(0, 1, 0.047, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.4)
                self.insuredText.show()
            else:
                self.insuredText = DirectLabel(parent=self.insured, relief=None, text="+95", text_fg=(0, 1, 0.047, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.4)
                self.insuredText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.insured, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isOilRain:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/oilrain_icon')
            self.insuredText = DirectLabel(parent=self.insured, relief=None, text="%s" % (self.cog.getOilRainRounds() - 1),
                                           text_fg=(1, 1, 1, 1),
                                           text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                           pos=(0.25, 0, -.5),
                                           text_scale=.5)
            self.insuredText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.insured, slot, slotColor=(1, 0.984, 0, 1))


        if self.cog.extraAttack:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/extra_attacks_icon')
            self.extraAttacksText = DirectLabel(parent=self.extraAttacks, relief=None, text="+%s" % self.cog.getExtraAttacks(),
                                                text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.extraAttacksText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.extraAttacks, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.extraAbility:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/extra_attacks_icon')
            self.extraAttacksText = DirectLabel(parent=self.extraAttacks, relief=None, text="%s" % self.cog.getExtraAbilities(),
                                                text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.extraAttacksText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.extraAttacks, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp = status.find('**/suit_damage_up_icon')
            self.damageMultText = DirectLabel(parent=self.damageUp, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.4)
            self.damageMultText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.damageUp, slot)
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.isDamageReduction:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageReduction = status.find('**/shield_icon')  # third slot vulnerability icon
            if self.cog.dna.name == 'rkeeper':
                self.vulnerabilityText = DirectLabel(parent=self.damageReduction, relief=None,
                                                         text="50%",
                                                         text_fg=(1, 0, 0, 1),
                                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                         pos=(0.25, 0, -.5),
                                                         text_scale=.4)
                self.vulnerabilityText.show()
            else:
                self.vulnerabilityText = DirectLabel(parent=self.damageReduction, relief=None,
                                                     text="%s" % self.cog.getDamageReduction() + "%",
                                                     text_fg=(1, 0, 0, 1),
                                                     text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                     pos=(0.25, 0, -.5),
                                                     text_scale=.4)
                self.vulnerabilityText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.damageReduction, slot)
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon = status.find('**/ink_drain_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.syphon, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isDamageDown:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp = status.find('**/suit_damage_down_icon')
            if self.cog.dna.name == 'safesupervis':
                self.damageMultText2 = DirectLabel(parent=self.damageUp, relief=None, text="25%", text_fg=(0, 1, 0.047, 1),
                                                  text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                  pos=(0.25, 0, -.5),
                                                  text_scale=.4)
                self.damageMultText2.show()
            else:
                self.damageMultText2 = DirectLabel(parent=self.damageUp, relief=None, text="%s" % self.cog.getDamageDown() + "%", text_fg=(0, 1, 0.047, 1),
                                                   text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                   pos=(0.25, 0, -.5),
                                                   text_scale=.4)
                self.damageMultText2.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.damageUp, slot)
            self._pulseStatusSlot(slot, fromColor=(0.027, 1, 0, 1), toColor=(0, 0.902, 1, 1))

        if self.cog.isVulnerable and not self.cog.dna.name == 'hroller2':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            if self.cog.dna.name == 'bcaster':
                self.vulnerabilityText = DirectLabel(parent=self.vulnerable, relief=None,
                                                 text="100%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.4)
            elif self.cog.dna.name == 'cbutcher':
                self.vulnerabilityText = DirectLabel(parent=self.vulnerable, relief=None,
                                                 text="100%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.4)
            else:
                self.vulnerabilityText = DirectLabel(parent=self.vulnerable, relief=None,
                                                     text="%s" % self.cog.getVulnerability() + "%",
                                                     text_fg=(0, 1, 0.047, 1),
                                                     text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                     pos=(0.25, 0, -.5),
                                                     text_scale=.4)
            self.vulnerabilityText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.vulnerable, slot)
            self._pulseStatusSlot(slot, fromColor=(0.027, 1, 0, 1), toColor=(0, 0.902, 1, 1))

        if self.cog.isSued:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.sued = status.find('**/sued_icon')
            self.suedRoundsText = DirectLabel(parent=self.sued, relief=None, text="%s" % (self.cog.getSuedRounds() - 1),
                                         text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.suedRoundsText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.sued, slot, slotColor=(0, 0.902, 1, 1))

        if self.cog.isSued:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.sued2 = status.find('**/damage_over_time_icon')
            self.sued2RoundsText = DirectLabel(parent=self.sued2, relief=None, text="-%s" % int(self.cog.getMaxHP() / 4),
                                               text_fg=(1, 0, 0, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.4)
            self.sued2RoundsText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.sued2, slot, slotColor=(0, 0.902, 1, 1))

        if self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            if self.cog.isLured == 1:
                self.luredCog = status.find('**/lured_icon')
            else:
                self.luredCog = status.find('**/lured_prestige_icon')
            self.luredText = DirectLabel(parent=self.luredCog, relief=None, text="%s" % self.cog.getLuredRounds(),
                                         text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.luredCog, slot, slotColor=(0, 0.902, 1, 1))

        if self.cog.isZapped:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.zapped = status.find('**/reward_cooldown_icon')
            self.zappedRoundsText = DirectLabel(parent=self.zapped, relief=None, text="-%s" % self.cog.getZapCondition(),
                                         text_fg=(1, 0, 0, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.4),
                                         text_scale=.4)
            self.zappedRoundsText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.zapped, slot, slotColor=(0, 0.902, 1, 1))

        if self.cog.isMarked:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.marked = status.find('**/deepfreeze_icon')
            self.markedRoundsText = DirectLabel(parent=self.marked, relief=None, text="1",
                                         text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.markedRoundsText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.marked, slot, slotColor=(0, 0.902, 1, 1))

        if self.cog.isDazed:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.dazed = status.find('**/confusion_icon')
            self.dazedText = DirectLabel(parent=self.dazed, relief=None,
                                         text="1",
                                         text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.dazedText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.dazed, slot, slotColor=(0, 0.902, 1, 1))

        if self.cog.isSoaked:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.soaked = status.find('**/scope_creep_icon')
            self.soakedRoundsText = DirectLabel(parent=self.soaked, relief=None, text="%s" % self.cog.getSoakRounds(),
                                         text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.soakedRoundsText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.soaked, slot, slotColor=(0, 0.902, 1, 1))

        if self.cog.isTrapped:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            if self.cog.isTrapped == 8:
                self.dazed = status.find('**/inventory_tnt')
            elif self.cog.isTrapped == 7:
                self.dazed = status.find('**/inventory_wreckingball')
            elif self.cog.isTrapped == 6:
                self.dazed = status.find('**/inventory_trapdoor')
            elif self.cog.isTrapped == 5:
                self.dazed = status.find('**/inventory_quicksand_icon')
            elif self.cog.isTrapped == 4:
                self.dazed = status.find('**/inventory_springboard')
            elif self.cog.isTrapped == 3:
                self.dazed = status.find('**/inventory_marbles')
            elif self.cog.isTrapped == 2:
                self.dazed = status.find('**/inventory_rake')
            else:
                self.dazed = status.find('**/inventory_banana_peel')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.dazed, slot, slotColor=(0, 0.902, 1, 1), scale=(5.5, 5.5, 5.5))


        self.healthText['text'] = t

    def updateHealthBar(self):
        self.setLevelText()
        condition = self.cog.healthCondition
        if self.cog.getHP() >= 0:
            self.hp = self.cog.getHP()
        else:
            self.hp = 0
        self.maxHp = self.cog.getMaxHP()
        if self.cog.isImmortal and not self.cog.dna.name == 'hroller' and not self.cog.isPhase3:
            self.hp = 'Immune'
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setProp('barColor', (1, 1, 1, 1))
                self.__changeColor()
                self.healthBar2.setProp('value', self.cog.getMaxHP())
                taskMgr.remove(self.uniqueName('blink-task2'))
        elif condition == 9:
            taskMgr.remove(self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setProp('barColor', (1, 1, 1, 1))
                self.__changeColor()
                self.healthBar2.setProp('value', self.cog.getHP())
                taskMgr.remove(self.uniqueName('blink-task2'))
        elif condition == 10:
            taskMgr.remove(self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setProp('barColor', (1, 1, 1, 1))
                self.__changeColor()
                self.healthBar2.setProp('value', self.cog.getHP())
                blinkTask = Task.loop(Task(self.__pulseRed), Task.pause(0.75), Task(self.__pulseGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task2'))
        elif condition == 11:
            taskMgr.remove(self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setProp('barColor', (1, 1, 1, 1))
                self.__changeColor()
                self.healthBar2.setProp('value', self.cog.getHP())
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task2'))
        elif condition == 13:
            taskMgr.remove(self.uniqueName('blink-task2'))
            if self.healthBar2:
                self.healthBar2.setProp('barColor', (1, 1, 1, 1))
                self.healthBar2.setProp('value', self.cog.getHP())
                blinkTask = Task.loop(Task(self.__blinkPurple), Task.pause(1), Task(self.__blinkPurpleColor),
                                      Task.pause(3))
                taskMgr.add(blinkTask, self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(1, 1, 1, 1.0)
        else:
            taskMgr.remove(self.uniqueName('blink-task'))
            if self.healthBar2:
                self.healthBar2.setProp('barColor', (1, 1, 1, 1))
                self.__changeColor()
                self.healthBar2.setProp('value', self.cog.getHP())
                taskMgr.remove(self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
        if self.cog.isImmortal and not self.cog.dna.name == 'hroller' and not self.cog.isPhase3:
            self.hpText['text'] = str(self.hp)
        else:
            self.hpText['text'] = str(self.hp) + '/' + str(self.maxHp)

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
        if self.cog.isImmortal and not self.cog.dna.name == 'hroller' and not self.cog.isPhase3:
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


    def generateSuitHead(self, name):
        self.suitHead = Suit.attachSuitHead(self, name)
        self.suitHead.setScale(0.1)
        AnimList = 'neutral'
        if name == 'bfh2':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -90, 0, 0, .105, .105, .105)
        elif name == 'ls':
            self.suitHead.setPosHprScale(-0.26, 0.5, 0.12, -90, 0, 0, .085, .085, .085)
        elif name == 'mg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .115, .115, .115)
        elif name == 'whistleb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .0775, .0775, .0775)
        elif name == 'ksp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .09, .09, .09)
        elif name == 'ppl':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .095, .095, .095)
        elif name == 'stenog' or name == 'crystal' or name == 'rkeeper':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0725, .0725, .0725)
        elif name == 'cbutcher':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0725, .0725, .0725)
            self.suitHead.setColor((0, 0, 0, 1))
        elif name == 'clubpres':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .105, .105, .105)
        elif name == 'fmaker':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .105, .105, .105)
        elif name == 'director':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .105, .105, .105)
        elif name == 'choreo':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .105, .105, .105)
        elif name == 'cinema':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .105, .105, .105)
        elif name == 'key':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .065, .065, .065)
        elif name == 'sgoat':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .1, .1, .1)
        elif name == 'tbc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .09, .09, .09)
        elif name == 'hroller2' or name == 'hrollers' or name == 'hroller' or name == 'ghd':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .09, .09, .09)
        elif name == 'hho':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .07, .07, .07)
        elif name == 'br':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .1, .1, .1)
        elif name == 'pph':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.085, -180, 0, 0, .1, .1, .1)
        elif name == 'bkeeper':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .09, .09, .09)
        elif name == 'cbr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .065, .065, .065)
        elif name == 'le':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.135, -180, 0, 0, .115, .115, .115)
        elif name == 'bgh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.135, -180, 0, 0, .1, .1, .1)
        elif name == 'cv':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .075, .075, .075)
        elif name == 'm' or name == 'tf' or name == 'mdm' or name == 'dc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .089, .089, .089)
        elif name == 'pp' or name == 'sw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .06, .06, .06)
        elif name == 'p':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .07, .07, .07)
        elif name == 'bc' or name == 'kbc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1, .1, .1)
        elif name == 'txm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .12, .12, .12)
        elif name == 'b':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .09, .09, .09)
        elif name == 'wtapper':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .08, .08, .08)
        elif name == 'prethink':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .1, .1, .1)
        elif name == 'ambass':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .1, .1, .1)
        elif name == 'mouthp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1, .1, .1)
        elif name == 'bf':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .12, .12, .12)
        elif name == 'chw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .16, .16, .16)
        elif name == 'mldr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .095, .095, .095)
        elif name == 'mh' or name == 'ym' or name == 'trs' or name == 'chairp' or name == 'std2' or name == 'bsht' or name == 'std' or name == 'enf' or name == 'rb' or name == 'mh2' or name == 'cnd' or name == 'vpr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .105, .105, .105)
        elif name == 'pyc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .13, .13, .13)
        elif name == 'gms':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .095, .095, .095)
        elif name == 'ms' or name == 'inw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .085, .085, .085)
        elif name == 'fct':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .12, .12, .12)
        elif name == 'fcs':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .091, .091, .091)
        elif name == 'sd':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .075, .075, .075)
        elif name == 'sh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .09, .09, .09)
        elif name == 'ang':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .07, .07, .07)
        elif name == 'mm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .12, .12, .12)
        elif name == 'bw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .09, .09, .09)
        elif name == 'ad':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .1, .1, .1)
        elif name == 'rus' or name == 'tm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .085, .085, .085)
        elif name == 'sdb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .0675, .0675, .0675)
        elif name == 'ds':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .0825, .0825, .0825)
        elif name == 'cn':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .08, .08, .08)
        elif name == 'bs':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .0675, .0675, .0675)
        elif name == 'nn':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .09, .09, .09)
        elif name == 'ac':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .08, .08, .08)
        elif name == 'cc' or name == 'sc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .12, .12, .12)
        elif name == 'blh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .17, .177, .177)
        elif name == 'hh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .175, .175, .175)
        elif name == 'f' or name == 'cr' or name == 'ca' or name == 'skd' or name == 'tw' or name == 'asm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .175, .175, .175)
        elif name == 'nc' or name == 'nd' or name == 'sfs':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .08, .08, .08)
        elif name == 'txl':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .085, .085, .085)
        elif name == 'derrman':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .1, .1, .1)
        elif name == 'treek':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .075, .075, .075)
        elif name == 'pcrat':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .085, .085, .085)
        elif name == 'dopa':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .095, .095, .095)
        elif name == 'dopr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .1675, .1675, .1675)
        elif name == 'fires':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .0675, .0675, .0675)
        elif name == 'safesupervis':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .0675, .0675, .0675)
        elif name == 'watchm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1, .1, .1)
        elif name == 'mplayer' or name == 'mplayer2':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .08, .08, .08)
        elif name == 'chainsaw' or name == 'chainsaw2':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0875, .0875, .0875)
        elif name == 'duckshfl':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .075, .075, .075)
        elif name == 'bellring':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.095, -180, 0, 0, .08, .08, .08)
        elif name == 'liquid':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .075, .075, .075)
        elif name == 'ubuster':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1025, .1025, .1025)
        elif name == 'radiog':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .0725, .0725, .0725)
        elif name == 'gatekeep':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .055, .055, .055)
        elif name == 'djockey' or name == 'ptjockey':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .055, .055, .055)
        elif name == 'dola':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .0875, .0875, .0875)
        elif name == 'phouse':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .065, .065, .065)
        elif name == 'dking':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.145, -180, 0, 0, .08, .08, .08)
        elif name == 'racket':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .115, .115, .115)
        elif name == 'redd':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.145, -180, 0, 0, .08, .08, .08)
        elif name == 'chairman':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .095, .095, .095)
        elif name == 'dold':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .08, .08, .08)
        elif name == 'mslacker' or name == 'videog' or name == 'bcaster':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .06, .06, .06)
        elif name == 'wsi' or name == 'kerberos' or name == 'charon' or name == 'bdirector' or name == 'sya' or name == 'pbl' or name == 'foreman':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .12, .12, .12)
        elif name == 'shw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .00001, .00001, .00001)
        elif name == 'autocad':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .125, .125, .125)
        elif name == 'hydra' or name == 'styx' or name == 'supervis':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .3, .3, .3)
        elif name == 'clerk' or name == 'ovt' or name == 'ant' or name == 'nix' or name == 'jls':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .2, .2, .2)
        elif name == 'judy':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .1, .1, .1)
        elif name == 'bf':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .11, .11, .11)
        elif name == 'whunter':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0575, .0575, .0575)
        elif name == 'rainmake':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.155, -180, 0, 0, .07, .07, .07)
        elif name == 'erfit' or name == 'erclaim':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.135, -180, 0, 0, .075, .075, .075)
        elif name == 'derrhand':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .09, .09, .09)
        elif name == 'caseman':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.15, -180, 0, 0, .09, .09, .09)
        elif name == 'dl':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .11, .11, .11)
        elif name == 'bfh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .08, .08, .08)
        elif name == 'dt':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .08, .08, .08)
        elif name == 'itn':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .115, .115, .115)
        elif name == 'brn':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .085, .085, .085)
        elif name == 'cmk':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .155, .155, .155)
        elif name == 'dhr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .115, .115, .115)
        elif name == 'ins':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .105, .105, .105)
        elif name == 'fbed':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.135, -180, 0, 0, .14, .14, .14)
        elif name == 'shy':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1225, -180, 0, 0, .14, .14, .14)
        elif name == 'ppb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .105, .105, .105)
        elif name == 'shb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .075, .075, .075)
        elif name == 'bsd':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .15, .15, .15)
        elif name == 'sbg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .12, .12, .12)
        elif name == 'hck':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0875, .0875, .0875)
        elif name == 'ath':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .08, .08, .08)
        elif name == 'ghw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .07, .07, .07)
        elif name == 'dcw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .065, .065, .065)
        elif name == 'gzt':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .075, .075, .075)
        elif name == 'wnk':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .13, .13, .13)
        elif name == 'nsh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .08, .08, .08)
        elif name == 'anc':
            self.suitHead.setPosHprScale(-0.28, 0.5, 0.11, -180, 0, 0, .0725, .0725, .0725)
        elif name == 'stg':
            self.suitHead.setPosHprScale(-0.28, 0.5, 0.12, -180, 0, 0, .14, .14, .14)
        elif name == 'blk':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .095, .095, .095)
        elif name == 'psetter':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .105, .105, .105)
        elif name == 'gld':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1075, .1075, .1075)
        elif name == 'arbit' or name == 'cdirector':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0925, .0925, .0925)
        else:
            self.suitHead.setPos(-0.27, 0.5, 0.13)

    def show(self):
        if settings.get('show-cog-levels', True):
            if self.cog:
                self.updateHealthBar()
            self.hidden = False
            self.healthNode.show()
            self.button.show()
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
        self.button.hide()
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

