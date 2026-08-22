from toontown.shader.ShaderDefinition import ShaderDefinition


class LUTShaderDefinition(ShaderDefinition):
    """
    The definitions of a LUT shader.
    """

    lutFilepath = 'phase_3/luts/'

    def __init__(self,
                 fragmentFilename='lut',
                 vertexFilename='passthrough',
                 uniformDefinitions=None,
                 lutFilename='dramatic_lut.png'):
        # Load superclass.
        super(LUTShaderDefinition, self).__init__(fragmentFilename=fragmentFilename,
                         vertexFilename=vertexFilename,
                         uniformDefinitions=uniformDefinitions)

        # Handle lut things now.
        self.lutFilename = lutFilename

        # Add wet if it was forgotten.
        if 'wet' not in self.uniformDefinitions:
            self.uniformDefinitions['wet'] = 1.0

    def getUniformDefinitions(self):
        uniformDefs = super(LUTShaderDefinition, self).getUniformDefinitions()
        uniformDefs.update(self.getLutDefinition())
        return uniformDefs

    def getLutFilename(self):
        return self.lutFilepath + self.lutFilename

    def getLutDefinition(self):
        lut = loader.loadTexture(self.getLutFilename(), okMissing=True)
        if lut is None:
            # LUT could not load properly.
            return {}
        lut.setFormat(Texture.F_rgb16)
        lut.setWrapU(Texture.WMClamp)
        lut.setWrapV(Texture.WMClamp)
        lut.setClearColor((0, 0, 0, 0))
        return {'lut': lut}