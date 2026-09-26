from toontown.utils import ColorHelper

if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    # base.initCR()  # defines base.cr
    # base.startHeadlessShow()

from toontown.gui.GUINode import GUINode

from toontown.gui.game.condition.ConditionFrame import ConditionFrame
from toontown.gui.game.condition.ConditionGlobals import ConditionArgs, ConditionArg, ConditionState, ConditionSide, ConditionStateArgs

from toontown.gui.game.condition.subframes.ConditionSubframeBase import ConditionSubframeBase
from toontown.gui.hover.HoverFrameTypes import HoverFrameTypes
from toontown.gui import TTGui
from toontown.toonbase import ToontownGlobals

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from toontown.inventory.enums import RarityEnums
from toontown.inventory.enums.ItemEnums import MaterialItemType, ItemType
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle import BattleGlobals
from toontown.toon import NPCToons
from toontown.toon.ToonHead import ToonHead
from toontown.toonbase import TTLocalizer

from direct.gui.DirectGui import DirectLabel, OnscreenImage
from direct.interval.IntervalGlobal import LerpFunctionInterval, Sequence, Wait
from panda3d.core import *
from typing import Optional


@DirectNotifyCategory()
class ScavengeConditionFrame(ConditionFrame):
    """
    Scavenge condition frames for receiving new hammerspace items.
    """
    HoverFrameType = HoverFrameTypes.Scavenge
    ConditionPatternTexture = 'core/gui/maps/cc_t_gui_sframe_pat_testgrayscale.png'

    @InjectorTarget
    def __init__(self, parent, **kw):
        # Perform GUI boilerplate.
        optiondefs = TTGui.kwargsToOptionDefs(
            dismissable=True,
            subframeStart=0.21,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(ScavengeConditionFrame)

        self.iconHolder: GUINode = GUINode(self.anchor)
        self.icon: Optional[NodePath] = None

        self.currencySubtype = self.obj.getItemSubtype()
        self.isCurrencyPopup = self.currencySubtype in (
            MaterialItemType.Jellybeans,
            MaterialItemType.Gumballs,
            MaterialItemType.PinkSlips,
            MaterialItemType.CeaseAndDesists,
            MaterialItemType.Counterfeits,
        )
        self.currencyCount = None
        self.currencyCountSeq = None

        self.isIOUPopup = self.obj.getItemType() == ItemType.IOU
        self.iouHead = None
        self.iouCard = None
        self.iouTrackLabel = None
        self.iouNameLabel = None
        self.iouBoostLabel = None
        self.iouQuantityLabel = None

        if self.isCurrencyPopup:
            self.frame.setColorScale(1, 1, 1, 0)

    def destroy(self):
        if self.currencyCountSeq:
            self.currencyCountSeq.pause()
            self.currencyCountSeq = None

        for elementName in (
            'iouTrackLabel',
            'iouNameLabel',
            'iouBoostLabel',
            'iouQuantityLabel',
        ):
            element = getattr(self, elementName, None)
            if element:
                element.destroy()
                setattr(self, elementName, None)

        if self.iouHead:
            self.iouHead.cleanup()
            self.iouHead.removeNode()
            self.iouHead = None

        if self.iouCard:
            self.iouCard.removeNode()
            self.iouCard = None

        super().destroy()

    def __setCurrencyCount(self, value):
        if not self.currencyCount:
            return

        amount = int(round(value))
        if self.currencySubtype == MaterialItemType.Gumballs:
            countText = 'x%d' % amount
        else:
            countText = '+%d' % amount

        self.currencyCount['text'] = countText

    def __createCurrencyVisuals(self):
        if self.currencySubtype == MaterialItemType.Jellybeans:
            self.icon = OnscreenImage(
                parent=self.iconHolder,
                image='gui/common/maps/cc_t_gui_icon_jellybeanJar_1.png',
                pos=(0, 0, 0),
                scale=0.115,
            )
        elif self.currencySubtype == MaterialItemType.Gumballs:
            self.icon = OnscreenImage(
                parent=self.iconHolder,
                image='gui/common/maps/cc_t_gui_icon_gumball_1.png',
                pos=(0, 0, 0),
                scale=0.115,
            )
        else:
            model = loader.loadModel('phase_3.5/models/gui/battlegui/status_effects')
            nodeName = {
                MaterialItemType.PinkSlips: 'pinkslip_icon',
                MaterialItemType.CeaseAndDesists: 'sued_icon',
                MaterialItemType.Counterfeits: 'counterfeit_icon',
            }[self.currencySubtype]
            node = model.find('**/' + nodeName)
            self.icon = NodePath(node.node().makeCopy())
            self.icon.reparentTo(self.iconHolder)
            self.icon.setScale(0.19)

        self.icon.setTransparency(TransparencyAttrib.MAlpha)

        mult = 1 if self.side == ConditionSide.LEFT else -1
        if self.currencySubtype == MaterialItemType.Gumballs:
            countText = 'x0'
            countScale = 0.054
            countColor = (1.0, 0.55, 0.78, 1)
            countShadowOffset = (0.028, 0.028)
            countPos = (mult * 0.165, -0.01, -0.082)
        elif self.currencySubtype == MaterialItemType.Jellybeans:
            countText = '+0'
            countScale = 0.062
            countColor = (1.0, 0.15, 0.15, 1)
            countShadowOffset = (0.036, 0.036)
            countPos = (mult * 0.112, -0.01, -0.06)
        elif self.currencySubtype == MaterialItemType.PinkSlips:
            countText = '+0'
            countScale = 0.058
            countColor = (1.00, 0.80, 0.76, 1)
            countShadowOffset = (0.028, 0.028)
            countPos = (mult * 0.165, -0.01, -0.082)
        elif self.currencySubtype == MaterialItemType.CeaseAndDesists:
            countText = '+0'
            countScale = 0.058
            countColor = (0.82, 0.74, 1.00, 1)
            countShadowOffset = (0.028, 0.028)
            countPos = (mult * 0.165, -0.01, -0.082)
        else:
            countText = '+0'
            countScale = 0.058
            countColor = (0.78, 0.96, 0.91, 1)
            countShadowOffset = (0.028, 0.028)
            countPos = (mult * 0.165, -0.01, -0.082)

        self.currencyCount = DirectLabel(
            parent=self.anchor,
            relief=None,
            text=countText,
            text_font=ToontownGlobals.getToonFont(),
            text_align=TextNode.ACenter,
            text_scale=countScale,
            text_fg=countColor,
            text_shadow=(0, 0, 0, 1),
            text_shadowOffset=countShadowOffset,
            pos=countPos,
        )

        amount = max(0, self.obj.getQuantity())
        rollDuration = 1.15 if self.currencySubtype == MaterialItemType.Gumballs else 0.9
        self.currencyCountSeq = Sequence(
            Wait(0.15),
            LerpFunctionInterval(
                self.__setCurrencyCount,
                fromData=0,
                toData=amount,
                duration=rollDuration,
                blendType='easeOut',
            ),
        )
        self.currencyCountSeq.start()

    def __createIOUVisuals(self):
        definition = self.obj.getItemDefinition()
        npcId = definition.getNpcId()
        npcToon = NPCToons.NPCToonDict.get(npcId)
        if not npcToon:
            self.notify.warning(
                'Unable to find NPC data for IOU NPC ID %s.' % npcId
            )
            return

        track = definition.getGagTrack()
        boost = definition.getBoost()
        quantity = max(1, self.obj.getQuantity())

        if track == -1:
            trackName = 'ALL GAGS'
            trackColor = (0.35, 0.35, 0.8, 1)
        else:
            trackName = TTLocalizer.BattleGlobalTracksUpper[track]
            rawTrackColor = BattleGlobals.TrackColors[track]
            trackColor = (rawTrackColor[0], rawTrackColor[1], rawTrackColor[2], 1)

        boostTerm = {
            AttackEnum.TOON_HEAL: 'LAFF',
            AttackEnum.TOON_LURE: 'KNOCKBACK',
        }.get(track, 'DAMAGE')

        # Use the real SOS/IOU card model as the popup background.
        cardModel = loader.loadModel('phase_3.5/models/gui/battlegui/sos_card')

        # The BAM root is a SequenceNode. Copy every direct child into a
        # normal static node so the complete card is shown without animation.
        self.iouCard = self.anchor.attachNewNode('iou-card')
        sequenceNode = cardModel.find('**/+SequenceNode')
        if sequenceNode.isEmpty():
            sequenceNode = cardModel

        for child in sequenceNode.getChildren():
            child.copyTo(self.iouCard)

        cardModel.removeNode()

        self.iouCard.setScale(0.45)
        self.iouCard.setPos(
            (0.24 if self.side == ConditionSide.LEFT else -0.24),
            0.02,
            -0.005,
        )
        self.iouCard.setTransparency(TransparencyAttrib.MAlpha)
        self.iouCard.setColorScale(trackColor)
        self.iouCard.setDepthWrite(False)
        self.iouCard.setDepthTest(False)
        self.iouCard.setBin('fixed', -10)

        # Fully hide the normal scavenge frame. Making it transparent still
        # lets it write to the depth buffer, which causes the two frames to
        # flicker against each other.
        self.frame.hide()

        # 3-D NPC head rendered directly in the 2-D popup.
        npc = NPCToons.createLocalNPC(npcId)
        if not npc:
            return
        self.iouHead = ToonHead()
        self.iouHead.setupHead(npc.getStyle(), forGui=1)
        self.iouHead.fitAndCenterHead(0.44, forGui=1)
        npc.removeNode()
        self.iouHead.reparentTo(self.iconHolder)
        self.iouHead.setPos(0.15, 0, 0.002)
        self.iouHead.setScale(0.08)

        mult = 1 if self.side == ConditionSide.LEFT else -1

        self.iouTrackLabel = DirectLabel(
            parent=self.anchor,
            relief=None,
            pos=(mult * 0.250, -0.01, 0.105),
            text=trackName,
            text_font=ToontownGlobals.getSignFont(),
            text_scale=0.042,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_align=TextNode.ACenter,
        )

        self.iouNameLabel = DirectLabel(
            parent=self.anchor,
            relief=None,
            pos=(mult * 0.250, -0.01, -0.065),
            text=npcToon.name,
            text_font=ToontownGlobals.getBuildingNametagFont(),
            text_scale=0.036,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_align=TextNode.ACenter,
            text_wordwrap=8.0,
        )

        self.iouBoostLabel = DirectLabel(
            parent=self.anchor,
            relief=None,
            pos=(mult * 0.250, -0.01, -0.135),
            text='+%d %s' % (boost, boostTerm),
            text_font=ToontownGlobals.getSignFont(),
            text_scale=0.037,
            text_fg=trackColor,
            text_shadow=(0, 0, 0, 1),
            text_align=TextNode.ACenter,
        )

        self.iouQuantityLabel = DirectLabel(
            parent=self.anchor,
            relief=None,
            pos=(mult * 0.265, -0.01, -0.04),
            text='+%d' % quantity,
            text_font=ToontownGlobals.getSignFont(),
            text_scale=0.055,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_align=TextNode.ACenter,
        )

    """
    Visuals
    """

    def getRarityColor(self):
        return RarityEnums.RarityColors[self.obj.getRarity()]

    def getConditionScaledColor(self):
        return self.getRarityColor()

    def getConditionPatternColor(self):
        rarityColor = self.getRarityColor()
        newCol = ColorHelper.lerpColor(rarityColor, (1, 1, 1, 1), 0.3)
        newCol = (newCol[0], newCol[1], newCol[2], 0.6)
        return newCol

    def getFrameScale(self) -> float:
        """
        Gets the scale of this frame.
        Index is the actual index position on da side.
        """
        return super().getFrameScale() * 1.12

    """
    Subclass Interface
    """

    def determineSubframeClasses(self) -> list[type[ConditionSubframeBase]]:
        """
        Given our frame's parameters,
        determine the kinds of subframes to make at this moment.
        """

        # Return no subframes, as we just want the icon
        return []

    def makeConditionArgs(self) -> ConditionArgs:
        """
        Creates a dictionary of ConditionArgs based on our params.
        Subframes will get these.
        """
        args = ConditionArgs()

        # Base args.
        args[ConditionArg.HAMMERSPACE_ITEM] = self.obj

        return args

    def place(self):
        """
        Super call this and implement custom placement logic in base classes.
        """
        super().place()

        mult = 1 if self.side == ConditionSide.LEFT else -1

        if self.isCurrencyPopup:
            if not self.icon:
                self.__createCurrencyVisuals()

            self.iconHolder.setScale(1.0)
            self.iconHolder.setPos(mult * 0.105, 0, -0.005)
            if self.currencyCount:
                if self.currencySubtype == MaterialItemType.Gumballs:
                    self.currencyCount.setPos(mult * 0.165, -0.01, -0.082)
                elif self.currencySubtype == MaterialItemType.Jellybeans:
                    self.currencyCount.setPos(mult * 0.112, -0.01, -0.06)
                else:
                    self.currencyCount.setPos(mult * 0.165, -0.01, -0.082)
            return

        if self.isIOUPopup:
            if not self.iouHead:
                self.__createIOUVisuals()

            self.iconHolder.setScale(1.0)
            self.iconHolder.setPos(mult * 0.105, 0, 0.005)
            return

        if not self.icon:
            try:
                self.icon = self.obj.getItemDefinition().getGuiItemModel(parent=self.iconHolder)
            except (AssertionError, OSError):
                self.notify.warning(
                    'Unable to create inventory popup icon for item type %s, subtype %s.' % (
                        self.obj.getItemType(),
                        self.obj.getItemSubtype(),
                    )
                )
                return

            if not self.icon or self.icon.isEmpty():
                self.notify.warning(
                    'Inventory popup icon is empty for item type %s, subtype %s.' % (
                        self.obj.getItemType(),
                        self.obj.getItemSubtype(),
                    )
                )
                self.icon = None
                return

        # Place and scale normal item model.
        iconScale = 0.85
        self.iconHolder.setScale(iconScale)
        self.iconHolder.setPos(mult * 0.10246, 0, 0)


if __name__ == "__main__":
    from toontown.inventory.base.InventoryItem import InventoryItem
    from toontown.inventory.enums import ItemEnums
    base.setBackgroundColor(0.6, 0.4, 0.2)

    obj = InventoryItem.fromSubtype(ItemEnums.MaterialItemType.Jellybeans, quantity=500)

    gui = ScavengeConditionFrame(
        parent=base.a2dTopLeft,
        pos=(0, 0, -0.1),
        obj=obj,
        conditionState=ConditionState.GLOBAL,
        conditionStateArgs=ConditionStateArgs({
            ConditionArg.HAMMERSPACE_ITEM: obj
        }),
        side=ConditionSide.LEFT,
    )

    # GUITemplateSliders(
    #     gui.headHolder,
    #     'pos', 'scale', 'hpr',
    # )
    gui.buildSubframes()
    base.run()
