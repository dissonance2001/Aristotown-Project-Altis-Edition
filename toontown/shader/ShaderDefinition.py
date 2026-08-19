class ShaderDefinition:
    """
    The definitions of a shader.
    """

    def __init__(self,
                 fragmentFilename: str = 'passthrough',
                 vertexFilename: str = 'passthrough',
                 uniformDefinitions: dict = None) -> None:
        if uniformDefinitions is None:
            uniformDefinitions = {}
        self.fragmentFilename = fragmentFilename
        self.vertexFilename = vertexFilename
        self.uniformDefinitions = uniformDefinitions

    def loadShader(self) -> Shader:
        return Shader.load(
            Shader.SLGLSL,
            f'phase_3/shaders/{self.getVertexFilename()}.vert',
            f'phase_3/shaders/{self.getFragmentFilename()}.frag',
        )

    def getFragmentFilename(self) -> str:
        return self.fragmentFilename

    def getVertexFilename(self) -> str:
        return self.vertexFilename

    def getUniformDefinitions(self) -> dict:
        return self.uniformDefinitions
