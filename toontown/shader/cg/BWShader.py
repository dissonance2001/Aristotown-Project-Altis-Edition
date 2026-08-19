"""
BWShader.py
Author: Loonatic
Date: 10/12/2021

Note: This is a CG shader intended as a workaround for the LUTMAN YOTT B&W effect being incompatible with macOS (GLSL)
"""
from panda3d.core import TransparencyAttrib as ta
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class BWShader:
    def __init__(self, manager=None, manager2d=None):
        self.manager = manager
        self.manager2d = manager2d
        self.shaderFile = Filename("phase_3/shaders/cg/bandw.sha")
        # Generic shader intended to "hide" bandw
        self.shaderProxy = Filename("phase_3/shaders/cg/cg_empty.sha")
        self.shader = None
        self.quad = None
        self.quad2d = None
        self.tex2d = None
        self.tex3d = None
        self.loaded = self.setupShader(self.shaderFile)
        base.shaderMode = 'bw'

    def setupShader(self, inputShader):
        """
        Sets up the vertex and fragment shaders
        returns True if shader was successfully initialized/loaded, False if not.
        """
        self.shader = Shader.load(inputShader, Shader.SL_Cg)
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
        if self.quad is None: # Should only be ran *once*
            colortex = Texture()  # Create an empty Texture object
            # quad is a GeomNode (NodePath) known as filter-base-quad
            self.quad = self.manager.renderSceneInto(colortex=colortex)  # Render-to-texture our scene (3D)
            self.quad.setShader(self.shader)  # Load shaders
            # Pass our rendered scene texture for the shader to process
            self.quad.setShaderInput("tex", colortex)
            # self.quad.setTransparency(1) uncomment if you want source engine broken skybox vibes
            self.tex3d = colortex
        else: # Aux for shaderProxy
            self.quad.setShader(self.shader)

    def loadShader2d(self):
        if self.manager2d is None:
            return
        if self.quad2d is None:
            colortex2d = Texture()
            colortex2d.setClearColor((0, 0, 0, 0))
            self.quad2d = self.manager2d.renderSceneInto(colortex=colortex2d)
            self.quad2d.setShader(self.shader)
            self.quad2d.setShaderInput("tex", colortex2d)
            self.quad2d.setTransparency(ta.MAlpha, 1)  # This MUST be enabled else GUI will break!
            self.tex2d = colortex2d
        else:
            self.quad2d.setShader(self.shader)

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
        # self.clearBlackAndWhite()
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
        del self.shaderFile
        del self.shaderProxy
        del self.tex2d
        del self.tex3d
        del self.loaded
        base.shader = None

    def cleanup(self):
        if self.manager is not None:
            self.manager.cleanup()
        if self.manager2d is not None:
            self.manager2d.cleanup()

    def cleanup3d(self):
        if self.manager is None:
            return
        self.manager.cleanup()
        if self.quad is not None:
            self.quad.removeNode()
        self.quad = None
        self.tex3d = None
        self.manager = None

    def cleanup2d(self):
        """
        Removes manager2d for this current instance of the LUT manager.
        Currently utilized for the YOTT black and white shader.
        :return:
        """
        if self.affect2d:
            return
        if self.manager2d is None:
            return
        self.manager2d.cleanup()
        if self.quad2d is not None:
            self.quad2d.removeNode()
        self.quad2d = None
        self.tex2d = None
        self.manager2d = None

    # Shortcut methods
    def toggleBlackAndWhite(self):
        # Optional toggleable function if desired
        if not base.BWEnabled:
            self.setupShader(self.shaderFile)
        else:
            self.setupShader(self.shaderProxy)
        base.BWEnabled = not base.BWEnabled

    def setBlackAndWhite(self):
        self.setupShader(self.shaderFile)
        base.BWEnabled = True

    def clearBlackAndWhite(self):
        # Force disable
        self.setupShader(self.shaderProxy)
        base.BWEnabled = False


