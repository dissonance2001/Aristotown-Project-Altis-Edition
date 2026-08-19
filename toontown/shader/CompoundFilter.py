"""Filter API adapter for modular filters that contain other Filters.

To the outside, this exposes the same API as Filter, but internally the CompoundFilter consists
of a list of Filters (any Filters - also other CompoundFilters if desired).

The key idea is that those filters, whose internal shaders are reusable as building blocks for other filters
(e.g. bloom, blur), can be split into reusable modular parts. These parts can then be assembled into a
compound filter inherited from CompoundFilter, which encapsulates them into a single package, which is
easier to use than instantiating each part separately and adding them to the pipeline manually.

For example, blur is usable as an intermediate step in bloom, while bloom itself is usable as a preprocessor
for volumetric lighting.

The compositing step can be either done by the last contained filter, or custom-provided as for
any other Filter. The contained filters are mainly intended to generate internal textures
in a modular manner: being Filters in their own right, but also usable as building blocks
to construct more complex filters.


The usual texture name lookup rules apply, with the modification that there is an internal pre-lookup
inside the CompoundFilter before the usual lookup proceeds.

Even inside the CompoundFilter, the most recent definition (later in self.filters) masks any earlier ones.
At onAttachPipeline() time, each filter starts the texture name lookup from itself, proceeding backward in self.filters,
and then to filters earlier in the same FilterStage.

At attachStage() time, the latest definition under each name (in this CompoundFilter) will be exported
to the FilterStage level so that later filters can see it. The latest definition is also available
in the compositing shader for the CompoundFilter.

If the CompoundFilter defines its own internal stages, those are considered to come *before*
all the contained filters.

The bottom line is that this should work as expected even if the contained filters define duplicate
texture names.

"""

import types

from toontown.shader.Filter import Filter, TextureInfo, SCENETEXTURES
from functools import reduce


