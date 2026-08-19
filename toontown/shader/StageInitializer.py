from panda3d.core import AuxBitplaneAttrib, Vec4

from toontown.shader.Filter import Filter

###################################################
# Special magic filter to initialize a render pass
###################################################

class StageInitializer(Filter):
    """This filter simply initializes pixcolor from the current pixel in the pipeline stage input color texture.

    It is automatically inserted into each FilterStage created during FilterPipeline.reconfigure().

    Unlike other filters, the properties of StageInitializer are not meaningful,
    and the filter is owned by (the only is reference stored in) the FilterStage it resides in.
    Hence, during each reconfigure of the pipeline, old StageInitializers are destroyed,
    and new ones created (because FilterStages are).

    The sort value must be -1, which places StageInitializer before any other filters in the stage.
    Only StageInitializer is allowed to have a sort value of -1.

    """
    def __init__(self, **kwargs):
        super(StageInitializer, self).__init__(**kwargs)

        # Unlike usual, this filter doesn't want the compositing fshader
        # to supply the current value of pixcolor to the filter function
        # (because the purpose of StageInitializer is to
        #  determine and assign the initial value of pixcolor).
        #
        # For more information, see Filter.__init__().
        #
        self._needPixcolor = False

    def onReset(self):
        super(StageInitializer, self).onReset()  # reset inherited properties
        self.sort        = -1     # Initialization goes first before any other filter
                                  # in the same FilterStage.

        self.stageName   = None   # This filter is special; the value of stageName is not used.
                                  # Instead, each created render pass gets one copy of the filter.

        self.isMergeable = None   # The initialization filter is only added after the logical stage
                                  # into render pass merging process is complete. The value of isMergeable
                                  # is ignored.

    def onAttachPipeline(self):
        # The compositing shader needs the color texture to initialize the output color.
        self.registerInputTexture(texName="color")

    def onSynthesizeCompositor(self):
        # Registered textures are accessed with self.getTextureInfo(texName).
        # This ensures that the correct definition is returned.
        #
        # See Filter.TextureInfo for the available fields.
        #
        # pixcolor is the input/output variable for the color of the current pixel.
        #
        txcolor = self.getTextureInfo("color")
        return ("stageInitializer",
                "float4 pixcolor = tex2D(%(k_txcolor)s, %(texcoord_txcolor)s);\n" % { "k_txcolor" : txcolor.get('varname'),
                                                                                      "texcoord_txcolor" : txcolor.get('texcoord') },
                "// initialize pixcolor\n")
