"""FilterStage: one render pass in FilterPipeline. This is part of the postprocessing filter system."""



from panda3d.core import NodePath, Shader, ATSNone

from toontown.shader.Filter import Filter, SCENETEXTURES
from toontown.shader.CompoundFilter import CompoundFilter

# Note: if we needed to import FilterPipeline in this module, we would need to be careful,
# because FilterPipeline imports us. See comment about loading order in Filter.py.

# MiscFilters contains StageInitializer, but it imports us. Same caution here.
# (We only need to import this for a run-time isinstance() check; the rest relies on duck typing.)
#
from toontown.shader.StageInitializer import StageInitializer

from toontown.shader import FilterUtils


class FilterStage(object):
    """Single render pass. Several FilterStages together make up a FilterPipeline."""

    def __init__(self, pipeline, name=None):
        """Constructor.

        Parameters:
            pipeline = FilterPipeline instance where this FilterStage instance belongs to.

            name     = Optional human-readable name for this FilterStage. Used in error messages and ls().

        """
        super(FilterStage, self).__init__()

        self.filters = []  # must exist before cleanup() is called
        self.cleanup()
        self.pipeline = pipeline  # FilterPipeline instance

        if name is not None:
            self.name = name
        else:
            self.name = "instance at 0x%x" % id(self)


    def __del__(self):
        """Destructor."""
        self.cleanup()


    def ls(self, indent=0):
        """Print a human-readable description of this FilterStage instance into the terminal."""
        ind = (indent * " ")
        nf  = len(self.filters)
        hpsStatus = ", HalfPixelShift enabled" if self.halfPixelShift else ""

        if nf < 1:
            print(("%sFilterStage %s: <no filters%s>" % (ind, self.name, hpsStatus)))
        else:
            # Even with only HalfPixelShift, there is always the StageInitializer.

            fplural = "s" if nf != 1 else ""
            print(("%sFilterStage %s: <%d filter%s%s>" % (ind, self.name, nf, fplural, hpsStatus)))

            if len(self.registeredTextures) > 0:
                # Find out which filters enabled which textures
                # (in general, several filters may enable the same texture)
                #
                texToFilters = {}
                for f in self.filters:
                    if f not in self.registeredTextures:
                        continue
                    # needTexpix and metaOnly are currently not reported in ls(). (internalOnly is handled below)
                    for texName in self.registeredTextures[f]:
                        if texName not in texToFilters:
                            texToFilters[texName] = []
                        texToFilters[texName].append( f )

                # sort by texture name for human-readability; add list of filters that registered each texture
                textureslist = []
                for texName in sorted(texToFilters.keys()):
                    filternames = [ "%s %s" % (f.__class__.__name__, f.name) for f in texToFilters[texName] ]
                    textureslist.append( "%s (reg. by %s)" % (texName, filternames) )

                if len(textureslist) > 0:
                    print(("%s  Textures registered to compositing shader: %s" % (ind, textureslist) ))
                else:
                    print(("%s  No textures registered to compositing shader" % ind ))

            if len(self.registeredCustomInputs) > 0:
                # These are uniquely named, so each custom input corresponds only to one filter.
                #
                inputsByName = {}
                for f in self.filters:
                    if f not in self.registeredCustomInputs:
                        continue
                    for item in self.registeredCustomInputs[f]:  # item is a CustomInputMetadata
                        inputsByName[item.get('inputName')] = "%s %s (reg. by ['%s %s'])" % (item.get('inputType'),
                                                                                      item.get('inputName'),
                                                                                      f.__class__.__name__,
                                                                                      f.name)

                # sort by input name for human-readability
                inputslist = []
                for key in sorted(inputsByName.keys()):
                    inputslist.append( inputsByName[key] )

                print(("%s  Custom inputs registered to compositing shader: %s" % (ind, inputslist) ))

            for f in self.filters:
                f.ls(indent=indent+4)


    def cleanup(self):
        """Cleanup function. Deletes any dynamically created state."""
        # This function must not raise exceptions; it may be called in response to exceptions.

        # Detach the Filters from the FilterStage.
        for f in self.filters:
            f.detachStage()
        self.filters  = []
        self.pipeline = None

        self.finalQuad = None  # the output quad of this FilterStage (not necessarily of the whole pipeline)
        self.stageInputTextures = {}  # input "scene textures" obtained from the pipeline

        # per-filter input parameters
        #
        self.registeredTextures       = {}
        self.registeredCustomInputs   = {}

        # run-time onUpdate() functions defined by filters
        #
        self.updateFunctions = {}

        # general FilterStage-level parameters
        #
        self._halfPixelShift = False
        self._shaderSourceCode = None
        self._shaderObj = None
        self._texcoords = {}  # key: texture name, value: texcoord variable name


    # Note: shaders of internal stages do *not* need to support HalfPixelShift, because *the compositing shader*
    # will apply the shift when reading in the registered textures created by the internal shaders.
    #
    # E.g. the data in the original "color" texture is non-shifted anyway, so any internal textures computed
    # from it should be, too. Then, in the compositing shader, when both "color" and those internal textures
    # are read using the same shift value, we get consistent data.
    #
    @property
    def halfPixelShift(self):
        """Bool. If True, shift the output of this FilterStage by half a pixel in both x and y directions. Default False."""
        # This is actually implemented by shifting the *input* to the compositing shader, but as a description
        # of how it affects the output, the above is correct, and potentially less worrying ("but will it
        # consider my internal stages?").
        #
        return self._halfPixelShift
    @halfPixelShift.setter
    def halfPixelShift(self, value):
        oldValue = self._halfPixelShift
        self._halfPixelShift = value
        if value != oldValue:
            if self.pipeline is not None:
                self.pipeline._needsCompile = True


    def getTextureInfo(self, texName, caller=None):
        """Obtain a texture object reference (and some metadata) by texture name.

        The textures are looked up as follows:

            a) If texName specifies a valid scene texture (is one of Filter.SCENETEXTURES),
               input scene textures provided to this FilterStage.

               (Be sure to call connectInput() first before querying for scene textures.)

            b) Otherwise, internal textures of Filters placed in this FilterStage.

               The filter list is walked backwards, so that when the filters are in sorted order,
               in case of duplicate texture names, the latest definition wins.

               If "caller" is provided and is a filter in this FilterStage, the search starts there,
               and any filters later than it are ignored. In this case, the "most recent" definition
               (as seen from caller) wins.

        Any textures defined in earlier FilterStages are considered as being out of date
        and cannot be retrieved.

        Parameters:
            texName = string. Name of the texture to retrieve, e.g. "color", "bloomOutput", ...

            caller  = Filter instance (that must be in this FilterStage) or None.
                      Starting point of name resolution; if provided, any internal textures provided
                      by Filters later than this are ignored.

        Return value:
            Named tuple of type Filter.TextureInfo:

              (varname, suffix, texpix, texpad, texcoord, texture, owner)

            where

              varname   = Name of the sampler2D variable, as it appears in the code (mangled, and with k_tx prefix),
                          or None if this texture not registered into the compositing shader.

              texpix    = Name of the variable holding the corresponding texpix in the compositing shader,
                          or None if this texture not registered into the compositing shader.

              texpad    = Name of the variable holding the corresponding texpad in the compositing shader,
                          or None if this texture not registered into the compositing shader.

                          If the texture is not padded, this will be the constant "float2(0.5, 0.5)"
                          instead of an actual variable name.

              texcoord  = Name of the variable holding the corresponding texcoord in the compositing shader,
                          or None if this texture not registered into the compositing shader

              texture   = Reference to the Texture object

              owner     = If texRef is a texture defined in a Filter (an internal stage texture):
                            Filter reference to the filter that defines the texture.
                          If texRef is a scene texture:
                            owner = None.

        If no texture named texName is seen by caller (or, if caller is None, no texture named
        texName is found anywhere in this FilterStage), raises ValueError.

        """
        # Input scene textures provided to this FilterStage.
        #
        # (Only those listed in SCENETEXTURES are valid scene textures.)
        #
        if texName in SCENETEXTURES:
            if texName in self.stageInputTextures:
                tex = self.stageInputTextures[texName]

                # self._texcoords is only populated for textures that have been registered for compositing.
                #
                # Note also that it becomes populated just after filters are attached to the FilterStage
                # and just before compositing shader synthesis begins; see FilterStage.reconfigure().
                #
                # Thus, at attach time, it is not yet populated.
                if texName in self._texcoords:
                    # Do the same optimization as in vshader synthesis (see FilterStage.reconfigure()):
                    # use the texture padding variable only if the texture is actually padded.
                    #
                    # (Here it is actually much more important to do this than in the vshader; the vshader
                    #  runs only a few times (for the corners of the fullscreen quad), while the fshader
                    #  runs once for each pixel.)
                    #
                    texPadded = (tex.getAutoTextureScale() != ATSNone)
                    texCenter = "texpad_tx%s" % (texName) if texPadded else "float2(0.5, 0.5)"

                    return {'varname': "k_tx%s"      % (texName),
                                        'texpix': "texpix_tx%s" % (texName),
                                        'texpad': texCenter,
                                        'texcoord': self._texcoords[texName],
                                        'texture': tex,
                                        'owner': None }  # owner=None  =  texture not defined in a Filter
                else:
                    # Scene texture that is required from FilterPipeline (by a Filter in this FilterStage),
                    # but not registered for compositing (in this FilterStage). (Or we are being called
                    # at attach time.)
                    #
                    # Our metadata refers to the variable names in the compositing shader,
                    # so we leave them blank in this case.
                    #
                    # Note that each Filter manually sets up the inputs of its internal stages,
                    # and can name its texcoord/texpix/texpad variables whatever it wants.
                    #
                    # Also, at attach time, the Filter is typically only interested in the texture
                    # object reference (which is typically needed to send it to an internal shader input).
                    #
                    return {'varname': None,
                                        'texpix': None,
                                        'texpad': None,
                                        'texcoord': None,
                                        'texture': tex,
                                        'owner': None } # owner=None  =  texture not defined in a Filter
            else:
                raise ValueError("In stage '%s': scene texture '%s' not present" % (self.name, texName))

        # Internal textures defined in Filters.
        #
        if caller is None:
            # No caller specified - look in all filters.
            start = -1
        elif caller in self.filters:
            # Look only in caller and any earlier filters.
            start = self.filters.index(caller)
        else:
            raise ValueError("In stage '%s': specified caller '%s' (%s) is not present in this FilterStage" % (self.name, caller.__class__.__name__, caller.name))

        # Name masking: look backwards so that the most recent definition wins
        # in case of duplicate texture names (defined in different filters).
        #
        for f in self.filters[start::-1]:
            if texName in f.get('texture'):
                tex = f.get('texture')[texName]  # non-mangled name here!
                mangledTexName = f.getMangledName(texName)

                # Same observations about registered textures, and about attach time behavior, as above.
                if mangledTexName in self._texcoords:
                    texPadded = (tex.getAutoTextureScale() != ATSNone)
                    texCenter = "texpad_tx%s" % (mangledTexName) if texPadded else "float2(0.5, 0.5)"

                    return {'varname': "k_tx%s"      % (mangledTexName),
                                        'texpix': "texpix_tx%s" % (mangledTexName),
                                        'texpad': texCenter,
                                        'texcoord': self._texcoords[mangledTexName],
                                        'texture': tex,
                                        'owner': f }
                else:
                    # Internal texture defined by a Filter, but not registered for compositing.
                    # (Or we are being called at attach time.)
                    #
                    # The typical use case is to call getTextureInfo() in Filter.onAttachStage() to obtain
                    # just the texture object reference (to send it to an input of an internal stage shader).
                    #
                    return {'varname': None,
                                        'texpix': None,
                                        'texpad': None,
                                        'texcoord': None,
                                        'texture': tex,
                                        'owner': f }

        if caller is None:
            raise ValueError("In stage '%s': texture '%s' not present" % (self.name, texName))
        else:
            raise ValueError("In stage '%s': texture '%s' (as seen by %s %s) not present" % (self.name, texName, caller.__class__.__name__, caller.name))


    def connectInput(self, stageInputTextures):
        """Connect input to this FilterStage.

        This assigns the given input textures to this FilterStage.

        This is called by FilterPipeline.reconfigure() before running the stage reconfigure.

        Parameters:

            stageInputTextures  = Input texture dictionary, containing input textures
                                  for this FilterStage.

                                  May contain entries keyed by names in Filter.SCENETEXTURES,
                                  their values containing the references to the corresponding
                                  Texture instances.

        """
        # This is an internal function called only by FilterPipeline.reconfigure().
        #
        assert( isinstance(stageInputTextures, dict) )
        # We must not assert() on the number of entries in stageInputTextures, because it is legal
        # for a filter not to register any input textures (although it will be a very boring filter).

        self.stageInputTextures = stageInputTextures


    def connectOutput(self, outputQuad):
        """Connect this FilterStage to output, and start rendering.

        This assigns to this FilterStage the output quad into which the compositing shader
        (in this FilterStage) renders.

        Then, all registered input textures are assigned to the quad, and the shader (already created
        by reconfigure at this point) is assigned to the quad.

        Parameters:

            outputQuad          = NodePath instance; output quad for this FilterStage.

                                  This is the destination where the compositing shader will be
                                  assigned. This will also be passed to any assigned Filters.

                                  Note that it is the output quad of *this FilterStage*.
                                  It is not the finalQuad of the whole pipeline,
                                  unless this is the last stage of the pipeline.

        """
        # This is an internal function called only by FilterPipeline.reconfigure().
        assert( outputQuad is not None )
        assert( isinstance(outputQuad, NodePath) )

        assert( self._shaderObj is not None )  # reconfigure (to build shader) must have been run first

        self.finalQuad = outputQuad

        # Propagate finalQuad to filters in this stage.
        #
        for f in self.filters:
            f.connectOutput( self.finalQuad )

        # Set texture inputs for our compositing shader.
        #
        for mangledTexName, texture in list(self._findRegisteredTextures().items()):
            self.finalQuad.setShaderInput("tx"+mangledTexName, texture)

        # Assign the compositing shader to finalQuad.
        #
        self.finalQuad.setShader(self._shaderObj)
        self._shaderObj = None  # finalQuad will keep the shader instance reference alive, so we don't need to


    def _registerInputTexture(self, filterInstance, texName):
        """Register an input texture for a filter.

        This method is intended to be called from FilterPipeline after it has created
        the FilterStages, and knows which Filter ends up in which FilterStage.
        It then propagates the registration information to us.

        For the user callback (that is used by onAttachPipeline() in classes derived from Filter),
        see FilterPipeline._registerInputTexture().

        Registered input textures will be inserted to the parameter list of the compositing fshader
        of the pipeline stage. They will also be inserted to the Cg function call for the filter
        that requested the register.

        """
        assert( filterInstance is not None )
        assert( isinstance(filterInstance, Filter) )

        # Add the texture to per-filter inputs.
        #
        # The per-filter data is used for generating the Cg function call to the user-specified code
        # (inserted into the compositing fshader), and for composing the function definition.
        #
        if filterInstance not in self.registeredTextures:
            self.registeredTextures[filterInstance] = []
        self.registeredTextures[filterInstance].append( texName )

    # TODO: name: _registerCustomInput() or _registerCustomShaderInput()?
    def _registerCustomInput(self, filterInstance, customInputMetadata):
        """Register a custom shader input for a filter.

        This method is intended to be called from FilterPipeline after it has created
        the FilterStages, and knows which Filter ends up in which FilterStage.
        It then propagates the registration information to us.

        For the user callback (that is used by onAttachPipeline() in classes derived from Filter),
        see FilterPipeline._registerCustomInput().

        Registered custom inputs will be inserted to the parameter list of the compositing fshader
        of the pipeline stage. They will also be inserted to the Cg function call for the filter
        that requested the register.

        """
        assert( filterInstance is not None )
        assert( isinstance(filterInstance, Filter) )

        # Add the custom input to per-filter inputs.
        #
        # The per-filter data is used for generating the Cg function call to the user-specified code
        # (inserted into the compositing fshader), and for composing the function definition.
        #
        if filterInstance not in self.registeredCustomInputs:
            self.registeredCustomInputs[filterInstance] = []
        self.registeredCustomInputs[filterInstance].append( customInputMetadata )

    def _registerUpdatable(self, filterInstance, updateFunction):
        """Register filterInstance as updatable, with updateFunction providing the code to run at update time.

        This method is intended to be called from FilterPipeline after it has created
        the FilterStages, and knows which Filter ends up in which FilterStage.
        It then propagates the registration information to us.

        For the user callback (that is used by onAttachPipeline() in classes derived from Filter),
        see FilterPipeline._registerUpdatable().

        """
        assert( filterInstance is not None )
        assert( isinstance(filterInstance, Filter) )
        assert( updateFunction is not None )

        self.updateFunctions[filterInstance] = updateFunction


    def addFilterInstance(self, f):
        """Assign a Filter instance to this FilterStage.

        Internal method, used by FilterPipeline.

        Note that FilterPipeline manages the Filter instances. FilterStages are volatile
        in the sense that they are destroyed and created at each reconfigure() of the pipeline.

        Thus FilterStage has no methods to query or remove filters, or to set filter parameters;
        use the methods of FilterPipeline to do that.

        """
        assert( f is not None )
        assert( isinstance(f, Filter) )

        self.filters.append( f )


    def _findRegisteredTexturesForFilter(self, f):
        """Return mangled names and Texture instance references for textures registered by Filter instance f.

        (Regardless whether they are scene textures (FilterStage input),
          or internal textures defined by filters.)

        This implements name resolution via getTextureInfo().

        Note that the names of internal textures defined by filters are mangled by the owner of the texture,
        which is not necessarily f itself; filters may register textures provided by other filters earlier
        in the same FilterStage.

        Scene texture names are not mangled.

        Return value:
          dict:  key: mangled texture name, value: Texture instance reference

        """
        assert( isinstance(f, Filter) )

        textures = {}
        if f in self.registeredTextures:  # has this filter registered any textures?
            for texName in self.registeredTextures[f]:
                # Find the definition of texName that is seen by "f" (getTextureInfo implements name masking).
                #
                texInfo = self.getTextureInfo(texName, caller=f)
                if texInfo.get('owner') is None:  # scene texture
                    mangledTexName = texName
                else:
                    mangledTexName = texInfo.get('owner').getMangledName(texName)
                textures[mangledTexName] = texInfo.get('texture')

        return textures


    def _findRegisteredTextures(self):
        """Return mangled names and Texture instance references for all registered textures of render-enabled filters.

        (Regardless whether they are scene textures (FilterStage input),
          or internal textures defined by filters.)

        Render-enabled means that the filter instance participates in compositing.

        Return value:
          dict:  key: mangled texture name, value: Texture instance reference

        See also:
          _findRegisteredTexturesForFilter()

        """
        allRegisteredTextures = {}  # key: mangled texture name, value: Texture instance reference

        renderingFilters = [item for item in self.filters if item.enableRender]
        for f in renderingFilters:
            allRegisteredTextures.update( self._findRegisteredTexturesForFilter(f) )

        return allRegisteredTextures


    def reconfigure(self):
        """Synthesize and compile shaders.

        FilterStage has no "_needsCompile" flag, because it is currently not supported to recompile
        only a single FilterStage. Thus, this method is only called by FilterPipeline.reconfigure(),
        and this always compiles the FilterStage.

        This limitation is because FilterManager has only a monolithic cleanup() that destroys
        *all* dynamic state (i.e. it is not possible to destroy only the state related to
        a given FilterStage).

        """
        # This function always works like the "fullrebuild" mode in old CommonFilters (up to 1.8.1).
        #
        # Because configuration resides in filter object properties, and their setters take care of
        # updating the appropriate shader inputs, FilterStage.reconfigure() only has work to do when
        # a compositing shader recompile is needed.

        # - We are being called from FilterPipeline.reconfigure(),
        #   so we can consider ourselves an internal function. Hence asserts.
        #
        # - connect() must have been called first to set up the input textures
        #   before it is valid to call attachStage() for the filters.
        #   Check that now before we begin the actual build.
        #
        assert( isinstance(self.stageInputTextures, dict) )
        # We must not assert() on the number of entries in self.stageInputTextures, because it is legal
        # for a filter not to register any input textures (although it will be a very boring filter).

        # Also sanity-check the enabled filters.
        #
        # addFilterInstance() already does this, but the data member is public (TODO: maybe shouldn't be?)
        #
        for f in self.filters:
            assert( f is not None )
            assert( isinstance(f, Filter) )

        # Validate sort values for all filters, and if the check passes, then sort the filters.
        #
        # The check can fail due to errors in user-defined code, so here we raise an exception on error.
        #
        sortvalues = {}  # for sort conflict error message
        for f in self.filters:

            # definedness
            if f.sort is None:
                raise ValueError("In FilterStage '%s': filter %s (%s) has no sort value (sort is None). Valid: integer, 0 <= sort < 100." % (self.name, f.__class__.__name__, f.name))

            # range
            if isinstance(f, StageInitializer):
                if f.sort != -1:
                    raise ValueError("In FilterStage '%s': stage initialization filter %s (%s) must have sort = -1, but has %d." % (self.name, f.__class__.__name__, f.name, f.sort))
            elif f.sort < 0  or  f.sort > 99:
                raise ValueError("In FilterStage '%s': filter %s (%s) has out-of-range sort value %d. Valid: integer, 0 <= sort < 100." % (self.name, f.__class__.__name__, f.name, f.sort))

            # uniqueness (better to raise an error than let containers decide what to do in case of conflict;
            #             the whole idea of the sort value is that it defines an explicit ordering for the
            #             filters.)
            #
            if (f.mergings, f.sort) in sortvalues:
                g = sortvalues[(f.mergings, f.sort)]
                raise ValueError("In FilterStage '%s': sort conflict between same-stage filters %s (%s) and %s (%s); both have sort value %d." % (self.name, f.__class__.__name__, f.name, g.__class__.__name__, g.name, f.sort))
            sortvalues[(f.mergings, f.sort)] = f  # remember which filter had this sort value (for conflict error message)

        # This accounts also for stage mergings by FilterPipeline. At first, f.mergings is zero
        # for all filters "f", and each stage merge for a filter "f" in the current rebuild
        # increases f.mergings by one.
        #
        self.filters.sort(key=lambda f: (f.mergings, f.sort))

        # Attach filters to the stage.
        #
        # Note that the stage input (scene) textures MUST be available before this is done; the filters
        # store their stage input texture references from us at FilterStage attach time.
        #
        # attachStage() calls onAttachStage() to create internal stages if the filter has any,
        # and (now that the interQuads are available) compiles the filter's internal shaders
        # if it has any.
        #
        for f in self.filters:
            f.attachStage( filterStage=self )

        # We synthesize the compositing shader here. Skip any filters that have render disabled.
        #
        # Those filters not participate in compositing, but only provide their intermediate textures
        # for other filters to read. (Use case example: VolumetricLighting uses Bloom as a preprocessor.)
        #
        renderingFilters = [item for item in self.filters if item.enableRender]

        # Figure out which texcoord and texpad variables will be needed.
        #
        # We also check which texpix variables will be needed *in the vshader*.
        #
        # For the fshader, we always provide texpix for each registered texture, and let the
        # shader compiler eliminate the input at compile time if it is unused. Panda also
        # notices that its builtin texpix_txXXX is not being used by the shader, and doesn't
        # bother sending the data to the GPU.
        #
        # Note that name mangling implies that the Texture reference for any given texName depends on
        # which Filter requests it; duplicate names are masked by the most recent definition as seen by
        # the requesting filter instance (walking self.filters backward; see _findRegisteredTextures(),
        # and getTextureInfo() which actually implements this).
        #
        # Also note that we only need to set up texture information for those filters that have render enabled.
        # It doesn't matter whether the texture source (if it is a filter) has its render enabled or not,
        # but obviously the compositing shader only needs textures registered by filters that actually
        # participate in the compositing (regardless of whichever filter actually owns those textures!).
        #
        texcoords       = {}
        texcoordPadding = {}
        allRegisteredTextures = self._findRegisteredTextures()
        for mangledTexName, texture in list(allRegisteredTextures.items()):
            # texpad and texpix must be handled per-texture due to possibly different texture sizes.
            #
            # texpad holds the coordinates of the center of the texture, in texture coordinates.
            # If this is a "textures-power-2 none" texture (i.e. not padded), then the center position
            # is always (0.5, 0.5), and we can omit that from the shader inputs.
            #
            # HalfPixelShift implies per-texture texcoord due to possibly different texture sizes,
            # i.e. different textures will require different amounts of shift in texture coordinates.
            #
            # Most of the time, all filter textures are "textures-power-2 none", and HalfPixelShift
            # is not enabled, allowing us to provide only one shared texcoord variable.
            #
            texPadded = (texture.getAutoTextureScale() != ATSNone)
            if texPadded  or  self.halfPixelShift:  # need per-texture texcoord?
                texcoords[mangledTexName] = "l_texcoord_" + mangledTexName
                padName = mangledTexName if texPadded else None
                pixName = mangledTexName if self.halfPixelShift else None
                texcoordPadding["l_texcoord_" + mangledTexName] = (padName, pixName)
            else:
                # Share unpadded texture coordinates for this texture.
                texcoords[mangledTexName] = "l_texcoord"
                texcoordPadding["l_texcoord"] = (None, None)
        self._texcoords = texcoords

        # number for matching TEXCOORD registers between vshader and fshader,
        # name for the corresponding texcoord variable.
        texcoordSets = list(enumerate(texcoordPadding.keys()))


        ########################################################
        # Synthesize compositing shader for this pipeline stage
        ########################################################

        # complete program = language header + vertex shader + filter functions + fragment shader

        # top-level indentation depth, in spaces
        #
        tabWidth = 4

        # We use the ancient arbvp1 and arbfp1 profiles, because when using any newer profile supported by Cg,
        # the shaders compiled by Cg only work properly on NVIDIA cards. Shaders compiled using arbvp1/arbfp1
        # profiles work properly on all cards, at least those supporting shader model 2.0 and above.
        #
        # The good thing is that arbvp1/arbfp1 shaders will run on even rather ancient (2007) hardware.
        #
        # TODO: Port this and all Filters over to GLSL, since Cg is no longer maintained.
        # TODO: Decide later what to do about supporting old hardware at that point.

        cgHeader  = "//Cg\n"
        cgHeader += "//\n"
        cgHeader += "//Cg profile arbvp1 arbfp1\n\n"

        # Generate some documentation for self.shaderSourceCode
        cgHeader += "// FilterPipeline generated shader for render pass:\n"
        cgHeader += "//   %s\n" % self.name
        cgHeader += "//\n"
        if self.halfPixelShift:
            cgHeader += "// HalfPixelShift enabled\n"
            cgHeader += "//\n"
        cgHeader += "// Enabled filters (in this order):\n"
        for f in self.filters:
            renderStatus = "" if f.enableRender else " (no render)"
            cgHeader += "//   %s %s%s\n" % (f.__class__.__name__, f.name, renderStatus)
        cgHeader += "\n"

        ##################
        # compose vshader
        ##################

        # Here we don't need to do anything special to account for texture name mangling,
        # because the names in texcoordPadding (including padTex and pixTex)
        # have already been resolved and mangled.

        vshader  = "void vshader( "
        ind = (len(vshader) * " ")  # indentation in parameter list
        vshader += "float4 vtx_position : POSITION,\n"
        vshader += "%sout float4 l_position : POSITION,\n" % ind

        for padTex, pixTex in list(texcoordPadding.values()):
            if padTex is not None:
                vshader += "%suniform float4 texpad_tx%s,\n" % (ind, padTex)
            if pixTex is not None:
                vshader += "%suniform float4 texpix_tx%s,\n" % (ind, pixTex)
        for i, name in texcoordSets:
            vshader += "%sout float2 %s : TEXCOORD%d,\n" % (ind, name, i)

        vshader += "%suniform float4x4 mat_modelproj )\n" % ind
        vshader += "{\n"
        ind = (tabWidth * " ")  # indentation in vshader body
        vshader += "%sl_position = mul(mat_modelproj, vtx_position);\n" % ind

        for texcoord, item in list(texcoordPadding.items()):
            padTex, pixTex = item
            if padTex is not None:
                vshader += "%s%s = (vtx_position.xz * texpad_tx%s.xy) + texpad_tx%s.xy;\n" % (ind, texcoord,
                                                                                              padTex, padTex)
            else:
                vshader += "%s%s = (vtx_position.xz * float2(0.5, 0.5)) + float2(0.5, 0.5);\n" % (ind, texcoord)
            if pixTex is not None:  # this implements HalfPixelShift
                vshader += "%s%s += texpix_tx%s.xy * 0.5;\n" % (ind, texcoord, pixTex)

        vshader += "}\n\n"

        ###########################
        # compose filter functions
        ###########################

        # We build both the functions and their invocations here.

        filterFunctions = ""
        filterCalls = {}  # key: Filter instance reference, value: string, function invocation
        for f in renderingFilters:
            fshaderdata = f.synthesizeCompositor()
            funcName, funcImplementation, funcComment = fshaderdata[0:3]  # these are mandatory
            if len(fshaderdata) > 3:  # optional internal functions (one per list element)
                internalFuncs = fshaderdata[3:]
            else:
                internalFuncs = None

            # Mangling the function name is the only safe solution to handle duplicates, because
            # Filters are allowed to generate different code depending on their configuration.
            #
            # Thus, if two or more copies of the same type of filter end up in this FilterStage,
            # we have no idea whether their implementations are the same (in which case, in principle,
            # one function definition would suffice) or different.
            #
            funcName = f.getMangledName(funcName)

            code     = ""
            funcCall = ""

            # Add any helper functions defined by the filter. The caller is responsible for mangling
            # the internal function name.
            #
            if internalFuncs is not None:
                for internalFunc in internalFuncs:
                    code += "// Helper function for %s %s\n" % (f.__class__.__name__, f.name)
                    code += "//\n"
                    code += internalFunc
                    code += "\n"

            # Start both function definition and its call by the short comment,
            # if one was provided by the filter.
            #
            if funcComment is not None:
                code     += funcComment
                funcCall += funcComment

            # Line that begins the actual function definition / call.
            #
            codeStart = "inline float4 %s( " % funcName
            callStart = "pixcolor = %s( "    % funcName

            # Determine amount of indentation needed for parameter list
            indCode = (len(codeStart) * " ")
            indCall = (len(callStart) * " ")

            code     += codeStart 
            funcCall += callStart

            # Basically all filters except StageInitializer want pixcolor as an argument
            # to the filter function.
            #
            # We however provide a general mechanism to communicate this, so that this can work
            # also with unexpected setups.
            #
            paramlist_code = []
            paramlist_call = []
            if f._needPixcolor:
                paramlist_code.append( "float4 pixcolor" )
                paramlist_call.append( "pixcolor" )

            # Add texture inputs
            #
            texcoordinputs = set()
            for mangledTexName, texture in list(self._findRegisteredTexturesForFilter(f).items()):
                paramlist_code.append( "uniform sampler2D k_tx%s" % (mangledTexName) )
                paramlist_call.append( "k_tx%s" % (mangledTexName) )

                # Add corresponding texcoord if not added yet
                # (may have been added by another texture in case of shared unpadded texcoords)
                #
                if texcoords[mangledTexName] not in texcoordinputs:
                    paramlist_code.append( "float2 %s" % (texcoords[mangledTexName]) )
                    paramlist_call.append( "%s" % (texcoords[mangledTexName]) )
                    texcoordinputs.add(texcoords[mangledTexName])

                paramlist_code.append( "uniform float4 texpix_tx%s" % (mangledTexName) )
                paramlist_call.append( "texpix_tx%s" % (mangledTexName) )

                texPadded = (texture.getAutoTextureScale() != ATSNone)
                if texPadded:
                    paramlist_code.append( "uniform float4 texpad_tx%s" % (mangledTexName) )
                    paramlist_call.append( "texpad_tx%s" % (mangledTexName) )

            # Add custom inputs
            #
            if f in self.registeredCustomInputs:  # has this filter registered any custom inputs?
                for item in self.registeredCustomInputs[f]:
                    # Note that this requires that the code returned by the Filter's onSynthesizeCompositor() method
                    # also uses the mangled names for the custom inputs.
                    #
                    # We use mangled names here for forward-compatibility with GLSL, where uniforms
                    # are globals (and hence must have unique names across all filters in the same FilterStage).
                    #
                    mangledInputName = f.getMangledName(item.get('inputName'))
                    paramlist_code.append( "uniform %s %s" % (item.get('inputType'), mangledInputName) )
                    paramlist_call.append( "%s" % (mangledInputName) )

            # Construct parameter list.
            #
            # The separator contains the indentation for the next line.
            #
            code     += (",\n%s" % (indCode)).join(paramlist_code)
            code += " )\n"

            funcCall += (",\n%s" % (indCall)).join(paramlist_call)
            funcCall += " );\n\n"

            # Paste implementation from the filter.
            #
            code += "{\n"
            # If pixcolor is not provided as a parameter to the filter function,
            # the filter implementation is required to create it and set its value.
