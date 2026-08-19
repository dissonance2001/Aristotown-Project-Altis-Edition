class InjectorShader:
    """
    A shader manager class that is designed to be compatible with the injector.
    """

    existingShaders = []

    def __init__(self, node,
                 uniformInputs: dict,
                 vertexFilename: str = 'passthrough',
                 fragmentFilename: str = 'passthrough',
                 cleanupExisting: bool = True):
        # Add ourselves to the existing shader list.
        if cleanupExisting:
            self.cleanupShaders()
        self.existingShaders.append(self)

        # Load our shader.
        self.node = node
        self.uniformInputs = uniformInputs
        self.shader = Shader.load(Shader.SLGLSL,
                                  f'phase_3/shaders/{vertexFilename}.vert',
                                  f'phase_3/shaders/{fragmentFilename}.frag')

        # Set it up.
        self.setupShader()

    def setupShader(self):
        if self.shader is None:
            print("No shader found.")
            self.node.clearShader()
        else:
            self.node.setShader(self.shader)
            for key, val in self.uniformInputs.items():
                self.node.setShaderInput(key, val)

        # Render a frame and see if something messed up.
        try:
            base.graphicsEngine.renderFrame()
        except AssertionError as e:
            # Yep.
            self.removeShader()
            raise e

    def removeShader(self):
        self.node.clearShader()
        del self.node

    @classmethod
    def cleanupShaders(cls):
        for shader in cls.existingShaders:
            shader.removeShader()
        cls.existingShaders = []
