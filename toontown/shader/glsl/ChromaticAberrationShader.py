"""
Chromatic Aberration Shader (CAS)

"""
from panda3d.core import TransparencyAttrib as ta

class ChromaticAberrationShader:
    def __init__(self, manager=None, manager2d=None):
        self.manager = manager
        self.manager2d = manager2d

        self.vertexShader = "phase_3/shaders/base.vert"
        self.fragmentShader = "phase_3/shaders/chromatic-abberation.frag"
        self.quad = None
        self.quad2d = None
        self.enabled = True
        self.loaded = self.loadShader()

    def loadShader(self):
        """
        Sets up the vertex and fragment shaders
        :return:
        """
        if self.quad is not None:
            return self.loaded # Shader has already been setup
        shader = Shader.load(Shader.SLGLSL, self.vertexShader, self.fragmentShader)
        if shader is not None:  # Avoid a game crash
            colortex = Texture()  # Create an empty Texture object
            #colortex.setClearColor((0, 0, 0, 1))
            # quad is a GeomNode (NodePath) known as filter-base-quad
            self.quad = self.manager.renderSceneInto(colortex=colortex)  # Render-to-texture our scene
            self.quad.setShader(shader)  # Load shaders
            self.quad.setShaderInput("colorTexture", colortex) # Pass our rendered scene texture for the shader to process
            self.quad.setTransparency(1)

            if self.manager2d is not None:
                colortex2d = Texture()
                colortex2d.setClearColor((0, 0, 0, 0))
                #self.quad2d = render2d
                self.quad2d = self.manager2d.renderSceneInto(colortex=colortex2d) # renderQuad doesn't do anything, fixme
                self.quad2d.setShader(shader)
                self.quad2d.setShaderInput("colorTexture", colortex2d)
                self.quad2d.setTransparency(ta.MAlpha, 1)
            return True
        else:
            return False



    def getQuad(self):
        return self.quad

    def removeShader(self):
        """
        Removes LUTManager but should allow to be initialized again, should be used where LUT filters aren't necessarily needed
        Bug: Doesn't fully cleanup the buffer from memory, trying to cleanup and then init again will cause a memory leak
        todo: make sure everything gets properly removed
        """
        self.quad.clearShader()
        self.quad.removeNode()
        self.quad = None
        if self.quad2d is not None:
            self.quad2d.clearShader()
            self.quad2d.removeNode()
            self.quad2d = None
