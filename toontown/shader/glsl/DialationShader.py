"""
  Dialation Shader (DLS)

"""

class DialationShader:
    def __init__(self, manager):
        self.manager = manager
        self.vertexShader = "phase_3/shaders/basic.vert"
        self.fragmentShader = "phase_3/shaders/dialation.frag"
        self.size = 2
        self.separation = 2.0
        self.quad = None
        self.loaded = self.loadShader()

    def loadShader(self):
        """
        Sets up the vertex and fragment shaders
        todo: customize size and separation values
        :return:
        """
        if self.quad is not None:
            return self.loaded # Shader has already been setup
        colortex = Texture() # Create an empty Texture object

        # quad is a GeomNode (NodePath) known as filter-base-quad
        self.quad = self.manager.renderSceneInto(colortex=colortex)  # Render-to-texture our scene
        shader = Shader.load(Shader.SLGLSL, self.vertexShader, self.fragmentShader)
        if shader is not None:  # Avoid a game crash
            self.quad = self.manager.renderSceneInto(colortex=colortex)
            self.quad.setShader(shader)
            self.quad.setShaderInput("colorTexture", colortex)
            self.quad.setShaderInput("parameters", (self.size, self.separation))
            return True
        else:
            return False


    def setSize(self, size):
        self.size = int(size)
        self.refreshParameters()

    def getSize(self):
        return self.size

    def setSeparation(self, separation):
        self.separation = float(separation)
        self.refreshParameters()

    def getSeparation(self):
        return self.separation

    def getParameters(self):
        return (self.size, self.separation)

    def refreshParameters(self):
        self.quad.setShaderInput("parameters", (self.size, self.separation))

    def deleteShader(self):
        self.manager.cleanup()
        del self.manager
        self.quad.removeNode()
        del self.quad
        del self.vertexShader
        del self.fragmentShader
        del self.loaded
