class ShaderDefinition(object):
    """
    The definitions of a shader.
    """

    def __init__(self,
                 fragmentFilename='passthrough',
                 vertexFilename='passthrough',
                 uniformDefinitions=None):
        if uniformDefinitions is None:
            uniformDefinitions = {}
        self.fragmentFilename = fragmentFilename
        self.vertexFilename = vertexFilename
        self.uniformDefinitions = uniformDefinitions

    def loadShader(self):
        return Shader.load(
            Shader.SLGLSL,
            'phase_3/shaders/{0}.vert'.format(self.getVertexFilename()),
            'phase_3/shaders/{0}.frag'.format(self.getFragmentFilename()),
        )

    def getFragmentFilename(self):
        return self.fragmentFilename

    def getVertexFilename(self):
        return self.vertexFilename

    def getUniformDefinitions(self):
        return self.uniformDefinitions