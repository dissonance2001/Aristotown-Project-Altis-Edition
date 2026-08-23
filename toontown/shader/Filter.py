"""This module defines the Filter API. This is part of the postprocessing filter system.


The Filter API is used to implement new postprocessing filters.

If you are looking to use existing postprocessing filters, see the FilterPipeline class,
which provides the primary user API. Refer to the individual subclasses of Filter for
descriptions of available filters.

Both of these APIs were introduced in Panda 1.9.0. The CommonFilters class provides
backward compatibility (1.8.x) for existing scripts, working on top of FilterPipeline.

It is recommended to target new scripts to the new FilterPipeline API, which offers
more flexibility. The new API also allows the definition of custom filters that
can be mixed together in the same postprocessing pipeline with the ones provided in Panda.


Below is a quick reference for the Filter interface. See the existing filters for complete examples.

Usually, inheriting from the abstract base class Filter is the right thing to do,
but it is also legal to inherit from another existing filter, if that is more appropriate
for your particular filter.


# Add whichever Panda imports are needed by your filter. Maybe the most common ones:
#from panda3d.core import Vec2, Vec4, AuxBitplaneAttrib, Shader

from Filter import Filter, TextureInfo

class MyCoolEffectFilter(Filter):
    # You can use class scope constants for enums.
    #
    # MyCoolEffectFilter operating modes
    MBasic   = 0
    MAwesome = 1

    def __init__(self, **kwargs):
        super(MyCoolEffectFilter, self).__init__(**kwargs)

        # your custom code here (if needed - usually not)

    def onReset(self):
        # Reset inherited properties.
        super(MyCoolEffectFilter, self).onReset()

        # - Set self.sort and self.stageName to desired default values at this point.
        # - You can also set self.isMergeable.
        #
        # By default, the filter is mergeable to previous stages.
        #
        # Note that sort and stageName have no default, because they are specific
        # to each filter type.

        # - Set your properties to their default values. Note PROPERTIES,
        #   not their internal data members; this is needed so that reset()
        #   (which calls onReset()) does the right thing also when called for a
        #   running filter instance.

        self.sort = 10
        self.param1 = 0.75
        self.param2 = 3.14
        self.param3 = MyCoolEffectFilter.MAwesome

    def onAttachPipeline(self):
        # Called when the filter is being attached to a FilterPipeline.
        #
        # Register input textures, custom shader inputs if any, and aux bits if any.
        # See existing filters for examples.
        #
        # Also register the filter as updatable if you need to provide update().

    def onAttachStage(self):
        # Called when the filter is being attached to a FilterStage.
        #
        # Create internal stages here, if needed (see BlurSharpenFilter for an example).

    def onDetachPipeline(self):
    def onDetachStage(self):
        # If you allocate something manually in onAttachPipeline() or in onAttachStage(),
        # these callbacks can be used to tear down those resources.
        #
        # The most common resources used by internal stages of the filter are cleaned up automatically
        # by detachStage(), which detaches the filter from the pipeline stage (FilterStage);
        # it is very rare that there is a need to define these methods. See Filter.detachStage().
        #
        # These methods are part of cleanup; they must not raise exceptions. (Cleanup may be triggered
        # in response to exceptions.)

    def onCompileInternalStages(self):
        # Load or compile, and assign shaders for internal stages (see BlurSharpenFilter for an example).
        #
        # If your filter has no internal stages, it does not need to define this method.

    def onSynthesizeCompositor(self):
        # Generate fshader code for the compositing shader. See docstring of this function for details.
        #
        # Most filters provide this function in order to be able to render output, but in the rare case
        # that your filter is intended to only work as a preprocessor for other filters (always having
        # enableRender=False), then it does not need to define onSynthesizeCompositor().

    def onUpdate(self):
        # Update those run-time parameters that must be updated every frame.
        #
        # If your filter does not have any such parameters, then there is no need
        # to provide this function.
        #
        # If you define onUpdate(), be sure to call self.registerUpdatable() in your onAttachPipeline(),
        # so that your onUpdate() will be automatically called at each frame (just before the frame is drawn).


    # Create Python properties for filter parameters.
    #
    # It is mandatory to use properties for filter parameters; do not use bare data members
    # or explicit getXXX()/setXXX() functions. This is to guarantee a unified interface.
    #
    # Default values and initialization are provided by onReset(), defined above.
    #
    # The property getter can usually just return the value of the underlying data member.
    # It should also provide a descriptive docstring explaining what the parameter affects.
    #
    # The details for how to program the property setter differ depending on what the parameter does:
    #
    #  - Some parameters send custom shader inputs to the compositing shader.
    #    In this case, the shader input must be accessed by its mangled name
    #    (because multiple instances of the same filter type are allowed
    #     in the same FilterStage).
    #
    #  - Some parameters send custom shader inputs to internal stages.
    #    In this case, name mangling is not needed.
    #
    #  - Some parameters control the code generation of the compositing shader.
    #    The setter should flag a *pipeline* recompile, so that the changes will be
    #    automatically applied before the next frame is rendered.
    #
    #  - Some parameters control the code generation of internal stages.
    #    The setter should flag a *filter* recompile, so that the changes will be
    #    automatically applied before the next frame is rendered.
    #
    #  - Some parameters control the behavior of the custom onUpdate() function in various ways.
    #
    #  - The same parameter may fall into several of the above categories.
    #
    # It is easiest to learn by example; see the existing filters for working code examples
    # of all of the above.

"""

# NOTE: Currently textures are pipeline-level objects.
#
#       Input texture registration also takes place at pipeline level.
#
#       Thus, any property that changes which textures are needed in the compositing fshader,
#       or any property that affects texture creation (e.g. number of internal stages
#       in the filter), is conceptually, and must be implemented as, a FilterPipeline-level
#       compile-time parameter.
#
#       Currently, although conceptually it should not, this same observation affects also properties
#       that change the connections between internal stages in a filter, because those connections are set up
#       when the filter is attached to FilterStage, but FilterStage cannot destroy any existing textures
#       or quads due to the monolithic cleanup in FilterManager.
#
#       (Actually, since attachStage() creates the internal textures and quads,
#        this means that currently, attachStage() (for any given Filter instance)
#        can only be called once per *pipeline* reconfigure.)
#
#       This conceptual change, and (if added later) support for fine-grained cleanup in FilterManager,
#       would allow for simplifying the code by removing the delegation mechanism from FilterStage.reconfigure()
#       and letting FilterStage-level and Filter-level recompiles recompile just the changed part.


