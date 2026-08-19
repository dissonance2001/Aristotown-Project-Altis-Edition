"""
  ToontownShaderManager
  Wrapper class for all things shaders

  Notice: It is important to remember that you can only call setShader one at a time, meaning
  you cannot have multiple shaders called on top of each other, unless they are combined within the same shader file.
  Also, filters won't work properly if textures-power-2 is enabled or set to True


  Currently, only TSM is intialized and setup when the client starts.
  - Important to consider that this will generate a new texture in memory that will ALWAYS be called for.
  - It's possible (and probably much more optimal) that if neither of these modules are being utilized that they can
  be disabled, but that feature isn't implemented yet.
  - At the moment, filter effects are disabled by just turning off the shader but not necessarily removing it from
  memory. Keep this in mind for now.

  TODO
  - Make it where you can initialize a shader for only render or render2d
    - Need to add more checks "if self.manager is not None ..."
    - For GenericShader, would be ideal to pass a tuple/list
  - Should each shader have an "enabled" variable in them for feasibility? Some have it, some don't
  - Also, for shaders, do we need to use Vec2 for single elements like booleans?

"""
from panda3d.core import ConfigVariableBool
# from direct.filter.FilterManager import FilterManager
from .FilterManager import FilterManager
from ..utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class ToontownShaderManager:
    def __init__(self, override=None):
        if ConfigVariableBool('textures-power-2', True).getValue():
            # This is a workaround, if ^ is enabled, the game would only render in the bottom left corner of the window.
            self.notify.warning("Cannot be initialized with texture-power-2 config enabled.")
            return

        """
        The FilterManager constructor requires you to provide a window which is rendering a scene,
        and the camera which is used by that window to render the scene.
        These are henceforth called the 'original window' and the 'original camera.'

        At the very moment TSM only supports postprocessing shaders,
        """
        wantTSM = ConfigVariableBool('want-tsm', False).getValue()
        if override is not None:
            wantTSM = override
        if not wantTSM:
            # Should only be called manually using an injector
            # Experimental purposes only
            self.manager = base.effectMgr.filterPipeline.manager
            self.manager2d = None
        else:
            self.manager = FilterManager(base.win, base.cam)
            self.manager2d = FilterManager(base.win, base.cam2d)

        self.notify.info("Initialized ToontownShaderManager")

    # This is a template shader, used for debugging/testing
    def initTemplateShader(self):
        from . import TemplateShader
        return TemplateShader.TemplateShader(self.manager, self.manager2d)

    # Default shader, shouldn't change anything visually
    def initGenericShader(self):
        from . import GenericShader as bs
        return bs.GenericShader(2)  # self.manager, self.manager2d)

    def initLUTManager(self, affect2d = True):
        from . import LUTManager
        return LUTManager.LUTManager(self.manager, self.manager2d, affect2d = affect2d)

    def initCAS(self):
        from .glsl import ChromaticAberrationShader as cas
        return cas.ChromaticAberrationShader(self.manager, self.manager2d)

    def initFilmGrain(self):
        from .glsl import FilmGrainShader as fgs
        return fgs.FilmGrainShader(self.manager, self.manager2d)

    def initKWS(self):
        from .glsl import KuwaharaShader as kws
        return kws.KuwaharaShader(self.manager, self.manager2d)

    def initDialation(self):
        from .glsl import DialationShader as dls
        return dls.DialationShader(self.manager)

    def initBW(self):  # This is a CG shader
        from .cg import BWShader as bws
        return bws.BWShader(self.manager)

    # You shouldn't need to call this normally
    def destroy(self):
        self.notify.info("Removing ToontownShaderManager")
        self.manager.cleanup()
        self.manager2d.cleanup()
        del self.manager
        del self.manager2d
        base.tsm = None

    # Util methods
    def resizeBuffers(self):
        # Resize all buffers to match the size of the window.
        # could possibly be used as a workaround with having to force textures-powers-2 to be disabled..?
        self.manager.resizeBuffers()

    def resizeBuffersAuto(self):
        # When the window changes size, automatically resize all buffers
        # idk what this actually does
        self.manager.window_event(base.win)

    def isFullscreen(self):
        return self.manager.isFullscreen()

    """
    Todo:
    Document special shaders such as position.frag
    See if some filter modules can be integrated/used in conjunction with this module
    Convert panda cg shaders to glsl

    PixelizeShader
    SSAOShader, if possible to generate a normal map and use as input
    """
