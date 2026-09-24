from typing import Optional, List

from panda3d.core import ConfigVariableBool, NodePath
from direct.distributed.ClockDelta import globalClockDelta
from direct.distributed.DistributedObject import ESGenerated
from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from direct.interval.IntervalGlobal import *
from toontown.chat.constants.ChatGlobals import (CFThought, CFTimeout, CFSpeech, CFQuicktalker)
from toontown.nametag import NametagGroup

from otp.avatar.DistributedAvatar import DistributedAvatar
from toontown.clashbattle.battle import BattleGlobals
from toontown.chat.enums.ChatSpeedChatType import ChatSpeedChatType
from toontown.chat.enums.ChatZoneModifier import ChatZoneModifier
from toontown.chat.models.ChatMessage import ChatMessage
from toontown.inventory.base.Inventory import Inventory
from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.enums.ItemEnums import ItemType, ChatStickersItemType, ClothingTopItemType, ClothingBottomItemType, \
    CheesyEffectItemType

from toontown.inventory.registry import ItemTypeRegistry
from toontown.modifiers.ModifierEnums import ModifierType
from toontown.stickers.sequences.StickerSequenceBase import StickerSequenceBase
from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.club.ClubGlobals import ClubItemIndex, ClubMaxNameLength
from toontown.distributed.DelayDeletable import DelayDeletable
from toontown.toon import Experience, GagInventory
from toontown.toon.OldLaffMeter import OldLaffMeter
from toontown.toon.Toon import Toon
from toontown.toonbase import TTLocalizer, ToontownGlobals


