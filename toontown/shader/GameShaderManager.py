from toontown.shader.NodeShaderManager import NodeShaderManager
from toontown.shader.ShaderEnums import ShaderType


class GameShaderManager(NodeShaderManager):
    """
    A shader manager that is designed for functionality with the scene graph.
    Implements shader effect fallbacks if necessary.
    """

    def __init__(self, node, active: bool = True):
        super().__init__(node=node, active=active)
        self.cgShader = None

    def onShaderFail(self):
        # Attempt to find a shader we can substitute.
        nodeShaders = self.getActiveShaders()
        nodeShaders.sort(reverse=True)
        for nodeShader in nodeShaders:
            # Look for a valid shader to cover.
            if nodeShader.getShaderType() == ShaderType.LUT_Monochrome:
                # We can use a monochrome shader.
                if base.effectMgr:
                    # Set the B&W from the effectMgr directly.
                    base.effectMgr.setBlackAndWhite(1)
                else:
                    # Use a cgShader for fallback.
                    self.cgShader = base.tsm.initBW()

                # No matter what, we return.
                return

        # We couldn't find one, so disable.
        if base.effectMgr:
            # With the effectMgr, we disable everything.
            base.effectMgr.setBlackAndWhite(0)
        else:
            # Using a CG fallback, make sure it is cleared.
            if self.cgShader is not None:
                self.cgShader.removeShader()
                self.cgShader = None
