import math, colorsys
from direct.gui.DirectGui import *
from panda3d.core import *
from direct.showbase.PythonUtil import bound


class ColorGUI(DirectFrame):

    def __init__(self, parent = aspect2d, **kw):
        DirectFrame.__init__(self, parent, *kw)

        self.hsv = [0, 0, 0]
        self.rgb = (0, 0, 0)

        self.maxDistFromCenter = 2

        self.colorWheel = None
        self.colorWheelOverlay = None
        self.valueBarImage = None
        self.valueBar = None
        self.valueBarOverlay = None
        self.maxDistFromCenter = 2.0

        self.load()

    def load(self):
        gui = loader.loadModel("phase_3/models/gui/mat_colorpicker_gui")
        gui2 = loader.loadModel("phase_3/models/gui/ttcc_colorpicker")

        self.colorWheel = DirectFrame(parent = self, relief = None, image = gui.find("**/colorwheel"),
                                      state = DGG.NORMAL, scale = 1.7)
        self.colorWheel.bind(DGG.B1PRESS, self.beginSelecting)
        self.colorWheel.bind(DGG.B1RELEASE, self.stopSelecting)

        self.colorWheelOverlay = DirectFrame(parent = self, relief = None, image = gui.find("**/colorwheel_overlay"),
                                             scale = 1.7)

        self.valueBarImage = DirectFrame(parent = self, relief = None, image = gui.find("**/color_brightness_bar"),
                                         image_scale = (2, 1, 1), pos = (0, 0, -2), scale = (1, 1, 0.5))

        self.valueBarOverlay = DirectFrame(parent = self, relief = None, pos = (0, 0, -2), scale = (2, 1, 0.5),
                                           image = gui.find("**/color_brightness_overlay"))

        self.valueBar = DirectSlider(parent=self, relief=None,
                                     thumb_image=gui2.find("**/picker"), thumb_relief=None,
                                     thumb_image_scale=(0.35, 0.9, 0.9), thumb_image_pos=(0, 0, 0.4),
                                     pos=(0, 0, -2), scale=(1, 1, 0.5),
                                     command=self.setBrightness, value=85, range=(50, 95))
        gui.removeNode()
        gui2.removeNode()

    def destroy(self):
        self.stopSelecting(0)

        if self.colorWheel:
            self.colorWheel.destroy()

        if self.colorWheelOverlay:
            self.colorWheelOverlay.destroy()

        if self.valueBarImage:
            self.valueBarImage.destroy()

        if self.valueBar:
            self.valueBar.destroy()

        if self.valueBarOverlay:
            self.valueBarOverlay.destroy()

        DirectFrame.destroy(self)

    def beginSelecting(self, event):
        taskMgr.add(self.selectTask, 'ColorWheelSelection')

    def stopSelecting(self, event):
        taskMgr.remove('ColorWheelSelection')

    def selectTask(self, task):
        if base.mouseWatcherNode.hasMouse():
            mx = base.mouseWatcherNode.getMouseX()
            my = base.mouseWatcherNode.getMouseY()
        else:
            return task.done

        wX = self.colorWheel.getX(render2d)
        wZ = self.colorWheel.getZ(render2d)

        xDist = wX - mx
        zDist = wZ - my

        distFromCenter = math.sqrt(
            (xDist ** 2) + (zDist ** 2))

        hue = math.degrees(math.atan2(xDist, zDist))

        # We don't want hue to be below 0, needs to be 0-360 scale
        if hue < 0: hue += 360

        saturation = (distFromCenter / 0.23) * 100

        self.setHsv(hue, saturation, self.valueBar['value'])
        return task.cont

    def setHsv(self, hue, saturation, value):
        saturation = bound(saturation, 20, 90)
        value = bound(value, 50, 95)

        if self.valueBar['value'] != value: self.valueBar['value'] = value

        self.updateColor(hue, saturation, value)

    def setBrightness(self):
        self.setHsv(self.hsv[0] * 360., self.hsv[1] * 100., self.valueBar['value'])

    def setFromRgb(self, r, g, b):
        r = min(r, 255) / 255.
        g = min(g, 255) / 255.
        b = min(b, 255) / 255.

        hsv = self.rgbToHsv(r, g, b)
        self.setHsv(hsv[0] * 360, hsv[1] * 100, hsv[2] * 100)

    def updateColor(self, hue, saturation, value):
        self.hsv = [hue / 360., saturation / 100., value / 100.]

        self.rgb = self.hsvToRgb(*self.hsv)

        # Adjust the brightness of the color wheel to accurately(-ish) reflect the values
        self.colorWheel.setColorScale(Vec4(value / 100, value / 100, value / 100, 1))

        # Tint the bar to represent the current rgb value
        self.valueBarImage.setColorScale(Vec4(self.hsvToRgb(hue / 360., saturation / 100., 1)))

        messenger.send("colorPicked")

    def hsvToRgb(self, h, s, v):
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return VBase4(rgb[0], rgb[1], rgb[2], 1)

    def rgbToHsv(self, r, g, b, a = 1):
        hsv = colorsys.rgb_to_hsv(r, g, b)
        return VBase3(hsv[0], hsv[1], hsv[2])
