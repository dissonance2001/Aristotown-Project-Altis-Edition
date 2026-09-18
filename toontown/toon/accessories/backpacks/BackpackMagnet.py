from toontown.toon.accessories.ToonAccessory import ToonAccessory


class BackpackMagnet(ToonAccessory):
    # TODO: Potentially add flicker to this?

    def fixupAccessoryGeom(self):
        lightning = self.accessoryGeom.find('**/lightning')
        lightning.hide()

    @classmethod
    def modifyPreview(cls, geom):
        """
        Can be overriden in subclasses to modify the preview of an accessory item if needed
        In this case, it removes the lightning from the preview geom
        """
        lightning = geom.find('**/lightning')
        if not lightning.isEmpty():
            lightning.removeNode()
