from panda3d.core import *
from panda3d.direct import *
from toontown.battle.BattleGlobals import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownBattleGlobals import *
from direct.directnotify import DirectNotifyGlobal
import string
from toontown.toon import LaffMeter
from toontown.battle import BattleBase
from toontown.toonbase import ToontownBattleGlobals
from direct.gui.DirectGui import *
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
        self.status2 = None
        self.status3 = None
        self.status4 = None
        self.attackIcon = None
        self.attackIcon1 = None
        self.attackIcon2 = None
        self.attackIcon3 = None
        self.avatar = None
        self.snapped = None
        self.snappedText = None
        self.snappedRoundsText = None
        self.vulnerable = None
        self.vulnerableText = None
        self.vulnerableRoundsText = None
        self.encore = None
        self.winded = None
        self.encoreRounds = None
        self.windedRounds = None
        self.damageDown = None
        self.damageDownRounds = None
        self.damageUp = None
        self.damageUpRounds = None
        self.confused = None
        self.confusedRounds = None
        self.hidden = None
        self.hiddenRounds = None
        self.markedWood = None
        self.markedWoodRounds = None
        self.damageOvertime = None
        self.damageOvertimeRounds = None
        self.cooldown = None
        self.cooldownRounds = None
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

    def setLaffMeter(self, avatar):
        self.statusEffects = 0
        if self.status != None:
            self.status.removeNode()
        if self.status2 != None:
            self.status2.removeNode()
        if self.status3 != None:
            self.status3.removeNode()
        if self.status4 != None:
            self.status4.removeNode()
        if self.encore != None:
            self.encore.removeNode()
        if self.encoreRounds != None:
            self.encoreRounds.removeNode()
        if self.winded != None:
            self.winded.removeNode()
        if self.windedRounds != None:
            self.windedRounds.removeNode()
        if self.damageUpRounds != None:
            self.damageUpRounds.removeNode()
        if self.damageUp != None:
            self.damageUp.removeNode()
        if self.damageDownRounds != None:
            self.damageDownRounds.removeNode()
        if self.damageDown != None:
            self.damageDown.removeNode()
        if self.damageOvertime != None:
            self.damageOvertime.removeNode()
        if self.damageOvertimeRounds != None:
            self.damageOvertimeRounds.removeNode()
        if self.cooldown != None:
            self.cooldown.removeNode()
        if self.cooldownRounds != None:
            self.cooldownRounds.removeNode()
        if self.confused != None:
            self.confused.removeNode()
        if self.confusedRounds != None:
            self.confusedRounds.removeNode()
        if self.hidden != None:
            self.hidden.removeNode()
        if self.hiddenRounds != None:
            self.hiddenRounds.removeNode()
        if self.markedWood != None:
            self.markedWood.removeNode()
        if self.markedWoodRounds != None:
            self.markedWoodRounds.removeNode()
        if self.snapped != None:
            self.snapped.removeNode()
        if self.snappedText != None:
            self.snappedText.removeNode()
        if self.snappedRoundsText != None:
            self.snappedRoundsText.removeNode()
        if self.vulnerable != None:
            self.vulnerable.removeNode()
        if self.vulnerableText != None:
            self.vulnerableRoundsText.removeNode()
        if self.attackIcon != None:
            self.attackIcon.removeNode()
        if self.attackIcon1 != None:
            self.attackIcon1.removeNode()
        if self.attackIcon2 != None:
            self.attackIcon2.removeNode()
        if self.attackIcon3 != None:
            self.attackIcon3.removeNode()
        self.status = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status3 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status4 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.attackIcon3 = self.status4.find('**/default_background')  # fourth
        self.attackIcon3.reparentTo(self)
        self.attackIcon3.setPosHprScale(-0.1675, 0, -0.1925, 0, 0, 0, .125, .125, .125)
        self.attackIcon3.setColor(0.525, 0.133, 0.122, 1)
        self.attackIcon2 = self.status3.find('**/default_background')  # third
        self.attackIcon2.reparentTo(self)
        self.attackIcon2.setPosHprScale(-0.29, 0, -0.15, 0, 0, 0, .125, .125, .125)
        self.attackIcon2.setColor(0.525, 0.133, 0.122, 1)
        self.attackIcon1 = self.status2.find('**/default_background')  # second
        self.attackIcon1.reparentTo(self)
        self.attackIcon1.setPosHprScale(-0.3675, 0, -0.05, 0, 0, 0, .125, .125, .125)
        self.attackIcon1.setColor(0.525, 0.133, 0.122, 1)
        self.attackIcon = self.status.find('**/default_background')  # first
        self.attackIcon.reparentTo(self)
        self.attackIcon.setPosHprScale(-0.39, 0, 0.075, 0, 0, 0, .125, .125, .125)
        self.attackIcon.setColor(0.525, 0.133, 0.122, 1)
        if avatar.isSnapped:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.snapped = status.find('**/vulnerable_icon')
            self.snappedRoundsText = DirectLabel(parent=self.snapped, relief=None, text="%s" % avatar.getSnappedRounds(), text_fg=(1, 1, 1, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.6)
            self.snappedRoundsText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.snapped.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.snapped.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.snapped.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.snapped.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.snapped.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.snapped.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.snapped.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.snapped.setColor(1, 1, 1, 1)
        if avatar.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable = status.find('**/broken_shield_icon')
            self.vulnerableRoundsText = DirectLabel(parent=self.vulnerable, relief=None, text="%s" % avatar.getVulnerabilityRounds(), text_fg=(1, 1, 1, 1),
                                                    text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                    pos=(0.25, 0, -.5),
                                                    text_scale=.6)
            self.vulnerableRoundsText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.vulnerable.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.vulnerable.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.vulnerable.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.vulnerable.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.vulnerable.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.vulnerable.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.vulnerable.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.vulnerable.setColor(1, 1, 1, 1)
        if avatar.markedWood:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.markedWood = status.find('**/marked_wood_icon')
            self.markedWoodRounds = DirectLabel(parent=self.markedWood, relief=None, text="%s" % avatar.getMarkedWoodRounds(), text_fg=(1, 1, 1, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.6)
            self.markedWoodRounds.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.markedWood.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.markedWood.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.markedWood.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.markedWood.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.markedWood.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.markedWood.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.markedWood.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.markedWood.setColor(1, 1, 1, 1)
        if avatar.damageDown:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageDown = status.find('**/toon_damage_down_icon')
            self.damageDownRounds = DirectLabel(parent=self.damageDown, relief=None, text="%s" % avatar.getDamageDownRounds(), text_fg=(1, 1, 1, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.6)
            self.damageDownRounds.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.damageDown.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.damageDown.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.damageDown.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.damageDown.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.damageDown.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.damageDown.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.damageDown.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.damageDown.setColor(1, 1, 1, 1)
        if avatar.damageOvertime:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageOvertime = status.find('**/damage_over_time_icon')
            self.damageOvertimeRounds = DirectLabel(parent=self.damageOvertime, relief=None, text="%s" % avatar.getDamageOvertimeRounds(), text_fg=(1, 1, 1, 1),
                                                    text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                    pos=(0.25, 0, -.5),
                                                    text_scale=.6)
            self.damageOvertimeRounds.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.damageOvertime.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.damageOvertime.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.damageOvertime.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.damageOvertime.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.damageOvertime.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 11)
                self.damageOvertime.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.damageOvertime.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.damageOvertime.setColor(1, 1, 1, 1)
        if avatar.confused:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.confused = status.find('**/confusion_icon')
            self.confusedRounds = DirectLabel(parent=self.confused, relief=None, text="%s" % avatar.getConfusedRounds(), text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.6)
            self.confusedRounds.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.confused.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.confused.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.confused.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.confused.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.confused.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.confused.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.confused.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.confused.setColor(1, 1, 1, 1)
        if avatar.cooldown:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.cooldown = status.find('**/unite_cooldown_icon')
            self.cooldownRounds = DirectLabel(parent=self.cooldown, relief=None, text="%s" % avatar.getCooldownRounds(), text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.6)
            self.cooldownRounds.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.cooldown.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.cooldown.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.cooldown.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.cooldown.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.cooldown.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.cooldown.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.cooldown.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.cooldown.setColor(1, 1, 1, 1)
        if avatar.hidden:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.hidden = status.find('**/fog_icon')
            self.hiddenRounds = DirectLabel(parent=self.hidden, relief=None, text="%s" % avatar.getHiddenRounds(), text_fg=(1, 1, 1, 1),
                                            text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                            pos=(0.25, 0, -.5),
                                            text_scale=.6)
            self.hiddenRounds.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.hidden.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.hidden.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.hidden.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.hidden.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.hidden.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.hidden.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.hidden.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.hidden.setColor(1, 1, 1, 1)
        if avatar.winded:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.winded = status.find('**/encore_icon')
            self.windedRounds = DirectLabel(parent=self.winded, relief=None, text="%s" % avatar.getWindedRounds(), text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.6)
            self.windedRounds.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.winded.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.winded.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.winded.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.winded.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.winded.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.winded.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.winded.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.winded.setColor(1, 1, 1, 1)
        if avatar.encore:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.encore = status.find('**/encore_icon')
            self.encoreRounds = DirectLabel(parent=self.encore, relief=None, text="%s" % avatar.getEncoreRounds(), text_fg=(1, 1, 1, 1),
                                            text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                            pos=(0.25, 0, -.5),
                                            text_scale=.6)
            self.encoreRounds.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.encore.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.encore.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.encore.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.encore.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.encore.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.encore.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.encore.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.encore.setColor(1, 1, 1, 1)
        if avatar.damageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp = status.find('**/toon_damage_up_icon')
            self.damageUpRounds = DirectLabel(parent=self.damageUp, relief=None, text="%s" % avatar.getDamageUpRounds(), text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.6)
            self.damageUpRounds.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.damageUp.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.damageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.damageUp.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.damageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.damageUp.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.damageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.damageUp.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.damageUp.setColor(1, 1, 1, 1)
        self.notify.debug('setLaffMeter: new avatar %s' % avatar.doId)
        if self.avatar == avatar:
            messenger.send(self.avatar.uniqueName('hpChange'), [avatar.hp, avatar.maxHp, 1])
        else:
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
            if track == HEAL_TRACK and 'healBoost' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['healBoost'][0] * 0.01) + 1.0)))
            elif track == HEAL_TRACK and 'encore' in base.localAvatar.battleConditions:
                damage = int(math.ceil(damage * ((base.localAvatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            elif track == TRAP_TRACK and 'trapBoost' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['trapBoost'][0] * 0.01) + 1.0)))
            elif track == LURE_TRACK and 'lureBoost' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['lureBoost'][0] * 0.01) + 1.0)))
                lureValue = math.ceil(
                    ((ToontownBattleGlobals.AvLureKnockback[level] * 100) +
                     self.avatar.battleConditions['lureBoost'][
                         0]) / 2)
            elif track == SOUND_TRACK and 'soundBoost' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['soundBoost'][0] * 0.01) + 1.0)))
            elif track == THROW_TRACK and 'throwBoost' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['throwBoost'][0] * 0.01) + 1.0)))
            elif track == SQUIRT_TRACK and 'squirtBoost' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['squirtBoost'][0] * 0.01) + 1.0)))
            elif track == ZAP_TRACK and 'zapBoost' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['zapBoost'][0] * 0.01) + 1.0)))
            elif track == DROP_TRACK and 'dropBoost' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['dropBoost'][0] * 0.01) + 1.0)))
            elif track == SOUND_TRACK and 'encore' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            elif track == TRAP_TRACK and 'encore' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            elif track == THROW_TRACK and 'encore' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            elif track == SQUIRT_TRACK and 'encore' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            elif track == ZAP_TRACK and 'encore' in  self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            elif track == DROP_TRACK and 'encore' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore'][0] * 0.01) + 1.0)))
            elif track == LURE_TRACK and 'encore' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore'][0] * 0.01) + 1.0)))
                lureValue = int(math.ceil(
                    ((ToontownBattleGlobals.AvLureKnockback[level] * 100) + self.avatar.battleConditions['encore'][
                        0]) / 2))
            elif track == SOUND_TRACK and 'encore2' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
            elif track == TRAP_TRACK and 'encore2' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
            elif track == THROW_TRACK and 'encore2' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
            elif track == SQUIRT_TRACK and 'encore2' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
            elif track == ZAP_TRACK and 'encore2' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
            elif track == DROP_TRACK and 'encore2' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
            elif track == LURE_TRACK and 'encore2' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['encore2'][0] * 0.01) + 1.0)))
                lureValue = int(math.ceil(
                    ((ToontownBattleGlobals.AvLureKnockback[level] * 100) +
                     base.localAvatar.battleConditions['encore2'][
                         0]) / 2))
            elif track == SOUND_TRACK and 'winded' in self.avatar.battleConditions:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['winded'][0] * 0.01) + 1.0)))
            elif allGagBoost and not track == LURE_TRACK:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['allGagBoost'][0] * 0.01) + 1.0)))
                lureValue = int(math.ceil(
                    ((ToontownBattleGlobals.AvLureKnockback[level] * 100) / 2)))
            elif raisedAnte and not track == LURE_TRACK:
                damage = int(math.ceil(damage * ((self.avatar.battleConditions['raisedAnte'][0] * 0.01) + 1.0)))
                lureValue = int(math.ceil(
                    ((ToontownBattleGlobals.AvLureKnockback[level] * 100) / 2)))
            else:
                lureValue = int(math.ceil(
                    ((ToontownBattleGlobals.AvLureKnockback[level] * 100) / 2)))
            if numTargets is not None and targetIndex is not None and localNum is not None:
                self.whichText.show()
                self.whichText['text'] = self.determineWhichText(numTargets, targetIndex, localNum, index, track)
            if track == LURE_TRACK:
                self.roundsText.show()
                if self.avatar.trackBonusLevel[track] >= 1:
                    self.roundsText['text'] = str(NumRoundsLured[level] + 1) + '/' + str(int(lureValue * 1.2)) + '%'
                else:
                    self.roundsText['text'] = str(NumRoundsLured[level] + 1) + '/' + str(lureValue) + '%'
                # self.knockbackText.show()
                # self.knockbackText['text'] = 'Knockback: ' + str(lureValue)+'%'
            if track == HEAL_TRACK:
                self.roundsText.show()
                if self.avatar.trackBonusLevel[track] >= 1:
                    self.roundsText['text'] = '+' + str(damage) + '/' + str(int(damage / 2.22))
                else:
                    self.roundsText['text'] = '+' + str(damage) + '/' + str(int(damage / 4))
                self.roundsText.setColor(0.176, 1, 0, 1)
                # self.selfHealText.show()
                # self.selfHealText['text'] = 'Self Heal: ' + str(damage / 2.5)
                # self.selfHealText.setColor(0.176, 1, 0, 1)
            if track == TRAP_TRACK:
                self.damageText.show()
                if self.avatar.trackBonusLevel[track] >= 1:
                    self.damageText['text'] = '-' + str(int(damage * 1.15) + 1) + '/' + str(
                        int(((damage * 1.15) * 1.3) + 1))
                else:
                    self.damageText['text'] = '-' + str(damage) + '/' + str(int(damage * 1.3))
                # self.exeDamageText.show()
                # self.exeDamageText['text'] = 'Exe./Gov.: ' + str(damage * 1.3)
            if track == SOUND_TRACK:
                self.damageText.show()
                self.damageText['text'] = '-' + str(damage)
            if track == THROW_TRACK:
                self.damageText.show()
                self.damageText['text'] = '-' + str(damage)
                # self.selfHealText.show()
                # self.selfHealText['text'] = 'Self Heal: ' + str(damage/5)
            if track == DROP_TRACK:
                self.damageText.show()
                self.damageText['text'] = '-' + str(damage)
            if track == SQUIRT_TRACK:
                self.damageText.show()
                if self.avatar.trackBonusLevel[track] >= 1:
                    self.damageText['text'] = '-' + str(int(damage * .75)) + '/ -' + str(damage) + '/ -' + str(
                        int(damage * .75))
                else:
                    self.damageText['text'] = '-' + str(int(damage / 3)) + '/ -' + str(damage) + '/ -' + str(
                        int(damage / 3))
                # self.soakedRoundsText.show()
                # self.soakedRoundsText['text'] = 'Rounds: ' + str(ToontownBattleGlobals.AvSoakRounds[level])
            if track == ZAP_TRACK:
                self.damageText.show()
                self.damageText['text'] = '-' + str(damage)
                # self.soakedDamageText.show()
                # self.soakedDamageText['text'] = 'If Soaked: ' + str(damage * 3)
        else:
            self.notify.error('Bad track value: %s' % track)

    def determineWhichText(self, numTargets, targetIndex, localNum, index, track):
        returnStr = ''
        targetList = range(numTargets)
        targetList.reverse()
        try:
            if 'confused' in self.avatar.battleConditions:
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