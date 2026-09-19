import random

from direct.distributed.DistributedObject import DistributedObject

from toontown.battle.gui.MrDiceChoice import MrDiceChoice

from typing import List

from toontown.chat.constants import ChatEvents
from toontown.inventory.enums.ItemEnums import UniteItemType
from toontown.inventory.registry.UniteRegistry import UniteRegistry
from toontown.instances import HighRollerGlobals


class DistributedDiceChoice(DistributedObject):

    def __init__(self, cr):
        super().__init__(cr)

        # Create Mr. Dice Choice.
        townBattle = base.cr.playGame.getPlace().townBattle
        inventory = base.localAvatar.inventory
        self.mrDiceChoice = MrDiceChoice(townBattle=townBattle, inventory=inventory)

        # Listen to events.
        self.accept('dice-selection', self.selectDice)

    def delete(self):
        super().delete()
        self.ignoreAll()
        self.mrDiceChoice.destroy()

    """
    Senders
    """

    def selectDice(self, pip):
        self.sendUpdate('receivePipChoice', [pip])

    """
    Receivers
    """

    def closeChoices(self):
        if hasattr(base.localAvatar, 'forceShowDiscountLolz'):
            delattr(base.localAvatar, 'forceShowDiscountLolz')
        self.mrDiceChoice.disableChoice()

    def sendPipFields(self, pips: List[int], ownedPips: int):
        self.mrDiceChoice.enableChoice(pips=pips, ownedPips=ownedPips)

    def callbackPipChoice(self, avId: int, pip: int, remainingPips: int, phrase: str):
        """
        Someone's pip choice was a success.
        """
        av = base.cr.doId2do.get(avId)
        if av:
            from toontown.chat.constants.ChatGlobals import  CFSpeech, CFTimeout, CFQuicktalker
            av.setChatAbsolute(phrase, CFSpeech | CFQuicktalker | CFTimeout)
            messenger.send(ChatEvents.Store_LogZoneMessage, [av, phrase])

            if pip == 5:
                townBattle = base.cr.playGame.getPlace().townBattle
                avIds = [toon.doId for toon in townBattle.toons if toon]
                UniteRegistry.get(UniteItemType.ToonUpMid).doEffect(av, avIds)

        if avId == base.localAvatar.doId:
            if pip == 2:
                # hack
                setattr(base.localAvatar, 'forceShowDiscountLolz', 2)
            base.localAvatar.inventory.updateGUI()
            self.mrDiceChoice.disablePip(pip + 1, remainingPips)

            # Pull back attack if necessary.
            townBattle = base.cr.playGame.getPlace().townBattle
            if townBattle and HighRollerGlobals.getPipCost(base.localAvatar, townBattle.track, townBattle.level) >= remainingPips:
                # Pull back!!
                townBattle.waitPanel.requestBack()
