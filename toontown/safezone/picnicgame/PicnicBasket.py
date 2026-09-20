from direct.fsm.FSM import FSM
from direct.fsm.StateData import StateData
from direct.gui.DirectGui import DirectButton
from direct.showbase.MessengerGlobal import messenger

from toontown.gui import TTDialog
from toontown.toonbase import TTLocalizer


class PicnicBasket(StateData, FSM):

    def __init__(self, doneEvent, tableName, seatNumber):
        StateData.__init__(self, doneEvent)
        FSM.__init__(self, "PicnicBasket")
        self.tableName = tableName
        self.seatNumber = seatNumber
        self.accept("RequestTableExit", self.request, extraArgs=["RequestExit"])
        self.accept("ExitTableDone", self.handleTableDone)

    def load(self):
        self.gui = base.loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')

    def unload(self):
        FSM.cleanup(self)
        self.gui.removeNode()
        del self.gui

    def enter(self):
        if base.localAvatar.getHp() > 0:
            # let the distributed picnic basket know it is ok for us to enter the basket
            messenger.send(f'enter{self.tableName}-{self.seatNumber}_OK')
            self.request('Boarded')
        else:
            self.request('TrolleyHFA')

    def exit(self):
        self.ignoreAll()
    
    def enterBoarded(self):
        self.accept("enableExitButton", self.enableExitButton)

    def exitBoarded(self):
        self.ignore("enableExitButton")
        self.disableExitButton()

    def enterTrolleyHFA(self):
        self.noTrolleyBox = TTDialog.TTGlobalDialog(
            message = TTLocalizer.PicnicBasketHFAMessage,
            doneEvent = 'noTrolleyAck',
            style = TTDialog.Acknowledge
        )
        self.noTrolleyBox.show()
        base.localAvatar.b_setAnimState('Neutral', 1)
        self.accept('noTrolleyAck', self.__handleNoTrolleyAck)

    def exitTrolleyHFA(self):
        self.ignore('noTrolleyAck')
        self.noTrolleyBox.cleanup()
        del self.noTrolleyBox

    def __handleNoTrolleyAck(self):
        ntbDoneStatus = self.noTrolleyBox.doneStatus
        if ntbDoneStatus == 'ok':
            doneStatus = {'mode': 'reject'}
            messenger.send(self.doneEvent, [doneStatus])
        else:
            self.notify.error('Unrecognized doneStatus: ' + str(ntbDoneStatus))

    def enableExitButton(self):
        self.exitButton = DirectButton(
            parent = base.a2dBottomRight, relief = None, scale = 2.0,
            image = (
                self.gui.find('**/CloseBtn_UP'),
                self.gui.find('**/CloseBtn_DN'),
                self.gui.find('**/CloseBtn_Rllvr'),
                self.gui.find('**/CloseBtn_UP')
            ),
            pos = (-0.17, 0, 0.1),
            command = lambda: messenger.send("RequestTableExit"),
        )

    def disableExitButton(self):
        if getattr(self, "exitButton", None):
            self.exitButton.destroy()
            del self.exitButton

    def enterRequestExit(self):
        messenger.send('TableExit')
    
    def handleTableDone(self):
        doneStatus = {'mode': 'exit'}
        messenger.send(self.doneEvent, [doneStatus])
    
    def handleRejectBoard(self):
        doneStatus = {'mode': 'reject'}
        messenger.send(self.doneEvent, [doneStatus])
