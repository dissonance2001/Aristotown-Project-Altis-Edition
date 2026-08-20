from __future__ import absolute_import
from direct.task.Task import Task
import random
from . import Street
from toontown.battle import BattleParticles

class OTStreet(Street.Street):

    def __init__(self, loader, parentFSM, doneEvent):
        Street.Street.__init__(self, loader, parentFSM, doneEvent)

    def load(self):
        Street.Street.load(self)

    def unload(self):
        Street.Street.unload(self)

    def enter(self, requestStatus):
        self.nextBirdTime = 0
        taskMgr.add(self.__birds, 'OT-birds')
        Street.Street.enter(self, requestStatus)

    def exit(self):
        taskMgr.remove('OT-birds')
        Street.Street.exit(self)

    def __birds(self, task):
        if task.time < self.nextBirdTime:
            return Task.cont
        randNum = random.random()
        bird = int(randNum * 100) % 6 + 1
        if bird == 1:
            base.playSfx(self.loader.crow1Sound)
        elif bird == 2:
            base.playSfx(self.loader.crow2Sound)
        elif bird == 3:
            base.playSfx(self.loader.raven1Sound)
        elif bird == 4:
            base.playSfx(self.loader.raven2Sound)
        elif bird == 5:
            base.playSfx(self.loader.ravenCrow1Sound)
        elif bird == 6:
            base.playSfx(self.loader.ravenCrow2Sound)
        self.nextBirdTime = task.time + randNum * 40.0
        return Task.cont
