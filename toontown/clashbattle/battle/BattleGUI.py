import math
from typing import Optional

from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.gui.ChatBubbleTextFrame import ChatBubbleTextFrame
from toontown.gui.DiceButton import DiceButton
from toontown.inventory.registry.IOURegistry import IOURegistry
from toontown.modifiers.ModifierEnums import ModifierType
from toontown.modifiers.classes.GagsContentSyncModifier import GagsContentSyncModifier
from toontown.toon.ToonHead import ToonHead
from toontown.toon.gui import GuiBinGlobals
from toontown.toon.npc import NPCToons # Until NPCs are added we will use Reia's NPCToon port file
from toontown.toon.socialpanel.SocialPanelGlobals import sp_gui
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.clashbattle.battle import BattleGlobals
from toontown.gui.TTGui import ExtendedOnscreenText, ScalingButton, ScrollWheelFrame, kwargsToOptionDefs
from toontown.clashbattle.battle.BattleGUIGlobals import *
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG, StatusEffects, SEE
from toontown.clashbattle.battle import SuitBattleGlobals
from toontown.utils import Nodes
from toontown.utils.text import getTextScaleAfterLength, capTextScaleToWidth


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
# Enum for GUI element dictionary keys #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
# Battle Inventory Specific Enums
BATTLE_FRAME = 0
TRACK_HOLDER_FRAME = 1

# Gag Track Enums
TRACKS_FRAME = 100
TRACKS_ROWS = 101
TRACKS_NAME_LABELS = 102
TRACKS_EXPERIENCE_BARS = 103
TRACKS_PRESTIGE_STARS = 104
TRACKS_GAG_BUTTONS = 105
TRACKS_TRACK_HOVERS = 106
TRACKS_SUBFRAMES = 107

# Details Panel Enums
DETAILS_FRAME = 200
DETAILS_EMBLEM = 201
DETAILS_NAME_LABEL = 202
DETAILS_AMOUNT_LABEL = 203
DETAILS_DATA_LABEL = 204

# Tab Enums
TABS_FRAME = 300
TABS_PASS = 301
TABS_RUN = 302
TABS_SOS = 303
TABS_SUE = 304
TABS_FIRE = 305
TABS_COUNTERFEIT = 306
TABS_SURRENDER = 307
TABS_SURRENDER_FLAG = 308
TABS_COUNTERFEIT_BACK = 309

# Total Gag Panel Enums
TOTAL_GAGS_FRAME = 400
TOTAL_GAGS_TITLE_LABEL = 401
TOTAL_GAGS_NUMBER_LABEL = 402

# Suit Panel Enums
SUIT_PANEL_FRAME = 500
SUIT_PANEL_SLOTS = 501
SUIT_PANEL_CYCLE_BACK_BUTTON = 502
SUIT_PANEL_CYCLE_FORWARD_BUTTON = 503
SUIT_PANEL_HEALTH_BAR = 504
SUIT_PANEL_HEALTH_BAR_LABEL = 505
SUIT_PANEL_HEALTH_BAR_CLIPPING_PLANE = 506
SUIT_PANEL_LEVEL_LABEL = 507
SUIT_PANEL_INFO_BUTTON = 508

# Toon Panel Enums
TOON_PANEL_FRAME = 600
TOON_PANEL_SLOTS = 601
TOON_PANEL_CYCLE_BACK_BUTTON = 602
TOON_PANEL_CYCLE_FORWARD_BUTTON = 603
TOON_PANEL_LAFF_METER_NODE = 604
TOON_PANEL_CHOICE_EMBLEM = 605
TOON_PANEL_GAG_LOCK = 606
TOON_PANEL_INFO_BUTTON = 607
TOON_PANEL_SURRENDER_FLAG = 608

Tracks = BattleGlobals.Tracks
TrackColors = BattleGlobals.TrackColors
Levels = BattleGlobals.Levels
AvPropsNew = BattleGlobals.AvPropsNew

# Text properties
tpm = TextPropertiesManager.getGlobalPtr()

# Knockback
tp_knockBack = TextProperties()
tp_knockBack.setTextColor(*BattleGlobals.HurtColor_Orange, 1)
tp_knockBack.setFont(ToontownGlobals.getSignFont())
tpm.setProperties("Knockback", tp_knockBack)

# Self heal
tp_selfHeal = TextProperties()
tp_selfHeal.setTextColor(*BattleGlobals.HealColor, 1)
tp_selfHeal.setFont(ToontownGlobals.getSignFont())
tpm.setProperties("SelfHeal", tp_selfHeal)

# region ChatBubbleTextFrame textproperties

# These text properties have a glyph shift to make them work properly with ChatBubbleTextFrame.

# Battle Tracks
for i in range(len(Tracks)):
    trackProperty = TextProperties()
    trackProperty.setTextColor(*TrackColors[i], 1.0)
    trackProperty.setFont(ToontownGlobals.getSignFont())
    trackProperty.setGlyphShift(-0.06)
    tpm.setProperties(f"GagTrack_{Tracks[i]}", trackProperty)

battleInfoPositive = TextProperties()
battleInfoPositive.setTextColor(*BattleGlobals.HealColor, 1.0)
battleInfoPositive.setFont(ToontownGlobals.getSignFont())
battleInfoPositive.setGlyphShift(-0.06)
tpm.setProperties("BattleInfo_Positive", battleInfoPositive)

battleInfoKnockback = TextProperties()
battleInfoKnockback.setTextColor(*BattleGlobals.HurtColor_Orange, 1.0)
battleInfoKnockback.setFont(ToontownGlobals.getSignFont())
battleInfoKnockback.setGlyphShift(-0.06)
tpm.setProperties("BattleInfo_Knockback", battleInfoKnockback)

battleInfoCombo = TextProperties()
battleInfoCombo.setTextColor(*BattleGlobals.HurtColor_Yellow, 1.0)
battleInfoCombo.setFont(ToontownGlobals.getSignFont())
battleInfoCombo.setGlyphShift(-0.06)
tpm.setProperties("BattleInfo_Combo", battleInfoCombo)

battleInfoDamage = TextProperties()
battleInfoDamage.setTextColor(*BattleGlobals.HurtColor, 1.0)
battleInfoDamage.setFont(ToontownGlobals.getSignFont())
battleInfoDamage.setGlyphShift(-0.06)
tpm.setProperties("BattleInfo_Damage", battleInfoDamage)

# endregion