class CompoundFilter(Filter):
    """Base class for building complex filters that use the internal textures of other filters
    as building blocks.

    This class "packages" a compound filter into one object, making it easier to
    manage its sorting (in applications that use the pipeline), and to make it self-documenting
    how to correctly set up and connect the parts for any particular compound filter.


    Within the CompoundFilter, the contained filters will be ordered in the order they appear
    in self.filters (as added by the user-defined createContainedFilters()); their "stageName" and "sort"
    (as well as "isMergeable") are ignored.

    The "stageName" and "sort" values of the CompoundFilter itself will be used to determine
    its placement within the pipeline.

    A CompoundFilter is always non-mergeable (isMergeable=False).


    As usual, synthesize() can be overridden to provide a custom code snippet for the compositing fshader,
    and onAttachPipeline() used to register input textures (now including those defined by the contained filters),
    custom inputs, and an update method. (If your class provides onUpdate(), the implementation *must* call
    super's onUpdate() to ensure that the contained filters are updated correctly.)

    The internal textures created by the contained filters will be available; in case of duplicate
    texture names, the most recent definition of each.

    Also internal textures created locally in the CompoundFilter itself will be available.
    These are considered to come *before* the internal textures of all contained filters
    (so any textures of the same name in the contained filters will mask them).


    Unique to CompoundFilter, there is a default compositor: if self._customCompositing is False,
    the synthesizeCompositor() of the last contained filter will be used to provide the compositing shader.
    Similarly, then the inputs and textures registered by the last contained filter will be registered
    (for compositing) by the compound filter.

    This can be useful in cases like VolumetricLighting, which just wants to include another filter
    as a preprocessor, the compositing code (and its shader inputs) being fine as it is.
    (This use case basically requires that the last filter exposes some texture selection parameters,
     like "source" in VolumetricLighting - which can then be set up by the compound filter
     to use an appropriate texture from some contained filter.)

    self._customCompositing is a design-time flag, which must be set in the derived class's __init__(),
    *after* calling super's init. The default value is False.


    In either case:

        Any scene textures "required" either explicitly or implicitly (via registerInputTexture())
        by *any* contained filter will be automatically "required" by the CompoundFilter.

        Any aux bits "required" by *any* contained filter will be automatically "required"
        by the CompoundFilter.

        Any update() registrations (registerUpdatable()) done by *any* contained filter will be active.
        This ensures that any dynamic parameters will be updated correctly (whether or not they affect
        the internal stage texture generation).


    Filter parameters *must* be re-published in the CompoundFilter itself, to provide a flat interface.
    As usual, parameters must be implemented as Python properties.

    Each setter implementation should just write to the appropriate contained filter's property,
    causing the original setter to be called.


    Technically, this works as follows:


    - CompoundFilter overrides Filter's interface methods, providing modified versions that operate
      on the contained filters, and seen from the outside, appear just like any other Filter.


    - Then __init__() goes to punch some ducks, re-routing callbacks for the contained filter instances
      through the CompoundFilter.

      This is done by replacing the contained filters' instance methods getMangledName(), getTextureInfo(),
      registerInputTexture(), registerCustomInput() and registerUpdatable() by CompoundFilter-aware
      implementations, to make them do the right thing in this somewhat different operating environment.
      Only the actual Filter instances contained in the current CompoundFilter instance are modified.

      The rerouting effectively makes the CompoundFilter instance itself register the inputs and textures,
      and to use the compound filter's id for all mangled identifier names. This is how FilterStage and
      FilterPipeline expect a Filter to behave. (Note that mangled names are only needed in the compositing
      shader and its inputs; hence there won't be any conflicts, because we use the compositing shader
      of at most *one* contained filter (the last one).)

      Without the duck punching, any texture or custom input registrations performed by the contained filters
      would get ignored, because FilterPipeline._propagateRegistrationData() only iterates over filters
      actually placed in the stages (i.e. it does not see any filters contained inside other filters).
      Similarly, FilterStage only iterates over filters in self.filters.

      (The thing is that CompoundFilter contains Filters, which have no idea of the existence of such a thing
       as a CompoundFilter. The possibilities are to either change Filter so that it knows about that,
       or to dynamically replace the instance methods; this does the latter.)

    """

    def __init__(self, **kwargs):
        self.updateFunctions = {}
        self.filters = []

        # This flag tells synthesizeFragmentShader() whether the user class provides its own compositing shader.
        # If False (default), the compositing logic of the last contained filter will be used.
        #
        self._customCompositing = False

        # If someone tries to instantiate this abstract base class directly, some name must be available
        # for the NotImplementedError raised by createContainedFilters(). The default name is initialized
        # by Filter.onReset() later (via super's init).
        #
        self._name = "[being initialized]"

        # This (user code) creates the filters in the correct order.
        #
        # We must do this before super's init so that super can then call resetConfiguration()
        # and load in our parameters (which may be sent to contained filters, through *our* properties)
        # as usual.
        #
        self.createContainedFilters()

        super(CompoundFilter, self).__init__(**kwargs)

        # Go punch some ducks.
        #
        # We need to redefine getMangledName(), getTextureInfo() and register*() methods of the contained
        # filters to perform special handling, because FilterPipeline and FilterStage will ignore any
        # registrations from contained filters. We want the pipeline to see the registered textures and inputs
        # as belonging to the CompoundFilter instance.
        #
        # (FilterStage only iterates over filters in self.filters; FilterPipeline._propagateRegistrationData()
        #  only iterates over filters actually placed in the stages.)
        #
        # We freeze "compoundFilterInstance" to point to us at definition time.
        #
        def cfGetMangledName(self, originalName, compoundFilterInstance=self):
            """CompoundFilter-aware getMangledName(). For original, see Filter.getMangledName()."""
            # We mangle with the CompoundFilter's identifier, not with that of the contained filter itself.
            return compoundFilterInstance.getMangledName(originalName)

        def cfGetTextureInfo(self, texName, compoundFilterInstance=self):
            """CompoundFilter-aware getTextureInfo(). For original, see Filter.getTextureInfo()."""
            # We must redefine this, too, because caller (for FilterStage.getTextureInfo())
            # would otherwise be invalid when a contained filter calls this.
            #
            # (FilterStage.getTextureInfo(), which is called by Filter.getTextureInfo(),
            # requires the filter to be directly present in the stage; it doesn't know
            # about contained filters.)
            #
            # We also need to do the internal lookup inside the CompoundFilter
            # before we let the call proceed.

            # For non-scene textures, try first looking up in the contained filters
            # to implement name masking inside the CompoundFilter.
            #
            if texName not in SCENETEXTURES:
                # This is always called from one of the contained filters.
                start = compoundFilterInstance.filters.index(self)
                for g in compoundFilterInstance.filters[start::-1]:
                    # This should work also with nested CompoundFilters,
                    # because CompoundFilter "exports final names" via self.get('texture').
                    #
                    # The most recent definition of any texName is guaranteed to be exported
                    # after attachStage() has been run.
                    #
                    if texName in g.get('texture'):
                        tex = g.get('texture')[texName]
                        isExported = False
                        for exportedTex in list(compoundFilterInstance.get('texture').values()):
                            if exportedTex is tex:
                                isExported = True
                                break

                        if isExported:
                            # This is an exported texture visible to FilterStage,
                            # so we can let FilterStage fill in the info.
                            #
                            # (compoundFilterInstance sets itself as caller and calls FilterStage.getTextureInfo().)
                            #
                            # It is actually important to do so, because we might be being called
                            # in synthesize(), in which case the variable naming metadata
                            # *generated by FilterStage* is needed.
                            #
                            return compoundFilterInstance.getTextureInfo(texName)
                        else:
                            # This is a texture whose name has been masked by a more recent one,
                            # or alternatively, we are not yet attached (so compoundFilterInstance.get('texture')
                            # is not yet filled in).
                            #
                            # We do the same thing as FilterStage does in similar cases: we leave the
                            # metadata blank, and return only the texture instance reference and owner.
                            # This is useful for sending shader inputs in onAttachStage(), where only the
                            # texture instance reference is needed.
                            #
                            # We provide owner=compoundFilterInstance just to distinguish it from a scene texture.
                            # This value is chosen so that it remains stable for exported textures,
                            # after the export occurs at attach time.
                            #
                            # The owner value returned here is not very useful; if this is not an exported
                            # texture, calling owner.getMangledName(texName) produces an identifier
                            # that won't be actually available in the compositing shader.
                            # (The onAttachStage() methods won't do that, though.)
                            #
                            return TextureInfo( varname  = None,
                                                texpix   = None,
                                                texpad   = None,
                                                texcoord = None,
                                                texture  = tex,
                                                owner    = compoundFilterInstance )

            # Not our own texture; let FilterStage find it.
            #
            return compoundFilterInstance.getTextureInfo(texName)

        def cfRegisterInputTexture(self, texName, compoundFilterInstance=self):
            """CompoundFilter-aware registerInputTexture(). For original, see Filter.registerInputTexture()."""
            if not compoundFilterInstance._customCompositing:
                # We register the texture to the compound filter instance, not to the contained filter instance.
                # Only the last contained filter participates in compositing.
                idx = compoundFilterInstance.filters.index(self)
                if idx == len(compoundFilterInstance.filters) - 1:
                    compoundFilterInstance.registerInputTexture(texName)

            # When using custom compositing, all needed registrations (for the compositing shader)
            # must be done by the onAttachPipeline() of the class derived from CompoundFilter.

            # This step is normally done in FilterPipeline, but here we must do it manually
            # to trigger it also for scene textures needed by filters other than the last one.
            # (Multiple calls to requireSceneTexture() for the same texture - even by the same filter - are allowed.)
            #
            if texName in SCENETEXTURES:
                compoundFilterInstance.requireSceneTexture(texName)

        def cfRegisterCustomInput(self, inputType, inputName, compoundFilterInstance=self):
            """CompoundFilter-aware registerCustomInput(). For original, see Filter.registerCustomInput()."""
            if not compoundFilterInstance._customCompositing:
                # We register the custom input to the compound filter instance, not to the contained filter instance.
                # Only the last contained filter participates in compositing.
                idx = compoundFilterInstance.filters.index(self)
                if idx == len(compoundFilterInstance.filters) - 1:
                    compoundFilterInstance.registerCustomInput(inputType, inputName)

        def cfRegisterUpdatable(self, compoundFilterInstance=self):
            """CompoundFilter-aware registerUpdatable(). For original, see Filter.registerUpdatable()."""
            compoundFilterInstance.updateFunctions[self] = self.onUpdate
            # Make the CompoundFilter itself updatable, so that our update() gets called.
            compoundFilterInstance.registerUpdatable()

        # Replace the instance methods with the CompoundFilter-aware ones
        # (but only for our contained filter instances).
        #
        for f in self.filters:
            f.getMangledName       = types.MethodType(cfGetMangledName,       f, f.__class__)
            f.getTextureInfo       = types.MethodType(cfGetTextureInfo,       f, f.__class__)
            f.registerInputTexture = types.MethodType(cfRegisterInputTexture, f, f.__class__)
            f.registerCustomInput  = types.MethodType(cfRegisterCustomInput,  f, f.__class__)
            f.registerUpdatable    = types.MethodType(cfRegisterUpdatable,    f, f.__class__)

        # The _needsCompile flag of the CompoundFilter itself is meaningless.
        #
        self._needsCompile = False

        # Make the instance name more informative
        #
        containedFilterNamesList   = [obj.__class__.__name__ for obj in self.filters]
        containedFilterNamesString = reduce( lambda a, b: a + ", " + b, containedFilterNamesList )
        self.name = "(compound of %s) %s" % (containedFilterNamesString, self.name)

    # TODO: How to let derived classes to select *at runtime* which filters to create? (useful for e.g. changing
    # TODO: blur type at instance creation time if there are several different blur filters exposing the
    # TODO: same parameters.)
    # TODO:
    # TODO: We cannot just pass through kwargs from __init__(), because super's init will complain about
    # TODO: any extra parameters that do not correspond to properties of the current instance - so in the
    # TODO: current implementation, kwargs cannot contain anything that is meant just for createContainedFilters()
    # TODO: (or also, anything meant for any of the contained filters).
    #
    def createContainedFilters(self):
        """Abstract method. Called in __init__(). Override this in derived classes.

        The implementation must create the contained filters and append them to self.filters
        in the desired order.

        Note that you also need to provide properties for those parameters of the contained filters
        that you would like to be accessible in your compound filter. (In the property setters,
        it is enough to just write to the relevant property of the appropriate contained filter,
        which will then invoke the original setter for that property.)

        Example:

            def createContainedFilters(self):
                self.bloom = Bloom()
                self.volumetricLighting = VolumetricLighting()

                # The ordering of the append()s defines filter ordering.
                #
                # This affects buffer creation order (for internal stages)
                # and texture name lookup.
                #
                self.filters.append( self.bloom )
                self.filters.append( self.volumetricLighting )

            # In other methods (especially property setters), you can then access the filters created in
            # this example as self.bloom and self.volumetricLighting. Only CompoundFilter itself
            # is interested in self.filters.

        """
        # TODO: pass (no exception in __init__() if someone instantiates this), or raise NotImplementedError?
        raise NotImplementedError("Abstract method CompoundFilter.createContainedFilters() called; current instance is %s %s" % (self.__class__.__name__, self.name))


    #################################################
    # Implementations for abstract methods of Filter
    #################################################

    def onAttachPipeline(self):
        """Dummy method. This just un-abstracts onAttachPipeline() so that it is valid to attachPipeline() the CompoundFilter.

        The implementation is a no-op, because CompoundFilter itself doesn't need to do anything in onAttachPipeline().
        In a CompoundFilter, the interesting things happen in the onAttachPipeline() calls of the individual contained
        filters, called from the overridden attachPipeline() (via each filter's attachPipeline()).

        If your derived class sets self._customCompositing=True, then it must provide onAttachPipeline();
        otherwise no need.

        """
        if self._customCompositing:
            raise NotImplementedError("In %s %s: a filter derived from CompoundFilter with self._customCompositing=True must override onAttachPipeline(), but this one does not." % (self.__class__.__name__, self.name))

        # If the compositing shader is borrowed from the last contained filter,
        # CompoundFilter itself doesn't need to do anything here.


    def onAttachStage(self):
        """Dummy method. This just un-abstracts onAttachStage() so that it is valid to attachStage() the CompoundFilter.

        The implementation is a no-op, because CompoundFilter itself doesn't need to do anything in onAttachStage().
        In a CompoundFilter, the interesting things happen in the onAttachStage() calls of the individual contained
        filters, called from the overridden attachStage() (via each filter's attachStage()).

        If your derived class sets self._customCompositing=True, then it must provide onAttachStage();
        otherwise no need.

        """
        if self._customCompositing:
            raise NotImplementedError("In %s %s: a filter derived from CompoundFilter with self._customCompositing=True must override onAttachStage(), but this one does not." % (self.__class__.__name__, self.name))

        # If the compositing shader is borrowed from the last contained filter,
        # CompoundFilter itself doesn't need to do anything here.


    def onSynthesizeCompositor(self):
        """Synthesize this filter's code snippet for the compositing fragment shader.

        If your derived class sets self._customCompositing=True, then it must provide synthesizeCompositor();
        otherwise no need.

        """
        if self._customCompositing:
            raise NotImplementedError("In %s %s: a filter derived from CompoundFilter with self._customCompositing=True must override synthesizeCompositor(), but this one does not." % (self.__class__.__name__, self.name))

        # This doesn't need to do anything; synthesizeFragmentShader() calls the
        # corresponding method for the last contained filter if custom compositing is off.


    def onUpdate(self):
        """Update shader inputs that must be updated at each frame.

        The contained filters are not directly seen by FilterStage, so CompoundFilter propagates the onUpdate()
        to any contained filters that have registered themselves as updatable.

        If you override this, be sure to call  super(YourClass, self).onUpdate()  in your implementation
        so that the contained filters' update() methods will get called if needed.

        """
        for f in self.filters:  # this enforces the filter ordering.
            if f in self.updateFunctions:
                self.updateFunctions[f]()


    ###############################
    # Overridden interface methods
    ###############################

    def resetConfiguration(self):
        """CompoundFilter-aware resetConfiguration(). For original, see Filter.resetConfiguration()."""

        # We must reset the filters first, because the CompoundFilter itself may override default values
        # that are set in the contained filters (by assigning to the properties exposed in CompoundFilter).
        #
        for f in self.filters:
            f.resetConfiguration()
        super(CompoundFilter, self).resetConfiguration()

        # CompoundFilter is a base class; no default stageName or sort

        # CompoundFilter is always non-mergeable (it has internal textures;
        # if it doesn't, there is no point in creating a CompoundFilter)
        #
        self.isMergeable = False


    def attachPipeline(self, pipeline=None):
        """CompoundFilter-aware attachPipeline(). For original, see Filter.attachPipeline()."""

        # We must attach self before attaching contained filters, so that compoundFilterInstance.pipeline
        # will be available in cfRegister*(), and so that compoundFilterInstance.getTextureInfo()
        # (which is called from cfGetTextureInfo()) will have access to compoundFilterInstance.filterStage.
        #
        # This has the implication that the CompoundFilter's own internal stages render *before*
        # the internal stages of the contained filters, because they are initialized first.
        # It would be more useful to have this the other way around, but that is difficult to implement cleanly.
        #
        # (It is possible to work around this by defining another filter that contains the desired internal stages
        #  and the compositor, and then use that filter as the compositor instead of _customCompositing.)
        #
        super(CompoundFilter, self).attachPipeline(pipeline)

        # This does the interesting things: registrations and requires.
        #
        for f in self.filters:
            f.attachPipeline(pipeline)


    def attachStage(self, filterStage=None):
        """CompoundFilter-aware attachStage(). For original, see Filter.attachStage()."""

        # Attach self before attaching contained filters.
        #
        super(CompoundFilter, self).attachStage(filterStage)

        # This does the interesting things: internal texture allocation / internal shader setup.
        #
        for f in self.filters:
            f.attachStage(filterStage)

        # To support texture borrowing from CompoundFilter, "export final names": copy the texture references
        # from all contained filters to us. This lets FilterStage.getTextureInfo() see them.
        #
        # In case of duplicate texture names, walking the filters in an ordered manner leaves only the
        # most recent definition standing - that is the one that will be exported (and will be available
        # for other filters later in the same FilterStage).
        #
        # This should work also for nested CompoundFilters; the above call to f.attachStage() invokes this
        # same method for the other instance, and it will export its textures before our instance reaches
        # this point.
        #
        for f in self.filters:
            self.get('texture').update(f.get('texture'))


    def connectOutput(self, outputQuad):
        """CompoundFilter-aware connectOutput(). For original, see Filter.connectOutput()."""
        super(CompoundFilter, self).connectOutput(outputQuad)

        if not self._customCompositing:
            # Only the last contained filter participates in compositing.
            #
            # Not connecting the others to the output saves Panda from keeping track of a bunch of
            # unused shader inputs, and avoids possible name conflicts in the shader inputs
            # (since now only one of our filters will "push" its inputs to the outputQuad).
            #
            # (Note that getMangledName() of the contained filters is redefined to mangle using *our* id,
            #  as FilterStage expects. Hence a duplicate name across different contained filter instances
            #  would cause a duplicate mangled name.)
            #
            self.filters[-1].connectOutput(outputQuad)


    def detachStage(self):
        """CompoundFilter-aware detachStage(). For original, see Filter.detachStage()."""

        # These will be registered again during next attachStage() (by cfRegisterUpdatable()).
        self.updateFunctions = {}

        for f in self.filters:
            f.detachStage()
 
        # Note that this will discard texture references, so we don't need to do that manually.
        #
        # Also, there is no need to distinguish between our own internal textures
        # and those from contained filters, since we're just discarding references.
        #
        super(CompoundFilter, self).detachStage()


    def detachPipeline(self):
        """CompoundFilter-aware detachPipeline(). For original, see Filter.detachPipeline()."""

        for f in self.filters:
            f.detachPipeline()
 
        super(CompoundFilter, self).detachPipeline()


    def synthesizeCompositor(self):
        """CompoundFilter-aware synthesizeCompositor(). For original, see Filter.synthesizeCompositor().

        If self.customCompositing == True:
            This works as usual.

        If self.customCompositing == False:
            This requests the last contained filter to synthesize code for the compositing shader.
            The onSynthesizeCompositor() methods of any earlier contained filters are ignored.

        """
        if self._customCompositing:
            # User-defined synthesize() in derived class.
            #
            # As a fallback, our own synthesize() raises NotImplementedError.
            #
            return super(CompoundFilter, self).synthesizeCompositor()
        else:
            # In this case we don't need our own synthesize(), because we only want the compositing shader code
            # from the last contained filter.
            #
            # Hence we do not call super.
            #
            # The overriding of getMangledName() and getTextureInfo() by CompoundFilter-aware versions
            # (in our __init__()) makes the filter's synthesize() do what we want.
            #
            return self.filters[-1].synthesizeCompositor()


    def reconfigure(self):
        """CompoundFilter-aware reconfigure(). For original, see Filter.reconfigure()."""

        # Account for the possibility that the derived class might define some new internal stages
        # in the compound filter.
        #
        # Usually this just returns immediately, since in the more common case where we have
        # no internal stages of our own, self._needsCompile will remain False.
        #
        super(CompoundFilter, self).reconfigure()

        # Then reconfigure all contained filters.
        #
        # We do not check the _needsCompile flag here, because in a CompoundFilter, the top-level
        # _needsCompile flag and the contained filter's _needsCompile flags are independent,
        # each referring only to its local level.
        #
        # In case of nested CompoundFilters, this proceeds recursively.
        #
        for f in self.filters:
            f.reconfigure()

