from direct.fsm.StateData import StateData
from direct.fsm.FSM import FSM
from direct.gui.DirectGui import DirectButton
from direct.showbase.MessengerGlobal import messenger

from toontown.toonbase import TTLocalizer
from toontown.gui import TTDialog


class Chair(StateData, FSM):

    def __init__(self, doneEvent, chairName):
        StateData.__init__(self, doneEvent)
        FSM.__init__(self, "Chair")
        self.chairName = chairName
        self.exitButton = None
        self.accept("RequestChairExit", self.request, extraArgs=["RequestExit"])

    def load(self):
        self.gui = base.loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')

    def unload(self):
        self.cleanup()
        self.gui.removeNode()
        del self.gui

    def enter(self):
        if base.localAvatar.getHp() > 0:
            # let the distributed picnic basket know it is ok for us to enter the basket
            messenger.send('enter%s-OK' % self.chairName)
            self.request('Boarded')
        else:
            self.request('HFA')

    def exit(self):
        self.ignoreAll()

    def enterHFA(self):
        self.noTrolleyBox = TTDialog.TTGlobalDialog(
            message=TTLocalizer.ChairHFAMessage,
            doneEvent='noTrolleyAck',
            style=TTDialog.Acknowledge
        )
        self.noTrolleyBox.show()
        base.localAvatar.b_setAnimState('Neutral', 1)
        self.accept('noTrolleyAck', self.__handleNoTrolleyAck)

    def exitHFA(self):
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

    def handleRejectBoard(self):
        doneStatus = {'mode': 'reject'}
        messenger.send(self.doneEvent, [doneStatus])

    def enterBoarded(self):
        self.accept("enableExitButton", self.enableExitButton)

    def exitBoarded(self):
        self.ignore("enableExitButton")
        self.disableExitButton()

    def enableExitButton(self):
        if self.exitButton:
            self.exitButton.destroy()
        self.exitButton = DirectButton(
            parent=base.a2dBottomRight, relief=None, scale=2.0,
            image=(
                self.gui.find('**/CloseBtn_UP'),
                self.gui.find('**/CloseBtn_DN'),
                self.gui.find('**/CloseBtn_Rllvr'),
                self.gui.find('**/CloseBtn_UP')
            ),
            pos=(-0.17, 0, 0.1),
            command=lambda: messenger.send("RequestChairExit"),
        )

    def disableExitButton(self):
        if self.exitButton:
            self.exitButton.destroy()
            self.exitButton = None

    def enterRequestExit(self):
        messenger.send('ChairExit')
        self.accept("ExitChairDone", self.handleChairDone)

    def handleChairDone(self):
        doneStatus = {'mode': 'exit'}
        messenger.send(self.doneEvent, [doneStatus])