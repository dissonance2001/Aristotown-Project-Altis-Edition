from pandac.PandaModules import *
from direct.fsm import StateData
from direct.gui.DirectGui import *
from pandac.PandaModules import *
from toontown.toonbase import TTLocalizer

class TownBattleWaitPanel(StateData.StateData):

    def __init__(self, doneEvent):
        StateData.StateData.__init__(self, doneEvent)

    def load(self):
        gui = loader.loadModel('phase_3.5/models/gui/battlegui/targeting')
        self.frame = DirectFrame(relief=None, image=gui.find('**/targeting_main'), text_align=TextNode.ALeft, pos=(0, 0, 0), scale=0.65)
        self.frame.hide()
        self.backButton = DirectButton(parent=self.frame, relief=None, image=(gui.find('**/back_neutral'), gui.find('**/back_press'), gui.find('**/back_hover')), pos=(-0.847, -0.3, -0.011), scale=.5, text=TTLocalizer.TownBattleWaitBack, text_scale=0.3, text_pos=(0.01, -0.015), text_fg=Vec4(0, 0, 0, 1), command=self.__handleBack)
        gui.removeNode()

    def unload(self):
        self.frame.destroy()
        del self.frame
        del self.backButton

    def enter(self, numParticipants):
        if numParticipants > 1:
            self.frame['text'] = TTLocalizer.TownBattleWaitTitle
            self.frame['text_pos'] = (0, 0.15, 0.5)
            self.frame['text_scale'] = 0.08
        else:
            self.frame['text'] = TTLocalizer.TownSoloBattleWaitTitle
            self.frame['text_pos'] = (0, 0.12, 0.5)
            self.frame['text_scale'] = 0.08
        self.frame.show()

    def exit(self):
        self.frame.hide()

    def __handleBack(self):
        doneStatus = {'mode': 'Back'}
        messenger.send(self.doneEvent, [doneStatus])
