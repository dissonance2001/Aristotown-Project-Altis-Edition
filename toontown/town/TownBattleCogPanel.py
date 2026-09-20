from direct.task.Task import Task
from direct.gui.DirectGui import *
from panda3d.core import *

from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.clashsuit.suit.Suit import Suit
from toontown.clashsuit.suit import SuitHealthMeter
from toontown.toonbase import TTLocalizer
from toontown.clashbattle.battle import BattleGUI
from toontown.quest3.gui.Quest3Poster import QuestPoster
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.nametag.NametagFloat2d import NametagFloat2d
from toontown.nametag import NametagGlobals
from toontown.nametag import Nametag

@DirectNotifyCategory()
class TownBattleCogPanel(DirectFrame):
    healthColors = SuitHealthMeter.HEALTH_COLORS
    healthGlowColors = SuitHealthMeter.HEALTH_COLORS

    NORMAL_COG_FRAME_COLOR = Vec4(.7, .7, .7, .8)
    EXE_COG_FRAME_COLOR = Vec4(.5, .5, .5, .8)
    MINIBOSS_FRAME_COLOR = Vec4(.7, .4, .4, .8)

    def __init__(self, townBattle):
        self.notify.debug("Init Cog Battle Panel!")
        DirectFrame.__init__(self, relief=None)
        self.initialiseoptions(TownBattleCogPanel)
        self.townBattle = townBattle
        self.hidden = False
        self.cog = None
        self.head = None
        self.isLoaded = 0
        self.suitInfoTooltip = None
        self.statusEffectTooltip = None
        self.blinkTask = None
        self.blinkTaskName = self.uniqueName('blink-task')
        self.guiElements = None
        self.suitPanelFrame = None
        self.healthBar = None
        self.hpText = None
        self.healthBarClippingPlane = None
        self.levelText = None
        self.hidByBattle = False
        self.effectSlots = None
        self.currentHeadModelName = None
        self.avatarEffects = []
        self.statusEffects = []
        self.offset = 0
        self.hoveredEffects = []
        self.load()
        self.hide()

    def load(self):
        self.guiElements = BattleGUI.generateSuitPanel()
        self.suitPanelFrame = self.guiElements[BattleGUI.SUIT_PANEL_FRAME]
        self.suitPanelFrame.reparentTo(self)
        self.suitPanelFrame.setScale(BattleGUI.SuitPanelScale)
        self.healthBar = self.guiElements[BattleGUI.SUIT_PANEL_HEALTH_BAR]
        self.hpText = self.guiElements[BattleGUI.SUIT_PANEL_HEALTH_BAR_LABEL]
        self.healthBarClippingPlane = self.guiElements[BattleGUI.SUIT_PANEL_HEALTH_BAR_CLIPPING_PLANE]
        self.levelText = self.guiElements[BattleGUI.SUIT_PANEL_LEVEL_LABEL]
        self.effectSlots = self.guiElements[BattleGUI.SUIT_PANEL_SLOTS]
        # Set commands for the cycling buttons
        self.guiElements[BattleGUI.SUIT_PANEL_CYCLE_BACK_BUTTON].configure(command=lambda: self.changeOffset(-1))
        self.guiElements[BattleGUI.SUIT_PANEL_CYCLE_FORWARD_BUTTON].configure(command=lambda: self.changeOffset(1))
        # Create Suit Tooltip
        self.createSuitInfoTooltip()
        # Set binds for the info button
        self.guiElements[BattleGUI.SUIT_PANEL_INFO_BUTTON].bind(DGG.WITHIN, self.enterInfoButton)
        self.guiElements[BattleGUI.SUIT_PANEL_INFO_BUTTON].bind(DGG.WITHOUT, self.exitInfoButton)
        # Set command for the info button
        self.guiElements[BattleGUI.SUIT_PANEL_INFO_BUTTON].configure(command=self.activateInfoButton)
        self.createStatusEffectTooltip()
        self.isLoaded = 1

    def isConcealed(self) -> bool:
        return bool(base.localAvatar.getStatusEffectOfType(StatusEffects.ObscureInformationStatusEffect))

    def hpIsConcealed(self) -> bool:
        return bool(self.cog.getStatusEffectOfType(StatusEffects.ObscureHPStatusEffect))

    def setCogInformation(self, cog):
        self.cog = cog
        self.updateStatusEffects()
        ''' NOT SURE IF WE WANNA COLOR THIS FRAME
        if self.cog.isMiniboss():
            self['image_color'] = self.MINIBOSS_FRAME_COLOR
        elif self.cog.getElite():
            self['image_color'] = self.EXE_COG_FRAME_COLOR
        else:
            self['image_color'] = self.NORMAL_COG_FRAME_COLOR
        '''
        self.updateHealthBar()

        if not self.isConcealed():
            # We are visible. Spawn the cog head.
            cogName = self.cog.style.name
            if self.currentHeadModelName != cogName:
                self.currentHeadModelName = cogName
                if self.head:
                    self.head.removeNode()

                self.head = self.attachNewNode('head')

                head = QuestPoster.createSuitHead(self.cog.style.name)
                head.copyTo(self.head)

                self.head.setPos(-0.1405, 0, 0.107)
                self.head.setScale(0.12)

            # Also set various data.
            self.setLevelText(cog.getActualLevel(), cog.getSkeleRevives())

            # If we're a trivia or shuffle cog, we'll use our name instead for the level text
            for effect in cog.getVisualEffectsOfId(VisualEffectEnum.HIGHROLLER_TRIVIA):
                name: str = effect.getName()
                if len(name) > 16:
                    name = f"{name[:14].strip()}..."
                self.levelText['text'] = name

            self.suitInfoTooltip.setSuitInfo(cog)
        else:
            # Stats are concealed -- go ahead and hide them
            if self.head:
                self.head.removeNode()
                self.head = None
            self.levelText['text'] = "?"

    def setLevelText(self, level, revives = 0):
        if not self.isConcealed():
            text = TTLocalizer.DisguisePageCogLevel % str(level)
            appended = 0
            if self.cog.getElite() and not self.cog.isMiniboss():
                text += TTLocalizer.AvatarSuitPanelExecutive
                appended += 1
            elif self.cog.isMiniboss():
                text += TTLocalizer.AvatarSuitPanelManager
                appended += 1
            if revives > 0:
                text += TTLocalizer.SkeleRevivePostFix
                appended += 1
        else:
            text = TTLocalizer.DisguisePageCogLevel % '???'
        self.levelText['text'] = text
        if appended >= 2:
            self.levelText['text_scale'] = (0.06, 0.063, 0.063)
        else:
            self.levelText['text_scale'] = 0.063

    def updateStatusEffects(self):
        # Clear out previous round's effects
        for effect in self.statusEffects:
            if effect.bgSequence:
                effect.bgSequence.finish()
            effect.destroy()
        # Reset offset of effects to 0
        self.offset = 0
        # Reset the hovered effects
        self.hoveredEffects = []
        # Hide tooltips
        self.statusEffectTooltip.hide()
        self.suitInfoTooltip.hide()
        if self.isConcealed():
            self.avatarEffects = []
        else:
            self.avatarEffects = self.cog.getVisibleStatusEffects()
        self.statusEffects = BattleGUI.generateStatusEffects(self.avatarEffects)
        # Bind all the new effects to the hover over update functions.
        for i in range(len(self.statusEffects)):
            self.statusEffects[i].bind(DGG.WITHIN, self.enterStatusEffect, extraArgs=[i])
            self.statusEffects[i].bind(DGG.WITHOUT, self.exitStatusEffect, extraArgs=[i])
        BattleGUI.fitStatusEffectsIntoSlots(self.effectSlots, self.statusEffects, self.offset,
                                            self.guiElements[BattleGUI.SUIT_PANEL_CYCLE_BACK_BUTTON],
                                            self.guiElements[BattleGUI.SUIT_PANEL_CYCLE_FORWARD_BUTTON])

    def createSuitInfoTooltip(self):
        if self.isConcealed():
            return
        self.suitInfoTooltip = BattleGUI.SuitInfoTooltip(
            parent=self,
            relief=None,
            pos=(0, 0, -0.3),
            scale=1.2
        )
        self.suitInfoTooltip.setBin("gui-popup", 100)
        self.suitInfoTooltip.hide()

    def enterInfoButton(self, _):
        if self.isConcealed():
            return
        self.suitInfoTooltip.show()

    def exitInfoButton(self, _):
        if self.isConcealed():
            return
        self.suitInfoTooltip.hide()

    def activateInfoButton(self):
        if self.isConcealed():
            return
        if self.cog == self.townBattle.informationPanel.av:
            self.townBattle.informationPanel.clearPanel()
        else:
            panel = BattleGUI.SuitInformationPanel(relief=None)
            panel.setSuitInfo(self.cog)
            panel.setStatusEffects(self.avatarEffects)
            self.townBattle.informationPanel.setPanel(self.cog, panel)

    def createStatusEffectTooltip(self):
        if self.isConcealed():
            return
        self.statusEffectTooltip = BattleGUI.StatusEffectTooltip(
            parent=self,
            relief=None,
            pos=(0, 0, -0.3)
        )
        self.statusEffectTooltip.setIsToon(False)
        self.statusEffectTooltip.setBin("gui-popup", 100)
        self.statusEffectTooltip.hide()

    def enterStatusEffect(self, effectIndex, _):
        if effectIndex not in self.hoveredEffects:
            self.hoveredEffects.append(effectIndex)
        self.setStatusEffectTooltip(self.avatarEffects[effectIndex])

    def exitStatusEffect(self, effectIndex, _):
        # Check now to see if we are exiting the status effect currently being shown
        removingShownEffect = True if len(self.hoveredEffects) > 0 and self.hoveredEffects[-1] == effectIndex else False
        # Remove this effect from the list
        if effectIndex in self.hoveredEffects:
            self.hoveredEffects.remove(effectIndex)
        # If there are still effects in the list, set tooltip to the next effect in the list.
        if len(self.hoveredEffects) > 0:
            if removingShownEffect:
                self.setStatusEffectTooltip(self.avatarEffects[self.hoveredEffects[-1]])
        else:
            # Hide tooltip otherwise.
            self.statusEffectTooltip.hide()

    def setStatusEffectTooltip(self, effect):
        self.statusEffectTooltip.setStatusEffect(effect)
        self.statusEffectTooltip.show()

    def changeOffset(self, amount):
        offset = self.offset + amount
        # Clamp offset value to prevent indexing out of range
        offset = max(0, min(offset, len(self.statusEffects) - len(self.effectSlots)))

        # Readjust status effects if offset has changed
        if offset != self.offset:
            self.offset = offset
            BattleGUI.fitStatusEffectsIntoSlots(self.effectSlots, self.statusEffects, self.offset,
                                                self.guiElements[BattleGUI.SUIT_PANEL_CYCLE_BACK_BUTTON],
                                                self.guiElements[BattleGUI.SUIT_PANEL_CYCLE_FORWARD_BUTTON])

    def updateHealthBar(self):
        if not self.isConcealed() and not self.hpIsConcealed():
            condition = getattr(self.cog.healthBar, "hpCond", 0)
            if condition == 9:
                self.blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.75), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(self.blinkTask, self.blinkTaskName)
            elif condition == 10:
                taskMgr.remove(self.blinkTaskName)
                blinkTask = Task.loop(Task(self.__blinkRed), Task.pause(0.25), Task(self.__blinkGray), Task.pause(0.1))
                taskMgr.add(blinkTask, self.blinkTaskName)
            elif condition == 11:
                taskMgr.remove(self.blinkTaskName)
                if not self.healthBar.isEmpty():
                    self.healthBar.setColor(self.healthColors[10], 1)
            # elif condition == 12:
            #     taskMgr.remove(self.uniqueName('blink-task'))
            #     if not self.button.isEmpty():
            #         self.button.setColor(self.healthColors[11], 1)
            else:
                taskMgr.remove(self.blinkTaskName)
                if not self.healthBar.isEmpty():
                    self.healthBar.setColor(self.healthColors[condition], 1)
            self.hp = self.cog.getHp()
            self.maxHp = self.cog.getMaxHp()
            self.hpText['text'] = str(self.hp) + '/' + str(self.maxHp)
            if condition == 12:
                self.hpText['text_fg'] = Vec4(1, 1, 1, 1)
                self.hpText['text_shadow'] = Vec4(0, 0, 0, 1)
            else:
                self.hpText['text_fg'] = Vec4(0, 0, 0, 1)
                self.hpText['text_shadow'] = Vec4(0, 0, 0, 0)

            # Update clipping plane based off current health
            self.healthBarClippingPlane.setPlane(Plane(Vec3(-1, 0, 0), Point3(self.__lerp(-0.49, 0.49, self.cog.getHealthPercentage()), 0, 0)))
        else:
            taskMgr.remove(self.blinkTaskName)
            if not self.healthBar.isEmpty():
                self.healthBar.setColor(self.healthColors[10], 1)

            self.hp = "?"
            self.maxHp = "?"
            self.hpText['text'] = str(self.hp) + '/' + str(self.maxHp)
            self.hpText['text_fg'] = Vec4(0, 0, 0, 1)
            self.hpText['text_shadow'] = Vec4(0, 0, 0, 0)
            self.healthBarClippingPlane.setPlane(Plane(Vec3(-1, 0, 0), Point3(self.__lerp(-0.49, 0.49, 0), 0, 0)))

    def __lerp(self, x, y, lerpAmount):
        '''
        Returns a float linearly interpolated from 0 to 1
        For lerpAmount, 0 = x and 1 = y. 0.5 would be the midpoint.
        '''
        return x - lerpAmount * (x - y)

    def __blinkRed(self, task):
        if not self.healthBar.isEmpty():
            self.healthBar.setColor(self.healthColors[8], 1)

        return Task.done

    def __blinkGray(self, task):
        if not self.healthBar.isEmpty():
            self.healthBar.setColor(self.healthColors[9], 1)

        return Task.done

    def show(self):
        if self.cog:
            self.updateHealthBar()
        self.hidden = False
        self.hidByBattle = False
        DirectFrame.show(self)

    def hide(self, hidByBattle=False):
        if self.blinkTask:
            taskMgr.remove(self.blinkTaskName)
            self.blinkTask = None

        self.hidden = True
        self.hidByBattle = hidByBattle
        DirectFrame.hide(self)

    def unload(self):
        if self.isLoaded == 0:
            return
        self.isLoaded = 0
        self.exit()
        del self.cog
        if self.blinkTask:
            taskMgr.remove(self.blinkTaskName)
            self.blinkTask = None
        del self.hpText
        del self.townBattle
        DirectFrame.destroy(self)

    def cleanup(self):
        self.ignoreAll()
        if self.head:
            self.head.removeNode()
            del self.head

        if self.blinkTask:
            taskMgr.remove(self.blinkTaskName)
            self.blinkTask = None

        for effect in self.statusEffects:
            if effect.bgSequence:
                effect.bgSequence.finish()
            effect.destroy()
        del self.statusEffects

        del self.blinkTask
        DirectFrame.destroy(self)