# -=-=-=-=-=-=-=-=-= #
# Battle GUI Classes #
# -=-=-=-=-=-=-=-=-= #
class ChoiceEmblem(DirectFrame):
    def __init__(self, parent=aspect2d, ccpScale: float = 0.0026, **kw):
        gagSelectionGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
        self.undecidedImage = gagSelectionGui.find('**/emblem_question')
        self.blankImage = gagSelectionGui.find('**/emblem_gag')
        self.blankPresImage = NodePath()
        self.blankPresImage = self.blankImage.copyTo(self.blankPresImage)
        self.passImage = gagSelectionGui.find('**/pass_icon')

        optiondefs = kwargsToOptionDefs(
            relief=None,
        )

        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, parent)
        self.initialiseoptions(ChoiceEmblem)
        self.geomScale = 3

        # State attributes
        self.track: Optional[int] = None
        self.level: Optional[int] = None
        self.luredSuits: Optional[list] = None
        self.emblemMoveSeq = None
        self.emblemLeaveSeq = None
        self.avatar = None

        self.hoverFrame = None

        # Create clipping planes.
        self.right_ccp = Nodes.SemicircleClippingPlane(segments=14)
        self.right_ccpNP = self.attachNewNode(self.right_ccp.node())
        self.right_ccpNP.setScale(ccpScale)
        self.left_ccp = Nodes.SemicircleClippingPlane(segments=14)
        self.left_ccpNP = self.attachNewNode(self.left_ccp.node())
        self.left_ccpNP.setScale(ccpScale)
        self.left_ccpNP.setH(180)
        self.left_ccpNP.setPos(-0.011, 0, 0)

        self.emblem = self.makeEmblemBase()
        self.enableOutlines = True
        self.outlines = []
        self.updateOutline()

        self.presBgTexture = loader.loadTexture('phase_3.5/maps/battlegui/pres_scroll_bg.png')
        self.presBgTexture.setMinfilter(Texture.FTLinearMipmapLinear)
        self.presBgTexture.setMagfilter(Texture.FTLinear)

        self.presBgScroll = TextureStage('presScroll')
        self.presBgScroll.setMode(TextureStage.MModulate)
        self.presUVScroll = 0

        self.pauseTexMatrix = True
        self.texActive = False
        self.bgColorSeq = None

        texMatrixScrollTime = 1 / 15

        def rollTexMatrix(task):
            task.delayTime = texMatrixScrollTime

            if self.pauseTexMatrix:
                if self.texActive:
                    self.blankPresImage.clearTexture(self.presBgScroll)
                    self.texActive = False
                return task.again

            if not self.texActive:
                self.texActive = True
                self.blankPresImage.setTexture(self.presBgScroll, self.presBgTexture)

            image = self['image']
            image.setColor(self['image_color'])
            image.setTexScale(self.presBgScroll, 4, 4, 1)
            image.setTexOffset(self.presBgScroll, self.presUVScroll, -self.presUVScroll)
            self.presUVScroll -= 0.0025
            if self.presUVScroll < -1:
                self.presUVScroll = 0
            self['image'] = image

            return task.again

        taskMgr.add(rollTexMatrix, self.uniqueName('scroll-task'))

        # Cleanup
        gagSelectionGui.removeNode()

        self['image'] = self.undecidedImage

    def destroy(self):
        self.finishBgSeq()
        DirectFrame.destroy(self)
        taskMgr.remove(self.uniqueName('scroll-task'))
        del self.bgColorSeq
        del self.presBgTexture
        del self.undecidedImage
        del self.blankImage
        del self.blankPresImage
        del self.passImage
        del self.emblem
        del self.luredSuits
        del self.avatar

    def setValues(self, track: int, level: int = None, avatar=None,
                  suitId: int = 0, luredSuits: dict = None, battle: bool = False,
                  target=None, townBattle=None):
        # Only change the values if the new ones are different.
        if self.track == track and self.level == level and self.luredSuits == luredSuits:
            return

        self.finishBgSeq()

        gagOrder = BattleGlobals.GAG_TRACK_ORDER if townBattle is None or townBattle.battle is None else townBattle.battle.getGagOrder()

        # Figure out state.
        trackChanged = self.track != track
        levelChanged = self.level != level
        levelDecreased = False
        if None not in (level, self.level):
            levelDecreased = level < self.level

        self.track = track
        self.level = level
        self.luredSuits = luredSuits
        self.avatar = avatar
        self.geomScale = 3

        if track != AttackEnum.TOON_PASS:
            # Clear out afk label
            self['text'] = None

        # Is this prestige?
        prestige = False
        if avatar is not None and (0 <= track < len(Tracks)):
            prestige = avatar.getTrackBonusLevel(track) >= 1

        if trackChanged or levelChanged:
            direction = -1  # gags going in left
            if levelDecreased:
                direction = 1  # gags going in right

            # Discard the old emblem.
            self.discardEmblem(direction)

            # Make a new emblem.
            self.emblem = self.makeEmblemBase()
            self.introduceEmblem(direction)

        # If we aren't attacking, make the undecided image now.
        if track in (AttackEnum.TOON_NO_ATTACK, AttackEnum.TOON_UN_ATTACK):
            # ? image for no choice.
            self['image'] = self.undecidedImage
            self['image_color'] = (1, 1, 1, 1)
            return

        # Set the blank image otherwise.
        self.pauseTexMatrix = not prestige
        if not prestige:
            self['image'] = self.blankImage
        else:
            self['image'] = self.blankPresImage

        # Set the hover label.
        if battle:
            def updateLabel(show: bool, *args):
                if not self.hoverFrame:
                    return
                if show:
                    self.hoverFrame.show()
                else:
                    self.hoverFrame.hide()

            if self.hoverFrame:
                self.hoverFrame.destroy()
            self.hoverFrame = ChatBubbleTextFrame(
                parent=self.emblem, pos=(0, 0, 0.45), scale=0.15,
            )
            self.hoverFrame.scaleBeforeScalePoint = True
            self.hoverFrame.setBin('sorted-gui-popup', GuiBinGlobals.HoverTextBin)
            self.hoverFrame.hide()

            self.emblem.attackInfo = self.hoverFrame

            headLabel = DirectLabel(parent=self.emblem, relief=None, text='hey', text_scale=0.5)
            headLabel.setColorScale(0, 0, 0, 0)
            headLabel['state'] = DGG.NORMAL
            headLabel.setBin('sorted-gui-popup', 450)
            headLabel.bind(DGG.ENTER, updateLabel, [True])
            headLabel.bind(DGG.EXIT, updateLabel, [False])

            self.emblem.npcInfo = headLabel

            text = ""

        # Hide prestige stars if cringe.
        if track not in BattleGlobals.ATTACK_TRACKS:
            self.pauseTexMatrix = True

        # Overlay text or geom based on choice.
        if track == AttackEnum.TOON_PASS:
            r, g, b = BattleGlobals.PassColor
            self['image_color'] = (r, g, b, 1)
            self.emblem['geom'] = self.passImage
            self.geomScale /= 8.0
            self.emblem['geom_scale'] = self.geomScale
        elif track in (AttackEnum.TOON_SUE, AttackEnum.TOON_FIRE):
            r, g, b = (BattleGlobals.FireColor if track == AttackEnum.TOON_FIRE else BattleGlobals.SueColor)
            self['image_color'] = (r, g, b, 1)
            statusEffectImages = loader.loadModel('phase_3.5/models/gui/battlegui/status_effects')
            battleIcon = statusEffectImages.find(f'**/{"pinkslip" if track == AttackEnum.TOON_FIRE else "sued"}_icon')
            statusEffectImages.removeNode()
            self.emblem['geom'] = battleIcon
            self.geomScale = 0.5
            self.emblem['geom_scale'] = self.geomScale
        elif track == AttackEnum.TOON_NPC:
            r, g, b = BattleGlobals.SOSColor
            self['image_color'] = (r, g, b, 1)
            iou = IOURegistry[level]
            npcToon = NPCToons.NPCToonDict.get(iou.getNpcId())
            head = ToonHead()
            head.setupHead(npcToon.getToonDNA(), forGui=1)
            head.fitAndCenterHead(0.45, forGui=1)

            hNode = self.emblem.attachNewNode('head', 20)
            head.reparentTo(hNode)
            self.emblem.headModel = head

            if battle:
                uses = iou.getUses()
                track = iou.getGagTrack()
                modifier = iou.getBoost()

                damageType = {
                    AttackEnum.TOON_LURE: "Knockback",
                    AttackEnum.TOON_HEAL: "Heal"
                }.get(track, "Damage")

                if 0 <= track < len(BattleGlobals.Tracks):
                    attackName = f"\1GagTrack_{TTLocalizer.BattleGlobalTracks[track]}\1{TTLocalizer.BattleGlobalTracksUpper[track]}\2 "
                else:
                    attackName = ''

                fullAttackName = f"{attackName}Gag" if uses == 1 else f"{uses} {attackName}Gags"

                text = f"\1deepBlue\1{damageType}:\2 \1{'BattleInfo_Positive'}\1+{modifier}\2\nNext {fullAttackName}"

                self.emblem["text"] = npcToon.name
                self.emblem["text_pos"] = (0, 0.4)
                self.emblem["text_font"] = ToontownGlobals.getBuildingNametagFont()

            self.geomScale = 0.25
        elif track in BattleGlobals.ATTACK_TRACKS:
            r, g, b = TrackColors[track]
            self['image_color'] = (r, g, b, 1)
            geom = base.localAvatar.inventory.buttonLookup(track, level)
            self.emblem['geom'] = geom
            self.emblem['geom_scale'] = self.geomScale
            self.emblem['geom_pos'] = (0, 0, 0)

            # Handle UV texture if the gag is prestiged.
            if avatar is not None:
                prestige = avatar.getTrackBonusLevel(track) >= 1
                baseDamage = BattleGlobals.getAvPropDamage(track, level, avatar.getExperience()[track], prestige)
                finalDamage = self.getToonDamageModifiers(avatar, track, baseDamage, target)
            else:
                prestige = False
                baseDamage = 0
                finalDamage = 0

            if battle:
                if track in (AttackEnum.TOON_THROW, AttackEnum.TOON_SQUIRT) and suitId and luredSuits:
                    trackIndex = gagOrder.index(track)
                    if (luredSuits[suitId]['knockback']) and (
                        luredSuits[suitId]['unluredBy'] >= trackIndex or luredSuits[suitId]['unluredBy'] == 0
                    ):  # Translation: If the cog is lured and wasn't unlured already
                        text += f"\1deepBlue\1Damage:\2 \1BattleInfo_Damage\1{-finalDamage}\2\n"
                        text += f"\1deepBlue\1Knockback:\2 \1BattleInfo_Knockback\1{-luredSuits[suitId]['knockback']}\2\n"

                if track == AttackEnum.TOON_THROW and prestige:
                    text += f"\1deepBlue\1Self Heal:\2 \1BattleInfo_Positive\1+{int(math.ceil(finalDamage * BattleGlobals.ThrowPresHealPercent))}\2\n"

                elif track == AttackEnum.TOON_LURE:
                    kbDamage = finalDamage
                    if avatar is not None:
                        for boost in avatar.getStatusEffectsOfType(StatusEffects.LureKnockbackModifierStatusEffect):
                            kbDamage = boost.handleLureKb(kbDamage)
                    kbDamage = int(math.ceil(round(kbDamage, 4)))
                    text += f"\1deepBlue\1Knockback:\2 \1BattleInfo_Knockback\1{-kbDamage}\2\n"

                elif track == AttackEnum.TOON_HEAL:
                    text += f"\1deepBlue\1Self Heal:\2 \1BattleInfo_Positive\1+{int(math.ceil(finalDamage * BattleGlobals.ToonupSelfHealAmt[prestige]))}\2\n"
        elif track == AttackEnum.TOON_DICE:
            geom = DiceButton.getDicePipIcon(level + 1)
            self.emblem['geom'] = geom
            self.geomScale = 0.42
            self.emblem['geom_scale'] = self.geomScale
            self.emblem['geom_pos'] = (0, 0, 0)

        self.checkAvatarBannedGags(townBattle, avatar, track, level)

        if battle:
            self.hoverFrame.setText(text)
            if text:
                self.hoverFrame.scaleToText()

        self.updateOutline()
        # endregion

    def checkAvatarBannedGags(self, townBattle, avatar, track, level):
        if not townBattle:
            return
        if not avatar:
            return

        bannedGags = townBattle.getToonBannedGags(avatar)
        if bannedGags and level in bannedGags.get(track, []):
            def setImageColor(value):
                g = lerp(0.35, 0.6, value)
                b = lerp(0.35, 0.6, value)
                self['image_color'] = (1, g, b, 1)

            self.bgColorSeq = Sequence(
                LerpFunctionInterval(setImageColor, 0.75, fromData=1, toData=0, blendType='easeInOut'),
                LerpFunctionInterval(setImageColor, 0.75, fromData=0, toData=1, blendType='easeInOut')
            )
            self.bgColorSeq.loop()

    def finishBgSeq(self):
        if self.bgColorSeq:
            self.bgColorSeq.finish()
            self.bgColorSeq = None

    def makeEmblemBase(self) -> DirectFrame:
        frame = DirectFrame(
            parent=self,
            relief=None,
            text='',
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_pos=(-0.012, -0.055),
            text_scale=0.2,
            geom=None,
            geom_scale=1,
        )
        frame.setBin('sorted-gui-popup', GuiBinGlobals.BattleChoiceEmblem)
        return frame

    def discardEmblem(self, direction = -1):
        if not self.emblem:
            return
        if self.emblemMoveSeq:
            self.emblemMoveSeq.finish()
            self.emblemMoveSeq = None
        self.emblem.clearClipPlane()
        ccp = self.right_ccp if direction == 1 else self.left_ccp
        ccp.attachNodeToPlanes(self.emblem)

        def cleanupEmblem(emblem):
            if not emblem:
                return
            if getattr(emblem, "headModel", None):
                emblem.headModel.detachNode()
                del emblem.headModel
            if getattr(emblem, "npcInfo", None):
                emblem.npcInfo.destroy()
                del emblem.npcInfo
            if getattr(emblem, "attackInfo", None):
                emblem.attackInfo.destroy()
                del emblem.attackInfo
            emblem.destroy()

        self.emblemLeaveSeq = Sequence(
            LerpPosInterval(
                nodePath=self.emblem,
                duration=0.1,
                pos=(direction * 0.5, 0, 0),
                blendType='easeOut',
            ),
            Func(cleanupEmblem, self.emblem),
        )
        self.emblemLeaveSeq.start()
        if settings['reduce-gui-movement']:
            self.emblemLeaveSeq.finish()
            self.emblemLeaveSeq = None

    def introduceEmblem(self, direction = -1):
        if not self.emblem:
            return
        if self.emblemMoveSeq:
            return
        self.emblem.clearClipPlane()
        ccp = self.right_ccp if direction == -1 else self.left_ccp
        ccp.attachNodeToPlanes(self.emblem)

        def clearEmblemClipPlane():
            if getattr(self, 'emblem', None) and not self.emblem.isEmpty():
                self.emblem.clearClipPlane()

        self.emblemMoveSeq = Sequence(
            LerpPosInterval(
                nodePath=self.emblem,
                duration=0.1,
                pos=(0, 0, 0),
                startPos=(direction * -0.5, 0, 0),
                blendType='easeOut',
            ),
            Func(clearEmblemClipPlane),
        )
        self.emblemMoveSeq.start()
        if settings['reduce-gui-movement']:
            self.emblemMoveSeq.finish()
            self.emblemMoveSeq = None

    def getToonDamageModifiers(self, avatar, attackType: int, damage, target):
        attackEffects = avatar.getStatusEffectsOfType(StatusEffects.AttackEffectivenessStatusEffect)
        for statusEffect in attackEffects:
            if not statusEffect.isDisabled():
                damage = statusEffect.handleAttackDamage(attackType, damage, target)
        damage = int(math.ceil(round(damage, 4)))
        return damage

    def clearValues(self):
        # Clear stored values
        self.track = None
        self.level = None

        # Clear the image and text being shown on top of the emblem.
        self.finishBgSeq()
        self.discardEmblem()
        self.emblem = self.makeEmblemBase()
        self.emblem['geom'] = None
        self.emblem['text'] = ''
        self['image'] = self.undecidedImage
        self['image_color'] = (1, 1, 1, 1)

        # Upadte the outline.
        self.updateOutline()

    def updateOutline(self):
        # Clear the outline on the gag.
        if not self.enableOutlines:
            return
        if not self.emblem:
            return
        for outline in self.outlines:
            outline.destroy()
        self.outlines = []
        # Get a copy of the emblem's geom.
        geomCopy = None
        geomScale = 1
        if self.emblem['geom']:
            geomCopy = NodePath()
            geomCopy = self.emblem['geom'].copyTo(geomCopy)
            geomCopy.setColorScale(0.439, 0.439, 0.439, 0.1)
            geomCopy.flattenStrong()
            geomScale = self.geomScale
        # Create positioning for the frames.
        dist = 0.012
        y = -0.1
        pos = (
            (dist, y, dist), (dist, y, -dist), (-dist, y, dist), (-dist, y, -dist),
            (0, y, dist), (0, y, -dist), (dist, y, 0), (-dist, y, 0),
        )
        # Create all frames using the geom copy.
        for position in pos:
            frame = DirectFrame(parent=self.emblem, relief=None, geom=geomCopy, geom_scale=geomScale, pos=position)
            frame.setBin('sorted-gui-popup', GuiBinGlobals.BattleChoiceEmblem - 1)
            self.outlines.append(frame)


