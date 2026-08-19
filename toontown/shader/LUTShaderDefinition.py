from toontown.shader.ShaderDefinition import ShaderDefinition


class LUTShaderDefinition(ShaderDefinition):
    """
    The definitions of a LUT shader.
    """

    lutFilepath = 'phase_3/luts/'

    def __init__(self,
                 fragmentFilename: str = 'lut',
                 vertexFilename: str = 'passthrough',
                 uniformDefinitions: dict = None,
                 lutFilename: str = 'dramatic_lut.png') -> None:
        # Load superclass.
        super().__init__(fragmentFilename=fragmentFilename,
                         vertexFilename=vertexFilename,
                         uniformDefinitions=uniformDefinitions)

        # Handle lut things now.
        self.lutFilename = lutFilename

        # Add wet if it was forgotten.
        if 'wet' not in self.uniformDefinitions:
            self.uniformDefinitions['wet'] = 1.0

    def getUniformDefinitions(self) -> dict:
        uniformDefs = super().getUniformDefinitions()
        uniformDefs.update(self.getLutDefinition())
        return uniformDefs

    def getLutFilename(self) -> str:
        return self.lutFilepath + self.lutFilename

    def getLutDefinition(self) -> dict:
        lut = loader.loadTexture(self.getLutFilename(), okMissing=True)
        if lut is None:
            # LUT could not load properly.
            return {}
        lut.setFormat(Texture.F_rgb16)
        lut.setWrapU(Texture.WMClamp)
        lut.setWrapV(Texture.WMClamp)
        lut.setClearColor((0, 0, 0, 0))
        return {'lut': lut}
