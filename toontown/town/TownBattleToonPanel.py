from toontown.clashbattle.battle.statuses.StatusEffectDefinitions import DEBUFF, getEffectIdsOfQuality, StatusEffectDefinitions
from toontown.gui.ScaledFrame import ScaledFrame
from toontown.clashsuit.suit.ClashSuitBase import ClashSuitBase
from toontown.toon.gui import GuiBinGlobals
from toontown.toonbase import ToontownGlobals
from toontown.clashbattle.battle.BattleGlobals import *
import math
from toontown.toon import OldLaffMeter
from toontown.clashbattle.battle import BattleBase, BattleGlobals
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from toontown.toonbase import TTLocalizer
from toontown.clashbattle.battle import BattleGUI
from toontown.clashbattle.battle.statuses import StatusEffects
from otp import *
from toontown.nametag.NametagFloat2d import NametagFloat2d
from toontown.nametag import NametagGlobals
from toontown.nametag.Nametag import *
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class TownBattleToonPanel(DirectFrame):

    damageTextPositions = (
        (0.12, 0, 0.126),  # top middle
        (0.04, 0, 0.075),  # left
        (0.22, 0, 0.075),  # right
        (0.07, 0, 0.115),  # mid-left
        (0.17, 0, 0.115),  # mid-right
    )

    def __init__(self, townBattle):
        DirectFrame.__init__(self, relief=None)
        self.initialiseoptions(TownBattleToonPanel)
        self.townBattle = townBattle
        self.guiElements = BattleGUI.generateToonPanel()
        self.guiElements[BattleGUI.TOON_PANEL_FRAME].reparentTo(self)
        self.guiElements[BattleGUI.TOON_PANEL_FRAME].setScale(BattleGUI.ToonPanelScaling)
        self.avatar = None
        self.cogs = []
        self.sosText = DirectLabel(parent=self, relief=None, pos=(0.14, 0, -0.14), text='', text_font=ToontownGlobals.getBuildingNametagFont(), text_scale=0.038)
        self.sosText.hide()
        self.roundsText = DirectLabel(parent=self, relief=None, pos=self.damageTextPositions[0], text='', text_font=ToontownGlobals.getBuildingNametagFont(), text_scale=0.075)
        self.roundsText.hide()
        self.knockbackText = DirectLabel(parent=self, relief=None, pos=(0.23, 0, 0.092), text='', text_font=ToontownGlobals.getBuildingNametagFont(), text_scale=0.06)
        self.knockbackText.hide()
        self.zapJumpText = [
            DirectLabel(parent=self, relief=None, pos=self.damageTextPositions[0], text_fg=(0.85, 0, 0, 1),
                        text='', text_font=ToontownGlobals.getBuildingNametagFont(), text_scale=0.075, text_pos=(0, -0.004))
        ] + [
            DirectLabel(parent=self, relief=None, pos=self.damageTextPositions[i + 1],
                        text='', text_fg=Vec4(0.800, 0.808, 1, 1), text_shadow=Vec4(0.894, 0.808, 1, 1),
                        text_font=ToontownGlobals.getBuildingNametagFont(), text_scale=0.055) for i in range(2)]
        for label in self.zapJumpText:
            label.hide()
        self.healthText = DirectLabel(parent=self, text='', pos=(-0.06, 0, -0.075), text_scale=0.055)
        self.healthText.hide()
        self.nameText = DirectLabel(parent=self, relief=None, pos=(-0.1, 0, 0.18), text='', text_scale=0.04, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1))

        # Counterfeit stuff
        self.counterfeitHolder = ScaledFrame(parent=self, relief=None, pos=(0.05, 0, 0.15),
                                             frameSize=(-0.13, 0.12, -0.02, 0.04),
                                             scaledTexture='phase_3/maps/gui/ttcc_gui_scaledFrame_shadow.png')
        self.counterfeitHolder.setBin('sorted-gui-popup', GuiBinGlobals.BattleCounterfeitTooltip)
        self.counterfeitHolder.hide()
        self.counterfeitText = DirectLabel(parent=self.counterfeitHolder, relief=None, text_align=TextNode.ACenter,
                                           text_font=ToontownGlobals.getSignFont(), text_fg=Vec4(0, 1, 0, 1),
                                           text_scale=0.2, text='\1white\1\5battle_counterfeitIcon_popup\5\2',
                                           text_pos=(-0.075, -0.04))
        self.counterfeitGagIcon = DirectFrame(parent=self.counterfeitText, relief=None, scale=0.85, text='+',
                                              text_pos=(-0.04, -0.07), text_scale=0.12,
                                              text_font=ToontownGlobals.getSignFont(), text_fg=(0, 1, 0, 1))
        text0 = self.counterfeitText.component('text0')
        bMin, bMax = text0.getTightBounds()
        self.counterfeitGagIcon.setPos(bMax[0] + 0.06, 0, 0.01)
        self.counterfeitSeq = None
        self.counterfeitSfx = loader.loadSfx('phase_3.5/audio/sfx/cc_s_sfx_bat_counterfeitUsed.ogg')

        self.hpChangeEvent = None
        self.hidByBattle = False
        self.toonInfoTooltip = None
        self.statusEffectTooltip = None
        self.laffMeter = None
        self.tag1 = None
        self.tag1Node = None
        self.tag2 = None
        self.tag2Node = None
        self.whichText = DirectLabel(parent=self, text='', pos=(0.13, 0, -0.15), text_scale=0.06, text_fg=Vec4(1, 1, 1, 1), text_shadow=Vec4(0, 0, 0, 1))
        self.effectSlots = self.guiElements[BattleGUI.TOON_PANEL_SLOTS]
        self.avatarEffects = []
        self.statusEffects = []
        self.offset = 0
        self.hoveredEffects = []
        self.bannedGags = {}
        self.lockInState = None
        # Set commands for the cycling buttons
        self.guiElements[BattleGUI.TOON_PANEL_CYCLE_BACK_BUTTON].configure(command=lambda: self.changeOffset(-1))
        self.guiElements[BattleGUI.TOON_PANEL_CYCLE_FORWARD_BUTTON].configure(command=lambda: self.changeOffset(1))
        # Create Toon Tooltip
        self.createToonInfoTooltip()
        # Set binds for the info button
        self.guiElements[BattleGUI.TOON_PANEL_INFO_BUTTON].bind(DGG.WITHIN, self.enterInfoButton)
        self.guiElements[BattleGUI.TOON_PANEL_INFO_BUTTON].bind(DGG.WITHOUT, self.exitInfoButton)
        # Set command for the info button
        self.guiElements[BattleGUI.TOON_PANEL_INFO_BUTTON].configure(command=self.activateInfoButton)
        self.createStatusEffectTooltip()
        self.setBin('sorted-gui-popup', GuiBinGlobals.BattleToonPanel)

        self.surrenderFlag = self.guiElements[BattleGUI.TOON_PANEL_SURRENDER_FLAG]
        self.surrenderFlag.setBin('sorted-gui-popup', GuiBinGlobals.BattleToonPanelFlag)
        self.surrenderFlag.hide()
        self.surrenderSeq = None
        self.surrenderState = False

        self.hide()

    def setLaffMeter(self, avatar):
        self.notify.debug('setLaffMeter: new avatar %s' % avatar.doId)
        if self.avatar == avatar:
            messenger.send(self.avatar.uniqueName('hpChange'), [avatar.getHp(), avatar.getMaxHp(), 1])
        else:
            self.cleanupLaffMeterAndNametag()
            self.avatar = avatar
            self.bannedGags = {}
            self.setNametag()
            self.set3dNametagVisiblity(False)
            self.laffMeter = OldLaffMeter.OldLaffMeter(avatar.style, avatar.getHp(), avatar.getMaxHp(), battleGui=True)
            self.laffMeter.setAvatar(self.avatar)
            self.laffMeter.reparentTo(self.guiElements[BattleGUI.TOON_PANEL_LAFF_METER_NODE])
            self.laffMeter.start()
            self.setHealthText(avatar.getHp(), avatar.getMaxHp())
            self.hpChangeEvent = self.avatar.uniqueName('hpChange')
            self.accept(self.hpChangeEvent, self.setHealthText)
            # Clean up the old tooltip and make a new one if its info has been set already.
            if self.toonInfoTooltip.loaded:
                self.toonInfoTooltip.destroy()
                self.createToonInfoTooltip()
            # Set up Toon info tooltip now that we have the avatar
            self.toonInfoTooltip.setToonInfo(self.avatar)

        self.updateStatusEffects()

    def setNametag(self):
        self.tag1Node = NametagFloat2d()
        self.avatar.nametag.add(self.tag1Node)
        self.tag1Node.hideNametag()
        self.tag1 = self.attachNewNode(self.tag1Node)
        self.tag1.setPosHprScale(-0.145, 0, 0.13, 0, 0, 0, 0.04, 0.04, 0.04)

        self.tag2Node = NametagFloat2d()
        self.avatar.nametag.add(self.tag2Node)
        self.tag2Node.hideChat()  # was: CName
        self.tag2Node.hideThought()
        self.tag2 = self.attachNewNode(self.tag2Node)
        self.tag2.setPosHprScale(-0.095, 0, 0.145, 0, 0, 0, 0.035, 0.035, 0.035)

    def set3dNametagVisiblity(self, visible):
        if self.avatar is None:
            return
        elif not hasattr(self.avatar, 'nametag'):
            return

        if visible:
            self.avatar.showNametag3d()
        else:
            self.avatar.hideNametag3d()

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
        self.toonInfoTooltip.hide()
        # Generate new effects for this round
        self.avatarEffects = self.avatar.getVisibleStatusEffects()
        self.statusEffects = BattleGUI.generateStatusEffects(self.avatarEffects)
        # Bind all the new effects to the hover over update functions.
        for i in range(len(self.statusEffects)):
            self.statusEffects[i].bind(DGG.WITHIN, self.enterStatusEffect, extraArgs=[i])
            self.statusEffects[i].bind(DGG.WITHOUT, self.exitStatusEffect, extraArgs=[i])
        BattleGUI.fitStatusEffectsIntoSlots(self.effectSlots, self.statusEffects, self.offset,
                                            self.guiElements[BattleGUI.TOON_PANEL_CYCLE_BACK_BUTTON],
                                            self.guiElements[BattleGUI.TOON_PANEL_CYCLE_FORWARD_BUTTON])

        # Check if we have any fancy new banned gags smiley face
        self.checkAvatarBannedGags()

    def checkAvatarBannedGags(self):
        affected = {track: [] for track in range(len(BattleGlobals.Tracks))}
        if not self.avatar:
            self.bannedGags = affected
            return

        # First handle effect that affects all levels
        gagLevelPunishment = self.avatar.getStatusEffectsOfSpecificType(StatusEffects.UseGagLevelSenderStatusEffect)
        if gagLevelPunishment:
            for effect in gagLevelPunishment:
                for track in range(len(BattleGlobals.Tracks)):
                    affected[track].extend([effect.gagLevel, effect.gagLevel2])

        # Now handle effect that affects indivudal tracks and levels
        gagLevelTrackPunishment = self.avatar.getStatusEffectsOfSpecificType(StatusEffects.UseGagLevelsWithTrackSenderStatusEffect)
        if gagLevelTrackPunishment:
            for effect in gagLevelTrackPunishment:
                for track in range(len(BattleGlobals.Tracks)):
                    gagLevel = int(effect.getGagLevel(track))
                    if gagLevel == -1:
                        continue
                    affected[track].append(gagLevel)

        self.bannedGags = affected

    def createToonInfoTooltip(self):
        self.toonInfoTooltip = BattleGUI.ToonInfoTooltip(
            parent=self,
            relief=None,
            pos=(0, 0, 0.3),
            scale=1.2
        )
        self.toonInfoTooltip.setBin("sorted-gui-popup", GuiBinGlobals.BattleInfoTooltip)
        self.toonInfoTooltip.hide()

    def enterInfoButton(self, _):
        self.toonInfoTooltip.show()

    def exitInfoButton(self, _):
        self.toonInfoTooltip.hide()

    def activateInfoButton(self):
        if self.avatar == self.townBattle.informationPanel.av:
            self.townBattle.informationPanel.clearPanel()
        else:
            panel = BattleGUI.ToonInformationPanel(relief=None)
            panel.setToonInfo(self.avatar)
            panel.setStatusEffects(self.avatarEffects)
            self.townBattle.informationPanel.setPanel(self.avatar, panel)

    def createStatusEffectTooltip(self):
        self.statusEffectTooltip = BattleGUI.StatusEffectTooltip(
            parent=self,
            relief=None,
            pos=(0, 0, 0.3)
        )
        self.statusEffectTooltip.setBin("sorted-gui-popup", GuiBinGlobals.BattleStatusInfoTooltip)
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
                                                self.guiElements[BattleGUI.TOON_PANEL_CYCLE_BACK_BUTTON],
                                                self.guiElements[BattleGUI.TOON_PANEL_CYCLE_FORWARD_BUTTON])

    def setHealthText(self, hp, maxHp, quietly = 0):
        self.healthText['text'] = TTLocalizer.TownBattleHealthText % {'hitPoints': hp,
                                                                      'maxHit': maxHp}

    def show(self):
        DirectFrame.show(self)
        self.hidByBattle = False
        if self.laffMeter:
            self.laffMeter.start()

    def hide(self, hidByBattle=False):
        DirectFrame.hide(self)
        self.hidByBattle = hidByBattle
        if self.laffMeter:
            self.laffMeter.stop()

    def updateLaffMeter(self, hp):
        if self.laffMeter:
            self.laffMeter.adjustFace(hp, self.avatar.getMaxHp())
        self.setHealthText(hp, self.avatar.getMaxHp())

    def setLockIn(self, lockedIn):
        if lockedIn == self.lockInState:
            return
        self.lockInState = lockedIn
        gui = base.loader.loadModel('phase_3.5/models/gui/battlegui/toon_panel')
        if lockedIn:
            image = gui.find('**/lock_locked')
        else:
            image = gui.find('**/lock_unlocked')
        self.guiElements[BattleGUI.TOON_PANEL_GAG_LOCK]['image'] = image
        gui.removeNode()

    def setCogs(self, cogs):
        self.cogs = cogs

    def setValues(self, index, track, level=None, numTargets=None, targetIndex=None, 
                  localNum=None, soaked=False,
                  luredSuits=None, markedSuits=None, soakedSuits=None,
                  untouchableIndices=None, untouchableByTrapIndices=None, townBattle=None):
        self.notify.debug('Toon Panel setValues: index=%s track=%s level=%s numTargets=%s targetIndex=%s localNum=%s soaked=%s luredSuits=%s' % (index,
         track, level, numTargets, targetIndex, localNum, soaked, luredSuits))
        if markedSuits is None:
            markedSuits = []
        if soakedSuits is None:
            soakedSuits = []
        if untouchableIndices is None:
            untouchableIndices = []
        if untouchableByTrapIndices is None:
            untouchableByTrapIndices = []

        gagOrder = GAG_TRACK_ORDER if townBattle is None or townBattle.battle is None else townBattle.battle.getGagOrder()

        suitId = 0
        target = None
        if track in ATTACK_TRACKS and track != AttackEnum.TOON_HEAL and isinstance(targetIndex, (int, list)):
            if isinstance(targetIndex, list) and targetIndex:
                if len(targetIndex) == 1 or track == AttackEnum.TOON_SQUIRT:
                    target = self.cogs[targetIndex[0]]
                else:
                    target = None
            elif 0 <= targetIndex < len(self.cogs):
                target = self.cogs[targetIndex]
            if target:
                suitId = target.doId

        # Update emblem visuals
        self.guiElements[BattleGUI.TOON_PANEL_CHOICE_EMBLEM].setValues(
            track, level, self.avatar, suitId, luredSuits, battle=True, target=target, townBattle=townBattle)

        # Handle choice text
        self.roundsText['text_scale'] = 0.075
        self.roundsText.hide()
        self.knockbackText.hide()
        self.sosText.hide()
        self.whichText.hide()
        for i, label in enumerate(self.zapJumpText):
            color = Vec4(0.85, 0, 0, 1) if i == 0 else Vec4(0.800, 0.808, 1, 1)
            label['text_fg'] = color
            label['text_align'] = TextNode.ACenter
            label.hide()
        updateTargetText = ''

        if track in (AttackEnum.TOON_FIRE, AttackEnum.TOON_SUE):
            self.whichText.show()
            updateTargetText = self.determineWhichText(
                numTargets, targetIndex, localNum, index, track, untouchableIndices, untouchableByTrapIndices)
        elif track == AttackEnum.TOON_NPC:
            if numTargets is not None:
                self.whichText.show()
                updateTargetText = self.determineWhichText(
                    numTargets, targetIndex, localNum, index, track, untouchableIndices, untouchableByTrapIndices)
        elif track in ATTACK_TRACKS:
            self.roundsText.show()
            if self.avatar:
                prestige = self.avatar.getTrackBonusLevel(track) >= 1
            else:
                prestige = False

            if numTargets is not None and targetIndex not in (None, [-1]) and localNum is not None:
                self.whichText.show()
                updateTargetText = self.determineWhichText(
                    numTargets, targetIndex, localNum, index, track, level=level, untouchableIndices=untouchableIndices,
                    untouchableByTrapIndices=untouchableByTrapIndices, prestige=prestige)
                self.roundsText['text_scale'] = 0.08

            if track == AttackEnum.TOON_LURE:
                self.roundsText['text_scale'] = 0.085
                self.roundsText['text_fg'] = (0.3, 0.6, 0.35, 1)
                self.roundsText['text_pos'] = (0.015, 0, 0)
                self.roundsText['text'] = str(NumRoundsLured[level])
            else:
                self.roundsText['text_pos'] = (0, 0, 0)
                if track == AttackEnum.TOON_HEAL:
                    self.roundsText['text_fg'] = (0, 0.85, 0, 1)
                    if self.avatar:
                        healAmount = int(getAvPropDamage(track, level, self.avatar.getExperience()[track], prestige))
                        healAmount = self.getToonDamageModifiers(track, healAmount, -1)
                        firstText = self.roundsText
                        if isGroup(track, level) and numTargets:
                            firstText['text'] = '+' + str(math.ceil(healAmount/(max(numTargets-1, 1))))
                        else:
                            firstText['text'] = '+' + str(healAmount)
                    else:
                        self.roundsText['text'] = '+0'
                else:
                    self.roundsText['text_fg'] = (0.85, 0, 0, 1)
                    if self.avatar:
                        damage = int(getAvPropDamage(track, level, self.avatar.getExperience()[track], prestige))
                    else:
                        damage = 0

                    if track == AttackEnum.TOON_TRAP:
                        if targetIndex is not None:
                            try:
                                cog = self.cogs[targetIndex]
                                if cog.isElite and not cog.isMiniboss():
                                    damage *= TrapEliteBonus
                                damage = math.ceil(damage)
                            except:
                                pass

                    elif track == AttackEnum.TOON_ZAP:
                        if targetIndex is not None:
                            targetIndex = [t for t in targetIndex if t not in untouchableIndices]
                            try:
                                if soaked:
                                    if settings['battle-information'] and len(targetIndex) > 1:
                                        self.roundsText.hide()
                                        # first, set all of the text for all of the zap jumps.
                                        targetsHit = len(targetIndex)
                                        totalJumpDamage = getZapJumpDamage(damage, prestige)
                                        perJumpDamage = int(math.ceil(totalJumpDamage / (targetsHit - 1)))
                                        for i in range(targetsHit):
                                            self.zapJumpText[i].show()
                                            dmgShow = self.getGeneralDamageModifiers(track, targetIndex[i], damage if i == 0 else perJumpDamage, markedSuits)
                                            self.zapJumpText[i]['text'] = f"-{math.ceil(dmgShow)}"

                                        # now, position all of the jump texts correctly.
                                        if targetsHit == 1:
                                            # only one hit, so just position the first zap jump text proper.
                                            self.zapJumpText[0].setPos(self.damageTextPositions[0])
                                        else:
                                            # we hit multiple targets, so we need to figure out what direction we go
                                            goingRight = (targetIndex[1] - targetIndex[0]) > 0
                                            if targetsHit == 2:
                                                # we hit two targets, so place the two zap texts accordingly.
                                                mainTextPos = 0
                                                sideTextPos = 1 if goingRight else 2
                                                self.zapJumpText[0].setPos(self.damageTextPositions[mainTextPos])
                                                self.zapJumpText[1].setPos(self.damageTextPositions[sideTextPos])
                                            elif targetsHit == 3:
                                                # we hit three targets, line the end zap texts accordingly.
                                                mainTextPos = 2 if goingRight else 1
                                                middleTextPos = 0
                                                sideTextPos = 1 if goingRight else 2
                                                self.zapJumpText[0].setPos(self.damageTextPositions[mainTextPos])
                                                self.zapJumpText[1].setPos(self.damageTextPositions[middleTextPos])
                                                self.zapJumpText[2].setPos(self.damageTextPositions[sideTextPos])
                                elif targetIndex and -1 not in targetIndex:
                                    damage = 0
                            except:
                                pass

                    if track != AttackEnum.TOON_ZAP or soaked:
                        useIndex = targetIndex
                        if track == AttackEnum.TOON_SQUIRT and isinstance(targetIndex, list):
                            useIndex = targetIndex[0]
                        damage = self.getGeneralDamageModifiers(track, useIndex, damage, markedSuits)

                    # Keep the original damage value for splash damage calculations.
                    baseDamage = damage

                    # Add the knockback after the mods have been applied.
                    if track in (AttackEnum.TOON_THROW, AttackEnum.TOON_SQUIRT) and luredSuits and suitId in luredSuits:
                        trackIndex = gagOrder.index(track)
                        if (luredSuits[suitId]['knockback']) and (
                            luredSuits[suitId]['unluredBy'] >= trackIndex or luredSuits[suitId]['unluredBy'] == 0
                        ):  # Translation: If the cog is lured and wasn't unlured already
                            damage += luredSuits[suitId]['knockback']

                    if track == AttackEnum.TOON_DROP:
                        if prestige and isinstance(targetIndex, int) and 0 <= targetIndex < len(self.cogs):
                            cog: ClashSuitBase = self.cogs[targetIndex]
                            effectIdSet = {effect.getEffectId()
                                           for effect in cog.getStatusEffects()
                                           if effect.getEffectId() not in DropPrestigeBlacklist
                                           and StatusEffectDefinitions.get(effect.getEffectId()).quality == DEBUFF}

                            # Add Marked to the set if they are being marked.
                            if targetIndex in markedSuits:
                                effectIdSet.add(SEE.EFFECT_MARKED_FOR_LAUGH)

                            # Add Dazed to the set if the cog is being unlured by trap.
                            if suitId in luredSuits and luredSuits[suitId]['unluredByTrack'] == AttackEnum.TOON_TRAP:
                                effectIdSet.add(SEE.EFFECT_SUIT_DAZED)

                            # Add Soaked to the set if the cog is gonna be soaked!!
                            if soakedSuits[targetIndex]:
                                effectIdSet.add(SEE.EFFECT_SUIT_SOAKED)

                            debuffCount = len(effectIdSet)
                            bonus = (DropPrestigeStartAmt + (DropPrestigeAmt * debuffCount)) if debuffCount else 1.0
                            damage = round(damage * bonus)

                    self.roundsText['text'] = '-' + str(damage)

                    if track == AttackEnum.TOON_SQUIRT and targetIndex is not None and len(targetIndex) > 1:
                        # Check if the left or right cogs were splashed.
                        splashLeft = max(targetIndex) > targetIndex[0]
                        splashRight = min(targetIndex) < targetIndex[0]

                        if splashLeft:
                            self.zapJumpText[1].setPos(self.damageTextPositions[1])
                            splashDamage = math.ceil(self.getSuitDefenseModifiers(max(targetIndex), baseDamage * SplashDamageAmt[prestige], markedSuits=markedSuits))
                            self.zapJumpText[1]['text'] = f"-{splashDamage}"
                            self.zapJumpText[1].show()

                        if splashRight:
                            self.zapJumpText[2].setPos(self.damageTextPositions[2])
                            splashDamage = math.ceil(self.getSuitDefenseModifiers(min(targetIndex), baseDamage * SplashDamageAmt[prestige], markedSuits=markedSuits))
                            self.zapJumpText[2]['text'] = f"-{splashDamage}"
                            self.zapJumpText[2].show()

        if updateTargetText:
            shouldShowSoak = track == AttackEnum.TOON_SQUIRT
            newText = ''
            # If we need to convert these to smaller x's/o's,
            # or if we need to convert these to smaller, blue markers for soak,
            # do that here.
            for i in range(len(updateTargetText)):
                newCharStr = ''
                if updateTargetText[i] in ('a', 'x', 'b', 'o'):
                    if updateTargetText[i] in ('a', 'b'):
                        newMarker = {'a': 'x', 'b': 'o'}.get(updateTargetText[i])
                        newCharStr = f'\1TextShrink\1{newMarker}\2'
                    else:
                        newCharStr = updateTargetText[i]
                    if shouldShowSoak:
                        newCharStr = f'\1soak_text\1{newCharStr}\2'
                else:
                    newCharStr += updateTargetText[i]
                newText += newCharStr
            updateTargetText = newText

            self.whichText['text'] = updateTargetText

    def getGeneralDamageModifiers(self, attackTrack: int, suitIndex, damage, markedSuits):
        # Calculates both toon and suit damage modifiers.
        damage = self.getToonDamageModifiers(attackTrack, damage, suitIndex)
        damage = self.getSuitDefenseModifiers(suitIndex, damage, attackTrack, markedSuits)
        return damage

    def getToonDamageModifiers(self, attackType: int, damage, suitIndex=-1):
        if suitIndex is None:
            target = None
        else:
            if isinstance(suitIndex, list):
                target = suitIndex[0]
            else:
                battle = self.townBattle.battle
                if not 0 <= suitIndex < len(battle.suits):
                    target = None
                else:
                    target = battle.suits[suitIndex]
        try:
            if self.avatar is not None:
                # If we have any gag effectiveness status effects, then affect the toon's damage here.
                # Sort these by their "priority" value, highest applies first
                attackEffects = sorted(
                    self.avatar.getStatusEffectsOfType(StatusEffects.AttackEffectivenessStatusEffect),
                    key=lambda x: x.SortPriority, reverse=True
                )
                for statusEffect in attackEffects:
                    if not statusEffect.isDisabled():
                        damage = statusEffect.handleAttackDamage(attackType, damage, target)
                damage = int(math.ceil(round(damage, 4)))
        except:
            pass

        return damage

    def getSuitDefenseModifiers(self, suitIndex, damage, attackTrack = 0, markedSuits: list = None):
        # suitIndex -> right is 0
        if markedSuits is None:
            markedSuits = []
        if type(suitIndex) == list or suitIndex is None:
            if not suitIndex:
                return damage
            suitIndex = suitIndex[0]
        battle = self.townBattle.battle
        if not 0 <= suitIndex < len(battle.suits):
            return damage
        suitAv = self.townBattle.battle.suits[suitIndex]
        defenseEffects = suitAv.getStatusEffectsOfType(StatusEffects.AvatarTakeModifiedDamageStatusEffect)
        for statusEffect in defenseEffects:
            if not isinstance(statusEffect, StatusEffects.LureStatusEffect):
                damage = statusEffect.handleAttackDamageTaken(damage, attackTrack, self.avatar)
        if suitIndex in markedSuits and attackTrack not in (AttackEnum.TOON_TRAP, AttackEnum.TOON_THROW):
            damage *= BattleGlobals.ThrowMarkPercent
        return math.ceil(round(damage, 4))

    def determineWhichText(self, numTargets, targetIndex, localNum, index, track,
                           untouchableIndices, untouchableByTrapIndices, level=0, prestige=False):
        returnStr = ''
        targetList = list(range(numTargets))
        targetList.reverse()
        # Un-comment this if we want the prestige marker stuff back
        # try:
        #     if self.avatar and self.avatar.getTrackBonusLevel(track) >= 1:
        #         marker = 'O'
        #     else:
        #         marker = 'X'
        # except:
        marker = 'X'
        marker_one = 'x'  # if marker == 'X' else 'o'
        marker_two = 'a'  # if marker == 'X' else 'b'
        extra_marker = 'o'

        if isinstance(targetIndex, list):
            # Create markers depending on the list
            if targetIndex == [-1]:
                return ''

            targetLength = len(targetIndex)
            if targetLength >= 0:
                for target in targetList:
                    if (
                        target in untouchableIndices and track not in (AttackEnum.TOON_HEAL, AttackEnum.TOON_TRAP)) or (
                        target in untouchableByTrapIndices and track == AttackEnum.TOON_TRAP
                    ):
                        returnStr += '-'
                        continue
                    if target == targetIndex[0]:
                        returnStr += marker
                    else:
                        marked = False
                        if targetLength >= 2:
                            if target == targetIndex[1]:
                                returnStr += marker_one
                                marked = True
                        if targetLength >= 3:
                            if target == targetIndex[2]:
                                returnStr += marker_two
                                marked = True
                        if not marked:
                            returnStr += '-'
        else:
            shouldShowSoak = track == AttackEnum.TOON_SQUIRT
            for i in targetList:
                if (
                    i in untouchableIndices and track not in (AttackEnum.TOON_HEAL, AttackEnum.TOON_TRAP)) or (
                    i in untouchableByTrapIndices and track == AttackEnum.TOON_TRAP
                ):
                    returnStr += '-'
                    continue
                if targetIndex == -1:
                    returnStr += marker
                elif targetIndex == -2:
                    if i == index:
                        # if track == AttackEnum.TOON_HEAL and prestige:
                        #     returnStr += extra_marker
                        # else:
                        returnStr += '-'
                    else:
                        returnStr += marker
                elif targetIndex >= 0 and targetIndex <= BattleBase.MaxBattleAvatars - 1:
                    if i == targetIndex:
                        returnStr += marker
                    else:
                        # If we should show soak and they're within 1 index of the hit target
                        if shouldShowSoak and abs(targetIndex - i) <= 1:
                            returnStr += extra_marker
                        else:
                            # if track == AttackEnum.TOON_HEAL and prestige and i == index:
                            #     returnStr += extra_marker
                            # else:
                            returnStr += '-'
                else:
                    self.notify.error('Bad target index: %s' % targetIndex)

        return returnStr

    def cleanup(self):
        self.notify.debug('Cleaning up TownBattleToonPanel!')
        self.ignoreAll()
        if self.surrenderSeq:
            self.surrenderSeq.finish()
            self.surrenderSeq = None
        self.surrenderFlag = None

        self.cleanupLaffMeterAndNametag()
        del self.townBattle

        for effect in self.statusEffects:
            if effect.bgSequence:
                effect.bgSequence.finish()
            effect.destroy()
        del self.statusEffects

        if self.counterfeitSeq:
            self.counterfeitSeq.finish()
            self.counterfeitSeq = None
        self.counterfeitHolder = None
        self.counterfeitGagIcon = None
        self.counterfeitText = None
        self.counterfeitSfx.stop()
        self.counterfeitSfx = None

        DirectFrame.destroy(self)

    def cleanupLaffMeterAndNametag(self):
        self.notify.debug('Cleaning up laffmeter and nametag!')
        self.ignore(self.hpChangeEvent)
        if self.avatar is not None and self.tag1 is not None:
            self.set3dNametagVisiblity(True)
            if hasattr(self.avatar, 'nametag'):
                self.avatar.nametag.removeNametag(self.tag1Node)
                self.avatar.nametag.removeNametag(self.tag2Node)
            self.tag1.removeNode()
            self.tag2.removeNode()
            self.tag1 = None
            self.tag1Node = None
            self.tag2 = None
            self.tag2Node = None
        if self.laffMeter:
            self.bannedGags = {}
            self.avatar = None
            self.laffMeter.destroy()
            self.laffMeter = None

    def doCounterfeitAnimation(self, track, level):
        if self.counterfeitSeq:
            self.counterfeitSeq.finish()
            self.counterfeitSeq = None

        newGagIcon = base.localAvatar.inventory.buttonLookup(track, level).copyTo(NodePath())
        self.counterfeitGagIcon['geom'] = newGagIcon
        self.counterfeitSeq = Sequence(
            Func(self.counterfeitHolder.setPos, (0, 0, 0.18)),
            Func(self.counterfeitHolder.setColorScale, (1, 1, 1, 0)),
            Func(base.playSfx, self.counterfeitSfx, volume=0.45),
            Parallel(
                LerpPosInterval(self.counterfeitHolder, 0.4, (0, 0, 0.26), blendType='easeInOut'),
                LerpColorScaleInterval(self.counterfeitHolder, 0.3, (1, 1, 1, 1), blendType='easeIn'),
            ),
            Wait(1.2),
            Parallel(
                Sequence(
                    LerpPosInterval(self.counterfeitHolder, 0.4, (0, 0, 0.43), blendType='easeIn')
                ),
                LerpColorScaleInterval(self.counterfeitHolder, 0.3, (1, 1, 1, 0), blendType='easeIn'),
            ),
            Func(self.counterfeitHolder.hide),
        )
        self.counterfeitSeq.start()
        self.counterfeitHolder.show()

    def showAfkLabel(self):
        emblem = self.guiElements[BattleGUI.TOON_PANEL_CHOICE_EMBLEM]
        emblem.configure(
            text="AFK",
            text_pos=(0, 0.4),
            text_scale=0.2,
            text_font=ToontownGlobals.getBuildingNametagFont(),
            text_fg=(1, 1, 1, 1),
        )

    def updateSurrenderState(self, surrenderState, instant=False):
        changeState = self.surrenderState != surrenderState
        self.surrenderState = surrenderState
        if not changeState:
            return

        if self.surrenderSeq:
            self.surrenderSeq.finish()

        if instant:
            self.surrenderFlag.show() if surrenderState else self.surrenderFlag.hide()
            return

        if self.surrenderState:
            self.surrenderSeq = Sequence(
                Func(self.surrenderFlag.setPos, (-0.17, 0, 0.0)),
                Func(self.surrenderFlag.setScale, 0.01),
                Func(self.surrenderFlag.show),
                Parallel(
                    LerpScaleInterval(self.surrenderFlag, 0.2, 0.3, blendType='easeOut'),
                    LerpPosInterval(self.surrenderFlag, 0.2, (-0.45, 0, 0.28), blendType='easeOut'),
                ),
            )
        else:
            self.surrenderSeq = Sequence(
                Func(self.surrenderFlag.setPos, (-0.45, 0, 0.28)),
                Func(self.surrenderFlag.setScale, 0.3),
                Parallel(
                    LerpScaleInterval(self.surrenderFlag, 0.2, 0.01, blendType='easeIn'),
                    LerpPosInterval(self.surrenderFlag, 0.2, (-0.17, 0, 0.0), blendType='easeIn'),
                ),
                Func(self.surrenderFlag.hide),
            )

        self.surrenderSeq.start()