class TargetingGUI(DirectFrame):
    def __init__(self, parent=aspect2d, townBattle=None, **kw):
        optiondefs = (
            ('relief', None, None),
        )

        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, parent)
        self.initialiseoptions(TargetingGUI)

        self.lockedIn = False
        self.townBattle = townBattle

        targetingGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/targeting')
        toonPanelGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/toon_panel')
        self.unlockedImage = toonPanelGui.find('**/lock_unlocked')
        self.lockedImage = toonPanelGui.find('**/lock_locked')

        # Store these to set on the lock button as needed
        self.notLockedInImageList = (targetingGui.find('**/lock_toggle_hover'),
                                     targetingGui.find('**/lock_toggle_press'),
                                     targetingGui.find('**/lock_toggle_hover'))
        self.lockedInImageList = (targetingGui.find('**/lock_toggle_neutral'),
                                  targetingGui.find('**/lock_toggle_press'),
                                  targetingGui.find('**/lock_toggle_hover'))

        self.backButton = DirectButton(
            parent=self,
            relief=None,
            image=(
                targetingGui.find('**/back_neutral'),
                targetingGui.find('**/back_press'),
                targetingGui.find('**/back_hover')
            ),
            image_scale=(1, 1, 0.5),
            text=TTLocalizer.TownBattleBack,
            text_fg=(0.157, 0.153, 0.306, 1),
            text_pos=(0.03, -0.062),
            text_scale=0.16,
            frameSize=(-0.5, 0.5, -0.18, 0.17),
            pos=(-0.035, 0, -0.59),
            scale=0.85
        )

        self.lockInButton = DirectButton(
            parent=self,
            relief=None,
            image=self.notLockedInImageList,
            image_scale=(1, 1, 0.5),
            text='TEXT MISSING',
            text_pos=(0.03, -0.065),
            text_scale=0.24,
            frameSize=(-0.33, 0.47, -0.25, 0.25),
            pos=(0.65, 0, -0.3),
            scale=0.5
        )

        self.emblem = ChoiceEmblem(
            parent=self,
            relief=None,
            pos=(0, 0, 0.14)
        )

        self.background = DirectFrame(
            parent=self,
            relief=None,
            image=targetingGui.find('**/targeting_main'),
            text='TEXT MISSING',
            text_font=ToontownGlobals.getMinnieFont(),
            text_fg=(0.965, 0.784, 0.286, 1),
            text_shadow=(0, 0, 0, 1),
            text_pos=(0, -0.345),
            text_scale=0.13
        )

        self.lock = DirectFrame(
            parent=self,
            relief=None,
            image=toonPanelGui.find('**/lock_unlocked'),
            image_scale=(0.5, 1, 1),
            pos=(0.275, 0, -0.02),
            scale=0.5
        )
        self.lock.setBin('sorted-gui-popup', GuiBinGlobals.BattleChoiceEmblem + 3)

        self.lockInButtonTrack = None

        self.button_gagLeft = DirectButton(
            parent=self,
            relief=None,
            pos=(-0.49221, 0.0, 0.14403),
            scale=0.37684,
            image=(
                sp_gui.find('**/LargeArrow_N'),
                sp_gui.find('**/LargeArrow_P'),
                sp_gui.find('**/LargeArrow_H'),
            ),
            image_pos=(0, 0, 0),
            image_scale=(-(81 / 140), 1, 1),
            command=self.changeGagLevel, extraArgs=[-1],
        )
        self.button_gagRight = DirectButton(
            parent=self,
            relief=None,
            pos=(0.491, 0.0, 0.14403),
            scale=0.37684,
            image=(
                sp_gui.find('**/LargeArrow_N'),
                sp_gui.find('**/LargeArrow_P'),
                sp_gui.find('**/LargeArrow_H'),
            ),
            image_pos=(0, 0, 0),
            image_scale=((81 / 140), 1, 1),
            command=self.changeGagLevel, extraArgs=[1],
        )
        self.gagChangeCallback = None

        targetingGui.removeNode()
        toonPanelGui.removeNode()

        self.accept(base.MOVE_LEFT, self.changeGagLevel, extraArgs=[-1, True])
        self.accept(base.MOVE_RIGHT, self.changeGagLevel, extraArgs=[1, True])

        def doLockIn():

            if self.lockInButton['command']:
                self.lockInButton['command']()

        self.accept(base.JUMP, doLockIn)

    """
    Gag Changing
    """

    def update(self):
        self.updateGagButtons()

    def setGagChangeCallback(self, callback):
        self.gagChangeCallback = callback

    def updateGagButtons(self) -> None:
        # First, hide the buttons.
        self.button_gagLeft.hide()
        self.button_gagRight.hide()

        # Get the track and level.
        track = self.emblem.track
        level = self.emblem.level
        if None in (track, level):
            # No gags -- don't even bother showing them again.
            return

        # Attempt to show if gags exist.
        distance = self.getGagDistance(track)
        nextLevel = self.getNextGagLevel(track, level, -distance)
        if nextLevel != -1:
            self.button_gagLeft.show()
        nextLevel = self.getNextGagLevel(track, level, distance)
        if nextLevel != -1:
            self.button_gagRight.show()

    def changeGagLevel(self, direction: int, fromHotkey: bool = False):
        # Change the gag level we plan to use.
        track = self.emblem.track
        level = self.emblem.level
        if None in (track, level):
            return self.updateGagButtons()

        # Get the next gag level.
        nextLevel = self.getNextGagLevel(track, level, direction * self.getGagDistance(track))
        if nextLevel == -1:
            # The gag could not change. Do not bother.
            return

        # Change the gags!
        self.emblem.setValues(track=track, level=nextLevel, avatar=self.emblem.avatar, townBattle=self.townBattle)
        if self.gagChangeCallback:
            self.gagChangeCallback(track, nextLevel)

        # Then, update the gag buttons.
        self.updateGagButtons()

    @staticmethod
    def getNextGagLevel(track: int, level: int, direction: int) -> int:
        """
        Gets the next gag level in a certain direction.
        If it does not exist, will return -1.
        """
        inventory = base.localAvatar.inventory
        counterfeit = base.localAvatar.getStatusEffectOfId(SEE.EFFECT_COUNTERFEIT_CONTAINER)

        while True:
            # Move the level a bit.
            level += direction
            if not (0 <= level <= 7):
                break

            if inventory.isGagDisabled(track, level):
                continue

            # Do we have items here?
            numItem = inventory.numItem(track, level)
            # Also include fake items from counterfeits
            if counterfeit:
                numItem += counterfeit.getGagTrackLevel(track, level)
            if numItem > 0:
                # It'll do.
                return level

        # No level found.
        return -1

    @staticmethod
    def getGagDistance(track: int) -> int:
        if track in (AttackEnum.TOON_HEAL, AttackEnum.TOON_LURE):
            return 2
        return 1

    """
    GUI
    """

    def destroy(self):
        DirectFrame.destroy(self)
        self.ignoreAll()
        self.stopLockInTrack()
        del self.townBattle
        del self.notLockedInImageList
        del self.lockedInImageList
        del self.unlockedImage
        del self.lockedImage
        del self.backButton
        del self.lockInButton
        del self.emblem
        del self.background
        del self.lock
        del self.lockInButtonTrack

    def activateTargetingMode(self):
        # Hide Lock In Elements
        self.stopLockInTrack()
        self.lock.hide()
        self.lockInButton.hide()

    def applySuitText(self):
        self.background['text'] = TTLocalizer.TownBattleChooseAvatarCogTitle
        self.background['text_scale'] = 0.10
        self.background['text_pos'] = (0, -0.345)

    def applyToonText(self):
        self.background['text'] = TTLocalizer.TownBattleChooseAvatarToonTitle
        self.background['text_scale'] = 0.10
        self.background['text_pos'] = (0, -0.345)

    def applyFireText(self, amount, hasEnough):
        if hasEnough:
            self.background['text'] = TTLocalizer.FireCogTitle % amount
        else:
            self.background['text'] = TTLocalizer.FireCogLowTitle % amount
        self.background['text_scale'] = 0.075
        self.background['text_pos'] = (0, -0.29)

    def applySueText(self, amount, hasEnough):
        if hasEnough:
            self.background['text'] = TTLocalizer.SueCogTitle % amount
        else:
            self.background['text'] = TTLocalizer.SueCogLowTitle % amount
        self.background['text_scale'] = 0.075
        self.background['text_pos'] = (0, -0.29)

    def activateLockInMode(self):
        # Show Lock In Elements
        self.lock.show()
        self.lockInButton.show()

        # Default to not being locked in
        self.setLockIn(False)

    def setLockIn(self, lockedIn):
        self.lockedIn = lockedIn
        if self.lockedIn:
            self.lock['image'] = self.lockedImage
            self.lockInButton['text'] = TTLocalizer.TownBattleUndo
            self.lockInButton['image'] = self.lockedInImageList
            self.background['text'] = TTLocalizer.TownBattleLockedIn
            self.stopLockInTrack()
        else:
            self.lock['image'] = self.unlockedImage
            self.lockInButton['text'] = TTLocalizer.TownBattleLock
            self.lockInButton['image'] = self.notLockedInImageList
            self.background['text'] = TTLocalizer.TownBattleLockIn
            # Don't re-start it if it is already playing.
            if not (self.lockInButtonTrack and self.lockInButtonTrack.isPlaying()):
                self.startLockInTrack()

        self.background['text_scale'] = 0.13

    def startLockInTrack(self):
        self.stopLockInTrack()
        self.lockInButtonTrack = Sequence(LerpColorScaleInterval(self.lockInButton, .75, VBase4(1, 1, 1, 1)),
                                          LerpColorScaleInterval(self.lockInButton, .75, VBase4(0.8, 0.7, 0.9, 1)), name='lockInButtonTrack')
        self.lockInButtonTrack.loop()

    def stopLockInTrack(self):
        if self.lockInButtonTrack:
            self.lockInButtonTrack.finish()
            self.lockInButtonTrack = None
        if self.lockInButton:
            self.lockInButton.setColorScale(1, 1, 1, 1)


