from __future__ import absolute_import
from direct.task.Task import Task
import random
from toontown.classicchars import CCharPaths
from toontown.safezone import Playground
from toontown.safezone.GrandPiano import GrandPiano
from toontown.toonbase import TTLocalizer


class TTPlayground(Playground.Playground):

    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)
        taskMgr.doMethodLater(1, self.__birds, 'TT-birds')

        # The placement printer was temporary.  The final piano owns its model,
        # proximity prompt, controls and GUI in separate files.
        self.grandPiano = GrandPiano()

    def exit(self):
        if hasattr(self, 'grandPiano'):
            self.grandPiano.destroy()
            del self.grandPiano

        Playground.Playground.exit(self)
        taskMgr.remove('TT-birds')

    def showPaths(self):
        self.showPathPoints(CCharPaths.getPaths(TTLocalizer.Mickey))

    def __birds(self, task):
        base.playSfx(random.choice(self.loader.birdSound))
        time = random.random() * 20.0 + 1
        taskMgr.doMethodLater(time, self.__birds, 'TT-birds')
        return Task.done

    def detectedElevatorCollision(self, elevator):
        elevator.handleEnterElevator()