import inspect
import collections

from panda3d.core import NodePath, Shader

from toontown.shader import FilterUtils, FilterPipeline, FilterStage

# The following are needed for some explicit isinstance() checks in parameter validation only;
# the rest relies on duck typing.
#
# Note that these modules do "from Filter import Filter", so Filter must be fully loaded first
# before either of them can finish loading.
#
# To avoid cyclic dependencies, we just register that we would like to have these modules,
# whenever they become available and whatever names they happen to contain (instead of
# "from ... import ...", which requires the target module to be fully loaded
# to extract names from it).
#

"""Scene textures supported by FilterManager."""
SCENETEXTURES = ["color", "depth", "aux"]

###########################################################################
# Metadata helper classes for FilterStage's compositing fshader parameters
###########################################################################

# inputType = string. Cg datatype of input, e.g. int, float, float4, ...
# inputName = string. Name of input exactly as it appears in the code, e.g. k_blur_amount.
#
CustomInputMetadata = collections.namedtuple("CustomInputMetadata", "inputType inputName")

# See Filter.getTextureInfo() for details.
#
# varname   = Name of the sampler2D variable, as it appears in the code (mangled, and with k_tx prefix)
# texpix    = Name of the variable holding the corresponding texpix
# texpad    = Name of the variable holding the corresponding texpad (or "float2(0.5, 0.5)" if not padded)
# texcoord  = Name of the variable holding the corresponding texture coordinate
# texture   = Reference to the Texture object
# owner     = Filter instance reference for internal stage textures, and None for scene textures.
#
TextureInfo = collections.namedtuple("TextureInfo", ["varname", "texpix", "texpad", "texcoord", "texture", "owner"])


#############################################################
# The Filter class itself.
#############################################################

