from panda3d.core import *
from panda3d.direct import *
from toontown.battle.BattleGlobals import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownBattleGlobals import *
from direct.directnotify import DirectNotifyGlobal
import string
import math
from toontown.toon import LaffMeter
from toontown.battle import BattleBase
from toontown.toonbase import ToontownBattleGlobals
from direct.task.Task import Task
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from panda3d.direct import *
from toontown.toonbase import TTLocalizer

class TownBattleToonPanel(DirectFrame):
    notify = DirectNotifyGlobal.directNotify.newCategory('TownBattleToonPanel')

    def __init__(self, id):
        if settings['newGui'] == True:
            gui = loader.loadModel('phase_3.5/models/gui/battle_gui_new')
        else:
            gui = loader.loadModel('phase_3.5/models/gui//battlegui/toon_panel')
        
        DirectFrame.__init__(self, relief=None, image=gui.find('**/toon_panel_frame'))
        self.setScale(0.5)
        self.initialiseoptions(TownBattleToonPanel)
        self.status = None
        self.liquidated = None
        self.liquidatedText = None
        self.governaughtDamageUp = None
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
        # self.snapped = status.find('**/vulnerable_icon')
        # self.snapped.setPosHprScale(-0.25, 0, 0.03, -180, 0, 0, .125, .125, .125)
        # self.snapped.reparentTo(self)
        # self.snapped.hide()
        # self.vulnerable = status.find('**/broken_shield_icon')
        # self.vulnerable.setPosHprScale(0.22, 0, 0.03, -180, 0, 0, .125, .125, .125)
        # self.vulnerable.reparentTo(self)
        # self.vulnerable.hide()
        self.sosText = DirectLabel(parent=self, relief=None, pos=(0.22, 0, 0.03), text=TTLocalizer.TownBattleToonSOS, text_fg=(0.176, 1, 0, 1), text_scale=0.1, text_font=getSignFont())
        self.sosText.hide()
        self.fireText = DirectLabel(parent=self, relief=None, pos=(0.22, 0, 0.03), text=TTLocalizer.TownBattleToonFire, text_fg=(1, 0, 0, 1), text_scale=0.1, text_font=getSignFont())
        self.fireText.hide()
        self.sueText = DirectLabel(parent=self, relief=None, pos=(0.22, 0, 0.03), text=TTLocalizer.TownBattleToonSue, text_fg=(0.75, 0.75, 0.95, 1), text_scale=0.1, text_font=getSignFont())
        self.sueText.hide()
        self.roundsText = DirectLabel(parent=self, relief=None, pos=(0, 0.05, 0.25), text='', text_scale=0.15, text_fg=(0.176, 1, 0, 1), text_font=getSignFont())
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
        self.passText = DirectLabel(parent=self, relief=None, pos=(0.2, 0, 0.03),
                                    text='', text_scale=0.1, text_fg=(1, 0, 0, 1), text_font=getSignFont())
        self.passText.hide()
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
        self.whichText = DirectLabel(parent=self, text='', pos=(0.22, 0.1, -0.24), text_scale=0.1, text_font=getSignFont())
        self.hide()
        gui.removeNode()

    def _attachToonStatusIcon(self, iconNode, slot, slotColor=(1, 1, 1, 1), scale=(1, 1, 1)):
        if slot is None:
            return

        if isinstance(scale, (int, float)):
            scale = (scale, scale, scale)

        sx, sy, sz = scale

        slot['bg'].setColor(*slotColor)
        slot['bg'].setColorScale(1, 1, 1, 1)
        slot['bg'].show()

        slot['iconRoot'].show()
        iconNode.reparentTo(slot['iconRoot'])
        iconNode.setPosHprScale(0, 0, 0, 0, 0, 0, sx, sy, sz)
        iconNode.setColor(1, 1, 1, 1)
        iconNode.setColorScale(1, 1, 1, 1)
        iconNode.show()

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
        self._clear_toon_status_interval('pulseTask')
        self._clear_toon_status_interval('rainbowPulseTask')

        if hasattr(self, 'toonStatusSlots'):
            for slot in self.toonStatusSlots:
                pulse = slot.get('pulse')
                if pulse is not None:
                    try:
                        pulse.finish()
                    except:
                        pass
                    slot['pulse'] = None

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
                'cheerRounds', 'cheer', 'burnedRounds', 'burned',
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
            return None

        slot = self.toonStatusSlots[self.statusEffects]
        self.statusEffects += 1

        if self.statusEffects > 4:
            slot['bg'].show()
            slot['iconRoot'].show()

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

    def _pulseToonStatusSlot(self, slot, fromColor, toColor=(1, 1, 1, 1), duration=1.0):
        if slot is None:
            return

        self._stopToonStatusPulse(slot)

        r, g, b, z = toColor
        slot['bg'].setColorScale(r, g, b, z)

        slot['pulse'] = Sequence(
            LerpColorScaleInterval(slot['bg'], duration, fromColor, blendType='easeInOut'),
            LerpColorScaleInterval(slot['bg'], duration, toColor, blendType='easeInOut'), Wait(1.0)
        )
        slot['pulse'].loop()

    def _pulseRainbowToonStatusSlot(self, slot, duration=0.35):
        if slot is None:
            return

        self._stopToonStatusPulse(slot)

        slot['bg'].setColorScale(1, 1, 1, 1)

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

    def _buildToonStatusSlots(self):
        slotLayouts = [
            (-0.39, 0, 0.075),  # 1
            (-0.3675, 0, -0.05),  # 2
            (-0.29, 0, -0.15),  # 3
            (-0.1675, 0, -0.1925),  # 4
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
            bgNode.setPosHprScale(x, y, z, 0, 0, 0, .125, .125, .125)
            bgNode.setColor(0.525, 0.133, 0.122, 1)

            iconRoot = self.attachNewNode('toonStatusIconRoot-%d' % i)
            iconRoot.setPosHprScale(x, y, z, 0, 0, 0, .125, .125, .125)

            if i >= 4:
                bgNode.hide()
                iconRoot.hide()

            self.toonStatusSlots[i] = {
                'bgModel': bgModel,
                'bg': bgNode,
                'iconRoot': iconRoot,
                'pulse': None,
            }

        # backward compatibility names
        self.status = self.toonStatusSlots[0]['bgModel']
        self.status2 = self.toonStatusSlots[1]['bgModel']
        self.status3 = self.toonStatusSlots[2]['bgModel']
        self.status4 = self.toonStatusSlots[3]['bgModel']
        self.status5 = self.toonStatusSlots[4]['bgModel']
        self.status6 = self.toonStatusSlots[5]['bgModel']
        self.status7 = self.toonStatusSlots[6]['bgModel']
        self.status8 = self.toonStatusSlots[7]['bgModel']
        self.status9 = self.toonStatusSlots[8]['bgModel']
        self.status10 = self.toonStatusSlots[9]['bgModel']

        self.attackIcon = self.toonStatusSlots[0]['bg']
        self.attackIcon1 = self.toonStatusSlots[1]['bg']
        self.attackIcon2 = self.toonStatusSlots[2]['bg']
        self.attackIcon3 = self.toonStatusSlots[3]['bg']
        self.attackIcon4 = self.toonStatusSlots[4]['bg']
        self.attackIcon5 = self.toonStatusSlots[5]['bg']
        self.attackIcon6 = self.toonStatusSlots[6]['bg']
        self.attackIcon7 = self.toonStatusSlots[7]['bg']
        self.attackIcon8 = self.toonStatusSlots[8]['bg']
        self.attackIcon9 = self.toonStatusSlots[9]['bg']

    def setStatusEffects(self, avatar):
        self.avatar = avatar
        self._cleanupToonStatusDisplay()
        self._buildToonStatusSlots()

        if avatar.raisedAnte:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.raisedAnte = status.find('**/raise_the_ante_icon')
            self.raisedAnteText = DirectLabel(parent=self.raisedAnte, relief=None, text="%s" % avatar.getRaisedAnte() + "%", text_fg=(0, 1, 0.004, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, 0.15),
                                              text_scale=.4)
            self.raisedAnteText.show()
            self.raisedAnte.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.raisedAnte, slot)
            self._clear_toon_status_interval('rainbowPulseTask')
            self.rainbowPulseTask = self._pulseRainbowToonStatusSlot(slot, duration=2.0)

        if avatar.governaughtDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.governaughtDamageUp = status.find('**/toon_damage_up_icon')
            self.govDamageText = DirectLabel(parent=self.governaughtDamageUp, relief=None, text="%s" % avatar.getDamageUpGovernaught() + "%", text_fg=(0, 1, 0.004, 1),
                                             text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                             pos=(0.25, 0, 0.15),
                                             text_scale=.4)
            self.govDamageText.show()
            self.governaughtDamageUp.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.governaughtDamageUp, slot)
            self._pulseToonStatusSlot(slot, fromColor=(0.027, 1, 0, 1), toColor=(1, 0.984, 0, 1))

        if avatar.damageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp = status.find('**/toon_damage_up_icon')
            self.damageUpRounds = DirectLabel(parent=self.damageUp, relief=None, text="%s" % avatar.getDamageUpRounds(), text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.6)
            self.damageUpRounds.show()
            self.damageUpText = DirectLabel(parent=self.damageUp, relief=None, text="%s" % avatar.getDamageUp() + "%", text_fg=(0, 1, 0.004, 1),
                                            text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                            pos=(0.25, 0, 0.15),
                                            text_scale=.4)
            self.damageUpText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.damageUp, slot)
            self._pulseToonStatusSlot(slot, fromColor=(0.027, 1, 0, 1), toColor=(1, 0.984, 0, 1))

        if avatar.gagBoost:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.gagBoost = status.find('**/toon_damage_up_icon')
            self.gagBoostRoundsText = DirectLabel(parent=self.gagBoost, relief=None, text="%s" % avatar.getGagBoostRounds(), text_fg=(1, 1, 1, 1),
                                                  text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                  pos=(0.25, 0, -.5),
                                                  text_scale=.6)
            self.gagBoostRoundsText.show()
            self.gagBoostText = DirectLabel(parent=self.gagBoost, relief=None, text="%s" % avatar.getGagBoost() + "%", text_fg=(0, 1, 0.004, 1),
                                            text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                            pos=(0.25, 0, 0.15),
                                            text_scale=.4)
            self.gagBoostText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.gagBoost, slot)
            self._pulseToonStatusSlot(slot, fromColor=(0.027, 1, 0, 1), toColor=(1, 0.984, 0, 1))

        if avatar.toonupGagBoost:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.toonupGagBoost = status.find('**/inventory_cannon')
            self.toonupGagBoostRoundsText = DirectLabel(parent=self.toonupGagBoost, relief=None, text="%s" % avatar.getToonupGagBoostRounds(), text_fg=(1, 1, 1, 1),
                                                        text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                        pos=(0.045, 0, -.085),
                                                        text_scale=.1)
            self.toonupGagBoostRoundsText.show()
            self.toonupGagBoostText = DirectLabel(parent=self.toonupGagBoost, relief=None, text="%s" % avatar.getToonupGagBoost() + "%", text_fg=(0, 1, 0.004, 1),
                                                  text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                  pos=(0.045, 0, 0.027),
                                                  text_scale=.07)
            self.toonupGagBoostText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.toonupGagBoost, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if avatar.trapGagBoost:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.trapGagBoost = status.find('**/inventory_wreckingball')
            self.trapGagBoostRoundsText = DirectLabel(parent=self.trapGagBoost, relief=None, text="%s" % avatar.getTrapGagBoostRounds(), text_fg=(1, 1, 1, 1),
                                                      text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                      pos=(0.045, 0, -.085),
                                                      text_scale=.1)
            self.trapGagBoostRoundsText.show()
            self.trapGagBoostText = DirectLabel(parent=self.trapGagBoost, relief=None, text="%s" % avatar.getTrapGagBoost() + "%", text_fg=(0, 1, 0.004, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.045, 0, 0.027),
                                                text_scale=.07)
            self.trapGagBoostText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.trapGagBoost, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if avatar.lureGagBoost:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.lureGagBoost = status.find('**/inventory_hypno_goggles')
            self.lureGagBoostRoundsText = DirectLabel(parent=self.lureGagBoost, relief=None, text="%s" % avatar.getLureGagBoostRounds(), text_fg=(1, 1, 1, 1),
                                                      text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                      pos=(0.045, 0, -.085),
                                                      text_scale=.1)
            self.lureGagBoostRoundsText.show()
            self.lureGagBoostText = DirectLabel(parent=self.lureGagBoost, relief=None, text="%s" % avatar.getLureGagBoost() + "%", text_fg=(0, 1, 0.004, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.045, 0, 0.027),
                                                text_scale=.07)
            self.lureGagBoostText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.lureGagBoost, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if avatar.throwGagBoost:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.throwGagBoost = status.find('**/inventory_cake')
            self.throwGagBoostRoundsText = DirectLabel(parent=self.throwGagBoost, relief=None, text="%s" % avatar.getThrowGagBoostRounds(), text_fg=(1, 1, 1, 1),
                                                       text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                       pos=(0.045, 0, -.085),
                                                       text_scale=.1)
            self.throwGagBoostRoundsText.show()
            self.throwGagBoostText = DirectLabel(parent=self.throwGagBoost, relief=None, text="%s" % avatar.getThrowGagBoost() + "%", text_fg=(0, 1, 0.004, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.045, 0, 0.027),
                                                 text_scale=.07)
            self.throwGagBoostText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.throwGagBoost, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if avatar.squirtGagBoost:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.squirtGagBoost = status.find('**/inventory_storm_cloud')
            self.squirtGagBoostRoundsText = DirectLabel(parent=self.squirtGagBoost, relief=None, text="%s" % avatar.getSquirtGagBoostRounds(), text_fg=(1, 1, 1, 1),
                                                        text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                        pos=(0.045, 0, -.085),
                                                        text_scale=.1)
            self.squirtGagBoostRoundsText.show()
            self.squirtGagBoostText = DirectLabel(parent=self.squirtGagBoost, relief=None, text="%s" % avatar.getSquirtGagBoost() + "%", text_fg=(0, 1, 0.004, 1),
                                                  text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                  pos=(0.045, 0, 0.027),
                                                  text_scale=.07)
            self.squirtGagBoostText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.squirtGagBoost, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if avatar.zapGagBoost:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.zapGagBoost = status.find('**/inventory_tesla_coil')
            self.zapGagBoostRoundsText = DirectLabel(parent=self.zapGagBoost, relief=None, text="%s" % avatar.getZapGagBoostRounds(), text_fg=(1, 1, 1, 1),
                                                     text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                     pos=(0.045, 0, -.085),
                                                     text_scale=.1)
            self.zapGagBoostRoundsText.show()
            self.zapGagBoostText = DirectLabel(parent=self.zapGagBoost, relief=None, text="%s" % avatar.getZapGagBoost() + "%", text_fg=(0, 1, 0.004, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.045, 0, 0.027),
                                               text_scale=.07)
            self.zapGagBoostText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.zapGagBoost, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if avatar.soundGagBoost:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.soundGagBoost = status.find('**/inventory_fog_horn')
            self.soundGagBoostRoundsText = DirectLabel(parent=self.soundGagBoost, relief=None, text="%s" % avatar.getSoundGagBoostRounds(), text_fg=(1, 1, 1, 1),
                                                       text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                       pos=(0.045, 0, -.085),
                                                       text_scale=.1)
            self.soundGagBoostRoundsText.show()
            self.soundGagBoostText = DirectLabel(parent=self.soundGagBoost, relief=None, text="%s" % avatar.getSoundGagBoost() + "%", text_fg=(0, 1, 0.004, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.045, 0, 0.027),
                                                 text_scale=.07)
            self.soundGagBoostText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.soundGagBoost, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if avatar.dropGagBoost:
            status = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            self.dropGagBoost = status.find('**/inventory_boulder')
            self.dropGagBoostRoundsText = DirectLabel(parent=self.dropGagBoost, relief=None, text="%s" % avatar.getDropGagBoostRounds(), text_fg=(1, 1, 1, 1),
                                                      text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                      pos=(0.045, 0, -.085),
                                                      text_scale=.1)
            self.dropGagBoostRoundsText.show()
            self.dropGagBoostText = DirectLabel(parent=self.dropGagBoost, relief=None, text="%s" % avatar.getDropGagBoost() + "%", text_fg=(0, 1, 0.004, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.045, 0, 0.027),
                                                text_scale=.07)
            self.dropGagBoostText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.dropGagBoost, slot, slotColor=(1, 0.984, 0, 1), scale=(5.5, 5.5, 5.5))

        if avatar.cheer:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.cheer = status.find('**/cheer_icon')
            self.cheerRounds = DirectLabel(parent=self.cheer, relief=None, text="%s" % avatar.getCheerRounds(), text_fg=(1, 1, 1, 1),
                                            text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                            pos=(0.25, 0, -.5),
                                            text_scale=.6)
            self.cheerRounds.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.cheer, slot, slotColor=(1, 0.984, 0, 1))

        if avatar.encore:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.encore = status.find('**/encore_icon')
            self.encoreRounds = DirectLabel(parent=self.encore, relief=None, text="%s" % avatar.getEncoreRounds(), text_fg=(1, 1, 1, 1),
                                            text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                            pos=(0.25, 0, -.5),
                                            text_scale=.6)
            self.encoreRounds.show()
            self.encoreText = DirectLabel(parent=self.encore, relief=None, text="%s" % avatar.getEncore() + "%", text_fg=(0, 1, 0.004, 1),
                                          text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                          pos=(0.25, 0, 0.15),
                                          text_scale=.4)
            self.encoreText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.encore, slot, slotColor=(1, 0.984, 0, 1))

        if avatar.isGagBan:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.gagBan = status.find('**/backfire_icon')
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.gagBan, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.isSnapped:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.snapped = status.find('**/vulnerable_icon')
            self.snappedRoundsText = DirectLabel(parent=self.snapped, relief=None, text="%s" % avatar.getSnappedRounds(), text_fg=(1, 1, 1, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.6)
            self.snappedRoundsText.show()
            self.snappedText = DirectLabel(parent=self.snapped, relief=None, text="%s" % avatar.getSnapped() + "%", text_fg=(1, 0, 0, 1),
                                           text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                           pos=(0.25, 0, 0.15),
                                           text_scale=.4)
            self.snappedText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.snapped, slot)
            self._pulseToonStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(0, 0.902, 1, 1))

        if avatar.isBombed:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.bombed = status.find('**/trap_card_icon')
            self.bombedRoundsText = DirectLabel(parent=self.bombed, relief=None, text="%s" % avatar.getBombedRounds(), text_fg=(1, 1, 1, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.6)
            self.bombedRoundsText.show()
            # self.bombedText = DirectLabel(parent=self.bombed, relief=None, text="%s" % avatar.getBombed() + "%", text_fg=(1, 0, 0, 1),
            #                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
            #                               pos=(0.25, 0, 0.15),
            #                               text_scale=.4)
            # self.bombedText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.bombed, slot)
            self._pulseToonStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(0, 0.902, 1, 1))

        if avatar.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable = status.find('**/broken_shield_icon')
            self.vulnerableRoundsText = DirectLabel(parent=self.vulnerable, relief=None, text="%s" % avatar.getVulnerabilityRounds(), text_fg=(1, 1, 1, 1),
                                                    text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                    pos=(0.25, 0, -.5),
                                                    text_scale=.6)
            self.vulnerableRoundsText.show()
            self.vulnerableText = DirectLabel(parent=self.vulnerable, relief=None, text="%s" % avatar.getVulnerability() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, 0.15),
                                              text_scale=.4)
            self.vulnerableText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.vulnerable, slot)
            self._pulseToonStatusSlot(slot, fromColor=(1, 0, 0, 1), toColor=(0, 0.902, 1, 1))

        if avatar.markedWood: # marked for extra damage not marked wood
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.markedWood = status.find('**/sued_icon')
            self.markedWoodRounds = DirectLabel(parent=self.markedWood, relief=None, text="%s" % avatar.getMarkedWoodRounds(), text_fg=(1, 1, 1, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.6)
            self.markedWoodRounds.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.markedWood, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.inkDrain:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.inkDrain = status.find('**/ink_drain_icon')
            self.inkDrainRoundsText = DirectLabel(parent=self.inkDrain, relief=None, text="%s" % avatar.getInkDrainRounds(), text_fg=(1, 1, 1, 1),
                                                  text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                  pos=(0.25, 0, -.5),
                                                  text_scale=.6)
            self.inkDrainRoundsText.show()
            self.inkDrainText = DirectLabel(parent=self.inkDrain, relief=None, text="%s" % avatar.getInkDrain() + "%", text_fg=(1, 0, 0, 1),
                                            text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                            pos=(0.25, 0, 0.15),
                                            text_scale=.4)
            self.inkDrainText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.inkDrain, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.damageDown:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageDown = status.find('**/toon_damage_down_icon')
            self.damageDownRounds = DirectLabel(parent=self.damageDown, relief=None, text="%s" % avatar.getDamageDownRounds(), text_fg=(1, 1, 1, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.6)
            self.damageDownRounds.show()
            self.damageDownText = DirectLabel(parent=self.damageDown, relief=None, text="%s" % avatar.getDamageDown() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, 0.15),
                                              text_scale=.4)
            self.damageDownText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.damageDown, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.isBurned:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.burned = status.find('**/trialbyfire_icon')
            self.burnedRounds = DirectLabel(parent=self.burned, relief=None, text="%s" % avatar.getBurnedRounds(), text_fg=(1, 1, 1, 1),
                                            text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                            pos=(0.25, 0, -.5),
                                            text_scale=.6)
            self.burnedRounds.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.burned, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.liquidated:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.liquidated = status.find('**/heavyrain_icon')
            self.liquidatedText = DirectLabel(parent=self.liquidated, relief=None, text="%s" % avatar.getLiquidatedRounds(), text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.6)
            self.liquidatedText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.liquidated, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.damageOvertime:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageOvertime = status.find('**/damage_over_time_icon')
            self.damageOvertimeRounds = DirectLabel(parent=self.damageOvertime, relief=None, text="%s" % avatar.getDamageOvertimeRounds(), text_fg=(1, 1, 1, 1),
                                                    text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                    pos=(0.25, 0, -.5),
                                                    text_scale=.6)
            self.damageOvertimeRounds.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.damageOvertime, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.confused:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.confused = status.find('**/confusion_icon')
            self.confusedRounds = DirectLabel(parent=self.confused, relief=None, text="%s" % avatar.getConfusedRounds(), text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.6)
            self.confusedRounds.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.confused, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.cooldown:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.cooldown = status.find('**/unite_cooldown_icon')
            self.cooldownRounds = DirectLabel(parent=self.cooldown, relief=None, text="%s" % avatar.getCooldownRounds(), text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.6)
            self.cooldownRounds.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.cooldown, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.hidden:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.hidden = status.find('**/fog_icon')
            self.hiddenRounds = DirectLabel(parent=self.hidden, relief=None, text="%s" % avatar.getHiddenRounds(), text_fg=(1, 1, 1, 1),
                                            text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                            pos=(0.25, 0, -.5),
                                            text_scale=.6)
            self.hiddenRounds.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.hidden, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.noDodge:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.noDodge = status.find('**/hurry_sickness_icon')
            self.nodDodgeRoundsText = DirectLabel(parent=self.noDodge, relief=None, text="%s" % avatar.getNoDodgeRounds(), text_fg=(1, 1, 1, 1),
                                                  text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                  pos=(0.25, 0, -.5),
                                                  text_scale=.6)
            self.nodDodgeRoundsText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.noDodge, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.collectCalled:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.collectCall = status.find('**/bewitched_icon')
            self.collectCallRoundsText = DirectLabel(parent=self.collectCall, relief=None, text="%s" % avatar.getCollectCallRounds(), text_fg=(1, 1, 1, 1),
                                                     text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                     pos=(0.25, 0, -.5),
                                                     text_scale=.6)
            self.collectCallRoundsText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.collectCall, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.mandatoryToll:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.mandatoryToll = status.find('**/bewitched_icon')
            self.mandatoryTollNumberText = DirectLabel(parent=self.mandatoryToll, relief=None, text="-%s" % avatar.getMandatoryToll(), text_fg=(1, 0, 0, 1),
                                                       text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                       pos=(0.25, 0, -.5),
                                                       text_scale=.6)
            self.mandatoryTollNumberText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.mandatoryToll, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.groupDamageDown:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.groupDamageDown = status.find('**/fizzle_icon')
            self.groupDamageDownRoundsText = DirectLabel(parent=self.groupDamageDown, relief=None, text="%s" % avatar.getGroupDamageDownRounds(), text_fg=(1, 1, 1, 1),
                                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                         pos=(0.25, 0, -.5),
                                                         text_scale=.6)
            self.groupDamageDownRoundsText.show()
            self.groupDamageDownText = DirectLabel(parent=self.groupDamageDown, relief=None, text="-50%", text_fg=(1, 0, 0, 1),
                                                   text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                   pos=(0.25, 0, 0.15),
                                                   text_scale=.4)
            self.groupDamageDownText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.groupDamageDown, slot, slotColor=(0, 0.902, 1, 1))

        if avatar.winded:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.winded = status.find('**/encore_icon')
            self.windedRounds = DirectLabel(parent=self.winded, relief=None, text="%s" % avatar.getWindedRounds(), text_fg=(1, 1, 1, 1),
                                            text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                            pos=(0.25, 0, -.5),
                                            text_scale=.6)
            self.windedRounds.show()
            self.windedText = DirectLabel(parent=self.winded, relief=None, text="%s" % avatar.getWinded() + "%", text_fg=(1, 0, 0, 1),
                                          text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                          pos=(0.25, 0, 0.15),
                                          text_scale=.4)
            self.windedText.show()
            slot = self._claimNextToonStatusSlot()
            self._attachToonStatusIcon(self.winded, slot, slotColor=(0, 0.902, 1, 1))


    def setLaffMeter(self, avatar):
        self.notify.debug('setLaffMeter: new avatar %s' % avatar.doId)
        if self.avatar == avatar:
            self.setStatusEffects(avatar)
            messenger.send(self.avatar.uniqueName('hpChange'), [avatar.hp, avatar.maxHp, 1])
        else:
            self.setStatusEffects(avatar)
            if self.avatar:
                self.cleanupLaffMeter()
            self.avatar = avatar
            self.laffMeter = LaffMeter.LaffMeter(avatar.style, avatar.hp, avatar.maxHp)
            self.laffMeter.setAvatar(self.avatar)
            self.laffMeter.reparentTo(self)
            self.laffMeter.setPos(-0.15, 0.14, 0.05)
            self.laffMeter.setScale(0.11)
            self.laffMeter.start()

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

    def setValues(self, index, track, level = None, numTargets = None, targetIndex = None, localNum = None):
        self.notify.debug('Toon Panel setValues: index=%s track=%s level=%s numTargets=%s targetIndex=%s localNum=%s' % (index,
         track,
         level,
         numTargets,
         targetIndex,
         localNum))
        self.undecidedText.hide()
        self.sosText.hide()
        self.fireText.hide()
        self.sueText.hide()
        self.roundsText.hide()
        self.damageText.hide()
        self.exeDamageText.hide()
        self.soakedDamageText.hide()
        self.soakedRoundsText.hide()
        self.knockbackText.hide()
        self.selfHealText.hide()
        self.gagNode.hide()
        self.whichText.hide()
        self.passNode.hide()
        self.passText.hide()
        if self.hasGag:
            self.gag.removeNode()
            self.hasGag = 0
        if track == BattleBase.NO_ATTACK or track == BattleBase.UN_ATTACK:
            self.undecidedText.show()
            #self.undecidedText2.show()
        elif track == BattleBase.PASS_ATTACK:
            self.passText.show()
            self.passText['text'] = 'PASS'
        elif track == BattleBase.FIRE:
            self.fireText.show()
            self.whichText.show()
            self.whichText['text'] = self.determineWhichText(numTargets, targetIndex, localNum, index, track)
        elif track == BattleBase.SUE:
            self.sueText.show()
            self.whichText.show()
            self.whichText['text'] = self.determineWhichText(numTargets, targetIndex, localNum, index, track)
        elif track == BattleBase.SOS or track == BattleBase.NPCSOS or track == BattleBase.PETSOS:
            self.sosText.show()
        elif track >= MIN_TRACK_INDEX and track <= MAX_TRACK_INDEX:
            self.undecidedText.hide()
            self.passText.hide()
            self.gagNode.show()
            invButton = base.localAvatar.inventory.buttonLookup(track, level)
            self.gag = invButton.instanceUnderNode(self.gagNode, 'gag')
            self.gag.setScale(0.8)
            self.gag.setPos(0.105, -0.2, 0.035)
            if self.avatar.trackBonusLevel[track] >= 1:
                self.gag.setColor(0.6, 0.6, 1.0, 1)
            else:
                self.gag.setColor(1, 1, 1, 1)
            self.hasGag = 1
            allGagBoost = False
            if 'allGagBoost' in self.avatar.battleConditions:
                allGagBoost = True
            raisedAnte = False
            if 'raisedAnte' in self.avatar.battleConditions:
                raisedAnte = True
            damage = int(math.ceil(getAvPropDamage(track, level, self.avatar.experience.getExp(track))))
            lureValue = int(
                ((ToontownBattleGlobals.AvLureKnockback[level] * 100) / 2))
            if self.avatar.toonupGagBoost and track == HEAL_TRACK:
                damage *= (1.0 + self.avatar.getToonupGagBoost() * 0.01)
                lureValue *= (1.0 + self.avatar.getToonupGagBoost() * 0.01)
            if self.avatar.trapGagBoost and track == TRAP_TRACK:
                damage *= (1.0 + self.avatar.getTrapGagBoost() * 0.01)
                lureValue *= (1.0 + self.avatar.getTrapGagBoost() * 0.01)
            if self.avatar.lureGagBoost and track == LURE_TRACK:
                damage *= (1.0 + self.avatar.getLureGagBoost() * 0.01)
                lureValue *= (1.0 + self.avatar.getLureGagBoost() * 0.01)
            if self.avatar.throwGagBoost and track == THROW_TRACK:
                damage *= (1.0 + self.avatar.getThrowGagBoost() * 0.01)
                lureValue *= (1.0 + self.avatar.getThrowGagBoost() * 0.01)
            if self.avatar.squirtGagBoost and track == SQUIRT_TRACK:
                damage *= (1.0 + self.avatar.getSquirtGagBoost() * 0.01)
                lureValue *= (1.0 + self.avatar.getSquirtGagBoost() * 0.01)
            if self.avatar.zapGagBoost and track == ZAP_TRACK:
                damage *= (1.0 + self.avatar.getZapGagBoost() * 0.01)
                lureValue *= (1.0 + self.avatar.getZapGagBoost() * 0.01)
            if self.avatar.soundGagBoost and track == SOUND_TRACK:
                damage *= (1.0 + self.avatar.getSoundGagBoost() * 0.01)
                lureValue *= (1.0 + self.avatar.getSoundGagBoost() * 0.01)
            if self.avatar.dropGagBoost and track == DROP_TRACK:
                damage *= (1.0 + self.avatar.getDropGagBoost() * 0.01)
                lureValue *= (1.0 + self.avatar.getDropGagBoost() * 0.01)
            if self.avatar.gagBoost:
                damage *= (1.0 + self.avatar.getGagBoost() * 0.01)
                lureValue *= (1.0 + self.avatar.getGagBoost() * 0.01)
            if self.avatar.damageUp:
                damage *= (1.0 + self.avatar.getDamageUp() * 0.01)
                lureValue *= (1.0 + self.avatar.getDamageUp() * 0.01)
            if self.avatar.encore:
                damage *= (1.0 + self.avatar.getEncore() * 0.01)
                lureValue *= (1.0 + self.avatar.getEncore() * 0.01)
            if self.avatar.governaughtDamageUp:
                damage *= (1.0 + self.avatar.getDamageUpGovernaught() * 0.01)
                lureValue *= (1.0 + self.avatar.getDamageUpGovernaught() * 0.01)
            if self.avatar.raisedAnte:
                damage *= (1.0 + self.avatar.getRaisedAnte() * 0.01)
                lureValue *= 1
            if self.avatar.winded and track == SOUND_TRACK:
                damage *= (1.0 + self.avatar.getWinded() * 0.01)
                lureValue *= (1.0 + self.avatar.getWinded() * 0.01)
            if self.avatar.damageDown:
                damage *= (1.0 + self.avatar.getDamageDown() * 0.01)
                lureValue *= (1.0 + self.avatar.getDamageDown() * 0.01)
            if self.avatar.inkDrain:
                damage *= (1.0 + self.avatar.getInkDrain() * 0.01)
                lureValue *= (1.0 + self.avatar.getInkDrain() * 0.01)
            if self.avatar.groupDamageDown and ((track == LURE_TRACK and level == 1) or (track == LURE_TRACK and level == 3) or (track == LURE_TRACK and level == 5) or (track == LURE_TRACK and level == 7) or (track == SOUND_TRACK)\
                    or (track == ZAP_TRACK) or (track == HEAL_TRACK and level == 1) or (track == HEAL_TRACK and level == 3) or (track == HEAL_TRACK and level == 5) or (track == HEAL_TRACK and level == 7) or (track == SQUIRT_TRACK)):
                damage *= (1.0 + -50 * 0.01)
                lureValue *= (1.0 + -50 * 0.01)
            if numTargets is not None and targetIndex is not None and localNum is not None:
                self.whichText.show()
                self.whichText['text'] = self.determineWhichText(numTargets, targetIndex, localNum, index, track)
            if track == LURE_TRACK:
                self.roundsText.show()
                if self.avatar.trackBonusLevel[track] >= 1:
                    self.roundsText['text'] = str(NumRoundsLured[level] + 1) + '/' + str(int(math.ceil(lureValue * 1.2))) + '%'
                else:
                    self.roundsText['text'] = str(NumRoundsLured[level] + 1) + '/' + str(int(math.ceil(lureValue))) + '%'
                # self.knockbackText.show()
                # self.knockbackText['text'] = 'Knockback: ' + str(lureValue)+'%'
            if track == HEAL_TRACK:
                self.roundsText.show()
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
                if self.avatar.trackBonusLevel[track] >= 1:
                    self.damageText['text'] = '-' + str(int(math.ceil(damage * 1.15))) + '/' + str(
                        int(math.ceil(math.ceil(damage * 1.15) * 1.3)))
                else:
                    self.damageText['text'] = '-' + str(int(math.ceil(damage))) + '/' + str(int(math.ceil(damage * 1.3)))
                # self.exeDamageText.show()
                # self.exeDamageText['text'] = 'Exe./Gov.: ' + str(damage * 1.3)
            if track == SOUND_TRACK:
                self.damageText.show()
                self.damageText['text'] = '-' + str(int(math.ceil(damage)))
            if track == THROW_TRACK:
                self.damageText.show()
                self.damageText['text'] = '-' + str(int(math.ceil(damage)))
                # self.selfHealText.show()
                # self.selfHealText['text'] = 'Self Heal: ' + str(damage/5)
            if track == DROP_TRACK:
                self.damageText.show()
                self.damageText['text'] = '-' + str(int(math.ceil(damage)))
            if track == SQUIRT_TRACK:
                self.damageText.show()
                if self.avatar.trackBonusLevel[track] >= 1:
                    self.damageText['text'] = '-' + str(int(math.ceil(damage * .75))) + '/ -' + str(int(math.ceil(damage))) + '/ -' + str(
                        int(math.ceil(damage * .75)))
                else:
                    self.damageText['text'] = '-' + str(int(damage / 3)) + '/ -' + str(int(damage)) + '/ -' + str(
                        int(math.ceil(damage / 3)))
                # self.soakedRoundsText.show()
                # self.soakedRoundsText['text'] = 'Rounds: ' + str(ToontownBattleGlobals.AvSoakRounds[level])
            if track == ZAP_TRACK:
                self.damageText.show()
                self.damageText['text'] = '-' + str(int(math.ceil(damage)))
                # self.soakedDamageText.show()
                # self.soakedDamageText['text'] = 'If Soaked: ' + str(damage * 3)
        else:
            self.notify.error('Bad track value: %s' % track)

    def determineWhichText(self, numTargets, targetIndex, localNum, index, track):
        returnStr = ''
        targetList = range(numTargets)
        targetList.reverse()
        try:
            if self.avatar.confused:
                marker = '-'
            elif self.avatar.trackBonusLevel[track] >= 1:
                marker = 'O'
            else:
                marker = 'X'
        except:
            marker = 'X'
        for i in targetList:
            if targetIndex == -1:
                returnStr += marker
            elif targetIndex == -2:
                if i == index:
                    returnStr += '-'
                else:
                    returnStr += marker
            elif targetIndex >= 0 and targetIndex <= 5:
                if i == targetIndex:
                    returnStr += marker
                else:
                    returnStr += '-'
            else:
                self.notify.error('Bad target index: %s' % targetIndex)

        return returnStr

    def cleanup(self):
        self.ignoreAll()
        self.cleanupLaffMeter()
        if self.hasGag:
            self.gag.removeNode()
            del self.gag
        self.gagNode.removeNode()
        del self.gagNode
        DirectFrame.destroy(self)

    def cleanupLaffMeter(self):
        self.notify.debug('Cleaning up laffmeter!')
        self.ignore(self.hpChangeEvent)
        if self.laffMeter:
            self.laffMeter.destroy()
            self.laffMeter = None