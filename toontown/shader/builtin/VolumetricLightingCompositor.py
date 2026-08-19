from panda3d.core import Vec4, Point2

from toontown.shader.Filter import Filter

# This is the compositing fshader code. See onSynthesizeCompositor().
#
VL_BODY="""float decay = 1.0f;
float2 curcoord = %(texcoord_txsource)s;
float2 lightdir = curcoord - %(k_casterpos)s.xy;
lightdir *= %(k_vlparams)s.x;
half4 sample = pixcolor;  // The initial sample value always comes from the color texture.
float3 vlcolor = sample.rgb * sample.a;
for (int i = 0; i < %(numsamples)d; i++) {
    curcoord -= lightdir;
    sample = tex2D(%(k_txsource)s, curcoord);
    sample *= sample.a * decay;//*weight
    vlcolor += sample.rgb;
    decay *= %(k_vlparams)s.y;
}
pixcolor += %(k_vlparams)s.w * float4(vlcolor * %(k_vlparams)s.z, 1);
"""


class VolumetricLightingCompositor(Filter):
    """A volumetric lighting ("god rays") filter.

    This filter implements the calculation of the light rays and the compositing step,
    given an input glow texture (such as the last internal texture of Bloom).
    If used on the color texture directly, this will just blur radially,
    centered on the caster's position on the screen.

    Algorithm as explained in NVIDIA: GPU Gems 3, chapter 13, Volumetric Light Scattering as a Post-Process.

    """

    def __init__(self, **kwargs):
        super(VolumetricLightingCompositor, self).__init__(**kwargs)


    def onReset(self):
        super(VolumetricLightingCompositor, self).onReset()

        self._dstrength = 1.0  # "directional strength" factor; used in onUpdate()

        self.isMergeable = False
        self.stageName = "SceneOptics"
        self.sort = 60  # this should come after AmbientOcclusion, but can be done in the same render pass.

        self.caster     = None  # no sensible default possible
        self.source     = "color"
        self.numsamples = 32
        self.density    =  0.6
        self.decay      =  0.98
        self.exposure   =  0.1

    def onAttachPipeline(self):
        self.registerCustomInput(inputType="float4", inputName="k_casterpos")
        self.registerCustomInput(inputType="float4", inputName="k_vlparams")

        # The default is "color", like was the only option in old versions.
        #
        # An alternative is e.g. "bloomOutput"; FilterStage will look it up for us when we getTextureInfo()
        # in the code synthesis.
        #
        # The only requirement for using "bloomOutput" is that then a bloom filter must be placed
        # earlier in the same stage. (Respectively, any internal texture, any filter providing it.
        #
        # In case of multiple filters defining a texture with the same name, the most recent definition
        # (in sort order, starting backward from the point where VolumetricLighting itself is placed)
        # masks any earlier ones.)
        #
        self.registerInputTexture(texName=self.source)

        # Filters defining onUpdate() must register themselves as "updatable", which means
        # onUpdate() will actually get called.
        #
        self.registerUpdatable()


    def onSynthesizeCompositor(self):
        txsource = self.getTextureInfo(self.source)

        code = VL_BODY % { "texcoord_txsource" : txsource.get('texcoord'),
                           "k_txsource"        : txsource.get('varname'),
                           "k_casterpos"       : self.getMangledName("k_casterpos"),
                           "k_vlparams"        : self.getMangledName("k_vlparams"),
                           "numsamples"        : self.numsamples }

        return ("volumetricLightingCompositor",
                code,
                "// Volumetric lighting\n")


    def onUpdate(self):
        # Update shader inputs that need to be updated each frame.
        #
        # This only gets called while the filter is running
        # (so self.pipeline and self.finalQuad are always valid here).

        # TODO: we could by default set the caster at the camera's origin, causing a radial blur effect?
        if self.caster is None:
            raise ValueError("VolumetricLightingCompositor needs a caster, but caster=None. See the documentation.")

        cam = self.pipeline.manager.camera
        caster3DPos = self.caster.getPos(cam)
        caster2DPos = Point2()
        cam.node().getLens().project(caster3DPos, caster2DPos)
        # TODO: how to account for texpad? caster2DPos is in coordinates of the finalQuad i.e. [-1,1]x[-1,1],
        # TODO: and we want a value in texture coordinates, inside the used part of the texture.
        casterTexturePos = Vec4(caster2DPos.getX() * 0.5 + 0.5,
                                caster2DPos.getY() * 0.5 + 0.5,
                                0, 0)
        self.finalQuad.setShaderInput( self.getMangledName("casterpos"), casterTexturePos )

