from toontown.toon.accessories.ToonAccessory import ToonAccessory


class GlassesHideEyes(ToonAccessory):
    def load(self):
        super().load()
        self.async_addLoadCallback(self.toon.hideEyes)

    def unload(self):
        super().unload()
        self.toon.showEyes()
