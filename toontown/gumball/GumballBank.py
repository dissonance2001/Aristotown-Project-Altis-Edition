from __future__ import absolute_import
from direct.gui.DirectGui import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import TextNode, Texture, TransparencyAttrib
from toontown.toonbase import ToontownGlobals

class GumballBank(DirectFrame):

    def __init__(self, parent, **kw):
        self.iconModel = None
        image = None
        try:
            image = loader.loadTexture('gui/common/maps/cc_t_gui_icon_gumball_1.png')
            if image:
                image.setMinfilter(Texture.FTLinearMipmapLinear)
                image.setMagfilter(Texture.FTLinear)
        except:
            image = None
        if image is None:
            try:
                self.iconModel = loader.loadModel('phase_3.5/models/gui/gumballmachine/gumball_machine_gui')
                node = self.iconModel.find('**/gumballs')
                if not node.isEmpty():
                    image = node
            except:
                image = None
        DirectFrame.__init__(self, parent=parent, relief=None, image=image, **kw)
        self.initialiseoptions(GumballBank)
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.text = OnscreenText(parent=self, text='0', pos=(0, -0.32928), scale=1.0, fg=(242.0 / 255.0, 136.0 / 255.0, 165.0 / 255.0, 1), shadow=(0, 0, 0, 1), font=ToontownGlobals.getSignFont(), align=TextNode.ACenter, mayChange=1)
        if image is None:
            self['frameSize'] = (-0.36, 0.36, -0.30, 0.30)
            self['frameColor'] = (0.95, 0.53, 0.67, 1)
            self['relief'] = 1
            self.fallbackLetter = OnscreenText(parent=self, text='G', pos=(0, -0.12), scale=1.15, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1), font=ToontownGlobals.getSignFont(), align=TextNode.ACenter)
        else:
            self.fallbackLetter = None
        self.updateGumballs()
        if getattr(base, 'localAvatar', None):
            self.accept(base.localAvatar.uniqueName('gumballsChange'), self.updateGumballs)

    def updateGumballs(self, value=None):
        if value is None:
            av = getattr(base, 'localAvatar', None)
            if not av or not hasattr(av, 'getGumballs'):
                value = 0
            else:
                value = av.getGumballs()
        self.text.setText(str(value))

    def destroy(self):
        self.ignoreAll()
        if self.text:
            self.text.destroy()
            self.text = None
        if self.fallbackLetter:
            self.fallbackLetter.destroy()
            self.fallbackLetter = None
        if self.iconModel:
            self.iconModel.removeNode()
            self.iconModel = None
        DirectFrame.destroy(self)
