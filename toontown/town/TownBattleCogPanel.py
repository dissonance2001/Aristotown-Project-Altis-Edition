from panda3d.core import *
from panda3d.direct import *
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
        status = loader.loadModel('phase_3.5/models/gui/status_effects')
        status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
        status3 = loader.loadModel('phase_3.5/models/gui/status_effects')
        status4 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.enraged = status.find('**/rage_mode_icon')  # second slot enraged
        self.enraged.reparentTo(self.healthNode)
        self.enraged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.enraged.hide()
        self.shielding = status.find('**/defense_mode_icon')  # second slot defense
        self.shielding.reparentTo(self.healthNode)
        self.shielding.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.shielding.hide()
        self.enraged2 = status2.find('**/rage_mode_icon')  # third slot enraged
        self.enraged2.reparentTo(self.healthNode)
        self.enraged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.enraged2.hide()
        self.shielding2 = status2.find('**/defense_mode_icon')  # third slot defense
        self.shielding2.reparentTo(self.healthNode)
        self.shielding2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.shielding2.hide()
        self.enraged3 = status3.find('**/rage_mode_icon')  # fourth slot enraged
        self.enraged3.reparentTo(self.healthNode)
        self.enraged3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.enraged3.hide()
        self.shielding3= status3.find('**/defense_mode_icon')  # fourth slot defense
        self.shielding3.reparentTo(self.healthNode)
        self.shielding3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.shielding3.hide()
        self.overcharged = status.find('**/overcharge_icon') # second slot overcharge
        self.overcharged.reparentTo(self.healthNode)
        self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.overcharged.hide()
        self.overcharged2 = status2.find('**/overcharge_icon') #third slot overcharge
        self.overcharged2.reparentTo(self.healthNode)
        self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.overcharged2.hide()
        self.lured = status.find('**/lured_prestige_icon') #lure resistance overcharge first slot
        self.lured.reparentTo(self.healthNode)
        self.lured.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.lured.hide()
        self.luredCog = status.find('**/lured_icon')  # lure icon first
        self.luredCog.reparentTo(self.healthNode)
        self.luredCog.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.luredCog.hide()
        self.luredCog2 = status2.find('**/lured_icon')  # lure icon 2nd
        self.luredCog2.reparentTo(self.healthNode)
        self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.luredCog2.hide()
        self.luredCog3 = status3.find('**/lured_icon')  # lure icon 3rd
        self.luredCog3.reparentTo(self.healthNode)
        self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.luredCog3.hide()
        self.luredCog4 = status4.find('**/lured_icon')  # lure icon 4th
        self.luredCog4.reparentTo(self.healthNode)
        self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.luredCog4.hide()
        self.luredManager = status2.find('**/lured_prestige_icon') # lure resistance manager first slot
        self.luredManager.reparentTo(self.healthNode)
        self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.luredManager.hide()
        self.luredManager2 = status3.find('**/lured_prestige_icon') #lure resistance second slot
        self.luredManager2.reparentTo(self.healthNode)
        self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165) #second slot lure resist
        self.luredManager2.hide()
        self.insured = status3.find('**/insured_icon') #second slot insurance
        self.insured.reparentTo(self.healthNode)
        self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.insured.hide()
        self.insured2 = status2.find('**/insured_icon')
        self.insured2.reparentTo(self.healthNode)
        self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165) #third slot insurance
        self.insured2.hide()
        self.insured4 = status4.find('**/insured_icon')
        self.insured4.reparentTo(self.healthNode)
        self.insured4.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)  # 1st slot insurance
        self.insured4.hide()
        self.insured3 = status.find('**/insured_icon')
        self.insured3.reparentTo(self.healthNode)
        self.insured3.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165) # 4th slot insurance
        self.insured3.hide()
        self.damageUp = status2.find('**/suit_damage_up_icon') #second slot damage up
        self.damageUp.reparentTo(self.healthNode)
        self.damageUp.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.damageUp.hide()
        self.damageUp2 = status.find('**/suit_damage_up_icon') # third slot damage up
        self.damageUp2.reparentTo(self.healthNode)
        self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.damageUp2.hide()
        self.damageUpMgr = status3.find('**/suit_damage_up_icon') # 4th slot damage up
        self.damageUpMgr.reparentTo(self.healthNode)
        self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.damageUpMgr.hide()
        self.skeleton = status.find('**/skelecog_icon')
        self.skeleton.reparentTo(self.healthNode)
        self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.skeleton.hide()
        self.virtual = status.find('**/virtual_icon')
        self.virtual.reparentTo(self.healthNode)
        self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.virtual.hide()
        self.immortal = status.find('**/worker_management_icon') #second slot immunity icon
        self.immortal.reparentTo(self.healthNode)
        self.immortal.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.immortal.hide()
        self.immortal2 = status.find('**/unite_cooldown_icon')  # third slot immunity icon
        self.immortal2.reparentTo(self.healthNode)
        self.immortal2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.immortal2.hide()
        self.immortal3 = status2.find('**/focused_defense_icon')  # third slot immunity icon
        self.immortal3.reparentTo(self.healthNode)
        self.immortal3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.immortal3.hide()
        self.immortal4 = status.find('**/focused_defense_icon')  # fourth slot immunity icon
        self.immortal4.reparentTo(self.healthNode)
        self.immortal4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.immortal4.hide()
        self.vulnerable = status.find('**/broken_shield_icon')  # first slot vulnerability icon
        self.vulnerable.reparentTo(self.healthNode)
        self.vulnerable.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.vulnerable.hide()
        self.vulnerable2 = status2.find('**/broken_shield_icon') # second slot vulnerability icon
        self.vulnerable2.reparentTo(self.healthNode)
        self.vulnerable2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.vulnerable2.hide()
        self.vulnerable3 = status3.find('**/broken_shield_icon') # third slot vulnerability icon
        self.vulnerable3.reparentTo(self.healthNode)
        self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.vulnerable3.hide()
        self.vulnerable4 = status4.find('**/broken_shield_icon')  # fourth slot vulnerability icon
        self.vulnerable4.reparentTo(self.healthNode)
        self.vulnerable4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.vulnerable4.hide()
        self.soakResist = status.find('**/soaked_icon')  # first slot soak resist icon
        self.soakResist.reparentTo(self.healthNode)
        self.soakResist.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.soakResist.hide()
        self.soakResist2 = status2.find('**/soaked_icon')  # 2 slot soak resist icon
        self.soakResist2.reparentTo(self.healthNode)
        self.soakResist2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.soakResist2.hide()
        self.soakResist3 = status3.find('**/soaked_icon')  # 3 slot soak resist icon
        self.soakResist3.reparentTo(self.healthNode)
        self.soakResist3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.soakResist3.hide()
        self.soakResist4 = status4.find('**/soaked_icon')  # 4 slot soak resist icon
        self.soakResist4.reparentTo(self.healthNode)
        self.soakResist4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.soakResist4.hide()
        self.syphon = status.find('**/ink_drain_icon')  # 1 slot soak syphon icon
        self.syphon.reparentTo(self.healthNode)
        self.syphon.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.syphon.hide()
        self.syphon2 = status2.find('**/ink_drain_icon')  # 2 slot soak syphon icon
        self.syphon2.reparentTo(self.healthNode)
        self.syphon2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.syphon2.hide()
        self.syphon3 = status3.find('**/ink_drain_icon')  # 3 slot soak syphon icon
        self.syphon3.reparentTo(self.healthNode)
        self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.syphon3.hide()
        self.syphon4 = status4.find('**/ink_drain_icon')  # 4 slot soak syphon icon
        self.syphon4.reparentTo(self.healthNode)
        self.syphon4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.syphon4.hide()
        self.absorbing = status.find('**/damage_absorb_icon')  # 1 slot absorb icon
        self.absorbing.reparentTo(self.healthNode)
        self.absorbing.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.absorbing.hide()
        self.absorbing2 = status2.find('**/damage_absorb_icon')  # 2 slot absorb icon
        self.absorbing2.reparentTo(self.healthNode)
        self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.absorbing2.hide()
        self.absorbing3 = status3.find('**/damage_absorb_icon')  # 3 slot absorb icon
        self.absorbing3.reparentTo(self.healthNode)
        self.absorbing3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.absorbing3.hide()
        self.absorbing4 = status4.find('**/damage_absorb_icon')  # 4 slot absorb icon
        self.absorbing4.reparentTo(self.healthNode)
        self.absorbing4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.absorbing4.hide()
        self.damageReduction = status.find('**/shield_icon')  # 1 slot damage reduction
        self.damageReduction.reparentTo(self.healthNode)
        self.damageReduction.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.damageReduction.hide()
        self.damageReduction2 = status2.find('**/shield_icon')  # 2 slot damage reduction
        self.damageReduction2.reparentTo(self.healthNode)
        self.damageReduction2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.damageReduction2.hide()
        self.damageReduction3 = status3.find('**/shield_icon')  # 3 slot damage reduction
        self.damageReduction3.reparentTo(self.healthNode)
        self.damageReduction3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.damageReduction3.hide()
        self.damageReduction4 = status4.find('**/shield_icon')  # 4 slot damage reduction
        self.damageReduction4.reparentTo(self.healthNode)
        self.damageReduction4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.damageReduction4.hide()
        self.lureImmune = status.find('**/cashback_icon')  # 1 slot lure immune
        self.lureImmune.reparentTo(self.healthNode)
        self.lureImmune.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.lureImmune.hide()
        self.lureImmune2 = status2.find('**/cashback_icon')  # 2 slot lure immune
        self.lureImmune2.reparentTo(self.healthNode)
        self.lureImmune2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.lureImmune2.hide()
        self.lureImmune3 = status3.find('**/cashback_icon')  # 3 slot lure immune
        self.lureImmune3.reparentTo(self.healthNode)
        self.lureImmune3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.lureImmune3.hide()
        self.lureImmune4 = status4.find('**/cashback_icon')  # 4 slot lure immune
        self.lureImmune4.reparentTo(self.healthNode)
        self.lureImmune4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.lureImmune4.hide()
        self.yellow = status3.find('**/fizzle_icon')  # 3 slot lure immune
        self.yellow.reparentTo(self.healthNode)
        self.yellow.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.yellow.hide()
        self.orange = status3.find('**/full_deck_icon')  # 3 slot lure immune
        self.orange.reparentTo(self.healthNode)
        self.orange.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.orange.hide()
        self.lightblue = status3.find('**/duck_drop_icon')  # 3 slot lure immune
        self.lightblue.reparentTo(self.healthNode)
        self.lightblue.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.lightblue.hide()
        self.green = status3.find('**/no_green_light_icon')  # 3 slot lure immune
        self.green.reparentTo(self.healthNode)
        self.green.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.green.hide()
        self.blue = status3.find('**/singing_blues_icon')  # 3 slot lure immune
        self.blue.reparentTo(self.healthNode)
        self.blue.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.blue.hide()
        self.red = status3.find('**/trap_card_icon')  # 3 slot lure immune
        self.red.reparentTo(self.healthNode)
        self.red.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.red.hide()
        self.pink = status3.find('**/brain_icon')  # 3 slot lure immune
        self.pink.reparentTo(self.healthNode)
        self.pink.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.pink.hide()
        self.rainbow = status3.find('**/harmonious_colors_icon')
        self.rainbow.reparentTo(self.healthNode)
        self.rainbow.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.rainbow.hide()
        self.hollywoods = status3.find('**/marked_icon')
        self.hollywoods.reparentTo(self.healthNode)
        self.hollywoods.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.hollywoods.hide()
        self.sharkwatcher = status3.find('**/ripped_icon')
        self.sharkwatcher.reparentTo(self.healthNode)
        self.sharkwatcher.setPosHprScale(-0.3925, 0.5, 0.025, 0, 0, 0, .24, .24, .24)
        self.sharkwatcher.hide()
        self.healthBar2 = DirectWaitBar(parent=self, pos=(-0.026, -0.11, -0.035), relief=DGG.SUNKEN, value=100,
                                        frameSize=(-2.5, 2.75, -0.6, 0.65),
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

    def setLevelText(self):
        self.skeleton.hide()
        self.virtual.hide()
        self.damageUp.hide()
        self.luredManager2.hide()
        self.damageUpMgr.hide()
        self.overcharged2.hide()
        self.overcharged.hide()
        self.shielding.hide()
        self.shielding2.hide()
        self.shielding3.hide()
        self.enraged.hide()
        self.enraged2.hide()
        self.enraged3.hide()
        self.damageUp2.hide()
        self.insured2.hide()
        self.insured.hide()
        self.insured3.hide()
        self.lured.hide()
        self.luredCog.hide()
        self.luredCog2.hide()
        self.luredCog3.hide()
        self.luredCog4.hide()
        self.immortal.hide()
        self.immortal2.hide()
        self.immortal3.hide()
        self.immortal4.hide()
        self.luredManager.hide()
        self.syphon.hide()
        self.syphon2.hide()
        self.syphon3.hide()
        self.insured4.hide()
        self.syphon4.hide()
        self.vulnerable.hide()
        self.vulnerable2.hide()
        self.vulnerable3.hide()
        self.vulnerable4.hide()
        self.soakResist.hide()
        self.soakResist2.hide()
        self.soakResist3.hide()
        self.soakResist4.hide()
        self.absorbing.hide()
        self.absorbing2.hide()
        self.absorbing3.hide()
        self.absorbing4.hide()
        self.damageReduction.hide()
        self.damageReduction2.hide()
        self.damageReduction3.hide()
        self.damageReduction4.hide()
        self.lureImmune.hide()
        self.lureImmune2.hide()
        self.lureImmune3.hide()
        self.lureImmune4.hide()
        self.yellow.hide()
        self.orange.hide()
        self.lightblue.hide()
        self.green.hide()
        self.blue.hide()
        self.red.hide()
        self.pink.hide()
        self.rainbow.hide()
        self.hollywoods.hide()
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
        if self.cog.isImmortal and self.cog.dna.name == 'dsf':
            self.luredManager.show()
            self.insured.show()
            self.absorbing3.show()
        elif self.cog.dna.name == 'dsf':
            self.luredManager.show()
            self.insured.show()
        elif self.cog.dna.name == 'crf' and self.cog.isVulnerable:
            self.luredManager.show()
        elif self.cog.dna.name == 'crf' and self.cog.isPhase3:
            self.luredManager.show()
            self.rainbow.show()
        elif self.cog.dna.name == 'crf':
            self.luredManager.show()
            self.hollywoods.show()
        elif self.cog.dna.name == 'mad' and self.cog.healthCondition == 13 and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.lureImmune4.show()
            self.overcharged2.show()
        elif self.cog.dna.name == 'mad' and self.cog.healthCondition == 13:
            self.virtual.show()
            self.luredManager2.show()
            self.lureImmune4.show()
            self.overcharged2.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 13000 and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.orange.show()
            self.luredCog4.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 13000:
            self.virtual.show()
            self.luredManager2.show()
            self.orange.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12900 and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.orange.show()
            self.luredCog4.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12900:
            self.virtual.show()
            self.luredManager2.show()
            self.orange.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12800 and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.lureImmune3.show()
            self.luredCog4.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12800:
            self.virtual.show()
            self.luredManager2.show()
            self.lureImmune3.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12700 and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.lightblue.show()
            self.luredCog4.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12700:
            self.virtual.show()
            self.luredManager2.show()
            self.lightblue.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12600 and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.pink.show()
            self.luredCog4.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12600:
            self.virtual.show()
            self.luredManager2.show()
            self.pink.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12500 and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.red.show()
            self.luredCog4.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12500:
            self.virtual.show()
            self.luredManager2.show()
            self.red.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12400 and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.blue.show()
            self.luredCog4.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12400:
            self.virtual.show()
            self.luredManager2.show()
            self.blue.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12275 and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.yellow.show()
            self.luredCog4.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12275:
            self.virtual.show()
            self.luredManager2.show()
            self.yellow.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12100 and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.orange.show()
            self.luredCog4.show()
        elif self.cog.dna.name == 'mad' and self.cog.getMaxHP() == 12100:
            self.virtual.show()
            self.luredManager2.show()
            self.orange.show()
        elif self.cog.dna.name == 'mad' and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.green.show()
            self.luredCog4.show()
        elif self.cog.dna.name == 'mad':
            self.virtual.show()
            self.luredManager2.show()
            self.green.show()
        elif self.cog.isVirtual and self.cog.isImmortal:
            self.virtual.show()
            self.immortal.show()
            self.immortal2.show()
            self.immortal4.show()
        elif self.cog.isSkeleton and self.cog.isImmortal:
            self.virtual.hide()
            self.immortal.show()
            self.immortal2.show()
            self.immortal4.show()
        elif self.cog.isImmortal:
            self.luredManager.show()
            self.immortal.show()
            self.immortal2.show()
            self.immortal4.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.dna.name == 'scg' and self.cog.isAngry:
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.enraged3.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.dna.name == 'scg' and self.cog.isAngry:
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.enraged3.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.dna.name == 'scg' and self.cog.isShielding:
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.shielding3.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.dna.name == 'scg' and self.cog.isShielding:
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.shielding3.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and not self.cog.getManager() and self.cog.isSyphon:
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.syphon4.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and not self.cog.getManager() and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.luredCog4.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and not self.cog.getManager() and self.cog.isDamageUp:
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.damageUpMgr.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isInsured and not self.cog.getManager():
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.insured3.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and not self.cog.getManager():
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isSyphon:
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.syphon4.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isLureImmune:
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.lureImmune4.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isShielding:
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.absorbing4.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isSyphon:
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.syphon4.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.luredCog4.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isVulnerable:
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.vulnerable4.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isDamageUp:
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.damageUpMgr.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual:
            self.virtual.show()
            self.luredManager2.show()
            self.overcharged2.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isInsured and not self.cog.getManager():
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.insured3.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and not self.cog.getManager() and self.cog.isSyphon:
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.syphon4.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and not self.cog.getManager() and self.cog.isLured:
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.luredCog4.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and not self.cog.getManager() and self.cog.isDamageUp:
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.damageUpMgr.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and not self.cog.getManager():
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isSyphon:
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.syphon4.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isLureImmune:
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.lureImmune4.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isShielding:
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.absorbing4.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isSyphon:
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.syphon4.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isVulnerable:
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.vulnerable4.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isLured:
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.luredCog4.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isDamageUp:
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
            self.damageUpMgr.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton:
            self.skeleton.show()
            self.luredManager2.show()
            self.overcharged2.show()
        elif self.cog.healthCondition == 13 and not self.cog.getManager() and self.cog.isSyphon and self.cog.isLured:
            self.luredManager.show()
            self.overcharged.show()
            self.syphon3.show()
            self.luredCog4.show()
        elif self.cog.healthCondition == 13 and not self.cog.getManager() and self.cog.isInsured and self.cog.isLured:
            self.luredManager.show()
            self.overcharged.show()
            self.insured2.show()
            self.luredCog4.show()
        elif self.cog.healthCondition == 13 and self.cog.isInsured and not self.cog.getManager():
            self.luredManager.show()
            self.overcharged.show()
            self.insured2.show()
        elif self.cog.healthCondition == 13 and not self.cog.getManager() and self.cog.isSyphon:
            self.luredManager.show()
            self.overcharged.show()
            self.syphon3.show()
        elif self.cog.healthCondition == 13 and not self.cog.getManager() and self.cog.isInsured:
            self.luredManager.show()
            self.overcharged.show()
            self.insured2.show()
        elif self.cog.healthCondition == 13 and not self.cog.getManager() and self.cog.isLured:
            self.luredManager.show()
            self.overcharged.show()
            self.luredCog3.show()
        elif self.cog.healthCondition == 13 and not self.cog.getManager():
            self.luredManager.show()
            self.overcharged.show()
        elif self.cog.healthCondition == 13 and self.cog.isSyphon and self.cog.isLureImmune:
            self.luredManager.show()
            self.overcharged.show()
            self.syphon3.show()
            self.lureImmune4.show()
        elif self.cog.healthCondition == 13 and self.cog.isSyphon and self.cog.isShielding:
            self.luredManager.show()
            self.overcharged.show()
            self.syphon3.show()
            self.absorbing4.show()
        elif self.cog.healthCondition == 13 and self.cog.isSyphon and self.cog.isDamageUp:
            self.luredManager.show()
            self.overcharged.show()
            self.syphon3.show()
            self.damageUpMgr.show()
        elif self.cog.healthCondition == 13 and self.cog.isVulnerable and self.cog.isDamageUp:
            self.luredManager.show()
            self.overcharged.show()
            self.vulnerable3.show()
            self.damageUpMgr.show()
        elif self.cog.healthCondition == 13 and self.cog.isSyphon and self.cog.isLured:
            self.luredManager.show()
            self.overcharged.show()
            self.syphon3.show()
            self.luredCog4.show()
        elif self.cog.healthCondition == 13 and self.cog.isVulnerable and self.cog.isLured:
            self.luredManager.show()
            self.overcharged.show()
            self.vulnerable3.show()
            self.luredCog4.show()
        elif self.cog.healthCondition == 13 and self.cog.isVulnerable:
            self.luredManager.show()
            self.overcharged.show()
            self.vulnerable3.show()
        elif self.cog.healthCondition == 13 and self.cog.isSyphon:
            self.luredManager.show()
            self.overcharged.show()
            self.syphon3.show()
        elif self.cog.healthCondition == 13 and self.cog.isLureImmune and self.cog.isDamageUp:
            self.luredManager.show()
            self.overcharged.show()
            self.lureImmune3.show()
            self.damageUpMgr.show()
        elif self.cog.healthCondition == 13 and self.cog.isShielding and self.cog.isDamageUp:
            self.luredManager.show()
            self.overcharged.show()
            self.absorbing3.show()
            self.damageUpMgr.show()
        elif self.cog.healthCondition == 13 and self.cog.isLureImmune and self.cog.isLured:
            self.luredManager.show()
            self.overcharged.show()
            self.lureImmune3.show()
            self.luredCog4.show()
        elif self.cog.healthCondition == 13 and self.cog.isShielding and self.cog.isLured:
            self.luredManager.show()
            self.overcharged.show()
            self.absorbing3.show()
            self.luredCog4.show()
        elif self.cog.healthCondition == 13 and self.cog.isSyphon and self.cog.isLured:
            self.luredManager.show()
            self.overcharged.show()
            self.syphon3.show()
            self.luredCog4.show()
        elif self.cog.healthCondition == 13 and self.cog.isSoakImmune and self.cog.isLured:
            self.luredManager.show()
            self.overcharged.show()
            self.soakResist3.show()
            self.luredCog4.show()
        elif self.cog.healthCondition == 13 and self.cog.isLured and self.cog.isDamageUp:
            self.luredManager.show()
            self.overcharged.show()
            self.luredCog4.show()
            self.damageUp2.show()
        elif self.cog.healthCondition == 13 and self.cog.isSoakImmune:
            self.luredManager.show()
            self.overcharged.show()
            self.soakResist3.show()
        elif self.cog.healthCondition == 13 and self.cog.isLureImmune:
            self.luredManager.show()
            self.overcharged.show()
            self.lureImmune3.show()
        elif self.cog.healthCondition == 13 and self.cog.isShielding:
            self.luredManager.show()
            self.overcharged.show()
            self.absorbing3.show()
        elif self.cog.healthCondition == 13 and self.cog.isSyphon:
            self.luredManager.show()
            self.overcharged.show()
            self.syphon3.show()
        elif self.cog.healthCondition == 13 and self.cog.isVulnerable:
            self.luredManager.show()
            self.overcharged.show()
            self.vulnerable3.show()
        elif self.cog.healthCondition == 13 and self.cog.isDamageUp:
            self.luredManager.show()
            self.overcharged.show()
            self.damageUp2.show()
        elif self.cog.healthCondition == 13 and self.cog.isLured:
            self.luredManager.show()
            self.overcharged.show()
            self.luredCog3.show()
        elif self.cog.healthCondition == 13:
            self.luredManager.show()
            self.overcharged.show()
        elif self.cog.isVirtual and self.cog.dna.name == 'scg' and self.cog.isAngry and self.cog.isDamageUp:
            self.virtual.show()
            self.luredManager2.show()
            self.enraged2.show()
            self.damageUpMgr.show()
        elif self.cog.isVirtual and self.cog.dna.name == 'scg' and self.cog.isAngry and self.cog.isInsured:
            self.virtual.show()
            self.luredManager2.show()
            self.enraged2.show()
            self.insured3.show()
        elif self.cog.isSkeleton and self.cog.dna.name == 'scg' and self.cog.isAngry and self.cog.isDamageUp:
            self.skeleton.show()
            self.luredManager2.show()
            self.enraged2.show()
            self.damageUpMgr.show()
        elif self.cog.isSkeleton and self.cog.dna.name == 'scg' and self.cog.isAngry:
            self.skeleton.show()
            self.luredManager2.show()
            self.enraged2.show()
        elif self.cog.isVirtual and self.cog.dna.name == 'scg' and self.cog.isShielding and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.shielding2.show()
            self.luredCog4.show()
        elif self.cog.isVirtual and self.cog.dna.name == 'scg' and self.cog.isShielding and self.cog.isDamageUp:
            self.virtual.show()
            self.luredManager2.show()
            self.shielding2.show()
            self.damageUpMgr.show()
        elif self.cog.isVirtual and self.cog.dna.name == 'scg' and self.cog.isShielding:
            self.virtual.show()
            self.luredManager2.show()
            self.shielding2.show()
        elif self.cog.isSkeleton and self.cog.dna.name == 'scg' and self.cog.isShielding and self.cog.isLured:
            self.skeleton.show()
            self.luredManager2.show()
            self.shielding2.show()
            self.luredCog4.show()
        elif self.cog.isSkeleton and self.cog.dna.name == 'scg' and self.cog.isShielding and self.cog.isDamageUp:
            self.skeleton.show()
            self.luredManager2.show()
            self.shielding2.show()
            self.damageUpMgr.show()
        elif self.cog.isSkeleton and self.cog.dna.name == 'scg' and self.cog.isShielding and self.cog.isInsured:
            self.skeleton.show()
            self.luredManager2.show()
            self.shielding2.show()
            self.insured4.show()
        elif self.cog.isSkeleton and self.cog.dna.name == 'scg' and self.cog.isShielding:
            self.skeleton.show()
            self.luredManager2.show()
            self.shielding2.show()
        elif self.cog.dna.name == 'scg' and self.cog.isShielding and self.cog.isDamageUp and self.cog.isInsured:
            self.luredManager.show()
            self.shielding.show()
            self.damageUp2.show()
            self.insured3.show()
        elif self.cog.dna.name == 'scg' and self.cog.isShielding and self.cog.isLured:
            self.luredManager.show()
            self.shielding.show()
            self.luredCog3.show()
        elif self.cog.dna.name == 'scg' and self.cog.isShielding and self.cog.isInsured:
            self.luredManager.show()
            self.shielding.show()
            self.insured2.show()
        elif self.cog.dna.name == 'scg' and self.cog.isShielding:
            self.luredManager.show()
            self.shielding.show()
        elif self.cog.dna.name == 'scg' and self.cog.isAngry and self.cog.isDamageUp and self.cog.isInsured:
            self.luredManager.show()
            self.enraged.show()
            self.damageUp2.show()
            self.insured3.show()
        elif self.cog.dna.name == 'scg' and self.cog.isAngry and self.cog.isDamageUp:
            self.luredManager.show()
            self.enraged.show()
            self.damageUp2.show()
        elif self.cog.dna.name == 'scg' and self.cog.isAngry and self.cog.isInsured:
            self.luredManager.show()
            self.enraged.show()
            self.insured2.show()
        elif self.cog.dna.name == 'scg' and self.cog.isAngry:
            self.luredManager.show()
            self.enraged.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isContracted and self.cog.isLured:
            self.virtual.show()
            self.insured.show()
            self.luredCog3.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isInsured and self.cog.isLured:
            self.virtual.show()
            self.insured.show()
            self.luredCog3.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isSyphon and self.cog.isLured:
            self.virtual.show()
            self.syphon2.show()
            self.luredCog3.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isSyphon and self.cog.isDamageUp:
            self.virtual.show()
            self.syphon2.show()
            self.damageUp2.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isContracted:
            self.virtual.show()
            self.insured.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isInsured:
            self.virtual.show()
            self.insured.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isSyphon:
            self.virtual.show()
            self.syphon2.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isLured and self.cog.isDamageUp:
            self.virtual.show()
            self.luredCog2.show()
            self.damageUp2.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isLured:
            self.virtual.show()
            self.luredCog2.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isDamageUp:
            self.virtual.show()
            self.damageUp.show()
        elif self.cog.isVirtual and not self.cog.getManager():
            self.virtual.show()
        elif self.cog.isVirtual and self.cog.isSyphon and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.syphon3.show()
            self.luredCog4.show()
        elif self.cog.isVirtual and self.cog.isVulnerable and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.vulnerable3.show()
            self.luredCog4.show()
        elif self.cog.isVirtual and self.cog.isVulnerable and self.cog.isDamageUp:
            self.virtual.show()
            self.luredManager2.show()
            self.vulnerable3.show()
            self.damageUpMgr.show()
        elif self.cog.isVirtual and self.cog.isSyphon and self.cog.isDamageUp:
            self.virtual.show()
            self.luredManager2.show()
            self.syphon3.show()
            self.damageUpMgr.show()
        elif self.cog.isVirtual and self.cog.isSyphon:
            self.virtual.show()
            self.luredManager2.show()
            self.syphon3.show()
        elif self.cog.isVirtual and self.cog.isLureImmune and self.cog.isDamageUp:
            self.virtual.show()
            self.luredManager2.show()
            self.lureImmune3.show()
            self.damageUpMgr.show()
        elif self.cog.isVirtual and self.cog.isLureImmune:
            self.virtual.show()
            self.luredManager2.show()
            self.lureImmune3.show()
        elif self.cog.isVirtual and self.cog.isShielding and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.absorbing3.show()
            self.luredCog4.show()
        elif self.cog.isVirtual and self.cog.isShielding and self.cog.isDamageUp:
            self.virtual.show()
            self.luredManager2.show()
            self.absorbing3.show()
            self.damageUpMgr.show()
        elif self.cog.isVirtual and self.cog.isShielding:
            self.virtual.show()
            self.luredManager2.show()
            self.absorbing3.show()
        elif self.cog.isVirtual and self.cog.isSyphon and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.syphon3.show()
            self.luredCog4.show()
        elif self.cog.isVirtual and self.cog.isSyphon and self.cog.isDamageUp:
            self.virtual.show()
            self.luredManager2.show()
            self.syphon3.show()
            self.damageUpMgr.show()
        elif self.cog.isVirtual and self.cog.isSyphon:
            self.virtual.show()
            self.luredManager2.show()
            self.syphon3.show()
        elif self.cog.isVirtual and self.cog.isDamageUp and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.luredCog3.show()
            self.damageUpMgr.show()
        elif self.cog.isVirtual and self.cog.isDamageUp:
            self.virtual.show()
            self.luredManager2.show()
            self.damageUp2.show()
        elif self.cog.isVirtual and self.cog.isLured:
            self.virtual.show()
            self.luredManager2.show()
            self.luredCog3.show()
        elif self.cog.isVirtual:
            self.virtual.show()
            self.luredManager2.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isSyphon and self.cog.isLured:
            self.skeleton.show()
            self.syphon2.show()
            self.luredCog3.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isContracted and self.cog.isLured:
            self.skeleton.show()
            self.insured.show()
            self.luredCog3.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isInsured and self.cog.isLured:
            self.skeleton.show()
            self.insured.show()
            self.luredCog3.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isSyphon and self.cog.isDamageUp:
            self.skeleton.show()
            self.syphon2.show()
            self.damageUp2.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isSyphon:
            self.skeleton.show()
            self.syphon2.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isLured and self.cog.isDamageUp:
            self.skeleton.show()
            self.luredCog2.show()
            self.damageUp2.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isLured:
            self.skeleton.show()
            self.luredCog2.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isContracted:
            self.skeleton.show()
            self.insured.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isInsured:
            self.skeleton.show()
            self.insured.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isDamageUp:
            self.skeleton.show()
            self.damageUp.show()
        elif self.cog.isSkeleton and not self.cog.getManager():
            self.skeleton.show()
        elif self.cog.isSkeleton and self.cog.isInsured and self.cog.isDamageUp:
            self.skeleton.show()
            self.luredManager2.show()
            self.insured2.show()
            self.damageUpMgr.show()
        elif self.cog.isSkeleton and self.cog.isSyphon and self.cog.isLured:
            self.skeleton.show()
            self.luredManager2.show()
            self.syphon3.show()
            self.luredCog4.show()
        elif self.cog.isSkeleton and self.cog.isInsured and self.cog.isLured:
            self.skeleton.show()
            self.luredManager2.show()
            self.insured2.show()
            self.luredCog4.show()
        elif self.cog.isSkeleton and self.cog.isSyphon and self.cog.isDamageUp:
            self.skeleton.show()
            self.luredManager2.show()
            self.syphon3.show()
            self.damageUpMgr.show()
        elif self.cog.isSkeleton and self.cog.isContracted:
            self.skeleton.show()
            self.luredManager2.show()
            self.insured2.show()
        elif self.cog.isSkeleton and self.cog.isInsured:
            self.skeleton.show()
            self.luredManager2.show()
            self.insured2.show()
        elif self.cog.isSkeleton and self.cog.isSyphon:
            self.skeleton.show()
            self.luredManager2.show()
            self.syphon3.show()
        elif self.cog.isSkeleton and self.cog.isVulnerable and self.cog.isLured:
            self.skeleton.show()
            self.luredManager2.show()
            self.vulnerable3.show()
            self.luredCog4.show()
        elif self.cog.isSkeleton and self.cog.isVulnerable and self.cog.isDamageUp:
            self.skeleton.show()
            self.luredManager2.show()
            self.vulnerable3.show()
            self.damageUpMgr.show()
        elif self.cog.isSkeleton and self.cog.isVulnerable:
            self.skeleton.show()
            self.luredManager2.show()
            self.vulnerable3.show()
        elif self.cog.isSkeleton and self.cog.isLureImmune and self.cog.isDamageUp:
            self.skeleton.show()
            self.luredManager2.show()
            self.lureImmune3.show()
            self.damageUpMgr.show()
        elif self.cog.isSkeleton and self.cog.isLureImmune:
            self.skeleton.show()
            self.luredManager2.show()
            self.lureImmune3.show()
        elif self.cog.isSkeleton and self.cog.isShielding and self.cog.isLured:
            self.skeleton.show()
            self.luredManager2.show()
            self.absorbing3.show()
            self.luredCog4.show()
        elif self.cog.isSkeleton and self.cog.isShielding and self.cog.isDamageUp:
            self.skeleton.show()
            self.luredManager2.show()
            self.absorbing3.show()
            self.damageUpMgr.show()
        elif self.cog.isSkeleton and self.cog.isShielding:
            self.skeleton.show()
            self.luredManager2.show()
            self.absorbing3.show()
        elif self.cog.isSkeleton and self.cog.isSyphon and self.cog.isLured:
            self.skeleton.show()
            self.luredManager2.show()
            self.syphon3.show()
            self.luredCog4.show()
        elif self.cog.isSkeleton and self.cog.isSyphon and self.cog.isDamageUp:
            self.skeleton.show()
            self.luredManager2.show()
            self.syphon3.show()
            self.damageUpMgr.show()
        elif self.cog.isSkeleton and self.cog.isSyphon:
            self.skeleton.show()
            self.luredManager2.show()
            self.syphon3.show()
        elif self.cog.isSkeleton and self.cog.isDamageUp and self.cog.isLured:
            self.skeleton.show()
            self.luredManager2.show()
            self.luredCog3.show()
            self.damageUpMgr.show()
        elif self.cog.isSkeleton and self.cog.isDamageUp:
            self.skeleton.show()
            self.luredManager2.show()
            self.damageUp2.show()
        elif self.cog.isSkeleton and self.cog.isLured:
            self.skeleton.show()
            self.luredManager2.show()
            self.luredCog3.show()
        elif self.cog.isSkeleton:
            self.skeleton.show()
            self.luredManager2.show()
        elif not self.cog.getManager() and self.cog.isContracted and self.cog.isLured:
            self.insured4.show()
            self.luredCog2.show()
        elif not self.cog.getManager() and self.cog.isInsured and self.cog.isLured:
            self.insured4.show()
            self.luredCog2.show()
        elif not self.cog.getManager() and self.cog.isSyphon and self.cog.isLured:
            self.syphon.show()
            self.luredCog2.show()
        elif not self.cog.getManager() and self.cog.isSyphon:
            self.syphon.show()
        elif not self.cog.getManager() and self.cog.isLured and self.cog.isDamageUp:
            self.luredCog2.show()
            self.luredManager.show()
            self.damageUp2.show()
        elif not self.cog.getManager() and self.cog.isLured:
            self.luredCog.show()
        elif not self.cog.getManager() and self.cog.isContracted:
            self.insured4.show()
        elif not self.cog.getManager() and self.cog.isInsured:
            self.insured4.show()
        elif self.cog.isSyphon and self.cog.isLured and self.cog.isDamageUp:
            self.luredManager.show()
            self.syphon2.show()
            self.luredCog3.show()
            self.damageUpMgr.show()
        elif self.cog.isLureImmune and self.cog.isDamageUp and self.cog.isSyphon:
            self.luredManager.show()
            self.lureImmune2.show()
            self.syphon3.show()
            self.damageUpMgr.show()
        elif self.cog.isShielding and self.cog.isDamageUp and self.cog.isSyphon:
            self.luredManager.show()
            self.absorbing2.show()
            self.syphon3.show()
            self.damageUpMgr.show()
        elif self.cog.isSoakImmune and self.cog.isDamageUp and self.cog.isSyphon:
            self.luredManager.show()
            self.soakResist2.show()
            self.syphon3.show()
            self.damageUpMgr.show()
        elif self.cog.isDamageUp and self.cog.isLured and self.cog.isContracted:
            self.luredManager.show()
            self.luredCog2.show()
            self.damageUp2.show()
            self.insured3.show()
        elif self.cog.isDamageUp and self.cog.isLured and self.cog.isInsured:
            self.luredManager.show()
            self.luredCog2.show()
            self.damageUp2.show()
            self.insured3.show()
        elif self.cog.isContracted and self.cog.isLured:
            self.luredManager.show()
            self.insured.show()
            self.luredCog3.show()
        elif self.cog.isInsured and self.cog.isLured:
            self.luredManager.show()
            self.insured.show()
            self.luredCog3.show()
        elif self.cog.isSoakImmune and self.cog.isLured:
            self.luredManager.show()
            self.soakResist2.show()
            self.luredCog3.show()
        elif self.cog.isLureImmune and self.cog.isSyphon:
            self.luredManager.show()
            self.lureImmune2.show()
            self.syphon3.show()
        elif self.cog.isShielding and self.cog.isSyphon:
            self.luredManager.show()
            self.absorbing2.show()
            self.syphon3.show()
        elif self.cog.isSyphon and self.cog.isLured:
            self.luredManager.show()
            self.syphon2.show()
            self.luredCog3.show()
        elif self.cog.isSyphon and self.cog.isDamageUp:
            self.luredManager.show()
            self.syphon2.show()
            self.damageUp2.show()
        elif self.cog.isVulnerable and self.cog.isLured and self.cog.isDamageUp:
            self.luredManager.show()
            self.vulnerable2.show()
            self.luredCog3.show()
            self.damageUpMgr.show()
        elif self.cog.isVulnerable and self.cog.isLured:
            self.luredManager.show()
            self.vulnerable2.show()
            self.luredCog3.show()
        elif self.cog.isVulnerable and self.cog.isDamageUp:
            self.luredManager.show()
            self.vulnerable2.show()
            self.damageUp2.show()
        elif self.cog.isSyphon:
            self.luredManager.show()
            self.syphon2.show()
        elif self.cog.isVulnerable:
            self.luredManager.show()
            self.vulnerable2.show()
        elif self.cog.isSoakImmune:
            self.luredManager.show()
            self.soakResist2.show()
        elif self.cog.isShielding and self.cog.isContracted and self.cog.isDamageUp:
            self.luredManager.show()
            self.absorbing2.show()
            self.insured2.show()
            self.damageUpMgr.show()
        elif self.cog.isShielding and self.cog.isInsured and self.cog.isDamageUp:
            self.luredManager.show()
            self.absorbing2.show()
            self.insured2.show()
            self.damageUpMgr.show()
        elif self.cog.isInsured and self.cog.isDamageUp:
            self.luredManager.show()
            self.insured.show()
            self.damageUp2.show()
        elif self.cog.isInsured:
            self.luredManager.show()
            self.insured.show()
        elif self.cog.isLureImmune and self.cog.isDamageUp:
            self.luredManager.show()
            self.lureImmune2.show()
            self.damageUp2.show()
        elif self.cog.isLureImmune:
            self.luredManager.show()
            self.lureImmune2.show()
        elif self.cog.isShielding and self.cog.isContracted and self.cog.isLured:
            self.luredManager.show()
            self.absorbing2.show()
            self.insured2.show()
            self.luredCog4.show()
        elif self.cog.isShielding and self.cog.isInsured and self.cog.isLured:
            self.luredManager.show()
            self.absorbing2.show()
            self.insured2.show()
            self.luredCog4.show()
        elif self.cog.isShielding and self.cog.isContracted:
            self.luredManager.show()
            self.absorbing2.show()
            self.insured2.show()
        elif self.cog.isShielding and self.cog.isInsured:
            self.luredManager.show()
            self.absorbing2.show()
            self.insured2.show()
        elif self.cog.isShielding and self.cog.isLured:
            self.luredManager.show()
            self.absorbing2.show()
            self.luredCog3.show()
        elif self.cog.isShielding and self.cog.isDamageUp:
            self.luredManager.show()
            self.absorbing2.show()
            self.damageUp2.show()
        elif self.cog.isShielding:
            self.luredManager.show()
            self.absorbing2.show()
        elif self.cog.isDamageUp and self.cog.isLured:
            self.luredManager.show()
            self.luredCog2.show()
            self.damageUp2.show()
        elif self.cog.isDamageUp:
            self.luredManager.show()
            self.damageUp.show()
        elif self.cog.isLured:
            self.luredManager.show()
            self.luredCog2.show()
        elif self.cog.getManager():
            self.luredManager.show()
        else:
            self.skeleton.hide()
            self.virtual.hide()
            self.damageUp.hide()
            self.luredManager2.hide()
            self.damageUpMgr.hide()
            self.overcharged2.hide()
            self.overcharged.hide()
            self.shielding.hide()
            self.shielding2.hide()
            self.shielding3.hide()
            self.enraged.hide()
            self.enraged2.hide()
            self.enraged3.hide()
            self.damageUp2.hide()
            self.insured2.hide()
            self.insured.hide()
            self.lured.hide()
            self.luredCog.hide()
            self.luredCog2.hide()
            self.luredCog3.hide()
            self.luredCog4.hide()
            self.immortal.hide()
            self.immortal2.hide()
            self.immortal3.hide()
            self.immortal4.hide()
            self.luredManager.hide()
            self.syphon.hide()
            self.syphon2.hide()
            self.syphon3.hide()
            self.syphon4.hide()
            self.vulnerable.hide()
            self.vulnerable2.hide()
            self.vulnerable3.hide()
            self.vulnerable4.hide()
            self.soakResist.hide()
            self.soakResist2.hide()
            self.soakResist3.hide()
            self.soakResist4.hide()
            self.absorbing.hide()
            self.absorbing2.hide()
            self.absorbing3.hide()
            self.absorbing4.hide()
            self.damageReduction.hide()
            self.damageReduction2.hide()
            self.damageReduction3.hide()
            self.damageReduction4.hide()
            self.lureImmune.hide()
            self.lureImmune2.hide()
            self.lureImmune3.hide()
            self.lureImmune4.hide()
            self.insured3.hide()
            self.yellow.hide()
            self.orange.hide()
            self.insured4.hide()
            self.lightblue.hide()
            self.green.hide()
            self.blue.hide()
            self.red.hide()
            self.pink.hide()
            self.rainbow.hide()
            self.hollywoods.hide()
        self.healthText['text'] = t

    def updateHealthBar(self):
        self.setLevelText()
        if self.cog.dna.name == 'bgh':
            self.sharkwatcher.show()
        else:
            self.sharkwatcher.hide()
        condition = self.cog.healthCondition
        if self.cog.getHP() >= 0:
            self.hp = self.cog.getHP()
        else:
            self.hp = 0
        self.maxHp = self.cog.getMaxHP()
        if condition == 9:
            taskMgr.remove(self.uniqueName('blink-task'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
                taskMgr.remove(self.uniqueName('blink-task'))
        elif condition == 10:
            taskMgr.remove(self.uniqueName('blink-task'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
        elif condition == 11:
            taskMgr.remove(self.uniqueName('blink-task'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
        elif condition == 13:
            taskMgr.remove(self.uniqueName('blink-task'))
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
                blinkTask = Task.loop(Task(self.__blinkPurple), Task.pause(1.5), Task(self.__blinkPurpleColor),
                                      Task.pause(1.5))
                taskMgr.add(blinkTask, self.uniqueName('blink-task'))
            self.hpText['text_fg'] = Vec4(1, 1, 1, 1.0)
        else:
            taskMgr.remove(self.uniqueName('blink-task'))
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
                taskMgr.remove(self.uniqueName('blink-task'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
        self.hpText['text'] = str(self.hp) + '/' + str(self.maxHp)

    def updateStatusIcons(self, cog, battle):
        if battle.isSuitLured(cog):
            self.lured.show()
        else:
            self.lured.hide()

    def __changeColor(self):
        self.interval = Parallel(LerpColorScaleInterval(self.healthBar2, duration=0, colorScale=(self.healthColors[self.cog.healthCondition]),
                                   blendType='easeInOut'))
        self.interval.start()

    def __pulseRed(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.healthBar2, duration=.25, colorScale=(1, 0, 0, 1),
                                   blendType='easeInOut'))
        self.interval.start()

    def __pulseGray(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.healthBar2, duration=.25, colorScale=(0.431, 0.431, 0.431, 1),
                                   blendType='easeInOut'))
        self.interval.start()

    def __pulsePurple(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.healthBar2, duration=1, colorScale=(0.702, 0, 1, 1),
                                                        blendType='easeInOut'))
        self.interval.start()

    def __pulsePurpleColor(self, task):
        self.interval = Parallel(LerpColorScaleInterval(self.healthBar2, duration=1, colorScale=(self.healthColors[13]),
                                                        blendType='easeInOut'))
        self.interval.start()

    def __blinkPurple(self, task):
        self.healthBar2.setProp('barColor', (0.702, 0, 1, 1))

    def __blinkPurpleColor(self, task):
        self.healthBar2.setProp('barColor', self.healthColors[13])

    def __blinkRed(self, task):
        self.healthBar2.setProp('barColor', self.healthColors[9])

    def __blinkGray(self, task):
        self.healthBar2.setProp('barColor', self.healthColors[10])


    def generateSuitHead(self, name):
        self.suitHead = Suit.attachSuitHead(self, name)
        self.suitHead.setScale(0.1)
        AnimList = 'neutral'
        if name == 'dfh':
            self.suitHead.setPosHprScale(-0.26, 0.5, 0.115, -90, 0, 0, .105, .105, .105)
        elif name == 'ptr':
            self.suitHead.setPosHprScale(-0.26, 0.5, 0.12, -90, 0, 0, .085, .085, .085)
        elif name == 'rng':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .115, .115, .115)
        elif name == 'jdg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .08, .08, .08)
        elif name == 'isw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .09, .09, .09)
        elif name == 'dvg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .1, .1, .1)
        elif name == 'trm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .095, .095, .095)
        elif name == 'bgh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .001, .001, .001)
        elif name == 'ste' or name == 'wrt':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0725, .0725, .0725)
        elif name == 'bg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .105, .105, .105)
        elif name == 'gry':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .065, .065, .065)
        elif name == 'scg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .1, .1, .1)
        elif name == 'kpn':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .09, .09, .09)
        elif name == 'crf' or name == 'mad':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .09, .09, .09)
        elif name == 'tld':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .07, .07, .07)
        elif name == 'sjg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .1, .1, .1)
        elif name == 'cn':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.09, -180, 0, 0, .1, .1, .1)
        elif name == 'fbd':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .09, .09, .09)
        elif name == 'mg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.135, -180, 0, 0, .06, .06, .06)
        elif name == 'arb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.135, -180, 0, 0, .115, .115, .115)
        elif name == 'ca':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .1, .1, .1)
        elif name == 'bs':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .075, .075, .075)
        elif name == 'ssm' or name == 'cvy' or name == 'mka' or name == 'txm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .089, .089, .089)
        elif name == 'pp' or name == 'nc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .06, .06, .06)
        elif name == 'p':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .07, .07, .07)
        elif name == 'mb' or name == 'kbc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1, .1, .1)
        elif name == 'bfh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .12, .12, .12)
        elif name == 'b':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .09, .09, .09)
        elif name == 'frs':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .08, .08, .08)
        elif name == 'prethink':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .1, .1, .1)
        elif name == 'gtk':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .1, .1, .1)
        elif name == 'ggm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1, .1, .1)
        elif name == 'bf':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .12, .12, .12)
        elif name == 'cps':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .16, .16, .16)
        elif name == 'trb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .095, .095, .095)
        elif name == 'ssr' or name == 'mm' or name == 'ds' or name == 'pht' or name == 'jb' or name == 'ka' or name == 'vpr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .1, .1, .1)
        elif name == 'ms':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .11, .11, .11)
        elif name == 'pyc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .13, .13, .13)
        elif name == 'gms':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .095, .095, .095)
        elif name == 'mh' or name == 'inw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .085, .085, .085)
        elif name == 'ls':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .12, .12, .12)
        elif name == 'm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .09, .09, .09)
        elif name == 'sb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .075, .075, .075)
        elif name == 'cfp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .09, .09, .09)
        elif name == 'bdb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .07, .07, .07)
        elif name == 'hh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .12, .12, .12)
        elif name == 'lsc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .09, .09, .09)
        elif name == 'brv':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .1, .1, .1)
        elif name == 'rus' or name == 'tm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .085, .085, .085)
        elif name == 'sdb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .0675, .0675, .0675)
        elif name == 'tbc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .08, .08, .08)
        elif name == 'nd':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .08, .08, .08)
        elif name == 'bw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .06, .06, .06)
        elif name == 'le':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .09, .09, .09)
        elif name == 'sd':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.09, -180, 0, 0, .08, .08, .08)
        elif name == 'cc' or name == 'sc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .12, .12, .12)
        elif name == 'cr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .17, .177, .177)
        elif name == 'bdb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .12, .12, .12)
        elif name == 'dot':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .175, .175, .175)
        elif name == 'f' or name == 'cpl' or name == 'trm' or name == 'sw' or name == 'skd' or name == 'bc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .175, .175, .175)
        elif name == 'rb' or name == 'gh' or name == 'sfs':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .08, .08, .08)
        elif name == 'bkp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .085, .085, .085)
        elif name == 'msr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .09, .09, .09)
        elif name == 'dsf':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .09, .09, .09)
        elif name == 'dm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .075, .075, .075)
        elif name == 'trk':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .085, .085, .085)
        elif name == 'fd':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1, .1, .1)
        elif name == 'nar':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .175, .175, .175)
        elif name == 'tc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .07, .07, .07)
        elif name == 'gm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1, .1, .1)
        elif name == 'tb' or name == 'ts':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .08, .08, .08)
        elif name == 'adc' or name == 'drm' or name == 'cry':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0875, .0875, .0875)
        elif name == 'mes':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .075, .075, .075)
        elif name == 'fm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .08, .08, .08)
        elif name == 'dsk':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1025, .1025, .1025)
        elif name == 'blr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .0725, .0725, .0725)
        elif name == 'dfg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .055, .055, .055)
        elif name == 'yuh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .055, .055, .055)
        elif name == 'dfr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .09, .09, .09)
        elif name == 'cp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .0875, .0875, .0875)
        elif name == 'dvk':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.145, -180, 0, 0, .08, .08, .08)
        elif name == 'dvp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.145, -180, 0, 0, .08, .08, .08)
        elif name == 'tcm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .095, .095, .095)
        elif name == 'ffm' or name == 'nhy' or name == 'bsh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .08, .08, .08)
        elif name == 'jr' or name == 'prr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .065, .065, .065)
        elif name == 'laa' or name == 'csh' or name == 'gb' or name == 'lbs' or name == 'ddv' or name == 'sya' or name == 'pbl' or name == 'mdr' or name == 'fas' or name == 'gkp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .12, .12, .12)
        elif name == 'cg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .125, .125, .125)
        elif name == 'jl' or name == 'tcc' or name == 'bgr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .3, .3, .3)
        elif name == 'jur' or name == 'ant' or name == 'fb' or name == 'jls' :
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .2, .2, .2)
        elif name == 'cm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .1, .1, .1)
        elif name == 'bf':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .11, .11, .11)
        elif name == 'whunter':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0575, .0575, .0575)
        elif name == 'th':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.155, -180, 0, 0, .07, .07, .07)
        elif name == 'mp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .08, .08, .08)
        elif name == 'tr' or name == 'msp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .075, .075, .075)
        elif name == 'kb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .09, .09, .09)
        elif name == 'csm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.15, -180, 0, 0, .09, .09, .09)
        elif name == 'hho':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .11, .11, .11)
        elif name == 'mld':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .08, .08, .08)
        elif name == 'ac':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .08, .08, .08)
        elif name == 'sys':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .115, .115, .115)
        elif name == 'kyl':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .085, .085, .085)
        elif name == 'cmk':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .155, .155, .155)
        elif name == 'phs':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .115, .115, .115)
        elif name == 'mdm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .105, .105, .105)
        elif name == 'tg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.135, -180, 0, 0, .14, .14, .14)
        elif name == 'tw':
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
        elif name == 'fpn':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .08, .08, .08)
        elif name == 'ghw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .07, .07, .07)
        elif name == 'bbr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .065, .065, .065)
        elif name == 'std':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .1, .1, .1)
        elif name == 'gzt':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .075, .075, .075)
        elif name == 'wnk':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .13, .13, .13)
        elif name == 'nsh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .08, .08, .08)
        elif name == 'anc':
            self.suitHead.setPosHprScale(-0.28, 0.5, 0.11, -180, 0, 0, .0725, .0725, .0725)
        elif name == 'ym':
            self.suitHead.setPosHprScale(-0.28, 0.5, 0.12, -180, 0, 0, .14, .14, .14)
        elif name == 'shp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .095, .095, .095)
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
        del self.cog
        del self.button
        del self.blinkTask
        del self.hpText
        DirectFrame.destroy(self)

    def cleanup(self):
        self.ignoreAll()
        self.cleanupHead()

        if self.blinkTask:
            taskMgr.remove(self.blinkTask)
            self.blinkTask = None

        del self.blinkTask
        taskMgr.remove(self.uniqueName('blink-task'))
        self.healthNode.removeNode()
        self.button.removeNode()
        DirectFrame.destroy(self)

    def cleanupHead(self):
        if self.suitHead:
            self.suitHead.removeNode()
            del self.suitHead
