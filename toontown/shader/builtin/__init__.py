"""Postprocessing filter system.

See modules:

FilterPipeline - main user API for applying postprocessing filters. Supports automatic generation of multiple
                 render passes based on requirements of enabled filters.

FilterStage    - internal module representing one render pass in FilterPipeline. Not useful on its own.

Filter         - API for implementing filters for FilterPipeline.

                 The existing postprocessing filters have been implemented using this API.
                 Any custom filters using this API can be inserted into the same FilterPipeline
                 with the existing filters.

                 The various other modules (AmbientOcclusion, Bloom, ...) implement the actual filters.

                 The MiscFilters module contains a collection of short, simple filters
                 for which a separate module each would be overkill.

CompoundFilter - Filter API adapter for modular filters that contain other Filters.

CommonFilters  - backward compatibility layer for legacy scripts (Panda 1.8.x).

FilterManager  - low-level render buffer management; provides the basis for pipeline support.
                 (This already existed in 1.8.x.)


ListAllFilters - command-line introspection tool (python -m ListAllFilters).

                 This gives an overall idea of the default stageName and sort values
                 across all defined filters, making it easier to choose appropriate
                 values when implementing a new filter type.

"""
pass

## the old CommonFilters used to import:
#from FilterManager import FilterManager
#from panda3d.core import Point3, Vec3, Vec4, Point2
#from panda3d.core import NodePath, PandaNode
#from panda3d.core import Filename
#from panda3d.core import AuxBitplaneAttrib
#from panda3d.core import RenderState, Texture, Shader, ATSNone
#import sys,os

