from pandac.PandaModules import *
from toontown.toonbase import ToontownGlobals
from toontown.safezone import Playground
from toontown.launcher import DownloadForceAcknowledge
from toontown.building import Elevator
from toontown.toontowngui import TTDialog
from toontown.toonbase import TTLocalizer
from toontown.racing import RaceGlobals
from direct.fsm import State
from toontown.safezone import GolfKart
from direct.task.Task import Task

class OZPlayground(Playground.Playground):
    waterLevel = 1

    def __init__(self, loader, parentFSM, doneEvent):
        Playground.Playground.__init__(self, loader, parentFSM, doneEvent)
        self.parentFSM = parentFSM

    def load(self):
        Playground.Playground.load(self)

    def unload(self):
        Playground.Playground.unload(self)

    def enter(self, requestStatus):
        Playground.Playground.enter(self, requestStatus)

    def exit(self):
        Playground.Playground.exit(self)
        taskMgr.remove('oz-check-toon-underwater')
        taskMgr.remove('oz-check-cam-underwater')
        self.loader.hood.setNoFog()

    def doRequestLeave(self, requestStatus):
        self.fsm.request('trialerFA', [requestStatus])

    def enterDFA(self, requestStatus):
        doneEvent = 'dfaDoneEvent'
        self.accept(doneEvent, self.enterDFACallback, [requestStatus])
        self.dfa = DownloadForceAcknowledge.DownloadForceAcknowledge(doneEvent)
        if requestStatus['hoodId'] == ToontownGlobals.MyEstate:
            self.dfa.enter(base.cr.hoodMgr.getPhaseFromHood(ToontownGlobals.MyEstate))
        else:
            self.dfa.enter(5)

    def enterTeleportIn(self, requestStatus):
        reason = requestStatus.get('reason')
        if reason == RaceGlobals.Exit_Barrier:
            requestStatus['nextState'] = 'popup'
            self.dialog = TTDialog.TTDialog(text=TTLocalizer.KartRace_RaceTimeout, command=self.__cleanupDialog, style=TTDialog.Acknowledge)
        elif reason == RaceGlobals.Exit_Slow:
            requestStatus['nextState'] = 'popup'
            self.dialog = TTDialog.TTDialog(text=TTLocalizer.KartRace_RacerTooSlow, command=self.__cleanupDialog, style=TTDialog.Acknowledge)
        elif reason == RaceGlobals.Exit_BarrierNoRefund:
            requestStatus['nextState'] = 'popup'
            self.dialog = TTDialog.TTDialog(text=TTLocalizer.KartRace_RaceTimeoutNoRefund, command=self.__cleanupDialog, style=TTDialog.Acknowledge)
        self.toonSubmerged = -1
        Playground.Playground.enterTeleportIn(self, requestStatus)

    def teleportInDone(self):
        self.toonSubmerged = -1
        Playground.Playground.teleportInDone(self)
