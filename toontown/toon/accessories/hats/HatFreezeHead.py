from toontown.toon.accessories.ToonAccessory import ToonAccessory


class HatFreezeHead(ToonAccessory):
    """
    A custom Hat type that freezes all head animations when active.

    Also does other visual stuff to sell the 'frozen' effect, like
    putting on a sad muzzle, disabling blinking, using sad eyes,
    and freezing the head anims on Dog toons.
    """

    stopBlink = True
    stopStareAt = True
    stopLookAround = True
    stopHeadPose = True
    overwriteEyes = True
    overwriteMuzzle = True

    def __init__(self, *args):
        super().__init__(*args)
        self.frozen = True
        self.async_addLoadCallback(self.openEvents)

    def openEvents(self):
        self.accept(self.toon.getStartLookAroundMessengerName(), self.freezeToonHead)
        self.accept(self.toon.getStartStareAtMessengerName(), self.freezeToonHead)
        self.accept(self.toon.getStartBlinkMessengerName(), self.freezeToonHead)
        self.accept(self.toon.getUpdateEyesEventName(), self.updateEyes)
        self.accept(self.toon.getUpdateMuzzleEventName(), self.updateMuzzle)

    def load(self):
        super().load()
        self.async_addLoadCallback(self.freezeToonHead)

    def unload(self):
        self.unfreezeToonHead()
        self.ignoreAll()
        super().unload()

    def freezeToonHead(self):
        """
        Freezes the Toon Head.
        :return: None.
        """
        if self.stopBlink:
            self.toon.stopBlink()
        if self.stopStareAt:
            self.toon.stopStareAtNow()
        if self.stopLookAround:
            self.toon.stopLookAroundNow()
        if self.overwriteEyes:
            self.updateEyes()
        if self.overwriteMuzzle:
            self.updateMuzzle()
        if hasattr(self.toon, 'style'):
            if self.stopHeadPose:
                taskMgr.add(self.poseToonHeadTask, self.poseToonHeadTaskName())

    def unfreezeToonHead(self):
        """
        Unfreezes the Toon Head.
        :return: None.
        """
        self.frozen = False
        if self.stopBlink:
            self.toon.startBlink()
        if self.overwriteEyes:
            self.toon.normalEyes()
            self.toon.closeEyes()  # close eyes
            self.toon.openEyes()  # and then enter the right state
        if self.overwriteMuzzle:
            self.toon.hideAllMuzzles()
            self.toon.showNormalMuzzle()
        if hasattr(self.toon, 'style'):
            if self.toon.style.getType() == 'dog' and self.stopHeadPose:
                self.toon.loop(animName='neutral', partName='head')

    def updateEyes(self, eyeType=None):
        """
        Updates the eyes to be SAD.
        :return: None.
        """
        if not self.frozen:
            return
        if not self.overwriteEyes:
            return
        if eyeType not in ('sad', 'closed', 'open'):
            self.toon.sadEyes()    # set eye texture
            self.toon.closeEyes()  # close eyes
            self.toon.openEyes()   # and then enter the right state

    def updateMuzzle(self, muzzleType=None):
        """
        Updates the muzzle to be ANGY.
        :return: None.
        """
        if not self.frozen:
            return
        if not self.overwriteMuzzle:
            return
        if self.toon.isIgnoreCheesyEffect():
            return
        if muzzleType != 'angry':
            self.toon.hideAllMuzzles()
            self.toon.showAngryMuzzle()

    def poseToonHeadTask(self, task):
        """
        Ensures that the Toon's head is posed properly.
        :param task:
        :return:
        """
        if not self.frozen:
            return task.done
        if hasattr(self.toon, 'style') and self.toon.style.getType() == 'dog':
            self.toon.pose(animName='neutral', frame=0, partName='head')
        return task.cont

    def poseToonHeadTaskName(self) -> str:
        """
        Returns the task name for the poseHeadToonTask.
        :return: String name of the task.
        """
        return f"{id(self.toon)}-hat-pose-head-task"
