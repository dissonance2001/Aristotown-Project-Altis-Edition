from panda3d.core import Point3
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import *
from direct.showbase.MessengerGlobal import messenger


class HQRamp(FSM):
    """HQRamp: Handles the states of the HQ ramps present
    in the Sellbot boss.
    """

    defaultTransitions = {
        "Off": ["Extend", "Extended", "Retract", "Retracted"],
        "Extend": ["Extended", "Retract", "Retracted"],
        "Extended": ["Retract", "Retracted"],
        "Retract": ["Extend", "Extended", "Retracted"],
        "Retracted": ["Extend", "Extended"],
    }

    def __init__(self, name, rampNode):
        super().__init__(name)
        self.rampSlideSfx = loader.loadSfx('phase_9/audio/sfx/CHQ_VP_ramp_slide.ogg')
        self.rampNode = rampNode
    
    def cleanup(self):
        self.rampNode.remove_node()
        del self.rampNode
        del self.rampSlideSfx
        return super().cleanup()
    
    def request(self, request, *args):
        if request == self.getCurrentOrNextState():
            return
        return super().request(request, *args)

    def uniqueName(self, string: str) -> str:
        return f"{string}-{id(self)}"
    
    def enterExtend(self):
        intervalName = self.uniqueName('extend-%s' % self.rampNode.getName())
        adjustTime = 2.0 * self.rampNode.getX() / 18.0
        ival = Parallel(SoundInterval(self.rampSlideSfx, node=self.rampNode), self.rampNode.posInterval(adjustTime, Point3(0, 0, 0), blendType='easeInOut', name=intervalName))
        ival.start()
        messenger.send("boss_storeInterval", [ival, intervalName])

    def exitExtend(self):
        intervalName = self.uniqueName('extend-%s' % self.rampNode.getName())
        messenger.send("boss_clearInterval", [intervalName])

    def enterExtended(self):
        self.rampNode.setPos(0, 0, 0)

    def enterRetract(self):
        intervalName = self.uniqueName('retract-%s' % self.rampNode.getName())
        adjustTime = 2.0 * (18 - self.rampNode.getX()) / 18.0
        ival = Parallel(SoundInterval(self.rampSlideSfx, node=self.rampNode), self.rampNode.posInterval(adjustTime, Point3(18, 0, 0), blendType='easeInOut', name=intervalName))
        ival.start()
        messenger.send("boss_storeInterval", [ival, intervalName])

    def exitRetract(self):
        intervalName = self.uniqueName('retract-%s' % self.rampNode.getName())
        messenger.send("boss_clearInterval", [intervalName])

    def enterRetracted(self):
        self.rampNode.setPos(18, 0, 0)
