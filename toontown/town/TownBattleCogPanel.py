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
        self.enraged = None
        self.shielding = None
        self.overcharged = None
        self.luredCog = None
        self.luredManager = None
        self.status8 = None
        self.statusFrame = None
        self.statusFramePanel = None
        self.insured = None
        self.damageUp = None
        self.skeleton = None
        self.virtual = None
        self.immortal = None
        self.vulnerable = None
        self.soakResist = None
        self.syphon = None
        self.absorbing = None
        self.damageReduction = None
        self.zapped = None
        self.status = None
        self.marked = None
        self.sued2 = None
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
        self.lureImmune = None
        self.rainbow = None
        self.hollywoods = None
        self.sharkwatcher = None
        self.soaked = None
        self.dazed = None
        self.pulseTask = None
        self.extraAttacks = None
        self.setScale(0.525)
        self.button = button
        self.head = None
        self.suitHead = None
        self.blinkTask = None
        self.luredCogTest = None
        self.statusText1 = None
        self.statusText2 = None
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
        taskMgr.remove(self.uniqueName('overcharge-pulse-task'))
        self.statusEffects = 0
        if self.attackIcon != None:
            self.attackIcon.removeNode()
        if self.pulseTask != None:
            self.pulseTask.finish()
            del self.pulseTask
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
        if self.statusFrame != None:
            self.statusFrame.removeNode()
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
        self.status = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status2 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status3 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status4 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status5 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status6 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status7 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.status8 = loader.loadModel('phase_3.5/models/gui/status_effects')
        self.attackIcon7 = self.status8.find('**/default_background')  # fourth upper
        self.attackIcon7.reparentTo(self.healthNode)
        self.attackIcon7.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
        self.attackIcon7.hide()
        self.attackIcon6 = self.status7.find('**/default_background')  # third upper
        self.attackIcon6.reparentTo(self.healthNode)
        self.attackIcon6.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
        self.attackIcon6.hide()
        self.attackIcon5 = self.status6.find('**/default_background')  # second upper
        self.attackIcon5.reparentTo(self.healthNode)
        self.attackIcon5.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
        self.attackIcon5.hide()
        self.attackIcon4 = self.status5.find('**/default_background')  # first upper
        self.attackIcon4.reparentTo(self.healthNode)
        self.attackIcon4.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
        self.attackIcon4.hide()
        self.attackIcon3 = self.status4.find('**/default_background')  # fourth
        self.attackIcon3.reparentTo(self.healthNode)
        self.attackIcon3.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.attackIcon2 = self.status3.find('**/default_background')  # third
        self.attackIcon2.reparentTo(self.healthNode)
        self.attackIcon2.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.attackIcon1 = self.status2.find('**/default_background')  # second
        self.attackIcon1.reparentTo(self.healthNode)
        self.attackIcon1.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
        self.attackIcon = self.status.find('**/default_background')  # first
        self.attackIcon.reparentTo(self.healthNode)
        self.attackIcon.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
        self.attackIcon.setColor(1, 1, 1, 1)
        self.attackIcon1.setColor(1, 1, 1, 1)
        self.attackIcon2.setColor(1, 1, 1, 1)
        self.attackIcon3.setColor(1, 1, 1, 1)
        self.attackIcon4.setColor(1, 1, 1, 1)
        self.attackIcon5.setColor(1, 1, 1, 1)
        self.attackIcon6.setColor(1, 1, 1, 1)
        self.attackIcon7.setColor(1, 1, 1, 1)
        if self.luredText != None:
            self.luredText.removeNode()
        if self.damageMultText != None:
            self.damageMultText.removeNode()
        if self.damageMultText2 != None:
            self.damageMultText2.removeNode()
        if self.extraAttacks != None:
            self.extraAttacks.removeNode()
        if self.sued != None:
            self.sued.removeNode()
        if self.sued2 != None:
            self.sued2.removeNode()
        if self.suedRoundsText != None:
            self.suedRoundsText.removeNode()
        if self.sued2RoundsText != None:
            self.sued2RoundsText.removeNode()
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
        if self.marked != None:
            self.marked.removeNode()
        if self.zapped != None:
            self.zapped.removeNode()
        if self.zappedRoundsText != None:
            self.zappedRoundsText.removeNode()
        if self.markedRoundsText != None:
            self.markedRoundsText.removeNode()
        if self.enraged != None:
            self.enraged.removeNode()
        if self.dazed != None:
            self.dazed.removeNode()
        if self.extraAttacks != None:
            self.extraAttacks.removeNode()
        if self.shielding != None:
            self.shielding.removeNode()
        if self.skeleton != None:
            self.skeleton.removeNode()
        if self.virtual != None:
            self.virtual.removeNode()
        if self.damageUp != None:
            self.damageUp.removeNode()
        if self.overcharged != None:
            self.overcharged.removeNode()
        if self.insured != None:
            self.insured.removeNode()
        if self.insuredText != None:
            self.insuredText.removeNode()
        if self.vulnerabilityText != None:
            self.vulnerabilityText.removeNode()
        if self.damageReductionText != None:
            self.damageReductionText.removeNode()
        if self.luredCog != None:
            self.luredCog.removeNode()
        if self.luredManagerText != None:
            self.luredManagerText.removeNode()
        if self.rageBuildingText != None:
            self.rageBuildingText.removeNode()
        if self.immortal != None:
            self.immortal.removeNode()
        if self.luredManager != None:
            self.luredManager.removeNode()
        if self.syphon != None:
            self.syphon.removeNode()
        if self.vulnerable != None:
            self.vulnerable.removeNode()
        if self.soakResist != None:
            self.soakResist.removeNode()
        if self.absorbing != None:
            self.absorbing.removeNode()
        if self.damageReduction != None:
            self.damageReduction.removeNode()
        if self.lureImmune != None:
            self.lureImmune.removeNode()
        if self.rainbow != None:
            self.rainbow.removeNode()
        if self.hollywoods != None:
            self.hollywoods.removeNode()
        if self.sharkwatcher != None:
            self.sharkwatcher.removeNode()
        if self.statusFramePanel != None:
            self.statusFramePanel.removeNode()
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
        if self.cog.isVirtual:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.virtual = status.find('**/virtual_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.virtual.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0.361, 0.361, 0.361, 1)
                self.virtual.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.virtual.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0.361, 0.361, 0.361, 1)
                self.virtual.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.virtual.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0.361, 0.361, 0.361, 1)
                self.virtual.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.virtual.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0.361, 0.361, 0.361, 1)
                self.virtual.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.virtual.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0.361, 0.361, 0.361, 1)
                self.virtual.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.virtual.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0.361, 0.361, 0.361, 1)
                self.virtual.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.virtual.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0.361, 0.361, 0.361, 1)
                self.virtual.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.virtual.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0.361, 0.361, 0.361, 1)
                self.virtual.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isSkeleton and not self.cog.isVirtual:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.skeleton = status.find('**/skelecog_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.skeleton.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0.722, 0.722, 0.722, 1)
                self.skeleton.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.skeleton.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0.722, 0.722, 0.722, 1)
                self.skeleton.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.skeleton.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0.722, 0.722, 0.722, 1)
                self.skeleton.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.skeleton.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0.722, 0.722, 0.722, 1)
                self.skeleton.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.skeleton.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0.722, 0.722, 0.722, 1)
                self.skeleton.setColor(1, 1, 1, 1)
                self.skeleton.show()
            if self.statusEffects == 6:
                self.skeleton.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0.722, 0.722, 0.722, 1)
                self.skeleton.setColor(1, 1, 1, 1)
                self.skeleton.show()
            if self.statusEffects == 7:
                self.skeleton.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0.722, 0.722, 0.722, 1)
                self.skeleton.setColor(1, 1, 1, 1)
                self.skeleton.show()
            if self.statusEffects == 8:
                self.skeleton.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0.722, 0.722, 0.722, 1)
                self.skeleton.setColor(1, 1, 1, 1)
                self.skeleton.show()
        if self.cog.getManager() or self.cog.isLureResist or self.cog.extraAttack or self.cog.isInsured or self.cog.isInsured2 or self.cog.isContracted or self.cog.healthCondition == 13:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredManager = status.find('**/lured_prestige_icon')
            if (self.cog.isDesperation and self.cog.isAngry) or self.cog.dna.name == 'hroller' or self.cog.isImmortal or (self.cog.getActualLevel() == 25 and self.cog.dna.name == 'hrollers') or self.cog.isLureImmune:
                self.luredManagerText = DirectLabel(parent=self.luredManager, relief=None,
                                                    text="0",
                                                    text_fg=(1, 0, 0, 1),
                                                    text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                    pos=(0.25, 0, -.5),
                                                    text_scale=.5)
            elif self.cog.isDesperation or self.cog.dna.name == 'hroller2' or self.cog.dna.name == 'videog' or self.cog.dna.name == 'fires' or self.cog.dna.name == 'fbed' or self.cog.dna.name == 'mouthp' \
                    or self.cog.dna.name == 'rainmake' or self.cog.dna.name == 'whunter' or self.cog.extraAttack or self.cog.dna.name == 'wsi' or self.cog.dna.name == 'redd' or self.cog.dna.name == 'duckshfl' or self.cog.dna.name == 'treek' \
                    or self.cog.dna.name == 'bellring' or self.cog.dna.name == 'ddiver' or self.cog.dna.name == 'gatekeep' or self.cog.isAngry or (self.cog.isVulnerable and not self.cog.dna.name == 'phouse') or self.cog.extraAttack:
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
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.luredManager.reparentTo(self.healthNode)
                self.luredManager.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.luredManager.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.luredManager.reparentTo(self.healthNode)
                self.luredManager.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.luredManager.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.luredManager.reparentTo(self.healthNode)
                self.luredManager.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.luredManager.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.luredManager.reparentTo(self.healthNode)
                self.luredManager.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.luredManager.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.luredManager.reparentTo(self.healthNode)
                self.luredManager.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.luredManager.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.luredManager.reparentTo(self.healthNode)
                self.luredManager.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.luredManager.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.luredManager.reparentTo(self.healthNode)
                self.luredManager.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.luredManager.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.attackIcon7.reparentTo(self.healthNode)
                self.attackIcon7.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.luredManager.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.healthCondition == 13:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.overcharged = status.find('**/overcharge_icon')
            self.overcharged.setScale(0.8)
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.overcharged.reparentTo(self.healthNode)
                self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .145, .145, .145)
                self.pulseTask = Sequence(LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                   blendType='easeInOut'), LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(self.healthColors[13]),
                                   blendType='easeInOut'), Wait(2)).loop()
                self.overcharged.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.overcharged.reparentTo(self.healthNode)
                self.overcharged.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .145, .145, .145)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(self.healthColors[13]),
                                           blendType='easeInOut'), Wait(2)).loop()
                self.overcharged.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.overcharged.reparentTo(self.healthNode)
                self.overcharged.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .145, .145, .145)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(self.healthColors[13]),
                                           blendType='easeInOut'), Wait(2)).loop()
                self.overcharged.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.overcharged.reparentTo(self.healthNode)
                self.overcharged.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .145, .145, .145)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(self.healthColors[13]),
                                           blendType='easeInOut'), Wait(2)).loop()
                self.overcharged.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.overcharged.reparentTo(self.healthNode)
                self.overcharged.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .145, .145, .145)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(self.healthColors[13]),
                                           blendType='easeInOut'), Wait(2)).loop()
                self.overcharged.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.overcharged.reparentTo(self.healthNode)
                self.overcharged.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .145, .145, .145)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(self.healthColors[13]),
                                           blendType='easeInOut'), Wait(2)).loop()
                self.overcharged.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.overcharged.reparentTo(self.healthNode)
                self.overcharged.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .145, .145, .145)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(self.healthColors[13]),
                                           blendType='easeInOut'), Wait(2)).loop()
                self.overcharged.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.overcharged.reparentTo(self.healthNode)
                self.overcharged.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .145, .145, .145)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(0.992, 0.227, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(self.healthColors[13]),
                                           blendType='easeInOut'), Wait(2)).loop()
                self.overcharged.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isImmortal and self.cog.dna.name == 'videog':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.hollywoods = status.find('**/marked_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.hollywoods.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.hollywoods.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.hollywoods.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.hollywoods.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.hollywoods.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.hollywoods.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.hollywoods.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.hollywoods.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.dna.name == 'hroller2' and not self.cog.isPhase3:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.hollywoods = status.find('**/marked_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.hollywoods.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.hollywoods.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.hollywoods.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.hollywoods.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.hollywoods.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.hollywoods.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.hollywoods.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.hollywoods.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.hollywoods.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.dna.name == 'phouse':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/sparkplug_icon')
            self.rageBuildingText = DirectLabel(parent=self.extraAttacks, relief=None,
                                                text="%s" % self.cog.getPowerhouseRotation() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.4)
            self.rageBuildingText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.extraAttacks.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.extraAttacks.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.extraAttacks.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.extraAttacks.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.extraAttacks.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.extraAttacks.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.extraAttacks.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.extraAttacks.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.dna.name == 'cbutcher':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/chainsaw_icon')
            self.rageBuildingText = DirectLabel(parent=self.extraAttacks, relief=None,
                                                text="%s" % self.cog.getRPM() + "K", text_fg=(1, 1, 1, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.4)
            self.rageBuildingText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.extraAttacks.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.extraAttacks.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.extraAttacks.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.extraAttacks.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.extraAttacks.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.extraAttacks.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.extraAttacks.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.extraAttacks.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.dna.name == 'cbutcher' and self.cog.isVulnerable:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/kickback_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.extraAttacks.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.extraAttacks.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.extraAttacks.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.extraAttacks.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.extraAttacks.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.extraAttacks.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.extraAttacks.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.extraAttacks.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.dna.name == 'hroller':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/insured_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.extraAttacks.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.extraAttacks.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.extraAttacks.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.extraAttacks.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.extraAttacks.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.extraAttacks.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.extraAttacks.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.extraAttacks.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.dna.name == 'hroller2' and not self.cog.isVulnerable and self.cog.isPhase3:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/harmonious_colors_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.extraAttacks.reparentTo(self.healthNode)
                self.extraAttacks.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'), LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'), LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'), LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'), LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'), LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'), LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(0.56, 0, 1, 1), blendType='easeInOut')).loop()
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.extraAttacks.reparentTo(self.healthNode)
                self.extraAttacks.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.extraAttacks.reparentTo(self.healthNode)
                self.extraAttacks.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.extraAttacks.reparentTo(self.healthNode)
                self.extraAttacks.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.extraAttacks.reparentTo(self.healthNode)
                self.extraAttacks.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.extraAttacks.reparentTo(self.healthNode)
                self.extraAttacks.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.extraAttacks.reparentTo(self.healthNode)
                self.extraAttacks.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.extraAttacks.reparentTo(self.healthNode)
                self.extraAttacks.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
                self.rainbow = status.find('**/brain_icon')
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
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.rainbow.reparentTo(self.healthNode)
                self.rainbow.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.rainbow.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.rainbow.reparentTo(self.healthNode)
                self.rainbow.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.rainbow.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.rainbow.reparentTo(self.healthNode)
                self.rainbow.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.rainbow.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.rainbow.reparentTo(self.healthNode)
                self.rainbow.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.rainbow.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.rainbow.reparentTo(self.healthNode)
                self.rainbow.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.rainbow.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.rainbow.reparentTo(self.healthNode)
                self.rainbow.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.rainbow.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.rainbow.reparentTo(self.healthNode)
                self.rainbow.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.rainbow.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.rainbow.reparentTo(self.healthNode)
                self.rainbow.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(1, 0.5, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(1, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(0, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(0, 0, 1, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(0.29, 0, 0.51, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=2, colorScale=(0.56, 0, 1, 1),
                                           blendType='easeInOut')).loop()
                self.rainbow.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isAngry:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/rage_mode_icon')
            self.enrageCountText = DirectLabel(parent=self.enraged, relief=None,
                                              text="%s" % self.cog.getEnrageCounter(), text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.enrageCountText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.enraged.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.enraged.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.enraged.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.enraged.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.enraged.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.enraged.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.enraged.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.enraged.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isStormCell:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/stormcell_icon')
            self.enrageCountText = DirectLabel(parent=self.enraged, relief=None,
                                              text="-%s" % self.cog.getStormCellDamage(), text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.4)
            self.enrageCountText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.enraged.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.enraged.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.enraged.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.enraged.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.enraged.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.enraged.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.enraged.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.enraged.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isHeavyRain:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/heavyrain_icon')
            self.enrageCountText = DirectLabel(parent=self.enraged, relief=None,
                                              text="-%s" % self.cog.getHeavyRainDamage(), text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.4)
            self.enrageCountText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.enraged.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.enraged.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.enraged.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.enraged.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.enraged.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.enraged.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.enraged.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.enraged.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isMonsoon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/monsoon_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.enraged.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.enraged.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.enraged.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.enraged.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.enraged.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.enraged.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.enraged.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.enraged.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isFreezingRain:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/frozen_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.enraged.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.enraged.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.enraged.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.enraged.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.enraged.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.enraged.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.enraged.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.enraged.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isOilRain:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/oilrain_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.enraged.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.enraged.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.enraged.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.enraged.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.enraged.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.enraged.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.enraged.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.enraged.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isShielding and self.cog.dna.name == 'sgoat':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing = status.find('**/defense_mode_icon')
            self.rageBuildingText = DirectLabel(parent=self.absorbing, relief=None,
                                                text="%s" % self.cog.getRageBuilding() + "%", text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.4)
            self.rageBuildingText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.absorbing.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.absorbing.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.absorbing.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.absorbing.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.absorbing.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.absorbing.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.absorbing.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.absorbing.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isShielding and not self.cog.dna.name == 'sgoat' and not self.cog.dna.name == 'hroller':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.absorbing = status.find('**/damage_absorb_icon')  # 3 slot absorb icon
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.absorbing.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.absorbing.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.absorbing.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.absorbing.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.absorbing.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.absorbing.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.absorbing.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.absorbing.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.absorbing.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isDropImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/duck_drop_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.enraged.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.enraged.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.enraged.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.enraged.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.enraged.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.enraged.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.enraged.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.enraged.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isZapImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.enraged = status.find('**/fizzle_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.enraged.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.enraged.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.enraged.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.enraged.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.enraged.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.enraged.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.enraged.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.enraged.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.enraged.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isLureImmune and not self.cog.dna.name == 'hrollers':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.lureImmune = status.find('**/cashback_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.lureImmune.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.lureImmune.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.lureImmune.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.lureImmune.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.lureImmune.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.lureImmune.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.lureImmune.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.lureImmune.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.lureImmune.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.lureImmune.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.lureImmune.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.lureImmune.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.lureImmune.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.lureImmune.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.lureImmune.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.lureImmune.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isImmortal and not self.cog.dna.name == 'hroller' and not self.cog.dna.name == 'hroller2':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/schadenfreude_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isBookkeeping:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/backfire_icon')
            self.damageMultText2 = DirectLabel(parent=self.immortal, relief=None, text="1", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText2.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.getGovernaught():
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/tie_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isSleepy:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.immortal = status.find('**/lunch_background')
            self.damageMultText = DirectLabel(parent=self.immortal, relief=None, text="%s" % (self.cog.getSleepyCondition() - 1), text_fg=(1, 1, 1, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.5)
            self.damageMultText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.immortal.reparentTo(self.healthNode)
                self.immortal.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.immortal.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isDamageUp:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp = status.find('**/suit_damage_up_icon')
            self.damageMultText = DirectLabel(parent=self.damageUp, relief=None, text="%s" % self.cog.getDamageUp() + "%", text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.4)
            self.damageMultText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isDamageDown:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageUp = status.find('**/suit_damage_down_icon')
            self.damageMultText2 = DirectLabel(parent=self.damageUp, relief=None, text="%s" % self.cog.getDamageDown() + "%", text_fg=(0, 1, 0.047, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.4)
            self.damageMultText2.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.damageUp.reparentTo(self.healthNode)
                self.damageUp.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageUp.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            else:
                self.vulnerabilityText = DirectLabel(parent=self.vulnerable, relief=None,
                                                     text="%s" % self.cog.getVulnerability() + "%",
                                                     text_fg=(0, 1, 0.047, 1),
                                                     text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                     pos=(0.25, 0, -.5),
                                                     text_scale=.4)
            self.vulnerabilityText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.vulnerable.reparentTo(self.healthNode)
                self.vulnerable.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.vulnerable.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.vulnerable.reparentTo(self.healthNode)
                self.vulnerable.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.vulnerable.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.vulnerable.reparentTo(self.healthNode)
                self.vulnerable.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.vulnerable.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.vulnerable.reparentTo(self.healthNode)
                self.vulnerable.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.vulnerable.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.vulnerable.reparentTo(self.healthNode)
                self.vulnerable.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.vulnerable.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.vulnerable.reparentTo(self.healthNode)
                self.vulnerable.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.vulnerable.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.vulnerable.reparentTo(self.healthNode)
                self.vulnerable.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.vulnerable.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.vulnerable.reparentTo(self.healthNode)
                self.vulnerable.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(0.027, 1, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.vulnerable.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isDamageReduction:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.damageReduction = status.find('**/shield_icon')  # third slot vulnerability icon
            self.vulnerabilityText = DirectLabel(parent=self.damageReduction, relief=None,
                                                     text="%s" % self.cog.getDamageReduction() + "%",
                                                     text_fg=(1, 0, 0, 1),
                                                     text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                     pos=(0.25, 0, -.5),
                                                     text_scale=.4)
            self.vulnerabilityText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.damageReduction.reparentTo(self.healthNode)
                self.damageReduction.setPosHprScale(-0.335, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageReduction.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.damageReduction.reparentTo(self.healthNode)
                self.damageReduction.setPosHprScale(-0.2075, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon1, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageReduction.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.damageReduction.reparentTo(self.healthNode)
                self.damageReduction.setPosHprScale(-0.045, 0.5, -0.355, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon2, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageReduction.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.damageReduction.reparentTo(self.healthNode)
                self.damageReduction.setPosHprScale(0.085, 0.4, -0.26, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon3, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageReduction.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.damageReduction.reparentTo(self.healthNode)
                self.damageReduction.setPosHprScale(-0.37, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon4, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageReduction.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.damageReduction.reparentTo(self.healthNode)
                self.damageReduction.setPosHprScale(-0.2075, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon5, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageReduction.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.damageReduction.reparentTo(self.healthNode)
                self.damageReduction.setPosHprScale(-0.045, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon6, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageReduction.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.damageReduction.reparentTo(self.healthNode)
                self.damageReduction.setPosHprScale(0.115, 0.4, 0.23, 0, 0, 0, .165, .165, .165)
                self.pulseTask = Sequence(
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0, 0, 1),
                                           blendType='easeInOut'),
                    LerpColorScaleInterval(self.attackIcon7, duration=1, colorScale=(1, 0.984, 0, 1),
                                           blendType='easeInOut'), Wait(1)).loop()
                self.damageReduction.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isSyphon:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.syphon = status.find('**/ink_drain_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.syphon.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.syphon.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.syphon.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.syphon.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.syphon.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.syphon.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.syphon.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.syphon.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.syphon.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.syphon.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.syphon.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.syphon.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.syphon.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.syphon.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.syphon.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.syphon.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.insured.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.insured.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.insured.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.insured.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.insured.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.insured.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.insured.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.insured.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isContracted or self.cog.dna.name == 'supervis' or self.cog.dna.name == 'ovt':
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.insured = status.find('**/insured_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.insured.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.insured.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.insured.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.insured.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.insured.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.insured.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.insured.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.insured.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.insured.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.extraAttack:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.extraAttacks = status.find('**/extra_attacks_icon')
            self.extraAttacksText = DirectLabel(parent=self.extraAttacks, relief=None, text="+%s" % self.cog.getExtraAttacks(),
                                                text_fg=(1, 0, 0, 1),
                                                text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                                pos=(0.25, 0, -.5),
                                                text_scale=.5)
            self.extraAttacksText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.extraAttacks.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.extraAttacks.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.extraAttacks.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.extraAttacks.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.extraAttacks.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.extraAttacks.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.extraAttacks.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.extraAttacks.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.extraAttacks.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isSoakImmune:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.soakResist = status.find('**/soaked_icon')
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.soakResist.reparentTo(self.attackIcon)
                self.attackIcon.setColor(1, 0.984, 0, 1)
                self.soakResist.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.soakResist.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(1, 0.984, 0, 1)
                self.soakResist.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.soakResist.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(1, 0.984, 0, 1)
                self.soakResist.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.soakResist.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(1, 0.984, 0, 1)
                self.soakResist.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.soakResist.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(1, 0.984, 0, 1)
                self.soakResist.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.soakResist.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(1, 0.984, 0, 1)
                self.soakResist.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.soakResist.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(1, 0.984, 0, 1)
                self.soakResist.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.soakResist.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(1, 0.984, 0, 1)
                self.soakResist.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isSued:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.sued = status.find('**/sued_icon')
            self.suedRoundsText = DirectLabel(parent=self.sued, relief=None, text="%s" % (self.cog.getSuedRounds() - 1),
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
        if self.cog.isSued:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.sued2 = status.find('**/damage_over_time_icon')
            self.sued2RoundsText = DirectLabel(parent=self.sued2, relief=None, text="-%s" % int(self.cog.getMaxHP() / 4),
                                              text_fg=(1, 0, 0, 1),
                                              text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                              pos=(0.25, 0, -.5),
                                              text_scale=.4)
            self.sued2RoundsText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.sued2.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.sued2.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.sued2.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.sued2.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.sued2.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.sued2.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.sued2.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.sued2.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.sued2.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.sued2.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.sued2.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.sued2.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.sued2.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.sued2.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.sued2.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.sued2.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isLured:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.luredCog = status.find('**/lured_icon')
            self.luredText = DirectLabel(parent=self.luredCog, relief=None, text="%s" % self.cog.getLuredRounds(),
                                         text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.luredText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.luredCog.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.luredCog.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.luredCog.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.luredCog.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.luredCog.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.luredCog.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.luredCog.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.luredCog.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.luredCog.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.luredCog.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.luredCog.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.luredCog.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.luredCog.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.luredCog.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.luredCog.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.luredCog.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isZapped:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.zapped = status.find('**/reward_cooldown_icon')
            self.zappedRoundsText = DirectLabel(parent=self.zapped, relief=None, text="-%s" % self.cog.getZapCondition(),
                                         text_fg=(1, 0, 0, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.4),
                                         text_scale=.4)
            self.zappedRoundsText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.zapped.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.zapped.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.zapped.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.zapped.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.zapped.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.zapped.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.zapped.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.zapped.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.zapped.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.zapped.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.zapped.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.zapped.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.zapped.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.zapped.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.zapped.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.zapped.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
        if self.cog.isMarked:
            status = loader.loadModel('phase_3.5/models/gui/status_effects')
            self.marked = status.find('**/deepfreeze_icon')
            self.markedRoundsText = DirectLabel(parent=self.marked, relief=None, text="1",
                                         text_fg=(1, 1, 1, 1),
                                         text_font=getSignFont(), text_bg=Vec4(0, 0, 0, 0),
                                         pos=(0.25, 0, -.5),
                                         text_scale=.5)
            self.markedRoundsText.show()
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.marked.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.marked.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.marked.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.marked.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.marked.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.marked.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.marked.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.marked.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.marked.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.marked.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.marked.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.marked.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.marked.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.marked.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.marked.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.marked.setColor(1, 1, 1, 1)
                self.attackIcon7.show()
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
            self.statusEffects += 1
            if self.statusEffects == 1:
                self.dazed.reparentTo(self.attackIcon)
                self.attackIcon.setColor(0, 0.902, 1, 1)
                self.dazed.setColor(1, 1, 1, 1)
            if self.statusEffects == 2:
                self.dazed.reparentTo(self.attackIcon1)
                self.attackIcon1.setColor(0, 0.902, 1, 1)
                self.dazed.setColor(1, 1, 1, 1)
            if self.statusEffects == 3:
                self.dazed.reparentTo(self.attackIcon2)
                self.attackIcon2.setColor(0, 0.902, 1, 1)
                self.dazed.setColor(1, 1, 1, 1)
            if self.statusEffects == 4:
                self.dazed.reparentTo(self.attackIcon3)
                self.attackIcon3.setColor(0, 0.902, 1, 1)
                self.dazed.setColor(1, 1, 1, 1)
            if self.statusEffects == 5:
                self.dazed.reparentTo(self.attackIcon4)
                self.attackIcon4.setColor(0, 0.902, 1, 1)
                self.dazed.setColor(1, 1, 1, 1)
                self.attackIcon4.show()
            if self.statusEffects == 6:
                self.dazed.reparentTo(self.attackIcon5)
                self.attackIcon5.setColor(0, 0.902, 1, 1)
                self.dazed.setColor(1, 1, 1, 1)
                self.attackIcon5.show()
            if self.statusEffects == 7:
                self.dazed.reparentTo(self.attackIcon6)
                self.attackIcon6.setColor(0, 0.902, 1, 1)
                self.dazed.setColor(1, 1, 1, 1)
                self.attackIcon6.show()
            if self.statusEffects == 8:
                self.dazed.reparentTo(self.attackIcon7)
                self.attackIcon7.setColor(0, 0.902, 1, 1)
                self.dazed.setColor(1, 1, 1, 1)
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
            self.hp = 'Immune!'
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
        elif name == 'mh' or name == 'ym' or name == 'trs' or name == 'chairp' or name == 'std2' or name == 'bsht' or name == 'std' or name == 'enf' or name == 'rb' or name == 'mh2' or name == 'cnd' or name == 'vpr':
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
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.10, -180, 0, 0, .06, .06, .06)
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
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .0675, .0675, .0675)
        elif name == 'safesupervis':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.125, -180, 0, 0, .0675, .0675, .0675)
        elif name == 'watchm':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .1, .1, .1)
        elif name == 'mplayer' or name == 'mplayer2':
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.11, -180, 0, 0, .08, .08, .08)
        elif name == 'chainsaw' or name == 'chainsaw2' or name == 'cbutcher':
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
        elif name == 'rainmake' or name == 'liquid':
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
            self.suitHead.setPosHprScale(-0.27, 0.5, 0.12, -180, 0, 0, .09, .09, .09)
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
        if self.luredText != None:
            self.luredText.removeNode()
        if self.damageMultText != None:
            self.damageMultText.removeNode()
        if self.damageMultText2 != None:
            self.damageMultText2.removeNode()
        if self.extraAttacks != None:
            self.extraAttacks.removeNode()
        if self.sued != None:
            self.sued.removeNode()
        if self.sued2 != None:
            self.sued2.removeNode()
        if self.suedRoundsText != None:
            self.suedRoundsText.removeNode()
        if self.sued2RoundsText != None:
            self.sued2RoundsText.removeNode()
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
        if self.markedRoundsText != None:
            self.markedRoundsText.removeNode()
        if self.marked != None:
            self.marked.removeNode()
        if self.zappedRoundsText != None:
            self.zappedRoundsText.removeNode()
        if self.zapped != None:
            self.zapped.removeNode()
        if self.enraged != None:
            self.enraged.removeNode()
        if self.dazed != None:
            self.dazed.removeNode()
        if self.soaked != None:
            self.soaked.removeNode()
        if self.extraAttacks != None:
            self.extraAttacks.removeNode()
        if self.shielding != None:
            self.shielding.removeNode()
        if self.skeleton != None:
            self.skeleton.removeNode()
        if self.virtual != None:
            self.virtual.removeNode()
        if self.damageUp != None:
            self.damageUp.removeNode()
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
        if self.damageUpMgr != None:
            self.damageUpMgr.removeNode()
        if self.overcharged != None:
            self.overcharged.removeNode()
        if self.insured != None:
            self.insured.removeNode()
        if self.insuredText != None:
            self.insuredText.removeNode()
        if self.overcharged != None:
            self.overcharged.removeNode()
        if self.lured != None:
            self.lured.removeNode()
        if self.vulnerabilityText != None:
            self.vulnerabilityText.removeNode()
        if self.damageReductionText != None:
            self.damageReductionText.removeNode()
        if self.luredManagerText != None:
            self.luredManagerText.removeNode()
        if self.rageBuildingText != None:
            self.rageBuildingText.removeNode()
        if self.immortal != None:
            self.immortal.removeNode()
        if self.luredManager != None:
            self.luredManager.removeNode()
        if self.syphon != None:
            self.syphon.removeNode()
        if self.vulnerable != None:
            self.vulnerable.removeNode()
        if self.soakResist != None:
            self.soakResist.removeNode()
        if self.absorbing != None:
            self.absorbing.removeNode()
        if self.damageReduction != None:
            self.damageReduction.removeNode()
        if self.lureImmune != None:
            self.lureImmune.removeNode()
        if self.rainbow != None:
            self.rainbow.removeNode()
        if self.hollywoods != None:
            self.hollywoods.removeNode()
        if self.sharkwatcher != None:
            self.sharkwatcher.removeNode()
        if self.luredCog != None:
            self.luredCog.removeNode()
        if self.statusFrame != None:
            self.statusFrame.removeNode()
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
        if self.pulseTask != None:
            self.pulseTask.finish()
            del self.pulseTask
        if self.statusFramePanel != None:
            self.statusFramePanel.removeNode()
        if self.statusText2 != None:
            self.statusText2.removeNode()
        if self.statusText1 != None:
            self.statusText1.removeNode()
        del self.enraged
        del self.shielding
        del self.overcharged
        del self.luredCog
        del self.luredManager
        del self.insured
        del self.damageUp
        del self.damageDown
        del self.skeleton
        del self.virtual
        del self.immortal
        del self.vulnerable
        del self.soakResist
        del self.syphon
        del self.marked
        del self.absorbing
        del self.damageReduction
        del self.lureImmune
        del self.rainbow
        del self.hollywoods
        del self.sharkwatcher
        del self.soaked
        del self.dazed
        del self.extraAttacks
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
        del self.statusFrame
        del self.healthNode
        del self.statusFramePanel
        del self.statusText2
        del self.statusText2
        del self.pulseTask
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

