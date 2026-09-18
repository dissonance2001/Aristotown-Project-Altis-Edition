from toontown.toon.accessories.ToonAccessory import ToonAccessory


class GlassesHideLashes(ToonAccessory):
    def load(self):
        super().load()
        self.async_addLoadCallback(self.toon.hideEyelashes)

    def unload(self):
        super().unload()
        self.toon.showEyelashes()
