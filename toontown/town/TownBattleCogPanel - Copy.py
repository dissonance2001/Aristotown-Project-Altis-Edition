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

self.statusFrame = loader.loadModel('phase_3.5/models/gui/battlegui/info_panels')
self.statusFramePanelSoaked = self.statusFrame.find('**/tooltip_debuff')
self.statusFramePanelSoaked.reparentTo(self.soaked)
self.statusFramePanelSoaked.setScale(11.5, 10, 5)
self.statusFramePanelSoaked.setPos(0, 0, -2)
self.statusFramePanelSoaked.hide()
self.soakedStatusText2 = DirectLabel(parent=self.statusFramePanel, relief=None, text='Soaked',
                                     text_align=TextNode.ACenter, text_fg=Vec4(0.302, 0.71, 0.871, 1),
                                     text_font=getSignFont(), pos=(0, 0, .075),
                                     text_scale=(0.045, 0.125, 0.2))
self.soakedStatusText1 = DirectLabel(parent=self.statusFramePanel, relief=None,
                                     text='Soaked Cogs have a -10% dodge chance and are\nvulnerable to ZAP Gags.\n\nRemoved if this Cog is hit by ZAP Gags.',
                                     text_align=TextNode.ACenter, text_fg=Vec4(0.663, 0.906, 1, 1),
                                     text_font=getSignFont(), pos=(0, 0, -.05),
                                     text_scale=(0.03, 0.075, 0.125))
self.soaked.bind(DGG.WITHIN, self.showPanel, extraArgs=[1])
self.soaked.bind(DGG.WITHOUT, self.hidePanel, extraArgs=[1])

