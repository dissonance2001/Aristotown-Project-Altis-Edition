from panda3d.core import *

from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.enums.ItemEnums import ItemType
from toontown.toonbase import ToontownGlobals
from toontown.utils.asyncutil.AsyncDirectObject import AsyncDirectObject
from toontown.toon import ToonDNA, AccessoryGlobals


class ToonAccessory(AsyncDirectObject):
    def __init__(self, toon, item: InventoryItem):
        super().__init__()
        self.toon = toon
        self.item = item

        self.accessoryNodes = []
        self.accessoryGeom = None

    def load(self):
        """Loads the accessory"""
        self._loadModel()
        self.async_addLoadCallback(self.start)

    def load_postModelLoad(self, model):
        self.accessoryGeom = model
        self._loadTexture()
        self._positionAccessory()
        self._attachAccessory()

        if self.item.getItemType() in (
        ItemType.Cosmetic_Hat, ItemType.Cosmetic_Glasses) and self.accessoryIgnoreEffects():
            self.accessoryGeom.hide()

        self.fixupAccessoryGeom()
        self.async_loadDone()

    def fixupAccessoryGeom(self):
        # Inheritors can edit the accessory geom here if they wish
        pass

    def unload(self):
        """Unloads the accessory"""
        AsyncDirectObject.cleanup(self)
        self.stop()
        for n in self.accessoryNodes:
            n.removeNode()

    def _loadModel(self):
        """Loads the accessory model"""
        itemDef = self.item.getItemDefinition()
        modelPath = itemDef.getModelPath()
        if modelPath:
            geom = loader.loadModel(modelPath)
            self.load_postModelLoad(geom)
        else:
            geom = hidden.attachNewNode('blankAccessory')
            self.load_postModelLoad(geom)

    def _loadTexture(self):
        """Loads a custom texture onto the accessory"""
        itemDef = self.item.getItemDefinition()
        texturePath = itemDef.getTexturePath()
        if not texturePath:
            return
        texture = loader.loadTexture(texturePath, okMissing=1)
        if texture and itemDef.getModelPath():
            texture.setMinfilter(Texture.FTLinearMipmapLinear)
            texture.setMagfilter(Texture.FTLinear)
            self.accessoryGeom.setTexture(texture, 1)

    def _positionAccessory(self):
        itemDef = self.item.getItemDefinition()
        placementDict = itemDef.getAccessoryPlacement(self.item) or {}
        itemType = self.item.getItemType()
        placementTuple = None

        if itemType in (ItemType.Cosmetic_Hat, ItemType.Cosmetic_Glasses):
            headType = self.toon.style.head
            for key in (headType, headType[:2], headType[:1]):
                if key in placementDict:
                    placementTuple = placementDict[key]
                    break
        elif itemType in (ItemType.Cosmetic_Backpack, ItemType.Cosmetic_Neck):
            torsoType = self.toon.style.torso[:1]
            if torsoType in placementDict:
                placementTuple = placementDict[torsoType]

        if placementTuple is None:
            if itemType == ItemType.Cosmetic_Hat:
                placementTuple = AccessoryGlobals.HatTransTable.get(self.toon.style.head[:2])
            elif itemType == ItemType.Cosmetic_Glasses:
                placementTuple = AccessoryGlobals.GlassesTransTable.get(self.toon.style.head[:2])
            elif itemType in (ItemType.Cosmetic_Backpack, ItemType.Cosmetic_Neck):
                placementTuple = AccessoryGlobals.BackpackTransTable.get(self.toon.style.torso[:1])

        if placementTuple is None:
            placementTuple = ((0, 0, 0), (0, 0, 0), (1, 1, 1))

        xyz, hpr, sxyz = placementTuple
        self.accessoryGeom.setPosHpr(*xyz, *hpr)
        self.accessoryGeom.setScale(*sxyz)

    def _attachAccessory(self):
        """Attaches the accessory to the toon"""
        itemDef = self.item.getItemDefinition()
        attachNode = itemDef.getToonAttachNode()
        if self.toon.hasLOD():
            for lodName in self.toon.getLODNames():
                lodRoot = self.toon.getLOD(lodName)
                for partNode in lodRoot.findAllMatches(attachNode):
                    accNode = partNode.attachNewNode('hatNode')
                    self.accessoryNodes.append(accNode)
                    self.accessoryGeom.instanceTo(accNode)
        else:
            for partNode in self.toon.findAllMatches(attachNode):
                accNode = partNode.attachNewNode('hatNode')
                self.accessoryNodes.append(accNode)
                self.accessoryGeom.instanceTo(accNode)

    def accessoryIgnoreEffects(self):
        # Do nothing if the following effects are ON
        # ignoredEffects = (ToontownGlobals.CESnowMan,
        #                   *ToontownGlobals.PumpkinEffects)
        ignoredEffects = []
        if self.toon.cheesyEffect in ignoredEffects:
            return True
        return False

    def forcePlace(self):
        self._positionAccessory()

    def start(self):
        """
        This is just here for custom implementation
        Called after load
        """
        pass

    def stop(self):
        """
        This is just here for custom implementation
        Called before unload
        """
        pass

    def request(self, request):
        """
        Does nothing for this class.
        However, is used for ToonActorAccessories.
        """
        pass

    @classmethod
    def modifyPreview(cls, geom):
        """
        Can be overriden in subclasses to modify the preview of an accessory item if needed
        """
        pass

    @property
    def toonIsReal(self):
        if getattr(self.toon, 'isFakeToon', False):
            return False

        from toontown.toon.DistributedToonBase import DistributedToonBase
        return isinstance(self.toon, DistributedToonBase)

    """
    Getters
    """

    def getInventoryItem(self) -> InventoryItem:
        return self.item
