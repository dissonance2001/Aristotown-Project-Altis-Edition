from panda3d.core import Fog

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectRadioButton import DirectRadioButton
from direct.gui.OnscreenText import OnscreenText

from toontown.shader.FogManager import FogManager
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from typing import Optional


@DirectNotifyCategory()
class FogDebugUtil(DirectFrame):
    def __init__(self, parent, pos = (-1.4, -0.20),  fogName = "ActiveFog", rgb = (1, 1, 1), fogOverride: Optional[FogManager] = None):
        self._parent = parent
        DirectFrame.__init__(
            self, parent = self._parent,
            relief = None,
            scale = 1.0
        )

        self.fogName = fogName  # To give a friendly name, just in case we have multiple utils on screen.

        self.fogMode = [0]  # default we will use Exponential

        self.colorR, self.colorG, self.colorB = rgb

        self.expDensity = 0.5
        self.linRange_Onset = 0.5
        self.linRange_Opacity = 0.5
        base.setSceneGraphAnalyzerMeter(False)

        self.buttonSpacing = 0.1
        # self.buttonbase_xcoord = -1.4

        if fogOverride is None:
            self.fog = FogManager(name=fogName)
            self.fog.setFog(parent)
        else:
            self.fog = fogOverride
            self.colorR, self.colorG, self.colorB, _ = fogOverride.getColor()
            self.expDensity = fogOverride.getDensity()
            self.linRange_Onset = fogOverride.getLinearOnset().length()
            self.linRange_Opacity = fogOverride.getLinearOpacity().length()
            self.fogMode = [fogOverride.getFogMode()]

        # Dictates the positioning of the menu
        # Can eventually set preset locations for feasibility
        self.buttonbase_xcoord, self.buttonbase_ycoord = pos

        self.buttonList = []
        self.buttonExpDensity = None
        self.loadFogModifiers()

        self.loadGUI()
        self.addAuxButtons()

    def loadGUI(self):
        self.buttonColorR = DirectSlider(
            value = self.colorR,
            pos = (self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.buttonSpacing * 3),
            range = (0, 1), scale = 0.4,
            frameSize = (-0.5, 0.5, -0.08, 0.08),
            command = self.changeColorValue,
            text = "R", text_scale = 0.15,
            text_pos = (0.6, -0.025),
        )

        self.buttonColorG = DirectSlider(
            value = self.colorG,
            pos = (self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.buttonSpacing * 4),
            range = (0, 1), scale = 0.4,
            frameSize = (-0.5, 0.5, -0.08, 0.08),
            command = self.changeColorValue,
            text = "G", text_scale = 0.15,
            text_pos = (0.6, -0.05),
        )

        self.buttonColorB = DirectSlider(
            value = self.colorB,
            pos = (self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.buttonSpacing * 5),
            range = (0, 1), scale = 0.4,
            frameSize = (-0.5, 0.5, -0.08, 0.08),
            command = self.changeColorValue,
            text = "B", text_scale = 0.15,
            text_pos = (0.6, -0.025),
        )

        self.buttonColorMode = [
            DirectRadioButton(
                text = 'Linear Fog',
                variable = self.fogMode,
                value = [2],
                scale = 0.05,
                pos = (self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.buttonSpacing * -2),
                command = self.addAuxButtons
            ),
            DirectRadioButton(
                text = 'Exponential Fog (Squared)',
                variable = self.fogMode, value = [1],
                scale = 0.05,
                pos = (self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.buttonSpacing * -3),
                command = self.addAuxButtons),
            DirectRadioButton(
                text = 'Exponential Fog',
                variable = self.fogMode,
                value = [0],
                scale = 0.05,
                pos = (self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.buttonSpacing * -4),
                command = self.addAuxButtons
            )
        ]
        for button in self.buttonColorMode:
            button.setOthers(self.buttonColorMode)

        self.buttonPrint = DirectButton(
            pos = (self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.buttonSpacing * -0.5),
            text = "Print",
            scale = 0.075,
            command = self.printFog
        )

        self.textFogName = OnscreenText(
            pos = (self.buttonbase_xcoord + 0.1,  self.buttonbase_ycoord - self.buttonSpacing * -5),
            text = self.fogName,
            scale = 0.075,
        )

    def loadFogModifiers(self):
        self.buttonExpDensity = DirectSlider(
            value = self.expDensity,
            pos = (self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.buttonSpacing * 1),
            range = (0, 0.01), scale = 0.4,
            frameSize = (-0.5, 0.5, -0.08, 0.08),
            command = self.changeDensity,
            text = "Density", text_scale = 0.15,
            text_pos = (0.9, -0.025),
        )
        self.buttonExpDensity.hide()

        self.buttonLinearRange_Onset = DirectSlider(
            value = self.linRange_Onset,
            pos = (self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.buttonSpacing * 1),
            range = (-1000, 1000), scale = 0.4,
            frameSize = (-0.5, 0.5, -0.08, 0.08),
            command = self.setLinearRange,
            text = "Onset", text_scale = 0.15,
            text_pos = (0.9, -0.025),
        )
        self.buttonLinearRange_Onset.hide()

        self.buttonLinearRange_Opacity = DirectSlider(
            value = self.linRange_Opacity,
            pos = (self.buttonbase_xcoord + 0.1, 0.0, self.buttonbase_ycoord - self.buttonSpacing * 2),
            range = (-1000, 1000), scale = 0.4,
            frameSize = (-0.5, 0.5, -0.08, 0.08),
            command = self.setLinearRange,
            text = "Opacity", text_scale = 0.15,
            text_pos = (0.9, -0.025),
        )
        self.buttonLinearRange_Opacity.hide()

    def addAuxButtons(self):
        self.removeAuxButtons()

        # Weird hack, too lazy to use brain
        if self.fog.getFogMode() == 0:
            self.buttonLinearRange_Onset.hide()
            self.buttonLinearRange_Opacity.hide()

        self.fog.setFogMode(self.fogMode[0])

        if self.fogMode[0] == 0 or self.fogMode[0] == 1:  # Exponential
            self.buttonExpDensity.show()
            self.buttonList.append(self.buttonExpDensity)
        else:
            self.buttonLinearRange_Onset.show()
            self.buttonLinearRange_Opacity.show()
            self.buttonList.append(self.buttonLinearRange_Onset)
            self.buttonList.append(self.buttonLinearRange_Opacity)

    def removeAuxButtons(self):
        for btn in self.buttonList:
            btn.hide()
            self.buttonList.remove(btn)

    def changeDensity(self):
        self.expDensity = self.buttonExpDensity['value']
        self.fog.setDensity(self.expDensity)

    def setLinearRange(self):
        self.linRange_Onset = self.buttonLinearRange_Onset['value']
        self.linRange_Opacity = self.buttonLinearRange_Opacity['value']
        self.notify.debug("linrange: ({}, {})".format(self.linRange_Onset, self.linRange_Opacity))
        self.fog.setLinearRange(self.linRange_Onset, self.linRange_Opacity)

    def forceLinearRange(self, onset, opacity):
        self.linRange_Onset = self.buttonLinearRange_Onset['value'] = onset
        self.linRange_Opacity = self.buttonLinearRange_Opacity['value'] = opacity
        self.notify.debug("linrange: ({}, {})".format(self.linRange_Onset, self.linRange_Opacity))
        self.fog.setLinearRange(self.linRange_Onset, self.linRange_Opacity)

    def changeColorValue(self):
        self.colorR = self.buttonColorR['value']
        self.colorG = self.buttonColorG['value']
        self.colorB = self.buttonColorB['value']
        self.buttonColorR['text_fg'] = (self.colorR, 0.0, 0.0, 1.0)
        self.buttonColorG['text_fg'] = (0.0, self.colorG, 0.0, 1.0)
        self.buttonColorB['text_fg'] = (0.0, 0.0, self.colorB, 1.0)
        self.buttonPrint['text_bg'] = (self.colorR, self.colorG, self.colorB, 1.0)
        self.fog.setColor(self.colorR, self.colorG, self.colorB)

    def forceColorValue(self, r, g, b):
        self.colorR = self.buttonColorR['value'] = r
        self.colorG = self.buttonColorG['value'] = g
        self.colorB = self.buttonColorB['value'] = b
        self.fog.setColor(self.colorR, self.colorG, self.colorB)

    def getFog(self):
        return self.fog

    def printFog(self):
        # type = self.fog.fogTypes[self.fogMode]
        print(
            f"RGB = {self.colorR, self.colorG, self.colorB}\nexpDensity = {self.expDensity}\nlinRange_Onset = "
            f"{self.linRange_Onset}\nlinRange_Opacity = {self.linRange_Opacity}\nFog Mode: {self.fogMode}")


######

"""
base.render.clearFog()
from toontown.shader import FogDebugUtil
fdu = FogDebugUtil.FogDebugUtil(base.render)
"""

"""
fdu.getFog().setFog(base.render)

# Ring Game Fog (Debug)
#WATER_COLOR = Vec4(0, 0, 0.6)
FAR_PLANE_DIST = 150
fog = fdu.getFog()
fdu.forceColorValue(0, 0, 0.6)
fdu.forceLinearRange(0.1, FAR_PLANE_DIST - 1.0)
#fog.setLinearRange(0.1, FAR_PLANE_DIST - 1.0)

###### Dreamland Fog
sky = base.render.find('**/Sky')
fog = fdu.getFog()
fdu.forceColorValue(.55, .55, .65)
fdu.forceLinearRange(0.0, 800.0)
render.clearFog()
render.setFog(fog.fog)
sky.clearFog()
sky.setFog(fog.fog)
"""
