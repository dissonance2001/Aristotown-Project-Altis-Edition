from panda3d.core import AuxBitplaneAttrib, Vec4

from toontown.shader.Filter import Filter


class Bloom(Filter):
    """A bloom filter, causing bright objects to have a glowing halo around them.

    Note: If you want to use glow maps to indicate which parts of the image should receive bloom,
    you should assign a nonzero value to the alpha value of the "blend" parameter, and you should
    enable the shader generator for models that have glow maps applied. (The autoshader then writes
    the glow map into the alpha channel of the color texture; the alpha channel is otherwise unused.)

    """

    SIZES = ["small", "medium", "large"]

    def __init__(self, **kwargs):
        super(Bloom, self).__init__(**kwargs)

        # super's init will call cleanup(), which will call detach(), which triggers setdown(),
        # so we don't need to set self._downsampler here.

    def onReset(self):
        super(Bloom, self).onReset()
        self.sort = 50

        self.stageName   = "LensOpticsLate"
        self.isMergeable = False

        self.blend=(0.3, 0.4, 0.3, 0.0)
        self.mintrigger=0.6
        self.maxtrigger=1.0
        self.desat=0.6
        self.intensity=1.0
        self.size="medium"

    def onAttachPipeline(self):
        self.registerInputTexture(texName="bloomOutput")
        self.requireAuxBits(bitmask=AuxBitplaneAttrib.ABOGlow)

    def onAttachStage(self):
        if self.size not in Bloom.SIZES:
            raise ValueError("Bloom size '%s' unknown; valid sizes: %s" % (self.size, Bloom.SIZES) )

        if self.size == "large":
            scale = 8
            self._downsampler = "filter-down4.sha"
        elif self.size == "medium":
            scale = 4
            self._downsampler = "filter-copy.sha"
        else: # self.size == "small":
            scale = 2
            self._downsampler = None

        # It is good practice to name any potentially reusable textures using a human-readable name
        # (such as "bloomOutput" here), so that other filters later in the same stage can request
        # those textures regardless of the number of internal stages that happen to be set up.
        #
        if self._downsampler is not None:
            self.createInternalTextures( "bloom0", "bloom1", "bloom2", "bloomOutput" )
        else:
            self.createInternalTextures( "bloom0", "bloom1", "bloomOutput" )

        # The operation of the internal stages of this filter, especially regarding texture resolution
        # considerations, is somewhat nontrivial.
        #
        # The sequence of internal stages is:
        #
        #   - downscale to quarter resolution, generate bloom map
        #   - downscale further (if needed)
        #   - blur in x direction
        #   - blur in y direction, apply extra intensity if desired
        #
        # The compositing shader then takes the output from the final internal stage,
        # and blends it onto the scene.
        #
        #
        # Now, keep in mind that the "div" parameter of FilterManager is always given as a divisor
        # *for the window resolution*, regardless of the resolution of any input textures
        # that the shader (that is assigned to the quad) is fed with.
        #
        # We render the first internal stage into a quarter-resolution texture (div=2) compared to
        # the window resolution. The shader "filter-bloomi.sha" is designed for the special case of
        # rendering *from* a full-resolution texture *into* a quarter-resolution texture.
        #
        # When reading the shader source, keep in mind that the pixel size (texpix) refers to the *input*,
        # while the current texture coordinate in the fshader refers to an *output* pixel. For full-resolution
        # input and div=2, the center of each output pixel is placed exactly at the midway point
        # between the centers of four pixels of the input.
        #
        # Therefore, when a texture lookup is made *at the center of the output pixel*, the GPU combines
        # *the four input values* automatically using linear interpolation. We obtain the desired
        # linear interpolation, because Texture.FTLinear is the default Minfilter and
        # FilterUtils.createFilterTexture() (which is used by Filter.createInternalTextures())
        # does not change it; see
        #
        #   https://www.panda3d.org/manual/index.php/Texture_Filter_Types
        #
        #
        # The "align" parameter makes FilterManager round the window resolution numbers up to the next
        # integer multiple of "scale" before applying the division when computing the target texture size.
        #
        # This ensures that any last "leftover" pixel rows/columns (the remainder from division by "scale")
        # will also be represented in the target texture, although they have less than the usual number
        # of input pixels corresponding to them.
        #
        # The U and V wrap modes are set to Texture.WMClamp (again by FilterUtils.createFilterTexture());
        # thus the last row/column will be appropriately repeated in the downscale and blurring operations
        # (when these operations attempt to access pixels outside the input texture).
        #
        # TODO/FIXME: Doing this correctly for padded textures requires additional logic
        # TODO/FIXME: in the shader kernels themselves. The current kernels simply access pixels
        # TODO/FIXME: that belong to the padding, which is incorrect. Any texture coordinates used for
        # TODO/FIXME: lookups should be clamped to  2.0*texpad_src.xy - 0.5*texpix_src.xy  in each shader;
        # TODO/FIXME: the idea is that the last accessible position is the center of the last row/column.
        # TODO/FIXME: (The center, so that the lookup will not mix in any color from the padding.)
        # TODO/FIXME:
        # TODO/FIXME: This would make the shaders more complex, though, and almost everyone uses
        # TODO/FIXME: non-padded textures nowadays (by setting "textures-power-2 none" in Config.prc),
        # TODO/FIXME: so I'm not sure if the added complexity is worth the marginal compatibility gain.
        #
        self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["bloom0"], div=2, align=scale))
        self.interQuads[0].setShaderInput("src", self.getTextureInfo("color").get('texture'))

        # The first internal stage produces a quarter-resolution texture "bloom0".
        # Consider the downscale stage, which receives "bloom0" as input:
        #
        #  - If scale=2, we are already at the final target resolution. We can skip this step.
        #
        #  - If scale=4, we must scale down by another quarter-resolution step.
        #
        #    We can do this by copying from the quarter-resolution (div=2) "bloom0"
        #    into a 16th-resolution (div=4) texture. Then the center of each output pixel will be
        #    again located exactly at the midway point between the centers of four input pixels,
        #    and we obtain the desired linear interpolation with the "filter-copy.sha" kernel.
        #
        #  - Only if scale=8, we must combine pixels manually, to directly produce a 64th-resolution (div=8)
        #    texture from the quarter-resolution "bloom0". This is where "filter-down4.sha" comes in.
        #
        #    Each pixel in the div=8 texture corresponds to a 4x4 block of pixels in the div=2 texture
        #    (this is the same situation as it would be for div=4 output with full-resolution input).
        #
        #    The downscaler looks *one input pixel* away from the current output pixel center
        #    in the NW, NE, SW, SE directions, and combines the results. Each lookup averages 4 pixels
        #    (a 2x2 block; each different). In total, this averages all 16 pixels in the 4x4 block.
        #
        #
        # Observe that the output from the downscale stage is always at the final target texture resolution.
        # This simplifies the last two stages, as they do not have to consider any resolution changes.
        #
        # The last two stages then apply blurring, always using the final target texture resolution
        # both in their input (which, for the x blur, is the output from the downscale stage;
        # and for the y blur, the output from the x blur stage) and in their output.
        #
        # All internal stages use the same value of "align" (namely "scale"), so that any remainder
        # rows/columns from the final division by "scale" will be represented throughout the whole process.
        # This is important to correctly process the right and lower edges in case the window size
        # is not divisible by "scale".

        # In setShaderInput(), we can use self.getTextureInfo("bloom0").get('texture') or self.get('texture')["bloom0"].
        # They refer to the same texture, because we have created an internal texture "bloom0"
        # (and thus the name lookup will not proceed to filters earlier in the same FilterStage).
        #
        # It is recommended to use self.getTextureInfo(texName).get('texture'), because that is the correct way
        # to access any available texture, whereas self.get('texture')[texName] relies on an implementation detail,
        # and is valid only for those textures that were created internally in this particular filter instance.
        #
        if self._downsampler is not None:
            self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["bloom1"], div=scale, align=scale))
            self.interQuads[1].setShaderInput("src", self.getTextureInfo("bloom0").get('texture'))

            self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["bloom2"], div=scale, align=scale))
            self.interQuads[2].setShaderInput("src", self.getTextureInfo("bloom1").get('texture'))

            self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["bloomOutput"], div=scale, align=scale))
            self.interQuads[3].setShaderInput("src", self.getTextureInfo("bloom2").get('texture'))

        else:  # skip additional downsampling step (note that in this case, scale=2)
            self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["bloom1"], div=scale, align=scale))
            self.interQuads[1].setShaderInput("src", self.getTextureInfo("bloom0").get('texture'))

            self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["bloomOutput"], div=scale, align=scale))
            self.interQuads[2].setShaderInput("src", self.getTextureInfo("bloom1").get('texture'))

    def onDetachStage(self):
        # self.interQuads and self.get('texture') are cleaned up by detachStage() automatically.
        #
        self._downsampler = None

    def onCompileInternalStages(self):
        # Compile/load shaders of internal stages.
        #
        if self._downsampler is not None:
            self.interQuads[0].setShader(self.loadShader("filter-bloomi.sha"))
            self.interQuads[1].setShader(self.loadShader(self._downsampler))
            self.interQuads[2].setShader(self.loadShader("filter-bloomx.sha"))
            self.interQuads[3].setShader(self.loadShader("filter-bloomy.sha"))
        else:
            self.interQuads[0].setShader(self.loadShader("filter-bloomi.sha"))
            self.interQuads[1].setShader(self.loadShader("filter-bloomx.sha"))
            self.interQuads[2].setShader(self.loadShader("filter-bloomy.sha"))

    def onSynthesizeCompositor(self):
        txbloom = self.getTextureInfo("bloomOutput")
        code  = "pixcolor = saturate(pixcolor);\n"
        code += "float4 bloom = 0.5 * tex2D(%(k_txbloom)s, %(texcoord_txbloom)s);\n" % { "k_txbloom"        : txbloom.get('varname'),
                                                                                         "texcoord_txbloom" : txbloom.get('texcoord') }
        code += "pixcolor = 1.0 - ((1.0 - bloom)*(1.0 - pixcolor));\n"
        return ("bloom", code, "// Bloom blend pass\n")


    # The internal shader parameters "blend", "trigger" and "intensity" do not map directly to the user-given
    # parameter values, but need additional calculations to produce the values actually used in the shader.
    #
    # This is implemented in the _compute*() private methods.
    #
    def _computeBlendInput(self):
        value = self._blend
        return Vec4(value[0], value[1], value[2], 2.0*value[3])

    def _computeTriggerInput(self):
        if self._maxtrigger <= self._mintrigger:
            raise ValueError("maxtrigger must be > mintrigger; currently: mintrigger = %g, maxtrigger = %g" % (self._mintrigger, self._maxtrigger))
        return Vec4(self._mintrigger, 1.0/(self._maxtrigger - self._mintrigger), 0.0, 0.0)

    def _computeIntensityInput(self):
        value = 3.0 * self._intensity
        return Vec4(value, value, value, value)


    @property
    def blend(self):
        """The bloom filter needs to measure the brightness of each pixel. It does this by
        weighting the R,G,B and A components. Default weights: (0.3, 0.4, 0.3, 0.0).

        You should assign a nonzero weight to the alpha channel if you want the glow map
        to have an effect, or a value like (0, 0, 0, 1) if you only want your glow map
        to indicate which parts of a model should glow.

        """
        return self._blend
    @blend.setter
    def blend(self, value):
        self._blend = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "blend", self._computeBlendInput() )

    @property
    def mintrigger(self):
        """Minimum brightness at which a halo is generated. Float, default 0.6."""
        return self._mintrigger
    @mintrigger.setter
    def mintrigger(self, value):
        self._mintrigger = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "trigger", self._computeTriggerInput() )

    @property
    def maxtrigger(self):
        """Maximum brightness at which the halo reaches peak intensity. Float, default 1.0."""
        return self._maxtrigger
    @maxtrigger.setter
    def maxtrigger(self, value):
        self._maxtrigger = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "trigger", self._computeTriggerInput() )

    @property
    def desat(self):
        """Degree to which the halo is desaturated. Float, in [0, 1]. Default 0.6.

        Setting this to zero means the halo is the same color as the bright pixel.
        Setting this to one means the halo is white.

        """
        return self._desat
    @desat.setter
    def desat(self, value):
        self._desat = value
        if len(self.interQuads)  and  self.interQuads[0] is not None:
            self.interQuads[0].setShaderInput( "desat", value )

    @property
    def intensity(self):
        """An adjustment parameter for the brightness of the halos. Float, default 1.0."""
        return self._intensity
    @intensity.setter
    def intensity(self, value):
        self._intensity = value
        # This parameter goes to the last internal stage (y direction blur).
        if len(self.interQuads)  and  self.interQuads[-1] is not None:
            self.interQuads[-1].setShaderInput( "intensity", self._computeIntensityInput() )

    @property
    def size(self):
        """Halo size. One of Bloom.SIZES ("small", "medium" [default] or "large").

        Controls the distance how far the halo effect reaches out from each blooming pixel.

        This is a discrete value instead of a continuous one, because the blur operation used
        internally in the bloom effect involves downsampling the original image by a power of two.

        """
        return self._size
    @size.setter
    def size(self, value):
        # Changing this parameter may change texture scalings for our internal textures
        # (and the number of internal stages, too!), so we recompile the whole pipeline.
        #
        if (not hasattr(self, "_size")  or  value != self._size)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._size = value

