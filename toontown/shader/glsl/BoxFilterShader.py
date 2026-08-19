"""
Box Filter Shader (BFS)

"""

class BoxFilterShader:
    def __init__(self, manager):
        self.manager = manager
        self.vertexShader = "phase_3/shaders/basic.vert"
        self.fragmentShader = "phase_3/shaders/box-blur.frag"


    def loadShader(self):
        """
        Sets up the vertex and fragment shaders
        :param lut_file:
        :return:
        """
        size = int(2) # todo make arg
        separation = float(2.0)
        colortex = Texture()
        self.quad = self.manager.renderSceneInto(colortex=colortex)
        self.quad.setShader(Shader.load(Shader.SLGLSL, self.vertexShader, self.fragmentShader))
        self.quad.setShaderInput("colorTexture", colortex)
        self.quad.setShaderInput("parameters", (size, separation))
