"""
ToontownLUTManager.py
Author: Loonatic
Date: 8/15/2021

Note: This is currently not in either the cg or glsl folder if in the scenario that we want to
utilize a CG equivalent of lutman, for whatever reason.

LUTMAN is a child of TSM and gets initialized when needed, such as in the YOTT playground.
LUTMAN is NEVER active if TSM is not active.

To make custom LUTs for Toontown, open "def_lut.png" in Photoshop (phase_3/lut), go to Adjustments>Color Lookup...
Either pick one of the default presets or import a cube file, then export the result as a new png file.

To actually make custom LUTS, check out this video: https://youtu.be/yo5yivVOzMQ

https://developer.nvidia.com/gpugems/gpugems2/part-iii-high-quality-rendering/chapter-24-using-lookup-tables-accelerate-color

"""
from panda3d.core import TransparencyAttrib as ta
from . import ShaderGlobals
from ..utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class LUTManager:
    def __init__(self, manager = None, manager2d = None, affect2d = True):
        if __debug__:
            self.notify.setDebug(True)
        self.notify.debug("init")
        self.manager = manager
        self.manager2d = manager2d
        self.affect2d = affect2d
        self.visible = False
        self.sg = ShaderGlobals
        self.luts = self.sg.LUTList
        self.quad = None
        self.quad2d = None
        vertexShader = "phase_3/shaders/lut.vert"
        fragmentShader = "phase_3/shaders/lut.frag"
        self.shader = Shader.load(Shader.SLGLSL, vertexShader, fragmentShader)
        self.tex2d = None
        self.tex3d = None
        self.loaded = self.setupLUT()

    def setupLUT(self):
        """
        Sets up the LUT vertex and fragment shaders
        """
        self.notify.debug("setupLUT")
        if self.shader is not None:  # Avoid a game crash
            self.loadShader()
            if self.affect2d:
                self.loadShader2d()
            # We need to call this during setup else our screen will be white
            self.setLUTDefault()  # Load our [default] lookup table image as a texture object
            self.notify.info('Loaded default LUT shader')
            base.shaderMode = 'lut'
            return True
        else:
            self.notify.warning('Cannot load default LUT shader!')
            self.removeShader()  # panic
            return False

    def loadShader(self):
        self.notify.debug("loadShader")
        if self.manager is None:
            self.notify.debug("loadShader: self.manager is None, returning")
            return
        colortex = Texture()  # Create an empty Texture object
        # quad is a GeomNode (NodePath) known as filter-base-quad
        self.quad = self.manager.renderSceneInto(colortex = colortex)  # Render-to-texture our scene (3D)
        self.quad.setShader(self.shader)  # Load shaders
        # Pass our rendered scene texture for the shader to process
        self.quad.setShaderInput("colorTexture", colortex)
        # self.quad.setTransparency(1) uncomment if you want source engine broken skybox vibes
        self.tex3d = colortex

    def loadShader2d(self):
        self.notify.debug("loadShader2d")
        if self.manager2d is None:
            self.notify.debug("loadShader2d: self.manager2d is None, returning")
            return
        colortex2d = Texture()
        colortex2d.setClearColor((0, 0, 0, 0))
        self.quad2d = self.manager2d.renderSceneInto(colortex = colortex2d)
        self.quad2d.setShader(self.shader)
        self.quad2d.setShaderInput("colorTexture", colortex2d)
        self.quad2d.setTransparency(ta.MAlpha, 1)  # This MUST be enabled else GUI will break!
        self.tex2d = colortex2d

    def getLUTS(self):
        return self.luts

    def getColorblindLUTS(self):
        return self.sg.colorblindLUTList

    def getQuad(self):
        self.notify.debug(self.quad)
        return self.quad

    def getQuad2d(self):
        self.notify.debug(self.quad2d)
        return self.quad2d

    def getTex2d(self):
        self.notify.debug(self.tex2d)
        return self.tex2d

    def getTex3d(self):
        self.notify.debug(self.tex3d)
        return self.tex3d

    def getID(self):
        self.notify.debug(ShaderGlobals.lut)
        return ShaderGlobals.lut

    def loadLUT(self, lut_file):
        self.notify.debug("loadLUT")
        lut = loader.loadTexture(lut_file, okMissing = True)
        if lut is None:
            self.notify.warning('Cannot load LUT shader!')
            return False
        lut.setFormat(Texture.F_rgb16)  # Do not set this to rgba
        lut.setWrapU(Texture.WMClamp)
        lut.setWrapV(Texture.WMClamp)
        lut.setClearColor((0, 0, 0, 0))
        if self.quad is not None:
            self.notify.debug("quad.setShaderInput")
            self.quad.setShaderInput("lut", lut)  # Pass our LUT texture for the shader to process
        if self.quad2d is not None:
            self.notify.debug("quad2d.setShaderInput")
            self.quad2d.setShaderInput("lut", lut)  # Pass our LUT texture for the shader to process
        self.visible = True  # <-- unused right now
        del lut
        return True

    def setLUTDefault(self):
        """
        While this is the default LUT, the colors are not precise to the original game colors.
        You would want to call this if you want to temporarily hide an applied LUT.
        """
        self.loadLUT(self.luts[0][1])

    def removeShader(self):
        """
        Removes/cleanup the LUT Manager class entirely, lutman must be initialized again to be re-activated.
        """
        self.clearBlackAndWhite()
        if self.manager is not None:
            self.manager.cleanup()
        del self.manager
        if self.manager2d is not None:
            self.manager2d.cleanup()
        del self.manager2d
        if self.quad is not None:
            self.quad.removeNode()
        del self.quad
        if self.quad2d is not None:
            self.quad2d.removeNode()
        del self.quad2d
        del self.shader
        del self.sg
        del self.luts
        del self.tex2d
        del self.tex3d
        del self.visible
        del self.loaded
        base.shaderMode = 'none'
        base.shader = None

    def cleanup(self):
        if self.manager is not None:
            self.manager.cleanup()
        if self.manager2d is not None:
            self.manager2d.cleanup()

    def cleanup3d(self):
        self.notify.debug("cleanup3d")
        if self.manager is not None:
            self.manager.cleanup()
        if self.quad is not None:
            self.quad.removeNode()
        self.quad = None
        self.tex3d = None
        self.manager = None
        self.notify.debug("finished cleanup3d")

    def cleanup2d(self):
        """
        Removes manager2d for this current instance of the LUT manager.
        Currently utilized for the YOTT black and white shader.
        """
        self.notify.debug("cleanup2d")
        # if self.affect2d:
        #     return
        if self.manager2d is not None:
            self.manager2d.cleanup()
        if self.quad2d is not None:
            self.quad2d.removeNode()
        self.quad2d = None
        self.tex2d = None
        self.manager2d = None
        self.notify.debug("finished cleanup2d")

    # Shortcut methods
    def toggleBlackAndWhite(self):
        # Optional toggleable function if desired
        if not base.BWEnabled:
            self.loadLUT(self.getLUTS()[1][1])
        else:
            self.setLUTDefault()

    def setBlackAndWhite(self, strong = False):
        if not strong:
            self.loadLUT(self.getLUTS()[1][1])
        else:
            self.loadLUT(self.getLUTS()[19][1])

    def clearBlackAndWhite(self):
        # Force disable
        self.setLUTDefault()

    def setColorblindLut(self, index):
        if index == -1:
            return
        self.loadLUT(self.getColorblindLUTS()[index][1])

    def setLut(self, index):
        self.loadLUT(self.getLUTS()[index][1])


"""
from toontown.shader import LUTManager
lutman = LUTManager.LUTManager(base.aspect2d)
luts = lutman.getLUTS()
lutman.loadLUT(luts[0][1])

xx

from toontown.shader import LUTManager
lutman = LUTManager.LUTManager(base.aspect2d)
base.tsm.initLUTManager(affect2d=False)
luts = lutman.getLUTS()
base.shader.loadLUT(luts[0][2])

"""
