from toontown.shader.Filter import Filter


# A filter with internal stages.
#
class BlurSharpen(Filter):
    """A blur/sharpen filter. If the 'amount' parameter is 1.0, the filter will have no effect.
    A value of 0.0 means fully blurred, and a value higher than 1.0 (up to 2.0) sharpens the image."""

    SIZES = ["xsmall", "small", "medium", "large"]

    def __init__(self, **kwargs):
        super(BlurSharpen, self).__init__(**kwargs)

        # super's init will call cleanup(), which will call detach(), which triggers setdown(),
        # so we don't need to set self._downsampler here.

    def onReset(self):
        super(BlurSharpen, self).onReset()
        self.sort = 0  # first within the pipeline stage (right after init)
                       # (the blur filter overwrites pixcolor; "sort=0" is a strong hint of this to the user)

        # The input texture for the blur filter must see all previous changes;
        # hence this is not mergeable, and must come at an appropriate point
        # in the simulated image-forming process.
        #
        self.stageName   = "LensFocus"
        self.isMergeable = False

        self.amount = 0.0  # full strength
        self.size   = "medium"

        self.source = "color"

    def onAttachPipeline(self):
        # Our compositing fshader wants to blend between the original color texture provided
        # by FilterStage, and the internal blur1 texture set up here during FilterStage attach
        # (i.e. the output texture of the last internal stage).
        #
        # Register the "blurOutput" texture as an input texture to the compositing fshader
        # (in the FilterStage where this filter happens to be assigned), so that the code
        # provided in synthesize() will have access to it.
        #
        # We do not need to register the "color" texture, as our code does not access it explicitly,
        # and does not need its texture coordinate, either. From the color texture, we only need the
        # color of the current pixel, which is provided in pixcolor.
        #
        self.registerInputTexture(texName="blurOutput")

        # Our compositing fshader also has a custom input to control the strength of the blur effect.
        #
        # Note that registration only requests FilterStage to write the code to pass in this input;
        # we still need to create a property and make its setter update the shader input "blur_amount"
        # (stripping the "k_" prefix).
        #
        self.registerCustomInput(inputType="float", inputName="k_blur_amount")

    def onAttachStage(self):
        # Create interQuads for internal stages.
        #
        # Any setup-time parameters for the internal stages are applied here.
        # Usually this means configuring input and output textures to set up an internal pipeline.
        #
        # Note that the output texture for each interQuad is chosen in the call to renderQuadInto().
        # It must be an internal texture; only the compositing fshader can render to the final output.

        if self.size == "large":
            scale = 4
            self._downsampler = "filter-down4.sha"
        elif self.size == "medium":
            scale = 2
            self._downsampler = "filter-copy.sha"
        else: # self.size == "small"  or  self.size == "xsmall":
            scale = 1
            self._downsampler = None

        # Create a quad that outputs to texture "blur0". Connect its shader input named "src"
        # to the input color texture provided to us by the FilterStage this filter is attached to.
        #
        # It doesn't matter that the shader hasn't been created yet. Shader inputs are NodePath attributes,
        # so when we assign a shader later, the input named "src" will magically become available.
        # (It is then up to the shader code to actually use the input having that name.)
        #
        # Note that shader inputs for internal shaders are not registered to FilterStage;
        # the registration mechanism only concerns code generation of the compositing fshader.
        #
        #
        # We apply prescaling for the larger sizes.
        #
        # For example for "medium", we use div=2 to make a quarter-resolution texture relative to the
        # resolution of the window.
        #
        # This is good enough for blur, and usually renders much faster due to much fewer fshader calls.
        # It also increases the blur radius in a computationally cheap way. It is easier to make the
        # quarter-resolution texture first, and apply the blur shaders after that. This simplifies
        # the blur shaders, because then they never need to do any scaling (input and output resolutions
        # are the same).
        #
        # Note also that for this setup, the center of each output pixel (of this first internal stage)
        # is placed exactly at the midway point between the centers of four pixels of the input.
        # We use this to downsample the input to quarter resolution before applying the actual blur passes.
        #
        # Thus, when "filter-copy.sha" reads the texture at whole-pixel offsets (where the pixel size
        # refers to the *input*, while the current texture coordinate refers to an *output* pixel),
        # it will get values interpolated from four input pixels for each texture fetch;
        # thus the "copy" will actually be an interpolated downscale to quarter resolution.
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
        if scale != 1:  # pre-downscaling needed?

            # Create output textures for internal stages.
            #
            self.createInternalTextures( "blur0", "blur1", "blurOutput" )

            self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["blur0"], div=scale, align=scale))
            self.interQuads[0].setShaderInput("src", self.getTextureInfo(self.source).get('texture'))

            # Create a quad that outputs to texture "blur1". Connect its shader input named "src"
            # to the texture "blur0" (which is the output texture of the previous step).
            #
            # This also uses the same smaller resolution, with respect to the window size,
            # as "blur0" (note div=scale for both quads).
            #
            self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["blur1"], div=scale, align=scale))
            self.interQuads[1].setShaderInput("src", self.getTextureInfo("blur0").get('texture'))

            # Similar setup for "blurOutput".
            #
            self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["blurOutput"], div=scale, align=scale))
            self.interQuads[2].setShaderInput("src", self.getTextureInfo("blur1").get('texture'))

        else:  # no pre-downscaling needed

            if self.size == "small":
                # Create output textures for internal stages.
                #
                self.createInternalTextures( "blur0", "blurOutput" )

                self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["blur0"]))
                self.interQuads[0].setShaderInput("src", self.getTextureInfo(self.source).get('texture'))

                self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["blurOutput"]))
                self.interQuads[1].setShaderInput("src", self.getTextureInfo("blur0").get('texture'))

            else:  # self.size == "xsmall":
                self.createInternalTextures( "blurOutput" )

                self.interQuads.append(self.pipeline.manager.renderQuadInto(colortex=self.get('texture')["blurOutput"]))
                self.interQuads[0].setShaderInput("src", self.getTextureInfo(self.source).get('texture'))


    def onDetachStage(self):
        # self.interQuads and self.get('texture') are cleaned up by detachStage() automatically.
        #
        self._downsampler = None


    def onCompileInternalStages(self):
        # Compile and assign shaders for internal stages.
        #
        if self._downsampler is not None:
            self.interQuads[0].setShader(self.loadShader(self._downsampler))
            self.interQuads[1].setShader(self.loadShader("filter-blurx.sha"))
            self.interQuads[2].setShader(self.loadShader("filter-blury.sha"))
        else:
            if self.size == "small":
                self.interQuads[0].setShader(self.loadShader("filter-blurx.sha"))
                self.interQuads[1].setShader(self.loadShader("filter-blury.sha"))
            else:  # self.size == "xsmall":
                self.interQuads[0].setShader(self.loadShader("filter-blursmall.sha"))


    def onSynthesizeCompositor(self):
        txblur = self.getTextureInfo("blurOutput")
        k_blur_amount = self.getMangledName("k_blur_amount")
        code = "pixcolor = lerp(tex2D(%(k_txblur)s, %(texcoord_txblur)s.xy), pixcolor, %(k_blur_amount)s.x);\n" % \
                   { "k_txblur"        : txblur.get('varname'),
                     "texcoord_txblur" : txblur.get('texcoord'),
                     "k_blur_amount"   : k_blur_amount }
        return ("blurSharpen", code, "// Blur/sharpen blend pass\n")


    @property
    def amount(self):
        """Effect strength, float. 0 is full strength; 1 is "do nothing". Values in [0,1) blur, values in (1,2] sharpen."""
        return self._amount
    @amount.setter
    def amount(self, value):
        self._amount = value
        if self.finalQuad is not None:
            # This input goes to the compositing shader, so we must mangle the name, but without the k_ prefix,
            # to get the unique name of the *shader input*.
            #
            self.finalQuad.setShaderInput( self.getMangledName("blur_amount"), value )


    @property
    def size(self):
        """Blur/sharpen kernel size. One of BlurSharpen.SIZES ("xsmall", "small", "medium" [default] or "large").

        Introduced in 1.9.0.

        This is a discrete value instead of a continuous one, because the blur operation
        involves downsampling the original image by a power of two.

        For sharpening the image, smaller sizes may look better.

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


    @property
    def source(self):
        """Name of source texture.

        Can be either "color" [default], or the name of an internal texture defined by
        another filter placed earlier (with a smaller sort value) in the same FilterStage.

        The default "color" blurs the scene. This is the most common use case.

        Note that in any case BlurSharpen's compositor effectively replaces the current
        "color" texture by a blurred/sharpened version of the source texture.

        Setting this to a non-default value is mainly useful for compound filters
        using BlurSharpen as a component (in which case they typically define
        their own compositor).

        """
        return self._source
    @source.setter
    def source(self, value):
        if (not hasattr(self, "_source")  or  value != self._source)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._source = value

