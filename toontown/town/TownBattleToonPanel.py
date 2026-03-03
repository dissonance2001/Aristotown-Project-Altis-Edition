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
        self.liquidated = None
        self.liquidatedText = None
        self.governaughtDamageUp = None
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

    def setStatusEffects(self, avatar):
        self.avatar = avatar
        self.statusEffects = 0
        if self.gagBoost != None:
            self.gagBoost.removeNode()
        if self.gagBoostRoundsText != None:
            self.gagBoostRoundsText.removeNode()
        if self.gagBoostText != None:
            self.gagBoostText.removeNode()
        if self.collectCall != None:
            self.collectCall.removeNode()
        if self.collectCallRoundsText != None:
            self.collectCallRoundsText.removeNode()
        if self.noDodge != None:
            self.noDodge.removeNode()
        if self.nodDodgeRoundsText != None:
            self.nodDodgeRoundsText.removeNode()
        if self.mandatoryToll != None:
            self.mandatoryToll.removeNode()
        if self.mandatoryTollNumberText != None:
            self.mandatoryTollNumberText.removeNode()
        if self.attackIcon != None:
            self.attackIcon.removeNode()
        if self.attackIcon1 != None:
            self.attackIcon1.removeNode()
        if self.attackIcon2 != None:
            self.attackIcon2.removeNode()
        if self.attackIcon3 != None:
            self.attackIcon3.removeNode()
        if self.attackIcon4 != None:
            self.attackIcon4.removeNode()
        if self.attackIcon5 != None:
            self.attackIcon5.removeNode()
        if self.attackIcon6 != None:
            self.attackIcon6.removeNode()
        if self.attackIcon7 != None:
            self.attackIcon7.removeNode()
        if self.status != None:
            self.status.removeNode()
        if self.status2 != None:
            self.status2.removeNode()
        if self.status3 != None:
            self.status3.removeNode()
        if self.status4 != None:
            self.status4.removeNode()
        if self.status5 != None:
            self.status5.removeNode()
        if self.status6 != None:
            self.status6.removeNode()
        if self.status7 != None:
            self.status7.removeNode()
        if self.status8 != None:
            self.status8.removeNode()
        if self.encore != None:
            self.encore.removeNode()
        if self.govDamageText != None:
            self.govDamageText.removeNode()
        if self.governaughtDamageUp != None:
            self.governaughtDamageUp.removeNode()
        if self.encoreRounds != None:
            self.encoreRounds.removeNode()
        if self.winded != None:
            self.winded.removeNode()
        if self.gagBan != None:
            self.gagBan.removeNode()
        if self.windedRounds != None:
            self.windedRounds.removeNode()
        if self.damageUpRounds != None:
            self.damageUpRounds.removeNode()
        if self.damageUp != None:
            self.damageUp.removeNode()
        if self.cheerRounds != None:
            self.cheerRounds.removeNode()
        if self.cheer != None:
            self.cheer.removeNode()
        if self.burnedRounds != None:
            self.burnedRounds.removeNode()
        if self.burned != None:
            self.burned.removeNode()
        if self.liquidatedText != None:
            self.liquidatedText.removeNode()
        if self.liquidated != None:
            self.liquidated.removeNode()
        if self.damageDownRounds != None:
            self.damageDownRounds.removeNode()
        if self.damageDown != None:
            self.damageDown.removeNode()
        if self.groupDamageDown != None:
            self.groupDamageDown.removeNode()
        if self.groupDamageDownText != None:
            self.groupDamageDownText.removeNode()
        if self.groupDamageDownRoundsText != None:
            self.groupDamageDownRoundsText.removeNode()
        if self.bombed != None:
            self.bombed.removeNode()
        if self.bombedText != None:
            self.bombedText.removeNode()
        if self.bombedRoundsText != None:
            self.bombedRoundsText.removeNode()
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
        if self.markedWoodText != None:
            self.markedWoodText.removeNode()
        if self.inkDrain != None:
            self.inkDrain.removeNode()
        if self.inkDrainRoundsText != None:
            self.inkDrainRoundsText.removeNode()
        if self.inkDrainText != None:
            self.inkDrainText.removeNode()
        if self.snapped != None:
            self.snapped.removeNode()
        if self.snappedText != None:
            self.snappedText.removeNode()
        if self.snappedRoundsText != None:
            self.snappedRoundsText.removeNode()
        if self.vulnerable != None:
            self.vulnerable.removeNode()
        if self.vulnerableText != None:
            self.vulnerableText.removeNode()
        if self.vulnerableRoundsText != None:
            self.vulnerableRoundsText.removeNode()
        if self.damageDownText != None:
            self.damageDownText.removeNode()
        if self.encoreText != None:
            self.encoreText.removeNode()
        if self.windedText != None:
            self.windedText.removeNode()
        if self.damageUpText != None:
            self.damageUpText.removeNode()
        self.status = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status3 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status4 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status5 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status6 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status7 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status8 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.attackIcon7 = self.status8.find('**/default_background')
        self.attackIcon7.reparentTo(self)  # 8
        self.attackIcon7.setPosHprScale(0.36, 0.4, -0.355, 0, 0, 0, .125, .125, .125)
        self.attackIcon7.setColor(0.525, 0.133, 0.122, 1)
        self.attackIcon7.hide()
        self.attackIcon6 = self.status7.find('**/default_background')  # 7
        self.attackIcon6.reparentTo(self)
        self.attackIcon6.setPosHprScale(0.24, 0.4, -0.355, 0, 0, 0, .125, .125, .125)
        self.attackIcon6.setColor(0.525, 0.133, 0.122, 1)
        self.attackIcon6.hide()
        self.attackIcon5 = self.status6.find('**/default_background')  # 6
        self.attackIcon5.reparentTo(self)
        self.attackIcon5.setPosHprScale(0.12, 0, -0.355, 0, 0, 0, .125, .125, .125)
        self.attackIcon5.setColor(0.525, 0.133, 0.122, 1)
        self.attackIcon5.hide()
        self.attackIcon4 = self.status5.find('**/default_background')  # 5
        self.attackIcon4.reparentTo(self)
        self.attackIcon4.setPosHprScale(0, 0, -0.355, 0, 0, 0, .125, .125, .125)
        self.attackIcon4.setColor(0.525, 0.133, 0.122, 1)
        self.attackIcon4.hide()
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
        if avatar.cheer:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.cheer = status.find('**/cheer_icon')
            self.encoreRounds = DirectLabel(parent=self.cheer, relief=None, text="%s" % avatar.getCheerRounds(), text_fg=(1, 1, 1, 1),
                                            text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                            pos=(0.25, 0, -.5),
                                            text_scale=.6)
            self.encoreRounds.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.cheer.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.cheer.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.cheer.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.cheer.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.cheer.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.cheer.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.cheer.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.cheer.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.cheer.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.cheer.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.cheer.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.cheer.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.cheer.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.cheer.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.cheer.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.cheer.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.gagBoost.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.gagBoost.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.gagBoost.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.gagBoost.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.gagBoost.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.gagBoost.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.gagBoost.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.gagBoost.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.gagBoost.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.gagBoost.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.gagBoost.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.gagBoost.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.gagBoost.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.gagBoost.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.gagBoost.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.gagBoost.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            if self.statusEffects == 5:
                self.encore.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.encore.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.encore.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.encore.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.encore.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.encore.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.encore.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.encore.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if avatar.governaughtDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.governaughtDamageUp = status.find('**/toon_damage_up_icon')
            self.govDamageText = DirectLabel(parent=self.governaughtDamageUp, relief=None, text="%s" % avatar.getDamageUpGovernaught() + "%", text_fg=(0, 1, 0.004, 1),
                                             text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                             pos=(0.25, 0, 0.15),
                                             text_scale=.4)
            self.govDamageText.show()
            self.governaughtDamageUp.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.governaughtDamageUp.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.governaughtDamageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.governaughtDamageUp.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.governaughtDamageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.governaughtDamageUp.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.governaughtDamageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.governaughtDamageUp.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.governaughtDamageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.governaughtDamageUp.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.governaughtDamageUp.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.governaughtDamageUp.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.governaughtDamageUp.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.governaughtDamageUp.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.governaughtDamageUp.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.governaughtDamageUp.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.governaughtDamageUp.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            if self.statusEffects == 5:
                self.damageUp.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.damageUp.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.damageUp.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.damageUp.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.damageUp.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.damageUp.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.damageUp.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.damageUp.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if avatar.isGagBan:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.gagBan = status.find('**/backfire_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.gagBan.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.gagBan.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.gagBan.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.gagBan.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.gagBan.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.gagBan.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.gagBan.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.gagBan.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.gagBan.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.gagBan.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.gagBan.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.gagBan.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.gagBan.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.gagBan.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.gagBan.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.gagBan.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            if self.statusEffects == 5:
                self.snapped.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.snapped.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.snapped.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.snapped.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.snapped.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.snapped.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.snapped.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.snapped.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if avatar.isBombed:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.bombed = status.find('**/trap_card_icon')
            self.bombedRoundsText = DirectLabel(parent=self.bombed, relief=None, text="%s" % avatar.getBombedRounds(), text_fg=(1, 1, 1, 1),
                                                    text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                    pos=(0.25, 0, -.5),
                                                    text_scale=.6)
            self.bombedRoundsText.show()
            self.bombedText = DirectLabel(parent=self.bombed, relief=None, text="%s" % avatar.getBombed() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, 0.15),
                                              text_scale=.4)
            self.bombedText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.bombed.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.bombed.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.bombed.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.bombed.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.bombed.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.bombed.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.bombed.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.bombed.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.bombed.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.bombed.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.bombed.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.bombed.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.bombed.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.bombed.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.bombed.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.bombed.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            if self.statusEffects == 5:
                self.vulnerable.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.vulnerable.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.vulnerable.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.vulnerable.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.vulnerable.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.vulnerable.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.vulnerable.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.vulnerable.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if avatar.markedWood:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.markedWood = status.find('**/marked_wood_icon')
            self.markedWoodRounds = DirectLabel(parent=self.markedWood, relief=None, text="%s" % avatar.getMarkedWoodRounds(), text_fg=(1, 1, 1, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.6)
            self.markedWoodRounds.show()
            self.markedWoodText = DirectLabel(parent=self.markedWood, relief=None, text="%s" % avatar.getMarkedWood() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, 0.15),
                                              text_scale=.4)
            self.markedWoodText.show()
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
            if self.statusEffects == 5:
                self.markedWood.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.markedWood.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.markedWood.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.markedWood.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.markedWood.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.markedWood.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.markedWood.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.markedWood.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.inkDrain.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.inkDrain.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.inkDrain.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.inkDrain.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.inkDrain.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.inkDrain.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.inkDrain.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.inkDrain.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.inkDrain.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.inkDrain.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.inkDrain.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.inkDrain.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.inkDrain.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.inkDrain.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.inkDrain.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.inkDrain.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            if self.statusEffects == 5:
                self.damageDown.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.damageDown.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.damageDown.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.damageDown.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.damageDown.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.damageDown.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.damageDown.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.damageDown.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if avatar.isBurned:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.burned = status.find('**/trialbyfire_icon')
            self.burnedRounds = DirectLabel(parent=self.burned, relief=None, text="%s" % avatar.getBurnedRounds(), text_fg=(1, 1, 1, 1),
                                            text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                            pos=(0.25, 0, -.5),
                                            text_scale=.6)
            self.burnedRounds.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.burned.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.burned.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.burned.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.burned.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.burned.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 11)
                self.burned.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.burned.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.burned.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.burned.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.burned.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.burned.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.burned.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.burned.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.burned.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.burned.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.burned.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if avatar.liquidated:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.liquidated = status.find('**/heavyrain_icon')
            self.liquidatedText = DirectLabel(parent=self.liquidated, relief=None, text="%s" % avatar.getLiquidatedRounds(), text_fg=(1, 1, 1, 1),
                                            text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                            pos=(0.25, 0, -.5),
                                            text_scale=.6)
            self.liquidatedText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.liquidated.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.liquidated.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.liquidated.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.liquidated.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.liquidated.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 11)
                self.liquidated.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.liquidated.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.liquidated.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.liquidated.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.liquidated.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.liquidated.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.liquidated.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.liquidated.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.liquidated.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.liquidated.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.liquidated.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            if self.statusEffects == 5:
                self.damageOvertime.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.damageOvertime.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.damageOvertime.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.damageOvertime.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.damageOvertime.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.damageOvertime.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.damageOvertime.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.damageOvertime.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            if self.statusEffects == 5:
                self.confused.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.confused.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.confused.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.confused.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.confused.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.confused.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.confused.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.confused.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            if self.statusEffects == 5:
                self.cooldown.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.cooldown.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.cooldown.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.cooldown.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.cooldown.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.cooldown.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.cooldown.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.cooldown.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            if self.statusEffects == 5:
                self.hidden.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.hidden.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.hidden.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.hidden.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.hidden.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.hidden.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.hidden.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.hidden.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if avatar.noDodge:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.noDodge = status.find('**/hurry_sickness_icon')
            self.nodDodgeRoundsText = DirectLabel(parent=self.noDodge, relief=None, text="%s" % avatar.getNoDodgeRounds(), text_fg=(1, 1, 1, 1),
                                                     text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                     pos=(0.25, 0, -.5),
                                                     text_scale=.6)
            self.nodDodgeRoundsText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.noDodge.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.noDodge.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.noDodge.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.noDodge.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.noDodge.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.noDodge.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.noDodge.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.noDodge.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.noDodge.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.noDodge.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.noDodge.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.noDodge.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.noDodge.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.noDodge.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.noDodge.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.noDodge.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if avatar.collectCalled:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.collectCall = status.find('**/bewitched_icon')
            self.collectCallRoundsText = DirectLabel(parent=self.collectCall, relief=None, text="%s" % avatar.getCollectCallRounds(), text_fg=(1, 1, 1, 1),
                                                     text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                     pos=(0.25, 0, -.5),
                                                     text_scale=.6)
            self.collectCallRoundsText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.collectCall.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.collectCall.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.collectCall.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.collectCall.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.collectCall.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.collectCall.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.collectCall.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.collectCall.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.collectCall.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.collectCall.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.collectCall.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.collectCall.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.collectCall.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.collectCall.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.collectCall.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.collectCall.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if avatar.mandatoryToll:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.mandatoryToll = status.find('**/bewitched_icon')
            self.mandatoryTollNumberText = DirectLabel(parent=self.mandatoryToll, relief=None, text="-%s" % avatar.getMandatoryToll(), text_fg=(1, 0, 0, 1),
                                                     text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                     pos=(0.25, 0, -.5),
                                                     text_scale=.6)
            self.mandatoryTollNumberText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.mandatoryToll.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.mandatoryToll.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.mandatoryToll.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.mandatoryToll.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.mandatoryToll.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.mandatoryToll.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.mandatoryToll.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.mandatoryToll.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.mandatoryToll.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.mandatoryToll.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.mandatoryToll.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.mandatoryToll.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.mandatoryToll.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.mandatoryToll.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.mandatoryToll.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.mandatoryToll.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.groupDamageDown.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.groupDamageDown.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.groupDamageDown.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.groupDamageDown.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.groupDamageDown.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.groupDamageDown.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.groupDamageDown.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.groupDamageDown.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.groupDamageDown.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.groupDamageDown.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.groupDamageDown.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.groupDamageDown.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.groupDamageDown.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.groupDamageDown.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.groupDamageDown.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.groupDamageDown.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            if self.statusEffects == 5:
                self.winded.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.winded.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.winded.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.winded.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.winded.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.winded.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.winded.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.winded.setColor(1, 1, 1, 1)
                self.attackIcon7.show()

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