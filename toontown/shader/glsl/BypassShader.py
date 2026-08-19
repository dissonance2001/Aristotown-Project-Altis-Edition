"""
  Bypass Shader

"""

from panda3d.core import TransparencyAttrib as ta
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class BypassShader:
    def __init__(self, manager=None, manager2d=None):
        self.manager = manager
        self.manager2d = manager2d
        vertexShader = "phase_3/shaders/basic.vert"
        fragmentShader = "phase_3/shaders/basic.frag"
        self.shader = Shader.load(Shader.SLGLSL, vertexShader, fragmentShader)
        self.quad = None
        self.quad2d = None
        self.tex2d = None
        self.tex3d = None
        self.loaded = self.setupShader()

    def setupShader(self):
        """
        Sets up the vertex and fragment shaders
        returns True if shader was successfully initialized/loaded, False if not.
        """
        if self.shader is not None: # Avoid a game crash
            self.loadShader()
            self.loadShader2d()
            self.notify.info('Loaded shader')
            return True
        else:
            self.notify.warning('Failed to load shader!')
            return False

    def loadShader(self):
        if self.manager is None:
            return
        colortex = Texture()
        self.quad = self.manager.renderSceneInto(colortex=colortex)
        self.quad.setShader(self.shader)
        self.quad.setShaderInput("colorTexture", colortex)
        self.tex3d = colortex

    def loadShader2d(self):
        if self.manager2d is None:
            return
        colortex2d = Texture()
        colortex2d.setClearColor((0, 0, 0, 0))
        self.quad2d = self.manager2d.renderSceneInto(colortex=colortex2d)
        self.quad2d.setShader(self.shader)
        self.quad2d.setShaderInput("colorTexture", colortex2d)
        self.quad2d.setTransparency(ta.MAlpha, 1)
        self.tex2d = colortex2d

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
        del self.tex2d
        del self.tex3d
        # del self.sg
        del self.loaded
        base.shader = None


