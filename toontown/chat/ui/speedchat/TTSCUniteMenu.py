from panda3d.core import Vec3

from toontown.battle import BattleGlobals
from toontown.chat.ui.speedchat.SCMenu import SCMenu
from toontown.chat.ui.speedchat.SCMenuHolder import SCMenuHolder
from toontown.chat.ui.speedchat.SpeedChat import SpeedChat
from toontown.inventory.base.InventoryDelta import InventoryDelta
from toontown.inventory.enums.ItemEnums import ItemType
from .TTSCUniteTerminal import TTSCUniteTerminal


class TTSCUniteMenu(SpeedChat):

    def __init__(self, name, backgroundModelName=None, guiModelName=None):
        SpeedChat.__init__(self, name, None, backgroundModelName, guiModelName)
        self.accept(InventoryDelta.getItemDeltaEvent(ItemType.Unite), lambda _ : self.__unitesChanged())
        self.chatWindowOpen = False

    def destroy(self):
        self.ignore(InventoryDelta.getItemDeltaEvent(ItemType.Unite))
        SpeedChat.destroy(self)

    def clearMenu(self):
        SpeedChat.clearMenu(self)

    def setChatWindowOpen(self, chatWindowOpen):
        self.chatWindowOpen = chatWindowOpen

    def getPosOffset(self):
        # For positioned GUI
        # Move it back a bit if the chat window's open
        xVal = 0.1675 if self.chatWindowOpen else 0.275
        return Vec3(xVal * base.settings['chat-scale'], 0, -0.03)

    def __unitesChanged(self):
        self.clearMenu()
        if not hasattr(base, "localAvatar"):
            return

        for item in base.localAvatar.getUnites():
            if item.getQuantity() > 0:
                self.append(TTSCUniteTerminal(item))
