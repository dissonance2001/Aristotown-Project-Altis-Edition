"""
Bloom Shader (BLS)

"""

class BloomShader:
    def __init__(self, manager):
        self.manager = manager
        self.vertexShader = "phase_3/shaders/basic.vert"
        self.fragmentShader = "phase_3/shaders/bloom.frag"


    def loadShader(self):
        """
        Sets up the vertex and fragment shaders
        :param lut_file:
        :return:
        """
        colortex = Texture()
        self.quad = self.manager.renderSceneInto(colortex=colortex)
        self.quad.setShader(Shader.load(Shader.SLGLSL, self.vertexShader, self.fragmentShader))
        self.quad.setShaderInput("colorTexture", colortex)
        self.quad.setShaderInput("enabled", (1, 1))
