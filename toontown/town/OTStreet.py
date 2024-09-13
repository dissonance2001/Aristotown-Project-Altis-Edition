from direct.task.Task import Task
import random
import Street
from toontown.battle import BattleParticles

class OTStreet(Street.Street):

    def __init__(self, loader, parentFSM, doneEvent):
        Street.Street.__init__(self, loader, parentFSM, doneEvent)

    def load(self):
        Street.Street.load(self)

    def unload(self):
        Street.Street.unload(self)

    def enter(self, requestStatus):
        Street.Street.enter(self, requestStatus)

    def exit(self):
        Street.Street.exit(self)
