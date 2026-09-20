from direct.gui.DirectGui import *

from toontown.chat.ui.speedchat.SCTerminal import SCTerminal
from toontown.inventory.base.InventoryDelta import InventoryDelta
from toontown.inventory.enums.ItemEnums import ItemType
from toontown.inventory.registry.UniteRegistry import UniteItemDefinition

TTSCUniteMsgEvent = 'TTSCUniteMsg'
TTSCUniteStateChangedEvent = 'TTSCUniteStateChanged'

class TTSCUniteTerminal(SCTerminal):

    def __init__(self, item: UniteItemDefinition):
        SCTerminal.__init__(self)
        self.setCharges(item.getQuantity())
        self.item = item
        self.text = item.getItemDefinition().getName()
        self.accept(TTSCUniteStateChangedEvent, self.checkEnableUniteChat)
        self.accept(InventoryDelta.getItemDeltaEvent(ItemType.Unite), lambda _ : self.checkEnableUniteChat(), extraArgs=[123])
        self.needToBecomeUsable = False

    def isWhisperable(self):
        return False

    def isDisabled(self):
        # If we have either of our cooldowns active, we are disabled.
        if base.localAvatar.unitesDisabled['realtime'] or base.localAvatar.unitesDisabled['battle']:
            return True
        return SCTerminal.isDisabled(self)

    def checkEnableUniteChat(self):
        # If we have either of our cooldowns active, we don't need to re-enable the unite phrases.
        if base.localAvatar.unitesDisabled['realtime'] or base.localAvatar.unitesDisabled['battle']:
            return

        if not (hasattr(self, 'button') and self.button):
            self.needToBecomeUsable = True
            return

        self.enableUniteChat()

    def enableUniteChat(self):
        btn = self.button
        rolloverColor = self.getColorScheme().getRolloverColor() + (1,)
        pressedColor = self.getColorScheme().getPressedColor() + (1,)
        btn.frameStyle[DGG.BUTTON_ROLLOVER_STATE].setColor(*rolloverColor)
        btn.frameStyle[DGG.BUTTON_DEPRESSED_STATE].setColor(*pressedColor)
        btn.updateFrameStyle()
        btn['text_fg'] = self.getColorScheme().getTextColor() + (1,)
        btn['rolloverSound'] = DGG.getDefaultRolloverSound()
        btn['clickSound'] = DGG.getDefaultClickSound()

    def enterActive(self):
        SCTerminal.enterActive(self)
        if self.needToBecomeUsable:
            self.enableUniteChat()
            self.needToBecomeUsable = False

    def destroy(self):
        self.ignore(TTSCUniteStateChangedEvent)
        SCTerminal.destroy(self)

    def handleSelect(self):
        SCTerminal.handleSelect(self)
        messenger.send(self.getEventName(TTSCUniteMsgEvent), [self.item])

    def handleThreeSelect(self):
        self.handleSelect()  # Default to handleSelect(). DO NOT let unites be thought bubbles.