class ClashDistributedToonBase(DistributedAvatar, DistributedSmoothNode, Toon, DelayDeletable, BattleAvatar):
    """DistributedToonBase: Client representation of the base class
    for ALL distributed toon objects (players and npcs).
    """

    def __init__(self, cr):
        DistributedAvatar.__init__(self, cr)
        DistributedSmoothNode.__init__(self, cr)
        Toon.__init__(self)
        BattleAvatar.__init__(self)

        self.animalEffect = 0

        self.clubName = ''
        self.clubColor = 1000

        # Sticker Animation
        self.stickerSequence: Optional[StickerSequenceBase] = None

        self.inventory = None
        self.maxCarry = 0
        self.trackBonusLevel = [-1, -1, -1, -1, -1, -1, -1, -1]

        self.announceGenerated: bool = False

        self.equippedItems: List[InventoryItem] = []

    def generate(self):
        DistributedAvatar.generate(self)
        DistributedSmoothNode.generate(self)

    def announceGenerate(self):
        self.announceGenerated = True
        DistributedAvatar.announceGenerate(self)
        DistributedSmoothNode.announceGenerate(self)

    def disable(self):
        self.stopStickerSequence()
        super().disable()

    def delete(self) -> None:
        # Make sure we're cleaned up before deleting.
        self.stopStickerSequence()
        self.notify.debug('delete')
        self.cleanup()
        self.cleanupBattle()
        Toon.delete(self)
        DistributedAvatar.delete(self)
        DistributedSmoothNode.delete(self)
    
    def wrtReparentTo(self, parent):
        # We need to define this in DistributedToon just to force the right function to be called (we need the
        # DistributedSmoothNode flavor to be called, but it wants to call the NodePath flavor instead).
        DistributedSmoothNode.wrtReparentTo(self, parent)

    def d_setParent(self, parentToken):
        DistributedSmoothNode.d_setParent(self, parentToken)

    # We need to force the Toon version of these to be called, otherwise
    # we get the generic Avatar version which is undefined
    def setDNAString(self, dnaString):
        Toon.setDNAString(self, dnaString)

    def setDNA(self, dna):
        Toon.setDNA(self, dna)

    def getDialogueArray(self, *args):
        # Force the right inheritance chain to be called
        return Toon.getDialogueArray(self, *args)

    def request(self, name, *args):
        fsm = self.animFSM

        if isinstance(name, str) and name and name[0].isupper():
            lower = name[0].lower() + name[1:]
            try:
                stateNames = [s.getName() for s in fsm.getStates()]
            except Exception:
                stateNames = list(getattr(fsm, 'stateDict', {}).keys())
            if lower in stateNames:
                name = lower

        if not args:
            return fsm.request(name)

        # Already a single enterArgList
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            return fsm.request(name, list(args[0]))

        # Fallback: pack everything into enterArgList
        return fsm.request(name, list(args))

    ### setAnimState ###

    def b_setAnimState(self, animName, animMultiplier = 1.0, callback = None, extraArgs = []):
        self.d_setAnimState(animName, animMultiplier, None, extraArgs)
        self.setAnimState(animName, animMultiplier, None, None, callback, extraArgs)

    def d_setAnimState(self, animName, animMultiplier = 1.0, timestamp = None, extraArgs = []):
        timestamp = globalClockDelta.getFrameNetworkTime()
        self.sendUpdate('setAnimState', [animName, animMultiplier, timestamp])

    def setAnimState(self, animName, animMultiplier=1.0, timestamp=None, animType=None,
                     callback=None, extraArgs=[]):
        if not animName or animName == 'None':
            return

        if timestamp is None:
            ts = 0.0
        else:
            ts = globalClockDelta.localElapsedTime(timestamp)

        if ConfigVariableBool('check-invalid-anims', True).getValue():
            if animMultiplier > 1.0 and animName in ['neutral']:
                animMultiplier = 1.0

        # One list = enterArgList for ClassicFSM
        self.request(animName, [animMultiplier, ts, callback, extraArgs])
    
    def setName(self, name):
        super().setName(name)
        self.setDisplayName(name)

    def setDisplayName(self, name):
        """
        Sets the name that is displayed in the 3-d and 2-d nametags,
        but not the name that is used to prefix chat msgs.

        :param name: The name to set.
        :param tagString: A string to render underneath.
        :param tagStringColor: The color index to use. Sourced from ClubGlobals item IDs.
        """
        if not hasattr(self, 'nametag'):
            return

        # Set the nametag's name.
        if not name:
            name = self._name
        self.nametag.setName(name)

        # Now, start to build the display name.
        # First, get the toon's tag.
        if self.npcType:
            if self.playerType == NametagGroup.CCNoChat:
                name = f'\1NonPlayer\1{name}\2'
            elif self.playerType == NametagGroup.CCSuit:
                name = f'\1CogGray\1{name}\2'
            elif self.isLocal():
                name = f'\1LocalPlayer\1{name}\2'
            else:
                name = f'\1OtherPlayer\1{name}\2'

            name += (f'\n\1TextShadow\1{self.getToonTag()}\2')
        else:
            if self.hasLocalNametag():
                name = f'\1LocalPlayer\1{name}\2'
            elif self.playerType == NametagGroup.CCSuit:
                name = f'\1CogGray\1{name}\2'
            else:
                name = f'\1OtherPlayer\1{name}\2'

        self.notify.debug(f"nametag name: {name}")

        # Now, set a tag name for underneath.
        name += self.makeClubTag()

        self.nametag.setDisplayName(name)

    def makeClubTag(self) -> str:
        if not self.clubName:
            return ''
        clubItem = ClubItemIndex.getItem(self.clubColor)
        if clubItem is None:
            return ''
        clubColor = clubItem.getValue()
        if not clubColor.canUpdate():
            # Simple nametag color.
            return f'\n\1TextShrink\1\1TextOnlyShadow\1\1ClubColor-{self.clubColor}\1{self.clubName}\2\2\2'
        else:
            # Gradient nametag color.
            formattedClubName = ''
            for index, letter in enumerate(self.clubName):
                if letter == ' ':
                    # Since it is a space, we don't need a TPM for it.
                    formattedClubName += letter
                    continue

                # For each letter, we need to get the color that associates with
                # a certain part of the TextProperty of this club color.
                letterPercent = (index / (len(self.clubName) - 1))
                colorIndex = round(letterPercent * (ClubMaxNameLength - 1))
                formattedClubName += f'\1ClubColor-{self.clubColor}-{colorIndex}\1{letter}\2'

            # Return our formatted club name.
            return f'\n\1TextShrink\1\1TextOnlyShadow\1{formattedClubName}\2\2'

    def setAnimalEffect(self, effect):
        self.changeAnimalEffect(effect)
        self.animalEffect = effect

    def getAnimalEffect(self):
        return self.animalEffect

    def setCheesyEffect(self, effect):
        self.savedCheesyEffect = effect

        if self.activeState == ESGenerated:
            self.reconsiderCheesyEffect(lerpTime = 0.5)
        else:
            self.reconsiderCheesyEffect()

    def reconsiderCheesyEffect(self, lerpTime = 0):
        try:
            effect = self.savedCheesyEffect
        except AttributeError:
            # an NPC is probably trying to reconsider its cheesy effect... get outta here
            return
        if not base.cr.areCheesyEffectsAllowed():
            sizeEffects = (CheesyEffectItemType.BigLegs,
                           CheesyEffectItemType.SmallLegs,
                           CheesyEffectItemType.BigToon,
                           CheesyEffectItemType.SmallToon,
                           CheesyEffectItemType.BigWhite,
                           CheesyEffectItemType.Fired,
                           CheesyEffectItemType.Stomped,
                           CheesyEffectItemType.Backwards,
                           )
            if effect in sizeEffects:
                effect = ToontownGlobals.CENormal

        if self.ghostMode:
            self.hideNametag2d()
            self.hideNametag3d()
            effect = ToontownGlobals.CEGhost

        self.applyCheesyEffect(effect, lerpTime = lerpTime)

    """
    Chat
    These functions are here so NPCs can show things like stickers etc.
    """

    def receiveChatMessage(self, channelId: int, modifier: int, contentTypeId: int, content: str):
        """Forwards a chat message to the ChatManager"""
        if not base.localAvatar.isToonIgnored(self.doId):
            base.cr.chatManager.receiveChatMessage(channelId, modifier, contentTypeId, content, self.getDoId(), self.getName())

    def showTextMessage(self, message: ChatMessage):
        """Displays a text chat message."""
        isThought = ChatZoneModifier(message.modifier) == ChatZoneModifier.Thought
        self.setChatAbsolute(message.content.text, CFThought if isThought else CFTimeout | CFSpeech)

    def showSpeedChatMessage(self, message: ChatMessage):
        """Displays a SpeedChat chat message."""
        isThought = message.modifier == ChatZoneModifier.Thought
        if message.content.primaryId is not None and message.content.text is not None:
            self.setChatAbsolute(message.content.text, CFThought | CFQuicktalker if isThought else CFSpeech | CFQuicktalker | CFTimeout)

        if message.content.type != ChatSpeedChatType.Quest and message.content.secondaryId is not None:
            self.setEmoteState(message.content.secondaryId, animMultiplier=base.localAvatar.animMultiplier)

    def showSticker(self, stickerSubtype: ChatStickersItemType, modifier: Optional[int] = None):
        """
        Plays the sticker sequence

        :param stickerSubtype: The sticker subtype to display.
        :param modifier: The sticker's modifier.
        """
        # If we were already playing a sticker sequence, clean up before continuing.
        self.stopStickerSequence()

        # Get the sequence for this sticker
        stickerDefinition = ItemTypeRegistry.getItemDefinition(stickerSubtype)
        self.stickerSequence = stickerDefinition.getSequence()(render, self, stickerSubtype, modifier)
        self.stickerSequence.startSequence()

    def stopStickerSequence(self):
        """
        Cleans up the sticker animation if it's playing.
        """
        if self.stickerSequence:
            self.stickerSequence.stopSequence()
            self.stickerSequence = None

    def setExperience(self, experience):
        self.experience = Experience.Experience(*experience)
        if self.inventory:
            self.inventory.updateGUI()

    def getExperience(self):
        for gagModifier in self.getModifiersOfType(ModifierType.GagsContentSync):
            if gagModifier.getForceMaxed():
                e = Experience.Experience()
                e.maxOut()
                return e
        return self.experience

    def setInventory(self, inventoryNetString):
        # Create a new inventory if we don't already have one
        if not self.inventory:
            self.inventory = GagInventory.GagInventory(self, inventoryNetString)

        # update the inventory
        self.inventory.updateInvString(inventoryNetString)
        self.inventoryString = inventoryNetString

    def getInventory(self):
        return self.inventoryString

    def setTrackAccess(self, trackArray):
        self.trackArray = trackArray
        if self.inventory:
            self.inventory.updateGUI()

    def getTrackAccess(self):
        for gagModifier in self.getModifiersOfType(ModifierType.GagsContentSync):
            if gagModifier.getForceMaxed():
                return [1 for _ in range(BattleGlobals.NUM_GAG_TRACKS)]
        return self.trackArray

    def hasTrackAccess(self, track):
        """
        Can this toon use this track?

        :return: bool 0/1
        """
        trackArray = self.getTrackAccess()
        if trackArray and track < len(trackArray):
            return trackArray[track]
        else:
            # RAU this case can happen if we are opening the closet of another toon
            return 0

    def setBattleId(self, battleId):
        self.battleId = battleId
        messenger.send('ToonBattleIdUpdate', [self.doId])

    def setMaxCarry(self, maxCarry):
        self.maxCarry = maxCarry
        if self.inventory:
            self.inventory.updateGUI()

    def getMaxCarry(self):
        for gagModifier in self.getModifiersOfType(ModifierType.GagsContentSync):
            if gagModifier.getForceMaxed():
                return 100
        return self.maxCarry

    def setTrackBonusLevel(self, trackBonusLevelArray):
        self.trackBonusLevel = [8 if (trackBonusLevelArray or ([-1] * BattleGlobals.NUM_GAG_TRACKS + 1))[i] >= 1 else -1
                                for i in range(min(len(trackBonusLevelArray), BattleGlobals.NUM_GAG_TRACKS))]
        if self.inventory:
            self.inventory.updateGUI()

    def getTrackBonusLevel(self, track = None):
        for gagModifier in self.getModifiersOfType(ModifierType.GagsContentSync):
            if gagModifier.getForceMaxed():
                return [8 for _ in range(BattleGlobals.NUM_GAG_TRACKS)] if track is None else 1
        return self.trackBonusLevel if track is None else self.trackBonusLevel[track]

    def checkGagBonus(self, track, level):
        return self.getTrackBonusLevel(track) >= 1

    def toonUp(self, hpGained, hasInteractivePropBonus=False, extraText='', force=False):
        if self.hp is None or hpGained < 0:
            return
        oldHp = self.hp
        if self.hp + hpGained <= 0:
            self.hp += hpGained
        else:
            self.hp = min(max(self.hp, 0) + hpGained, self.getMaxHp())

        hpGained = self.hp - max(oldHp, 0)
        if hpGained >= 0:
            self.showHpText(hpGained, hasInteractivePropBonus=hasInteractivePropBonus, extraText=extraText, force=force)
            self.hpChange(quietly=0)

    def takeDamage(self, hpLost, bonus=0, extraText=''):
        if self.hp is None or hpLost < 0:
            return
        oldHp = self.hp
        self.hp = max(self.hp - hpLost, 0)
        # hpLost = oldHp - self.hp  [this check caps the damage to max out at the toon's laff]
        if hpLost > 0:
            self.showHpText(-hpLost, bonus, extraText=extraText)
            self.hpChange(quietly=0)
            self.__considerUpdateMeter()
            if self.hp <= 0 < oldHp:
                self.died()

    def __considerUpdateMeter(self):
        try:
            if not self.overheadMeter:
                self.overheadMeter = OldLaffMeter(self.style, self.hp, self.getMaxHp(), isOverhead = True)
                self.overheadMeter.setAvatar(self)
                self.overheadMeter.setZ(6.15)
                self.overheadMeter.setScale(1.5)
                self.overheadMeter.reparentTo(NodePath(self.nametag.getNameIcon()))
                # self.overheadMeter.hide(BitMask32.bit(1)) # Hide from 2D camera.
                self.overheadMeter.start()
                self.overheadMeter.show()
        except:
            pass

    def showHpText(self, number, bonus=0, scale=1, hasInteractivePropBonus=False, extraText='', force=False, fromVisual=False):
        if not fromVisual:
            hpTextOverride = self.getHpTextOverride(number, bonus=bonus, scale=scale,
                                                    hasInteractivePropBonus=hasInteractivePropBonus, extraText=extraText,
                                                    force=force)
            if hpTextOverride:
                # This means that a visual effect is overriding our hp text. Let's just let that handle it instead.
                return

        if self.HpTextEnabled and not self.ghostMode:
            if number != 0 or force:
                if self.hpText:
                    self.hideHpText()
                self.HpTextGenerator.setFont(ToontownGlobals.getSignFont())
                if number < 0:
                    self.HpTextGenerator.setText(str(number))
                else:
                    hpGainedStr = '+' + str(number)
                    if hasInteractivePropBonus:
                        hpGainedStr += '\n' + TTLocalizer.InteractivePropTrackBonusTerms[0]
                    self.HpTextGenerator.setText(hpGainedStr)
                if extraText:
                    self.HpTextGenerator.setText(self.HpTextGenerator.getText() + f'\n{extraText}')
                self.HpTextGenerator.clearShadow()
                self.HpTextGenerator.setAlign(TextNode.ACenter)
                if bonus == 1:
                    r = 1.0
                    g = 1.0
                    b = 0
                    a = 1
                elif bonus == 2:
                    r = 1.0
                    g = 0.5
                    b = 0
                    a = 1
                elif number < 0:
                    r = 0.9
                    g = 0
                    b = 0
                    a = 1
                else:
                    r = 0
                    g = 0.9
                    b = 0
                    a = 1
                self.HpTextGenerator.setTextColor(r, g, b, a)
                self.hpTextNode = self.HpTextGenerator.generate()
                self.hpText = self.attachNewNode(self.hpTextNode)
                self.hpText.setScale(scale)
                self.hpText.setColorScaleOff(1)
                self.hpText.setBillboardPointEye()
                self.hpText.setBin('fixed', 100)
                self.hpText.setPos(0, 0, self.height / 2)

                def setAlphaScale(value):
                    if self.hpText:
                        self.hpText.setAlphaScale(value)

                self.hpTextInterval = Sequence(
                    self.hpText.posInterval(1.0, Point3(0, 0, self.height + 1.5), blendType = 'easeOut'),
                    Wait(0.85),
                    LerpFunctionInterval(setAlphaScale, 0.5, fromData=1.0, toData=0.0),
                    Func(self.hideHpText)
                )
                self.hpTextInterval.start()

    def setEquippedItems(self, equippedItems):
        if not equippedItems:
            self.equippedItems = []
        elif isinstance(equippedItems[0], InventoryItem):
            self.equippedItems = equippedItems
        else:
            self.equippedItems = InventoryItem.fromStructList(equippedItems)
        messenger.send(f'EquippedInventorySet-{self.doId}')
        self.handlePostEquippedItemsSet()

    def getEquippedItems(self):
        return self.equippedItems

    def getEquippedItemsOfType(self, itemType: ItemType):
        equippedItems = self.getEquippedItems()
        equippedOfType = InventoryItem.findItemTypesFromItemList(itemType, equippedItems)

        return equippedOfType

    def handlePostEquippedItemsSet(self):
        # Fill in with items and other attributes that need to be updated once the avatar
        # receives a new set of equipped items.
        # Update nametag font
        self.setDisplayName(self.getName())

        # Update Cheesy Effect
        equippedCheesyEffects: list[InventoryItem] = self.getEquippedItemsOfType(ItemType.Social_CheesyEffect)
        equippedCheesyEffect = equippedCheesyEffects[0].getItemSubtype() if equippedCheesyEffects else 0
        self.setCheesyEffect(equippedCheesyEffect)

        # Update shirt and shorts.
        # Set shorts first since it may re-build the model
        equippedClothingBottoms: list[InventoryItem] = self.getEquippedItemsOfType(ItemType.Cosmetic_Clothing_Bottom)
        equippedClothingBottom = equippedClothingBottoms[0] if equippedClothingBottoms else InventoryItem.fromSubtype(ClothingBottomItemType.ShortswithBelt)

        equippedClothingTops: list[InventoryItem] = self.getEquippedItemsOfType(ItemType.Cosmetic_Clothing_Top)
        equippedClothingTop = equippedClothingTops[0] if equippedClothingTops else InventoryItem.fromSubtype(ClothingTopItemType.Shirt_Desat_Classic_Plain)

        # Populate accessories.
        accessoryTypes = [
            ItemType.Cosmetic_Hat,
            ItemType.Cosmetic_Glasses,
            ItemType.Cosmetic_Backpack,
            ItemType.Cosmetic_Shoes,
            ItemType.Cosmetic_Neck,
        ]
        equippedAccessories = [
            item
            for itemType in accessoryTypes
            for item in self.getEquippedItemsOfType(itemType)
        ]

        # Now set equipped items.
        self.setToonEquippedItems([equippedClothingBottom, equippedClothingTop] + equippedAccessories)
