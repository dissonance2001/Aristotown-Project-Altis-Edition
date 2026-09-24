""" DistributedInteractiveEntity module: contains the DistributedInteractiveEntity
    class, the client side representation of a 'landmark door'."""

from panda3d.core import *
from direct.distributed.ClockDelta import *
from direct.fsm import ClassicFSM, State
from toontown.level import DistributedEntity
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


# Currently unused, but we may want to use it to make interative props such as knock knock doors


@DirectNotifyCategory()
class DistributedInteractiveEntity(DistributedEntity.DistributedEntity):
    def __init__(self, cr):
        """constructor for the DistributedInteractiveEntity"""
        DistributedEntity.DistributedEntity.__init__(self, cr)
        self.fsm = ClassicFSM.ClassicFSM('DistributedInteractiveEntity',
                                         [State.State('off', self.enterOff, self.exitOff, ['playing', 'attract']),
                                          State.State('attract', self.enterAttract, self.exitAttract, ['playing']),
                                          State.State('playing', self.enterPlaying, self.exitPlaying, ['attract'])],
                                         # Initial State
                                         'off',
                                         # Final State
                                         'off')
        self.fsm.enterInitialState()

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        DistributedEntity.DistributedEntity.generate(self)

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        # Go to the off state when the object is put in the cache
        self.fsm.request('off')
        DistributedEntity.DistributedEntity.disable(self)

    def delete(self):
        del self.fsm
        DistributedEntity.DistributedEntity.delete(self)

    def setAvatarInteract(self, avatarId):
        self.avatarId = avatarId

    def setOwnerDoId(self, ownerDoId):
        self.ownerDoId = ownerDoId

    def setState(self, state, timestamp):
        if self.isGenerated():
            self.fsm.request(state, [globalClockDelta.localElapsedTime(timestamp)])
        else:
            self.initialState = state
            self.initialStateTimestamp = timestamp

    def enterTrigger(self, args=None):
        messenger.send('DistributedInteractiveEntity_enterTrigger')
        self.sendUpdate('requestInteract')

    def exitTrigger(self, args=None):
        messenger.send('DistributedInteractiveEntity_exitTrigger')
        self.sendUpdate('requestExit')

    def rejectInteract(self):
        """
        Server doesn't let the avatar interact with prop.
        """
        self.cr.playGame.getPlace().setState('Walk')

    def avatarExit(self, avatarId):
        pass

    ### Off State ###

    def enterOff(self):
        pass

    def exitOff(self):
        pass

    ### Attract State ###

    def enterAttract(self, ts):
        pass

    def exitAttract(self):
        pass

    ### Playing State ###

    def enterPlaying(self, ts):
        pass

    def exitPlaying(self):
        pass
