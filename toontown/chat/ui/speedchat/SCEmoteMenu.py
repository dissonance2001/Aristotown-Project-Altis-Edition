from copy import deepcopy

from toontown.chat.ui.speedchat.SCEmoteTerminal import SCEmoteTerminal
from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.inventory.base.InventoryDelta import InventoryDelta
from toontown.inventory.enums.ItemEnums import EmoteItemType, ItemType
from toontown.inventory.registry.EmoteRegistry import AllEmotes
from toontown.toonbase import TTLocalizer


class SCEmoteMenu(SCMenu):
    emoteCategories = {
        # TTLocalizer.SCMenuPositive: [
        #
        # ],
        # TTLocalizer.SCMenuNegative: [
        #
        # ],
        None: [
            EmoteItemType.Wave,
            EmoteItemType.Sleepy,
            EmoteItemType.Shrug,
            EmoteItemType.Think,

            EmoteItemType.Applause,
            EmoteItemType.Bow,
            EmoteItemType.Dance,
            EmoteItemType.Delighted,
            EmoteItemType.Happy,
            EmoteItemType.Laugh,
            EmoteItemType.Surprise,

            EmoteItemType.Angry,
            EmoteItemType.BananaPeel,
            EmoteItemType.BellyFlop,
            EmoteItemType.Bored,
            EmoteItemType.Confused,
            EmoteItemType.Cringe,
            EmoteItemType.Cry,
            EmoteItemType.Furious,
            EmoteItemType.Sad,
            EmoteItemType.Taunt,

            EmoteItemType.ResistanceSalute,
            EmoteItemType.Shiver,
            EmoteItemType.Yawn,
            EmoteItemType.Yes,
            EmoteItemType.No,
        ],
    }

    def __init__(self, binLevel=1):
        SCMenu.__init__(self, binLevel=binLevel)
        self.accept(InventoryDelta.getItemDeltaEvent(ItemType.Social_Emote), self.__emoteAccessChanged)
        self.accept('LocalInventorySet', self.__emoteAccessChanged)

    def destroy(self):
        SCMenu.destroy(self)

    def __emoteAccessChanged(self, itemDelta=None):
        self.clearMenu()

        # Empty menu dictionary to start.
        builtCategories = deepcopy(self.emoteCategories)

        # Figure out the categories now.
        equippedItems = [item.getItemSubtype()
                         for item in base.localAvatar.getHammerspace().getEquippedItems(ItemType.Social_Emote)]
        for emoteId in AllEmotes:
            # Revoke access from the relevant categories.
            if emoteId in equippedItems:
                continue

            for category, emoteIndices in builtCategories.items():
                if emoteId in emoteIndices:
                    # We do not have access to this emote. Remove it.
                    emoteIndices.remove(emoteId)
                    break

        # Terminal-ify all that is left.
        for emoteList in builtCategories.values():
            for listIndex, emoteId in enumerate(emoteList):
                emoteList[listIndex] = SCEmoteTerminal(emoteId)

        # Turn build categories into structure.
        structure = []
        for key, emotes in builtCategories.items():
            if key is not None:
                structure.append([key] + emotes)
        structure.extend(builtCategories.get(None, []))

        # Now set up the menu to reflect the changes.
        self.rebuildFromStructure(structure=structure)
