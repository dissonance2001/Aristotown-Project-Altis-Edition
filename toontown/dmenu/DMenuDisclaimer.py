from direct.gui.DirectGui import OnscreenText, DirectButton
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject
from toontown.toonbase import ToontownGlobals

class DMenuDisclaimer(DirectObject):
    notify = directNotify.newCategory('DisclaimerScreen')
    
    def __init__(self):
        DirectObject.__init__(self)
        base.setBackgroundColor(0, 0, 0)
        disclaimerText = "Aristotown: Altis Edition is fanmade version of Project Altis, made to mimic the feel of Toontown: Corporate Clash. This source is not in any way, shape or form affiliated with Toontown: Corporate Clash or it's team. ANY REPRODUCTION OR REDISTRIBUTION OF THIS SOURCE INCLUDING SHARING SCREENSHOTS/VIDEOS IS PROHIBITED W/O CONSENT FROM DISSONANCE! This source was meant to be shared with close friends, as well as to serve as a learning project for myself. If you have any questions, please DM Dissonance2020 on Discord. Please click the checkmark to obtain access to the rest of the game."
        self.disclaimer = OnscreenText(text = disclaimerText, font = ToontownGlobals.getMinnieFont(), style = 3, wordwrap = 40, scale = .07, pos = (0, .6, 0))
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui.bam')
        yesUp = gui.find('**/tt_t_gui_mat_okUp')
        yesDown = gui.find('**/tt_t_gui_mat_okDown')
        noUp = gui.find('**/tt_t_gui_mat_closeUp')
        noDown = gui.find('**/tt_t_gui_mat_closeDown')
        
        self.accept = DirectButton(parent = aspect2d, relief = None, image = (yesUp, yesDown, yesUp), image_scale = (0.6, 0.6, 0.6), image1_scale = (0.7, 0.7, 0.7), image2_scale = (0.7, 0.7, 0.7), text = ('', 'I Agree', 'I Agree'), text_pos=(0, -0.175), text_style = 3, text_scale=0.08, pos = (.4, 0, -.5), command = self.accept)
        
        self.deny = DirectButton(parent = aspect2d, relief = None, image = (noUp, noDown, noUp), image_scale = (0.6, 0.6, 0.6), image1_scale = (0.7, 0.7, 0.7), image2_scale = (0.7, 0.7, 0.7), text = ('', 'You better not click this button', 'You better not click this button'), text_pos=(0, -0.175), text_style = 3, text_scale=0.08, pos = (-.4, 0, -.5), command = self.deny)
        
    def accept(self):
        self.accept.destroy()
        self.deny.destroy()
        self.disclaimer.removeNode()
        base.cr.hasAccepted = True
        messenger.send("AgreeToGame")
        
    def deny(self):
        base.exitFunc()