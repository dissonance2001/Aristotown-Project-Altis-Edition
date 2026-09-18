from toontown.toon import ToonDNA
from .ToonAccessory import ToonAccessory
from toontown.utils.asyncutil.AsyncActor import AsyncActor
from ...inventory.enums.ItemEnums import ItemType


class ToonActorAccessory(ToonAccessory, AsyncActor):
    """
    A hodgepodge of ToonAccessory and AsyncActor, allowing
    accessories on Toons with associated model animations.
    """

    def __init__(self, toon, item):
        ToonAccessory.__init__(self, toon, item)
        AsyncActor.__init__(self, flattenable=0, setFinal=1)
        self.setBlend(frameBlend=base.wantSmoothAnims)
        self.accessoryGeom = self

        self.animNames = ()
        self.cleanedUp = False

    """
    Methods which must be overwritten
    by superclasses.
    """

    def getAnimNames(self) -> tuple:
        """
        Example:
        return 'loop', 'idle1', 'idle2', 'idle3'

        The first one is the default animation which gets looped.
        """
        raise Exception("getAnimDict must be defined by subclasses.")

    """
    Methods which can be called
    upon by superclasses.
    """

    def complete(self):
        """
        This method gets called upon on the
        completion of the load method.
        """
        pass

    def finish(self):
        """
        This method gets called upon at the
        start of the unload method.
        """
        pass

    def request(self, request):
        """
        This method can be called with specific request strings.
        A subclass can overwrite this method, and do fancy
        things reactively to various things.

        List of requests:
        dance-start, dance-end
        """
        pass

    """
    Methods that handle creation of
    the actual accessory.
    """

    def load(self):
        """Loads the accessory"""
        modelPath = self.item.getItemDefinition().getModelPath()
        animDict = self._buildAnimDict(modelPath)
        self.loadAnims(animDict)
        self.loadModel(modelPath, copy=True, callback=self.load_postModelLoad)
        self.async_addLoadCallback(self.start)

    def load_postModelLoad(self):
        self.loop(self.animNames[0])

        self._loadTexture()

        self.setShaderAuto()

        self._positionAccessory()
        self._attachAccessory()

        if self.item.getItemType() in (
        ItemType.Cosmetic_Hat, ItemType.Cosmetic_Glasses) and self.accessoryIgnoreEffects():
            self.accessoryGeom.hide()

        self.async_loadDone()

    def unload(self):
        """Unloads the accessory"""
        self.finish()
        self.stop()
        AsyncActor.cleanup(self)
        self.cleanedUp = True
        for n in self.accessoryNodes:
            n.removeNode()

    def start(self):
        self.complete()

    def stop(self, val=None):
        if not self.cleanedUp:
            AsyncActor.stop(self, val)

    """
    Some other stuff.
    """

    def uniqueName(self, name):
        # Unique name.
        if hasattr(self.toon, 'uniqueName'):
            return self.toon.uniqueName(name)
        else:
            # This can be called if the Toon is just a visual Toon.
            if hasattr(base, 'localAvatar'):
                return base.localAvatar.uniqueName(name)
            else:
                # We are literally on the main menu who cares
                return f'main-menu-{name}'

    def _buildAnimDict(self, modelPath) -> dict:
        self.animNames = self.getAnimNames()
        retdict = {}
        for anim in self.animNames:
            retdict[anim] = f'{modelPath}-{anim}'
        return retdict