if self.cog.isSoaked: # DEBUFFS
    self.status = loader.loadModel('phase_3.5/models/gui/status_effects')
    self.dazed = DirectButton(relief=None, geom=(self.status.find('**/confusion_icon')), rolloverSound=None,
                               clickSound=None)
    self.dazedText = DirectLabel(parent=self.dazed, relief=None,
                                         text="1",
                                         text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
    self.dazedText.show()
    self.statusFrame = loader.loadModel('phase_3.5/models/gui/battlegui/info_panels')
    self.statusFramePanel = self.statusFrame.find('**/tooltip_debuff')
    self.statusFramePanel.reparentTo(self.dazed)
    self.statusFramePanel.setScale(11.5, 10, 5)
    self.statusFramePanel.setPos(0, 0, -2)
    self.statusFramePanel.hide()
    statusText1 = DirectLabel(parent=self.statusFramePanel, relief=None, text='Dazed',
                                   text_align=TextNode.ACenter, text_fg=Vec4(0.302, 0.71, 0.871, 1), text_font=getSignFont(),
                                   pos=(0, 0, .075),
                                   text_scale=(0.045, 0.125, 0.2))
    statusText2 = DirectLabel(parent=self.statusFramePanel, relief=None,
                                   text='This Cog is dazed due to a TRAP activation, and\nas such has a -10% dodge chance reduction!',
                                   text_align=TextNode.ACenter, text_fg=Vec4(0.663, 0.906, 1, 1),
                                   text_font=getSignFont(), pos=(0, 0, -.05),
                                   text_scale=(0.03, 0.075, 0.125))
    self.dazed.bind(DGG.WITHIN, self.showPanel, extraArgs=[1])
    self.dazed.bind(DGG.WITHOUT, self.hidePanel, extraArgs=[1])

    if self.cog.isSoaked: # BUFFS
        self.status = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.dazed = DirectButton(relief=None, geom=(self.status.find('**/confusion_icon')), rolloverSound=None,
                                  clickSound=None)
        self.dazedText = DirectLabel(parent=self.dazed, relief=None,
                                     text="1",
                                     text_fg=(1, 1, 1, 1),
                                     text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                     pos=(0.25, 0, -.5),
                                     text_scale=.5)
        self.dazedText.show()
        self.statusFrame = loader.loadModel('phase_3.5/models/gui/battlegui/info_panels')
        self.statusFramePanel = self.statusFrame.find('**/tooltip_debuff')
        self.statusFramePanel.reparentTo(self.dazed)
        self.statusFramePanel.setScale(11.5, 10, 5)
        self.statusFramePanel.setPos(0, 0, -2)
        self.statusFramePanel.hide()
        statusText1 = DirectLabel(parent=self.statusFramePanel, relief=None, text='Dazed',
                                       text_align=TextNode.ACenter, text_fg=Vec4(0.302, 0.71, 0.871, 1),
                                       text_font=getSignFont(),
                                       pos=(0, 0, .075),
                                       text_scale=(0.045, 0.125, 0.2))
        statusText2 = DirectLabel(parent=self.statusFramePanel, relief=None,
                                       text='This Cog is dazed due to a TRAP activation, and\nas such has a -10% dodge chance reduction!',
                                       text_align=TextNode.ACenter, text_fg=Vec4(0.663, 0.906, 1, 1),
                                       text_font=getSignFont(), pos=(0, 0, -.05),
                                       text_scale=(0.03, 0.075, 0.125))
        self.dazed.bind(DGG.WITHIN, self.showPanel, extraArgs=[1])
        self.dazed.bind(DGG.WITHOUT, self.hidePanel, extraArgs=[1])


















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
        self.luredText = None
        self.dazedText = None
        self.extraAttacksText = None
        self.soakedRoundsText = None
        self.vulnerabilityText = None
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
        self.status = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status3 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status4 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status5 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status6 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status7 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status8 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.attackIcon = self.status.find('**/default_background')  # first
        self.attackIcon.reparentTo(self.healthNode)
        self.attackIcon.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.attackIcon1 = self.status2.find('**/default_background')  # second
        self.attackIcon1.reparentTo(self.healthNode)
        self.attackIcon1.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.attackIcon2 = self.status3.find('**/default_background')  # third
        self.attackIcon2.reparentTo(self.healthNode)
        self.attackIcon2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.attackIcon3 = self.status4.find('**/default_background')  # fourth
        self.attackIcon3.reparentTo(self.healthNode)
        self.attackIcon3.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.attackIcon4 = self.status5.find('**/default_background')  # first upper
        self.attackIcon4.reparentTo(self.healthNode)
        self.attackIcon4.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
        self.attackIcon4.hide()
        self.attackIcon5 = self.status6.find('**/default_background')  # second upper
        self.attackIcon5.reparentTo(self.healthNode)
        self.attackIcon5.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
        self.attackIcon5.hide()
        self.attackIcon6 = self.status7.find('**/default_background')  # third upper
        self.attackIcon6.reparentTo(self.healthNode)
        self.attackIcon6.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
        self.attackIcon6.hide()
        self.attackIcon7 = self.status8.find('**/default_background')  # fourth upper
        self.attackIcon7.reparentTo(self.healthNode)
        self.attackIcon7.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
        self.attackIcon7.hide()
        self.enraged = None
        self.shielding = None
        self.enraged2 = None
        self.shielding2 = None
        self.enraged3 = None
        self.shielding3 = None
        self.overcharged = None
        self.overcharged2 = None
        self.lured = None
        self.luredCog = None
        self.luredCog2 = None
        self.luredCog3 = None
        self.luredCog4 = None
        self.luredManager = None
        self.luredManager2 = None
        self.insured = None
        self.insured2 = None
        self.insured3 = None
        self.insured4 = None
        self.damageUp = None
        self.damageUp2 = None
        self.damageUpMgr = None
        self.skeleton = None
        self.virtual = None
        self.immortal = None
        self.immortal2 = None
        self.immortal3 = None
        self.immortal4 = None
        self.vulnerable = None
        self.vulnerable2 = None
        self.vulnerable3 = None
        self.vulnerable4 = None
        self.soakResist = None
        self.soakResist2 = None
        self.soakResist3 = None
        self.soakResist4 = None
        self.syphon = None
        self.syphon2 = None
        self.syphon3 = None
        self.syphon4 = None
        self.absorbing = None
        self.absorbing2 = None
        self.absorbing3 = None
        self.absorbing4 = None
        self.damageReduction = None
        self.damageReduction2 = None
        self.damageReduction3 = None
        self.damageReduction4 = None
        self.lureImmune = None
        self.lureImmune2 = None
        self.lureImmune3 = None
        self.lureImmune4 = None
        self.yellow = None
        self.orange = None
        self.lightblue = None
        self.green = None
        self.blue = None
        self.red = None
        self.pink = None
        self.rainbow = None
        self.hollywoods = None
        self.sharkwatcher = None
        self.soaked = None
        self.dazed = None
        self.extraAttacks = None
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
        self.luredCogTest = None
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
        self.statusEffects = 0
        if self.luredText != None:
            self.luredText.removeNode()
        if self.damageMultText != None:
            self.damageMultText.removeNode()
        if self.extraAttacks != None:
            self.extraAttacks.removeNode()
        if self.sued != None:
            self.sued.removeNode()
        if self.suedRoundsText != None:
            self.suedRoundsText.removeNode()
        if self.extraAttacksText != None:
            self.extraAttacksText.removeNode()
        if self.dazed != None:
            self.dazed.removeNode()
        if self.dazedText != None:
            self.dazedText.removeNode()
        if self.enrageCountText != None:
            self.enrageCountText.removeNode()
        if self.soakedRoundsText != None:
            self.soakedRoundsText.removeNode()
        if self.soaked != None:
            self.soaked.removeNode()
        if self.enraged != None:
            self.enraged.removeNode()
        if self.dazed != None:
            self.dazed.removeNode()
        if self.soaked != None:
            self.soaked.removeNode()
        if self.extraAttacks != None:
            self.extraAttacks.removeNode()
        if self.enraged2 != None:
            self.enraged2.removeNode()
        if self.shielding != None:
            self.shielding.removeNode()
        if self.shielding2 != None:
            self.shielding2.removeNode()
        if self.skeleton != None:
            self.skeleton.removeNode()
        if self.virtual != None:
            self.virtual.removeNode()
        if self.shielding3 != None:
            self.shielding3.removeNode()
        if self.enraged3 != None:
            self.enraged3.removeNode()
        if self.damageUp != None:
            self.damageUp.removeNode()
        if self.damageUp2 != None:
            self.damageUp2.removeNode()
        if self.luredManager2 != None:
            self.luredManager2.removeNode()
        if self.damageUpMgr != None:
            self.damageUpMgr.removeNode()
        if self.overcharged2 != None:
            self.overcharged2.removeNode()
        if self.overcharged != None:
            self.overcharged.removeNode()
        if self.insured != None:
            self.insured.removeNode()
        if self.insured2 != None:
            self.insured2.removeNode()
        if self.insured3 != None:
            self.insured3.removeNode()
        if self.insured4 != None:
            self.insured4.removeNode()
        if self.overcharged != None:
            self.overcharged.removeNode()
        if self.overcharged2 != None:
            self.overcharged2.removeNode()
        if self.lured != None:
            self.lured.removeNode()
        if self.vulnerabilityText != None:
            self.vulnerabilityText.removeNode()
        if self.luredCog3 != None:
            self.luredCog3.removeNode()
        if self.luredCog4 != None:
            self.luredCog4.removeNode()
        if self.luredCog2 != None:
            self.luredCog2.removeNode()
        if self.luredCogTest != None:
            self.luredCogTest.removeNode()
        if self.rageBuildingText != None:
            self.rageBuildingText.removeNode()
        if self.immortal != None:
            self.immortal.removeNode()
        if self.immortal2 != None:
            self.immortal2.removeNode()
        if self.immortal3 != None:
            self.immortal3.removeNode()
        if self.immortal4 != None:
            self.immortal4.removeNode()
        if self.luredManager != None:
            self.luredManager.removeNode()
        if self.syphon != None:
            self.syphon.removeNode()
        if self.syphon2 != None:
            self.syphon2.removeNode()
        if self.syphon3 != None:
            self.syphon3.removeNode()
        if self.syphon4 != None:
            self.syphon4.removeNode()
        if self.vulnerable != None:
            self.vulnerable.removeNode()
        if self.vulnerable2 != None:
            self.vulnerable2.removeNode()
        if self.vulnerable3 != None:
            self.vulnerable3.removeNode()
        if self.vulnerable4 != None:
            self.vulnerable4.removeNode()
        if self.soakResist != None:
            self.soakResist.removeNode()
        if self.soakResist2 != None:
            self.soakResist2.removeNode()
        if self.soakResist3 != None:
            self.soakResist3.removeNode()
        if self.soakResist4 != None:
            self.soakResist4.removeNode()
        if self.absorbing != None:
            self.absorbing.removeNode()
        if self.absorbing2 != None:
            self.absorbing2.removeNode()
        if self.absorbing3 != None:
            self.absorbing3.removeNode()
        if self.absorbing4 != None:
            self.absorbing4.removeNode()
        if self.damageReduction != None:
            self.damageReduction.removeNode()
        if self.damageReduction2 != None:
            self.damageReduction2.removeNode()
        if self.damageReduction3 != None:
            self.damageReduction3.removeNode()
        if self.damageReduction4 != None:
            self.damageReduction4.removeNode()
        if self.lureImmune != None:
            self.lureImmune.removeNode()
        if self.lureImmune2 != None:
            self.lureImmune2.removeNode()
        if self.lureImmune3 != None:
            self.lureImmune3.removeNode()
        if self.lureImmune4 != None:
            self.lureImmune4.removeNode()
        if self.yellow != None:
            self.yellow.removeNode()
        if self.orange != None:
            self.orange.removeNode()
        if self.lightblue != None:
            self.lightblue.removeNode()
        if self.green != None:
            self.green.removeNode()
        if self.blue != None:
            self.blue.removeNode()
        if self.red != None:
            self.red.removeNode()
        if self.pink != None:
            self.pink.removeNode()
        if self.rainbow != None:
            self.rainbow.removeNode()
        if self.hollywoods != None:
            self.hollywoods.removeNode()
        if self.sharkwatcher != None:
            self.sharkwatcher.removeNode()
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
        if self.cog.extraAttack:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/extra_attacks_icon')
            self.extraAttacksText = DirectLabel(parent=self.extraAttacks, relief=None, text="+%s" % self.cog.getExtraAttacks(),
                                                text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.extraAttacksText.show()
            if self.statusEffects == 1:
                self.extraAttacks.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0.973, 1, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.extraAttacks.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0.973, 1, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.extraAttacks.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0.973, 1, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.extraAttacks.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0.973, 1, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.extraAttacks.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0.973, 1, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.extraAttacks.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0.973, 1, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.extraAttacks.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0.973, 1, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.extraAttacks.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0.973, 1, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isSued:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.sued = status.find('**/sued_icon')
            self.suedRoundsText = DirectLabel(parent=self.sued, relief=None, text="%s" % self.cog.getSuedRounds(),
                                         text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.suedRoundsText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.sued.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.sued.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.sued.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.sued.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.sued.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.sued.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.sued.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.sued.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.sued.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.sued.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.sued.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.sued.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.sued.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.sued.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.sued.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.sued.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isSoaked:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.soaked = status.find('**/scope_creep_icon')
            self.soakedRoundsText = DirectLabel(parent=self.soaked, relief=None, text="%s" % self.cog.getSoakRounds(),
                                         text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.soakedRoundsText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.soaked.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.soaked.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.soaked.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.soaked.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.soaked.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.soaked.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.soaked.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.soaked.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.soaked.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.soaked.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.soaked.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.soaked.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.soaked.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.soaked.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.soaked.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.soaked.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.dna.name == 'phouse':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/pyromaniac_icon')
            self.extraAttacks.reparentTo(self.healthNode)
            self.extraAttacks.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.extraAttacks, relief=None,
                                                text="%s" % self.cog.getPowerhouseRotation() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.rageBuildingText.show()
        if self.cog.isDazed:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.dazed = status.find('**/confusion_icon')
            self.dazed.reparentTo(self.healthNode)
            self.dazed.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
            self.dazedText = DirectLabel(parent=self.dazed, relief=None,
                                                text="1",
                                                text_fg=(1, 1, 1, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.dazedText.show()
        if self.cog.isImmortal and self.cog.isDamageUp and self.cog.dna.name == 'videog':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.hollywoods = status.find('**/marked_icon')
            self.hollywoods.reparentTo(self.healthNode)
            self.hollywoods.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
            # self.absorbing3.show()
        elif self.cog.isImmortal and self.cog.dna.name == 'videog':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.hollywoods = status.find('**/marked_icon')
            self.hollywoods.reparentTo(self.healthNode)
            self.hollywoods.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            #self.absorbing3.show()
        elif self.cog.isImmortal and self.cog.dna.name == 'hroller':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            #self.absorbing3.show()
        elif self.cog.dna.name == 'hroller':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hroller2' and self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hroller2' and self.cog.isPhase3:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.rainbow = status.find('**/harmonious_colors_icon')
            self.rainbow.reparentTo(self.healthNode)
            self.rainbow.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hroller2':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.hollywoods = status.find('**/marked_icon')
            self.hollywoods.reparentTo(self.healthNode)
            self.hollywoods.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hrollers' and self.cog.healthCondition == 13 and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune4 = status.find('**/cashback_icon')  # 4 slot lure immune
            self.lureImmune4.reparentTo(self.healthNode)
            self.lureImmune4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hrollers' and self.cog.healthCondition == 13:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune4 = status.find('**/cashback_icon')  # 4 slot lure immune
            self.lureImmune4.reparentTo(self.healthNode)
            self.lureImmune4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 34 and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 34:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 33 and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal2 = status.find('**/unite_cooldown_icon')  # third slot immunity icon
            self.immortal2.reparentTo(self.healthNode)
            self.immortal2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 33:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal2 = status.find('**/unite_cooldown_icon')  # third slot immunity icon
            self.immortal2.reparentTo(self.healthNode)
            self.immortal2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 32 and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune3 = status.find('**/cashback_icon')  # 3 slot lure immune
            self.lureImmune3.reparentTo(self.healthNode)
            self.lureImmune3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 32:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune3 = status.find('**/cashback_icon')  # 3 slot lure immune
            self.lureImmune3.reparentTo(self.healthNode)
            self.lureImmune3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 31 and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lightblue = status.find('**/duck_drop_icon')  # 3 slot lure immune
            self.lightblue.reparentTo(self.healthNode)
            self.lightblue.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 31:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lightblue = status.find('**/duck_drop_icon')  # 3 slot lure immune
            self.lightblue.reparentTo(self.healthNode)
            self.lightblue.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 30 and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.pink = status.find('**/brain_icon')  # 3 slot lure immune
            self.pink.reparentTo(self.healthNode)
            self.pink.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 30:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.pink = status.find('**/brain_icon')  # 3 slot lure immune
            self.pink.reparentTo(self.healthNode)
            self.pink.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 29 and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.red = status.find('**/trap_card_icon')  # 3 slot lure immune
            self.red.reparentTo(self.healthNode)
            self.red.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 29:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.red = status.find('**/trap_card_icon')  # 3 slot lure immune
            self.red.reparentTo(self.healthNode)
            self.red.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 28 and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.blue = status.find('**/singing_blues_icon')  # 3 slot lure immune
            self.blue.reparentTo(self.healthNode)
            self.blue.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 28:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.blue = status.find('**/singing_blues_icon')  # 3 slot lure immune
            self.blue.reparentTo(self.healthNode)
            self.blue.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 27 and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.yellow = status.find('**/fizzle_icon')  # 3 slot lure immune
            self.yellow.reparentTo(self.healthNode)
            self.yellow.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 27:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.yellow = status.find('**/fizzle_icon')  # 3 slot lure immune
            self.yellow.reparentTo(self.healthNode)
            self.yellow.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 26 and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.orange = status.find('**/full_deck_icon')  # 3 slot lure immune
            self.orange.reparentTo(self.healthNode)
            self.orange.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.dna.name == 'hrollers' and self.cog.getActualLevel() == 26:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.orange = status.find('**/full_deck_icon')  # 3 slot lure immune
            self.orange.reparentTo(self.healthNode)
            self.orange.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.dna.name == 'hrollers' and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.green = status.find('**/no_green_light_icon')  # 3 slot lure immune
            self.green.reparentTo(self.healthNode)
            self.green.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.dna.name == 'hrollers':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.green = status.find('**/no_green_light_icon')  # 3 slot lure immune
            self.green.reparentTo(self.healthNode)
            self.green.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isVirtual and self.cog.isImmortal:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/worker_management_icon')  # second slot immunity icon
            self.immortal.reparentTo(self.healthNode)
            self.immortal.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal2 = status.find('**/unite_cooldown_icon')  # third slot immunity icon
            self.immortal2.reparentTo(self.healthNode)
            self.immortal2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal4 = status.find('**/focused_defense_icon')  # fourth slot immunity icon
            self.immortal4.reparentTo(self.healthNode)
            self.immortal4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.isSkeleton and self.cog.isImmortal:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/worker_management_icon')  # second slot immunity icon
            self.immortal.reparentTo(self.healthNode)
            self.immortal.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal2 = status.find('**/unite_cooldown_icon')  # third slot immunity icon
            self.immortal2.reparentTo(self.healthNode)
            self.immortal2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal4 = status.find('**/focused_defense_icon')  # fourth slot immunity icon
            self.immortal4.reparentTo(self.healthNode)
            self.immortal4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.isImmortal:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/worker_management_icon')  # second slot immunity icon
            self.immortal.reparentTo(self.healthNode)
            self.immortal.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal2 = status.find('**/unite_cooldown_icon')  # third slot immunity icon
            self.immortal2.reparentTo(self.healthNode)
            self.immortal2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal4 = status.find('**/focused_defense_icon')  # fourth slot immunity icon
            self.immortal4.reparentTo(self.healthNode)
            self.immortal4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.dna.name == 'sgoat' and self.cog.isAngry:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged3 = status.find('**/rage_mode_icon')  # fourth slot enraged
            self.enraged3.reparentTo(self.healthNode)
            self.enraged3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.enrageCountText = DirectLabel(parent=self.enraged3, relief=None,
                                              text="%s" % self.cog.getEnrageCounter(), text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.enrageCountText.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.dna.name == 'sgoat' and self.cog.isAngry:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged3 = status.find('**/rage_mode_icon')  # fourth slot enraged
            self.enraged3.reparentTo(self.healthNode)
            self.enraged3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.enrageCountText = DirectLabel(parent=self.enraged3, relief=None,
                                               text="%s" % self.cog.getEnrageCounter(), text_fg=(1, 1, 1, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.5)
            self.enrageCountText.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.dna.name == 'sgoat' and self.cog.isShielding:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding3 = status.find('**/defense_mode_icon')  # fourth slot defense
            self.shielding3.reparentTo(self.healthNode)
            self.shielding3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.dna.name == 'sgoat' and self.cog.isShielding:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding3 = status.find('**/defense_mode_icon')  # fourth slot defense
            self.shielding3.reparentTo(self.healthNode)
            self.shielding3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and not self.cog.getManager() and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon4 = status.find('**/ink_drain_icon')  # 4 slot soak syphon icon
            self.syphon4.reparentTo(self.healthNode)
            self.syphon4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and not self.cog.getManager() and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and not self.cog.getManager() and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isInsured and not self.cog.getManager():
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured3 = status.find('**/insured_icon')
            self.insured3.reparentTo(self.healthNode)
            self.insured3.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)  # 4th slot insurance
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and not self.cog.getManager():
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon4 = status.find('**/ink_drain_icon')  # 4 slot soak syphon icon
            self.syphon4.reparentTo(self.healthNode)
            self.syphon4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isLureImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.lureImmune4.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isShielding:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing4 = status.find('**/damage_absorb_icon')  # 4 slot absorb icon
            self.absorbing4.reparentTo(self.healthNode)
            self.absorbing4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon4 = status.find('**/ink_drain_icon')  # 4 slot soak syphon icon
            self.syphon4.reparentTo(self.healthNode)
            self.syphon4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resistv
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None,  text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable4 = status.find('**/broken_shield_icon')  # fourth slot vulnerability icon
            self.vulnerable4.reparentTo(self.healthNode)
            self.vulnerable4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable4, relief=None,
                                              text="%s" % self.cog.getVulnerability() + "%", text_fg=(0, 1, 0.047, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.vulnerabilityText.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.healthCondition == 13 and self.cog.isVirtual:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isInsured and not self.cog.getManager():
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured3 = status.find('**/insured_icon')
            self.insured3.reparentTo(self.healthNode)
            self.insured3.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)  # 4th slot insurance
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and not self.cog.getManager() and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon4 = status.find('**/ink_drain_icon')  # 4 slot soak syphon icon
            self.syphon4.reparentTo(self.healthNode)
            self.syphon4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and not self.cog.getManager() and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and not self.cog.getManager() and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and not self.cog.getManager():
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon4 = status.find('**/ink_drain_icon')  # 4 slot soak syphon icon
            self.syphon4.reparentTo(self.healthNode)
            self.syphon4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isLureImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune4 = status.find('**/cashback_icon')  # 4 slot lure immune
            self.lureImmune4.reparentTo(self.healthNode)
            self.lureImmune4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isShielding:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing4 = status.find('**/damage_absorb_icon')  # 4 slot absorb icon
            self.absorbing4.reparentTo(self.healthNode)
            self.absorbing4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon4 = status.find('**/ink_drain_icon')  # 4 slot soak syphon icon
            self.syphon4.reparentTo(self.healthNode)
            self.syphon4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable4 = status.find('**/broken_shield_icon')  # fourth slot vulnerability icon
            self.vulnerable4.reparentTo(self.healthNode)
            self.vulnerable4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable4, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.healthCondition == 13 and self.cog.isSkeleton:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged2 = status.find('**/overcharge_icon')  # third slot overcharge
            self.overcharged2.reparentTo(self.healthNode)
            self.overcharged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and not self.cog.getManager() and self.cog.isSyphon and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and not self.cog.getManager() and self.cog.isInsured and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and self.cog.isInsured and not self.cog.getManager():
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
        elif self.cog.healthCondition == 13 and not self.cog.getManager() and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and not self.cog.getManager() and self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
        elif self.cog.healthCondition == 13 and not self.cog.getManager() and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and not self.cog.getManager():
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isSyphon and self.cog.isLureImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune4 = status.find('**/cashback_icon')  # 4 slot lure immune
            self.lureImmune4.reparentTo(self.healthNode)
            self.lureImmune4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isSyphon and self.cog.isShielding:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing4 = status.find('**/damage_absorb_icon')  # 4 slot absorb icon
            self.absorbing4.reparentTo(self.healthNode)
            self.absorbing4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isSyphon and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.healthCondition == 13 and self.cog.isVulnerable and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.healthCondition == 13 and self.cog.isSyphon and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and self.cog.isVulnerable and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
        elif self.cog.healthCondition == 13 and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isLureImmune and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune3 = status.find('**/cashback_icon')  # 3 slot lure immune
            self.lureImmune3.reparentTo(self.healthNode)
            self.lureImmune3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.healthCondition == 13 and self.cog.isShielding and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing3 = status.find('**/damage_absorb_icon')  # 3 slot absorb icon
            self.absorbing3.reparentTo(self.healthNode)
            self.absorbing3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.healthCondition == 13 and self.cog.isLureImmune and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune3 = status.find('**/cashback_icon')  # 3 slot lure immune
            self.lureImmune3.reparentTo(self.healthNode)
            self.lureImmune3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and self.cog.isShielding and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing3 = status.find('**/damage_absorb_icon')  # 3 slot absorb icon
            self.absorbing3.reparentTo(self.healthNode)
            self.absorbing3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and self.cog.isSyphon and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and self.cog.isSoakImmune and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.soakResist3 = status.find('**/soaked_icon')  # 3 slot soak resist icon
            self.soakResist3.reparentTo(self.healthNode)
            self.soakResist3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13 and self.cog.isLured and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.healthCondition == 13 and self.cog.isSoakImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.soakResist3 = status.find('**/soaked_icon')  # 3 slot soak resist icon
            self.soakResist3.reparentTo(self.healthNode)
            self.soakResist3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isLureImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune3 = status.find('**/cashback_icon')  # 3 slot lure immune
            self.lureImmune3.reparentTo(self.healthNode)
            self.lureImmune3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isShielding:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing3 = status.find('**/damage_absorb_icon')  # 3 slot absorb icon
            self.absorbing3.reparentTo(self.healthNode)
            self.absorbing3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.healthCondition == 13 and self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
        elif self.cog.healthCondition == 13 and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.healthCondition == 13 and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.healthCondition == 13:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')  # second slot overcharge
            self.overcharged.reparentTo(self.healthNode)
            self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isVirtual and self.cog.dna.name == 'bcaster' and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isVirtual and self.cog.dna.name == 'bcaster':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
        elif self.cog.isVirtual and self.cog.dna.name == 'sgoat' and self.cog.isAngry and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged2 = status.find('**/rage_mode_icon')  # third slot enraged
            self.enraged2.reparentTo(self.healthNode)
            self.enraged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.enrageCountText = DirectLabel(parent=self.enraged2, relief=None,
                                               text="%s" % self.cog.getEnrageCounter(), text_fg=(1, 1, 1, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.5)
            self.enrageCountText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isVirtual and self.cog.dna.name == 'sgoat' and self.cog.isAngry and self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged2 = status.find('**/rage_mode_icon')  # third slot enraged
            self.enraged2.reparentTo(self.healthNode)
            self.enraged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.enrageCountText = DirectLabel(parent=self.enraged2, relief=None,
                                               text="%s" % self.cog.getEnrageCounter(), text_fg=(1, 1, 1, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.5)
            self.enrageCountText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured3 = status.find('**/insured_icon')
            self.insured3.reparentTo(self.healthNode)
            self.insured3.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)  # 4th slot insurance
        elif self.cog.isSkeleton and self.cog.dna.name == 'sgoat' and self.cog.isAngry and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged2 = status.find('**/rage_mode_icon')  # third slot enraged
            self.enraged2.reparentTo(self.healthNode)
            self.enraged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.enrageCountText = DirectLabel(parent=self.enraged2, relief=None,
                                               text="%s" % self.cog.getEnrageCounter(), text_fg=(1, 1, 1, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.5)
            self.enrageCountText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSkeleton and self.cog.dna.name == 'sgoat' and self.cog.isAngry:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged2 = status.find('**/rage_mode_icon')  # third slot enraged
            self.enraged2.reparentTo(self.healthNode)
            self.enraged2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.enrageCountText = DirectLabel(parent=self.enraged2, relief=None,
                                               text="%s" % self.cog.getEnrageCounter(), text_fg=(1, 1, 1, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.5)
            self.enrageCountText.show()
        elif self.cog.isVirtual and self.cog.dna.name == 'sgoat' and self.cog.isShielding and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding2 = status.find('**/defense_mode_icon')  # third slot defense
            self.shielding2.reparentTo(self.healthNode)
            self.shielding2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.shielding2, relief=None,
                                              text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.rageBuildingText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isVirtual and self.cog.dna.name == 'sgoat' and self.cog.isShielding and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding2 = status.find('**/defense_mode_icon')  # third slot defense
            self.shielding2.reparentTo(self.healthNode)
            self.shielding2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.shielding2, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.rageBuildingText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isVirtual and self.cog.dna.name == 'sgoat' and self.cog.isShielding:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding2 = status.find('**/defense_mode_icon')  # third slot defense
            self.shielding2.reparentTo(self.healthNode)
            self.shielding2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.shielding2, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.rageBuildingText.show()
        elif self.cog.isSkeleton and self.cog.dna.name == 'sgoat' and self.cog.isShielding and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding2 = status.find('**/defense_mode_icon')  # third slot defense
            self.shielding2.reparentTo(self.healthNode)
            self.shielding2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.shielding2, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.rageBuildingText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isSkeleton and self.cog.dna.name == 'sgoat' and self.cog.isShielding and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding2 = status.find('**/defense_mode_icon')  # third slot defense
            self.shielding2.reparentTo(self.healthNode)
            self.shielding2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.shielding2, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.rageBuildingText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSkeleton and self.cog.dna.name == 'sgoat' and self.cog.isShielding and self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding2 = status.find('**/defense_mode_icon')  # third slot defense
            self.shielding2.reparentTo(self.healthNode)
            self.shielding2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.shielding2, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.rageBuildingText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured4 = status.find('**/insured_icon')
            self.insured4.reparentTo(self.healthNode)
            self.insured4.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)  # 1st slot insurance
        elif self.cog.isSkeleton and self.cog.dna.name == 'sgoat' and self.cog.isShielding:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding2 = status.find('**/defense_mode_icon')  # third slot defense
            self.shielding2.reparentTo(self.healthNode)
            self.shielding2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.shielding2, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.rageBuildingText.show()
        elif self.cog.dna.name == 'sgoat' and self.cog.isShielding and self.cog.isDamageUp and self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding = status.find('**/defense_mode_icon')  # second slot defense
            self.shielding.reparentTo(self.healthNode)
            self.shielding.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.shielding, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.rageBuildingText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured3 = status.find('**/insured_icon')
            self.insured3.reparentTo(self.healthNode)
            self.insured3.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)  # 4th slot insurance
        elif self.cog.dna.name == 'sgoat' and self.cog.isShielding and self.cog.isDamageUp and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding = status.find('**/defense_mode_icon')  # second slot defense
            self.shielding.reparentTo(self.healthNode)
            self.shielding.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.shielding, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.rageBuildingText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(),
                                         text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None,
                                              text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.dna.name == 'sgoat' and self.cog.isShielding and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding = status.find('**/defense_mode_icon')  # second slot defense
            self.shielding.reparentTo(self.healthNode)
            self.shielding.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.shielding, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.rageBuildingText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.dna.name == 'sgoat' and self.cog.isShielding and self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding = status.find('**/defense_mode_icon')  # second slot defense
            self.shielding.reparentTo(self.healthNode)
            self.shielding.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.shielding, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.rageBuildingText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
        elif self.cog.dna.name == 'sgoat' and self.cog.isShielding and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding = status.find('**/defense_mode_icon')  # second slot defense
            self.shielding.reparentTo(self.healthNode)
            self.shielding.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.shielding, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.rageBuildingText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.dna.name == 'sgoat' and self.cog.isShielding:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.shielding = status.find('**/defense_mode_icon')  # second slot defense
            self.shielding.reparentTo(self.healthNode)
            self.shielding.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.rageBuildingText = DirectLabel(parent=self.shielding, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.rageBuildingText.show()
        elif self.cog.dna.name == 'sgoat' and self.cog.isAngry and self.cog.isDamageUp and self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/rage_mode_icon')  # second slot enraged
            self.enraged.reparentTo(self.healthNode)
            self.enraged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.enrageCountText = DirectLabel(parent=self.enraged, relief=None,
                                               text="%s" % self.cog.getEnrageCounter(), text_fg=(1, 1, 1, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.5)
            self.enrageCountText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured3 = status.find('**/insured_icon')
            self.insured3.reparentTo(self.healthNode)
            self.insured3.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)  # 4th slot insurance
        elif self.cog.dna.name == 'sgoat' and self.cog.isAngry and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/rage_mode_icon')  # second slot enraged
            self.enraged.reparentTo(self.healthNode)
            self.enraged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.enrageCountText = DirectLabel(parent=self.enraged, relief=None,
                                               text="%s" % self.cog.getEnrageCounter(), text_fg=(1, 1, 1, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.5)
            self.enrageCountText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.dna.name == 'sgoat' and self.cog.isAngry and self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/rage_mode_icon')  # second slot enraged
            self.enraged.reparentTo(self.healthNode)
            self.enraged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.enrageCountText = DirectLabel(parent=self.enraged, relief=None,
                                               text="%s" % self.cog.getEnrageCounter(), text_fg=(1, 1, 1, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.5)
            self.enrageCountText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
        elif self.cog.dna.name == 'sgoat' and self.cog.isAngry:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/rage_mode_icon')  # second slot enraged
            self.enraged.reparentTo(self.healthNode)
            self.enraged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.enrageCountText = DirectLabel(parent=self.enraged, relief=None,
                                               text="%s" % self.cog.getEnrageCounter(), text_fg=(1, 1, 1, 1),
                                               text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                               pos=(0.25, 0, -.5),
                                               text_scale=.5)
            self.enrageCountText.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isContracted and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isInsured and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isSyphon and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon2 = status.find('**/ink_drain_icon')  # 2 slot soak syphon icon
            self.syphon2.reparentTo(self.healthNode)
            self.syphon2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isSyphon and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon2 = status.find('**/ink_drain_icon')  # 2 slot soak syphon icon
            self.syphon2.reparentTo(self.healthNode)
            self.syphon2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isContracted:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon2 = status.find('**/ink_drain_icon')  # 2 slot soak syphon icon
            self.syphon2.reparentTo(self.healthNode)
            self.syphon2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isLured and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog2 = status.find('**/lured_icon')  # lure icon 2nd
            self.luredCog2.reparentTo(self.healthNode)
            self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog2, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog2 = status.find('**/lured_icon')  # lure icon 2nd
            self.luredCog2.reparentTo(self.healthNode)
            self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog2, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isVirtual and not self.cog.getManager() and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp = status.find('**/suit_damage_up_icon')  # second slot damage up
            self.damageUp.reparentTo(self.healthNode)
            self.damageUp.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isVirtual and not self.cog.getManager():
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.isVirtual and self.cog.isSyphon and self.cog.isLured and self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isVirtual and self.cog.isSyphon and self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
        elif self.cog.isVirtual and self.cog.isSyphon and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isVirtual and self.cog.isVulnerable and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isVirtual and self.cog.isVulnerable and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None,  text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isVirtual and self.cog.isSyphon and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isVirtual and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isVirtual and self.cog.isLureImmune and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune3 = status.find('**/cashback_icon')  # 3 slot lure immune
            self.lureImmune3.reparentTo(self.healthNode)
            self.lureImmune3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isVirtual and self.cog.isLureImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune3 = status.find('**/cashback_icon')  # 3 slot lure immune
            self.lureImmune3.reparentTo(self.healthNode)
            self.lureImmune3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isVirtual and self.cog.isShielding and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing3 = status.find('**/damage_absorb_icon')  # 3 slot absorb icon
            self.absorbing3.reparentTo(self.healthNode)
            self.absorbing3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isVirtual and self.cog.isShielding and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing3 = status.find('**/damage_absorb_icon')  # 3 slot absorb icon
            self.absorbing3.reparentTo(self.healthNode)
            self.absorbing3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.isVirtual and self.cog.isShielding:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing3 = status.find('**/damage_absorb_icon')  # 3 slot absorb icon
            self.absorbing3.reparentTo(self.healthNode)
            self.absorbing3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isVirtual and self.cog.isSyphon and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isVirtual and self.cog.isSyphon and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isVirtual and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isVirtual and self.cog.isDamageUp and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isVirtual and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isVirtual and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isVirtual:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.virtual.reparentTo(self.healthNode)
            self.virtual.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isSyphon and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon2 = status.find('**/ink_drain_icon')  # 2 slot soak syphon icon
            self.syphon2.reparentTo(self.healthNode)
            self.syphon2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isContracted and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isInsured and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isSyphon and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon2 = status.find('**/ink_drain_icon')  # 2 slot soak syphon icon
            self.syphon2.reparentTo(self.healthNode)
            self.syphon2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon2 = status.find('**/ink_drain_icon')  # 2 slot soak syphon icon
            self.syphon2.reparentTo(self.healthNode)
            self.syphon2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isLured and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog2 = status.find('**/lured_icon')  # lure icon 2nd
            self.luredCog2.reparentTo(self.healthNode)
            self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog2, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2,relief=None,  text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog2 = status.find('**/lured_icon')  # lure icon 2nd
            self.luredCog2.reparentTo(self.healthNode)
            self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog2, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isContracted:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isSkeleton and not self.cog.getManager() and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp = status.find('**/suit_damage_up_icon')  # second slot damage up
            self.damageUp.reparentTo(self.healthNode)
            self.damageUp.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSkeleton and not self.cog.getManager():
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif self.cog.isSkeleton and self.cog.isInsured and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSkeleton and self.cog.isSyphon and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isSkeleton and self.cog.isInsured and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredManager2.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isSkeleton and self.cog.isSyphon and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSkeleton and self.cog.isContracted:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
        elif self.cog.isSkeleton and self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
        elif self.cog.isSkeleton and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isSkeleton and self.cog.isVulnerable and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isSkeleton and self.cog.isVulnerable and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSkeleton and self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
        elif self.cog.isSkeleton and self.cog.isLureImmune and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune3 = status.find('**/cashback_icon')  # 3 slot lure immune
            self.lureImmune3.reparentTo(self.healthNode)
            self.lureImmune3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSkeleton and self.cog.isLureImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune3 = status.find('**/cashback_icon')  # 3 slot lure immune
            self.lureImmune3.reparentTo(self.healthNode)
            self.lureImmune3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isSkeleton and self.cog.isShielding and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing3 = status.find('**/damage_absorb_icon')  # 3 slot absorb icon
            self.absorbing3.reparentTo(self.healthNode)
            self.absorbing3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isSkeleton and self.cog.isShielding and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing3 = status.find('**/damage_absorb_icon')  # 3 slot absorb icon
            self.absorbing3.reparentTo(self.healthNode)
            self.absorbing3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSkeleton and self.cog.isShielding:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing3 = status.find('**/damage_absorb_icon')  # 3 slot absorb icon
            self.absorbing3.reparentTo(self.healthNode)
            self.absorbing3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isSkeleton and self.cog.isSyphon and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isSkeleton and self.cog.isSyphon and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSkeleton and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isSkeleton and self.cog.isDamageUp and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSkeleton and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSkeleton and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isSkeleton:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.skeleton.reparentTo(self.healthNode)
            self.skeleton.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager2 = status.find('**/lured_prestige_icon')  # lure resistance second slot
            self.luredManager2.reparentTo(self.healthNode)
            self.luredManager2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165,
                                              .165)  # second slot lure resist
        elif not self.cog.getManager() and self.cog.isContracted and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured4 = status.find('**/insured_icon')
            self.insured4.reparentTo(self.healthNode)
            self.insured4.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)  # 1st slot insurance
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog2 = status.find('**/lured_icon')  # lure icon 2nd
            self.luredCog2.reparentTo(self.healthNode)
            self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog2, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif not self.cog.getManager() and self.cog.isInsured and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured4 = status.find('**/insured_icon')
            self.insured4.reparentTo(self.healthNode)
            self.insured4.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)  # 1st slot insurance
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog2 = status.find('**/lured_icon')  # lure icon 2nd
            self.luredCog2.reparentTo(self.healthNode)
            self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog2, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif not self.cog.getManager() and self.cog.isSyphon and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon = status.find('**/ink_drain_icon')  # 1 slot soak syphon icon
            self.syphon.reparentTo(self.healthNode)
            self.syphon.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog2 = status.find('**/lured_icon')  # lure icon 2nd
            self.luredCog2.reparentTo(self.healthNode)
            self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog2, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif not self.cog.getManager() and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon = status.find('**/ink_drain_icon')  # 1 slot soak syphon icon
            self.syphon.reparentTo(self.healthNode)
            self.syphon.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        elif not self.cog.getManager() and self.cog.isLured and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog2 = status.find('**/lured_icon')  # lure icon 2nd
            self.luredCog2.reparentTo(self.healthNode)
            self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog2, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif not self.cog.getManager() and self.cog.isLured:
            status5 = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCogTest = status5.find('**/lured_icon')  # lure icon first
            self.luredCogTest.reparentTo(self.healthNode)
            self.luredCogTest.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCogTest, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif not self.cog.getManager() and self.cog.isContracted:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured4 = status.find('**/insured_icon')
            self.insured4.reparentTo(self.healthNode)
            self.insured4.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)  # 1st slot insurance
        elif not self.cog.getManager() and self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured4 = status.find('**/insured_icon')
            self.insured4.reparentTo(self.healthNode)
            self.insured4.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)  # 1st slot insurance
        elif self.cog.isLureImmune and self.cog.isSyphon and self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon = status.find('**/ink_drain_icon')  # 1 slot soak syphon icon
            self.syphon.reparentTo(self.healthNode)
            self.syphon.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune2 = status.find('**/cashback_icon')  # 2 slot lure immune
            self.lureImmune2.reparentTo(self.healthNode)
            self.lureImmune2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isShielding and self.cog.isSyphon and self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon = status.find('**/ink_drain_icon')  # 1 slot soak syphon icon
            self.syphon.reparentTo(self.healthNode)
            self.syphon.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing2 = status.find('**/damage_absorb_icon')  # 2 slot absorb icon
            self.absorbing2.reparentTo(self.healthNode)
            self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None,
                                              text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSoakImmune and self.cog.isSyphon and self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon = status.find('**/ink_drain_icon')  # 1 slot soak syphon icon
            self.syphon.reparentTo(self.healthNode)
            self.syphon.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.soakResist2 = status.find('**/soaked_icon')  # 2 slot soak resist icon
            self.soakResist2.reparentTo(self.healthNode)
            self.soakResist2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSyphon and self.cog.isLured and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon2 = status.find('**/ink_drain_icon')  # 2 slot soak syphon icon
            self.syphon2.reparentTo(self.healthNode)
            self.syphon2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSyphon and self.cog.isDamageUp and self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon2 = status.find('**/ink_drain_icon')  # 2 slot soak syphon icon
            self.syphon2.reparentTo(self.healthNode)
            self.syphon2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable3 = status.find('**/broken_shield_icon')  # third slot vulnerability icon
            self.vulnerable3.reparentTo(self.healthNode)
            self.vulnerable3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable3, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isLureImmune and self.cog.isDamageUp and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune2 = status.find('**/cashback_icon')  # 2 slot lure immune
            self.lureImmune2.reparentTo(self.healthNode)
            self.lureImmune2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isShielding and self.cog.isDamageUp and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing2 = status.find('**/damage_absorb_icon')  # 2 slot absorb icon
            self.absorbing2.reparentTo(self.healthNode)
            self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSoakImmune and self.cog.isDamageUp and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.soakResist2 = status.find('**/soaked_icon')  # 2 slot soak resist icon
            self.soakResist2.reparentTo(self.healthNode)
            self.soakResist2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isDamageUp and self.cog.isLured and self.cog.isContracted:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog2 = status.find('**/lured_icon')  # lure icon 2nd
            self.luredCog2.reparentTo(self.healthNode)
            self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog2, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured3 = status.find('**/insured_icon')
            self.insured3.reparentTo(self.healthNode)
            self.insured3.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)  # 4th slot insurance
        elif self.cog.isDamageUp and self.cog.isLured and self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog2 = status.find('**/lured_icon')  # lure icon 2nd
            self.luredCog2.reparentTo(self.healthNode)
            self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog2, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                          text_font=getSignFont(),text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured3 = status.find('**/insured_icon')
            self.insured3.reparentTo(self.healthNode)
            self.insured3.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)  # 4th slot insurance
        elif self.cog.isContracted and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isInsured and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isSoakImmune and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.soakResist2 = status.find('**/soaked_icon')  # 2 slot soak resist icon
            self.soakResist2.reparentTo(self.healthNode)
            self.soakResist2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isLureImmune and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune2 = status.find('**/cashback_icon')  # 2 slot lure immune
            self.lureImmune2.reparentTo(self.healthNode)
            self.lureImmune2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isShielding and self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing2 = status.find('**/damage_absorb_icon')  # 2 slot absorb icon
            self.absorbing2.reparentTo(self.healthNode)
            self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon3 = status.find('**/ink_drain_icon')  # 3 slot soak syphon icon
            self.syphon3.reparentTo(self.healthNode)
            self.syphon3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isSyphon and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon2 = status.find('**/ink_drain_icon')  # 2 slot soak syphon icon
            self.syphon2.reparentTo(self.healthNode)
            self.syphon2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isSyphon and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon2 = status.find('**/ink_drain_icon')  # 2 slot soak syphon icon
            self.syphon2.reparentTo(self.healthNode)
            self.syphon2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isVulnerable and self.cog.isLured and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable2 = status.find('**/broken_shield_icon')  # second slot vulnerability icon
            self.vulnerable2.reparentTo(self.healthNode)
            self.vulnerable2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable2, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isVulnerable and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable2 = status.find('**/broken_shield_icon')  # second slot vulnerability icon
            self.vulnerable2.reparentTo(self.healthNode)
            self.vulnerable2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable2, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isVulnerable and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable2 = status.find('**/broken_shield_icon')  # second slot vulnerability icon
            self.vulnerable2.reparentTo(self.healthNode)
            self.vulnerable2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable2, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon2 = status.find('**/ink_drain_icon')  # 2 slot soak syphon icon
            self.syphon2.reparentTo(self.healthNode)
            self.syphon2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.vulnerable2 = status.find('**/broken_shield_icon')  # second slot vulnerability icon
            self.vulnerable2.reparentTo(self.healthNode)
            self.vulnerable2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.vulnerabilityText = DirectLabel(parent=self.vulnerable2, relief=None,
                                                 text="%s" % self.cog.getVulnerability() + "%",
                                                 text_fg=(0, 1, 0.047, 1),
                                                 text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                 pos=(0.25, 0, -.5),
                                                 text_scale=.5)
            self.vulnerabilityText.show()
        elif self.cog.isSoakImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.soakResist2 = status.find('**/soaked_icon')  # 2 slot soak resist icon
            self.soakResist2.reparentTo(self.healthNode)
            self.soakResist2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isShielding and self.cog.isContracted and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing2 = status.find('**/damage_absorb_icon')  # 2 slot absorb icon
            self.absorbing2.reparentTo(self.healthNode)
            self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isShielding and self.cog.isInsured and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing2 = status.find('**/damage_absorb_icon')  # 2 slot absorb icon
            self.absorbing2.reparentTo(self.healthNode)
            self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUpMgr = status.find('**/suit_damage_up_icon')  # 4th slot damage up
            self.damageUpMgr.reparentTo(self.healthNode)
            self.damageUpMgr.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUpMgr, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isInsured and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')  # second slot insurance
            self.insured.reparentTo(self.healthNode)
            self.insured.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isLureImmune and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune2 = status.find('**/cashback_icon')  # 2 slot lure immune
            self.lureImmune2.reparentTo(self.healthNode)
            self.lureImmune2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isLureImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune2 = status.find('**/cashback_icon')  # 2 slot lure immune
            self.lureImmune2.reparentTo(self.healthNode)
            self.lureImmune2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isShielding and self.cog.isContracted and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing2 = status.find('**/damage_absorb_icon')  # 2 slot absorb icon
            self.absorbing2.reparentTo(self.healthNode)
            self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isShielding and self.cog.isInsured and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing2 = status.find('**/damage_absorb_icon')  # 2 slot absorb icon
            self.absorbing2.reparentTo(self.healthNode)
            self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog4 = status.find('**/lured_icon')  # lure icon 4th
            self.luredCog4.reparentTo(self.healthNode)
            self.luredCog4.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog4, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isShielding and self.cog.isContracted:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing2 = status.find('**/damage_absorb_icon')  # 2 slot absorb icon
            self.absorbing2.reparentTo(self.healthNode)
            self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
        elif self.cog.isShielding and self.cog.isInsured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing2 = status.find('**/damage_absorb_icon')  # 2 slot absorb icon
            self.absorbing2.reparentTo(self.healthNode)
            self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured2 = status.find('**/insured_icon')
            self.insured2.reparentTo(self.healthNode)
            self.insured2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)  # third slot insurance
        elif self.cog.isShielding and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing2 = status.find('**/damage_absorb_icon')  # 2 slot absorb icon
            self.absorbing2.reparentTo(self.healthNode)
            self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog3 = status.find('**/lured_icon')  # lure icon 3rd
            self.luredCog3.reparentTo(self.healthNode)
            self.luredCog3.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog3, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
        elif self.cog.isShielding and self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing2 = status.find('**/damage_absorb_icon')  # 2 slot absorb icon
            self.absorbing2.reparentTo(self.healthNode)
            self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isShielding:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing2 = status.find('**/damage_absorb_icon')  # 2 slot absorb icon
            self.absorbing2.reparentTo(self.healthNode)
            self.absorbing2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        elif self.cog.isDamageUp and self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog2 = status.find('**/lured_icon')  # lure icon 2nd
            self.luredCog2.reparentTo(self.healthNode)
            self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog2, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp2 = status.find('**/suit_damage_up_icon')  # third slot damage up
            self.damageUp2.reparentTo(self.healthNode)
            self.damageUp2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp2, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp = status.find('**/suit_damage_up_icon')  # second slot damage up
            self.damageUp.reparentTo(self.healthNode)
            self.damageUp.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.damageMultText = DirectLabel(parent=self.damageUp, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
        elif self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog2 = status.find('**/lured_icon')  # lure icon 2nd
            self.luredCog2.reparentTo(self.healthNode)
            self.luredCog2.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
            self.luredText = DirectLabel(parent=self.luredCog2, relief=None, text="%s" % self.cog.getLuredRounds(), text_fg=(1, 1, 1, 1),
                                             text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0), pos=(0.25, 0, -.5),
                                             text_scale=.5)
            self.luredText.show()
        elif self.cog.getManager():
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')  # lure resistance manager first slot
            self.luredManager.reparentTo(self.healthNode)
            self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.healthText['text'] = t

    def updateHealthBar(self):
        self.setLevelText()
        condition = self.cog.healthCondition
        if self.cog.getHP() >= 0:
            self.hp = self.cog.getHP()
        else:
            self.hp = 0
        self.maxHp = self.cog.getMaxHP()
        if condition == 9:
            taskMgr.remove(self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
                taskMgr.remove(self.uniqueName('blink-task2'))
        elif condition == 10:
            taskMgr.remove(self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task2'))
        elif condition == 11:
            taskMgr.remove(self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.uniqueName('blink-task2'))
        elif condition == 13:
            taskMgr.remove(self.uniqueName('blink-task2'))
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
                blinkTask = Task.loop(Task(self.__blinkPurple), Task.pause(1.5), Task(self.__blinkPurpleColor),
                                      Task.pause(1.5))
                taskMgr.add(blinkTask, self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(1, 1, 1, 1.0)
        else:
            taskMgr.remove(self.uniqueName('blink-task'))
            if self.healthBar2:
                self.healthBar2.setProp('barColor', self.healthColors[condition])
                self.healthBar2.setProp('value', self.cog.getHP())
                taskMgr.remove(self.uniqueName('blink-task2'))
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1.0)
        if self.cog.isImmortal:
            self.hpText['text'] = str(self.hp)
        else:
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
        if name == 'bfh2':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -90, 0, 0, .105, .105, .105)
        elif name == 'ls':
            self.suitHead.setPosHprScale(-0.26, 0.5, 0.12, -90, 0, 0, .085, .085, .085)
        elif name == 'mg':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .115, .115, .115)
        elif name == 'whistleb':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .08, .08, .08)
        elif name == 'ksp':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .09, .09, .09)
        elif name == 'ppl':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .095, .095, .095)
        elif name == 'stenog':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0725, .0725, .0725)
        elif name == 'clubpres':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .105, .105, .105)
        elif name == 'fmaker':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .105, .105, .105)
        elif name == 'director':
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
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.135, -180, 0, 0, .06, .06, .06)
        elif name == 'le':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.135, -180, 0, 0, .115, .115, .115)
        elif name == 'bgh':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.135, -180, 0, 0, .1, .1, .1)
        elif name == 'cv':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .075, .075, .075)
        elif name == 'm' or name == 'tf' or name == 'mdm':
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
        elif name == 'mh' or name == 'ym' or name == 'chairp' or name == 'std2' or name == 'bsht' or name == 'std' or name == 'enf' or name == 'rb' or name == 'mh2' or name == 'trs' or name == 'cnd' or name == 'vpr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .105, .105, .105)
        elif name == 'dc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .11, .11, .11)
        elif name == 'pyc':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .13, .13, .13)
        elif name == 'gms':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .095, .095, .095)
        elif name == 'ms' or name == 'inw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .085, .085, .085)
        elif name == 'fct':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .12, .12, .12)
        elif name == 'fcs':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .09, .09, .09)
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
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .08, .08, .08)
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
        elif name == 'f' or name == 'cr' or name == 'ca' or name == 'skd' or name == 'tw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .175, .175, .175)
        elif name == 'nc' or name == 'nd' or name == 'sfs':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .08, .08, .08)
        elif name == 'txl':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .085, .085, .085)
        elif name == 'derrman':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .095, .095, .095)
        elif name == 'treek':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .075, .075, .075)
        elif name == 'pcrat':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .085, .085, .085)
        elif name == 'dopa':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .095, .095, .095)
        elif name == 'dopr':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .17, .17, .17)
        elif name == 'fires':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .07, .07, .07)
        elif name == 'ovt' or name == 'watchm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1, .1, .1)
        elif name == 'mplayer' or name == 'mplayer2':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .08, .08, .08)
        elif name == 'chainsaw' or name == 'chainsaw2':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0875, .0875, .0875)
        elif name == 'duckshfl':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .075, .075, .075)
        elif name == 'bellring':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.095, -180, 0, 0, .08, .08, .08)
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
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.145, -180, 0, 0, .08, .08, .08)
        elif name == 'redd':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.145, -180, 0, 0, .08, .08, .08)
        elif name == 'chairman':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .095, .095, .095)
        elif name == 'safesupervis' or name == 'dold':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .08, .08, .08)
        elif name == 'mslacker' or name == 'videog' or name == 'bcaster':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .06, .06, .06)
        elif name == 'wsi' or name == 'maudit' or name == 'kerberos' or name == 'charon' or name == 'bdirector' or name == 'sya' or name == 'pbl' or name == 'foreman':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .12, .12, .12)
        elif name == 'shw':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .00001, .00001, .00001)
        elif name == 'autocad':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.105, -180, 0, 0, .125, .125, .125)
        elif name == 'hydra' or name == 'styx' or name == 'supervis':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .3, .3, .3)
        elif name == 'clerk' or name == 'ant' or name == 'nix' or name == 'jls':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .2, .2, .2)
        elif name == 'judy':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .1, .1, .1)
        elif name == 'bf':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.14, -180, 0, 0, .11, .11, .11)
        elif name == 'whunter':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.115, -180, 0, 0, .0575, .0575, .0575)
        elif name == 'rainmake':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.155, -180, 0, 0, .07, .07, .07)
        elif name == 'erfit' or name == 'erclaim':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.13, -180, 0, 0, .075, .075, .075)
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
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.1, -180, 0, 0, .095, .095, .095)
        elif name == 'psetter':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .105, .105, .105)
        elif name == 'gld':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1075, .1075, .1075)
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
        del self.status
        del self.status2
        del self.status3
        del self.status4
        del self.status5
        del self.status6
        del self.status7
        del self.status8
        del self.attackIcon
        del self.attackIcon1
        del self.attackIcon2
        del self.attackIcon3
        del self.attackIcon4
        del self.attackIcon5
        del self.attackIcon6
        del self.attackIcon7
        del self.healthNode
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