class StatusEffectTooltip(DirectFrame):
    def __init__(self, parent=aspect2d, **kw):
        optiondefs = (
            ('relief', None, None),
        )

        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, parent)
        self.initialiseoptions(StatusEffectTooltip)
        self.baseScale = self.getScale()

        self.background = DirectFrame(
            parent=self,
            relief=None
        )
        self.titleLabel = DirectLabel(
            parent=self.background,
            relief=None,
            pos=(0, 0, 0.039),
            text='',
            text_scale=0.053,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_wordwrap=200
        )
        self.descriptionLabel = DirectLabel(
            parent=self.background,
            relief=None,
            pos=(0, 0, -0.01),
            text='',
            text_scale=0.0375,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_wordwrap=23
        )
        self.isToon = True

    def show(self):
        DirectFrame.show(self)
        Sequence(
            LerpScaleInterval(self, .2, self.baseScale * 1.1, self.baseScale * 0.01, blendType='easeInOut'),
            LerpScaleInterval(self, .09, self.baseScale, blendType='easeInOut')).start()

    def destroy(self):
        DirectFrame.destroy(self)
        del self.background
        del self.titleLabel
        del self.descriptionLabel

    def setIsToon(self, isToon):
        self.isToon = isToon

    def setStatusEffect(self, effect):
        # Load models
        tooltipGUI = base.loader.loadModel('phase_3.5/models/gui/battlegui/info_panels')

        # Choose border type (buff or debuff)
        if SEG.StatusEffectId2Type.get(effect.effectId) == SEG.BUFF:
            tooltipBorder = tooltipGUI.find('**/tooltip_buff')
            icon = tooltipGUI.find('**/buff_icon' + ('_toon' if self.isToon else '_suit'))
        else:
            tooltipBorder = tooltipGUI.find('**/tooltip_debuff')
            icon = tooltipGUI.find('**/debuff_icon' + ('_toon' if self.isToon else '_suit'))
        self.background['image'] = tooltipBorder
        self.background['image_scale'] = (1, 1, 0.5)
        self.background['geom'] = icon
        self.background['geom_pos'] = (0, 0, 0.13)
        self.background['geom_scale'] = 0.125

        # Set text labels
        effectTitle, effectDesc = SEG.makeTitleAndDesc(effect, effect.effectId)
        self.titleLabel['text'] = effectTitle
        self.titleLabel['text_scale'] = 0.053
        capTextScaleToWidth(self.titleLabel, 0.83)
        self.descriptionLabel['text'] = effectDesc

        # Cleanup loaded models
        tooltipGUI.removeNode()


class ToonInfoTooltip(DirectFrame):
    def __init__(self, parent=aspect2d, **kw):
        optiondefs = (
            ('relief', None, None),
        )

        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, parent)
        self.initialiseoptions(ToonInfoTooltip)
        self.baseScale = self.getScale()
        self.loaded = False

    def show(self):
        DirectFrame.show(self)
        Sequence(
            LerpScaleInterval(self, .2, self.baseScale * 1.1, self.baseScale * 0.01, blendType='easeInOut'),
            LerpScaleInterval(self, .09, self.baseScale, blendType='easeInOut')).start()

    def setToonInfo(self, av):
        self.loaded = True

        inventory = av.inventory

        tooltipGUI = base.loader.loadModel('phase_3.5/models/gui/battlegui/info_panels')
        trackCardImage = tooltipGUI.find('**/tooltip_toon_holder')
        gagSelectGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
        prestigeStarFilled = gagSelectGui.find('**/prestige_star')
        prestigeStarEmpty = gagSelectGui.find('**/prestige_star_empty')

        background = DirectFrame(
            parent=self,
            relief=None,
            image=tooltipGUI.find('**/tooltip_toon'),
            image_scale=(1, 1, 0.5)
        )

        name = av.getName()
        if len(name) > 0 and name[-1].lower() == 's':
            titleText = TTLocalizer.ToonTooltipTitleWithoutS.format(name)
        else:
            titleText = TTLocalizer.ToonTooltipTitle.format(name)
        # Title Text
        DirectLabel(
            parent=background,
            relief=None,
            text=titleText,
            text_font=ToontownGlobals.getMinnieFont(),
            text_fg=(0.976, 0.788, 0.165, 1),
            text_shadow=(0, 0, 0, 1),
            text_pos=(0, 0.104),
            text_scale=getTextScaleAfterLength(titleText, 40, modifier=0.0006, baseScale=0.035),
            textMayChange=0
        )

        xSeparation = 0.119
        startingX = -(0.5 * (len(Tracks) - 1)) * xSeparation

        for track in BattleGlobals.ATTACK_TRACKS:
            if track in BattleGlobals.GAG_TRACK_ORDER:
                i = BattleGlobals.GAG_TRACK_ORDER.index(track)
            else:
                i = track
            if av.hasTrackAccess(track):
                trackColor = Vec4(
                    TrackColors[track][0],
                    TrackColors[track][1],
                    TrackColors[track][2],
                    1
                )
                titleColor = None
                gagLevel = GagsContentSyncModifier.capGagLevel(do=av, cap=av.getExperience().getExpLevel(track))
                gagIcon = inventory.invModels[track][gagLevel]
                gagColor = None
            else:
                trackColor = Vec4(
                    TrackColors[track][0] * 0.3,
                    TrackColors[track][1] * 0.3,
                    TrackColors[track][2] * 0.3,
                    1
                )
                titleColor = Vec4(0.3, 0.3, 0.3, 1)
                gagIcon = inventory.invModels[track][0]
                gagColor = Vec4(0, 0, 0, 1)
            trackCard = DirectFrame(
                parent=background,
                relief=None,
                image=trackCardImage,
                image_color=trackColor,
                geom=gagIcon,
                geom_color=gagColor,
                geom_scale=2.5,
                pos=(0, 0, -0.023),
                scale=0.21
            )
            trackCard.setX(startingX + (i * xSeparation))

            trackTitle = DirectFrame(
                parent=trackCard,
                relief=None,
                image=gagSelectGui.find('**/track_' + Tracks[track] + '_title'),
                image_color=titleColor,
                pos=(0, 0, 0.31),
                scale=(0.80 if Tracks[track] == 'toon-up' else 0.44, 1, 0.22)
            )

            prestigeStarSlot = DirectFrame(
                parent=trackCard,
                relief=None,
                image=prestigeStarEmpty,
                image_color=titleColor,
                pos=(0, 0, -0.325),
                scale=0.17
            )

            prestigeStar = DirectFrame(
                parent=trackCard,
                relief=None,
                image=prestigeStarFilled,
                pos=(0.001, 0, -0.325),
                scale=0.18
            )
            if not av.checkGagBonus(track, 0):
                prestigeStar.hide()

        tooltipGUI.removeNode()
        gagSelectGui.removeNode()


def generateSuitModifierText(av):
    text = ''
    name = av.style.name

    # Find the suit's specialization, if they have one
    if 'specialization' in SuitBattleGlobals.SuitAttributes[name]:
        specialization = SuitBattleGlobals.SuitAttributes[name]['specialization']
    else:
        specialization = SuitBattleGlobals.NORMAL

    # Function that adds new lines as needed.
    def addText(currentText, newText):
        # New line if there is a line already
        if currentText != '':
            currentText = currentText + '\n\n'

        # Return combined string
        return currentText + newText

    # Add text for specialization
    if specialization != SuitBattleGlobals.NORMAL:
        specializationName = SuitBattleGlobals.SuitSpecialization2Name[specialization]
        text = addText(text,
                       f'\1TextSubtitle\1{specializationName}:\2\n{TTLocalizer.SuitAttributeDescriptions[specializationName]}')

    # Add text for miniboss or executive. (miniboss has priority)
    if av.isMiniboss():
        text = addText(text,
                       f'\1TextSubtitle\1{TTLocalizer.SuitAttributeManager}:\2\n{TTLocalizer.SuitAttributeDescriptions[TTLocalizer.SuitAttributeManager]}')
    elif av.getElite():
        text = addText(text,
                       f'\1TextSubtitle\1{TTLocalizer.SuitAttributeExecutive}:\2\n{TTLocalizer.SuitAttributeDescriptions[TTLocalizer.SuitAttributeExecutive]}')

    # Add text for v2.0s
    if av.getSkeleRevives() >= 1:
        text = addText(text,
                       f'\1TextSubtitle\1{TTLocalizer.SuitAttributeRevive}:\2\n{TTLocalizer.SuitAttributeDescriptions[TTLocalizer.SuitAttributeRevive]}')

    # Use default text if there were no special modifications to this suit
    if text == '':
        text = TTLocalizer.SuitAttributeDescriptions[TTLocalizer.SuitAttributeNormal]

    return text


class SuitInfoTooltip(DirectFrame):
    def __init__(self, parent=aspect2d, **kw):
        optiondefs = (
            ('relief', None, None),
        )

        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, parent)
        self.initialiseoptions(SuitInfoTooltip)
        self.baseScale = self.getScale()

        tooltipGUI = base.loader.loadModel('phase_3.5/models/gui/battlegui/info_panels')

        background = DirectFrame(
            parent=self,
            relief=None,
            image=tooltipGUI.find('**/tooltip_suit'),
            image_scale=(1, 1, 0.5)
        )

        self.infoText = DirectLabel(
            parent=background,
            relief=None,
            text='',
            text_pos=(0, 0.041),
            text_scale=0.0325
        )

        # Title Text
        DirectLabel(
            parent=background,
            relief=None,
            text=TTLocalizer.SuitTooltipTitle,
            text_font=ToontownGlobals.getSuitFont(),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_pos=(0, 0.107),
            text_scale=0.045,
            textMayChange=0
        )

        tooltipGUI.removeNode()

    def show(self):
        DirectFrame.show(self)
        Sequence(
            LerpScaleInterval(self, .2, self.baseScale * 1.1, self.baseScale * 0.01, blendType='easeInOut'),
            LerpScaleInterval(self, .09, self.baseScale, blendType='easeInOut')).start()

    def setSuitInfo(self, av):
        self.infoText['text'] = generateSuitModifierText(av)


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
# Gag Selection GUI Generation Functions #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
def generateBattlePanel():
    '''
    Generates the extra GUI elements needed for the battle panel (excludes gag tracks + detail panel).
    :return: Dictionary of GUI Elements (refer to top of BattleGUI.py for the keys)
    '''
    # Load Models
    gagSelectGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')

    battleFrame = DirectFrame(
        relief=None
    )

    guiElements = {BATTLE_FRAME: battleFrame}
    guiElements.update(generateBattleTabs())

    tabsFrame = guiElements[TABS_FRAME]
    tabsFrame.reparentTo(battleFrame)
    tabsFrame.setPos(-0.36, 0, -0.025),
    tabsFrame.setScale(0.27)

    trackHolderFrame = DirectFrame(
        parent=battleFrame,
        relief=None,
        image=gagSelectGui.find('**/gag_selection_main')
    )

    guiElements.update({TRACK_HOLDER_FRAME: trackHolderFrame})
    guiElements.update(generateTotalGagsPanel())

    totalGagsFrame = guiElements[TOTAL_GAGS_FRAME]
    totalGagsFrame.reparentTo(trackHolderFrame)
    totalGagsFrame.setPos(-0.02, 0, 0.49),
    totalGagsFrame.setScale(0.45)

    # Clean Up Loaded Models
    gagSelectGui.removeNode()

    return guiElements


