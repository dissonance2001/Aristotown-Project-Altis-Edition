from direct.showbase.DirectObject import DirectObject
from toontown.toon.accessories.ToonAccessory import ToonAccessory


class ChainsawConsultantHat(ToonAccessory, DirectObject):
    """
    A custom Hat type that freezes all head animations when active.

    Also does other visual stuff to sell the 'frozen' effect, like
    putting on a sad muzzle, disabling blinking, using sad eyes,
    and freezing the head anims on Dog toons.
    """
    redLightTime = 4.0

    def _openEvents(self):
        from toontown.toon.DistributedToon import DistributedToon
        if isinstance(self.toon, DistributedToon):
            self.accept(self.toon.getTakeDamageMessageName(), lambda _: self._initRedLight())

    def load(self):
        super().load()

        def chainsawPostLoad(self=self):
            self._openEvents()
            self._setGreenLight()

        self.async_addLoadCallback(chainsawPostLoad)

    def fixupAccessoryGeom(self):
        # hack: the chainsaw hat has the red bulb & the green highlights initially hidden
        # so that it doesn't misbehave when being previewed in the items page

        # Chainsaw's hat is a bit special since it has some transparent nodes
        if self.toonIsReal:
            self._baseHatNode.setBin('opaque', 1)
            self._redLightNode.setBin('transparent', 1)
            self._redLightNode.find("**/lights_red_edge").setBin('opaque', 1)
            self._greenLightNode.setBin('transparent', 1)
            self._greenLightNode.find("**/lights_green_edge").setBin('opaque', 1)
            # don't think this works vvv
            self._greenLightNode.find("**/lights_green_highlight").show()

    def unload(self):
        self.ignoreAll()
        self.removeTask(self._resetLightTaskName())
        super().unload()

    def _setGreenLight(self):
        self._greenLightNode.show()
        self._redLightNode.hide()

    def _setRedLight(self):
        self._greenLightNode.hide()
        self._redLightNode.show()

    def _initRedLight(self):
        self._setRedLight()
        self.removeTask(self._resetLightTaskName())
        self.doMethodLater(self.redLightTime, self._resetLightTask, self._resetLightTaskName())

    def _resetLightTask(self, task):
        self._setGreenLight()
        return task.done

    def _resetLightTaskName(self) -> str:
        return f"{self.toon.toonName}-reset-head-lights"

    @property
    def _greenLightNode(self):
        return self.accessoryGeom.find('**/lights_1')

    @property
    def _redLightNode(self):
        return self.accessoryGeom.find('**/lights_2')

    @property
    def _baseHatNode(self):
        return self.accessoryGeom.find('**/hat_main')
