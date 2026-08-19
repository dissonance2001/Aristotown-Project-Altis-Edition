"""Specialization of CompoundFilter for rapid prototyping of new compound filters.

This automatically exposes all properties from the contained filters so that new filter combinations
can be prototyped quickly.

The automatic property mapping DOES NOT and CANNOT produce production-quality code; the final version of
your CompoundFilter subclass should always inherit from CompoundFilter (instead of this convenience class)
and expose the needed properties (and only the needed ones) manually.

E.g. in the below usage example there is no point in exposing "source", as it's set internally;
the code of the compound filter itself can use self.volumetricLighting.source directly.

Usage example:

    from direct.filter.Bloom import Bloom
    from direct.filter.VolumetricLighting import VolumetricLighting
    from direct.filter.RapidPrototypeCompoundFilter import RapidPrototypeCompoundFilter

    class MyFilter(RapidPrototypeCompoundFilter):
        def __init__(self, **kwargs):
            super(MyFilter, self).__init__(**kwargs)

        def onReset(self):
            super(MyFilter, self).onReset()
            self.stageName = "SceneOptics"
            self.sort = 50
            # use the texture from the contained bloom filter (override vl's default)
            self.VolumetricLighting_source = "bloomOutput"

        def createContainedFilters(self):
            self.bloom = Bloom()
            self.volumetricLighting = VolumetricLighting()
            self.filters.append( self.bloom )
            self.filters.append( self.volumetricLighting )


    # ...somewhere in your class inheriting from DirectObject...

    self.fp = FilterPipeline(base.win, base.cam)

    myFilter = MyFilter()
    self.fp.addFilterInstance(myFilter)

    # MyFilter has the properties of Bloom, plus those of VolumetricLighting.
    # (In this example case there are no name conflicts.)
    #
    myFilter.caster = self.myNodePath  # some object

"""

from toontown.shader.CompoundFilter import CompoundFilter

class RapidPrototypeCompoundFilter(CompoundFilter):
    """CompoundFilter that automatically creates properties that pass calls to contained filters.

    All properties defined by the contained filters are automatically made available in the
    top-level (CompoundFilter) scope.

    This is a convenience class, meant only for rapid prototyping of new CompoundFilter types.
    For final versions of filters, properties *must* be defined manually.

    Caveats:

        - This renames properties to avoid name conflicts, because if this was not done,
          in case of a conflict only the property defined in the "most recent" contained filter
          would be exposed.

          The naming scheme of the created properties is

          ClassName_PropName

          e.g.

          VolumetricLighting_source

        - This exposes *everything*, i.e. also now-useless properties that only control
          one of the ignored compositing shaders of the contained filters.

    """
    def __init__(self, **kwargs):
        super(RapidPrototypeCompoundFilter, self).__init__(**kwargs)

    def onReset(self):
        # We must call _autoprop() *now*, because it must run after the contained filters are created
        # (so that their properties will be available for aliasing), but before the configuration reset runs,
        # so that the *autoprops* become available before the derived class's onReset() tries to assign values
        # to them.
        #
        # (If we let it assign before the properties are created, then the assignments will actually create
        #  new non-property members having the given values, which we do not want.)
        #
        # (Note that in the Filter API, filters are required to call super's onReset() *first*
        #  before assigning any values. We utilize this.)
        #
        # CompoundFilter's init first calls createContainedFilters(), and then
        # its super's (Filter's) __init__(). Filter.__init__() calls self.onReset().
        #
        # Hence we place this here.
        #
        # Note that _autoprop() only modifies the class if the properties don't exist yet,
        # so this is safe also for already running instances (at that time _autoprop() will not add any properties).
        #
        self._autoprop()
        super(RapidPrototypeCompoundFilter, self).onReset()


    def _autoprop(self):
        """Automatically generate properties in self corresponding to the properties in contained filters.

        Getter and setter calls are passed through to each original property.

        """

        # http://stackoverflow.com/questions/3681272/can-i-get-a-reference-to-a-python-property
        def get_dict_attr(obj, attr):
            for obj in [obj]+obj.__class__.mro():
                if attr in obj.__dict__:
                    return obj.__dict__[attr]
            raise AttributeError

        def propertyFactory(obj, name):
            def _get(self):
                return getattr(obj, name)
            def _set(self, value):
                setattr(obj, name, value)

            # We need this only to pass the docstring through.
            p = get_dict_attr(obj, name)
            doc = "[%s] %s" % (obj.__class__.__name__, p.__doc__)

            return property(_get, _set, None, doc)

        for f in self.filters:
            for propname in f.getProperties():
                uniquePropName = "%s_%s" % (f.__class__.__name__, propname)

                if not hasattr(self, uniquePropName):
                    propobj = propertyFactory(obj=f, name=propname)
                    # http://stackoverflow.com/questions/1325673/how-to-add-property-to-a-python-class-dynamically
                    setattr(self.__class__, uniquePropName, propobj)

