"""
from direct.directnotify import DirectNotifyGlobal
from direct.gui.DirectGui import *
from panda3d.core import *
from toontown.menu.MainMenuGui import MainMenuButton
from toontown.utils.text import getTextScaleAfterLength

# Page Vars
itemFrameXorigin = -0.237
itemFrameZorigin = 0.365
buttonXstart = itemFrameXorigin + 0.293
listXorigin = -0.02
listFrameSizeX = 0.67
listZorigin = -0.96
listFrameSizeZ = 1.04
title_text_scale = 0.12
arrowButtonScale = 1.3
rightSideItemsX = 0.36
textRolloverColor = Vec4(1, 1, 0, 1)
textDownColor = Vec4(0.5, 0.9, 1, 1)
textDisabledColor = Vec4(0.4, 0.8, 0.4, 1)
"""

from panda3d.core import NodePath
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class ShaderDebugMenu(DirectFrame):
    def __init__(self, parent=None):
        DirectFrame.__init__(self, parent=base.aspect2d, relief=None, pos=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0))

        self.circleModel = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_nameShop')
        self.barTexture = loader.loadTexture('phase_3/maps/slider.png')
        self.textRowHeight = 0.2
        self.buttonbase_xcoord = 1.4
        self.buttonbase_ycoord = 0.45
        self.loadLensDistortionGUI()

    def loadLensDistortionGUI(self):

        base.effectMgr.setLensDistortion(True)

        self.lensDistortion_enabled = False
        self.lensDistortion_barrelFuzzy = False
        self.lensDistortion_barrelDistort = 0.05
        self.lensDistortion_useChromaDistort = True
        self.lensDistortion_chromaDistort = [0.01, -0.005, -0.02]
        self.lensDistortion_numsamples = 16

        self.guiEnabled = None
        self.guiBarrelFuzzy = None
        self.guiBarrelDistort = None
        self.guiChromaDistortR = None
        self.guiChromaDistortG = None
        self.guiChromaDistortB = None
        self.guiNumSamples = None

        #self.guiBarrelDistort = DirectSlider(parent=self, value=self.cartoonSep,
        #                                      pos=(-self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.textRowHeight * 2.5),
        #                                      thumb_relief=None, range=(0, 32), #self.SAMPLES_MAX
        #                                      thumb_geom=self.circleModel.find('**/tt_t_gui_mat_namePanelCircle'),
        #                                      frameTexture=self.barTexture, frameSize=(-0.5, 0.5, -0.08, 0.08),
        #                                      command=self.__changeCartoon)
        #                                      #command=self.__changeAOValue(self.samples, self.radius, self.amount, self.strength))
        #self.guiBarrelDistort.setScale(0.5)
        #self.guiBarrelDistort.setTransparency(True)

        self.guiChromaDistortR = DirectSlider(parent=self, value=self.lensDistortion_chromaDistort[0],
                                              pos=(-self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.textRowHeight * 3.5),
                                              thumb_relief=None, range=(-1, 1),
                                              thumb_geom=self.circleModel.find('**/tt_t_gui_mat_namePanelCircle'),
                                              frameTexture=self.barTexture, frameSize=(-0.5, 0.5, -0.08, 0.08),
                                              command=self.__changeChromaDistort)
        self.guiChromaDistortR.setScale(0.5)
        self.guiChromaDistortR.setTransparency(True)

        self.guiChromaDistortG = DirectSlider(parent=self, value=self.lensDistortion_chromaDistort[1],
                                              pos=(-self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.textRowHeight * 5.5),
                                              thumb_relief=None, range=(-1, 1), #self.SAMPLES_MAX
                                              thumb_geom=self.circleModel.find('**/tt_t_gui_mat_namePanelCircle'),
                                              frameTexture=self.barTexture, frameSize=(-0.5, 0.5, -0.08, 0.08),
                                              command=self.__changeChromaDistort)
        self.guiChromaDistortG.setScale(0.5)
        self.guiChromaDistortG.setTransparency(True)


        self.guiChromaDistortB = DirectSlider(parent=self, value=self.lensDistortion_chromaDistort[2],
                                              pos=(-self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.textRowHeight * 4.5),
                                              thumb_relief=None, range=(-1, 1), #self.SAMPLES_MAX
                                              thumb_geom=self.circleModel.find('**/tt_t_gui_mat_namePanelCircle'),
                                              frameTexture=self.barTexture, frameSize=(-0.5, 0.5, -0.08, 0.08),
                                              command=self.__changeChromaDistort)
        self.guiChromaDistortB.setScale(0.5)
        self.guiChromaDistortB.setTransparency(True)

    def __changeChromaDistort(self):
        r = self.guiChromaDistortR['value']
        self.lensDistortion_chromaDistort[0] = r
        g = self.guiChromaDistortG['value']
        self.lensDistortion_chromaDistort[1] = g
        b = self.guiChromaDistortB['value']
        self.lensDistortion_chromaDistort[2] = b

        base.effectMgr.setChromaDistort(r, g, b) # a doesn't change

    def __changeBarrelDistort(self):
        pass

