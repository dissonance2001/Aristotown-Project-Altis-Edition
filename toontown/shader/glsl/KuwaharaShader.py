"""
Kuwahara Shader (KWS)
Applies a painter-like effect
https://www.wikipedia.com/en/Kuwahara_filter
"""

from panda3d.core import TransparencyAttrib as ta
from direct.directnotify import DirectNotifyGlobal
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class KuwaharaShader:
    def __init__(self, manager=None, manager2d=None):
        self.manager = manager
        self.manager2d = manager2d
        vertexShader = "phase_3/shaders/basic.vert"
        fragmentShader = "phase_3/shaders/kuwahara-filter.frag"
        self.shader = Shader.load(Shader.SLGLSL, vertexShader, fragmentShader)
        self.quad = None
        self.quad2d = None
        self.tex2d = None
        self.tex3d = None
        self.quad = None
        # frag params
        self.variance = float(0.0)
        self.variance2d = float(0.0)
        self.size = 5
        self.size2d = 5
        self.loaded = self.setupShader()

    def setupShader(self):
        """
        Sets up the vertex and fragment shaders
        returns True if shader was successfully initialized/loaded, False if not.
        """
        if self.shader is not None:  # Avoid a game crash
            self.loadShader()
            self.loadShader2d()
            self.notify.info('Loaded shader')
            base.shaderMode = 'kws'
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
        self.quad.setShaderInput("parameters", (self.size, self.variance))
        self.tex3d = colortex

    def loadShader2d(self):
        if self.manager2d is None:
            return
        colortex2d = Texture()
        colortex2d.setClearColor((0, 0, 0, 0))
        self.quad2d = self.manager2d.renderSceneInto(colortex=colortex2d)
        self.quad2d.setShader(self.shader)
        self.quad2d.setShaderInput("colorTexture", colortex2d)
        self.quad2d.setShaderInput("parameters", (self.size2d, self.variance2d))
        self.quad2d.setTransparency(ta.MAlpha, 1)  # This MUST be enabled else GUI will break!
        self.tex2d = colortex2d

    def getSizeRender(self):
        return self.size

    def setSizeRender(self, value):
        self.size = value
        self.refreshParams()

    def getSizeRender2d(self):
        return self.size2d

    def setSizeRender2d(self, value2d):
        self.size2d = value2d
        self.refreshParams()

    def getVarianceRender(self):
        return self.variance

    def setVarianceRender(self, value):
        if value < -1:
            return
        self.variance = value
        self.refreshParams()

    def getVarianceRender2d(self):
        return self.variance2d

    def setVarianceRender2d(self, value):
        if value < -1:
            return
        self.variance2d = value
        self.refreshParams()

    # Convenience methods
    def setVariance(self, value):
        self.setVarianceRender(value)
        self.setVarianceRender2d(value)

    def setSize(self, value):
        self.setSizeRender(value)
        self.setSizeRender2d(value)

    def refreshParams(self):
        if self.quad is not None:
            self.quad.setShaderInput("parameters", (self.size, self.variance))
        if self.quad2d is not None:
            self.quad2d.setShaderInput("parameters", (self.size2d, self.variance2d))

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
        del self.loaded
        base.shaderMode = 'none'
        base.shader = None