def generateTotalGagsPanel():
    '''
    Generates the total gags panel.
    :return: Dictionary of GUI Elements (refer to top of BattleGUI.py for the keys)
    '''
    # Load Models
    gagSelectGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')

    totalGagsFrame = DirectFrame(
        relief=None,
        image=gagSelectGui.find('**/total_gags'),
        pos=(-0.02, 0, 0.49),
        scale=0.45
    )

    totalGagsTitleLabel = DirectLabel(
        parent=totalGagsFrame,
        text='Total Gags',
        text_fg=(0, 0, 0, 1),
        scale=0.1,
        pos=(0.0125, 0, 0.07),
        text_font=ToontownGlobals.getInterfaceFont(),
        text_align=TextNode.ACenter,
        relief=None
    )

    totalGagsNumberLabel = DirectLabel(
        parent=totalGagsFrame,
        text='120 / 120',
        text_fg=(0, 0, 0, 1),
        scale=0.1,
        pos=(0.0125, 0, -0.09),
        text_font=ToontownGlobals.getInterfaceFont(),
        text_align=TextNode.ACenter,
        relief=None
    )

    # Clean Up Loaded Models
    gagSelectGui.removeNode()

    guiElements = {
        TOTAL_GAGS_FRAME: totalGagsFrame,
        TOTAL_GAGS_TITLE_LABEL: totalGagsTitleLabel,
        TOTAL_GAGS_NUMBER_LABEL: totalGagsNumberLabel
    }

    return guiElements


def generateBattleTabs():
    '''
    Generates the battle action tabs.
    Event bindings and commands will need to be assigned using references in the element dictionary.
    :return: Dictionary of GUI Elements (refer to top of BattleGUI.py for the keys)
    '''
    # Load Models
    gagSelectGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')

    tabsFrame = DirectFrame(
        relief=None,
    )

    tabPass = ScalingButton(
        parent=tabsFrame,
        relief=None,
        image=(gagSelectGui.find('**/tab_pass'),
               gagSelectGui.find('**/tab_pass_press'),
               gagSelectGui.find('**/tab_pass_hover')),
        text=('',
              TTLocalizer.InventoryPass,
              TTLocalizer.InventoryPass),
        text_pos=(-0.55, -0.075),
        text_align=TextNode.ARight,
        text_scale=0.3,
        text_fg=(1, 1, 1, 1),
        text_shadow=(0, 0, 0, 1),
        frameSize=(-0.53, 0.4, -0.34, 0.34),
        pos=(0, 0, 1.25)
    )

    tabRun = ScalingButton(
        parent=tabsFrame,
        relief=None,
        image=(gagSelectGui.find('**/tab_run'),
               gagSelectGui.find('**/tab_run_press'),
               gagSelectGui.find('**/tab_run_hover')),
        text=('',
              TTLocalizer.InventoryRun,
              TTLocalizer.InventoryRun),
        text_pos=(-0.55, -0.075),
        text_align=TextNode.ARight,
        text_scale=0.3,
        text_fg=(1, 1, 1, 1),
        text_shadow=(0, 0, 0, 1),
        frameSize=(-0.53, 0.4, -0.34, 0.34),
        pos=(0, 0, 0.6)
    )

    tabSos = ScalingButton(
        parent=tabsFrame,
        relief=None,
        image=(gagSelectGui.find('**/tab_sos'),
               gagSelectGui.find('**/tab_sos_press'),
               gagSelectGui.find('**/tab_sos_hover')),
        text=('',
              TTLocalizer.InventorySOS,
              TTLocalizer.InventorySOS),
        text_pos=(-0.55, -0.075),
        text_align=TextNode.ARight,
        text_scale=0.3,
        text_fg=(1, 1, 1, 1),
        text_shadow=(0, 0, 0, 1),
        frameSize=(-0.53, 0.4, -0.34, 0.34),
        pos=(0, 0, -0.05)
    )

    RwdBttnStartZ = -0.55
    RwdBttnZInc = -0.4
    RwdBttnScale = 0.85

    tabCounterfeit = ScalingButton(
        parent=tabsFrame,
        relief=None,
        image=(gagSelectGui.find('**/tab_forge'),
               gagSelectGui.find('**/tab_forge_press'),
               gagSelectGui.find('**/tab_forge_hover')),
        frameSize=(-0.3, 0.2, -0.4, 0.4),
        pos=(0, 0, RwdBttnStartZ),
        scale=(2 * RwdBttnScale, 1, 0.5 * RwdBttnScale),
        hpr=(0, 0, 0)
    )

    tabSue = ScalingButton(
        parent=tabsFrame,
        relief=None,
        image=(gagSelectGui.find('**/tab_sue'),
               gagSelectGui.find('**/tab_sue_press'),
               gagSelectGui.find('**/tab_sue_hover')),
        frameSize=(-0.3, 0.2, -0.4, 0.4),
        pos=(0, 0, RwdBttnStartZ + RwdBttnZInc),
        scale=(2*RwdBttnScale, 1, 0.5*RwdBttnScale),
        hpr=(0, 0, 0)
    )

    tabFire = ScalingButton(
        parent=tabsFrame,
        relief=None,
        image=(gagSelectGui.find('**/tab_fire'),
               gagSelectGui.find('**/tab_fire_press'),
               gagSelectGui.find('**/tab_fire_hover')),
        frameSize=(-0.3, 0.2, -0.4, 0.4),
        pos=(0, 0, RwdBttnStartZ + (RwdBttnZInc*2)),
        scale=(2*RwdBttnScale, 1, 0.5*RwdBttnScale),
        hpr=(0, 0, 0)
    )

    tabCounterfeitBack = ScalingButton(
        parent=tabsFrame,
        relief=None,
        image=(gagSelectGui.find('**/tab_forge_back'),
               gagSelectGui.find('**/tab_forge_back_press'),
               gagSelectGui.find('**/tab_forge_back_hover')),
        frameSize=(-0.3, 0.2, -0.4, 0.4),
        pos=(1.0, 0, RwdBttnStartZ + RwdBttnZInc),
        scale=(2 * RwdBttnScale * 1.25, 1, 0.5 * RwdBttnScale * 1.25),
        hpr=(0, 0, 0)
    )

    tabSurrenderFlag = DirectFrame(
        parent=tabsFrame,
        relief=None,
        image=gagSelectGui.find('**/tab_surrender_tab'),
        text='0/0',
        text_pos=(0, -0.075),
        text_align=TextNode.ACenter,
        text_scale=0.2,
        text_fg=(0, 0, 0, 1),
        frameSize=(-0.53, 0.4, -0.34, 0.34),
        pos=(-0.7, 0, 0.6)
    )

    tabSurrender = ScalingButton(
        parent=tabsFrame,
        relief=None,
        image=(gagSelectGui.find('**/tab_surrender'),
               gagSelectGui.find('**/tab_surrender_press'),
               gagSelectGui.find('**/tab_surrender_hover')),
        text=('',
              TTLocalizer.InventorySurrender,
              TTLocalizer.InventorySurrender),
        text_pos=(-0.55, -0.075),
        text_align=TextNode.ARight,
        text_scale=0.3,
        text_fg=(1, 1, 1, 1),
        text_shadow=(0, 0, 0, 1),
        frameSize=(-0.53, 0.4, -0.34, 0.34),
        pos=(0, 0, 0.6)
    )

    # Clean Up Loaded Models
    gagSelectGui.removeNode()

    guiElements = {
        TABS_FRAME: tabsFrame,
        TABS_PASS: tabPass,
        TABS_RUN: tabRun,
        TABS_SOS: tabSos,
        TABS_SUE: tabSue,
        TABS_FIRE: tabFire,
        TABS_COUNTERFEIT: tabCounterfeit,
        TABS_SURRENDER: tabSurrender,
        TABS_SURRENDER_FLAG: tabSurrenderFlag,
        TABS_COUNTERFEIT_BACK: tabCounterfeitBack,
    }

    return guiElements


def generateDetailPanel():
    '''
    Generates the detail panel that displays info about gags/actions.
    :return: Dictionary of GUI Elements (refer to top of BattleGUI.py for the keys)
    '''
    # Load Models
    gagSelectGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')

    # Default Pos and Scale for being reparented to the Gag Tracks frame.
    detailFrame = DirectFrame(
        relief=None,
        pos=(0.61, 0, 0.019),
        scale=0.4
    )

    detailBackground = DirectFrame(
        parent=detailFrame,
        relief=None,
        image=gagSelectGui.find('**/gag_info_main'),
    )

    detailEmblem = ChoiceEmblem(
        parent=detailFrame,
        relief=None,
        pos=(0.02, 0, 0.31),
        scale=0.5,
        ccpScale=0.003,
    )

    # Detail Labels
    detailNameLabel = DirectLabel(
        parent=detailFrame,
        relief=None,
        text='',
        scale=0.07,
        pos=(0.02, 0, 0.08),
        text_font=ToontownGlobals.getInterfaceFont(),
    )

    detailAmountLabel = DirectLabel(
        parent=detailFrame,
        relief=None,
        text='',
        scale=0.055,
        pos=(0.02, 0, 0.01),
        text_font=ToontownGlobals.getInterfaceFont(),
    )

    detailDataLabel = DirectLabel(
        parent=detailFrame,
        relief=None,
        text='',
        scale=0.055,
        pos=(-0.25, 0, -0.08),
        text_font=ToontownGlobals.getInterfaceFont(),
        text_align=TextNode.ALeft,
    )

    # Clean Up Loaded Models
    gagSelectGui.removeNode()

    guiElements = {
        DETAILS_FRAME: detailFrame,
        DETAILS_EMBLEM: detailEmblem,
        DETAILS_NAME_LABEL: detailNameLabel,
        DETAILS_AMOUNT_LABEL: detailAmountLabel,
        DETAILS_DATA_LABEL: detailDataLabel
    }

    return guiElements


def calculateTrackZPos(index):
    # Given an index, calculates the track's Z position.
    return (7 - (index * 2)) * GagTracksZSeparation / 2


