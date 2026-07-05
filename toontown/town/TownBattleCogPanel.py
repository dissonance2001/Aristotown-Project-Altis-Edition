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
from toontown.quest.QuestPoster import QuestPoster

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
            elif self.cog.getExecutive():
                t += TTLocalizer.ExecutivePostFix
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
            elif self.cog.isDesperation or self.cog.isBookkeeping or self.cog.dna.name in ('bcaster', 'hroller', 'hroller2', 'videog', 'fires', 'fbed', 'mouthp', 'rainmake', 'whunter', 'wsi', 'redd', 'duckshfl', 'treek', 'director', 'bellring', 'ddiver', 'gatekeep')\
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
            self._attachStatusIcon(self.luredManager, slot, slotColor=(1, 0.984, 0, 1))
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
            self._attachStatusIcon(self.immortal, slot, slotColor=(1, 0.984, 0, 1))
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.dna.name == 'hroller2' and not self.cog.isVulnerable and self.cog.isPhase3:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/harmonious_colors_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.extraAttacks, slot)
            self._clear_status_interval('rainbowPulseTask')
            self._pulseRainbowStatusSlot(slot, duration=2.0)

        if self.cog.dna.name == 'hustle':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/last_tap_icon')
            texture = loader.loadTexture(
                'phase_3.5/maps/battlegui/status_effects_palette_4allc_12.png'
            )

            self.enraged.clearTexture()
            self.enraged.setTexture(texture, 1)
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.enraged, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.dna.name == 'hrollers':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            if self.cog.getActualLevel() == 36:
                self.rainbow = status.find('**/confusion_icon')
            if self.cog.getActualLevel() == 35:
                self.rainbow = status.find('**/damage_absorb_icon')
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

        if self.cog.isGreenLight:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/fog_icon')
            texture = loader.loadTexture(
                'phase_3.5/maps/battlegui/status_effects_palette_4allc_12.png'
            )

            self.enraged.clearTexture()
            self.enraged.setTexture(texture, 1)
            self.enrageCountText = DirectLabel(parent=self.enraged, relief=None,
                                              text="1", text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.enrageCountText.show()
            self.enrageCountText.clearTexture()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.enraged, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isRedLight:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/heavyrain_icon')
            texture = loader.loadTexture(
                'phase_3.5/maps/battlegui/status_effects_palette_4allc_12.png'
            )

            self.enraged.clearTexture()
            self.enraged.setTexture(texture, 1)
            self.enrageCountText = DirectLabel(parent=self.enraged, relief=None,
                                              text="1", text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.enrageCountText.show()
            self.enrageCountText.clearTexture()
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
            self._attachStatusIcon(self.immortal, slot, slotColor=(1, 0.984, 0, 1))
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.getGovernaught():
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/tie_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.immortal, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.dna.name == 'mh2' or self.cog.dna.name == 'std2':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/tie_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.immortal, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.isTarget or self.cog.isExplosive or self.cog.isOverpressured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/union_bust_icon')
            if self.cog.isExplosive:
                self.damageMultText = DirectLabel(parent=self.immortal, relief=None, text="%s" % (self.cog.getExplosiveCondition() - 1), text_fg=(1, 0, 0, 1),
                                                  text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                  pos=(0.25, 0, -.5),
                                                  text_scale=.5)
                self.damageMultText.show()
            else:
                if not self.cog.isOverpressured:
                    self.damageMultText = DirectLabel(parent=self.immortal, relief=None, text="1", text_fg=(1, 0, 0, 1),
                                                    text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                    pos=(0.25, 0, -.5),
                                                    text_scale=.5)
                    self.damageMultText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.immortal, slot, slotColor=(1, 0.984, 0, 1))
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

        if self.cog.isOverseer:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.collectcall = status.find('**/gatekeeper_icon')
            self.collectcallText = DirectLabel(parent=self.collectcall, relief=None, text="%s" % self.cog.getOverseerRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.collectcallText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.collectcall, slot, slotColor=(1, 0.984, 0, 1))

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
            if not self.cog.dna.name == 'supervis' and not self.cog.dna.name == 'ovt':
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

        if self.cog.isOilRain:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/diving_icon')
            self.insuredText = DirectLabel(parent=self.insured, relief=None, text="%s" % (self.cog.getOilRainRounds() - 1),
                                           text_fg=(1, 1, 1, 1),
                                           text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                           pos=(0.25, 0, -.5),
                                           text_scale=.5)
            self.insuredText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.insured, slot, slotColor=(1, 0.984, 0, 1))


        if self.cog.battleSpeed and self.cog.dna.name == 'clerk' and self.cog.getActualLevel() == 24:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/mileaminute_icon')
            self.insuredText = DirectLabel(parent=self.insured, relief=None, text="x%s" % (self.cog.getBattleSpeed()),
                                           text_fg=(1, 1, 1, 1),
                                           text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                           pos=(0.25, 0, -.5),
                                           text_scale=.4)
            self.insuredText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.insured, slot, slotColor=(1, 0.984, 0, 1))

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

        if self.cog.isDeepFrozen:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/frozen_icon')
            self.insuredText = DirectLabel(parent=self.insured, relief=None, text="%s" % (self.cog.getDeepFrozenRounds() - 1),
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

        if self.cog.isDanceSession:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/singing_blues_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.extraAttacks, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.extraAbility:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/chainsaw_icon')
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
            self._attachStatusIcon(self.damageUp, slot, slotColor=(1, 0.984, 0, 1))
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.ripped:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp = status.find('**/ripped_icon')
            self.damageMultText = DirectLabel(parent=self.damageUp, relief=None, text="%s" % self.cog.getRippedUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.4)
            self.damageMultText.show()
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.damageUp, slot, slotColor=(1, 0.984, 0, 1))
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.isDamageReduction:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            if self.cog.dna.name == 'erclaim':
                self.damageReduction = status.find('**/kickback_icon')  # third slot vulnerability icon
            else:
                self.damageReduction = status.find('**/shield_icon') 
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
            self._attachStatusIcon(self.damageReduction, slot, slotColor=(1, 0.984, 0, 1))
            self._pulseStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(1, 0.984, 0, 1))

        if self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon = status.find('**/ink_drain_icon')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.syphon, slot, slotColor=(1, 0.984, 0, 1))

        if self.cog.trapRushJob:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.syphon = status.find('**/inventory_wreckingball')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.syphon, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if self.cog.lureRushJob:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.syphon = status.find('**/inventory_hypno_goggles')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.syphon, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if self.cog.throwRushJob:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.syphon = status.find('**/inventory_cake')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.syphon, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if self.cog.squirtRushJob:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.syphon = status.find('**/inventory_storm_cloud')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.syphon, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if self.cog.zapRushJob:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.syphon = status.find('**/inventory_tesla_coil')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.syphon, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if self.cog.soundRushJob:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.syphon = status.find('**/inventory_fog_horn')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.syphon, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if self.cog.dropRushJob:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.syphon = status.find('**/inventory_boulder')
            slot = self._claimNextStatusSlot()
            self._attachStatusIcon(self.syphon, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

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
            self._attachStatusIcon(self.damageUp, slot, slotColor=(0, 0.902, 1, 1))
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
                                                 text="300%",
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
            self._attachStatusIcon(self.vulnerable, slot, slotColor=(0, 0.902, 1, 1))
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

    def createSuitHead(self, suitName, dimension=.8, setH=180):
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
    
    def fitGeometry(self, geom, fFlip = 0, dimension = 0.8, setH=180):
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
            head = self.createSuitHead(name, .7, 270)
        elif self.cog.dna.name == 'bfh2':
            head = self.createSuitHead(name, .8, 270)
        else:
            head = self.createSuitHead(name, .8, 180)
        head.copyTo(self.suitHead)

        if self.cog.dna.name == 'shw':
            self.suitHead.setPos(-0.265, 0.5, 0.1975)
        else:
            self.suitHead.setPos(-0.27, 0.5, 0.1975)
        if self.cog.dna.name == 'ls':
            self.suitHead.setScale(.225)
        else:
            self.suitHead.setScale(.25)

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

