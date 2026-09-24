"""
This file exists so we can switchably include these files, which are not
imported or shipped in production code, but are handy in the development environment.
"""

from toontown.level.editor import EditorGlobals

if EditorGlobals.wantLevelEditor():
    from toontown.utils.largeblob import DistributedLargeBlobSender
    from toontown.level.editor import DistributedInGameEditor
