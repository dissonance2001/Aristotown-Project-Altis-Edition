from typing import TYPE_CHECKING

from toontown.chat.ui.speedchat.SCCustomTerminal import SCCustomTerminal
from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.inventory.enums.ItemEnums import ItemType, CustomSpeedchatItemType
from toontown.inventory.registry import ItemTypeRegistry
from toontown.toonbase.TTLocalizer import CustomSCStrings

if TYPE_CHECKING:
    from toontown.utils.BuiltinHelper import base


class SCCustomMenu(SCMenu):
    def __init__(self, binLevel=1):
        SCMenu.__init__(self, binLevel=binLevel)

        self.accept(f'EquippedInventorySet-{base.localAvatar.doId}', self.__customMessagesChanged)

    def __customMessagesChanged(self):
        self.clearMenu()

        # Get equipped items.
        ownedPhrases = [item.getItemSubtype() for item in base.localAvatar.getEquippedItemsOfType(ItemType.Social_CustomSpeedchat)]

        for phrase in ownedPhrases:
            if phrase in CustomSCStrings:
                self.append(SCCustomTerminal(phrase))
