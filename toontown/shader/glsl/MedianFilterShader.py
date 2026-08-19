"""
Median Filter Shader (MFS)

"""

class MedianFilterShader:
    def __init__(self, manager):
        self.manager = manager
        self.vertexShader = "phase_3/shaders/basic.vert"
        self.fragmentShader = "phase_3/shaders/median-filter.frag"


    def setupShader(self):
        """
        Sets up the vertex and fragment shaders
        :param lut_file:
        :return:
        """
        size = int(2) # todo make arg
        binSize = float(2.0)
        colortex = Texture()
        self.quad = self.manager.renderSceneInto(colortex=colortex)
        self.quad.setShader(Shader.load(Shader.SLGLSL, self.vertexShader, self.fragmentShader))
        self.quad.setShaderInput("colorTexture", colortex)
        self.quad.setShaderInput("parameters", (size, binSize))
