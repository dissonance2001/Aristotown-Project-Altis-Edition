from toontown.toon.accessories.ToonActorAccessory import ToonActorAccessory
from toontown.toon.accessories.hats.HatHideEars import HatHideEars


class HighRollerHat(ToonActorAccessory, HatHideEars):
    hideEarsOn = [
        'cat', 'pig', 'beaver',
        'raccoon', 'bear'
    ]

    def load(self):
        super().load()
        self.async_addLoadCallback(self.hideEars)

    def unload(self):
        super().unload()
        self.showEars()

    def getAnimNames(self) -> tuple:
        return 'idle',
