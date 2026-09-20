from direct.fsm import StateData

from toontown.clashbattle.battle.statuses import SEE
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class TownBattleAttackPanel(StateData.StateData):
    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)

    def load(self):
        StateData.StateData.load(self)

    def unload(self):
        StateData.StateData.unload(self)

    def enter(self):
        StateData.StateData.enter(self)
        base.localAvatar.inventory.show()
        self.accept('inventory-selection', self.__handleInventory, [False])
        self.accept('inventory-selection-alt', self.__handleInventory, [True])
        self.accept('inventory-run', self.__handleRun)
        self.accept('inventory-surrender', self.__handleSurrender)
        self.accept('inventory-sos', self.__handleSOS)
        self.accept('inventory-pass', self.__handlePass, [False])
        self.accept('inventory-pass-alt', self.__handlePass, [True])
        self.accept('inventory-fire', self.__handleFire, [False])
        self.accept('inventory-fire-alt', self.__handleFire, [True])
        self.accept('inventory-sue', self.__handleSue, [False])
        self.accept('inventory-sue-alt', self.__handleSue, [True])
        self.accept('inventory-counterfeit', self.__handleCounterfeit, [False])
        self.accept('inventory-counterfeit-alt', self.__handleCounterfeit, [True])

    def exit(self):
        StateData.StateData.exit(self)
        self.ignore('inventory-selection')
        self.ignore('inventory-selection-alt')
        self.ignore('inventory-run')
        self.ignore('inventory-surrender')
        self.ignore('inventory-sos')
        self.ignore('inventory-sos-alt')
        self.ignore('inventory-pass')
        self.ignore('inventory-pass-alt')
        self.ignore('inventory-fire')
        self.ignore('inventory-fire-alt')
        self.ignore('inventory-sue')
        self.ignore('inventory-sue-alt')
        self.ignore('inventory-counterfeit')
        self.ignore('inventory-counterfeit-alt')
        base.localAvatar.inventory.hide()

    def __handleRun(self):
        doneStatus = {'mode': 'Run'}
        messenger.send(self.doneEvent, [doneStatus])

    def __handleSOS(self):
        doneStatus = {'mode': 'SOS'}
        messenger.send(self.doneEvent, [doneStatus])

    def __handleSurrender(self):
        doneStatus = {'mode': 'Surrender'}
        messenger.send(self.doneEvent, [doneStatus])

    def __handlePass(self, lockIn):
        doneStatus = {'mode': 'Pass', 'lockIn': lockIn}
        messenger.send(self.doneEvent, [doneStatus])

    def __handleFire(self, lockIn):
        doneStatus = {'mode': 'Fire', 'lockIn': lockIn}
        messenger.send(self.doneEvent, [doneStatus])

    def __handleSue(self, lockIn):
        doneStatus = {'mode': 'Sue', 'lockIn': lockIn}
        messenger.send(self.doneEvent, [doneStatus])

    def __handleCounterfeit(self, lockIn):
        doneStatus = {'mode': 'Counterfeit', 'lockIn': lockIn}
        messenger.send(self.doneEvent, [doneStatus])

    def __handleInventory(self, lockIn, track, level):
        numItem = base.localAvatar.inventory.numItem(track, level)
        counterfeit = base.localAvatar.getStatusEffectOfId(SEE.EFFECT_COUNTERFEIT_CONTAINER)
        if counterfeit:
            numItem += counterfeit.getGagTrackLevel(track, level)
        if numItem > 0:
            doneStatus = {
                'mode': 'Inventory',
                'lockIn': lockIn,
                'track': track,
                'level': level,
            }
            messenger.send(self.doneEvent, [doneStatus])
        else:
            self.notify.warning("An item we don't have: track %(track)s level %(level)s was selected." % {'track': track, 'level': level})
