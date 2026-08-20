from __future__ import absolute_import
from .DistributedCogHQDoor import *
from toontown.coghq import CogDisguiseGlobals
from toontown.distributed import DelayDelete
#from toontown.gui import TTDialog
from toontown.distributed.DelayDeletable import DelayDeletable
from toontown.building import DoorTypes


class DistributedCogHQBossDoor(DistributedCogHQDoor):
    """
    DistributedCogHQBossDoor(DistributedCogHQDoor)
    """

    def enterDoor(self):
        self.ignore(base.INTERACT)
        if hasattr(self, "enterText"):
            self.enterText.removeNode()
            del self.enterText
        if self.allowedToEnter() or True:
            messenger.send('DistributedDoor_doorTrigger')
            self.d_requestEnter()
        else:
            self.createNoMeritsDialogue()

    def d_requestEnter(self):
        self.ignore('doorRejectAck')
        self.ignore('stoppedAsleep')
        self.ignore('clientCleanup')
        self.ignore('continueNoMerits')

        if hasattr(self, 'rejectDialog'):
            wantContinue = self.rejectDialog.doneStatus == 'ok'
            # self.rejectDialog.delayDelete.destroy()
            # self.rejectDialog.cleanup()
            base.transitions.noFade()
            del self.rejectDialog
            if not wantContinue:
                base.cr.playGame.getPlace().setState('Walk')
                if base.localAvatar.isDisguised:
                    base.localAvatar.getGeomNode().hide()
                return

        #self.sendUpdate('requestEnter', [self.sentGagWarning, self.sentCompletesWarning])

    def createNoMeritsDialogue(self):
        meritsEvent = 'continueNoMerits'
        self.acceptOnce(meritsEvent, self.d_requestEnter)
        deptIndex = ToontownGlobals.cogHQZoneId2deptIndex(self.zoneId)
        message = TTLocalizer.NotEnoughMeritsWarning[deptIndex]

        # self.rejectDialog = TTDialog.TTGlobalDialog(
        #     message = message,
        #     style = TTDialog.TwoChoice,
        #     doneEvent = meritsEvent,
        #     fadeScreen = 0.5,
        # )
        # self.rejectDialog.show()
        # self.rejectDialog.delayDelete = DelayDelete.DelayDelete(self, '__faRejectEnter')

        event = 'clientCleanup'
        self.acceptOnce(event, self.handleClientCleanup)

        base.cr.playGame.getPlace().setState('Stopped')
        if base.localAvatar.isDisguised:
            base.localAvatar.getGeomNode().hide()

        self.acceptOnce('doorRejectAck', self.handleRejectAck)
        self.acceptOnce('stoppedAsleep', self.handleFallAsleepDoor)

    def allowedToEnter(self):
        deptIndex = ToontownGlobals.cogHQZoneId2deptIndex(self.zoneId)
        av = base.localAvatar
        if CogDisguiseGlobals.isSuitComplete(av.cogParts, deptIndex) and not av.readyForPromotion(deptIndex) and self.doorType == DoorTypes.EXT_COGHQ:
            return False
        return True
