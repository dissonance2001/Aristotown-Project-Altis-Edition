from __future__ import absolute_import
from panda3d.core import *
from . import Playground
from direct.task.Task import Task
import random
from toontown.hood import Place
from toontown.toonbase import ToontownGlobals

class OTPlayground(Playground.Playground):

    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)

    def load(self):
        Playground.Playground.load(self)

    def unload(self):
        Playground.Playground.unload(self)

    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)

    def exit(self):
        Playground.Playground.exit(self)

    def enterTunnelOut(self, requestStatus):
        Place.Place.enterTunnelOut(self, requestStatus)
