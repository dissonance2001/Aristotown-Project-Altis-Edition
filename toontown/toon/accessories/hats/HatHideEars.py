from toontown.toon.accessories.ToonAccessory import ToonAccessory


class HatHideEars(ToonAccessory):

    hideEarsOn = [
        'dog', 'cat', 'mouse', 'horse',
        'rabbit', 'duck', 'monkey', 'bear',
        'pig', 'deer', 'beaver', 'alligator',
        'fox', 'bat', 'raccoon', 'turkey',
        'kiwi', 'kangaroo', 'koala', 'armadillo',
    ]

    def load(self):
        super().load()
        self.async_addLoadCallback(self.hideEars)

    def unload(self):
        super().unload()
        self.showEars()

    def earCheck(self):
        return hasattr(self.toon, 'style') and self.toon.style and (
            self.toon.style.getAnimal() in self.hideEarsOn or self.toon.style.head[:2] in self.hideEarsOn)

    def hideEars(self):
        if self.earCheck():
            self.toon.hideEars()

    def showEars(self):
        if self.earCheck():
            self.toon.showEars()


class OttomanNumberOnePlantHat(HatHideEars):
    """On the plant hat, ears are hidden on a few species."""

    hideEarsOn = [
        'cat', 'horse', 'rabbit', 'pig',
        'beaver', 'fox', 'bat',
        'raccoon', 'koala', 'kangaroo',
        'armadillo', 'mouse', 'bear'
    ]


class Beret(HatHideEars):
    """On the beret hat, ears are hidden on a few species"""

    hideEarsOn = [
        'cat', 'bear'
    ]