###            if not f._needPixcolor:
###                # If pixcolor is not provided as a parameter to the filter function,
###                # the filter implementation is required to set its value.
###                code += FilterUtils.indent("float4 pixcolor;\n", tabWidth)
            code += FilterUtils.indent(funcImplementation, tabWidth)
            code += FilterUtils.indent("return pixcolor;\n", tabWidth)
            code += "}\n\n"
            filterFunctions += code

            filterCalls[f] = funcCall

        ##################
        # compose fshader
        ##################

        # The implementation of the fshader simply consists of calls to enabled filters,
        # ordered by the sort order already determined further above.
        #
        # We use a temporary "pixcolor" variable to prevent implicit saturation to [0, 1]
        # in intermediate processing; assigning to o_color directly would do that.
        #
        # The filters are expected to saturate explicitly, if they want to.
        #
        # We only assign the result to o_color once all the processing in this stage has completed.
        #
        # Initialization of pixcolor (from the current pixel in k_txcolor) is provided
        # by StageInitializer, which always goes first.

        fshader = "void fshader( "
        ind = (len(fshader) * " ")  # indentation in parameter list

        for i, name in texcoordSets:
            fshader += "float2 %s : TEXCOORD%d,\n%s" % (name, i, ind)

        # In the fshader parameter list, we must provide each registered texture instance exactly once,
        # regardless of how many filters ended up requesting it.
        #
        for mangledTexName, texture in list(allRegisteredTextures.items()):
            fshader += "uniform sampler2D k_tx%s,\n%s"   % (mangledTexName, ind)
            fshader += "uniform float4 texpix_tx%s,\n%s" % (mangledTexName, ind)

            texPadded = (texture.getAutoTextureScale() != ATSNone)
            if texPadded:
                fshader += "uniform float4 texpad_tx%s,\n%s" % (mangledTexName, ind)

        # Custom inputs are always defined by the filter that registered them,
        # so here we don't need to do any name masking lookups.
        #
        # Here the only effect of name mangling is to mangle the name into a
        # unique one (so that this works also when multiple instances of the
        # same filter type are placed in the same FilterStage).
        #
        for f in renderingFilters:
            if f in self.registeredCustomInputs:  # has this filter registered any custom inputs?
                for item in self.registeredCustomInputs[f]:
                    fshader += "uniform %s %s,\n%s" % (item.get('inputType'), f.getMangledName(item.get('inputName')), ind)

        fshader += "out float4 o_color : COLOR )\n"
        fshader += "{\n"
        fshader += FilterUtils.indent("float4 pixcolor;\n\n", tabWidth)
        for f in renderingFilters:
            fshader += FilterUtils.indent(filterCalls[f], tabWidth)
        fshader += FilterUtils.indent("o_color = pixcolor;\n", tabWidth)
        fshader += "}\n"

        ########################################################

        # Assemble the complete shader program and compile the shader.
        #
        # We save the current shader source code into a member variable
        # to aid debugging and run-time inspectability.
        #
        completeSourceCode = cgHeader + vshader + filterFunctions + fshader

        shaderObj = Shader.make(completeSourceCode)
        if shaderObj is None:
            filterlist = [ "%s %s" % (obj.__class__.__name__, obj.name) for obj in self.filters ]
            self.cleanup()
            raise RuntimeError("Shader.make() for compositing shader failed in FilterStage '%s', which had the following filters: %s" % (self.name, filterlist))
        self._shaderObj        = shaderObj  # compiled shader is ready; store it for connectOutput()
        self._shaderSourceCode = completeSourceCode


    @property
    def shaderSourceCode(self):
        """Source code of the currently active compositing shader of this FilterStage, or None if not running.

        Read-only property.

        Note that the source may contained compiled-in values for filter parameters,
        especially for loop limits (to conform to the arbvp1 and arbfp1 profiles,
        which do not allow variable loop limits; these profiles require all loops
        to be unrolled by the compiler, and hence loop limits must be known at compile time).

        Also, the exact content of the source code will (obviously) depend on which filters
        are present in this FilterStage, and on their settings. Note especially that
        filters are allowed to provide options that completely change their generated code
        (e.g. an algorithm selection option).

        Thus, this is mainly useful for debugging and examining the framework; for understanding
        individual Filter subclasses, it may be clearer to read their sources directly.

        This is also useful as a debugging aid when developing new filters, since this is the exact source
        that was sent to the shader compiler. Hence, if any errors are triggered during compilation of the
        compositing shader, the line numbers in the error messages (printed to the terminal window)
        will match this source.

        """
        return self._shaderSourceCode


    def update(self):
        """Update function. Called internally from FilterPipeline.updateTask().

        This runs deferred reconfigures (if any are pending), and calls the filters' update methods.

        """
        # We are only called when the pipeline is in a fully built state.
        # Hence this will walk the filters in the correct order.
        #
        for f in self.filters:
            # Run deferred reconfigure.

            # We must always run reconfigure() for CompoundFilters to avoid introducing a wart for
            # defining parameters in CompoundFilters.
            #
            # Without this, a CompoundFilter would be required to update its own _needsCompile flag
            # (which is basically meaningless and practically always False, as a CompoundFilter
            #  rarely defines any internal stages of its own) whenever the internal stage code generation
            # of some contained filter is affected by the change of some parameter.
            #
            # With this here, filter parameters in CompoundFilters need no special handling
            # regardless of what they do (in property setters, it is enough to call the original setter
            # from the contained filter).
            #
            if isinstance(f, CompoundFilter)  or  f._needsCompile:
                f.reconfigure()

            # Call the update function, if the filter has registered one.
            #
            # (CompoundFilter manages calling the updates of its contained filters if needed,
            #  so we don't need any special handling for that.)
            #
            if f in self.updateFunctions:
                self.updateFunctions[f]()