def generateGagTracks(inventory):
    '''
    Generates a complete version of the gag tracks.
    Event bindings and commands will need to be assigned using references in the element dictionary.
    :return: Dictionary of GUI Elements (refer to top of BattleGUI.py for the keys)
    '''
    trackRows = {}
    trackNameLabels = {}
    trackBars = {}
    prestigeStars = {}
    buttons = {}
    trackHovers = {}
    trackSubframes = {}

    # Load models
    invModel = base.loader.loadModel('phase_3.5/models/gui/inventory_icons')
    invModels = []
    for track in range(len(AvPropsNew)):
        itemList = []
        for item in range(len(AvPropsNew[track])):
            itemList.append(invModel.find('**/' + AvPropsNew[track][item]))

        invModels.append(itemList)

    gagSelectGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
    prestigeStarFilled = gagSelectGui.find('**/prestige_star')
    prestigeStarEmpty = gagSelectGui.find('**/prestige_star_empty')

    inventoryModels = base.loader.loadModel('phase_3.5/models/gui/inventory_gui')
    upButton = inventoryModels.find('**/InventoryButtonUp')
    downButton = inventoryModels.find('**/InventoryButtonDown')
    rolloverButton = inventoryModels.find('**/InventoryButtonRollover')
    flatButton = inventoryModels.find('**/InventoryButtonFlat')

    # Frame that will hold all the elements
    tracksFrame = DirectFrame(
        relief=None,
    )

    for index, trackIndex in enumerate(inventory.getGagOrder()):
        trackSubframe = DirectFrame(
            parent=tracksFrame,
            relief=None,
            pos=(0, 0, calculateTrackZPos(index)),
        )
        trackSubframes[trackIndex] = trackSubframe

        # Track Graphic
        track = DirectFrame(
            parent=trackSubframe,
            relief=None,
            image=gagSelectGui.find('**/track_' + Tracks[trackIndex]),
            scale=(1, 1, 0.0625),
            pos=(0, 0, 0)
        )
        trackRows[trackIndex] = track

        # Track Text
        trackTitle = DirectFrame(
            parent=trackSubframe,
            relief=None,
            image=gagSelectGui.find('**/track_' + Tracks[trackIndex] + '_title'),
            scale=(TrackTitleToonupScale if Tracks[trackIndex] == 'toon-up' else TrackTitleScale),
            pos=(-0.388, 0, TrackTitleZOffset)
        )
        trackNameLabels[trackIndex] = trackTitle

        # Track Experience Bar
        trackExperience = DirectWaitBar(parent=trackSubframe,
                                        pos=(-0.388, 0, -0.0118),
                                        relief=DGG.SUNKEN,
                                        frameSize=(-0.6,
                                                   0.6,
                                                   -0.1,
                                                   0.1), borderWidth=(0.02, 0.02), scale=0.12,
                                        frameColor=(TrackColors[trackIndex][0] * 0.6,
                                                    TrackColors[trackIndex][1] * 0.6,
                                                    TrackColors[trackIndex][2] * 0.6,
                                                    1), barColor=(TrackColors[trackIndex][0] * 0.9,
                                                                  TrackColors[trackIndex][1] * 0.9,
                                                                  TrackColors[trackIndex][2] * 0.9,
                                                                  1), text='0 / 0', text_scale=0.16,
                                        text_fg=(0, 0, 0, 0.8),
                                        text_align=TextNode.ACenter, text_pos=(0, -0.05))
        trackBars[trackIndex] = trackExperience

        prestigeStarSlot = DirectFrame(
            parent=trackSubframe,
            relief=None,
            image=prestigeStarEmpty,
            scale=0.04,
            pos=(0.44, 0, 0)
        )

        prestigeStar = DirectFrame(
            parent=trackSubframe,
            relief=None,
            image=prestigeStarFilled,
            scale=0.0424,
            pos=(0.44, 0, 0)
        )
        prestigeStars[trackIndex] = prestigeStar
        prestigeStar.hide()

        # Gag Buttons
        buttonList = []
        for item in range(len(Levels[trackIndex])):
            button = ScalingButton(
                parent=trackSubframe,
                relief=None,
                image=(upButton,
                       downButton,
                       rolloverButton,
                       flatButton),
                image_color=(TrackColors[trackIndex][0] * 0.95,
                             TrackColors[trackIndex][1] * 0.95,
                             TrackColors[trackIndex][2] * 0.95,
                             1),
                geom=invModels[trackIndex][item],
                geom_scale=0.7,
                geom_pos=(-0.01, -0.1, 0),
                text='50',
                text_align=TextNode.ARight,
                text_font=ToontownGlobals.getBuildingNametagFont(),
                text_scale=0.075,
                text_pos=(0.075, -0.05),
                text_fg=Vec4(1.0, 1.0, 1.0, 1.0),
                textMayChange=1,
                pos=(GagButtonsXOffset + item * GagButtonsXSpacing, 0,
                     0.0013 + 0),
                scale=0.485
            )
            buttonList.append(button)
        buttons[trackIndex] = buttonList

        trackHover = DirectButton(parent=trackSubframe,
                                  pos=(-0.388, 0, -0.0118),
                                  frameSize=(-0.65, 0.65, -0.24, 0.25), borderWidth=(0.02, 0.02), scale=0.12,
                                  frameColor=(1, 1, 1, 0))
        trackHovers[trackIndex] = trackHover

    # Clean Up Loaded Models
    invModel.removeNode()
    gagSelectGui.removeNode()
    inventoryModels.removeNode()

    guiElements = {
        TRACKS_FRAME: tracksFrame,
        TRACKS_ROWS: trackRows,
        TRACKS_NAME_LABELS: trackNameLabels,
        TRACKS_EXPERIENCE_BARS: trackBars,
        TRACKS_PRESTIGE_STARS: prestigeStars,
        TRACKS_GAG_BUTTONS: buttons,
        TRACKS_TRACK_HOVERS: trackHovers,
        TRACKS_SUBFRAMES: trackSubframes,
    }

    return guiElements


def generateAvatarPanelTracks(av):
    '''
    Creates a version of the Gag Selection GUI intended for the Toon Avatar Panel.
    :param av: Toon to generate tracks for.
    :return: DirectFrame containing all the elements. Can be linearly scaled.
    '''
    inventory = av.inventory

    # Load models
    gagSelectGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
    prestigeStarFilled = gagSelectGui.find('**/prestige_star')
    prestigeStarEmpty = gagSelectGui.find('**/prestige_star_empty')

    inventoryModels = base.loader.loadModel('phase_3.5/models/gui/inventory_gui')
    buttonModel = inventoryModels.find('**/InventoryButtonUp')

    # Frame that will hold all the elements
    tracksFrame = DirectFrame(
        relief=None,
    )

    for index, trackIndex in enumerate(BattleGlobals.GAG_TRACK_ORDER):
        # Track Graphic
        track = DirectFrame(
            parent=tracksFrame,
            relief=None,
            image=gagSelectGui.find('**/track_' + Tracks[trackIndex]),
            scale=(1, 1, 0.0625),
            pos=(0, 0, (7 - (index * 2)) * GagTracksZSeparation / 2)
        )

        # Track Text
        trackTitle = DirectFrame(
            parent=tracksFrame,
            relief=None,
            image=gagSelectGui.find('**/track_' + Tracks[trackIndex] + '_title'),
            scale=(0.25 if Tracks[trackIndex] == 'toon-up' else 0.125, 1, 0.0625),
            pos=(-0.388, 0, (7 - (index * 2)) * GagTracksZSeparation / 2)
        )

        prestigeStarSlot = DirectFrame(
            parent=tracksFrame,
            relief=None,
            image=prestigeStarEmpty,
            scale=0.04,
            pos=(0.44, 0, (7 - (index * 2)) * GagTracksZSeparation / 2)
        )

        prestigeStar = DirectFrame(
            parent=tracksFrame,
            relief=None,
            image=prestigeStarFilled,
            scale=0.0424,
            pos=(0.44, 0, (7 - (index * 2)) * GagTracksZSeparation / 2)
        )
        prestigeStar.hide()

        if av.hasTrackAccess(trackIndex):
            # Fill in prestige star if they have the track prestiged
            prestiged = False
            if av.checkGagBonus(trackIndex, 0):
                prestiged = True
                prestigeStar.show()
            curExp, nextExp = inventory.getCurAndNextExpValues(trackIndex)
            for item in range(0, len(Levels[trackIndex])):
                level = Levels[trackIndex][item]
                if item > GagsContentSyncModifier.capGagLevel(do=av):
                    break

                forceHas = any(
                    gagModifier.getForceMaxed()
                    for gagModifier in av.getModifiersOfType(ModifierType.GagsContentSync)
                )

                if curExp >= level or forceHas:
                    numItems = inventory.numItem(trackIndex, item)
                    counterfeitEffect = av.getStatusEffectOfId(SEE.EFFECT_COUNTERFEIT_CONTAINER)
                    hasBoostedAmount = counterfeitEffect and counterfeitEffect.getGagTrackLevel(trackIndex, item)
                    if numItems == 0:
                        image_color = inventory.UnpressableImageColorBonus if prestiged else inventory.UnpressableImageColor
                    else:
                        if hasBoostedAmount:
                            image_color = inventory.CounterfeitPressableImageColorBonus if prestiged else inventory.CounterfeitPressableImageColor
                        else:
                            image_color = inventory.PressableImageColorBonus if prestiged else inventory.PressableImageColor

                    numItemText = str(numItems)
                    if hasBoostedAmount:
                        numItemText = f'{numItemText}+1'
                    button = DirectLabel(
                        parent=tracksFrame,
                        image=buttonModel,
                        image_color=image_color,
                        geom=inventory.invModels[trackIndex][item],
                        geom_color=inventory.BookUnpressableGeomColor,
                        text=numItemText,
                        text_align=TextNode.ARight,
                        geom_scale=0.7,
                        geom_pos=(-0.01, -0.1, 0),
                        text_font=ToontownGlobals.getBuildingNametagFont(),
                        text_scale=0.06 if hasBoostedAmount else (0.075 if prestiged else 0.07),
                        text_pos=(0.075, -0.05),
                        text_fg=Vec4(1.0, 1.0, 1.0, 1.0),
                        textMayChange=1,
                        relief=None,
                        pos=(GagButtonsXOffset + item * GagButtonsXSpacing, 0,
                             0.0005 + (7 - (index * 2)) * GagTracksZSeparation / 2),
                        scale=0.48
                    )
                else:
                    break

    # Clean Up Loaded Models
    gagSelectGui.removeNode()
    inventoryModels.removeNode()

    return tracksFrame


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
# Battle Avatar Panel Generation Functions #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
def generateSuitPanel():
    suitPanelGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/suit_panel')

    suitPanelFrame = DirectFrame(
        relief=None
    )

    suitPanelBackground = DirectFrame(
        parent=suitPanelFrame,
        relief=None,
        image=suitPanelGui.find('**/suit_panel_main')
    )

    ### STATUS EFFECT SLOTS
    statusEffectSlots = []
    for i in range(4):
        statusEffectSlot = DirectFrame(
            parent=suitPanelFrame,
            relief=None,
            image=suitPanelGui.find('**/status_effect_slot'),
            sortOrder=4 - i
        )
        statusEffectSlots.append(statusEffectSlot)

    statusEffectSlots[0].setPos(-0.21, 0, -0.068)
    statusEffectSlots[0].setScale(0.16)

    statusEffectSlots[1].setPos(-0.081, 0, -0.166)
    statusEffectSlots[1].setScale(0.16)

    statusEffectSlots[2].setPos(0.081, 0, -0.166)
    statusEffectSlots[2].setScale(0.16)

    statusEffectSlots[3].setPos(0.21, 0, -0.068)
    statusEffectSlots[3].setScale(0.16)

    ### CYCLE BUTTONS
    cycleBackButton = DirectButton(
        parent=suitPanelFrame,
        relief=None,
        image=(
            suitPanelGui.find('**/Arrow_Nuetral'),
            suitPanelGui.find('**/Arrow_Press'),
            suitPanelGui.find('**/arrow_hover')
        ),
        frameSize=(-0.3, 0.3, -0.15, 0.2),
        pos=(-0.236, 0, 0.03),
        scale=(-0.242, 1, 0.22)
    )

    cycleForwardButton = DirectButton(
        parent=suitPanelFrame,
        relief=None,
        image=(
            suitPanelGui.find('**/Arrow_Nuetral'),
            suitPanelGui.find('**/Arrow_Press'),
            suitPanelGui.find('**/arrow_hover')
        ),
        frameSize=(-0.3, 0.3, -0.15, 0.2),
        pos=(0.236, 0, 0.03),
        scale=(0.242, 1, 0.22)
    )

    ### Health Bar
    healthBarBackground = DirectFrame(
        parent=suitPanelFrame,
        relief=None,
        image=suitPanelGui.find('**/suit_panel_health'),
        pos=(0.097, 0, 0.16),
        scale=(0.5, 1, 0.125)
    )

    healthBar = DirectFrame(
        parent=suitPanelFrame,
        relief=None,
        image=suitPanelGui.find('**/suit_panel_health'),
        pos=(0.097, 0, 0.16),
        scale=(0.5, 1, 0.125)
    )

    # Create clipping plane for meter fluid
    healthBarClippingPlane = PlaneNode('clippingPlane')
    healthBarClippingPlane.setPlane(Plane(Vec3(-1, 0, 0), Point3(0, 0, 0)))
    clipNP = healthBar.attachNewNode(healthBarClippingPlane)
    healthBar.setClipPlane(clipNP)

    infoButton = DirectButton(
        parent=suitPanelFrame,
        relief=None,
        image=(
            suitPanelGui.find('**/Info_Nuetral'),
            suitPanelGui.find('**/Info_Press'),
            suitPanelGui.find('**/Info_Hover')
        ),
        frameSize=(-0.17, 0.12, -0.22, 0.22),
        pos=(0.36, 0, 0.161),
        scale=0.25
    )

    healthBarLabel = DirectLabel(
        parent=suitPanelFrame,
        relief=None,
        text='99999/99999',
        text_font=ToontownGlobals.getInterfaceFont(),
        text_scale=0.0685,
        text_pos=(0.09, 0.1425)
    )

    levelLabel = DirectLabel(
        parent=suitPanelFrame,
        relief=None,
        text='Level 50.exe V2.0',
        text_font=ToontownGlobals.getInterfaceFont(),
        text_scale=0.063,
        text_pos=(0.105, 0.245)
    )

    suitPanelGui.removeNode()

    guiElements = {
        SUIT_PANEL_FRAME: suitPanelFrame,
        SUIT_PANEL_SLOTS: statusEffectSlots,
        SUIT_PANEL_CYCLE_BACK_BUTTON: cycleBackButton,
        SUIT_PANEL_CYCLE_FORWARD_BUTTON: cycleForwardButton,
        SUIT_PANEL_HEALTH_BAR: healthBar,
        SUIT_PANEL_HEALTH_BAR_LABEL: healthBarLabel,
        SUIT_PANEL_HEALTH_BAR_CLIPPING_PLANE: healthBarClippingPlane,
        SUIT_PANEL_LEVEL_LABEL: levelLabel,
        SUIT_PANEL_INFO_BUTTON: infoButton
    }

    return guiElements


