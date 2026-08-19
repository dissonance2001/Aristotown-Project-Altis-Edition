"""
  Film Grain Shader (FGS)

"""
from panda3d.core import TransparencyAttrib as ta
import math

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class FilmGrainShader:
    def __init__(self, manager=None, manager2d=None): # parent=aspect2d
        self.manager = manager
        self.manager2d = manager2d
        vertexShader = "phase_3/shaders/basic.vert"
        fragmentShader = "phase_3/shaders/film-grain.frag"
        self.shader = Shader.load(Shader.SLGLSL, vertexShader, fragmentShader)
        self.quad = None
        self.quad2d = None
        self.tex2d = None
        self.tex3d = None
        # Shader inputs
        self.enabled = False # doesn't do anything yet
        self.value = math.pi # Play around with this later
        self.value2d = math.pi
        self.loaded = self.setupShader()

    def setupShader(self):
        """
        Sets up the vertex and fragment shaders
        returns True if shader was successfully initialized/loaded, False if not.
        TODO
        customize amount somehow, possibly with multiplier
        and also see what different variations we can do, check frag for info on that <-
        If needed, have a function to change the self.enable value
        """
        if self.shader is not None: # Avoid a game crash
            self.loadShader()
            self.loadShader2d()
            self.notify.info('Loaded shader')
            base.shaderMode = 'fgs'
            return True
        else:
            self.notify.warning('Failed to load shader!')
            return False

    def loadShader(self):
        if self.manager is None:
            return
        colortex = Texture()  # Create an empty Texture object
        # quad is a GeomNode (NodePath) known as filter-base-quad
        self.quad = self.manager.renderSceneInto(colortex=colortex)  # Render-to-texture our scene (3D)
        self.quad.setShader(self.shader)  # Load shaders
        # Pass our rendered scene texture for the shader to process
        self.quad.setShaderInput("colorTexture", colortex)
        self.quad.setShaderInput("enabled", (1, 1))
        # We don't actually need to input the same thing twice, but it's defined as a Vec2 in frag
        self.quad.setShaderInput("pi", (self.value, self.value))
        self.tex3d = colortex

    def loadShader2d(self):
        if self.manager2d is None:
            return
        colortex2d = Texture()
        colortex2d.setClearColor((0, 0, 0, 0))
        self.quad2d = self.manager2d.renderSceneInto(colortex=colortex2d)
        self.quad2d.setShader(self.shader)
        self.quad2d.setShaderInput("colorTexture", colortex2d)
        self.quad2d.setShaderInput("enabled", (1, 1))
        # We don't actually need to input the same thing twice, but it's defined as a Vec2 in frag
        self.quad2d.setShaderInput("pi", (self.value2d, self.value2d))
        self.quad2d.setTransparency(ta.MAlpha, 1)  # This MUST be enabled else GUI will break!
        self.tex2d = colortex2d

    def getValueRender(self):
        return self.value

    def setValueRender(self, value):
        self.value = value
        self.quad.setShaderInput("pi", (self.value, self.value))

    def getValueRender2d(self):
        return self.value2d

    def setValueRender2d(self, value2d):
        self.value2d = value2d
        self.quad2d.setShaderInput("pi", (self.value2d, self.value2d))

    def getQuad(self):
        """
        Quad contains a GeomNode and a Camera.
        This is like a plane that is overlayed on the screen.
        It does not have any attributes for the most part, including hasShader
        :return: NodePath based off of render
        """
        return self.quad

    def getQuad2d(self):
        """
        Quad2D contains a GeomNode and a Camera.
        Same description as getQuad.
        :return: NodePath based off of render2d
        """
        return self.quad2d

    def getTex2d(self):
        return self.tex2d

    def getTex3d(self):
        return self.tex3d

    def removeShader(self):
        """
        Removes/cleanup the shader class entirely, shader must be initialized again to be re-activated.
        """
        # You can also clear any active applied effects
        self.manager.cleanup()
        del self.manager
        if self.manager2d is not None:
            self.manager2d.cleanup()
        del self.manager2d
        self.quad.removeNode()
        del self.quad
        if self.quad2d is not None:
            self.quad2d.removeNode()
        del self.quad2d
        del self.shader
        del self.tex2d
        del self.tex3d
        del self.enabled
        del self.loaded
        base.shader = None
