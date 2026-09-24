""" DistributedInteractiveEntityAI module: contains the DistributedInteractiveEntityAI
    class, the server side representation of a simple, animated, interactive
    prop."""


from direct.distributed.ClockDelta import *

from direct.directnotify import DirectNotifyGlobal
from toontown.level.DistributedEntityAI import DistributedEntityAI
from direct.fsm import ClassicFSM
from toontown.level import DistributedEntityAI
from direct.fsm import State

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedInteractiveEntityAI(DistributedEntityAI.DistributedEntityAI):
    """
    DistributedInteractiveEntityAI class:  The server side representation of
    an animated prop.  This is the object that remembers what the
    prop is doing.  The child of this object, the DistributedAnimatedProp
    object, is the client side version and updates the display that
    client's display based on the state of the prop.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedInteractiveEntityAI')

    def __init__(self, level, entId):
        """entId: a unique identifier for this prop."""
        DistributedEntityAI.DistributedEntityAI.__init__(self, level, entId)
        self.fsm = ClassicFSM.ClassicFSM('DistributedInteractiveEntityAI',
                           [State.State('off', self.enterOff, self.exitOff, ['playing']),
                            # Attract is an idle mode.  It is named attract
                            # because the prop is not interacting with an
                            # avatar, and is therefore trying to attract an
                            # avatar.
                            State.State('attract', self.enterAttract, self.exitAttract, ['playing']),
                            # Playing is for when an avatar is interacting
                            # with the prop.
                            State.State('playing', self.enterPlaying, self.exitPlaying, ['attract'])],
                           # Initial State
                           'off',
                           # Final State
                           'off',
                          )
        self.fsm.enterInitialState()
        self.avatarId = 0

    def delete(self):
        del self.fsm
        DistributedEntityAI.DistributedEntityAI.delete(self)

    def getAvatarInteract(self):
        return self.avatarId

    def requestInteract(self):
        avatarId = self.air.getAvatarIdFromSender()
        stateName = self.fsm.getCurrentState().getName()
        if stateName != 'playing':
            self.sendUpdate("setAvatarInteract", [avatarId])
            self.avatarId = avatarId
            self.fsm.request('playing')
        else:
            self.sendUpdateToAvatarId(avatarId, "rejectInteract", [])

    def requestExit(self):
        avatarId = self.air.getAvatarIdFromSender()
        if avatarId == self.avatarId:
            stateName = self.fsm.getCurrentState().getName()
            if stateName == 'playing':
                self.sendUpdate("avatarExit", [avatarId])
                self.fsm.request('attract')
        else:
            pass

    def getState(self):
        r = [self.fsm.getCurrentState().getName(), globalClockDelta.getRealNetworkTime()]
        return r

    def sendState(self):
        self.sendUpdate('setState', self.getState())

    ### Off State ###

    def enterOff(self):
        pass
        # self.setState('off')

    def exitOff(self):
        pass

    ### Attract State ###

    def enterAttract(self):
        self.sendState()

    def exitAttract(self):
        pass

    ### Open State ###

    def enterPlaying(self):
        self.sendState()

    def exitPlaying(self):
        pass