def generateToonPanel():
    gagSelectGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
    toonPanelGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/toon_panel')

    toonPanelFrame = DirectFrame(
        relief=None
    )

    toonPanelBackground = DirectFrame(
        parent=toonPanelFrame,
        relief=None,
        image=toonPanelGui.find('**/toon_panel_background')
    )

    choiceEmblem = ChoiceEmblem(
        parent=toonPanelFrame,
        relief=None
    )

    toonPanelBorder = DirectFrame(
        parent=toonPanelFrame,
        relief=None,
        image=toonPanelGui.find('**/toon_panel_frame')
    )

    laffMeterNode = DirectFrame(
        parent=toonPanelFrame,
        relief=None
    )

    statusEffectSlots = []
    for i in range(4):
        statusEffectSlot = DirectFrame(
            parent=toonPanelFrame,
            relief=None,
            image=toonPanelGui.find('**/status_effect_slot'),
            sortOrder=4 - i
        )
        statusEffectSlots.append(statusEffectSlot)

    cycleBackButton = DirectButton(
        parent=toonPanelFrame,
        relief=None,
        image=(
            toonPanelGui.find('**/arrow_neutral'),
            toonPanelGui.find('**/arrow_press'),
            toonPanelGui.find('**/arrow_hover')
        )
    )

    cycleForwardButton = DirectButton(
        parent=toonPanelFrame,
        relief=None,
        image=(
            toonPanelGui.find('**/arrow_neutral'),
            toonPanelGui.find('**/arrow_press'),
            toonPanelGui.find('**/arrow_hover')
        )
    )

    infoButton = DirectButton(
        parent=toonPanelFrame,
        relief=None,
        image=(
            toonPanelGui.find('**/info_neutral'),
            toonPanelGui.find('**/info_press'),
            toonPanelGui.find('**/info_hover')
        )
    )

    gagLock = DirectFrame(
        parent=toonPanelFrame,
        relief=None,
        image=toonPanelGui.find('**/lock_unlocked')
    )

    surrenderFlag = DirectFrame(
        parent=toonPanelFrame,
        relief=None,
        scale=0.3,
        image=toonPanelGui.find('**/surrender_flag'),
        frameSize=(-0.53, 0.4, -0.34, 0.34),
        pos=(-0.45, 0, 0.28),
    )

    gagSelectGui.removeNode()
    toonPanelGui.removeNode()

    # Placements
    laffMeterNode.setPos(-0.15, 0, 0.06)
    laffMeterNode.setScale(1.1)

    statusEffectSlots[0].setPos(-0.39, 0, 0.083)
    statusEffectSlots[1].setPos(-0.374, 0, -0.044)
    statusEffectSlots[2].setPos(-0.294, 0, -0.147)
    statusEffectSlots[3].setPos(-0.175, 0, -0.195)

    for slot in statusEffectSlots:
        slot.setScale(0.13)

    cycleBackButton.setPos(-0.384, 0, 0.175)
    cycleBackButton.setScale(0.15)
    cycleBackButton.setR(-90)

    cycleForwardButton.setPos(-0.082, 0, -0.205)
    cycleForwardButton.setScale(0.15)

    infoButton.setPos(0, 0, -0.06)
    infoButton.setScale(0.15)

    choiceEmblem.setPos(0.21, 0, 0.067)
    choiceEmblem.setScale(0.5)

    gagLock.setPos(0.345, 0, -0.04)
    gagLock.setScale(0.13, 1, 0.26)

    guiElements = {
        TOON_PANEL_FRAME: toonPanelFrame,
        TOON_PANEL_SLOTS: statusEffectSlots,
        TOON_PANEL_CYCLE_BACK_BUTTON: cycleBackButton,
        TOON_PANEL_CYCLE_FORWARD_BUTTON: cycleForwardButton,
        TOON_PANEL_LAFF_METER_NODE: laffMeterNode,
        TOON_PANEL_CHOICE_EMBLEM: choiceEmblem,
        TOON_PANEL_GAG_LOCK: gagLock,
        TOON_PANEL_INFO_BUTTON: infoButton,
        TOON_PANEL_SURRENDER_FLAG: surrenderFlag,
    }

    return guiElements


# -=-=-=-=-=-=-=-=-=-=-=-= #
# Targeting GUI Generation #
# -=-=-=-=-=-=-=-=-=-=-=-= #
def generateTargetingArrow(scale=1):
    targetingGui = base.loader.loadModel('phase_3.5/models/gui/battlegui/targeting')
    arrow = ScalingButton(
        relief=None,
        image=(
            targetingGui.find('**/arrow_neutral'),
            targetingGui.find('**/arrow_press'),
            targetingGui.find('**/arrow_hover')
        ),
        text='',
        text_font=ToontownGlobals.getInterfaceFont(),
        text_scale=0.3,
        text_pos=(-0.01, -0.25),
        textMayChange=1,
        scale=scale
    )
    targetingGui.removeNode()
    return arrow


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
# Status Effect Generation & Tooltip Functions #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
statusEffectImages = base.loader.loadModel('phase_3.5/models/gui/battlegui/status_effects')  # Intentional global -- this guy gets loaded A LOT!!
visibleEffectDict = {}


def buildVisibleEffectDict():
    global visibleEffectDict
    if visibleEffectDict:
        return

    from toontown.clashbattle.battle.statuses.StatusEffectDefinitions import StatusEffectDefinitions
    visibleEffectDict = {
        effectId: effect.visible for effectId, effect in StatusEffectDefinitions.items()
    }


def generateStatusEffects(effects):
    statusEffectElements = []
    buildVisibleEffectDict()

    for effect in effects:
        # Maybe we should skip this?
        if not visibleEffectDict.get(effect.effectId, 0):
            continue

        if not effect.isVisible():
            continue

        # Start building the Effect Icon.
        background, icon, iconScale, extraGeom, iconSuffix, bgSuffix = SEG.getBackgroundAndIconNames(effect, effect.effectId)
        if type(extraGeom) not in (list, tuple, set):
            extraGeom = [extraGeom]
        bgImage = statusEffectImages.find('**/' + background + bgSuffix)
        statusEffectBase = ScalingButton(
            relief=None,
            image=bgImage
        )
        bgSequence = None
        # If we're using the default, greyscale background, color it based on the effect
        # being a buff or a debuff
        if background == 'default':
            bgColor, bgSequence = SEG.getCustomBackgroundColor(effect, effect.effectId, bgNode=statusEffectBase, extraGeom=extraGeom)
            if effect.isDisabled():
                bgColor = Vec4(0.5, 0.5, 0.5, 1.0)
            statusEffectBase.configure(image_color=bgColor)
        statusEffectBase.bgSequence = bgSequence
        # Start the effect now if we have it
        if statusEffectBase.bgSequence:
            statusEffectBase.bgSequence.loop()
        statusEffectIcon = DirectFrame(
            parent=statusEffectBase,
            relief=None
        )
        if icon != '':
            iconImage = statusEffectImages.find('**/' + icon + iconSuffix) if type(icon) is str else icon
            statusEffectIcon.configure(image=iconImage)
            if iconScale:
                statusEffectIcon.configure(image_scale=iconScale)
            if effect.isDisabled():
                statusEffectIcon.configure(image_color=Vec4(0.5, 0.5, 0.5, 1.0))
        for geom in extraGeom:
            geom.reparentTo(statusEffectIcon)
        roundsLabel = DirectLabel(
            parent=statusEffectIcon,
            relief=None
        )
        rounds = SEG.getRoundsValue(effect, effect.effectId)
        if type(rounds) is str or rounds > 0:
            roundsLabel['text'] = str(rounds)
            roundsLabel['text_fg'] = Vec4(1, 1, 1, 1)
            roundsLabel['text_shadow'] = Vec4(0, 0, 0, 1)
            roundsLabel.setPos(0.25, 0, -0.45)
            roundsLabel.setScale(0.6)
        statusEffectElements.append(statusEffectBase)

    return statusEffectElements


