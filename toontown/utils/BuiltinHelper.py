import builtins
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from direct.showbase.Loader import Loader
    from direct.task.Task import TaskManager
    from direct.directnotify.DirectNotify import DirectNotify
    from direct.showbase.BulletinBoard import BulletinBoard
    from direct.showbase.EventManager import EventManager
    from direct.showbase.JobManager import JobManager
    from direct.showbase.Messenger import Messenger
    from panda3d.core import ClockObject, NodePath
    from panda3d.core import VirtualFileSystem
    from toontown.toonbase.ToonBase import ToonBase
    from panda3d.core import ConfigPageManager, ConfigVariableManager, PandaSystem
    from toontown.ai.AIBase import AIBase
    from toontown.settings import ToontownSettings

else:
    # This file should only ever be imported by a static type checker.
    raise AssertionError("The Builtin helper shouldn't be imported at runtime. Always ensure it's inside a TYPE_CHECKING conditional.")

"""
Builtin Helper
--------------
The Builtin helper is a band-aid solution to the "red line nightmare".

What are Builtins?
If you've ever used Python, you'll notice you can use a few types like `str` and `dict` without importing them.
The way this is achieved is through the builtin module.
If you load up a Python session and type `__builtins__.str`, you'll see it links to the string class.
`dir(__builtins__)` will show you all of the builtin types you can access.

What is the problem?
While developing ToonTown in an IDE, you'll be faced with a sea of errors.
These errors will most likely be NameError's for things like `base` and `simbase`.
This is because when Panda initializes, it injects a bunch of its own types into the Builtin collection.
As our IDE's don't initialize Panda3D, the Builtin collection is just the default Python one.
While this gives us access to things like ShowBase easily, it also lacks things like type hinting.

Our Solution:
In Python 3, we have support for type hinting through the typing module.
Inside the typing module, there is a handy constant called `TYPE_CHECKING`. 
When our IDE's do a static typing analysis, it will set `TYPE_CHECKING` to True (Otherwise it's always False).
So we can trick our IDE's into thinking these types exist by importing them.

How To Use:
from toontown.utils.BuiltinHelper import * [All builtins]
from toontown.utils.BuiltinHelper import base [Selected builtins (Recommended)]
"""


def __getBuiltinValue(name: str):
    """Gets the value of a builtin, if it exists."""
    return getattr(builtins, name) if hasattr(builtins, name) else None


"""
Panda 3D
"""
taskMgr: "TaskManager" = __getBuiltinValue("taskMgr")
directNotify: "DirectNotify" = __getBuiltinValue("directNotify")
loader: "Loader" = __getBuiltinValue("loader")
jobMgr: "JobManager" = __getBuiltinValue("jobMgr")
eventMgr: "EventManager" = __getBuiltinValue("eventMgr")
messenger: "Messenger" = __getBuiltinValue("messenger")
bboard: "BulletinBoard" = __getBuiltinValue("bboard")
globalClock: "ClockObject" = __getBuiltinValue("globalClock")
vfs: "VirtualFileSystem" = __getBuiltinValue("vfs")
hidden: "NodePath" = __getBuiltinValue("hidden")

"""
Client
"""
base: "ToonBase" = __getBuiltinValue("base")
render: "NodePath" = __getBuiltinValue("render")
render2d: "NodePath" = __getBuiltinValue("render2d")
aspect2d: "NodePath" = __getBuiltinValue("aspect2d")
pixel2d: "NodePath" = __getBuiltinValue("pixel2d")
camera: "NodePath" = __getBuiltinValue("camera")
cpMgr: "ConfigPageManager" = __getBuiltinValue("cpMgr")
cvMgr: "ConfigVariableManager" = __getBuiltinValue("cvMgr")
pandaSystem: "PandaSystem" = __getBuiltinValue("pandaSystem")
settings: "ToontownSettings.DefaultSettings" = __getBuiltinValue("settings")

"""
AI/UD
"""
simbase: "AIBase" = __getBuiltinValue("simbase")