#        # Implement an artifact-reducing suggestion from GPU Gems 3, section 13.6:
#        #
#        # Fade out the volumetric rays as the light approaches the plane perpendicular
#        # to the view axis. This eliminates the problem of potentially large sample separation,
#        # as the coordinates of the light tend to infinity on the camera plane. Without this,
#        # if the light is on the camera plane, and far away from the view, the separation
#        # between adjacent samples will be large and the "ray" effect breaks down.
#        #
#        # Basically, self._dstrength is based on the directional cosine between the view axis
#        # and caster3DPos. Negative values correspond to the light being behind the camera.
#        # We clip to nonnegative values and take the resulting value squared.
#        #
#        vecnorm = sqrt(caster3DPos.dot(caster3DPos))
#        self._dstrength = max(0.0, Vec3(0,1,0).dot(caster3DPos/vecnorm))**2
#        self.finalQuad.setShaderInput( self.getMangledName("vlparams"), self._computeVlparams() )


    # This private method maps run-time parameter values to actual shader input values.
    #
    def _computeVlparams(self):
        tcparam = self._density / float(self._numsamples)
        return Vec4(tcparam, self._decay, self._exposure, self._dstrength)


    @property
    def caster(self):
        """NodePath that indicates the origin of the rays. Usually, you would pass your light,
        and create a sun billboard which is reparented to the light's NodePath.

        The billboard should be centered on the light's origin to correctly represent
        the light source. This is important because the rays shine outward from the
        origin of the caster NodePath (your light).

        There is no default value for this parameter.

        """
        return self._caster
    @caster.setter
    def caster(self, value):
        # This is queried by update(), so we don't need to do anything except store the new value.
        self._caster = value


    @property
    def source(self):
        """Source texture for the light rays.

        The default is "color", which is not very sensible, although it does enable to use VolumetricLighting
        as a radial blur filter (with the origin of the blur set using the "caster" parameter).

        A better setup is to use a bloom filter as a preprocessor. Create a bloom filter,
        with enableRender=False (so that its output will not be composited onto the final image),
        and add it to the same stageName (as your VolumetricLighting) with a smaller sort.
        Then, the bloom filter's internal textures - including "bloomOutput" - become available as a source
        for VolumetricLightingCompositor. This makes it possible to use the glow map to specify
        which parts of the image should cast light rays (e.g. the sun billboard can have glow=1.0
        across the whole region).

        See the VolumetricLighting filter (which packages Bloom and VolumetricLightingCompositor
        into one filter as a compound), and setVolumetricLighting() in CommonFilters for examples.

        """
        return self._source
    @source.setter
    def source(self, value):
        # We must recompile the pipeline, because changing "source" affects texture registration
        # and the code generation of the compositing shader.
        #
        if (not hasattr(self, "_source")  or  value != self._source)  and  self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._source = value


    @property
    def numsamples(self):
        """Number of samples used to trace the light rays (default: 32).

        The more samples you use, the slower the effect will be, but you will have smoother light rays.
        Note that using a fuzzy billboarded dot instead of a hard-edged sphere as light caster can help
        with smoothing the end result. So does the use of the bloom filter as a preprocessor (see "source").

        This value does not need to be a power-of-two, it can be any positive number.

        """
        return self._numsamples
    @numsamples.setter
    def numsamples(self, value):
        # We must recompile the code because numsamples is used as a loop limit, and loop limits must be
        # constants in the arbfp1 profile.
        #
        if (not hasattr(self, "_numsamples")  or  int(value) != self._numsamples)  and  self.pipeline is not None:
            self._needsCompile = True
        self._numsamples = int(value)

        # Beside code generation, numsamples affects also the "vlparams" shader input.
        # This allows us to pass a precomputed step parameter, saving an instruction in the shader.
        #
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("vlparams"), self._computeVlparams() )


    @property
    def density(self):
        """Affects the length of the rays (default: 0.6).

        Usually a value between 0.5 and 1.0 works best. However, the best value for each particular case
        also depends on the values chosen for "numsamples" and "exposure".

        The default has changed in version 1.9.0; the backward-compatible CommonFilters API
        uses the old default value of 5.0, which is much too high for most cases.

        """
        return self._density
    @density.setter
    def density(self, value):
        self._density = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("vlparams"), self._computeVlparams() )


    @property
    def decay(self):
        """Affects how fast the rays decrease in brightness as they travel.

        Float, in interval (0,1). Smaller values make the rays decay faster (this acts as a damping coefficient).
        Usually, this should be a value close to 1.0, like 0.98 (default).

        The default has changed in version 1.9.0; the backward-compatible CommonFilters API
        uses the old default value of 0.1, which is much too low for most cases.

        """
        return self._decay
    @decay.setter
    def decay(self, value):
        self._decay = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("vlparams"), self._computeVlparams() )


    @property
    def exposure(self):
        """Defines the brightness of the rays (default 0.1)."""
        return self._exposure
    @exposure.setter
    def exposure(self, value):
        self._exposure = value
        if self.finalQuad is not None:
            self.finalQuad.setShaderInput( self.getMangledName("vlparams"), self._computeVlparams() )