class Filter(object):
    """Abstract base class for postprocessing filters. Filters are implemented in derived classes."""

    def __init__(self, **kwargs):
        """Constructor.

        This calls self.cleanup() (to create data members) and self.reset(),
        and loads any parameters from kwargs into properties.

        The key of each kwarg must be the name of a valid property of the instance being initialized.
        Trying to set a property that does not exist in the current instance (current filter type)
        raises AttributeError; this is meant to protect against human error in the parameter list
        (typos, and trying to send settings that belong to a different type of filter).

        This abstract base class defines the pipeline-related properties: "sort", "stageName" and "isMergeable".
        These must usually be set in onReset() of derived classes; "sort" does not even have a
        valid default value, as the sort value is very filter-specific.

        In your derived classes, be sure to call super(YourClass, self).__init__(**kwargs).

        Exact placement of the call (within derived class's __init__()) does not matter,
        as long as you keep in mind that this will basically run cleanup() (to create the
        related data members and initialize them to empty values), reset(),
        and setConfiguration().

        """
        super(Filter, self).__init__()

        # The _needsCompile flag stores whether this filter instance currently needs to be (re)compiled.
        #
        # It tracks changes to Filter-level compile-time parameters; i.e. those affecting
        # the shaders of internal stages.
        #
        self._needsCompile = True

        # Internal flag. Tells whether this filter wants the "pixcolor" (current pixel color)
        # parameter as input to its filter function in the compositing shader.
        #
        # (Basically, StageInitializationFilter is normally the only one that doesn't,
        #  because it sets the initial value of pixcolor.)
        #
        # If True (default):
        #   The float4 parameter "pixcolor" is passed to the filter function, and the function
        #   is expected to update its value.
        #
        # If False:
        #   The filter function must create a local variable "float4 pixcolor;"
        #   and assign a value to it.
        #
        # In either case, code to "return pixcolor;" is always synthesized into the filter function.
        #
        self._needPixcolor = True

        # self.pipeline and self.filterStage are managed by attachPipeline()/detachPipeline() and
        # attachStage()/detachStage(), respectively.
        #
        # We set these to None before calling cleanup() to create the data members and
        # initialize them with blanks, because cleanup() in derived classes (called from detachPipeline(),
        # which is called by our cleanup()) might reference these.
        #
        # (It makes possible errors in user-defined code easier to debug if the attribute always exists;
        #  something being None is a clear indication of that something not being initialized, while a
        #  missing attribute looks like an internal bug.)
        #
        self.pipeline = None
        self.filterStage = None
        self.cleanup()

        # This will call onReset().
        #
        self.reset()

        # Because we are not yet attached to any FilterStage, the setters should do the right thing
        # and just set the corresponding internal variable to the new value.
        #
        self.setConfiguration(**kwargs)

    def __del__(self):
        """Destructor."""
        self.cleanup()

    def cleanup(self):
        """Cleanup method for whole-hog object cleanup.

        (For the opposite of setup(), see setdown().)

        """
        self.detachStage()
        self.detachPipeline()

    def ls(self, indent = 0):
        """Print a human-readable description of this Filter instance into the terminal."""
        ind = (indent * " ")
        nints = len(self.get('texture'))

        if nints == 0:
            internal_passes = ""
        else:
            intplural = "es" if nints != 1 else ""
            internal_passes = "; %s internal render pass%s" % (nints, intplural)

        print(("%s%s %s%s" % (ind, self.__class__.__name__, self.name, internal_passes)))

        if len(self.get('texture')) > 0:
            # sort by texture name for human-readability
            print(("%s  Internal textures: %s" % (ind, sorted(self.get('texture').keys()))))

        for key, value in sorted(list(self.getConfiguration().items())):
            print(("%s    %s: %s" % (ind, key, value)))

    @property
    def name(self):
        """Optional human-readable name for this Filter instance.

        Used in error messages and ls().

        The default is a fairly noninformative "instance at 0x%x", where the number is id(self).

        If you e.g. use a filter with enableRender=False to create input textures for another filter,
        it may be useful to mention that in the name (useful if you have an independent instance of the
        "helper" filter in the same pipeline, so that if errors occur, it is easier to tell which instance
        triggered the error).

        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def enableRender(self):
        """Whether this filter participates in the compositing shader of the stage it is placed in.

        Bool. Default True.

        Disabling this can be useful to use the filter to render additional internal textures to be
        fed into other filters. For example, VolumetricLighting can use the bloomOutput texture from
        Bloom as its input (and that instance of Bloom should only render that texture,
        and not participate in the compositing).

        """
        return self._enableRender

    @enableRender.setter
    def enableRender(self, value):
        if (not hasattr(self, "_enableRender") or value != self._enableRender) and self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._enableRender = value

    @property
    def sort(self):
        """Sort value of this filter inside the pipeline stage it resides in.

        Integer, 0 <= sort < 100. Smaller means earlier. A special value of -1 is reserved
        for the pipeline stage initialization filter (see StageInitializationFilter).

        The sort value controls the ordering of the filters within the compositing shader
        of the pipeline stage.

        See also:

          stageName
          isMergeable

        """
        return self._sort

    @sort.setter
    def sort(self, value):
        if (not hasattr(self, "_sort") or value != self._sort) and self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._sort = value

    # Note: if FilterStage-level recompiles are implemented later:
    #
    # Changing stageName or isMergeable really requires the *whole pipeline* to be recompiled,
    # because (at least) two different stages are affected.
    #
    # (May affect more than two stages, depending on exactly which enabled filters have isMergeable set.
    #  Hence the simplest correct solution is to fully rebuild the pipeline.)
    #
    @property
    def stageName(self):
        """Which pipeline stage this filter should go into.

        String, one of fpp.knownStages where fpp is the FilterPipeline this filter will be placed in.

        (The constructor of FilterPipeline sets up a sensible default list designed to work with
         the default stage assignments of the Filters provided in Panda. It is however possible to
         override everything at runtime - defining a new list of stages in the pipeline instance,
         and setting the stageName of each Filter instance to one of the new stages when the app
         creates the Filter instances and adds them to the pipeline.)

        Each stage tentatively marks a new render pass (but see isMergeable).

        See also:

          sort
          isMergeable

        """
        return self._stageName

    @stageName.setter
    def stageName(self, value):
        if (not hasattr(self, "_stageName") or value != self._stageName) and self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._stageName = value

    @property
    def isMergeable(self):
        """Whether this filter can be merged into a previous stage.

        Bool.

        If True, stageName is considered tentative. If the stage specified by stageName contains
        only mergeable filters at pipeline reconfigure() time, the stage will be eliminated 
        (to reduce the number of render passes), by placing all filters from it to a previous stage.

        If False, stageName is considered absolute. This filter will be placed in the
        named stage, and nowhere else. A new render pass will be created, if not already
        created for another filter with the same stageName.

        Default is True. This should be set to False only in those Filter subclasses that need
        access to up-to-date texture information outside the current pixel in the fshader.
        BlurSharpen is an example.

        Note that the up-to-date color for the current pixel is always available in pixcolor.

        If your filter algorithm is such that it cannot respect previous changes to pixcolor,
        then it should begin a new stage, with stageName=..., isMergeable=False and sort=0.

        See also:

          sort
          stageName

        """
        return self._isMergeable

    @isMergeable.setter
    def isMergeable(self, value):
        if (not hasattr(self, "_isMergeable") or value != self._isMergeable) and self.pipeline is not None:
            self.pipeline._needsCompile = True
        self._isMergeable = value

    def reset(self):
        """Set filter-specific settings to their default values.

        Interface method.

        Do not override this; instead, override onReset(), which is provided for that purpose.

        """
        self.onReset()

    def onReset(self):
        """Set filter-specific settings to their default values.

        Implementation method.

        While this function is running, recompiles are guaranteed to be disabled.

        Derived classes should override this to set their sort, stageName and isMergeable values,
        and to set filter-specific parameters to sensible defaults.

        Be sure to call super(YourClass, self).onReset() *first* in your onReset() to make sure that any
        inherited properties are reset correctly. This requirement holds whether your class inherits
        from Filter or from an existing derived class.

        Derived classes ARE allowed, if it is considered necessary, to set different default values
        for inherited properties than their ancestors.

        The Filter base class defines three properties: "sort", "stageName" and "isMergeable".

        Always be sure to reset the configuration by assigning to the PROPERTIES, not directly to their
        internal data members. This allows reset() to behave as expected, not only during initialization,
        but also when called for a running filter instance.

        """
        # Note we set properties, not their internal data members.
        self.sort = None  # no valid default
        self.stageName = None  # no valid default
        self.isMergeable = True
        self.enableRender = True
        self.name = "instance at 0x%x" % id(self)

    def setConfiguration(self, **kwargs):
        """Set zero or more filter-specific settings, given as kwargs.

        Any setting that is implemented as a property is supported.

        Trying to set a property that does not exist in the current instance (current filter type)
        raises AttributeError; this is meant to protect against human error in the parameter list
        (typos, and trying to send settings that belong to a different type of filter).
        In such a case, the state of the Filter object is not modified.

        Any properties not specified in kwargs retain their previous values.

        There is no need to override this in derived classes.

        If the Filter is not currently attached to a FilterStage, this simply updates the
        stored data values; they will then be automatically applied at reconfigure() time,
        when attachStage() is called.

        See also:

          getConfiguration()

        """
        # We first validate all arguments, and then apply; this way, if the arguments contain an error,
        # the state of the Filter object is not modified.

        propertynames = self.getProperties()
        for key, value in list(kwargs.items()):
            if key not in propertynames:
                raise AttributeError("%s %s has no property named '%s'" % (self.__class__.__name__, self.name, key))

        for key, value in list(kwargs.items()):
            setattr(self, key, value)

    def getConfiguration(self):
        """Get all filter-specific settings.

        The return value is a dict, mapping property names (as strings) to the values
        they had at the time getConfiguration() was called.

        This can be used to store and later reload filter configuration values
        (assuming that no mutable objects are stored in the properties).

        If you want to get the default values, you can call reset()
        and then this.

        Example:

          # fpp is a FilterPipeline instance.
          #
          # f is a MyCoolEffectFilter, which has been added to fpp earlier.

          # Store current configuration
          storedSettings = f.getConfiguration()

          # ...do stuff...

          # Reload stored configuration
          f.setConfiguration(**storedSettings)

          # Add a copy of the filter with the same configuration into
          # another pipeline instance (such as when rendering
          # two independent views)
          #
          g = MyCoolEffectFilter(**storedSettings)
          myotherfpp.addFilterInstance(g)

        See also:

          setConfiguration()

        """
        result = {}
        for key in self.getProperties():
            result[key] = getattr(self, key)
        return result

    def loadShader(self, filename):
        """Convenience method to load a Cg shader .sha file placed in the phase_3/shaders directory

        Parameters:

          filename = string. Filename without the path.

        Return value:

          Passed through from Shader.load().

        """
        shaderObj = Shader.load("phase_3/shaders/" + filename)
        if shaderObj is None:
            self.cleanup()
            raise RuntimeError("Shader.load() for shader file '%s' failed in %s" % (filename, self.__class__.__name__))
        return shaderObj

    def getProperties(self):
        """Convenience method to return property names defined in the current filter type."""

        def isproperty(obj):
            return isinstance(obj, property)

        propertynames = [name for (name, value) in inspect.getmembers(self.__class__, isproperty)]
        #        # For future extension:
        #        propertynames = filter( lambda s: s[0] != "_", propertynames )  # ignore internal properties
        return propertynames

    def getTextureInfo(self, texName):
        """Obtain a texture object reference (and some metadata) by texture name.

        The textures are looked up as follows:

            a) If texName specifies a valid scene texture (is one of Filter.SCENETEXTURES),
               scene textures in the FilterStage the Filter is currently attached to.

            b) Otherwise, internal textures of Filters placed in that FilterStage.

               The lookup starts at this filter itself, and proceeds backwards toward the beginning
               of the FilterStage. In case of duplicate texture names, the most recent (largest sort)
               definition wins (it shadows any earlier definitions).

               (Requesting textures from earlier Filters in the same FilterStage is sometimes useful;
                see VolumetricLighting for an example.)

        Any textures defined in earlier FilterStages are considered as being out of date
        and cannot be retrieved.

        The current filter must be attached to a FilterStage (otherwise this raises RuntimeError).
        Calling this during attachStage() is fine.

        Parameters:
            texName = string. Name of the texture to retrieve, e.g. "color", "bloomOutput", ...

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

        If no texture named texName is seen by this filter, raises ValueError (propagated from FilterStage).

        """
        if self.filterStage is None:
            raise RuntimeError("In %s (%s): not currently attached to a FilterStage; cannot get textures." % (
            self.__class__.__name__, self.name))
        return self.filterStage.getTextureInfo(texName, caller = self)

    def getMangledName(self, originalName):
        """Get mangled name for given identifier.

        The mangled name is instance-specific, unique across all simultaneously existing objects.

        This is used e.g. to make the custom shader input names unique for each instance even when
        two or more copies of the same filter are placed in the same FilterStage.

        """
        # We must not use an underscore delimiter, because Shader.cxx will then choke on mangled
        # texpix_txmytexture_0x... and texpad_txmytexture_0x... names with the error
        # "parameter name has wrong number of words".
        #
        # See
        #   https://bugs.launchpad.net/panda3d/+bug/293479
        #
        # The names of k_ inputs are allowed to have underscores in them,
        # but magic names that request Panda to provide a built-in uniform are not.
        #
        return "%sMangled0x%x" % (originalName, id(self))

    def attachPipeline(self, pipeline = None):
        """Internal function. Attach the filter to a FilterPipeline.

        This is called from FilterPipeline.reconfigure().

        Correct call sequence is to attach to FilterPipeline first, then FilterStage (see attachStage()).

        There is no need to override this in derived classes; instead, see onAttachPipeline().


        This stores the pipeline reference, and calls onAttachPipeline() to let the filter implementation
        register input textures, custom shader inputs and aux bits.

        Having a stored pipeline reference means that updates to pipeline-level
        compile-time parameters in this Filter will affect the pipeline.


        This function is separate from the constructor, because filter objects
        are persistent across pipeline reconfigures.


        Parameters:

            pipeline    = FilterPipeline instance where this Filter instance is inserted
                          (i.e. the FilterPipeline instance whose scene texture and
                           and aux bits requirements this filter affects).

                          Must not be None.

        See also:

          detachPipeline()
          attachStage()
          detachStage()

          onAttachPipeline()
          onDetachPipeline()
          onAttachStage()
          onDetachStage()

        """
        # check parameters
        #
        if pipeline is None:
            raise ValueError("pipeline must be not None.")
        if not isinstance(pipeline, FilterPipeline.FilterPipeline):
            raise TypeError("pipeline must be an instance of FilterPipeline; got '%s'" % type(pipeline))

        # check call sequence constraints
        #
        if self.filterStage is not None:
            raise ValueError(
                "Cannot attach to a FilterPipeline while already attached to a FilterStage. Currently attached to FilterStage '%s'." % self.filterStage.stageName)
        if self.pipeline is not None:
            raise ValueError("Cannot attach to a FilterPipeline while already attached to a FilterPipeline.")

        # do actual work
        #        
        assert (self.filterStage is None)

        # Attaching to a FilterPipeline.
        #
        # This implies that setting any pipeline-level compile-time parameters
        # in this filter while attached will recompile the pipeline.
        #
        self.pipeline = pipeline

        # Register input textures, custom shader inputs and aux bits.
        #
        self.onAttachPipeline()

    def attachStage(self, filterStage = None):
        """Internal function. Attach the filter to a FilterStage.

        This is called from FilterStage.reconfigure().

        Correct call sequence is to attach pipeline first (see attachPipeline()), then filterStage.

        There is no need to override this in derived classes; instead, see onAttachStage().


        This configures the FilterStage input, and calls onAttachStage() to let the filter implementation
        set up its internal stages (if any).


        This function is separate from the constructor, because filter objects
        are persistent across pipeline reconfigures.


        Parameters:

            filterStage = FilterStage instance where this Filter instance is inserted
                          (i.e. the FilterStage instance whose compositing fshader
                           this filter goes into).

                          Must not be None.

        See also:

          detachStage()
          attachPipeline()
          detachPipeline()

          onAttachStage()
          onDetachStage()
          onAttachPipeline()
          onDetachPipeline()

        """
        # check parameters
        #
        if filterStage is None:
            raise ValueError("filterStage must be not None.")
        if not isinstance(filterStage, FilterStage.FilterStage):
            raise TypeError("filterStage must be an instance of FilterStage; got '%s'" % type(filterStage))

        # check call sequence constraints
        #
        if self.pipeline is None:
            raise ValueError(
                "Cannot attach to a FilterStage while not attached to a FilterPipeline. Attempted to attach to FilterStage '%s'." % filterStage.stageName)
        if self.filterStage is not None:
            raise ValueError("Cannot attach to FilterStage '%s' while already attached to FilterStage '%s'." % (
            filterStage.stageName, self.filterStage.stageName))

        # do actual work
        #
        assert (self.pipeline is not None)
        assert (isinstance(self.pipeline, FilterPipeline.FilterPipeline))

        # Attaching to a FilterStage.
        #
        self.filterStage = filterStage

        # Create any interQuads that are required by this filter.
        #
        # We do this when attaching to a FilterStage, because setting up the internal pipelining
        # for the internal stages requires the pipeline stage input textures to be available.
        #
        # Important to do this first before applying configuration; the interQuads will contain shaders,
        # which may be the target for some of the shader inputs in run-time parameters.
        #
        self.onAttachStage()

        # Compile internal shaders and assign them to interQuads.
        #
        # (This is done in user code, in onCompileInternalStages().)
        #
        self._needsCompile = True
        self.reconfigure()

    def connectOutput(self, outputQuad):
        """Assign the output quad into which the compositing shader renders.

        The quad is used solely to pass shader inputs; any inputs sent to "finalQuad"
        will be sent to the quad assigned here.

        This will nudge all setters to run, sending the current run-time parameter values
        to the quad immediately after the quad reference is stored.

        This is called internally by FilterStage.connectOutput().

        """
        # finalQuad = NodePath instance; output quad of filterStage.
        #
        #             This is used to pass custom parameters to the compositing fshader
        #             via setShaderInput() (in the property setters in derived classes).
        #
        #             Note that it is the finalQuad of *this pipeline stage*.
        #             It might not be "the" finalQuad of the whole pipeline,
        #             unless this filter resides in the last stage of the pipeline.
        #
        assert (outputQuad is not None)
        assert (isinstance(outputQuad, NodePath))

        # This comes after attachPipeline(); we have a pipeline
        assert (self.pipeline is not None)
        assert (isinstance(self.pipeline, FilterPipeline.FilterPipeline))

        self.finalQuad = outputQuad

        # Run all property setters to apply the current configuration.
        #
        # We need to do this because only each property setter itself knows
        # what needs to be done when the value of the property changes.
        #
        # Generally, they either set shader inputs (either to the compositing shader
        # of the pipeline stage, in self.finalQuad, or to an internal intermediate shader
        # in self.interQuads[idx] for some value of idx), or trigger a recompile
        # (if the value of a compile-time parameter has changed).
        #
        # What we actually want to do here is to send data to the shader inputs.
        #
        for s in self.getProperties():
            # Loopback to keep current value, while forcing setter side effects.
            setattr(self, s, getattr(self, s))

    def onAttachPipeline(self):
        """Filter-specific setup hook. Called from attach() when the filter is being attached to a FilterPipeline.

        Abstract method. Must be overridden in derived classes.

        In the very rare case that your filter does not need to do anything here,
        provide a blank implementation (just "pass"). (Examples: GammaAdjust and ColorInversion in MiscFilters.)

        The implementation must:

          - If the class inherits from an existing filter (not from the abstract Filter base class),
            call super(YourClass, self).onAttachPipeline().

            If the class inherits directly from Filter, then it MUST NOT call super(...).onAttachPipeline(),
            since this method is abstract in the base class, and calling it will raise NotImplementedError.

          - Register input textures and custom inputs needed by this filter in the compositing fshader.
            Use self.registerInputTexture() and self.registerCustomInput() to do this.

          - Register aux bits, if needed. Use self.requireAuxBits().

        See also:

          onDetachPipeline()
          onAttachStage()
          onDetachStage()

          attachPipeline()
          detachPipeline()
          attachStage()
          detachStage()

        """
        raise NotImplementedError(
            "Abstract method Filter.onAttachPipeline() called in %s %s" % (self.__class__.__name__, self.name))

    def onAttachStage(self):
        """Filter-specific setup hook. Called from attach() when the filter is being attached to a FilterStage.

        Default implementation is blank. Override this in derived classes if needed.
        Typically this is needed in filters that have internal stages.

        The implementation must:

          - If the class inherits from an existing filter (not from the abstract Filter base class),
            call super(YourClass, self).onAttachStage().

          - Allocate resources for internal processing stages, if needed.

            For example, a blur filter might have internal "blur-x" and "blur-y" passes
            that are applied to the pipeline stage input, and then their output is used
            in the compositing fshader of the pipeline stage.

            See also Filter.onCompileInternalStages().

            See BlurSharpenFilter for a complete example.

        See also:

          onDetachStage()
          onAttachPipeline()
          onDetachPipeline()

          attachStage()
          detachStage()
          attachPipeline()
          detachPipeline()

        """
        pass

    def detachStage(self):
        """Detach the filter from the FilterStage it is currently attached to.

        This is called from FilterStage.reconfigure().

        Correct call sequence is to detach FilterStage first, then pipeline (see detachPipeline()).

        There is no need to override this in derived classes; instead, see onDetachStage().

        This first calls self.onDetachStage() to run any custom cleanup, and then sets the
        current FilterStage input texture references (in this filter) as invalid, and cleans up
        any internal processing stages.

        The internal stages are cleaned up by setting self.get('texture') and self.interQuads to blank.

        See also:

          attachStage()
          attachPipeline()
          detachPipeline()

          onAttachStage()
          onDetachStage()
          onAttachPipeline()
          onDetachPipeline()

        """
        # This function must not raise exceptions; it is called during cleanup,
        # which may be called in response to exceptions.

        self.onDetachStage()
        self.texture = {}
        self.interQuads = []
        self.finalQuad = None
        self.filterStage = None
        self._needsCompile = False  # not attached to anything; no need to compile internal stages

    def detachPipeline(self):
        """Detach the filter from the FilterPipeline it is currently attached to.

        This is called from FilterPipeline.reconfigure().

        Correct call sequence is to detach FilterStage first (see detachStage()), then pipeline.

        There is no need to override this in derived classes; instead, see onDetachPipeline().

        This first calls self.onDetachPipeline(), and then discards the pipeline reference.
        (This implies that setting any pipeline-level compile-time parameters in the filter
        while not attached to a pipeline will not recompile any pipeline.)

        See also:

          attachPipeline()
          attachStage()
          detachStage()

          onAttachPipeline()
          onDetachPipeline()
          onAttachStage()
          onDetachStage()

        """
        # This function must not raise exceptions; it is called during cleanup,
        # which may be called in response to exceptions.

        # FilterStage must have been detached first.
        assert (self.filterStage is None)

        self.onDetachPipeline()
        self.pipeline = None

        # The "mergings" counter is used for logical stage -> render pass mapping in FilterPipeline.
        #
        # It counts by how many stages the filter has been bumped backward during the most recent pipeline setup,
        # if the filter is mergeable (see FilterPipeline._createFilterStages()).
        #
        # This and self.sort will be combined to a final sort value when the filters are sorted
        # within FilterStage (see FilterStage.reconfigure()).
        #
        self.mergings = 0

    def onDetachStage(self):
        """Filter-specific cleanup hook. Called from detachStage().

        This can be overridden in derived classes to perform any filter-specific cleanup.
        Internal stages, if any, are automatically cleaned up by detachStage().

        When detachStage() is called at __init__() time to create the data members and initialize
        them with blanks, self.pipeline and self.filterStage will be None.

        If onDetachStage() is overridden, the implementation:

          - Must free any dynamically allocated resources created in its overridden onAttachStage().

            Except: the most common resources needed by internal stages are cleaned up automatically.
            detachStage() already sets self.get('texture') and self.interQuads to blank, and FilterPipeline
            already calls FilterManager.cleanup() to delete the actual resources.

            If that is all you need, then your class does not need to provide a onDetachStage() function.
            This is the most common case.

          - Must not raise exceptions; this is a cleanup function. Cleanup may be called in response
            to exceptions.

          - Must not touch configuration parameters (properties)! This allows Filter instances to
            retain their configuration across pipeline reconfigures.

          - If the class inherits from an existing filter (not from the abstract Filter base class),
            it must call super(YourClass, self).onDetachStage() to ensure correct cleanup of any inherited
            dynamic resources.

        See also:

          onAttachStage()
          onAttachPipeline()
          onDetachPipeline()

          attachStage()
          detachStage()
          attachPipeline()
          detachPipeline()

        """
        pass

    def onDetachPipeline(self):
        """Filter-specific cleanup hook. Called from detachPipeline().

        This can be overridden in derived classes to perform any filter-specific cleanup.

        When detachPipeline() is called at __init__() time to create the data members and initialize
        them with blanks, self.pipeline and self.filterStage will be None.

        If onDetachPipeline() is overridden, the implementation:

          - Must free any dynamically allocated resources created in its overridden onAttachPipeline().

            Usually there are none; in that case, your class does not need to provide an onDetachPipeline() function.

          - Must not raise exceptions; this is a cleanup function. Cleanup may be called in response
            to exceptions.

          - Must not touch configuration parameters (properties)! This allows Filter instances to
            retain their configuration across pipeline reconfigures.

          - If the class inherits from an existing filter (not from the abstract Filter base class),
            it must call super(YourClass, self).onDetachPipeline() to ensure correct cleanup of any inherited
            dynamic resources.

        See also:

          onAttachPipeline()
          onAttachStage()
          onDetachStage()

          attachPipeline()
          detachPipeline()
          attachStage()
          detachStage()

        """
        pass

    def registerInputTexture(self, texName):
        """Register an input texture for the compositing fshader.

        Registered input textures will be inserted to the parameter list of the compositing fshader
        of the pipeline stage. They will also be inserted to the Cg function call for the filter
        that requested the register.

        Call this from setup() in derived classes to request textures to be provided to the compositing fshader.


        Including "color", "depth" or "aux" in the list in at least one filter that is enabled
        in the pipeline instructs the pipeline to configure itself to generate them.

        If you need a scene texture in internal stages only, use requireSceneTexture() instead;
        that will tell FilterPipeline to provide it, but won't request FilterStage to pass it
        into the compositing shader.

        (Registering a scene texture will also require it, so if you want e.g. "color" in the
         compositing shader, it is enough to register it.)


        Parameters:

          texName     = string. Name of texture to register. May be one of "color", "depth" or "aux"
                        (which are always available from the pipeline), or any internal texture
                        defined by the filter itself, or any internal texture defined by
                        another filter placed earlier in the same FilterStage.

                        In the case of an internal texture, the name must match the key used in
                        self.get('texture') (in the Filter subclass object), i.e. the texture name
                        given to Filter.createInternalTextures().

                        If you intend to use the "aux" (fragment normals) texture, be sure to set also
                        the ABOAuxNormal aux bit (see requireAuxBits()).

        Examples:

          Many filters want the color input texture, but are not interested in the pixel size:

            self.registerInputTexture("color")

          Some filters want both color and depth:

            self.registerInputTexture("color")
            self.registerInputTexture("depth")

          A cartoon inking filter might be interested in the fragment normals, with pixel size
          to compute whole-pixel offsets for normal map analysis:

            self.registerInputTexture("aux")
            self.requireAuxBits( AuxBitplaneAttrib.ABOAuxNormal )

        """
        # The user-defined setup(), which calls us, is triggered by FilterPipeline, so we can use asserts.
        assert (self.pipeline is not None)
        assert (isinstance(self.pipeline, FilterPipeline.FilterPipeline))
        self.pipeline._registerInputTexture(filterInstance = self, texName = texName)

    def registerCustomInput(self, inputType, inputName):
        """Register a custom shader input for the compositing fshader.

        Registered custom inputs will be inserted to the parameter list of the compositing fshader
        of the pipeline stage. They will also be inserted to the Cg function call for the filter
        that requested the register.

        Call this from setup() in derived classes to request your custom shader inputs to be created
        for the compositing fshader.


        Custom inputs for any internal stages must NOT be registered; this function is to be used
        only for inputs to the compositing fshader.

        When naming your custom inputs, keep in mind that potentially a large number of different filters
        may get synthesized into the same pipeline stage (FilterStage). The naming convention

          k_filtername_parametername

        is recommended to help the clarity of the generated shader source code (the viewing of which may be
        useful for debugging, extracting particular shader setups for use elsewhere, and just for technical
        curiosity). In any case, the variable names are automatically uniqified by name mangling, but the
        automatic mechanism uses the memory address of each filter instance to tag them, which by itself
        is not very human-readable.


        Note that custom input handling is performed in two separate parts:

          - Registration ensures that code for receiving the input is composed and inserted to the
            generated shader.

          - A run-time property supplies the data to the input (via the property's setter).
            This occurs at connectOutput() time, and while the filter is running, at any time
            when the run-time property is written to.


        Parameters:

          inputType = string. Low-level (Cg) datatype of the input. int, float, float4, ...

          inputName = string. The name of the parameter, exactly as it appears in the
                      compositing fshader code. (Do NOT strip the "k_" prefix if you use it.)

        Example:

          A cartoon ink filter might want to do:

            self.registerCustomInput("float4", "k_cartooncolor")

        """
        # The user-defined setup(), which calls us, is triggered by FilterPipeline, so we can use asserts.
        assert (self.pipeline is not None)
        assert (isinstance(self.pipeline, FilterPipeline.FilterPipeline))
        self.pipeline._registerCustomInput(filterInstance = self,
                                           customInputMetadata = {'inputName': inputName, 'inputType': inputType})

    def registerUpdatable(self):
        """Register this Filter as having shader inputs that must be updated automatically each frame.

        If you need this feature, call this from setup() in derived classes, and provide the
        actual update code by overriding update().

        """
        # The user-defined setup(), which calls us, is triggered by FilterPipeline, so we can use asserts.
        assert (self.pipeline is not None)
        assert (isinstance(self.pipeline, FilterPipeline.FilterPipeline))
        self.pipeline._registerUpdatable(filterInstance = self, updateFunction = self.onUpdate)

    def requireSceneTexture(self, texName):
        """Require a scene texture for this filter.

        This tells FilterPipeline to provide the requested scene texture (one of Filter.SCENETEXTURES).

        Call this from setup() in derived classes.

        Note: registering a scene texture as an input texture will automatically also require it,
        so if you have registered the scene texture for use in your compositing shader code,
        you don't need to call this.

        This function is provided for those cases where a particular scene texture is used only in
        the internal stages of a filter.

        """
        # The user-defined setup(), which calls us, is triggered by FilterPipeline, so we can use asserts.
        assert (self.pipeline is not None)
        assert (isinstance(self.pipeline, FilterPipeline.FilterPipeline))
        self.pipeline._requireSceneTexture(filterInstance = self, texName = texName)

    def requireAuxBits(self, bitmask):
        """Require aux bits for this filter.

        This tells FilterPipeline to enable the requested aux bits.

        Call this from setup() in derived classes to request aux data such as normals or the glow map.

        
        Aux bits indicate what additional information the filter wants from the main renderer,
        in conjunction with the pipeline stage input textures. How the information is passed
        depends on its type. Glow maps (ABOGlow) are passed in the alpha channel of the
        pipeline stage input color texture, while normal maps (ABOAuxNormal) are passed as an
        additional texture (called "aux").

        ABOAuxNormal must be enabled for the main renderer to generate the "aux" texture
        containing fragment normals. (Additionally, you'll want to register "aux" as an input texture;
        or if you only need it in your internal stages, require it instead of registering it.)

        ABOGlow must be enabled to fill the alpha channel of the "color" texture with the glow map.


        The default (if this is not called) is 0, which means all aux bits are off.

        If you need to enable several aux bits in the same filter, bitwise-OR them together with "|".
        Aux bits requested by different filter instances are automatically ORed together by FilterPipeline.

        Parameters:

          bitmask = bitmask made of panda3d.core.AuxBitplaneAttrib flags.

        """
        # The user-defined setup(), which calls us, is triggered by FilterPipeline, so we can use asserts.
        assert (self.pipeline is not None)
        assert (isinstance(self.pipeline, FilterPipeline.FilterPipeline))
        self.pipeline._requireAuxBits(filterInstance = self, bitmask = bitmask)

    def synthesizeCompositor(self):
        """Synthesize and return fragment shader implementation.

        Interface method. There is no need to override this in derived classes.

        The return value is passed through from onSynthesizeCompositor().

        """
        # Currently we don't need to do anything special here.
        # By having this method, we just reserve the possibility to add template code later.
        #
        return self.onSynthesizeCompositor()

    def onSynthesizeCompositor(self):
        """Synthesize and return fragment shader implementation.

        Abstract method.

        Override this in derived classes to provide the implementation of shader code generation.


        Return value:
          Tuple:
            (funcname, code, comment, ...)
          where
            funcname = string, bare function name.

                       This function will be called in the compositing fshader of the FilterStage
                       where the Filter is attached.

            code     = string, implementation of the function, in Cg code.

                       Treat the top level as having zero indentation; top-level indentation
                       will be inserted by FilterStage when it writes the shader.

                       Terminate by a newline to make the resulting source more readable.

            comment  = string or None. Can be used to provide a short comment about what the function does.
                       This will be pasted at the call site (just before the function call) and
                       at the definition site (just before the definition of the function).
                       Must be a valid comment, i.e. either wrap it in /* */ or begin each line by // .

                       If not None, must be terminated by a newline.

                       This should be one line, or two lines at most. For longer comments, it is recommended to
                       include them with the code, so that they will end up inside the function implementation.

                       Comments can be useful for debugging and examining the framework. Observe that
                       the source code of the currently active compositing shader can be retrieved
                       by reading the property FilterStage.shaderSourceCode.

            ...      = one or more optional custom functions that are used by your filter implementation.
                       Each item is a string, giving the complete function in Cg code.

                       Name mangling for the custom functions must be done manually to ensure that the
                       function names are unique, in case several filters try to provide a function
                       with the same name. Each filter instance must provide its own implementation,
                       because the filters are allowed to generate completely different code
                       depending on their configuration options.

                       Most filters do not need to define any custom functions.

                       See FilmNoise for an example.


        The pipeline automatically composes the final compositing fshader, using the shader code
        defined by onSynthesizeCompositor() in the enabled filters. The function calls are ordered
        using the sort value of the filters.

        For each filter, the function declaration and the call to the function in the compositing fshader
        are generated automatically by the pipeline, using the data sent by registerInputTexture()
        and registerCustomInput() at setup() time.

        Explicitly:

          // ...optional custom functions if any...

          // ...comment of myFunction...
          inline float4 myFunction( /* params */,
                                    float4 pixcolor )
          {
              // ...implementation of myFunction...

              return pixcolor;
          }

          void fshader( /* all params of current FilterStage */ )
          {
              // ...other code...

              // ...comment of myFunction...
              pixcolor = myFunction( /* params */,
                                     pixcolor );
        
              // ...other code...
          }

        The string "myFunction", the implementation of myFunction, and the comment of myFunction
        (or None if no comment) are what must be returned by onSynthesizeCompositor(); all the rest is
        automatically generated, including the params list.

        Observe that fshader() expects that myFunction() will modify existing pixcolor,
        not completely overwrite it.

        See existing filters for examples.


        Conventions:

          The implementation must apply the current values of any relevant (FilterStage-level or
          FilterPipeline-level) compile-time parameters stored in the properties of self.

          All filters must treat the input color alpha channel as if it contains a glow map.
          This is to ensure correct operation also when AuxBitplaneAttrib.ABOGlow is enabled.

          The code must respect previous modifications to pixcolor in the same pipeline stage,
          to avoid overwriting results from other filters earlier in the stage. A filter for which
          this is not possible should be placed as the first one in the pipeline stage,
          by setting sort=0 and isMergeable=False.

          The implementation must explicitly call

            pixcolor = saturate(pixcolor);

          at the end if it wants to do that. The color is processed through a temporary variable
          to prevent unintended saturation while more processing is still being done. Only the final result
          (from the last filter in the FilterStage) is saturated automatically (this happens implicitly,
          by storing the result in the variable corresponding to the output color semantic in the fshader).

          Currently it is not possible to pass a non-saturated color from a FilterStage to the next FilterStage.

        """
        raise NotImplementedError(
            "Abstract method Filter.onSynthesizeCompositor() called in %s %s" % (self.__class__.__name__, self.name))

    def reconfigure(self):
        """Compile shaders for internal stages and assign them to interQuads.

        Interface method.

        This provides the logic to disable recompiles if not currently attached
        to a FilterStage (in which case the interQuads do not exist),
        or if self._needsCompile is not set.

        This also clears the self._needsCompile flag if self.onCompileInternalStages() runs successfully.

        To implement the actual shader compilation code, override onCompileInternalStages().

        The interQuads must have been created in setup().


        See also:

          onAttachStage()
          onCompileInternalStages()
        
        """
        # Compiling the shaders for the interQuads requires that the Filter is attached
        # to a FilterStage, because only then the interQuads (to which the user code
        # will try to set the shaders) will exist.
        #
        # Trying to call reconfigure() when this requirement is not satisfied
        # is not an error, but the call will do nothing.
        #
        # Note that in such a case, self._needsCompile is left in its current state,
        # and hence a later reconfigure() (after self.filterStage becomes available)
        # may perform a compile that has been left pending earlier.
        #
        if self.filterStage is None:
            return

        # Compile only if needed.
        #
        if not self._needsCompile:
            return

        self.onCompileInternalStages()
        self._needsCompile = False

    def onCompileInternalStages(self):
        """Compile shaders for internal stages and assign them to interQuads.

        Implementation method.

        Default implementation is blank; this is fine for filters which do not need internal stages.

        Override this method in derived classes if (and only if) you need internal stages
        in your filter.

        This method should load or (re-)compile the internal shaders, and assign them to the
        interQuads that have been created in your overridden onAttachStage().

        The implementation must take into account the current values of the Filter-level
        compile-time parameters defined by that specific Filter (and any of its ancestors,
        if applicable; the abstract Filter base class itself has no such parameters).

        There is no need to check the state of, or set, any compile control flags (such as _needsCompile)
        in your code; the interface method reconfigure() already does that, and only calls onCompileInternalStages()
        when safe and necessary.


        By design, this method has no return value.

        If an error occurs (e.g. renderQuadInto() fails), the implementation should raise
        an appropriate exception with a descriptive error message.

        On an error that can only arise if there is a strictly internal bug in the subclass's
        own code, the implementation should fail an assert.


        See also:

          onAttachStage()

        """
        pass

    def createInternalTextures(self, *args):
        """Create textures for internal stages.

        This is a convenience method, meant to be called from an overridden onAttachStage()
        in filters with internal stages.

        The created Texture objects will become available in self.get('texture'),
        keyed by the names given.

        These same names can then be used, if necessary, in a registerInputTexture()
        call to configure the corresponding texture to be sent to the compositing fshader.
        Typically a filter with internal stages wants its final internal texture to be
        provided into the compositing fshader.

        The names are also recognized by getTextureInfo().

        There is no need to override this in derived classes.

        Parameters:

            Texture names.

        Example:

            self.createInternalTextures( "mycooltex0", "mycooltex1" )

        """
        # Only non-mergeable filters are allowed to create internal textures.
        #
        # The idea is that usually, in cases where it is meaningful to create an internal texture,
        # the filter must be able to access input pixels other than the one being processed.
        # Hence, it must see up-to-date information also at those other pixels - which means
        # that the filter must be non-mergeable.
        #
        # This has also the desirable feature that "borrowing" another filter's internal texture using
        # Filter.getTextureInfo() will never fail mysteriously, because the filter from which the
        # internal texture is being borrowed will, necessarily (because it is non-mergeable due to having
        # internal textures), reside in exactly that FilterStage where the user placed it (i.e. in the same
        # FilterStage as the borrower, as textures cannot be borrowed across FilterStage borders).
        #
        if self.isMergeable:
            raise RuntimeError(
                "In %s %s: only non-mergeable filters may have internal textures, but this filter is marked mergeable." % (
                self.__class__.__name__, self.name))

        for texName in args:
            self.get('texture')[texName] = FilterUtils.makeFilterTexture(texName)

    def onUpdate(self):
        """Update hook.

        Abstract method.

        Override this in derived classes to update those shader inputs that must be updated every frame.

        If your filter does not have any shader inputs requiring per-frame updates,
        then there is no need to provide this method.

        If self.registerUpdatable() has been called in setup(), this is called automatically
        just before each frame is drawn.

        If not, this method is ignored.

        """
        raise NotImplementedError(
            "Abstract method Filter.onUpdate() called in %s %s" % (self.__class__.__name__, self.name))
