from toontown.shader.ShaderDefinition import ShaderDefinition
from toontown.shader.ShaderEnums import ShaderType
from toontown.shader.ShaderGlobals import ShaderDefinitions


class NodeShader:
    """
    NodeShader is a container class for shader data for nodes.
    They can be applied directly to a node by using a NodeShaderManager.
    """

    def __init__(self,
                 shaderType: ShaderType,
                 priority: int = 0,
                 uniformOverrides: dict = None,
                 useCondition: callable = None):
        """
        Initializes a NodeShader.

        :param shaderType:       The type of shader to use.
        :param priority:         The priority of the shader on the node (higher = applied first).
        :param uniformOverrides: Values to use as overrides for uniform definitions.
        """
        self.shaderType = shaderType
        self.priority = priority
        self.uniformOverrides = uniformOverrides
        self.useCondition = useCondition

    """
    Setters
    """

    def setUniform(self, uniform: str, value):
        self.uniformOverrides[uniform] = value

    def updateUniforms(self, uniformDict: dict):
        self.uniformOverrides.update(uniformDict)

    """
    Getters
    """

    def getShaderDefinition(self) -> ShaderDefinition:
        return ShaderDefinitions.getShaderDef(self.getShaderType())

    def getShaderType(self) -> ShaderType:
        return self.shaderType

    def getPriority(self) -> int:
        return self.priority

    def getUniformOverrides(self) -> dict:
        if self.uniformOverrides:
            return self.uniformOverrides
        return {}

    def canUse(self) -> bool:
        if self.useCondition is None:
            return True
        return self.useCondition()

    def __iter__(self):
        yield self.priority

    def __lt__(self, other):
        return self.getPriority() < other.getPriority()

    def __gt__(self, other):
        return self.getPriority() > other.getPriority()

    def __eq__(self, other):
        return self.getPriority() == other.getPriority()
