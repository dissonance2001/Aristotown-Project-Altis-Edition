from direct.showbase.DirectObject import DirectObject

from toontown.shader.NodeShader import NodeShader
from toontown.shader.ShaderGlobals import canUseShaders
from direct.interval.IntervalGlobal import *

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class NodeShaderManager(DirectObject):
    """
    A class to help manage shaders on a given node.
    """

    def __init__(self, node, active=True):
        self.node = node
        self.active = active
        self.nodeShaders = []
        self.uniforms = {}
        self.uniformOverrides = {}
        self.accept('option-update-want-shaders', self.onShaderSettingsToggle)

    def cleanup(self):
        """
        Cleans up the NSM, and cleans the shader off the node.
        """
        if self.node:
            self.node.clearShader()
        for uniform in self.uniforms:
            self.node.clearShaderInput(uniform)
        self.nodeShaders = []
        self.ignoreAll()
        del self.node

    """
    Various external settings
    """

    def setActive(self, mode=None):
        """
        Sets the active level of the NSM.
        """
        if mode is None:
            self.active = not self.active
            self.updateShaders()
        elif self.active != mode:
            self.active = mode
            self.updateShaders()

    """
    Shader interface
    """

    def addShader(self, nodeShader=None, update=True):
        """
        Adds a shader to the NSM.
        """
        self.nodeShaders.append(nodeShader)
        if update:
            self.updateShaders()
        return nodeShader

    def removeShader(self, nodeShader=None, update=True):
        """
        Removes a shader from the NSM.
        """
        if nodeShader in self.nodeShaders:
            # Remove it from the list.
            self.nodeShaders.remove(nodeShader)

            # Remove shader uniforms from av.
            for uniform in self.uniforms:
                self.node.clearShaderInput(uniform)

            # Update if we want to.
            if update:
                self.updateShaders()

            # The shader was removed successfully.
            return True

        # Shader could not be found.
        return False

    def clearShaders(self):
        """
        Clears all shaders from the NSM.
        """
        for nodeShader in self.nodeShaders[:]:
            self.removeShader(nodeShader, update=False)
        self.updateShaders()

    """
    Node manipulation
    """

    def updateShaders(self):
        """
        Updates the currently active shaders on the node.
        """
        if not self.node:
            # There is no node. This is a problem.
            return self.notify.warning('NodeShaderManager tried to update, but the node didn\'t exist?')

        if not canUseShaders():
            # Don't bother doing anything -- we can't use shaders.
            self.onShaderFail()
            return

        # Get the active shaders.
        nodeShaders = self.getActiveShaders()

        if not nodeShaders or self.active is False or not settings['want-shaders']:
            # There are no applicable shaders to apply to the node.
            # Or, this NSM is deactivated.
            # Or, shaders are disabled in settings.
            self.node.clearShader()
        else:
            # There are shaders to apply to the node.
            # Find the highest priority shader to apply.
            nodeShader = max(nodeShaders)  # type: NodeShader
            shaderDefinition = nodeShader.getShaderDefinition()
            shader = shaderDefinition.loadShader()
            if shader is None:
                return self.notify.warning(
                    'Shader for {0} could not be loaded. Vertex: {1} | Fragment: {2}'.format(
                        self.node,
                        shaderDefinition.getVertexFilename(),
                        shaderDefinition.getFragmentFilename()
                    )
                )
            self.node.setShader(shader)

            # Set the uniform inputs on the shader.
            self.uniforms = shaderDefinition.getUniformDefinitions()
            self.uniforms.update(nodeShader.getUniformOverrides())
            self.uniforms.update(self.uniformOverrides)
            self.applyUniforms()

    def applyUniforms(self):
        """
        Applies the uniforms on the shader inputs.
        """
        if not canUseShaders():
            return
        for uniform, value in self.uniforms.items():
            self.node.setShaderInput(uniform, value if not callable(value) else value())

    def setUniformOverrides(self, overrides, update=True):
        # Updates the uniform overrides.
        self.uniformOverrides = overrides
        if update:
            self.updateShaders()

    def onShaderFail(self):
        # We do nothing if we can't support the shaders.
        pass

    def onShaderSettingsToggle(self, *_):
        # When the settings toggle, simply update our shaders.
        self.updateShaders()

    """
    Getters
    """

    def getActiveShaders(self):
        return [nodeShader for nodeShader in self.nodeShaders if nodeShader.canUse()]

    """
    Intervals
    """

    def lerpUniformInterval(self,
                            uniform, duration,
                            fromData=0.0,
                            toData=1.0,
                            blendType='easeInOut'):
        def updateInput(t):
            if hasattr(self, 'node'):
                self.node.setShaderInput(uniform, t)
        return LerpFunctionInterval(
            function=updateInput, duration=duration,
            fromData=fromData, toData=toData,
            blendType=blendType,
        )