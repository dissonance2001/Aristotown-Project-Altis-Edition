"""FilterPipeline implements the postprocessing filter pipeline, managing filters and render passes.

This is the main part of the user API for the postprocessing filter system.

"""



from toontown.shader.FilterManager import FilterManager
from toontown.shader.FilterStage import FilterStage
from toontown.shader.Filter import Filter, SCENETEXTURES

from toontown.shader import FilterUtils

from toontown.shader.StageInitializer import StageInitializer


class FilterPipeline(object):
    """This class provides the main part of the user API for the postprocessing filter system.

    See methods:

      addFilterInstance()
      removeFilterInstance()

    Internally, the main responsibilities of this class are to manage Filter instances and
    render passes (FilterStage instances), and to dynamically construct actual render passes
    from the logical stages (self.knownStages) by examining the configuration of enabled filters.
    Also the fullscreen textures and quads are managed by FilterPipeline (with the help of
    FilterManager for the low-level work).

    """

    def __init__(self, win, cam, name = None):
        """Constructor.

        Parameters:

          win = Window (or buffer e.g. from base.win.makeTextureBuffer()) to postprocess by this pipeline.

          cam = Camera that is currently either rendering "win", or rendering some display region of "win"
                (for windows having multiple DisplayRegions). FilterManager will automatically find the
                DisplayRegion associated with the specified camera.

          name = optional human-readable name for this FilterPipeline. Used in error messages and ls().

        The parameters "win" and "cam" are passed as-is to FilterManager (and they must not be None);
        see its documentation for a detailed explanation.

        Example:

          To apply postprocessing filters to the main window in a typical application using DirectStart,
          do this somewhere in your class inheriting from DirectObject:

            self.fpp = FilterPipeline(base.win, base.cam)

          Storing the FilterPipeline instance in a member of self guarantees that it will stay alive
          when your setup method returns.

          If you need to, you can later delete the pipeline by simply

            del self.fpp

          and the window should return to its original state.

        """
        super(FilterPipeline, self).__init__()

        # We use FilterManager to manage the actual render-to-quads and their textures.
        #
        self.manager = FilterManager(win, cam)

        # To FilterPipeline, which manages the Filter instances, the enabled
        # filters are an unordered collection. The concept of ordering of filters
        # within a render pass is implemented in FilterStage.
        #
        self.filters = set()

        # FilterPipeline is responsible for the ordering of render passes;
        # hence this needs an ordered collection (such as a list).
        #
        self.stages = []

        self._halfPixelShift = False

        if name is not None:
            self.name = name
        else:
            self.name = "instance at 0x%x" % id(self)

        # Logical stages of the simulated image-forming process; ordered list of names considered valid.
        #
        # Filters are assigned to these (see stageName in Filter). Depending on properties of enabled filters,
        # several logical stages may be merged into a single render pass (FilterStage) to minimize the
        # number of render passes.
        #
        # Examples of filters belonging to different stages:
        #   Preprocess:      Antialias, CartoonInk
        #   SceneOptics:     LocalReflection [if added later], AmbientOcclusion, VolumetricLighting
        #   LensFocus:       BlurSharpen (depends on interpretation), DepthOfField [if added later]
        #   LensOpticsEarly: LensDistortion
        #   LensOpticsLate:  Bloom, LensFlare   (to use distorted color texture as source)
        #   FilmOrDetector:  Desaturation, Inverted (depends on interpretation)
        #   Postprocess:     Tint
        #   DisplayDevice:   GammaCorrection, Scanlines
        #   DebugHelpers:    ViewGlow
        #
        self.knownStages = ["Preprocess", "SceneOptics", "LensFocus", "LensOpticsEarly", "LensOpticsLate",
                            "FilmOrDetector", "Postprocess", "DisplayDevice", "DebugHelpers"]

        self._updateTask = None  # update task for filter updates
        self.cleanup()

        # Update task for running deferred reconfigure.
        #
        # This should run just before the render in igLoop (which has sort=50). This avoids a one-frame lag.
        # Also, this should run before our task running filter updates, so we use a larger priority value.
        #
        self._reconfigureTask = taskMgr.add(self.reconfigureTask,
                                            "FilterPipeline %s deferred reconfigure watchdog" % (self.name), sort = 51,
                                            priority = 2)

    def __del__(self):
        """Destructor."""

        if self._reconfigureTask is not None:
            taskMgr.remove(self._reconfigureTask)
            self._reconfigureTask = None

        self.cleanup()  # this calls self.manager.cleanup(), too
        self.filters = set()
        self.manager = None

    @property
    def halfPixelShift(self):
        """Bool. If True, shift the output of the first FilterStage by half a pixel in both x and y directions. Default False."""
        return self._halfPixelShift

    @halfPixelShift.setter
    def halfPixelShift(self, value):
        self._halfPixelShift = value
        # This actually affects the first FilterStage, so pass the modification through.
        #
        # If we don't have any FilterStages at the moment, we are done (in that case, our reconfigure()
        # will eventually apply this when it creates the FilterStages).
        #
        if len(self.stages) >= 1:
            self.stages[0].halfPixelShift = value  # The setter will trigger reconfigure for the FilterStage.

    def ls(self, indent = 0):
        """Print a human-readable description of this FilterPipeline instance into the terminal."""
        ind = (indent * " ")
        nrp = len(self.stages)
        if nrp < 1:
            print(("%sFilterPipeline %s: <inactive>" % (ind, self.name)))
        else:
            hpsStatus = ", HalfPixelShift enabled" if self.halfPixelShift else ""
            rpplural = "es" if nrp != 1 else ""
            nf = len(self.filters)
            fplural = "s" if nf != 1 else ""
            print(("%sFilterPipeline %s: <active>, %d render pass%s, %d filter%s total%s" % (
            ind, self.name, nrp, rpplural, nf, fplural, hpsStatus)))
            # sort by texture name for human-readability
            print(("%s  Scene textures: %s" % (ind, sorted(self.sceneTextures.keys()))))
            # stages have an ordering; present them in their correct order.
            for i, stage in enumerate(self.stages):
                print(("%s  Render pass %d/%d:" % (ind, i + 1, nrp)))
                stage.ls(indent = indent + 4)

    def cleanup(self):
        """Cleanup function.

        Destroys dynamic state, leaving the FilterPipeline into a state suitable to begin a rebuild.

        Does NOT destroy Filter instances managed by this FilterPipeline; those are only destroyed
        when explicitly asked to do so (delFilter()), or when the FilterPipeline is destroyed.
        This makes the filters preserve their configuration across pipeline reconfigures.

        This is intended to be called from reconfigure().

        """
        # This function must not raise exceptions; it may be called in response to exceptions.

        # Stop the update task before doing anything else.
        if self._updateTask is not None:
            taskMgr.remove(self._updateTask)
            self._updateTask = None

        # per-filter input parameters (passed through to FilterStages once we know which filter goes where)
        #
        # key: filter instance
        #
        self.registeredTextures = {}
        self.registeredCustomInputs = {}

        # general parameters for requesting scene textures from FilterManager
        #
        self.requiredSceneTextures = set()
        self.requiredAuxBits = 0

        # run-time onUpdate() functions defined by filters
        #
        self.updateFunctions = {}

        # Clean up and destroy the current FilterStages.
        #
        # This detaches the Filters from the FilterStages, and releases the Filter references
        # from the FilterStages. The Filter instances stay owned by this FilterPipeline.
        #
        for s in self.stages:
            s.cleanup()
        self.stages = []

        # Detach the filters from the pipeline. In the cleaned-up state, FilterPipeline does not want
        # reconfigures due to parameter changes in the filters.
        #
        # This also resets the mergings count of the filters.
        #
        for f in self.filters:
            f.detachPipeline()

        # Clear input/output texture and quad references
        #
        self.sceneTextures = {}
        self.stageColorTextures = []
        self.quads = []

        # Now that the Filters are no longer attached, destroy textures and quads.
        #
        self.manager.cleanup()

        # All filters in detached state, no need to compile.
        self._needsCompile = False

    def _registerInputTexture(self, filterInstance, texName):
        """Register an input texture for a filter.

        Callback. This is meant to be called from onAttachPipeline() in classes derived from Filter,
        but usually via Filter.registerInputTexture(), which sets filterInstance automatically.
        (Hence, hidden method.)

        Registered input textures will be propagated to FilterStage._registerInputTexture()
        once the FilterStages are created during the rebuild.

        FilterPipeline itself uses this information to decide which scene textures are needed
        (it is passed to _requireSceneTexture()).

        """
        assert (filterInstance is not None)
        assert (isinstance(filterInstance, Filter))

        # for compositing shader in FilterStage
        if filterInstance not in self.registeredTextures:
            self.registeredTextures[filterInstance] = []
        self.registeredTextures[filterInstance].append(texName)

        # for FilterManager
        if texName in SCENETEXTURES:
            self._requireSceneTexture(filterInstance, texName)

    # TODO: name: _registerCustomInput() or _registerCustomShaderInput()?
    def _registerCustomInput(self, filterInstance, customInputMetadata):
        """Register a custom shader input for a filter.

        Callback. This is meant to be called from onAttachPipeline() in classes derived from Filter,
        but usually via Filter.registerCustomInput(), which sets filterInstance automatically.
        (Hence, hidden method.)

        Registered custom inputs will be propagated to FilterStage._registerCustomInput()
        once the FilterStages are created during the rebuild.

        """
        assert (filterInstance is not None)
        assert (isinstance(filterInstance, Filter))

        if filterInstance not in self.registeredCustomInputs:
            self.registeredCustomInputs[filterInstance] = []
        self.registeredCustomInputs[filterInstance].append(customInputMetadata)

    def _registerUpdatable(self, filterInstance, updateFunction):
        """Register filterInstance as updatable, with updateFunction providing the code to run at update time.

        Callback. This is meant to be called from onAttachPipeline() in classes derived from Filter,
        but usually via Filter.registerUpdatable(), which sets the parameters automatically.
        (Hence, hidden method.)

        Registered updatables will be propagated to FilterStage._registerUpdatable()
        once the FilterStages are created during the rebuild.

        """
        assert (filterInstance is not None)
        assert (isinstance(filterInstance, Filter))
        assert (updateFunction is not None)

        self.updateFunctions[filterInstance] = updateFunction

    def _requireSceneTexture(self, filterInstance, texName):
        """Require a scene texture for a filter.

        Callback. This is meant to be called from onAttachPipeline() in classes derived from Filter,
        but usually via Filter.requireSceneTexture(), which sets filterInstance automatically.
        (Hence, hidden method.)

        This tells FilterPipeline that the scene texture named texName is needed, and must be
        requested from FilterManager.

        texName must be one of Filter.SCENETEXTURES.

        """
        assert (filterInstance is not None)
        assert (isinstance(filterInstance, Filter))

        if texName not in SCENETEXTURES:
            raise ValueError("texName='%s' is not a scene texture; valid: %s" % (texName, SCENETEXTURES))

        # filterInstance is unused; this only affects global behavior
        self.requiredSceneTextures.add(texName)

    def _requireAuxBits(self, filterInstance, bitmask):
        """Require an AuxBitplaneAttrib bitmask (e.g. ABOGlow, ABOAuxNormal) for a filter.

        Callback. This is meant to be called from onAttachPipeline() in classes derived from Filter,
        but usually via Filter.requireAuxBits(), which sets filterInstance automatically.
        (Hence, hidden method.)

        FilterPipeline must know the aux bits that are needed before it can request the
        scene textures from FilterManager. The scene textures, in turn, must be set up
        before the FilterStages can be configured.

        """
        assert (filterInstance is not None)
        assert (isinstance(filterInstance, Filter))

        # Currently we don't use filterInstance here, as the aux bits only affect global behavior.
        #
        # The parameter is only there for API consistency with the _register*() methods,
        # to make future expansion easier.
        #
        self.requiredAuxBits |= bitmask

    # TODO: Supporting the mapping of a single *filter* instance to multiple *pipelines*
    # TODO: (which would automatically reflect the same configuration in multiple views)
    # TODO: would require at least the following modifications:
    #    - Filter.mergings must be replaced with a dict with one entry per host pipeline.
    #    - attachPipeline() and detachPipeline() must account for multiple hosts.
    #    - Pipeline-level compile-time parameters must set the compile flag in all hosts.
    #
    def addFilterInstance(self, f):
        """Add a Filter instance to this pipeline.

        Multiple instances of the same filter type CAN be added to the same pipeline,
        but each filter instance in the pipeline must have a unique (stageName, sort) pair.

        The same Filter instance MUST NOT be added to multiple pipelines; if you need
        to have the same filter in multiple views, read the configuration via
        Filter.getConfiguration() and create a new Filter instance
        for the other FilterPipeline with the same configuration options.

        You can manage the configuration of the Filter directly via its properties;
        FilterPipeline has no methods related to configuring filters.

        Be sure to store "f" yourself; the Filter instance can be later removed from the pipeline
        by passing f to removeFilterInstance() (this is the only way to remove it).

        See also:
            removeFilterInstance()
            hasFilterInstance()

        """
        if f is None:
            raise TypeError("In pipeline '%s': f must not be None" % (self.name))
        if not isinstance(f, Filter):
            raise TypeError("In pipeline '%s': f must be an instance of (a subclass of) Filter; got '%s'" % (
            self.name, f.__class__.__name__))

        self.filters.add(f)
        self._needsCompile = True

    def removeFilterInstance(self, f):
        """Remove a Filter instance (added earlier using addFilterInstance()) from this pipeline.

        See also:
            addFilterInstance()
            hasFilterInstance()

        """
        if f is None:
            raise TypeError("In pipeline '%s': f must not be None" % (self.name))
        if not isinstance(f, Filter):
            raise TypeError("In pipeline '%s': f must be an instance of (a subclass of) Filter; got '%s'" % (
            self.name, f.__class__.__name__))

        if f not in self.filters:
            raise ValueError("In pipeline '%s': trying to remove %s %s, which is not present in this pipeline" % (
            self.name, f.__class__.__name__, f.name))

        self.filters.remove(f)
        self._needsCompile = True

    def hasFilterInstance(self, f):
        """Return whether this FilterPipeline has the Filter instance f.

        See also:
            addFilterInstance()
            removeFilterInstance()

        """
        if f is None:
            raise TypeError("In pipeline '%s': f must not be None" % (self.name))
        if not isinstance(f, Filter):
            raise TypeError("In pipeline '%s': f must be an instance of (a subclass of) Filter; got '%s'" % (
            self.name, f.__class__.__name__))

        return (f in self.filters)

    def _createFilterStages(self):
        """Determine and create FilterStages. Part of pipeline rebuild process.

        Intended to be called from reconfigure() after self.cleanup() has been called
        and the filters have been attached to the pipeline. Not intended to support
        other call sites; hence hidden method.

        This maps logical filter stages (self.knownStages) to actual render pass FilterStages,
        creates the needed FilterStage instances in self.stages, and assigns the Filter
        instances from self.filters to them in the appropriate manner.

        The mapping is determined dynamically. The needed number of render passes and which
        filters should go into which pass are computed from currently enabled filters
        (specifically, their stageName and isMergeable parameters).

        Stages without any filters enabled will be skipped. Any stages containing only
        mergeable filters will be merged to the end of the previous non-empty render pass
        (multiple successive stages may be concatenated, preserving ordering, to the end
         of the same target).

        The result is that the filters will be assigned into an optimal number of render passes,
        where each render pass consists of filters from one or more logical stages.

        The name of each FilterStage will be of the format "[stage1 + stage2 + ... + stageN]",
        where "stageX" are the names of the original logical stages that have been combined
        to produce the render pass.

        If a render pass gets only a single logical stage assigned to it, it will be named "[stage]".


        Return value:

            bool: False if no filters have been enabled in this FilterPipeline, otherwise True.

        """

        # simple struct to make the counting code self-documenting
        class FilterKindCounts:
            def __init__(self, mergeable = 0, nonmergeable = 0):
                self.mergeable = mergeable
                self.nonmergeable = nonmergeable

        # Discover the stages needed by currently enabled filters, and count how many
        # mergeable and nonmergeable filters currently want to be placed in each stage.
        #
        # We will use this information to convert the logical stages into render passes,
        # where each render pass may combine multiple successive logical stages.
        # When we do that (later below), each stage (except the first nonempty stage)
        # will be merged into the previous render pass, unless it contains at least
        # one nonmergeable filter.
        #
        filterKindsByStage = {}
        filtersByStage = {}
        for f in self.filters:
            # StageInitializers do not participate in the merging logic.
            #
            assert (not isinstance(f, StageInitializer))

            # Sanity check that the stage is known; we need to be able to order the stages correctly
            # in order to set up the pipeline.
            #
            if f.stageName not in self.knownStages:
                raise ValueError(
                    "In pipeline '%s': the stageName of %s (%s) references undefined stage '%s'. List of valid stages (for this FilterPipeline): %s." % (
                    self.name, f.__class__.__name__, f.name, f.stageName, self.knownStages))

            if f.stageName not in filterKindsByStage:
                filterKindsByStage[f.stageName] = FilterKindCounts(mergeable = int(f.isMergeable),
                                                                   nonmergeable = int(not f.isMergeable))
            else:
                filterKindsByStage[f.stageName].mergeable += int(f.isMergeable)
                filterKindsByStage[f.stageName].nonmergeable += int(not f.isMergeable)

            # Make reverse lookup dict: list of enabled filters keyed by stageName.
            # We will need this when assigning filters to the FilterStages.
            #
            if f.stageName not in filtersByStage:
                filtersByStage[f.stageName] = []
            filtersByStage[f.stageName].append(f)

        # This dict will gather stage name mappings:
        #
        #   - key   = original stageName
        #   - value = target stageName to which the stage has been mapped (by merging)
        #
        stageNameToMerged = {}

        # Find first stage in the global ordering that has at least one enabled filter.
        #
        found = False
        for idx, stageName in enumerate(self.knownStages):
            if stageName not in filtersByStage:  # skip empty stages
                continue

            # The first enabled stage obviously cannot be merged to a previous one, so we map it to itself.
            #
            # We also set it as the merge target for successive stages.
            #
            # If any mergings occur, we will assemble the descriptive name of the combined stage
            # into combinedStageName.
            #
            combinedStageName = stageName
            mergeTargetStageName = stageName
            stageNameToMerged[stageName] = stageName
            mergeSteps = 0

            found = True
            break
        if not found:  # no filters enabled; no stages need to be configured.
            return False

        # This will gather human-readable descriptive names, documenting which original
        # stages have been combined into each final stage.
        #
        # We will use these as the stageNames of the actual FilterStages (render passes) we create.
        #
        # This information must be stored in an ordered container, so that we can connect
        # the FilterStages to each other correctly. Thus we use a list.
        #
        finalStageNames = []

        # This maps a finalStageName to its index in finalStageNames.
        # Used during construction of the FilterStages. 
        #
        finalStageNameToIndex = {}

        # This will gather mappings from the original names of the enabled stages to the
        # final human-readable ones.
        #
        # This intermediate step is needed because the final names are assembled dynamically.
        # During the processing, a later stage, if it gets merged, may contribute to the
        # name of the same final stage as the current stage being processed.
        #
        #   - key   = value in stageNameToMerged (this information is available during processing)
        #   - value = one of finalStageNames
        #
        mergedToFinal = {}

        # Determine stage mergings.
        #
        # First, check if we have only one enabled stage.
        #
        # If the first enabled stage is the last stage defined in self.knownStages, we will have only one stage.
        # Otherwise, check if at least one remaining stage is nonempty.
        #
        singleStage = (idx == len(self.knownStages) - 1)
        if not singleStage:
            found = False
            for stageName in self.knownStages[idx + 1:]:
                if stageName in filtersByStage:
                    found = True  # this stage is not empty
                    break
            singleStage = not found

        if not singleStage:
            # At this point, we have at least one more non-empty stage remaining.
            #
            # Walk the remaining stages and set up merges.
            #
            lastProcessed = ""  # needed for finalization of last render pass
            for stageName in self.knownStages[idx + 1:]:
                mergeSteps += 1

                # Skip empty stages.
                #
                if stageName not in filtersByStage:
                    continue

                # If no nonmergeable filters enabled in this stage,
                # merge this stage into the current merge target stage.
                #
                if filterKindsByStage[stageName].nonmergeable == 0:
                    combinedStageName += " + %s" % stageName
                    stageNameToMerged[stageName] = mergeTargetStageName

                    # Update number of mergings for filters in this stage to make sort preserve ordering
                    # even though several logical stages end up in the same render pass (and thus in
                    # the same FilterStage instance).
                    #
                    for f in filtersByStage[stageName]:
                        f.mergings += mergeSteps

                    lastProcessed = "mergeable"

                else:  # at least one nonmergeable filter in this stage
                    # Now that we found a stage that cannot be merged,
                    # the old combined stage name is final.
                    #
                    # Add it to final stages; a render pass will be created for it.
                    #
                    stylizedName = "[%s]" % combinedStageName
                    finalStageNames.append(stylizedName)
                    finalStageNameToIndex[stylizedName] = len(finalStageNames) - 1
                    mergedToFinal[mergeTargetStageName] = stylizedName

                    # Make this stage the new merge target and begin constructing a new render pass.
                    #
                    combinedStageName = stageName
                    mergeTargetStageName = stageName
                    stageNameToMerged[stageName] = stageName
                    mergeSteps = 0

                    lastProcessed = "nonmergeable"

        # Finalize the last (or only) render pass.
        #
        if singleStage or lastProcessed == "mergeable":
            stylizedName = "[%s]" % combinedStageName
        if not singleStage and lastProcessed == "nonmergeable":
            stylizedName = "[%s]" % mergeTargetStageName
        finalStageNames.append(stylizedName)
        finalStageNameToIndex[stylizedName] = len(finalStageNames) - 1
        mergedToFinal[mergeTargetStageName] = stylizedName

        # At this point:
        #   - We have at least one render pass.
        #   - finalStageNames contains an ordered list of final stage names (render pass names),
        #     accounting for any merged stages.
        #   - Each original stage name maps to one of the final stage names (render pass names)
        #     as "mergedToFinal[ stageNameToMerged[stageName] ]".
        #   - Each Filter instance has its mergings member set to indicate how many stage merges
        #     it participated in.

        # Create the FilterStages representing the render passes.
        #
        for s in finalStageNames:
            self._addFilterStage(s)

        # Assign our Filters to the created FilterStages.
        #
        # The ordering of filters within each FilterStage will be determined later,
        # by FilterStage.reconfigure().
        #
        for f in self.filters:
            s = mergedToFinal[stageNameToMerged[f.stageName]]  # final stage name
            stage = self.stages[finalStageNameToIndex[s]]
            stage.addFilterInstance(f)

        return True

    def _addFilterStage(self, name):
        """Create a FilterStage named name, and append it to self.stages.

        This also takes care of adding and setting up the StageInitializer
        for the new stage.

        Used internally by reconfigure() and _createFilterStages().

        """
        stage = FilterStage(pipeline = self, name = name)

        # We add the StageInitializer at this point, because
        # it must not participate in the logical stage merging process
        # in _createFilterStages().
        #
        # One initialization filter must be inserted in each actual render pass.
        #
        # Note that this effectively makes FilterStage own its StageInitializer;
        # we do not store a reference here.
        #
        # Other filters have already been attached to the pipeline when stages are created.
        # We must do that also for the initialization filter to make it run its onAttachPipeline(),
        # which registers its input textures (namely scene color) to the pipeline.
        #
        initFilter = StageInitializer()
        initFilter.attachPipeline(pipeline = self)
        stage.addFilterInstance(initFilter)

        self.stages.append(stage)

    def _propagateRegistrationData(self):
        """Propagate any relevant registration data to FilterStages.

        Internal method, called by reconfigure() after FilterStages have been created.

        """
        for stage in self.stages:
            # See if the filters assigned to this stage registered anything to us,
            # and pass the relevant information to the FilterStage.
            for f in stage.filters:
                if f in self.registeredTextures:
                    for texName in self.registeredTextures[f]:
                        stage._registerInputTexture(f, texName)

                if f in self.registeredCustomInputs:
                    for customInputMetadata in self.registeredCustomInputs[f]:
                        stage._registerCustomInput(f, customInputMetadata)

                if f in self.updateFunctions:
                    stage._registerUpdatable(f, self.updateFunctions[f])

    def reconfigure(self):
        """Rebuild the pipeline.

        If any filters are enabled, sets up postprocessing using those filters.
        Otherwise the scene is passed through.

        Note that the Filter objects retain their configuration across reconfigure() calls.

        """
        # TODO: pink tint?
        ###        If no filters are enabled, causes the screen to be tinted pink. This behavior
        ###        comes from FilterManager, and is intended as a visual clue that an unnecessary,
        ###        blank filter pipeline is currently enabled.

        # Compile only if needed.
        #
        if not self._needsCompile:
            # Compile filters if they need a compile.
            #
            # In the new API, this is not strictly needed, because the filter update task
            # will process deferred reconfigures for any filters (via FilterStage.update())
            # just before the frame is drawn.
            #
            # This is here to correctly support the old CommonFilters API, because it must know
            # before returning from the set***() and del***() calls whether anything went wrong.
            # It calls the pipeline-level reconfigure(), and expects an exception to be raised
            # *immediately* if there is anything wrong with the new configuration. This is
            # critically important to avoid crashes in legacy apps due to unexpected exceptions.
            #
            # Note that in case the pipeline is reconfigured, the filter reconfigures
            # will be called at attach time, so we only need to explicitly call the
            # filter reconfigures when no pipeline reconfigure is needed.
            #
            for f in self.filters:
                if f._needsCompile:
                    f.reconfigure()

            return

        # Detach filters from FilterStages and destroy the old FilterStages.
        # This also detaches the filters from the pipeline.
        #
        self.cleanup()

        ## We could do stuff here if we needed to do something specifically
        ## at the time when the filters are not attached to the pipeline.

        # Attach the filters to the pipeline.
        #
        # This calls onAttachPipeline(), registering input textures, custom shader inputs and aux bits.
        #
        # FilterPipeline needs to know the scene texture and aux bits requirements;
        # the rest gets passed on to FilterStage by _propagateRegistrationData()
        # after we create the FilterStages in _createFilterStages().
        #
        try:
            for f in self.filters:
                f.attachPipeline(pipeline = self)
        except:
            self.cleanup()
            raise

        # Map logical stages to render passes (FilterStage instances) based on which filters are enabled.
        # Create the FilterStage instances, and assign the filters to them.
        #
        # This also creates StageInitializers, one for each stage. They are special:
        # they have no meaningful properties, and are owned by the FilterStage.
        #
        # The initialization filters are not intended to be visible to the user, and they should
        # get destroyed automatically when the FilterStages are destroyed during the next cleanup();
        # hence this is the logical place to create them.
        #
        try:
            ret = self._createFilterStages()
        except:
            self.cleanup()
            raise
        if ret == False:
            # We have no filters enabled, except maybe...
            #
            # HalfPixelShift is not an fshader function like the other filters, so it has no corresponding
            # Filter object to represent it. Instead, it is an option that modifies the generated vshader
            # of a FilterStage.
            #
            # If the user wants to enable only HalfPixelShift, we need to generate a stage that has
            # just the initialization filter enabled, but with the HalfPixelShift flag set.
            #
            if self.halfPixelShift:
                self._addFilterStage("[HalfPixelShiftOnly]")

                # Now we have one stage, which has one enabled filter (namely StageInitializer),
                # and we can continue with the usual reconfigure process. We will set the stage's
                # HalfPixelShift flag later.
            else:
                # No filters enabled (not even HalfPixelShift).
                #
                # Just return - this will pass through the scene, because we have cleaned up self.manager,
                # which resets the rendering setup to the state it had before self.manager.renderSceneInto().
                #
                # (This is easier to get working consistently than setting a pink tint, because when created,
                #  FilterPipeline is in a "does not need compile" state. There is no point in calling
                #  reconfigure() in __init__() to set up a pink tint, because typically the user
                #  will add some filters right after the pipeline has been created.)
                #
                # If queried, ls() will tell the user that the pipeline is in an inactive state.

                #                # Let FilterManager set default pink tint and return.
                #                #
                #                self.sceneTextures["color"] = FilterUtils.makeFilterTexture("color")
                #                finalQuad = self.manager.renderSceneInto(textures=self.sceneTextures, auxbits=0)
                #                if finalQuad is None:
                #                    self.cleanup()
                #                    raise RuntimeError("In pipeline '%s': FilterManager.renderSceneInto() failed during setting default pink tint." % self.name)
                #                self.quads.append( finalQuad )

                return  # setup success (although no filters enabled)

        # FilterStages have now been created.
        #
        # At this point, we have at least one FilterStage.
        #
        assert (len(self.stages) >= 1)

        # Pass through the current value of our halfPixelShift setting to the first FilterStage.
        #
        # We write to the internal variable in FilterStage directly, because we don't want
        # the setter to flag a new pipeline reconfigure.
        #
        self.stages[0]._halfPixelShift = self.halfPixelShift

        # Propagate the registrations (input textures, custom shader inputs, update functions)
        # provided by the Filters to the relevant FilterStages.
        #
        self._propagateRegistrationData()

        # Create textures and quads. Connect stages via FilterManager.
        #
        # First, see which scene textures we will need. We only create those scene textures
        # that are actually needed by at least one enabled filter (including the initialization filter).
        #
        # We ignore any internal textures defined by the filters, as they will be created
        # by the filters themselves.
        #
        # However, we *do* include any scene textures that have been requested for internal use of the filters,
        # because it is our job to make those scene textures available from the renderer.
        # (This is done simply by doing nothing special - such scene textures are already "required".)
        #
        for texName in self.requiredSceneTextures:
            self.sceneTextures[texName] = FilterUtils.makeFilterTexture(texName)

        # Note that FilterManager.renderSceneInto() returns the *final* quad, which is actually shown on screen,
        # although rendering the scene into a set of textures is the *first* step that occurs in the pipeline
        # (before any filter stages proper).
        #
        # The shader that this last quad expects is that which will render the final output, i.e. the shader of
        # the *final* stage in the pipeline.
        #
        finalQuad = self.manager.renderSceneInto(textures = self.sceneTextures, auxbits = self.requiredAuxBits)
        if finalQuad is None:
            self.cleanup()
            raise RuntimeError(
                "In pipeline '%s': FilterManager.renderSceneInto() failed during setup of finalQuad. Aux bits = %s, scene textures = %s." % (
                self.name, self.requiredAuxBits, self.sceneTextures))

        # To get correct render order for the quads, they must be created in the order they need to be rendered.
        # (This is important so that multi-stage filters and multi-pass pipelines will render correctly.) 
        # This is because in FilterManager, the buffers are rendered in the order in which they are created.
        #
        # It is simpler to order the buffer creation calls appropriately than to add a mechanism
        # to FilterManager to let the caller access the internal buffer objects and set their sort values.
        #
        # We want the following render order:
        #  - scene textures
        #  - internal buffers of first stage
        #  - compositing output of first stage
        #  - internal buffers of second stage
        #  - compositing output of second stage
        #  ...
        #  - internal buffers of last stage
        #  - compositing output of the last stage
        #
        # The solution is:
        #  - connect input first (already exists when a stage is being configured)
        #  - reconfigure stage (this creates the intermediate quads if the enabled filters define any)
        #  - create output quad
        #  - connect output, assigning the created shader

        # All stages except the final one are intermediate stages, which render into a texture.
        #
        # output from scene = input to first stage
        self.stageColorTextures.append(self.sceneTextures["color"])
        for i, stage in enumerate(self.stages[:-1]):
            # We pass through "depth" and "aux" from the scene.
            #
            # TODO: Support updating aux and depth in the filters, via additional output textures
            #       (auxiliary render targets). Without that support, depth and aux become outdated
            #       after LensDistortion or similar image remapping (warping) filters.
            #
            stageInputTextures = self.sceneTextures.copy()  # shallow-copy references only
            stageInputTextures["color"] = self.stageColorTextures[-1]  # input color = previous output

            # Assign the input textures to the FilterStage.
            #
            stage.connectInput(stageInputTextures)

            # Reconfigure the stage (creating any intermediate quads).
            #
            # When FilterStage attaches its assigned Filters to the stage, each Filter will compile itself,
            # and get references to the currently connected stage input textures from FilterStage.
            #
            try:
                stage.reconfigure()
            except:
                self.cleanup()
                raise

            # Create the output quad.
            #
            outputTexture = FilterUtils.makeFilterTexture("stage%d" % i)  # output texture for this stage
            outputQuad = self.manager.renderQuadInto(colortex = outputTexture)
            if outputQuad is None:
                self.cleanup()
                raise RuntimeError(
                    "In pipeline '%s': FilterManager.renderQuadInto() failed during setup of stage '%s' (%d out of %d stages). Aux bits = %s, scene textures = %s." % (
                    self.name, stage.name, i + 1, len(self.stages), self.requiredAuxBits, self.sceneTextures))

            self.stageColorTextures.append(outputTexture)
            self.quads.append(outputQuad)

            # Assign the quad into which the compositing shader (from this FilterStage) renders,
            # and start this stage.
            #
            stage.connectOutput(outputQuad)

        # The final stage renders into finalQuad, which is shown on screen.
        # It does not need an output buffer.
        #
        stageInputTextures = self.sceneTextures.copy()  # shallow-copy references only
        stageInputTextures["color"] = self.stageColorTextures[-1]  # previous output
        self.stages[-1].connectInput(stageInputTextures)
        try:
            self.stages[-1].reconfigure()
        except:
            self.cleanup()
            raise
        self.quads.append(finalQuad)
        self.stages[-1].connectOutput(finalQuad)

        # The rebuild is now complete.
        #
        self._needsCompile = False

        # Start the update task for updating filters.
        #
        # This should run after the deferred reconfigure, so we use a smaller priority.
        #
        self._updateTask = taskMgr.add(self.updateTask, "FilterPipeline %s update" % (self.name), sort = 49,
                                       priority = 1)

        # Make sure the filters update once immediately, since they may have shader inputs
        # that are only sent in update().
        #
        self.updateTask()

    def reconfigureTask(self, task = None):
        """Task function for taskMgr. Used internally.

        This runs at each frame, running deferred reconfigure (if any is pending). 

        """
        # Run deferred reconfigure at the pipeline level. FilterStage manages the filter level
        # in FilterStage.update() (called by our updateTask()).
        #
        if self._needsCompile:
            self.reconfigure()

        if task is not None:
            return task.cont

    def updateTask(self, task = None):
        """Task function for taskMgr. Used internally.

        The task is set up by reconfigure() and torn down by cleanup().

        This calls the filters' update methods.

        """
        # Call the filters' update methods.
        #
        # To avoid any ordering issues, we delegate the filter updates to each FilterStage,
        # ensuring correct ordering across the whole pipeline.
        #
        for s in self.stages:
            s.update()

        if task is not None:
            return task.cont
