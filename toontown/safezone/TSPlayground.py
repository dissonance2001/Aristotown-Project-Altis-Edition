from panda3d.core import *
from . import Playground
from direct.task.Task import Task
import random
from toontown.hood import Place
from toontown.toonbase import ToontownGlobals

class TSPlayground(Playground.Playground):

    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)

    def load(self):
        Playground.Playground.load(self)

    def unload(self):
        Playground.Playground.unload(self)

    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)
        self.nextWindTime = 0
        taskMgr.add(self.__windTask, 'ts-wind')
        self.state = 0

    def exit(self):
        taskMgr.remove('ts-wind')
        taskMgr.remove('lerp-snow')
        Playground.Playground.exit(self)
        
    def __windTask(self, task):
        now = globalClock.getFrameTime()
        if now < self.nextWindTime:
            return Task.cont
        randNum = random.random()
        wind = int(randNum * 100) % 3 + 1
        if wind == 1:
            base.playSfx(self.loader.wind1Sound)
        elif wind == 2:
            base.playSfx(self.loader.wind2Sound)
        elif wind == 3:
            base.playSfx(self.loader.wind3Sound)
        self.nextWindTime = now + randNum * 8.0
        return Task.cont
