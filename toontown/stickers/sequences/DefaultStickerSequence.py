import math
from typing import Optional, TYPE_CHECKING

from direct.interval.IntervalGlobal import *
from panda3d.core import NodePath, LVecBase3f

from toontown.inventory.enums.ItemEnums import ChatStickersItemType
from toontown.inventory.registry import ItemTypeRegistry
from toontown.stickers.sequences.StickerSequenceBase import StickerSequenceBase

if TYPE_CHECKING:
    from toontown.inventory.registry.ChatStickerRegistry import ChatStickerDefinition


class DefaultStickerSequence(StickerSequenceBase):
    def __init__(self, worldParent: NodePath, toon: NodePath, stickerSubtype: ChatStickersItemType, modifier: Optional[int] = None):
        super().__init__(worldParent, toon, stickerSubtype)
        self._stickerDefinition: 'ChatStickerDefinition' = ItemTypeRegistry.getItemDefinition(stickerSubtype)
        self._stickerAssetNode = self._stickerDefinition.getItemModel(None, modifier)
        self._stickerSoundEffect = self._stickerDefinition.getStickerSound()
        self._stickerParentNode = NodePath("Sticker-Parent")
        self._stickerSequence: Optional[Sequence] = None
        self._toonSequence: Optional[Sequence] = None
        self._modifier = modifier
        self.accept(self.toon.uniqueName('toonMoved'), self.stopSequence)

    """
    Sequence Actions
    """

    def startSequence(self):
        # Attempt to place the sticker to start.
        if not self._placeSticker():
            return

        # Configure properties of sticker sequence.
        self._configureStickerSequence()

        # Create the sequences.
        self._stickerSequence = self._makeStickerSequence()
        self._toonSequence = self._makeToonSequence()

        # Play the sequence.
        self._toonSequence.start()

    def stopSequence(self):
        self.ignoreAll()
        self.enableEmotes()

        if self._toonSequence:
            self._toonSequence.pause()
            self._toonSequence = None

    def cleanupStickerSequence(self):
        if self._stickerSequence:
            self._stickerSequence.pause()
            self._stickerSequence = None

        if self._stickerAssetNode:
            self._stickerAssetNode.removeNode()
            self._stickerAssetNode = None

        if self._stickerParentNode:
            self._stickerParentNode.removeNode()
            self._stickerParentNode = None

        self._stickerDefinition = None

    """
    Subsequence Building
    """

    def _makeStickerSequence(self) -> Sequence:
        scaleSeq = self._makeStickerScaleSequence()
        posSeq = self._makeStickerPosSequence()
        cleanupSeq = self._makeStickerCleanupSequence(scaleSeq, posSeq)
        return Sequence(
            # Parent the sticker to the world, now the hand is in place
            Func(self.__parentStickerToGeom),

            # Spawn the Sticker
            Parallel(
                # Sticker Scale Animation
                scaleSeq,
                # Sticker Floating Animation
                posSeq,
                # Sticker Cleanup
                cleanupSeq
            )
        )

    def _makeStickerScaleSequence(self) -> Sequence:
        stickerScale = self._getStickerSize()
        return Sequence(
            # Make the sticker appear
            LerpScaleInterval(self._stickerAssetNode, duration=0.2, scale=stickerScale, blendType="easeIn"),

            # Display the sticker for 3 seconds
            Func(base.playSfx, self._stickerSoundEffect, looping=0),
            LerpScaleInterval(self._stickerAssetNode, duration=0.05, scale=stickerScale, blendType="easeOut"),

            # Display the sticker for a while
            Wait(4),

            # Hide the sticker
            LerpScaleInterval(self._stickerAssetNode, duration=0.05, scale=stickerScale, blendType="easeIn"),
            LerpScaleInterval(self._stickerAssetNode, duration=0.2, scale=0.001, blendType="easeOut"),
        )

    def _makeStickerPosSequence(self) -> Sequence:
        stickerScale = self._getStickerSize()
        zscale = stickerScale[2]
        return Sequence(
            LerpPosInterval(self._stickerAssetNode, 1.125, (0, 0, 0.25 * zscale), blendType="easeInOut"),
            LerpPosInterval(self._stickerAssetNode, 1.125, (0, 0, 0), blendType="easeInOut"),
            LerpPosInterval(self._stickerAssetNode, 1.125, (0, 0, 0.25 * zscale), blendType="easeInOut"),
            LerpPosInterval(self._stickerAssetNode, 1.125, (0, 0, 0), blendType="easeInOut")
        )

    def _makeStickerCleanupSequence(self, *seqs: Sequence):
        return Sequence(
            Wait(max(seq.getDuration() for seq in seqs) + 0.01),
            Func(self.cleanupStickerSequence),
        )

    def _makeToonSequence(self) -> Sequence:
        if self.toon.isDisguised and self.toon.suit:
            return Sequence(
                # Disable emotes
                Func(self.disableEmotes),
                Parallel(
                    Sequence(
                        ActorInterval(self.toon.suit, 'sticker', playRate=1.2),
                        # Return to normal
                        Func(self.toon.suit.loop, 'neutral'),
                    ),
                    Sequence(
                        Wait(self.toon.getDuration("toss", toFrame=20) / 2.6),
                        # Start the sticker sequence
                        Func(self._stickerSequence.start),
                        # Wait for the hand to go away
                        Wait(self.toon.getDuration("toss", fromFrame=21, toFrame=30) / 3.0),
                        Wait(self.toon.getDuration("toss", toFrame=30)),
                        Func(self.stopSequence),
                    ),
                ),
            )
        else:
            return Sequence(
                # Disable emotes
                Func(self.disableEmotes),

                # Present the hand
                Func(self.toon.setPlayRate, 3.0, 'toss'),
                Func(self.toon.play, "toss", None, 0, 20),
                Wait(self.toon.getDuration("toss", toFrame=20) / 3.0),

                # Start the sticker sequence
                Func(self._stickerSequence.start),

                # Present the hand
                Func(self.toon.play, "toss", None, 21, 30),  # Start from 21 to continue from the start of the Seq.
                Wait(self.toon.getDuration("toss", fromFrame=21, toFrame=30) / 3.0),

                # Put the hand away
                Func(self.toon.setPlayRate, -1.0, 'toss'),  # -1 so the animation plays backwards (Frame 30 -> 0)
                Func(self.toon.play, "toss", None, 0, 30),
                Wait(self.toon.getDuration("toss", toFrame=30)),

                # Return to normal
                Func(self.toon.loop, 'neutral'),
                Func(self.stopSequence)
            )

    """
    Sequence Configs
    """

    def _placeSticker(self) -> bool:
        # First place the node onto the right hand
        parentNode = self._getStickerParentNode()
        if parentNode.isEmpty():
            return False

        if self.toon.isDisguised and self.toon.suit:
            self._stickerParentNode.reparentTo(self.worldParent)
            relPos = self.worldParent.getRelativePoint(parentNode, self._getStickerParentOffset())
            self._stickerParentNode.setPos(relPos)
        else:
            self._stickerParentNode.reparentTo(parentNode)
            self._stickerParentNode.setPos(*self._getStickerParentOffset())

        # Attach the sticker to the parent node.
        # We do this, so it's easier to move the sticker during the sequence.
        self._stickerAssetNode.reparentTo(self._stickerParentNode)
        self._stickerAssetNode.setBillboardPointEye()
        self._stickerAssetNode.setPos(0, 0, 0)
        self._stickerAssetNode.setScale(0.01)
        return True

    def _configureStickerSequence(self):
        self._stickerSoundEffect.setPlayRate(self.__getStickerPitch())

    def _getStickerParentNode(self):
        if self.toon.isDisguised and self.toon.suit:
            return self.toon.suit.getRightHand()
        return self.toon.getRightHand()

    def _getStickerParentOffset(self):
        if self.toon.isDisguised and self.toon.suit:
            return -0.07, 0.3, -1.45
        return 0, 0.2, 1

    def __parentStickerToGeom(self):
        """Parents the sticker to the worlds' geom, so it exists in world space."""
        if self.toon.isDisguised and self.toon.suit:
            parentNode = self._getStickerParentNode()
            if parentNode.isEmpty():
                return
            relPos = self.worldParent.getRelativePoint(parentNode, self._getStickerParentOffset())
            self._stickerParentNode.reparentTo(self.worldParent)
            self._stickerParentNode.setPosHpr(*relPos, 0, 0, 0)
        else:
            positionInWorld = self._stickerParentNode.getPos(self.worldParent)
            self._stickerParentNode.reparentTo(self.worldParent)
            # Reset the HPR so there's no rotation from the hand applied.
            self._stickerParentNode.setPosHpr(*positionInWorld, 0, 0, 0)

    """
    Constant Getters
    """

    def _getStickerSize(self):
        toonScale = self.__getToonScale()
        stickerScale = self._stickerDefinition.getStickerScale3D()
        if type(stickerScale) not in (list, tuple):
            stickerScale = (stickerScale, stickerScale, stickerScale)

        return LVecBase3f(stickerScale[0]*toonScale[0], stickerScale[1]*toonScale[1], stickerScale[2]*toonScale[2])

    def __getStickerPitch(self):
        return math.sqrt(1 / max(0.1, self.__getToonScale(asFloat=True)))

    def __getToonScale(self, asFloat: bool = False):
        if not self.toon:
            return 1.0
        if not self.toon.getGeomNode():
            return 1.0
        if not self.toon.getGeomNode().getChild(0):
            return 1.0
        if self.toon.isDisguised and self.toon.suit:
            from toontown.suit import SuitGlobals
            suitAttrs = SuitGlobals.suitProperties[self.toon.suit.style.name]
            suitScale = suitAttrs[SuitGlobals.SCALE_INDEX]
            scale = LVecBase3f(suitScale, suitScale, suitScale)
        else:
            scale = self.toon.getGeomNode().getChild(0).getScale()
        if asFloat:
            if isinstance(scale, LVecBase3f):
                x, y, z = scale
                return (x + y + z) / 3
            return scale
        else:
            if isinstance(scale, LVecBase3f):
                return LVecBase3f(*scale)
            return LVecBase3f(scale)