def fitStatusEffectsIntoSlots(slots, statusEffects, offset, backButton, forwardButton):
    maxOffset = max(0, len(statusEffects) - len(slots))

    # Clamp offset to prevent out-of-range errors
    offset = max(0, min(offset, maxOffset))

    # Make all slots visible
    for slot in slots:
        slot['image_color'] = Vec4(1, 1, 1, 1)

    # Hide all effects
    for effect in statusEffects:
        effect.hide()

    # Show and reposition all status effects within the current range
    for i in range(min(len(statusEffects), len(slots))):
        effect = statusEffects[i + offset]
        effect.reparentTo(slots[i])
        effect.show()
        # Make slot transparent
        slots[i]['image_color'] = Vec4(0, 0, 0, 0)

    # Enable/disable cycle buttons based on if at min and/or max offset.
    if offset == 0:
        backButton['image_color'] = (0.5, 0.5, 0.5, 1)
        backButton['state'] = DGG.DISABLED
    else:
        backButton['image_color'] = (1, 1, 1, 1)
        backButton['state'] = DGG.NORMAL

    if offset == maxOffset:
        forwardButton['image_color'] = (0.5, 0.5, 0.5, 1)
        forwardButton['state'] = DGG.DISABLED
    else:
        forwardButton['image_color'] = (1, 1, 1, 1)
        forwardButton['state'] = DGG.NORMAL


# -=-=-=-=-=-=-=-=-= #
# Info Panel Classes #
# -=-=-=-=-=-=-=-=-= #
class StatusEffectCard(DirectFrame):
    def __init__(self, parent=aspect2d, **kwargs):
        optiondefs = (
            ('isToon', True, None),
        )

        self.defineoptions(kwargs, optiondefs)
        DirectFrame.__init__(self, parent, **kwargs)
        self.initialiseoptions(self.__class__)

        # Load models
        tooltipGUI = base.loader.loadModel('phase_3.5/models/gui/battlegui/info_panels')

        self.background = DirectFrame(
            parent=self,
            relief=None,
            image=tooltipGUI.find('**/info_panel_buff'+ ('_toon' if self['isToon'] else '_suit')),
            image_scale=(1, 1, 0.25)
        )
        self.iconNode = DirectFrame(
            parent=self.background,
            relief=None,
            pos=(-0.33, 0, 0.001),
            scale=0.15
        )
        self.titleLabel = DirectLabel(
            parent=self.background,
            relief=None,
            pos=(0.086, 0, 0.043),
            text='',
            text_scale=0.047,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_wordwrap=200
        )
        self.descriptionLabel = DirectLabel(
            parent=self.background,
            relief=None,
            pos=(0.086, 0, 0.01),
            text='',
            text_scale=0.029,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_wordwrap=23
        )
        self.bgSequence = None

        # Cleanup loaded models
        tooltipGUI.removeNode()

    def destroy(self):
        if self.bgSequence:
            self.bgSequence.finish()
        del self.bgSequence
        DirectFrame.destroy(self)
        del self.background
        del self.iconNode
        del self.titleLabel
        del self.descriptionLabel

    def setStatusEffect(self, effect, icon):
        if self.bgSequence:
            self.bgSequence.finish()
            self.bgSequence = None

        # Load models
        tooltipGUI = base.loader.loadModel('phase_3.5/models/gui/battlegui/info_panels')

        # Choose border type (buff or debuff)
        if SEG.StatusEffectId2Type.get(effect.effectId) == SEG.BUFF:
            cardBorder = tooltipGUI.find('**/info_panel_buff'+ ('_toon' if self['isToon'] else '_suit'))
        else:
            cardBorder = tooltipGUI.find('**/info_panel_debuff'+ ('_toon' if self['isToon'] else '_suit'))
        self.background['image'] = cardBorder
        self.background['image_scale'] = (1, 1, 0.25)
        icon['state'] = DGG.DISABLED
        icon.reparentTo(self.iconNode)
        if icon.bgSequence:
            self.bgSequence = icon.bgSequence

        # Set text labels
        effectTitle, effectDesc = SEG.makeTitleAndDesc(effect, effect.effectId)
        self.titleLabel['text'] = effectTitle
        self.titleLabel['text_scale'] = 0.047
        capTextScaleToWidth(self.titleLabel, 0.65)
        self.descriptionLabel['text'] = effectDesc

        # Cleanup loaded models
        tooltipGUI.removeNode()


class InformationPanel(DirectFrame):
    def __init__(self, parent=aspect2d, **kwargs):
        optiondefs = (
            ('isToon', True, None),
        )

        self.defineoptions(kwargs, optiondefs)
        DirectFrame.__init__(self, parent, **kwargs)
        self.initialiseoptions(self.__class__)

        self.statusEffects = []

        # Load models
        tooltipGUI = base.loader.loadModel('phase_3.5/models/gui/battlegui/info_panels')
        keybindsGUI = base.loader.loadModel('phase_3.5/models/gui/optionspage/keybinds_gui.bam')

        self.background = DirectFrame(
            parent=self,
            relief=None,
            image=tooltipGUI.find('**/info_panel_main' + ('_toon' if self['isToon'] else '_suit')),
            image_scale=(1, 1, 0.5),
            frameSize=(-0.485, 0.485, -0.235, 0.235)
        )
        # To block from interacting with stuff behind the panel
        self.background['state'] = DGG.NORMAL
        self.statusEffectsFrame = ScrollWheelFrame(
            parent=self.background,
            relief=None,
            frameSize=(-0.22, 0.25, -0.2315, 0.1425),
            canvasSize=(-0.22, 0.1, -0.0425, 0.048),
            scrollDistance=0.1,
            scrollCondition=lambda: len(self.statusEffects) > 4,
            pos=(0.226, 0, 0)
        )
        self.statusEffectsFrame['verticalScroll_thumb_image'] = tooltipGUI.find('**/scroll_thumb' + ('_toon' if self['isToon'] else '_suit'))
        self.statusEffectsFrame['verticalScroll_resizeThumb'] = False
        self.statusEffectsFrame['verticalScroll_relief'] = None
        self.statusEffectsFrame['verticalScroll_thumb_relief'] = None
        self.statusEffectsFrame['verticalScroll_thumb_frameSize'] = (-1, 1, -2, 2)
        self.statusEffectsFrame['verticalScroll_thumb_image_scale'] = (0.25, 1, 0.125)
        self.statusEffectsFrame.verticalScroll.incButton.hide()
        self.statusEffectsFrame.verticalScroll.decButton.hide()

        self.verticalScrollNode = DirectFrame(
            parent=self.background,
            relief=None,
            pos=(0.35925, 0, 0.002),
            scale=(0.5, 1, 1)
        )
        self.statusEffectsFrame.verticalScroll.reparentTo(self.verticalScrollNode)

        self.exitButton = DirectButton(
            parent=self.background,
            relief=None,
            image=(
                keybindsGUI.find('**/button_neutral'),
                keybindsGUI.find('**/button_click'),
                keybindsGUI.find('**/button_highlight')
            ),
            pos=(0.46, 0, 0.21),
            scale=0.05
        )

        self.setBin('sorted-gui-popup', GuiBinGlobals.BattleInfoTooltipExtended)

        # Unload models
        tooltipGUI.removeNode()
        keybindsGUI.removeNode()

    def destroy(self):
        DirectFrame.destroy(self)
        del self.background
        del self.statusEffectsFrame
        del self.verticalScrollNode

    def addStatusEffect(self, effect, icon):
        newStatusEffect = StatusEffectCard(
            parent=self.statusEffectsFrame.getCanvas(),
            relief=None,
            isToon=self['isToon'],
            pos=(0, 0, 0.003 + len(self.statusEffects) * -0.095),
            scale=0.495
        )
        newStatusEffect.setStatusEffect(effect, icon)
        self.statusEffects.append(newStatusEffect)

    def setStatusEffects(self, effects):
        icons = generateStatusEffects(effects)

        for i in range(len(effects)):
            self.addStatusEffect(effects[i], icons[i])

        self.statusEffectsFrame['canvasSize'] = (-0.22, 0.1, -0.0425 + (len(self.statusEffects) - 1) * -0.095, 0.048)

        if len(effects) <= 4:
            self.statusEffectsFrame.verticalScroll.hide()


class ToonInformationPanel(InformationPanel):
    def __init__(self, parent=aspect2d, **kwargs):
        optiondefs = (
            ('isToon', True, None),
        )

        self.defineoptions(kwargs, optiondefs)
        InformationPanel.__init__(self, parent, **kwargs)
        self.initialiseoptions(self.__class__)

        self.titleText = DirectLabel(
            parent=self.background,
            relief=None,
            text='',
            text_font=ToontownGlobals.getMinnieFont(),
            text_fg=(0.976, 0.788, 0.165, 1),
            text_shadow=(0, 0, 0, 1),
            text_pos=(0, 0.197)
        )

        self.inventoryNode = DirectFrame(
            parent=self.background,
            relief=None,
            pos=(-0.238, 0, -0.04),
            scale=0.495
        )

    def destroy(self):
        InformationPanel.destroy(self)
        del self.titleText

    def setToonInfo(self, av):
        name = av.getName()
        self.titleText['text'] = name
        self.titleText['text_scale'] = getTextScaleAfterLength(name, 40, modifier=0.0006, baseScale=0.035)

        # Create gag tracks
        tracksFrame = generateAvatarPanelTracks(av)
        tracksFrame.reparentTo(self.inventoryNode)


class SuitInformationPanel(InformationPanel):
    def __init__(self, parent=aspect2d, **kwargs):
        optiondefs = (
            ('isToon', False, None),
        )

        self.defineoptions(kwargs, optiondefs)
        InformationPanel.__init__(self, parent, **kwargs)
        self.initialiseoptions(self.__class__)

        self.titleText = DirectLabel(
            parent=self.background,
            relief=None,
            text='',
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont(),
            text_scale=0.035,
            text_pos=(0, 0.203)
        )

        self.modsTitleText = DirectLabel(
            parent=self.background,
            relief=None,
            text=TTLocalizer.SuitTooltipTitle,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont(),
            text_scale=0.035,
            text_pos=(-0.238, 0.157)
        )

        self.infoText = DirectLabel(
            parent=self.background,
            relief=None,
            text='',
            text_pos=(-0.238, 0.11),
            text_scale=0.017
        )

        self.effectsTitleText = DirectLabel(
            parent=self.background,
            relief=None,
            text=TTLocalizer.StatusEffectTitle,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_font=ToontownGlobals.getSuitFont(),
            text_scale=0.035,
            text_pos=(0.248, 0.157)
        )

    def destroy(self):
        InformationPanel.destroy(self)
        del self.titleText
        del self.modsTitleText
        del self.infoText
        del self.effectsTitleText

    def setSuitInfo(self, av):
        name = av.getName()
        self.titleText['text'] = name

        self.infoText['text'] = generateSuitModifierText(av)


class MasterInformationPanel:
    def __init__(self):
        self.informationPanel = None
        self.av = None

        self.baseScale = 2
        self.panelNode = DirectFrame(
            relief=None,
            scale=self.baseScale
        )
        self.panelNode.setBin('gui-popup', 100)

    def cleanup(self):
        self.clearPanel()
        del self.informationPanel
        del self.av
        self.panelNode.destroy()
        del self.panelNode

    def setPanel(self, av, panel):
        self.clearPanel()
        self.informationPanel = panel
        self.informationPanel.reparentTo(self.panelNode)
        self.informationPanel.exitButton.configure(command=self.clearPanel)
        Sequence(
            LerpScaleInterval(self.panelNode, .2, self.baseScale * 1.1, self.baseScale * 0.01, blendType='easeInOut'),
            LerpScaleInterval(self.panelNode, .09, self.baseScale, blendType='easeInOut')).start()
        self.av = av

    def clearPanel(self):
        if self.informationPanel is not None:
            self.informationPanel.destroy()
            self.informationPanel = None
            self.av = None
