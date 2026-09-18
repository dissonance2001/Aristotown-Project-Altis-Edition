"""
This module contains the item data for furniture.
"""
from __future__ import annotations
from direct.actor.Actor import Actor
from panda3d.core import NodePath

from toontown.building.interior.props.LavaLamp import LavaLamp
from toontown.estate.EstateGlobals import EstateItemType, EstateItemPlacementFlags, EstateKitType
from toontown.estate.items import EstateItemGlobals
from toontown.estate.zones.EstateDoorGlobals import EstateDoorType
from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.base.ItemDefinition import ItemDefinition
from typing import Dict, Optional
from enum import IntEnum

from toontown.inventory.enums.ItemAttribute import ItemAttribute
from toontown.inventory.enums.ItemEnums import FurnitureItemType
from toontown.utils import ColorHelper

textureExtension = ".png"


class FurnitureDefinition(ItemDefinition):
    """
    The definition structure for furniture.
    """

    SpecialFurnitureClasses = {
        FurnitureItemType.Prop_Fassuite_Lamp_Lava: LavaLamp,
    }

    def __init__(self,
                 modelName,
                 modelPath="",
                 modelNamePrefix="",
                 overrideDefaultModelPrefix=False,
                 textureName=None,
                 texturePath="",
                 textureNamePrefix="",
                 overrideDefaultTexturePrefix=False,
                 estateItemType: EstateItemType = EstateItemType.GENERIC,
                 modelFind: str = '',
                 estateItemPlacementFlag: EstateItemPlacementFlags = EstateItemPlacementFlags.STANDARD,
                 modelScale: float | tuple = 1.0,
                 modelScaleRange: tuple | None = None,
                 hidePlacedModel: bool = False,
                 nodeColors: dict[str, tuple] = None,
                 nodeTextures: dict[str, str] = None,
                 customColorNode: str = None,
                 customColors: dict[str, tuple] = None,
                 estateKitType: EstateKitType | None = None,
                 maxItems: int = -1,
                 # For actor furniture items.
                 wantActor: bool = False,
                 actorAnimations: dict[str, str] = None,
                 collisionNode: str = "",
                 throwables: int = None,
                 # For furniture items with sequence nodes.
                 sequenceNodes: list[str] | None = None,
                 animSpeed: float | None = None,
                 # For doorway definitions.
                 doorType: EstateDoorType = EstateDoorType.DEBUG,
                 doorOrigin: str = '',
                 doorColor: str = 'ffffff',
                 doorPosHprScale: tuple = (0, 0, 0, 0, 0, 0, 1.0, 1.0, 1.0),
                 # For chair definitions.
                 chairCollision: str | None = None,
                 chairAction: str = " to sit on the ",
                 chairPositions: tuple[tuple[float, float, float, float]] = None,
                 # For skybox definitions.
                 skyPath: str | None = None,
                 **kwargs):
        super().__init__(**kwargs)

        modelType = "a" if wantActor else "m"

        self.modelName = modelName
        self.modelPath = modelPath
        if not self.modelPath:
            if estateItemType == EstateItemType.HOUSE:
                self.modelPath = "areas/estate/houses/models/"
            else:
                self.modelPath = "areas/estate/furniture/models/"
        if not modelNamePrefix and not overrideDefaultModelPrefix:
            if estateItemType == EstateItemType.HOUSE:
                modelNamePrefix = "ara_est_prp_house_"
            elif estateItemType == EstateItemType.WINDOW_VIEW:
                modelNamePrefix = "ara_est_prp_wv_"
            else:
                modelNamePrefix = "ara_est_prp_furn_"

        self.textureName = textureName
        self.texturePath = texturePath
        if not self.texturePath:
            if estateItemType == EstateItemType.HOUSE:
                self.texturePath = "areas/estate/houses/maps/"
            else:
                self.texturePath = "areas/estate/furniture/maps/"
        if not textureNamePrefix and not overrideDefaultTexturePrefix:
            if estateItemType == EstateItemType.HOUSE:
                textureNamePrefix = "ara_est_prp_house_"
            elif estateItemType == EstateItemType.WINDOW_VIEW:
                textureNamePrefix = "ara_est_prp_wv_"
            else:
                textureNamePrefix = "ara_est_prp_furn_"

        if modelNamePrefix and not modelNamePrefix.endswith("_"):
            modelNamePrefix += "_"
        if textureNamePrefix and not textureNamePrefix.endswith("_"):
            textureNamePrefix += "_"

        # Only here temp until i port everything to use the cc_x prefix.
        if not overrideDefaultModelPrefix:
            self.baseModelPrefix = f"cc_{modelType}_{modelNamePrefix}"
        else:
            self.baseModelPrefix = modelNamePrefix

        if not overrideDefaultTexturePrefix:
            self.baseTexturePrefix = f"cc_t_{textureNamePrefix}"
        else:
            self.baseTexturePrefix = textureNamePrefix

        self.estateItemType = estateItemType
        self.modelFind = modelFind
        self.estateItemPlacementFlag = estateItemPlacementFlag
        if type(modelScale) is not tuple:
            modelScale = (modelScale, modelScale, modelScale)

        self.modelScale = modelScale
        # Todo
        if not modelScaleRange:
            modelScaleRange = EstateItemGlobals.ESTATE_ITEM_SCALE_RANGE
        self.modelScaleRange = modelScaleRange

        self.hidePlacedModel = hidePlacedModel
        self.nodeColors = nodeColors
        self.nodeTextures = nodeTextures
        self.doorType = doorType
        self.doorOrigin = doorOrigin
        self.doorColor = doorColor
        self.doorPosHprScale = doorPosHprScale
        self.estateKitType = estateKitType
        self.maxItems = maxItems
        self.wantActor = wantActor
        self.actorAnimations = actorAnimations
        self.collisionNode = collisionNode
        self.throwables = throwables
        self.customColorNode = customColorNode
        self.customColors = customColors
        self.sequenceNodes = sequenceNodes
        self.animSpeed = animSpeed
        self.chairCollision = chairCollision
        self.chairAction = chairAction
        self.chairPositions = chairPositions
        self.skyPath = skyPath

    def getModelName(self):
        if not self.modelName:
            return None
        return self.modelName

    def getModelPath(self):
        if not self.modelName:
            return None
        return f"{self.modelPath}{self.baseModelPrefix}{self.modelName}"

    def getTexturePath(self):
        if not self.textureName:
            return None
        return f"{self.texturePath}{self.baseTexturePrefix}{self.textureName}{textureExtension}"

    def getModelScale(self) -> tuple:
        return self.modelScale

    def getDoorType(self) -> EstateDoorType:
        return self.doorType

    def getDoorOrigin(self) -> str:
        return self.doorOrigin

    def getDoorColor(self) -> tuple:
        return ColorHelper.hexToPCol(self.doorColor)

    def getDoorPosHprScale(self) -> tuple:
        return self.doorPosHprScale

    def getEstateKitType(self) -> EstateKitType | None:
        return self.estateKitType

    def getMaxItems(self) -> int:
        return self.maxItems

    def getCustomColorNode(self) -> str | None:
        return self.customColorNode

    def getCustomColorChoices(self) -> dict | None:
        return self.customColors

    def getCustomColor(self, item: Optional[InventoryItem] = None) -> str:
        if item is None:
            # Default to white.
            return "FFFFFF"

        hex = item.getAttribute(ItemAttribute.PROP_COLOR_HEX)

        # If the color hasn't been set yet, use one of the specified colors if possible.
        if hex is None:
            if self.customColors is not None:
                return ColorHelper.rgbToHex(*list(map(lambda x: round(x * 255),
                                                      list(self.customColors.values())[0][:3])))
            # Default to white.
            return "FFFFFF"

        return hex

    def getSequenceNodes(self) -> list[str] | None:
        return self.sequenceNodes

    def getAnimSpeed(self) -> float | None:
        return self.animSpeed

    def getWantActor(self) -> bool:
        return self.wantActor

    def getActorAnimations(self) -> dict[str, str]:
        """
        Converts all supplied animations names to full paths. For this to work, all animations need to be in
        the same directory as the base model.
        :return:
        """
        if self.actorAnimations is None:
            return {}
        return {k: f"{self.modelPath}{self.baseModelPrefix}{v}" for k, v in self.actorAnimations.items()}

    def getCollisionNode(self) -> str:
        return self.collisionNode

    def getThrowables(self) -> int:
        return self.throwables

    def getChairCollision(self) -> str | None:
        return self.chairCollision

    def getChairAction(self) -> str:
        return self.chairAction

    def getChairPositions(self) -> tuple[tuple[float, float, float, float]] | None:
        return self.chairPositions

    def getSkyPath(self) -> str | None:
        return self.skyPath

    def getItemTypeName(self):
        return 'Furniture'

    def getRewardName(self, item: Optional[InventoryItem] = None):
        return f'{self.getName()} Furniture'

    def getClickable(self) -> tuple[bool, str]:
        if not base.estate:
            return True, ""

        if (
            self.getEstateKitType() is not None
            and self.getEstateKitType() != base.estate.getCurrentSubzone().getStyle().getItemDefinition().getEstateKitType()
        ):
            return False, "This item cannot be placed in the current Estate Kit."

        if (
            -1 < self.getMaxItems() <= sum(item.getItem().getItemDefinition().getEstateItemType() == self.getEstateItemType()
                                           for item in base.estate.getAllItemObjects())
        ):
            return False, "There are too many items of this type currently placed."

        return True, ""

    def isEstatePlaceable(self, item: InventoryItem) -> bool:
        """Is this item placeable in an estate?"""
        return True

    def getEstateItemType(self) -> EstateItemType:
        """
        Determines the AI object generated for this Item
        when placed in the estate.
        """
        return self.estateItemType

    def getEstateItemPlacementFlag(self) -> EstateItemPlacementFlags:
        """
        Determines how this object will be placed in-world in the estate.
        """
        return self.estateItemPlacementFlag

    def makeItemModel(self, *extraArgs, item: Optional[InventoryItem] = None) -> NodePath:
        """
        Returns a nodepath that represents this item.
        """
        specialCls = self.SpecialFurnitureClasses.get(self.itemSubtype, None)
        if specialCls:
            return specialCls()

        # Default load.
        if self.wantActor:
            node = model = Actor(self.getModelPath(), self.getActorAnimations())
            node.setBlend(frameBlend=base.wantSmoothAnims)
        else:
            node = hidden.attachNewNode('coolFurnitureModel')
            model = loader.loadModel(self.getModelPath())
            if self.modelFind:
                newModel = model.find(f'**/{self.modelFind}')
                model.removeNode()
                model = newModel
                model.setPosHprScale(0, 0, 0, 0, 0, 0, 1, 1, 1)
            model.reparentTo(node)
        model.setScale(*self.getModelScale())

        if self.animSpeed is not None:
            for seqNode in model.findAllMatches('**/seqNode*'):
                seqNode.node().setPlayRate(self.animSpeed)

        if self.nodeColors:
            for nodePath, col in self.nodeColors.items():
                for targetNode in model.findAllMatches(nodePath):
                    targetNode.setColorScale(col, 1)

        customColorNode = self.getCustomColorNode()
        if customColorNode:
            customColor = ColorHelper.hexToPCol(self.getCustomColor(item))
            for targetNode in model.findAllMatches(customColorNode):
                targetNode.setColorScale(*customColor)

        # Apply custom textures if need be.
        if self.estateItemType == EstateItemType.GENERIC_PLANE:
            texturePath = self.getTexturePath()
            if texturePath:
                texture = loader.loadTexture(texturePath)
                model.setTexture(texture, 1)

        if self.nodeTextures:
            for nodePath, texName in self.nodeTextures.items():
                self.textureName = texName
                texturePath = self.getTexturePath()
                texture = loader.loadTexture(texturePath)
                for targetNode in model.findAllMatches(nodePath):
                    targetNode.setTexture(texture, 1)

        return node


FurnitureRegistry: Dict[IntEnum, FurnitureDefinition] = {
    ### Debug Props ###
    # region
    FurnitureItemType.Debug_Doorway: FurnitureDefinition(
        name = 'Test Doorway',
        description = 'An exquisite testing doorway.',
        modelName = 'desat_pillar_cracked',
        modelPath = "phase_4/models/props/",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateItemType = EstateItemType.DOORWAY,
    ),
    FurnitureItemType.Debug_Floor_Lava: FurnitureDefinition(
        name = 'Evil lava',
        description = '>:)',
        modelName = 'plane_ouch',
        modelPath = "props/test/models/",
        modelNamePrefix = "test_prp_",
        estateItemType = EstateItemType.DEBUG_OUCH,
    ),
    FurnitureItemType.Debug_Scale_Interior_Small: FurnitureDefinition(
        name = 'ScaleRef Interior (Small)',
        modelPath = "props/test/models/",
        modelName = "plane_64x42",
        modelNamePrefix = "test_prp_",
    ),
    FurnitureItemType.Debug_Scale_Interior_Medium: FurnitureDefinition(
        name = 'ScaleRef Interior (Medium)',
        modelPath = "props/test/models/",
        modelName = "plane_64x42",
        modelNamePrefix = "test_prp_",
        modelScale = 2,
    ),
    FurnitureItemType.Debug_Scale_Interior_Large: FurnitureDefinition(
        name = 'ScaleRef Interior (Large)',
        modelPath = "props/test/models/",
        modelName = "plane_64x42",
        modelNamePrefix = "test_prp_",
        modelScale = 3,
    ),
    FurnitureItemType.Debug_Scale_Exterior_Small: FurnitureDefinition(
        name = 'ScaleRef Exterior (Small)',
        modelPath = "props/test/models/",
        modelName = "plane_150x150",
        modelNamePrefix = "test_prp_",
    ),
    FurnitureItemType.Debug_Scale_Exterior_Medium: FurnitureDefinition(
        name = 'ScaleRef Exterior (Medium)',
        modelPath = "props/test/models/",
        modelName = "plane_150x150",
        modelNamePrefix = "test_prp_",
        modelScale = 2.25,
    ),
    FurnitureItemType.Debug_Scale_Exterior_Large: FurnitureDefinition(
        name = 'ScaleRef Exterior (Large)',
        modelPath = "props/test/models/",
        modelName = "plane_150x150",
        modelNamePrefix = "test_prp_",
        modelScale = 4,
    ),
    FurnitureItemType.Debug_Primitive_Cube_Floor: FurnitureDefinition(
        name = 'Primitive Cube (Floor)',
        modelPath="core/props/models/",
        modelName="primitives",
        modelNamePrefix="cc_m_core_prp_",
        modelFind="floor_cube_grp",
        overrideDefaultModelPrefix = True,
        estateItemType=EstateItemType.DEBUG_PRIMITIVE,
    ),
    FurnitureItemType.Debug_Primitive_Cube_Wall: FurnitureDefinition(
        name='Primitive Cube (Wall)',
        modelPath="core/props/models/",
        modelName="primitives",
        modelNamePrefix="cc_m_core_prp_",
        modelFind="wall_cube_grp",
        overrideDefaultModelPrefix=True,
        estateItemType=EstateItemType.DEBUG_PRIMITIVE,
    ),
    FurnitureItemType.Debug_Primitive_Sphere: FurnitureDefinition(
        name='Primitive Sphere',
        modelPath="core/props/models/",
        modelName="primitives",
        modelNamePrefix="cc_m_core_prp_",
        modelFind="sphere_grp",
        overrideDefaultModelPrefix=True,
        estateItemType=EstateItemType.DEBUG_PRIMITIVE,
    ),
    FurnitureItemType.Debug_Primitive_Stair: FurnitureDefinition(
        name='Primitive Stair',
        modelPath="core/props/models/",
        modelName="primitives",
        modelNamePrefix="cc_m_core_prp_",
        modelFind="stair_grp",
        overrideDefaultModelPrefix=True,
        estateItemType=EstateItemType.DEBUG_PRIMITIVE,
    ),
    FurnitureItemType.Debug_Primitive_Ramp: FurnitureDefinition(
        name='Primitive Ramp',
        modelPath="core/props/models/",
        modelName="primitives",
        modelNamePrefix="cc_m_core_prp_",
        modelFind="ramp_grp",
        overrideDefaultModelPrefix=True,
        estateItemType=EstateItemType.DEBUG_PRIMITIVE,
    ),
    FurnitureItemType.Debug_Primitive_Cylinder: FurnitureDefinition(
        name='Primitive Cylinder',
        modelPath="core/props/models/",
        modelName="primitives",
        modelNamePrefix="cc_m_core_prp_",
        modelFind="cylinder_grp",
        overrideDefaultModelPrefix=True,
        estateItemType=EstateItemType.DEBUG_PRIMITIVE,
    ),

    # Debug_Primitive_Sphere = 2001
    # Debug_Primitive_Stair = 2002
    # Debug_Primitive_Ramp = 2003
    # endregion

    ### Default (classic collection) ###
    # region
    FurnitureItemType.Prop_Classic_GagFan: FurnitureDefinition(
        name = "Juliette's Fan",
        description = "No Description",
        modelName = "classic_fan_gag",
        estateItemType = EstateItemType.GENERIC,
        animSpeed = 0.50,
    ),
    FurnitureItemType.Prop_Classic_Bed: FurnitureDefinition(
        name = "Bed",
        description = "No Description",
        modelName = "classic_bed_regular",
        textureName = "classic_bed_palette_1_yellow",
        estateItemType = EstateItemType.GENERIC,
        customColorNode = '**/bed_frame_geom',
        customColors = {
            "Burly Wood": (0.933, 0.773, 0.569, 1.0),
            "Dark Goldenrod": (0.9333, 0.6785, 0.055, 1.0),
            "Peach Puff": (0.545, 0.451, 0.333, 1.0),
            "Deep Red": (0.541, 0.0, 0.0, 1.0),
            "Chocolate": (0.5451, 0.2706, 0.0745, 1.0),
            "Rosey Brown": (0.5451, 0.4118, 0.4118, 1.0),
        }
    ),
    FurnitureItemType.Prop_Classic_Couch: FurnitureDefinition(
        name = "Couch",
        description = "No Description",
        modelName = "classic_couch",
        modelPath = "props/toon_props/models/",
        modelNamePrefix = "gen_toon_prp_deco_",
        estateItemType = EstateItemType.PROP_CHAIR,
        customColorNode = '**/*couch',
        customColors = {
            "Red": (0.792, 0.353, 0.29, 1.0),
            "Green": (0.176, 0.592, 0.439, 1.0),
            "Purple": (0.439, 0.424, 0.682, 1.0),
            "Blue": (0.325, 0.58, 0.835, 1.0),
            "Pink": (0.753, 0.345, 0.557, 1.0),
            "Yellow": (0.992, 0.843, 0.392, 1.0),
        },
        chairCollision = "**/collision",
        chairPositions = ((-1.2, -2.6, 1.7, 180), (1.2, -2.6, 1.7, 180))
    ),
    FurnitureItemType.Prop_Classic_Candle: FurnitureDefinition(
        name = "Candle",
        description = "No Description",
        modelName = "win_candlestick_unlit",
        estateItemType = EstateItemType.GENERIC,
        customColorNode = '**/candlestick/candlestick',
        customColors = {
            "Green": (0.176, 0.592, 0.439, 1.0),
            "Purple": (0.439, 0.424, 0.682, 1.0),
            "Blue": (0.325, 0.58, 0.835, 1.0),
            "Pink": (0.753, 0.345, 0.557, 1.0),
            "Yellow": (0.992, 0.843, 0.392, 1.0),
            "Red": (0.792, 0.353, 0.29, 1.0),
        },
    ),
    FurnitureItemType.Prop_Classic_Candle_Lit: FurnitureDefinition(
        name = "Lit Candle",
        description = "No Description",
        modelName = "win_candlestick_lit",
        estateItemType = EstateItemType.GENERIC,
        customColorNode = '**/candlestick/candlestick',
        customColors = {
            "Green": (0.176, 0.592, 0.439, 1.0),
            "Purple": (0.439, 0.424, 0.682, 1.0),
            "Blue": (0.325, 0.58, 0.835, 1.0),
            "Pink": (0.753, 0.345, 0.557, 1.0),
            "Yellow": (0.992, 0.843, 0.392, 1.0),
            "Red": (0.792, 0.353, 0.29, 1.0),
        },
    ),

    FurnitureItemType.Prop_Classic_Chair_Cushioned: FurnitureDefinition(
        name = "Cushioned Chair",
        description = "No Description",
        modelName = "classic_chair",
        modelPath = "props/toon_props/models/",
        modelNamePrefix = "gen_toon_prp_deco_",
        estateItemType = EstateItemType.PROP_CHAIR,
        customColorNode = '**/*couch',
        customColors = {
            "Red": (0.792, 0.353, 0.29, 1.0),
            "Green": (0.176, 0.592, 0.439, 1.0),
            "Purple": (0.439, 0.424, 0.682, 1.0),
            "Blue": (0.325, 0.58, 0.835, 1.0),
            "Pink": (0.753, 0.345, 0.557, 1.0),
            "Yellow": (0.992, 0.843, 0.392, 1.0),
        },
        chairCollision = "**/g2",
        chairPositions = ((0, 0, 0, 180),),
    ),

    FurnitureItemType.Prop_Classic_Chair_Regal: FurnitureDefinition(
        name = "Armchair",
        description = "No Description",
        modelName = "classic_chair_regal",
        textureName = "classic_chair_regal_palette_1_green",
        estateItemType = EstateItemType.PROP_CHAIR,
        customColorNode = '**/chair_base_geom',
        customColors = {
            "Red": (0.792, 0.353, 0.29, 1.0),
            "Green": (0.176, 0.592, 0.439, 1.0),
            "Purple": (0.439, 0.424, 0.682, 1.0),
            "Blue": (0.325, 0.58, 0.835, 1.0),
            "Pink": (0.753, 0.345, 0.557, 1.0),
            "Yellow": (0.992, 0.843, 0.392, 1.0),
        },
        chairCollision = "**/chair_coll",
        chairPositions = ((0, -4.9, 2.1, 180),)
    ),

    FurnitureItemType.Prop_Classic_UmbrellaStand: FurnitureDefinition(
        name = "Umbrella Stand",
        description = "No Description",
        modelName = "classic_bin_umbrella",
        modelPath = "props/toon_props/models/",
        modelNamePrefix = "gen_toon_prp_deco_",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_CoatRack: FurnitureDefinition(
        name = "Coat Rack",
        description = "No Description",
        modelName = "classic_coatrack",
        modelPath = "props/toon_props/models/",
        modelNamePrefix = "gen_toon_prp_deco_",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_TrashCan: FurnitureDefinition(
        name = "Trash Can",
        description = "No Description",
        modelName = "classic_trashcan_paper",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Bed_Bathtub: FurnitureDefinition(
        name = "Bathtub Bed",
        description = "No Description",
        modelName = "classic_bed_bath",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Chair_Dining: FurnitureDefinition(
        name = "Chair",
        description = "No Description",
        modelName = "classic_chair_dining",
        estateItemType = EstateItemType.PROP_CHAIR,
        chairCollision = "**/seat_coll",
        chairPositions = ((0, -2.7, 1.8, 180),),
    ),
    FurnitureItemType.Prop_Classic_Chair_Desk: FurnitureDefinition(
        name = "Desk Chair",
        description = "No Description",
        modelName = "classic_chair_office",
        estateItemType = EstateItemType.PROP_CHAIR,
        chairCollision = "**/pPlane1",
        chairPositions = ((0, -2.8, 1.8, 180),),
    ),
    FurnitureItemType.Prop_Classic_Desk: FurnitureDefinition(
        name = "Desk",
        description = "No Description",
        modelName = "classic_desk",
        modelPath = "props/toon_props/models/",
        modelNamePrefix = "gen_toon_prp_deco_",
        estateItemType = EstateItemType.GENERIC,
    ),

    FurnitureItemType.Prop_Classic_Lamp_Table: FurnitureDefinition(
        name = "Moody Table Lamp",
        description = "No Description",
        modelName = "classic_lamp_moody",
        estateItemType = EstateItemType.GENERIC,
        customColorNode = '**/top',
        customColors = {
            "Green": (0.176, 0.592, 0.439, 1.0),
            "Purple": (0.439, 0.424, 0.682, 1.0),
            "Blue": (0.325, 0.58, 0.835, 1.0),
            "Pink": (0.753, 0.345, 0.557, 1.0),
            "Yellow": (0.992, 0.843, 0.392, 1.0),
            "Red": (0.792, 0.353, 0.29, 1.0),
        },
    ),
    FurnitureItemType.Prop_Classic_TV: FurnitureDefinition(
        name = "Classic Retro TV",
        description = "No Description",
        modelName = "classic_tv",
        estateItemType = EstateItemType.PROP_TV,
    ),
    FurnitureItemType.Prop_Classic_Wardrobe_Cute: FurnitureDefinition(
        name = "Cute Wardrobe",
        description = "No Description",
        modelName = "gen_closet_1",
        estateItemType = EstateItemType.PROP_WARDROBE,
        modelScale = 0.85,
    ),
    FurnitureItemType.Prop_Classic_Wardrobe_Cool: FurnitureDefinition(
        name = "Cool Wardrobe",
        description = "No Description",
        modelName = "gen_closet_2",
        estateItemType = EstateItemType.PROP_WARDROBE,
        modelScale = 0.85,
    ),
    FurnitureItemType.Prop_Classic_Lamp_Short: FurnitureDefinition(
        name = "Short Lamp",
        description = "No Description",
        modelName = "classic_lamp_small",
        modelPath = "props/toon_props/models/",
        modelNamePrefix = "gen_toon_prp_deco_",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Lamp_Tall: FurnitureDefinition(
        name = "Tall Lamp",
        description = "No Description",
        modelName = "classic_lamp_tall",
        modelPath = "props/toon_props/models/",
        modelNamePrefix = "gen_toon_prp_deco_",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_DisplayCabinet_Red: FurnitureDefinition(
        name = "Red Display Cabinet",
        description = "No Description",
        modelName = "classic_cabinet_sports",
        nodeTextures = {'**/cabinet_body_geom': "classic_cabinet_palette_1_red"},
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_DisplayCabinet_Yellow: FurnitureDefinition(
        name = "Yellow Display Cabinet",
        description = "No Description",
        modelName = "classic_cabinet_sports",
        nodeTextures = {'**/cabinet_body_geom': "classic_cabinet_palette_1_yellow"},
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Bookcase_Tall: FurnitureDefinition(
        name = "Tall Bookcase",
        description = "No Description",
        modelName = "classic_bookcase_tall",
        modelPath = "props/toon_props/models/",
        modelNamePrefix = "gen_toon_prp_deco_",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Bookcase_Low: FurnitureDefinition(
        name = "Low Bookcase",
        description = "No Description",
        modelName = "classic_bookcase_short",
        modelPath = "props/toon_props/models/",
        modelNamePrefix = "gen_toon_prp_deco_",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Bed_Trolley: FurnitureDefinition(
        name = "Trolley Bed",
        description = "No Description",
        modelName = "classic_bed_trolley",
        estateItemType = EstateItemType.GENERIC,
        animSpeed = 0.25,
    ),
    FurnitureItemType.Prop_Classic_Piano: FurnitureDefinition(
        name = "Player Piano",
        description = "No Description",
        modelName = "classic_piano",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Organ: FurnitureDefinition(
        name = "Pipe Organ",
        description = "No Description",
        modelName = "classic_organ",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Cannon_Interactive: FurnitureDefinition(
        name = "Toon Cannon",
        description = "No Description",
        modelName = "toon_cannon",
        modelPath = "phase_4/models/minigames/",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateItemType = EstateItemType.PROP_INTERACTIVE_CANNON,
    ),

    FurnitureItemType.Prop_MG_Cannon_Tower: FurnitureDefinition(
        name = "Prop_MG_Cannon_Tower",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "can_tower",
        modelNamePrefix = "mg_",
        modelPath = "activity/trolley/models/",
    ),

    FurnitureItemType.Prop_MG_Cannon_Hill: FurnitureDefinition(
        name = "Prop_MG_Cannon_Hill",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "can_hil",
        modelNamePrefix = "mg_",
        modelPath = "activity/trolley/models/",
    ),

    FurnitureItemType.Prop_MG_Slingshot_Trampoline: FurnitureDefinition(
        name = "Prop_MG_Slingshot_Trampoline",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "sli_trampoline",
        modelNamePrefix = "mg_",
        modelPath = "activity/trolley/models/",
    ),

    FurnitureItemType.Ceiling_MG_Vine: FurnitureDefinition(
        name = "Ceiling_MG_Vine",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "vin_vine",
        modelNamePrefix = "mg_",
        modelPath = "activity/trolley/models/",
    ),

    FurnitureItemType.Prop_Classic_Trunk_Cool: FurnitureDefinition(
        name = "Cool Trunk",
        description = "No Description",
        modelName = "gen_trunk_1",
        estateItemType = EstateItemType.PROP_TRUNK,
        modelScale = 0.9,
    ),
    FurnitureItemType.Prop_Classic_Trunk_Cute: FurnitureDefinition(
        name = "Cute Trunk",
        description = "No Description",
        modelName = "gen_trunk_2",
        estateItemType = EstateItemType.PROP_TRUNK,
        modelScale = 0.9,
    ),
    FurnitureItemType.Prop_Classic_Mailbox: FurnitureDefinition(
        name = "Prop_Classic_Mailbox",
        description = "No Description",
        modelName = 'mailbox_1',
        modelNamePrefix = "ara_est_prp_ext_",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Tree_Oak_Med_1: FurnitureDefinition(
        name = "Prop_Tree_Oak_Med_1",
        description = "No Description",
        modelName = "tree_1",
        modelPath = "props/general/models/",
        modelNamePrefix = "ara_gen_prp_",
        estateItemType = EstateItemType.GENERIC,
        modelScale = 0.75,
    ),
    FurnitureItemType.Prop_Tree_Oak_Med_2: FurnitureDefinition(
        name = "Prop_Tree_Oak_Med_2",
        description = "No Description",
        modelName = "tree_2",
        modelPath = "props/general/models/",
        modelNamePrefix = "ara_gen_prp_",
        estateItemType = EstateItemType.GENERIC,
        modelScale = 0.75,
    ),
    FurnitureItemType.Prop_Tree_Oak_Med_3: FurnitureDefinition(
        name = "Prop_Tree_Oak_Med_3",
        description = "No Description",
        modelName = "tree_3",
        modelPath = "props/general/models/",
        modelNamePrefix = "ara_gen_prp_",
        estateItemType = EstateItemType.GENERIC,
        modelScale = 0.75,
    ),
    FurnitureItemType.Prop_Tree_Oak_Dark_1: FurnitureDefinition(
        name = "Prop_Tree_Oak_Dark_1",
        description = "No Description",
        modelName = "tree_4",
        modelPath = "props/general/models/",
        modelNamePrefix = "ara_gen_prp_",
        estateItemType = EstateItemType.GENERIC,
        modelScale = 0.75,
    ),
    FurnitureItemType.Prop_Tree_Oak_Light_1: FurnitureDefinition(
        name = "Prop_Tree_Oak_Light_1",
        description = "No Description",
        modelName = "tree_5",
        modelPath = "props/general/models/",
        modelNamePrefix = "ara_gen_prp_",
        estateItemType = EstateItemType.GENERIC,
        modelScale = 0.75,
    ),
    FurnitureItemType.Prop_Classic_Garden_Wheelbarrow: FurnitureDefinition(
        name = "Prop_Wheelbarrow_Classic",
        description = "No Description",
        modelName = "wheelbarrow",
        modelPath = "props/general/models/",
        modelNamePrefix = "gdg_prp_",
        estateItemType = EstateItemType.GENERIC,
        modelScale = 0.75,
    ),
    FurnitureItemType.Prop_Construction_Suit: FurnitureDefinition(
        name = "ttcc_prop_sign_construction_suit",
        modelName = "ttcc_prop_sign_construction_suit",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_5/models/modules/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Construction_Toon: FurnitureDefinition(
        name = "ttcc_prop_sign_construction_toon",
        modelName = "ttcc_prop_sign_construction_toon",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_5/models/modules/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Classic_Table_Coffee: FurnitureDefinition(
        name = "Coffee Table",
        description = "No Description",
        modelName = "classic_table_coffee",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Table_Coffee_Red: FurnitureDefinition(
        name = "Red Coffee Table",
        description = "No Description",
        modelName = "classic_table_coffee",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Fireplace_Square: FurnitureDefinition(
        name = "Square Fireplace",
        description = "No Description",
        modelName = "classic_fireplace_square",
        estateItemType = EstateItemType.PROP_FIREPLACE,
        sequenceNodes = ["**/fireplace_fire_glow_seq", "**/fireplace_fire_seq"],
        # animSpeed=0.5,
    ),
    FurnitureItemType.Prop_Classic_Fireplace_Round: FurnitureDefinition(
        name = "Round Fireplace B",
        description = "No Description",
        modelName = "classic_fireplace_round",
        estateItemType = EstateItemType.PROP_FIREPLACE,
        sequenceNodes = ["**/seqNode_fireGroup", "**/seqNode_fireGlowGroup"],
        # animSpeed=0.5,
    ),
    FurnitureItemType.Prop_Classic_Radio_A_Green: FurnitureDefinition(
        name = "Green Radio",
        description = "No Description",
        modelName = "classic_radioA",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Radio_B_Red: FurnitureDefinition(
        name = "Red Radio",
        description = "No Description",
        modelName = "classic_radioB",
        modelScale=0.75,
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Radio_C_Brown: FurnitureDefinition(
        name = "Brown Radio",
        description = "No Description",
        modelName = "classic_radioC",
        modelScale = 0.75,
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Rug_Large: FurnitureDefinition(
        name = "Large Rug",
        description = "No Description",
        modelName = "classic_rug_square",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.RUG,
    ),
    FurnitureItemType.Prop_Classic_Rug_Small: FurnitureDefinition(
        name = "Small Rug",
        description = "No Description",
        modelName = "classic_rug_circle_B",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.RUG,
        modelScale = 2.5,
    ),
    FurnitureItemType.Prop_Classic_Rug_Round: FurnitureDefinition(
        name = "Round Rug",
        description = "No Description",
        modelName = "classic_rug_circle_A",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.RUG,
        customColorNode='**/pPlane*',
        customColors={
            "Red": (0.792, 0.353, 0.29, 1.0),
            "Green": (0.176, 0.592, 0.439, 1.0),
            "Purple": (0.439, 0.424, 0.682, 1.0),
            "Blue": (0.325, 0.58, 0.835, 1.0),
            "Pink": (0.753, 0.345, 0.557, 1.0),
            "Yellow": (0.992, 0.843, 0.392, 1.0),
        }
    ),
    FurnitureItemType.Prop_Classic_Table_Bedroom: FurnitureDefinition(
        name = "Bedroom Table",
        description = "No Description",
        modelName = "classic_table_square",
        estateItemType = EstateItemType.GENERIC,
        customColorNode = '**/table_grp',
        customColors = {
            "Burly Wood": (0.933, 0.773, 0.569, 1.0),
            "Dark Goldenrod": (0.9333, 0.6785, 0.055, 1.0),
            "Peach Puff": (0.545, 0.451, 0.333, 1.0),
            "Deep Red": (0.541, 0.0, 0.0, 1.0),
            "Chocolate": (0.5451, 0.2706, 0.0745, 1.0),
            "Rosey Brown": (0.5451, 0.4118, 0.4118, 1.0),
        }
    ),
    FurnitureItemType.Prop_Classic_Table_End: FurnitureDefinition(
        name = "End Table",
        description = "No Description",
        modelName = "classic_table_ending",
        modelPath = "props/toon_props/models/",
        modelNamePrefix = "gen_toon_prp_deco_",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_PopcornCart: FurnitureDefinition(
        name = "Popcorn Cart",
        description = "No Description",
        modelName = "classic_popcronCart",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Table_Small: FurnitureDefinition(
        name = "Small Table",
        description = "No Description",
        modelName = "classic_table_radio",
        estateItemType = EstateItemType.GENERIC,
        modelScale = 1.0,
        customColorNode = '**/table_grp',
        customColors = {
            "Burly Wood": (0.933, 0.773, 0.569, 1.0),
            "Dark Goldenrod": (0.9333, 0.6785, 0.055, 1.0),
            "Peach Puff": (0.545, 0.451, 0.333, 1.0),
            "Deep Red": (0.541, 0.0, 0.0, 1.0),
            "Chocolate": (0.5451, 0.2706, 0.0745, 1.0),
            "Rosey Brown": (0.5451, 0.4118, 0.4118, 1.0),
        }
    ),

    # endregion

    ### Candy ###
    # region
    FurnitureItemType.Prop_Candy_Chair_Cupcake: FurnitureDefinition(
        name = "Cupcake Chair",
        description = "No Description",
        modelName = "candy_chair_cupcake",
        estateItemType = EstateItemType.PROP_CHAIR,
        chairCollision = "**/chair_coll",
        chairPositions = ((0, 0.6, 1.9, 0),),
    ),
    FurnitureItemType.Prop_Candy_Bed_Icecream: FurnitureDefinition(
        name = "Ice Cream Bed",
        description = "No Description",
        modelName = "candy_bed",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Candy_SwingSet: FurnitureDefinition(
        name = "Candy Swing Set",
        description = "No Description",
        modelName = "candy_swingset",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Candy_CakeSlide: FurnitureDefinition(
        name = "Cake Slide",
        description = "No Description",
        modelName = "candy_slide_cake",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Candy_BananaSplitTub: FurnitureDefinition(
        name = "Banana Split Tub",
        description = "No Description",
        modelName = "candy_bathtub_bananasplit",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Candy_Fireplace_CaramelApple: FurnitureDefinition(
        name = "Caramel Apple Fireplace",
        description = "No Description",
        modelName = "candy_fireplace",
        estateItemType = EstateItemType.PROP_FIREPLACE,
    ),
    FurnitureItemType.Prop_Candy_Couch_Twinkie: FurnitureDefinition(
        name = "Shortcake Couch",
        description = "No Description",
        modelName = "candy_couch_twinkie",
        estateItemType = EstateItemType.PROP_CHAIR,
        chairCollision = "**/couch_top_coll",
        chairPositions = ((-1.25, -3.5, 2.4, 180), (1.25, -3.5, 2.4, 180)),
    ),
    FurnitureItemType.Prop_Candy_Table_Cookie: FurnitureDefinition(
        name = "Cookie Table",
        description = "No Description",
        modelName = "candy_table_cookie",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Candy_SundaeChest: FurnitureDefinition(
        name = "Sundae Chest",
        description = "No Description",
        modelName = "candy_chest_icecream",
        estateItemType = EstateItemType.GENERIC,
    ),
    # endregion

    ### Underwater ###
    # region
    FurnitureItemType.Prop_UW_Chair_Lobster: FurnitureDefinition(
        name = "Lobster Chair",
        description = "No Description",
        modelName = "uw_chair_lobster",
        estateItemType = EstateItemType.PROP_CHAIR,
        chairCollision = "**/collisions",
        chairPositions = ((0, -2.8, 1.6, 180),),
    ),
    FurnitureItemType.Prop_UW_Chair_Lifejacket: FurnitureDefinition(
        name = "Lifejacket Chair",
        description = "No Description",
        modelName = "uw_chair_lifesaver",
        estateItemType = EstateItemType.PROP_CHAIR,
        chairCollision = "**/chair_body_coll",
        chairPositions = ((0, -3.1, 1.7, 180),),
    ),
    FurnitureItemType.Prop_UW_Bed_Boat: FurnitureDefinition(
        name = "Boat Bed",
        description = "No Description",
        modelName = "uw_bed_boat",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_UW_Lamp_Jellyfish_Blue: FurnitureDefinition(
        name = "Blue Jellyfish Lamp",
        description = "No Description",
        modelName = "uw_lamp_jellyfishA",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_UW_Lamp_Jellyfish_Orange: FurnitureDefinition(
        name = "Orange Jellyfish Lamp",
        description = "No Description",
        modelName = "uw_lamp_jellyfishB",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_UW_CoralVase: FurnitureDefinition(
        name = "Coral Vase",
        description = "No Description",
        modelName = "uw_vase_coral",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_UW_ShellVase: FurnitureDefinition(
        name = "Shell Vase",
        description = "No Description",
        modelName = "uw_vase_shell",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_UW_Fireplace_Coral: FurnitureDefinition(
        name = "Coral Fireplace",
        description = "No Description",
        modelName = "uw_fireplace_coral",
        estateItemType = EstateItemType.PROP_FIREPLACE,
        sequenceNodes = ["**/seqNode_fireGroup", "**/seqNode_fireGlowGroup"],
        # animSpeed=0.5,
    ),
    FurnitureItemType.Wall_UW_Swordfish: FurnitureDefinition(
        name = "Swordfish",
        description = "No Description",
        modelName = "uw_fish_sword",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
    ),
    FurnitureItemType.Wall_UW_Hammerhead: FurnitureDefinition(
        name = "Hammerhead",
        description = "No Description",
        modelName = "uw_fish_hammerhead",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
    ),
    FurnitureItemType.Prop_UW_Statue_Fountain: FurnitureDefinition(
        name = "Fountain",
        description = "No Description",
        modelName = "uw_fountain",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_UW_WashingMachine: FurnitureDefinition(
        name = "Washing Machine",
        description = "No Description",
        modelName = "uw_dryer",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_UW_Table_Snorkel: FurnitureDefinition(
        name = "Snorkeler's Table",
        description = "No Description",
        modelName = "uw_table",
        estateItemType = EstateItemType.GENERIC,
    ),

    FurnitureItemType.Prop_UW_Coatrack_Coral: FurnitureDefinition(
        name = "Coral Coat Rack",
        description = "No Description",
        modelName = "uw_rack_clothes",
        estateItemType = EstateItemType.GENERIC,
    ),

    # endregion

    ### Western ###
    # region
    FurnitureItemType.Prop_Western_SaddleStool: FurnitureDefinition(
        name = "Saddle Stool",
        description = "No Description",
        modelName = "west_stool_saddle",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Western_Chair_Woven: FurnitureDefinition(
        name = "Woven Chair",
        description = "No Description",
        modelName = "west_chair_patched",
        estateItemType = EstateItemType.PROP_CHAIR,
        chairCollision = "**/chair_body_coll",
        chairPositions = ((-1.9, -1.15, 2.2, 90),),
    ),
    FurnitureItemType.Prop_Western_Bed_CactusHammock: FurnitureDefinition(
        name = "Cactus Hammock",
        description = "No Description",
        modelName = "west_bed_hammock",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Western_Couch_Hay: FurnitureDefinition(
        name = "Hay Couch",
        description = "No Description",
        modelName = "west_couch_hay",
        estateItemType = EstateItemType.PROP_CHAIR,
        chairCollision = "**/couch_body_coll",
        chairPositions = ((-2.1, -3.9, 1.6, 180), (-0.1, -3.9, 1.6, 180), (2.1, -3.9, 1.6, 180)),
    ),
    FurnitureItemType.Prop_Western_Lamp_Cowboy: FurnitureDefinition(
        name = "Cowboy Lamp",
        description = "No Description",
        modelName = "west_lamp_cowboy",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Wall_Western_HangingHorns: FurnitureDefinition(
        name = "Hanging Horns",
        description = "No Description",
        modelName = "west_horns",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
    ),
    FurnitureItemType.Wall_Western_Sombrero_Simple: FurnitureDefinition(
        name = "Simple Sombrero",
        description = "No Description",
        modelName = "west_sombrero_simple",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
    ),
    FurnitureItemType.Wall_Western_Sombrero_Fancy: FurnitureDefinition(
        name = "Fancy Sombrero",
        description = "No Description",
        modelName = "west_sombrero_fancy",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
    ),
    FurnitureItemType.Wall_Western_Poster_Stars: FurnitureDefinition(
        name = "Reach for the Stars Poster",
        description = "No Description",
        modelName = "west_poster_stars",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
    ),
    FurnitureItemType.Wall_Western_Horseshoe: FurnitureDefinition(
        name = "Horseshoe",
        description = "No Description",
        modelName = "west_horseshoe",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
    ),
    FurnitureItemType.Wall_Western_Portrait_Bison: FurnitureDefinition(
        name = "Bison Portrait",
        description = "No Description",
        modelName = "west_painting_bison",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
    ),
    FurnitureItemType.Prop_Western_BarrelStand: FurnitureDefinition(
        name = "Barrel Stand",
        description = "No Description",
        modelName = "west_barrel",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Western_Plant_Cactus: FurnitureDefinition(
        name = "Cactus Plant",
        description = "No Description",
        modelName = "west_cactus_fat",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Western_Tent_Explorer: FurnitureDefinition(
        name = "Tent",
        description = "No Description",
        modelName = "west_tent",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Western_FishBowl_Skull: FurnitureDefinition(
        name = "Skull Fishbowl",
        description = "No Description",
        modelName = "west_bowl_skull",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Western_FishBowl_Lizard: FurnitureDefinition(
        name = "Lizard Fishbowl",
        description = "No Description",
        modelName = "west_bowl_lizard",
        estateItemType = EstateItemType.GENERIC,
    ),


    # endregion

    ### Bug ###
    # region
    FurnitureItemType.Prop_Bug_Chair_Log: FurnitureDefinition(
        name = "Log Chair",
        description = "No Description",
        modelName = "bug_chair_wood",
        estateItemType = EstateItemType.PROP_CHAIR,
        chairCollision = "**/chair_body_coll",
        chairPositions = ((0, -4.1, 1.7, 180),),
    ),
    FurnitureItemType.Prop_Bug_Bed_Leaf: FurnitureDefinition(
        name = "Leaf Bed",
        description = "No Description",
        modelName = "bug_bed_leaf",
        estateItemType = EstateItemType.GENERIC,
        modelScaleRange = (0.01, 200),
    ),
    FurnitureItemType.Prop_Bug_Fireplace: FurnitureDefinition(
        name = "Bug Fireplace",
        description = "No Description",
        modelName = "bug_fireplace_tree",
        estateItemType = EstateItemType.PROP_FIREPLACE,
        sequenceNodes = ["**/group1"],
        # animSpeed=0.5,
    ),
    FurnitureItemType.Prop_Bug_Lamp_Sunflower: FurnitureDefinition(
        name = "Sunflower Lamp",
        description = "No Description",
        modelName = "bug_lamp_daisy_1",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Bug_Lamp_Lilac: FurnitureDefinition(
        name = "Lilac Lamp",
        description = "No Description",
        modelName = "bug_lamp_daisy_2",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Bug_TV: FurnitureDefinition(
        name = "Television",
        description = "No Description",
        modelName = "bug_tv",
        estateItemType = EstateItemType.PROP_TV,
    ),
    FurnitureItemType.Prop_Bug_Mushroom_Red: FurnitureDefinition(
        name = "Red Mushroom",
        description = "No Description",
        modelName = "bug_pot_mushroom",
        nodeTextures = {'**/mushroom_plant_geom': "bug_pot_mushroom_body_red"},
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Bug_Mushroom_Yellow: FurnitureDefinition(
        name = "Yellow Mushroom",
        description = "No Description",
        modelName = "bug_pot_mushroom",
        nodeTextures = {'**/mushroom_plant_geom': "bug_pot_mushroom_body_yellow"},
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Bug_Rug_LeafMat: FurnitureDefinition(
        name = "Leaf Mat",
        description = "No Description",
        modelName = "bug_mat_leaf",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.RUG,
    ),
    FurnitureItemType.Prop_Bug_Desk_Log: FurnitureDefinition(
        name = "Log Desk",
        description = "No Description",
        modelName = "bug_desk_wood",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Bug_Ladybug: FurnitureDefinition(
        name = "Ladybug",
        description = "No Description",
        modelName = "bug_beanbag_ladybug",
        estateItemType = EstateItemType.GENERIC,
    ),
    # endregion

    ### Princess/Medieval ###
    # region
    FurnitureItemType.Prop_Fantasy_Bed: FurnitureDefinition(
        name = "Princess Bed",
        description = "No Description",
        modelName = "princess_bed",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fantasy_Fireplace: FurnitureDefinition(
        name = "Princess Fireplace",
        description = "No Description",
        modelName = "princess_fireplace",
        estateItemType = EstateItemType.PROP_FIREPLACE,
        sequenceNodes = ["**/seqNode_fireGroup", "**/seqNode_fireGlowGroup"]
        # animSpeed=0.5,
    ),
    # endregion

    ### Idk ###
    # region
    FurnitureItemType.Wall_Painting_CezanneToon: FurnitureDefinition(
        name = "Cezanne Toon",
        description = "No Description",
        modelName = "gen_painting_square",
        textureName = "horse_cezanne_1",
        textureNamePrefix = "prp_toon_painting_",
        texturePath = "props/toon_props/maps/",
        estateItemType = EstateItemType.GENERIC_PLANE,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
        modelScale = 5.0,
    ),
    FurnitureItemType.Wall_Painting_Densunes: FurnitureDefinition(
        name = "Densunes' Painting",
        description = "No Description",
        modelName = "gen_painting_square",
        estateItemType = EstateItemType.GENERIC_PLANE,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
        modelScale = 2.0,
    ),
    FurnitureItemType.Wall_Painting_Koza: FurnitureDefinition(
        name = "Koza's Painting",
        description = "No Description",
        modelName = "gen_painting_square",
        estateItemType = EstateItemType.GENERIC_PLANE,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
        modelScale = 2.0,
    ),
    FurnitureItemType.Wall_Painting_RembrantToon: FurnitureDefinition(
        name = "Rembrant Toon",
        description = "No Description",
        modelName = "duck_rembrandt",
        modelPath = "props/toon_props/models/",
        modelNamePrefix = "gen_toon_prp_painting_",
        estateItemType = EstateItemType.GENERIC_PLANE,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
        modelScale = 2.0,
    ),
    FurnitureItemType.Wall_Painting_Toonscape: FurnitureDefinition(
        name = "Toonscape",
        description = "No Description",
        modelName = "gen_painting_square",
        textureName = "landscape_1",
        textureNamePrefix = "prp_toon_painting_",
        texturePath = "props/toon_props/maps/",
        estateItemType = EstateItemType.GENERIC_PLANE,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
        modelScale = 5.0,
    ),
    FurnitureItemType.Wall_Painting_Mechanicalhandz: FurnitureDefinition(
        name = "Mechanicalhandz's Painting",
        description = "No Description",
        modelName = "gen_painting_square",
        estateItemType = EstateItemType.GENERIC_PLANE,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
        modelScale = 2.0,
    ),
    FurnitureItemType.Wall_Painting_Mollyversus: FurnitureDefinition(
        name = "Mollyversus' Painting",
        description = "No Description",
        modelName = "gen_painting_square",
        estateItemType = EstateItemType.GENERIC_PLANE,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
        modelScale = 2.5,
    ),
    FurnitureItemType.Wall_Painting_NotaPie: FurnitureDefinition(
        name = "Not a Pie",
        description = "No Description",
        modelName = "magpie",
        modelPath = "props/toon_props/models/",
        modelNamePrefix = "gen_toon_prp_painting_",
        estateItemType = EstateItemType.GENERIC_PLANE,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
        modelScale = 2.0,
    ),
    FurnitureItemType.Wall_Painting_Jacky: FurnitureDefinition(
        name = "Jacky's Painting",
        description = "No Description",
        modelName = "gen_painting_square",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
        modelScale = 2.0,
    ),
    FurnitureItemType.Prop_Classic_Vase_Short_A: FurnitureDefinition(
        name = "Short Vase",
        description = "No Description",
        modelName = "classic_vaseA_short",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Vase_Tall_A: FurnitureDefinition(
        name = "Tall Vase",
        description = "No Description",
        modelName = "classic_vaseA_tall",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Vase_Short_B: FurnitureDefinition(
        name = "Short Vase",
        description = "No Description",
        modelName = "classic_vaseB_short",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Vase_Tall_B: FurnitureDefinition(
        name = "Tall Vase",
        description = "No Description",
        modelName = "classic_vaseB_tall",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Vase_Short_C: FurnitureDefinition(
        name = "Short Vase",
        description = "No Description",
        modelName = "classic_vaseC_short",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Classic_Vase_Short_D: FurnitureDefinition(
        name = "Short Vase",
        description = "No Description",
        modelName = "classic_vaseD_short",
        estateItemType = EstateItemType.GENERIC,
    ),

    FurnitureItemType.Prop_Val_Vase_Rose: FurnitureDefinition(
        name = "Rose Vase",
        description = "No Description",
        modelName = "val_vase_rose",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Val_Watercan_Rose: FurnitureDefinition(
        name = "Rose Watercan",
        description = "No Description",
        modelName = "val_watercan",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Wall_Val_Painting_RoseSRRedd: FurnitureDefinition(
        name = "Rose S.R. Redd",
        description = "No Description",
        modelName = "val_painting_1",
        estateItemType = EstateItemType.GENERIC_PLANE,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
    ),


    # endregion

    ### Toontown Central Props ###
    # region
    ## Schoolhouse Props
    # region
    FurnitureItemType.Prop_Schoolhouse_Training_Bench: FurnitureDefinition(
        name = "Training Room Bench",
        description = "No Description",
        modelName = "bench",
        modelNamePrefix = "ara_sch_int_trn_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),

    FurnitureItemType.Prop_Schoolhouse_Classroom_Canvas: FurnitureDefinition(
        name = "Colorful Canvas",
        description = "No Description",
        modelName = "canvas",
        modelNamePrefix = "ara_sch_int_cls_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Schoolhouse_Classroom_Desk_Student: FurnitureDefinition(
        name = "Student Desk Bench",
        description = "No Description",
        modelName = "desk_student",
        modelNamePrefix = "ara_sch_int_cls_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Schoolhouse_Classroom_Shelf_1: FurnitureDefinition(
        name = "Empty Shelf",
        description = "No Description",
        modelName = "shelf",
        modelNamePrefix = "ara_sch_int_cls_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Schoolhouse_Classroom_Shelf_2: FurnitureDefinition(
        name = "Busy Shelf",
        description = "No Description",
        modelName = "shelf",
        modelNamePrefix = "ara_sch_int_cls_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Schoolhouse_Classroom_PencilCase_1: FurnitureDefinition(
        name = "Wacky Pencil Case",
        description = "No Description",
        modelName = "pencilCase",
        modelNamePrefix = "ara_sch_int_cls_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Wall_Schoolhouse_Classroom_Clock: FurnitureDefinition(
        name = "Classroom Clock",
        description = "No Description",
        modelName = "clock",
        modelNamePrefix = "ara_sch_int_cls_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
    ),
    FurnitureItemType.Prop_Schoolhouse_Classroom_Bench_1: FurnitureDefinition(
        name = "Diligent Desk",
        description = "No Description",
        modelName = "bench_reception",
        modelNamePrefix = "ara_sch_int_cls_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Schoolhouse_Classroom_Binder_1: FurnitureDefinition(
        name = "Silly Binder",
        description = "No Description",
        modelName = "binder",
        modelNamePrefix = "ara_sch_int_cls_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Schoolhouse_Classroom_Rug: FurnitureDefinition(
        name = "Blue Square Rug",
        description = "No Description",
        modelName = "rug_square",
        modelNamePrefix = "ara_sch_int_cls_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Schoolhouse_Training_Watercooler: FurnitureDefinition(
        name = "Training Watercooler",
        description = "No Description",
        modelName = "watercooler_1",
        modelNamePrefix = "ara_sch_int_trn_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Schoolhouse_Training_GagBarrel: FurnitureDefinition(
        name = "Gag Barrel",
        description = "No Description",
        modelName = "gagBarrel_1",
        modelNamePrefix = "ara_sch_int_trn_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
        throwables = 1
    ),
    FurnitureItemType.Prop_Schoolhouse_Training_Weights: FurnitureDefinition(
        name = "Big Weights",
        description = "No Description",
        modelName = "weights",
        modelNamePrefix = "ara_sch_int_trn_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Schoolhouse_Basement_Chair_1: FurnitureDefinition(
        name = "Dusty Student Desk",
        description = "No Description",
        modelName = "chair_student_1",
        modelNamePrefix = "ara_sch_int_bse_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_ToonHall_Chair_Space: FurnitureDefinition(
        name = "Flippy's Starry Chair",
        description = "No Description",
        modelName = "chair_space_1",
        modelNamePrefix = "ara_toonhall_int_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_ToonHall_Desk_Lamp_Space: FurnitureDefinition(
        name = "Flippy's Starry Desk Lamp",
        description = "No Description",
        modelName = "lamp_desk_space_1",
        modelNamePrefix = "ara_toonhall_int_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_ToonHall_Sofa_Space: FurnitureDefinition(
        name = "Flippy's Spacious Sofa",
        description = "No Description",
        modelName = "sofa_space_1",
        modelNamePrefix = "ara_toonhall_int_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_ToonHall_Lamp_Space: FurnitureDefinition(
        name = "Flippy's Spacious Lamp",
        description = "No Description",
        modelName = "lamp_space_1",
        modelNamePrefix = "ara_toonhall_int_prp_",
        modelPath = "areas/toontown_central/models/",
        estateItemType = EstateItemType.GENERIC,
    ),

    # endregion
    FurnitureItemType.Prop_TTC_BigPlanter: FurnitureDefinition(
        name = "Big Flower Planter",
        description = "No Description",
        modelName = "planter_big",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_ttc_prp_",
        modelPath = "areas/toontown_central/models/",
    ),
    FurnitureItemType.Prop_TTC_StopSign: FurnitureDefinition(
        name = "Stop Sign",
        description = "eight AWESOME angles!!",
        modelName = "ttc_stopsign_1a",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_TTC_CautionSign: FurnitureDefinition(
        name = "Caution Barrier",
        description = "No Description",
        modelName = "barrier_1",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "prp_toon_",
        modelPath = "props/toon_props/models/",
    ),
    FurnitureItemType.Prop_TTC_Gazebo: FurnitureDefinition(
        name = "Gazebo",
        description = "No Description",
        modelName = "gazebo",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_ttc_prp_",
        modelPath = "areas/toontown_central/models/",
    ),
    FurnitureItemType.Prop_TTC_Statue_Fountain: FurnitureDefinition(
        name = "toontown_central_fountain",
        description = "No toontown_central_fountain",
        modelName = "statue_fountain",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_ttc_prp_",
        modelPath = "areas/toontown_central/models/",
    ),
    FurnitureItemType.Prop_TTC_Statue_Horse: FurnitureDefinition(
        name = "Horse Statue",
        description = "Statue",
        modelName = "statue_horse",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_ttc_prp_",
        modelPath = "areas/toontown_central/models/",
    ),
    FurnitureItemType.Prop_TTC_Lamp_1: FurnitureDefinition(
        name = "tt_m_ara_TT_streetlight_three_light",
        modelName = "lamp_triple",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_ttc_prp_",
        modelPath = "areas/toontown_central/models/",
    ),
    FurnitureItemType.Prop_TTC_Lamp_2: FurnitureDefinition(
        name = "tt_m_ara_TT_streetlight_one_light",
        modelName = "lamp_square",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_ttc_prp_",
        modelPath = "areas/toontown_central/models/",
    ),
    FurnitureItemType.Prop_TTC_Lamp_3: FurnitureDefinition(
        name = "tt_m_ara_TT_streetlight_sign",
        modelName = "lamp_sign",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_ttc_prp_",
        modelPath = "areas/toontown_central/models/",
    ),
    FurnitureItemType.Prop_TTC_Mailbox: FurnitureDefinition(
        name = "mailbox_TT",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "mailbox_1",
        modelNamePrefix = "ara_ttc_prp_",
        modelPath = "areas/toontown_central/models/",
        collisionNode="prop_mailboxcollisions",
        throwables=6
    ),
    FurnitureItemType.Prop_TTC_Mailbox_Anim: FurnitureDefinition(
        name = "tt_r_ara_ttc_mailbox",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "mailbox_1",
        modelNamePrefix = "ara_ttc_prp_",
        modelPath = "areas/toontown_central/models/",
        wantActor=True,
        actorAnimations = {
            "fightBoost": "mailbox_1-fightBoost",
            "fightCheer": "mailbox_1-fightCheer",
            "fightIdle": "mailbox_1-fightIdle",
            "fightIntoIdle": "mailbox_1-fightIntoIdle",
            "fightSad": "mailbox_1-fightSad",
            "idle0": "mailbox_1-idle0",
            "idle0settle": "mailbox_1-idle0settle",
            "idleAwesome3": "mailbox_1-idleAwesome3",
            "idleIntoFight": "mailbox_1-idleIntoFight",
            "idleLook1": "mailbox_1-idleLook1",
            "idleTake2": "mailbox_1-idleTake2",
            "victoryDance": "mailbox_1-victoryDance",
        },
    ),
    FurnitureItemType.Prop_TTC_Mailbox_Hydrant_Anim: FurnitureDefinition(
        name = "tt_r_ara_ttc_hydrant",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "hydrant_1",
        modelNamePrefix = "ara_ttc_prp_",
        modelPath = "areas/toontown_central/models/",
        wantActor = True,
        actorAnimations = {
            "fightBoost": "hydrant_1-fightBoost",
            "fightCheer": "hydrant_1-fightCheer",
            "fightIdle": "hydrant_1-fightIdle",
            "fightIntoIdle": "hydrant_1-fightIntoIdle",
            "fightSad": "hydrant_1-fightSad",
            "firstMoveArmUp1": "hydrant_1-firstMoveArmUp1",
            "firstMoveArmUp2": "hydrant_1-firstMoveArmUp2",
            "firstMoveArmUp3": "hydrant_1-firstMoveArmUp3",
            "firstMoveIntoSleep": "hydrant_1-firstMoveIntoSleep",
            "firstMoveJump": "hydrant_1-firstMoveJump",
            "firstMoveJumpBalance": "hydrant_1-firstMoveJumpBalance",
            "firstMoveJumpSpin": "hydrant_1-firstMoveJumpSpin",
            "firstMoveOutOfSleep": "hydrant_1-firstMoveOutOfSleep",
            "firstMoveSleepIdle": "hydrant_1-firstMoveSleepIdle",
            "firstMoveStruggle": "hydrant_1-firstMoveStruggle",
        },
    ),
    FurnitureItemType.Prop_TTC_Mailbox_Trashcan_Anim: FurnitureDefinition(
        name = "tt_r_ara_ttc_trashcan",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "trashcan_1",
        modelNamePrefix = "ara_ttc_prp_",
        modelPath = "areas/toontown_central/models/",
        wantActor = True,
        actorAnimations = {
            "fightBoost": "trashcan_1-fightBoost",
            "fightCheer": "trashcan_1-fightCheer",
            "fightIdle": "trashcan_1-fightIdle",
            "fightIntoIdle": "trashcan_1-fightIntoIdle",
            "fightSad": "trashcan_1-fightSad",
            "fightAwesome3": "trashcan_1-fightAwesome3",
            "idleHiccup0": "trashcan_1-idleHiccup0",
            "idleIntoFight": "trashcan_1-idleIntoFight",
            "idleLook1": "trashcan_1-idleLook1",
            "idleTake2": "trashcan_1-idleTake2",
            "open": "trashcan_1-open",
            "reveal": "trashcan_1-reveal",
            "victoryDance": "trashcan_1-victoryDance",
        },
    ),
    # endregion

    ### Boatyard Props ###
    # region
    FurnitureItemType.Prop_BB_PalmTreeFlat: FurnitureDefinition(
        name = "Flat Palm Tree",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "palmtree_1_flat_top",
        modelNamePrefix = "ara_bb_prp_",
        modelPath = "areas/barnacle_boatyard/models/",
    ),
    FurnitureItemType.Prop_BB_Streetlight: FurnitureDefinition(
        name = "Boatyard Streetlight",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "lamp_1",
        modelNamePrefix = "ara_bb_prp_",
        modelPath = "areas/barnacle_boatyard/models/",
    ),
    FurnitureItemType.Prop_BB_Trashcan: FurnitureDefinition(
        name = "Boatyard trashcan_DD",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "trashcan_1",
        modelNamePrefix = "ara_bb_prp_",
        modelPath = "areas/barnacle_boatyard/models/",
    ),
    FurnitureItemType.Prop_BB_Trashcan_Anim: FurnitureDefinition(
        name = "Boatyard Animated Trashcan",
        description = "No Description",
        modelName = "trashcan_1",
        modelNamePrefix = "ara_bb_prp_",
        modelPath = "areas/barnacle_boatyard/models/",
        wantActor = True,
        actorAnimations = {
            "fightBoost": "trashcan_1-fightBoost",
            "fightCheer": "trashcan_1-fightCheer",
            "fightIdle": "trashcan_1-fightIdle",
            "fightIntoIdle": "trashcan_1-fightIntoIdle",
            "fightSad": "trashcan_1-fightSad",
            "idle0": "trashcan_1-idle0",
            "idle0settle": "trashcan_1-idle0settle",
            "idle1": "trashcan_1-idle1",
            "idleAwesome3": "trashcan_1-idleAwesome3",
            "idleBounce2": "trashcan_1-idleHiccup0",
            "idleIntoFight": "trashcan_1-idleIntoFight",
            "victoryDance": "trashcan_1-victoryDance",
        },
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_BB_Mailbox: FurnitureDefinition(
        name = "Boatyard mailbox_DD",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "mailbox_1",
        modelNamePrefix = "ara_bb_prp_",
        modelPath = "areas/barnacle_boatyard/models/",
    ),
    FurnitureItemType.Prop_BB_Mailbox_Anim: FurnitureDefinition(
        name = "tt_r_ara_dod_mailbox",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "mailbox_1",
        modelNamePrefix = "ara_bb_prp_",
        modelPath = "areas/barnacle_boatyard/models/",
        wantActor = True,
        actorAnimations = {
            "fightBoost": "mailbox_1-fightBoost",
            "fightCheer": "mailbox_1-fightCheer",
            "fightIdle": "mailbox_1-fightIdle",
            "fightIntoIdle": "mailbox_1-fightIntoIdle",
            "fightSad": "mailbox_1-fightSad",
            "firstMoveFlagSpin1": "mailbox_1-firstMoveFlagSpin1",
            "firstMoveFlagSpin2": "mailbox_1-firstMoveFlagSpin2",
            "firstMoveFlagSpin3": "mailbox_1-firstMoveFlagSpin3",
            "firstMoveIntoSleep": "mailbox_1-firstMoveIntoSleep",
            "firstMoveJump": "mailbox_1-firstMoveJump",
            "firstMoveJump3Summersaults": "mailbox_1-firstMoveJump3Summersaults",
            "firstMoveJumpFall": "mailbox_1-firstMoveJumpFall",
            "firstMoveJumpSummersault": "mailbox_1-firstMoveJumpSummersault",
            "firstMoveOutOfSleep": "mailbox_1-firstMoveOutOfSleep",
            "firstMoveSleepIdle": "mailbox_1-firstMoveSleepIdle",
            "firstMoveStruggle": "mailbox_1-firstMoveStruggle",
            "idle0": "mailbox_1-idle0",
            "idle0settle": "mailbox_1-idle0settle",
            "idle1": "mailbox_1-idle1",
            "idle2": "mailbox_1-idle2",
            "idleAwesome3": "mailbox_1-idleAwesome3",
            "idleIntoFight": "mailbox_1-idleIntoFight",
            "victoryDance": "mailbox_1-victoryDance",
        },
    ),
    FurnitureItemType.Prop_BB_PalmTree_1_Full: FurnitureDefinition(
        name = "Awesome Palm Tree",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "palmtree_1_full",
        modelNamePrefix = "ara_bb_prp_",
        modelPath = "areas/barnacle_boatyard/models/",
    ),
    # endregion

    ### YOTT Props ###
    # region
    FurnitureItemType.Prop_YOTT_Barrel_Ext: FurnitureDefinition(
        name = "barrel_yott",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "barrel_upright",
        modelNamePrefix = "ara_yott_ext_prp_",
        modelPath = "areas/ye_olde_toontowne/models/",
    ),
    FurnitureItemType.Prop_YOTT_Barrel_Plant: FurnitureDefinition(
        name = "barrel-plant_yott",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "barrel_plant",
        modelNamePrefix = "ara_yott_ext_prp_",
        modelPath = "areas/ye_olde_toontowne/models/",
    ),
    FurnitureItemType.Prop_YOTT_Cart_Ext: FurnitureDefinition(
        name = "cart_yott",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "cart",
        modelNamePrefix = "ara_yott_ext_prp_",
        modelPath = "areas/ye_olde_toontowne/models/",
    ),
    FurnitureItemType.Prop_YOTT_Logstack_Ext: FurnitureDefinition(
        name = "logstack_yott",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "logstack",
        modelNamePrefix = "ara_yott_ext_prp_",
        modelPath = "areas/ye_olde_toontowne/models/",
    ),
    FurnitureItemType.Prop_YOTT_Well: FurnitureDefinition(
        name = "well_yott",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "well_1",
        modelNamePrefix = "ara_yott_ext_prp_",
        modelPath = "areas/ye_olde_toontowne/models/",
    ),
    FurnitureItemType.Prop_YOTT_Trashcan: FurnitureDefinition(
        name = "trashcan_OT",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "trashcan_1",
        modelNamePrefix = "ara_yott_ext_prp_",
        modelPath = "areas/ye_olde_toontowne/models/",
    ),
    FurnitureItemType.Prop_YOTT_Hydrant: FurnitureDefinition(
        name = "hydrant_OT",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "hydrant_1",
        modelNamePrefix = "ara_yott_ext_prp_",
        modelPath = "areas/ye_olde_toontowne/models/",
    ),
    FurnitureItemType.Prop_YOTT_Mailbox: FurnitureDefinition(
        name = "mailbox_OT",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "mailbox_1",
        modelNamePrefix = "ara_yott_ext_prp_",
        modelPath = "areas/ye_olde_toontowne/models/",
    ),
    FurnitureItemType.Prop_YOTT_Lamp_1: FurnitureDefinition(
        name = "lampD1_yott",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "lamp_1",
        modelNamePrefix = "ara_yott_ext_prp_",
        modelPath = "areas/ye_olde_toontowne/models/",
    ),
    FurnitureItemType.Prop_YOTT_Lamp_2: FurnitureDefinition(
        name = "lampD2_yott",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "lamp_2",
        modelNamePrefix = "ara_yott_ext_prp_",
        modelPath = "areas/ye_olde_toontowne/models/",
    ),
    FurnitureItemType.Prop_YOTT_Lamp_3: FurnitureDefinition(
        name = "lampD3_yott",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "lamp_3",
        modelNamePrefix = "ara_yott_ext_prp_",
        modelPath = "areas/ye_olde_toontowne/models/",
    ),

    # endregion

    ### DG Props ###
    # region
    FurnitureItemType.Prop_DG_DaisyTable: FurnitureDefinition(
        name = "Daisy Table",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "table_1",
        modelNamePrefix = "ara_dg_prp_",
        modelPath = "areas/daffodil_gardens/models/",
    ),
    FurnitureItemType.Prop_DG_Flowerbed_Pink: FurnitureDefinition(
        name = "Prop_DG_Flowerbed_Pink",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "flowerbox_red",
        modelNamePrefix = "gen_prp",
        modelPath = "props/general/models/",
    ),
    FurnitureItemType.Prop_DG_Flowerbed_Yellow: FurnitureDefinition(
        name = "Prop_DG_Flowerbed_Yellow",
        estateItemType = EstateItemType.GENERIC,
        modelName = "flowerbox_yellow",
        modelNamePrefix = "gen_prp",
        modelPath = "props/general/models/",
    ),
    FurnitureItemType.Prop_DG_Flowerbed_Round: FurnitureDefinition(
        name = "Prop_DG_Flowerbed_Round",
        estateItemType = EstateItemType.GENERIC,
        modelName = "flowerBed_1_round",
        modelNamePrefix = "gen_prp",
        modelPath = "props/general/models/",
    ),
    FurnitureItemType.Prop_DG_Gazebo: FurnitureDefinition(
        name = "Prop_DG_Gazebo",
        estateItemType = EstateItemType.GENERIC,
        modelName = "gazebo",
        modelNamePrefix = "ara_dg_prp_",
        modelPath = "areas/daffodil_gardens/models/",
    ),
    FurnitureItemType.Prop_DG_Fountain: FurnitureDefinition(
        name = "Prop_DG_Fountain",
        estateItemType = EstateItemType.GENERIC,
        modelName = "fountain_1",
        modelNamePrefix = "ara_dg_prp_",
        modelPath = "areas/daffodil_gardens/models/",
    ),
    FurnitureItemType.Prop_DG_Hydrant_Anim: FurnitureDefinition(
        name = "Prop_DG_Hydrant_Anim",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "hydrant_1",
        modelNamePrefix = "ara_dg_prp_",
        modelPath = "areas/daffodil_gardens/models/",
        wantActor = True,
        actorAnimations = {
            "fightBoost": "hydrant_1-fightBoost",
            "fightCheer": "hydrant_1-fightCheer",
            "fightIdle": "hydrant_1-fightIdle",
            "fightIntoIdle": "hydrant_1-fightIntoIdle",
            "fightSad": "hydrant_1-fightSad",
            "idle0": "hydrant_1-idle0",
            "idle0settle": "hydrant_1-idle0settle",
            "idleAwesome3": "hydrant_1-idleAwesome3",
            "idleIntoFight": "hydrant_1-idleIntoFight",
            "idleLook1": "hydrant_1-idleLook1",
            "idleSneeze2": "hydrant_1-idleSneeze2",
            "victoryDance": "hydrant_1-victoryDance",
        },
    ),
    FurnitureItemType.Prop_DG_Mailbox_Anim: FurnitureDefinition(
        name = "Prop_DG_Mailbox_Anim",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "mailbox_1",
        modelNamePrefix = "ara_dg_prp_",
        modelPath = "areas/daffodil_gardens/models/",
        wantActor = True,
        actorAnimations = {
            "fightBoost": "mailbox_1-fightBoost",
            "fightCheer": "mailbox_1-fightCheer",
            "fightIdle": "mailbox_1-fightIdle",
            "fightIntoIdle": "mailbox_1-fightIntoIdle",
            "fightSad": "mailbox_1-fightSad",
            "idle0": "mailbox_1-idle0",
            "idle0settle": "mailbox_1-idle0settle",
            "idleAwesome3": "mailbox_1-idleAwesome3",
            "idleIntoFight": "mailbox_1-idleIntoFight",
            "idleLook2": "mailbox_1-idleLook2",
            "idleTake1": "mailbox_1-idleTake1",
            "victoryDance": "mailbox_1-victoryDance",
        },
    ),
    FurnitureItemType.Prop_DG_Trashcan_Anim: FurnitureDefinition(
        name = "Prop_DG_Trashcan_Anim",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "trashcan_1",
        modelNamePrefix = "ara_dg_prp_",
        modelPath = "areas/daffodil_gardens/models/",
        wantActor = True,
        actorAnimations = {
            "fightBoost": "trashcan_1-fightBoost",
            "fightCheer": "trashcan_1-fightCheer",
            "fightIdle": "trashcan_1-fightIdle",
            "fightIntoIdle": "trashcan_1-fightIntoIdle",
            "fightSad": "trashcan_1-fightSad",
            "firstMoveIntoSleep": "trashcan_1-firstMoveIntoSleep",
            "firstMoveJump": "trashcan_1-firstMoveJump",
            "firstMoveJumpHit": "trashcan_1-firstMoveJumpHit",
            "firstMoveJumpJuggle": "trashcan_1-firstMoveJumpJuggle",
            "firstMoveLidFlip1": "trashcan_1-firstMoveLidFlip1",
            "firstMoveLidFlip2": "trashcan_1-firstMoveLidFlip2",
            "firstMoveLidFlip3": "trashcan_1-firstMoveLidFlip3",
            "firstMoveOutOfSleep": "trashcan_1-firstMoveOutOfSleep",
            "firstMoveSleepIdle": "trashcan_1-firstMoveSleepIdle",
            "firstMoveStruggle": "trashcan_1-firstMoveStruggle",
            "idleAwesome3": "trashcan_1-idleAwesome3",
            "idleHiccup0": "trashcan_1-idleHiccup0",
            "idleIntoFight": "trashcan_1-idleIntoFight",
            "idleLook1": "trashcan_1-idleLook1",
            "idleTake2": "trashcan_1-idleTake2",
            "victoryDance": "trashcan_1-victoryDance",
        },
    ),
    # endregion

    ### MML Props ###
    # region
    FurnitureItemType.Prop_Trampoline_MML: FurnitureDefinition(
        name = 'Melodyland Trampoline',
        description = 'Bouncy!',
        modelName = "drum_trampoline",
        modelNamePrefix = "ara_mml_prp_",
        modelPath = "areas/mezzo_melodyland/models/",
        modelScale = 0.7,
        estateItemType = EstateItemType.PROP_INTERACTIVE_TRAMPOLINE,
        estateItemPlacementFlag = EstateItemPlacementFlags.STANDARD,
    ),
    FurnitureItemType.Prop_MML_CrashedPiano: FurnitureDefinition(
        name = 'Crashed Piano',
        description = 'Bouncy!',
        modelName = 'piano_1',
        modelNamePrefix = "ara_mml_prp_",
        modelPath = "areas/mezzo_melodyland/models/",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.STANDARD,
    ),
    FurnitureItemType.Prop_MML_Drum: FurnitureDefinition(
        name = 'MML Drum',
        description = 'Bouncy!',
        modelName = "drum",
        modelNamePrefix = "ara_mml_prp_",
        modelPath = "areas/mezzo_melodyland/models/",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.STANDARD,
    ),
    FurnitureItemType.Prop_MML_Planter: FurnitureDefinition(
        name = "MML Planter",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "planter_1",
        modelNamePrefix = "ara_mml_prp_",
        modelPath = "areas/mezzo_melodyland/models/",
    ),
    FurnitureItemType.Prop_MML_Hydrant_Anim: FurnitureDefinition(
        name = "MML Hydrant",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "hydrant_1",
        modelNamePrefix = "ara_mml_prp_",
        modelPath = "areas/mezzo_melodyland/models/",
        wantActor = True,
        actorAnimations = {
            "fightBoost": "hydrant_1-fightBoost",
            "fightCheer": "hydrant_1-fightCheer",
            "fightIdle": "hydrant_1-fightIdle",
            "fightIntoIdle": "hydrant_1-fightIntoIdle",
            "fightSad": "hydrant_1-fightSad",
            "idle0": "hydrant_1-idle0",
            "idle0settle": "hydrant_1-idle0settle",
            "idle1": "hydrant_1-idle1",
            "idle1settle": "hydrant_1-idle1settle",
            "idle2": "hydrant_1-idle2",
            "idle2settle": "hydrant_1-idle2settle",
            "idleAwesome3": "hydrant_1-idleAwesome3",
            "idleIntoFight": "hydrant_1-idleIntoFight",
            "victoryDance": "hydrant_1-victoryDance",

        },
    ),
    FurnitureItemType.Prop_MML_Mailbox: FurnitureDefinition(
        name = "MML Mailbox",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "mailbox_1",
        modelNamePrefix = "ara_mml_prp_",
        modelPath = "areas/mezzo_melodyland/models/",
    ),
    FurnitureItemType.Prop_MML_Mailbox_Anim: FurnitureDefinition(
        name = "Animated MML Mailbox",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "mailbox_1",
        modelNamePrefix = "ara_mml_prp_",
        modelPath = "areas/mezzo_melodyland/models/",
        wantActor = True,
        actorAnimations = {
            "fightBoost": "mailbox_1-fightBoost",
            "fightCheer": "mailbox_1-fightCheer",
            "fightIdle": "mailbox_1-fightIdle",
            "fightIntoIdle": "mailbox_1-fightIntoIdle",
            "fightSad": "mailbox_1-fightSad",
            "idle0": "mailbox_1-idle0",
            "idle0settle": "mailbox_1-idle0settle",
            "idleAwesome3": "mailbox_1-idleAwesome3",
            "idleIntoFight": "mailbox_1-idleIntoFight",
            "idleLook2": "mailbox_1-idleLook2",
            "idleTake1": "mailbox_1-idleTake1",
            "victoryDance": "mailbox_1-victoryDance",
        },
    ),
    FurnitureItemType.Prop_MML_Trashcan: FurnitureDefinition(
        name = "MML Trashcan",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "trashcan_1",
        modelNamePrefix = "ara_mml_prp_",
        modelPath = "areas/mezzo_melodyland/models/",
    ),
    FurnitureItemType.Prop_MML_Trashcan_Anim: FurnitureDefinition(
        name = "Animated Trashcan",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "trashcan_1",
        modelNamePrefix = "ara_mml_prp_",
        modelPath = "areas/mezzo_melodyland/models/",
        wantActor = True,
        actorAnimations = {
            "fightBoost": "trashcan_1-fightBoost",
            "fightCheer0": "trashcan_1-fightCheer0",
            "fightCheer1": "trashcan_1-fightCheer1",
            "fightIdle": "trashcan_1-fightIdle",
            "fightIntoIdle": "trashcan_1-fightIntoIdle",
            "fightSad": "trashcan_1-fightSad",
            "idle0settle": "trashcan_1-idle0settle",
            "idleAwesome3": "trashcan_1-idleAwesome3",
            "idleBounce0": "trashcan_1-idleBounce0",
            "idleHelicopter2": "trashcan_1-idleHelicopter2",
            "idleIntoFight": "trashcan_1-idleIntoFight",
            "idleLook1": "trashcan_1-idleLook1",
            "victoryDance": "trashcan_1-victoryDance",
        },
    ),
    FurnitureItemType.Prop_MML_Streetlight_1: FurnitureDefinition(
        name = "Prop_MML_Streetlight_1",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "streetlight_1",
        modelNamePrefix = "ara_mml_prp_",
        modelPath = "areas/mezzo_melodyland/models/",
    ),
    FurnitureItemType.Prop_Theater_Lobby_Lamp: FurnitureDefinition(
        name = "Prop_Theater_Lobby_Lamp",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "lamp",
        modelNamePrefix = "ara_theater_int_lobby_prp_",
        modelPath = "areas/mezzo_melodyland/interiors/models/",
    ),
    FurnitureItemType.Prop_Theater_Lobby_Sofa: FurnitureDefinition(
        name = "Prop_Theater_Lobby_Sofa",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "sofa",
        modelNamePrefix = "ara_theater_int_lobby_prp_",
        modelPath = "areas/mezzo_melodyland/interiors/models/",
    ),
    FurnitureItemType.Prop_Theater_Lobby_Table: FurnitureDefinition(
        name = "Prop_Theater_Lobby_Table",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "table",
        modelNamePrefix = "ara_theater_int_lobby_prp_",
        modelPath = "areas/mezzo_melodyland/interiors/models/",
    ),
    FurnitureItemType.Ceiling_Theater_Lobby_Light: FurnitureDefinition(
        name = "boob lamp",
        description = "they are literally called boob lamps an they are known to suck (pun not intended)",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "light_ceiling",
        modelNamePrefix = "ara_theater_int_lobby_prp_",
        modelPath = "areas/mezzo_melodyland/interiors/models/",
    ),
    FurnitureItemType.Wall_Theater_Auditorium_Light: FurnitureDefinition(
        name = "Wall_Theater_Lobby_Light",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "light_wall",
        modelNamePrefix = "ara_theater_int_lobby_prp_",
        modelPath = "areas/mezzo_melodyland/interiors/models/",
    ),
    FurnitureItemType.Prop_Theater_Lobby_TicketCounter: FurnitureDefinition(
        name = "Prop_Theater_Lobby_TicketCounter",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "ticketcounter",
        modelNamePrefix = "ara_theater_int_lobby_prp_",
        modelPath = "areas/mezzo_melodyland/interiors/models/",
    ),
    # endregion

    ### The Brrrgh Props ###
    # region
    FurnitureItemType.Prop_TB_Hydrant: FurnitureDefinition(
        name = "Prop_TB_Hydrant",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "hydrant_1",
        modelNamePrefix = "ara_tb_prp_",
        modelPath = "areas/the_brrrgh/models/",
    ),
    FurnitureItemType.Prop_TB_Hydrant_Anim: FurnitureDefinition(
        name = "Prop_TB_Hydrant_Anim",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "hydrant_1",
        modelNamePrefix = "ara_tb_prp_",
        modelPath = "areas/the_brrrgh/models/",
        wantActor = True,
        actorAnimations = {
            "fightBoost": "hydrant_1-fightBoost",
            "fightCheer": "hydrant_1-fightCheer",
            "fightIdle": "hydrant_1-fightIdle",
            "fightIntoIdle": "hydrant_1-fightIntoIdle",
            "fightSad": "hydrant_1-fightSad",
            "idleAwesome3": "hydrant_1-idleAwesome3",
            "idleIntoFight": "hydrant_1-idleIntoFight",
            "idleRubNose0": "hydrant_1-idleRubNose0",
            "idleShiver1": "hydrant_1-idleShiver1",
            "idleSneeze2": "hydrant_1-idleSneeze2",
            "victoryDance": "hydrant_1-victoryDance",
        },
    ),
    FurnitureItemType.Prop_TB_Mailbox: FurnitureDefinition(
        name = "Prop_TB_Mailbox",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "mailbox_1",
        modelNamePrefix = "ara_tb_prp_",
        modelPath = "areas/the_brrrgh/models/",
        collisionNode="prop_mailboxcollisions",
        throwables = 4
    ),
    FurnitureItemType.Prop_TB_Mailbox_Anim: FurnitureDefinition(
        name = "Prop_TB_Mailbox_Anim",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "mailbox_1",
        modelNamePrefix = "ara_tb_prp_",
        modelPath = "areas/the_brrrgh/models/",
        wantActor = True,
        actorAnimations = {
            "fightBoost": "mailbox_1-fightBoost",
            "fightCheer": "mailbox_1-fightCheer",
            "fightIdle": "mailbox_1-fightIdle",
            "fightIntoIdle": "mailbox_1-fightIntoIdle",
            "fightSad": "mailbox_1-fightSad",
            "idle0": "mailbox_1-idle0",
            "idleAwesome3": "mailbox_1-idleAwesome3",
            "idleIntoFight": "mailbox_1-idleIntoFight",
            "idleShiver1": "mailbox_1-idleShiver1",
            "idleSneeze2": "mailbox_1-idleSneeze2",
            "idleSpin0": "mailbox_1-idleSpin0",
            "victoryDance": "mailbox_1-victoryDance",
        },
    ),
    FurnitureItemType.Prop_TB_Trashcan: FurnitureDefinition(
        name = "Prop_TB_Trashcan",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "trashcan_1",
        modelNamePrefix = "ara_tb_prp_",
        modelPath = "areas/the_brrrgh/models/",
    ),
    FurnitureItemType.Prop_TB_Trashcan_Anim: FurnitureDefinition(
        name = "Prop_TB_Trashcan_Anim",
        description = "No Description",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        modelName = "trashcan_1",
        modelNamePrefix = "ara_tb_prp_",
        modelPath = "areas/the_brrrgh/models/",
        wantActor = True,
        actorAnimations = {
            "fightBoost": "trashcan_1-fightBoost",
            "fightCheer": "trashcan_1-fightCheer",
            "fightIdle": "trashcan_1-fightIdle",
            "fightIntoIdle": "trashcan_1-fightIntoIdle",
            "fightSad": "trashcan_1-fightSad",
            "fightShiver": "trashcan_1-fightShiver",
            "idle0": "trashcan_1-idle0",
            "idleAwesome3": "trashcan_1-idleAwesome3",
            "idleIntoFight": "trashcan_1-idleIntoFight",
            "idleShiver1": "trashcan_1-idleShiver1",
            "idleSneeze2": "trashcan_1-idleSneeze2",
            "victoryDance": "trashcan_1-victoryDance",
        },
    ),
    FurnitureItemType.Prop_TB_Icecube: FurnitureDefinition(
        name = "Prop_TB_Icecube",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "icecube_1",
        modelNamePrefix = "ara_tb_prp_",
        modelPath = "areas/the_brrrgh/models/",
    ),
    FurnitureItemType.Prop_TB_PotbellyStove: FurnitureDefinition(
        name = "Prop_TB_PotbellyStove",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "potbellyStove_1",
        modelNamePrefix = "ara_tb_prp_",
        modelPath = "areas/the_brrrgh/models/",
    ),
    FurnitureItemType.Prop_TB_SnowPile: FurnitureDefinition(
        name = "Prop_TB_SnowPile",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "snowpile_1_full",
        modelNamePrefix = "ara_tb_prp_",
        modelPath = "areas/the_brrrgh/models/",
    ),
    FurnitureItemType.Prop_TB_NorthPole: FurnitureDefinition(
        name = "Prop_TB_NorthPole",
        description = "No Description",
        estateItemType = EstateItemType.GENERIC,
        modelName = "pole_1",
        modelNamePrefix = "ara_tb_prp_",
        modelPath = "areas/the_brrrgh/models/",
        wantActor = True,
        actorAnimations = {"wave": "pole_1-flag_wave_loop"},
    ),
    FurnitureItemType.Prop_MozPizza_Lobby_CashRegister: FurnitureDefinition(
        name = "Prop_MozPizza_Lobby_CashRegister",
        description = "No Description",
        modelName = "register",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Prop_MozPizza_Lobby_Table_Round: FurnitureDefinition(
        name = "Prop_MozPizza_Lobby_Table_Round",
        description = "No Description",
        modelName = "table_circle",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Prop_MozPizza_Lobby_Guestbook: FurnitureDefinition(
        name = "Prop_MozPizza_Lobby_Guestbook",
        description = "No Description",
        modelName = "podium",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Prop_MozPizza_Lobby_PopsicleTray: FurnitureDefinition(
        name = "Prop_MozPizza_Lobby_PopsicleTray",
        description = "No Description",
        modelName = "tray_popsicles",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Wall_MozPizza_Lobby_FanUnit: FurnitureDefinition(
        name = "Wall_MozPizza_Lobby_FanUnit",
        description = "No Description",
        modelName = "fanunit_1",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
        sequenceNodes = ["**/fan_seq"],
    ),
    FurnitureItemType.Prop_MozPizza_Lobby_Furnace_Frozen: FurnitureDefinition(
        name = "Prop_MozPizza_Lobby_Furnace_Frozen",
        description = "No Description",
        modelName = "furnace_frozen",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Ceiling_MozPizza_Lobby_Lamp: FurnitureDefinition(
        name = "Ceiling_MozPizza_Lobby_Lamp",
        description = "No Description",
        modelName = "light_ceiling",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Wall_MozPizza_Lobby_Lamp: FurnitureDefinition(
        name = "Wall_MozPizza_Lobby_Lamp",
        description = "No Description",
        modelName = "light_wall_curved",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Prop_MozPizza_Lobby_Dispenser: FurnitureDefinition(
        name = "Prop_MozPizza_Lobby_Dispenser",
        description = "No Description",
        modelName = "dispenser",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Prop_MozPizza_Lobby_CardboardBox: FurnitureDefinition(
        name = "Prop_MozPizza_Lobby_CardboardBox",
        description = "No Description",
        modelName = "box_cardboard",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Wall_MozPizza_Lobby_Dispenser_Cones: FurnitureDefinition(
        name = "Wall_MozPizza_Lobby_Dispenser_Cones",
        description = "No Description",
        modelName = "dispenser_cones",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Prop_MozPizza_Lobby_Machine_Cola: FurnitureDefinition(
        name = "Prop_MozPizza_Lobby_Machine_Cola",
        description = "No Description",
        modelName = "machine_cola",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Prop_MozPizza_Lobby_Machine_Popsicles: FurnitureDefinition(
        name = "Prop_MozPizza_Lobby_Machine_Popsicles",
        description = "No Description",
        modelName = "machine_popsicles",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Wall_MozPizza_Lobby_Pipe_End: FurnitureDefinition(
        name = "Wall_MozPizza_Lobby_Pipe_End",
        description = "No Description",
        modelName = "pipe_end_frozen",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Prop_MozPizza_Lobby_Bag_Dough: FurnitureDefinition(
        name = "Prop_MozPizza_Lobby_Bag_Dough",
        description = "No Description",
        modelName = "bag_dough_money",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Prop_MozPizza_Lobby_Shelf_Rack: FurnitureDefinition(
        name = "Prop_MozPizza_Lobby_Shelf_Rack",
        description = "No Description",
        modelName = "shelf_rack",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Prop_MozPizza_Lobby_Booth_Seats: FurnitureDefinition(
        name = "Prop_MozPizza_Lobby_Booth_Seats",
        description = "No Description",
        modelName = "booth_180",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    FurnitureItemType.Prop_MozPizza_Lobby_Gazebo_Entrance: FurnitureDefinition(
        name = "Prop_MozPizza_Lobby_Gazebo_Entrance",
        description = "No Description",
        modelName = "gazebo_entrance",
        modelNamePrefix = "ara_pizzeria_int_lobby_prp_",
        modelPath = "areas/the_brrrgh/interiors/models/",
    ),
    # endregion

    ### Acorn Acres Props ###
    # region
    FurnitureItemType.Prop_AA_Lamp_1: FurnitureDefinition(
        name = 'AA Streetlight 1',
        description = 'Play your favorite tunes on demand!',
        modelName = 'lamp_1',
        modelNamePrefix = "ara_aa_prp_",
        modelPath = "areas/acorn_acres/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_AA_Lamp_2: FurnitureDefinition(
        name = 'AA Streetlight 2',
        description = 'Play your favorite tunes on demand!',
        modelName = 'lamp_2',
        modelNamePrefix = "ara_aa_prp_",
        modelPath = "areas/acorn_acres/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_AA_Hydrant: FurnitureDefinition(
        name = 'AA Hydrant',
        description = 'Play your favorite tunes on demand!',
        modelName = 'hydrant_1',
        modelNamePrefix = "ara_aa_prp_",
        modelPath = "areas/acorn_acres/models/",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        wantActor = True,
        actorAnimations = {
            "fightIdle": "hydrant_1-fightIdle",
            "idle0": "hydrant_1-idle0",
            "victoryDance": "hydrant_1-victoryDance",
        },
    ),
    FurnitureItemType.Prop_AA_Mailbox: FurnitureDefinition(
        name = 'AA Mailbox',
        description = 'Play your favorite tunes on demand!',
        modelName = 'mailbox_1',
        modelNamePrefix = "ara_aa_prp_",
        modelPath = "areas/acorn_acres/models/",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        collisionNode = "mailbox_AA_coll",
        throwables = 5
    ),
    FurnitureItemType.Prop_AA_Trashcan: FurnitureDefinition(
        name = 'AA Trash can',
        description = 'Play your favorite tunes on demand!',
        modelName = 'trashcan_1',
        modelNamePrefix = "ara_aa_prp_",
        modelPath = "areas/acorn_acres/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    # endregion

    ### Drowsy Dreamland Props ###
    # region
    FurnitureItemType.Prop_DDL_Clouds_1: FurnitureDefinition(
        name = 'test_clouds',
        description = 'Play your favorite tunes on demand!',
        modelName = 'cloud_1',
        modelNamePrefix = "ara_ddl_prp_",
        modelPath = "areas/drowsy_dreamland/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_DDL_Hydrant_Anim: FurnitureDefinition(
        name = 'Prop_DDL_Hydrant',
        description = 'Play your favorite tunes on demand!',
        modelName = 'hydrant_1',
        modelNamePrefix = "ara_ddl_prp_",
        modelPath = "areas/drowsy_dreamland/models/",
        estateItemType = EstateItemType.GENERIC,
        wantActor = True,
        actorAnimations = {
            "fightBoost": "hydrant_1-fightBoost",
            "fightCheer": "hydrant_1-fightCheer",
            "fightIdle": "hydrant_1-fightIdle",
            "fightIntoIdle": "hydrant_1-fightIntoIdle",
            "fightSad": "hydrant_1-fightSad",
            "idle0": "hydrant_1-idle0",
            "idle1": "hydrant_1-idle1",
            "idle2": "hydrant_1-idle2",
            "idleAwesome3": "hydrant_1-idleAwesome3",
            "idleIntoFight": "hydrant_1-idleIntoFight",
            "victoryDance": "hydrant_1-victoryDance",
        },
    ),
    FurnitureItemType.Prop_DDL_Mailbox_Anim: FurnitureDefinition(
        name = 'Prop_DDL_Mailbox_Anim',
        description = 'Play your favorite tunes on demand!',
        modelName = 'mailbox_1',
        modelNamePrefix = "ara_ddl_prp_",
        modelPath = "areas/drowsy_dreamland/models/",
        estateItemType = EstateItemType.GENERIC,
        wantActor = True,
        actorAnimations = {
            "idleSleep0": "mailbox_1-idleSleep0",
        },
    ),
    FurnitureItemType.Prop_DDL_Trashcan_Anim: FurnitureDefinition(
        name = 'Prop_DDL_Mailbox_Anim',
        description = 'Play your favorite tunes on demand!',
        modelName = 'trashcan_1',
        modelNamePrefix = "ara_ddl_prp_",
        modelPath = "areas/drowsy_dreamland/models/",
        estateItemType = EstateItemType.GENERIC,
        wantActor = True,
        actorAnimations = {
            "idleSleep0": "trashcan_1-idleSleep0",
        },
    ),
    FurnitureItemType.Prop_DDL_Tree_1: FurnitureDefinition(
        name = 'Prop_DDL_Tree_1',
        description = 'Play your favorite tunes on demand!',
        modelName = 'tree_1',
        modelNamePrefix = "ara_ddl_prp_",
        modelPath = "areas/drowsy_dreamland/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    # endregion

    ### Roadster Raceway Props ###
    # region
    FurnitureItemType.Prop_RR_Crate: FurnitureDefinition(
        name = "Crate",
        modelName = 'crate_1',
        modelNamePrefix = "ara_rr_prp_",
        modelPath = "areas/roadster_raceway/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_RR_BigTires: FurnitureDefinition(
        name = "Big Tires",
        modelName = 'tire_stack',
        modelNamePrefix = "ara_rr_prp_",
        modelPath = "areas/roadster_raceway/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_RR_WrenchJack: FurnitureDefinition(
        name = "Wrench Jack",
        modelName = "wrenchJack",
        modelNamePrefix = "ara_rr_prp_",
        modelPath = "areas/roadster_raceway/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_RR_Mailbox: FurnitureDefinition(
        name = "Racer Mailbox",
        modelName = "mailbox_1",
        modelNamePrefix = "ara_rr_prp_",
        modelPath = "areas/roadster_raceway/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_RR_Lamppost: FurnitureDefinition(
        name = "Racer Lampost",
        modelName = 'lamp_1',
        modelNamePrefix = "ara_rr_prp_",
        modelPath = "areas/roadster_raceway/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_RR_Announcer: FurnitureDefinition(
        name = "Announcer",
        modelName = 'announcer_1',
        modelNamePrefix = "ara_rr_prp_",
        modelPath = "areas/roadster_raceway/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_RR_Cone: FurnitureDefinition(
        name = "Cone",
        modelName = 'cone',
        modelNamePrefix = "ara_rr_prp_",
        modelPath = "areas/roadster_raceway/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_RR_LeaderboardSign: FurnitureDefinition(
        name = "Leaderboard Sign",
        modelName = 'leaderboard_1',
        modelNamePrefix = "ara_rr_prp_",
        modelPath = "areas/roadster_raceway/models/",
        estateItemType = EstateItemType.GENERIC,
    ),
    # endregion

    ### Sellbot HQ ###
    # region
    # endregion

    ### Cashbot HQ ###
    # region
    FurnitureItemType.Prop_Cashbot_Safe_1: FurnitureDefinition(
        name = "CashBotSafe",
        modelName = "safe_1",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_cashbotHQ_prp_",
        modelPath = "areas/coghq/models/",
        modelScale = 0.25,
    ),
    FurnitureItemType.Prop_Cashbot_CashRegister_1: FurnitureDefinition(
        name = "CashBotHQCshRegister",
        modelName = "register_1",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_cashbotHQ_prp_",
        modelPath = "areas/coghq/models/",
        modelScale = 0.25,
    ),
    FurnitureItemType.Prop_Cashbot_Crate_1: FurnitureDefinition(
        name = "CBMetalCrate",
        modelName = "crate_2x2",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_cashbotHQ_prp_",
        modelPath = "areas/coghq/models/",
    ),
    FurnitureItemType.Prop_Cashbot_Crate_2: FurnitureDefinition(
        name = "CBWoodCrate",
        modelName = "crate_1x1",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_cashbotHQ_prp_",
        modelPath = "areas/coghq/models/",
    ),
    FurnitureItemType.Prop_Cashbot_GoldBar_Single: FurnitureDefinition(
        name = "GoldBar",
        modelName = "gold_bar",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_cashbotHQ_prp_",
        modelPath = "areas/coghq/models/",
        modelScale = 0.25,
    ),
    FurnitureItemType.Prop_Cashbot_GoldBar_Stack: FurnitureDefinition(
        name = "GoldBarStack",
        modelName = "gold_stack",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_cashbotHQ_prp_",
        modelPath = "areas/coghq/models/",
        modelScale = 0.25,
    ),
    FurnitureItemType.Prop_Cashbot_MoneyBag_Single: FurnitureDefinition(
        name = "MoneyBag",
        modelName = "MoneyBag",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_10/models/cashbotHQ/",
        overrideDefaultModelPrefix = True,
        modelScale = 0.25,
    ),
    FurnitureItemType.Prop_Cashbot_Money_Single: FurnitureDefinition(
        name = "MoneyStack",
        modelName = "MoneyStack",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_10/models/cashbotHQ/",
        overrideDefaultModelPrefix = True,
        modelScale = 0.25,
    ),
    FurnitureItemType.Prop_Cashbot_Money_Stack: FurnitureDefinition(
        name = "MoneyStackPallet",
        modelName = "MoneyStackPallet",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_10/models/cashbotHQ/",
        overrideDefaultModelPrefix = True,
        modelScale = 0.25,
    ),

    FurnitureItemType.Ceiling_Cashbot_TrainSignal: FurnitureDefinition(
        name = "Ceiling_Cashbot_TrainSignal",
        modelName = "lightSignal",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_cashbotHQ_prp_",
        modelPath = "areas/coghq/models/",
    ),

    FurnitureItemType.Prop_Cashbot_Column_Vault: FurnitureDefinition(
        name = "Prop_Cashbot_Column_Vault",
        modelName = "column_vault",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "ara_cashbotHQ_prp_",
        modelPath = "areas/coghq/models/",
    ),
    # endregion

    ### Lawbot HQ ###
    # region
    FurnitureItemType.Prop_Lawbot_Couch_1: FurnitureDefinition(
        name = "da_couch",
        modelName = "da_couch",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Couch_2: FurnitureDefinition(
        name = "cc_m_ara_lbhq_prp_couch_2",
        modelName = "cc_m_ara_lbhq_prp_couch_2",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Couch_3: FurnitureDefinition(
        name = "LB_couchA",
        modelName = "LB_couchA",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),

    FurnitureItemType.Prop_Lawbot_Desk_2: FurnitureDefinition(
        name = "da_desk",
        modelName = "da_desk",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Desk_3: FurnitureDefinition(
        name = "cc_m_ara_lbhq_prp_desk_3",
        modelName = "cc_m_ara_lbhq_prp_desk_3",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Plant_Fern: FurnitureDefinition(
        name = "cc_m_ara_lbhq_prp_plant_1",
        modelName = "cc_m_ara_lbhq_prp_plant_1",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Wall_Lawbot_Insignia: FurnitureDefinition(
        name = "cc_m_ara_lbhq_prp_insignia",
        modelName = "cc_m_ara_lbhq_prp_insignia",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Crate_1: FurnitureDefinition(
        name = "LB_CardBoardBox",
        modelName = "LB_CardBoardBox",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Crate_2: FurnitureDefinition(
        name = "LB_metal_crate",
        modelName = "LB_metal_crate",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Paper_Stack_1: FurnitureDefinition(
        name = "LB_paper_big_stacks3",
        modelName = "LB_paper_big_stacks3",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Bookshelf_1: FurnitureDefinition(
        name = "LB_bookshelfA",
        modelName = "LB_bookshelfA",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Bookshelf_2: FurnitureDefinition(
        name = "LB_bookshelfB",
        modelName = "LB_bookshelfB",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Cabinet_1: FurnitureDefinition(
        name = "LA_filing_cabA",
        modelName = "LA_filing_cabA",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Cabinet_2: FurnitureDefinition(
        name = "LA_filing_cabB",
        modelName = "LA_filing_cabB",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Vacuum_Pipes: FurnitureDefinition(
        name = "da_vacuum_pipes",
        modelName = "da_vacuum_pipes",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Lamp_Tall_1: FurnitureDefinition(
        name = "da_tall_lamp",
        modelName = "da_tall_lamp",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Lamp_Desk_1: FurnitureDefinition(
        name = "da_desk_lamp",
        modelName = "da_desk_lamp",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Armchair_1: FurnitureDefinition(
        name = "da_armchair",
        modelName = "da_armchair",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
    ),
    FurnitureItemType.Prop_Lawbot_Armchair_3: FurnitureDefinition(
        name = "LawbotBossRoomChair",
        modelName = "LawbotBossRoomChair",
        estateItemType = EstateItemType.GENERIC,
        modelNamePrefix = "",
        modelPath = "phase_11/models/lawbotHQ/",
        overrideDefaultModelPrefix = True,
        modelScale = 0.5,
    ),
    # endregion

    ### Halloween Props ###
    # region
    FurnitureItemType.Prop_HW_Pumpkin_Classic_Short: FurnitureDefinition(
        name = "Classic Short Pumpkin",
        description = "No Description",
        modelName = "hw_pumpkin_classic_short",
        estateItemType = EstateItemType.PROP_PUMPKIN,
    ),
    FurnitureItemType.Prop_HW_Pumpkin_Classic_Tall: FurnitureDefinition(
        name = "Classic Tall Pumpkin",
        description = "No Description",
        modelName = "hw_pumpkin_classic_tall",
        estateItemType = EstateItemType.PROP_PUMPKIN,
    ),
    FurnitureItemType.Wall_HW_Painting_AutographedErclaim: FurnitureDefinition(
        name = "Autographed Erclaim",
        description = "No Description",
        modelName = "gen_painting_tall",
        textureName = "hw_painting_count",
        estateItemType = EstateItemType.GENERIC_PLANE,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
        modelScale = 2.0,
    ),
    FurnitureItemType.Wall_HW_Painting_ChupDelight: FurnitureDefinition(
        name = "Chup Delight",
        description = "No Description",
        modelName = "gen_painting_tall",
        textureName = "hw_painting_chup",
        estateItemType = EstateItemType.GENERIC_PLANE,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
        modelScale = 2.0,
    ),

    # endregion

    ### Winter Props ###
    # region
    FurnitureItemType.Prop_Win_Tree_1: FurnitureDefinition(
        name = "Winter Tree",
        description = "No Description",
        modelName = "win_tree",
        estateItemType = EstateItemType.GENERIC,
        animSpeed = 0.1,
    ),
    FurnitureItemType.Wall_Win_Wreath: FurnitureDefinition(
        name = "Winter Wreath",
        description = "No Description",
        modelName = "win_wreath",
        estateItemType = EstateItemType.GENERIC,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL,
    ),
    FurnitureItemType.Prop_Win_Presents_Stack: FurnitureDefinition(
        name = "Presents",
        description = "No Description",
        modelName = "win_presents",
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Win_Sled: FurnitureDefinition(
        name = "Sled",
        description = "No Description",
        modelName = "win_sled",
        estateItemType = EstateItemType.GENERIC,
    ),
    # endregion

    ### Window Views ###
    # region
    FurnitureItemType.Window_LargeGarden: FurnitureDefinition(
        name = "Large Garden",
        description = "No Description",
        modelName = "garden_1",
        estateItemType = EstateItemType.WINDOW_VIEW,
        estateItemPlacementFlag = EstateItemPlacementFlags.WINDOW,
    ),
    FurnitureItemType.Window_WildGarden: FurnitureDefinition(
        name = "Wild Garden",
        description = "No Description",
        modelName = "garden_2",
        estateItemType = EstateItemType.WINDOW_VIEW,
        estateItemPlacementFlag = EstateItemPlacementFlags.WINDOW,
    ),
    FurnitureItemType.Window_GreekGarden: FurnitureDefinition(
        name = "Greek Garden",
        description = "No Description",
        modelName = "garden_3",
        estateItemType = EstateItemType.WINDOW_VIEW,
        estateItemPlacementFlag = EstateItemPlacementFlags.WINDOW,
    ),
    FurnitureItemType.Window_Cityscape: FurnitureDefinition(
        name = "Cityscape",
        description = "No Description",
        modelName = "city_1",
        estateItemType = EstateItemType.WINDOW_VIEW,
        estateItemPlacementFlag = EstateItemPlacementFlags.WINDOW,
    ),
    FurnitureItemType.Window_WildWest: FurnitureDefinition(
        name = "Wild West",
        description = "No Description",
        modelName = "west_2",
        estateItemType = EstateItemType.WINDOW_VIEW,
        estateItemPlacementFlag = EstateItemPlacementFlags.WINDOW,
    ),
    FurnitureItemType.Window_UnderTheSea: FurnitureDefinition(
        name = "Under the Sea",
        description = "No Description",
        modelName = "underwater_1",
        estateItemType = EstateItemType.WINDOW_VIEW,
        estateItemPlacementFlag = EstateItemPlacementFlags.WINDOW,
    ),
    FurnitureItemType.Window_TropicalIsland: FurnitureDefinition(
        name = "Tropical Island",
        description = "No Description",
        modelName = "tropic_1",
        estateItemType = EstateItemType.WINDOW_VIEW,
        estateItemPlacementFlag = EstateItemPlacementFlags.WINDOW,
    ),
    FurnitureItemType.Window_StarryNight: FurnitureDefinition(
        name = "Starry Night",
        description = "No Description",
        modelName = "space_1",
        estateItemType = EstateItemType.WINDOW_VIEW,
        estateItemPlacementFlag = EstateItemPlacementFlags.WINDOW,
    ),
    FurnitureItemType.Window_TikiPool: FurnitureDefinition(
        name = "Tiki Pool",
        description = "No Description",
        modelName = "pool_1",
        estateItemType = EstateItemType.WINDOW_VIEW,
        estateItemPlacementFlag = EstateItemPlacementFlags.WINDOW,
    ),
    FurnitureItemType.Window_FrozenFrontier: FurnitureDefinition(
        name = "Frozen Frontier",
        description = "No Description",
        modelName = "frost_1",
        estateItemType = EstateItemType.WINDOW_VIEW,
        estateItemPlacementFlag = EstateItemPlacementFlags.WINDOW,
    ),
    FurnitureItemType.Window_FarmCountry: FurnitureDefinition(
        name = "Farm Country",
        description = "No Description",
        modelName = "farm_1",
        estateItemType = EstateItemType.WINDOW_VIEW,
        estateItemPlacementFlag = EstateItemPlacementFlags.WINDOW,
    ),
    FurnitureItemType.Window_MainStreet: FurnitureDefinition(
        name = "Main Street",
        description = "No Description",
        modelName = "west_1",
        estateItemType = EstateItemType.WINDOW_VIEW,
        estateItemPlacementFlag = EstateItemPlacementFlags.WINDOW,
    ),
    # endregion

    ### Doorways ###
    # region
    FurnitureItemType.Doorway_DoubleRound: FurnitureDefinition(
        name = 'Double-Round Doors',
        description = 'I love doors',
        modelPath = 'areas/common/models/',
        modelNamePrefix = 'gen_prp_door_',
        modelName = 'double_round',
        estateItemType = EstateItemType.DOORWAY,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL_STUCK_TO_FLOOR,
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = '',
        modelScale = 1.0,
        hidePlacedModel = True,
    ),
    FurnitureItemType.Doorway_SellbotHQ: FurnitureDefinition(
        name = 'Sellbot HQ Doors',
        description = 'Covered in imported blueberry.',
        modelName = 'door_sellbotHQ',
        modelPath = "phase_9/models/modules/",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        modelFind = '',
        estateItemType = EstateItemType.DOORWAY,
        estateItemPlacementFlag = EstateItemPlacementFlags.WALL_STUCK_TO_FLOOR,
        doorType = EstateDoorType.SELLBOT_COG_HQ,
        doorOrigin = '',
        modelScale = 0.7,
        hidePlacedModel = True,
    ),
    # endregion

    ### Houses ###
    # region
    FurnitureItemType.House_Cabin_Classic: FurnitureDefinition(
        name = 'My Beautiful House',
        description = 'I love my beautioful house !',
        modelName = 'cabin_1',
        estateItemType = EstateItemType.HOUSE,
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = 'door_origin',
        doorPosHprScale = (0, 0, 0, 90, 0, 0, 0.8, 0.8, 0.8),
    ),
    FurnitureItemType.House_Default: FurnitureDefinition(
        name = 'My Default House',
        description = 'I love my Default house !',
        modelName = 'default_1',
        estateItemType = EstateItemType.HOUSE,
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = 'door_origin',
        doorPosHprScale = (0, 0, 0, 90, 0, 0, 0.8, 0.8, 0.8),
    ),
    FurnitureItemType.House_Yott_1: FurnitureDefinition(
        name = 'Yott House 1',
        description = 'I love my Yott house !',
        modelName = 'yott_1',
        estateItemType = EstateItemType.HOUSE,
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = 'door_origin',
        doorPosHprScale = (0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8),
        modelScale = 0.75,
    ),
    FurnitureItemType.House_Yott_2: FurnitureDefinition(
        name = 'Yott House 2',
        description = 'I love my Yott house !',
        modelName = 'yott_2',
        estateItemType = EstateItemType.HOUSE,
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = 'door_origin',
        doorPosHprScale = (0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8),
        modelScale = 0.7,
    ),
    FurnitureItemType.House_Yott_3: FurnitureDefinition(
        name = 'Yott House 3',
        description = 'I love my Yott house !',
        modelName = 'yott_3',
        estateItemType = EstateItemType.HOUSE,
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = 'door_origin',
        doorPosHprScale = (0, 0, 0, 0, 0, 0, 0.8, 0.8, 0.8),
        modelScale = 0.75,
    ),
    FurnitureItemType.House_SkyClan_WatchTower: FurnitureDefinition(
        name = 'Sky Clan Watchtower',
        description = 'I love my Yott house !',
        modelName = 'watchtower_ext',
        modelPath = 'areas/sky_clan/models/',
        modelNamePrefix = 'ara_msc_',
        estateItemType = EstateItemType.HOUSE,
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = 'door_origin',
        doorPosHprScale = (0, 0, 0, 0, 0, 0, 1, 1, 1),
        modelScale = 0.5,
    ),
    FurnitureItemType.House_SkyClan_WorkShop: FurnitureDefinition(
        name = 'Sky Clan Repair Shop',
        description = 'I love my Yott house !',
        modelName = 'workshop_ext',
        modelPath = 'areas/sky_clan/models/',
        modelNamePrefix = 'ara_msc_',
        estateItemType = EstateItemType.HOUSE,
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = 'door_origin',
        doorPosHprScale = (0, 0, 0, 0, 0, 0, 1, 1, 1),
        modelScale = 0.8,

    ),
    FurnitureItemType.House_SkyClan_RepairShop: FurnitureDefinition(
        name = 'Sky Clan Repair Shop',
        description = 'I love my Yott house !',
        modelName = 'repairshop_ext',
        modelPath = 'areas/sky_clan/models/',
        modelNamePrefix = 'ara_msc_',
        estateItemType = EstateItemType.HOUSE,
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = 'door_origin',
        doorPosHprScale = (0, 0, 0, 0, 0, 0, 1, 1, 1),
        modelScale = 0.8,

    ),
    FurnitureItemType.House_SkyClan_Hangar: FurnitureDefinition(
        name = 'Sky Clan Hangar',
        description = 'I love my Yott house !',
        modelName = 'hangar_ext',
        modelPath = 'areas/sky_clan/models/',
        modelNamePrefix = 'ara_msc_',
        estateItemType = EstateItemType.HOUSE,
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = 'door_origin',
        doorPosHprScale = (0, 0, 0, 0, 0, 0, 1, 1, 1),
        modelScale = 0.8,
    ),
    FurnitureItemType.House_SkyClan_FabricWorker: FurnitureDefinition(
        name = 'Sky Clan Fabric Worker',
        description = 'I love my Yott house !',
        modelName = 'fabworker_ext',
        modelPath = 'areas/sky_clan/models/',
        modelNamePrefix = 'ara_msc_',
        estateItemType = EstateItemType.HOUSE,
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = 'door_origin',
        doorPosHprScale = (0, 0, 0, 0, 0, 0, 1, 1, 1),
        modelScale = 0.8,
    ),
    FurnitureItemType.House_SkyClan_Hall: FurnitureDefinition(
        name = 'Sky Clan Hall',
        description = 'I love my Yott house !',
        modelName = 'clanhall_ext',
        modelPath = 'areas/sky_clan/models/',
        modelNamePrefix = 'ara_msc_',
        estateItemType = EstateItemType.HOUSE,
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = 'door_origin',
        doorPosHprScale = (0, 0, 0, 0, 0, 0, 1, 1, 1),
    ),
    # endregion

    # Special
    FurnitureItemType.Prop_Classic_Trampoline: FurnitureDefinition(
        name = 'Classic Trampoline',
        description = 'Bouncy!',
        modelName = 'trampoline_classic',
        modelNamePrefix = 'ara_est_prp_ext_',
        modelScale = 0.7,
        estateItemType = EstateItemType.PROP_INTERACTIVE_TRAMPOLINE,
        estateItemPlacementFlag = EstateItemPlacementFlags.STANDARD,
    ),
    FurnitureItemType.Prop_Classic_Jukebox: FurnitureDefinition(
        name = 'Classic Jukebox',
        description = 'Play your favorite tunes on demand!',
        modelName = 'jukebox_classic',
        modelNamePrefix = "prp_toon_",
        estateItemType = EstateItemType.PROP_INTERACTIVE_JUKEBOX,
        wantActor = True,
        actorAnimations = {"dance": "jukebox_classic-dance"},
    ),
    FurnitureItemType.Prop_PicnicTable: FurnitureDefinition(
        name = 'Picnic Game Table',
        description = 'Is that a We Just Wanna Play Toono reference?',
        modelName = 'tablegame_bench_1',
        modelNamePrefix = 'gen_toon_prp_',
        estateItemType = EstateItemType.PROP_TABLE_BOARDGAMES,
    ),
    FurnitureItemType.Prop_Classic_Dancefloor: FurnitureDefinition(
        name = 'Prop_Classic_Dancefloor',
        description = 'Swag',
        modelName = 'dancefloor_classic',
        modelNamePrefix = 'prp_toon_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_ToonStatue: FurnitureDefinition(
        name = 'Toon Statue',
        description = 'A wonderful sculpture of your own Toon!',
        modelName = 'statue_1',
        modelNamePrefix = "ara_est_prp_ext_",
        modelScale = (0.05 * 1.5, 0.05 * 1.5, 0.05),
        estateItemType = EstateItemType.PROP_STATUE_TOON,
    ),
    FurnitureItemType.Prop_Weather_Rain: FurnitureDefinition(
        name = 'Rain Generator',
        description = 'Let it rain!',
        modelName='speaker_amp',
        modelPath='areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix='ara_fassuite_int_prp_',
        estateItemType = EstateItemType.PROP_GENERATOR_WEATHER,
        estateKitType = EstateKitType.EXTERIOR,
        maxItems = 1,
    ),
    FurnitureItemType.Prop_Weather_Snow: FurnitureDefinition(
        name = 'Snow Generator',
        description = 'Let it snow!',
        modelName='speaker_amp',
        modelPath='areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix='ara_fassuite_int_prp_',
        estateItemType = EstateItemType.PROP_GENERATOR_WEATHER,
        estateKitType = EstateKitType.EXTERIOR,
        maxItems = 1,
    ),
    FurnitureItemType.Prop_Fireworks: FurnitureDefinition(
        name = 'Firework Generator',
        description = 'Wow! Fireworks!',
        modelName = 'weight_stand_mini',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.PROP_GENERATOR_FIREWORKS,
        estateKitType = EstateKitType.EXTERIOR,
        maxItems = 1,
    ),
    FurnitureItemType.Prop_Classic_InflatableTube: FurnitureDefinition(
        name = 'Inflatable Tube',
        description = 'Play your favorite tunes on demand!',
        modelName = 'inflatableTube',
        modelNamePrefix = "ara_est_prp_ext_",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        wantActor = True,
        actorAnimations = {"wave": "inflatableTube-wave"},
    ),
    FurnitureItemType.Prop_Classic_DummyCog: FurnitureDefinition(
        name = 'Cog Dummy',
        description = 'Play your favorite tunes on demand!',
        modelName = 'cogDummy_1',
        modelNamePrefix = "ara_est_prp_ext_",
        estateItemType = EstateItemType.ACTOR_INTERACTABLE,
        wantActor = True,
        actorAnimations = {"idle": "cogDummy_1-idle"},
    ),

    ### Sky Projectors ###
    # region
    FurnitureItemType.SkyProjector_Blue: FurnitureDefinition(
        name = 'Blue Sky Projector',
        description = 'ttc sky',
        modelName = 'speaker_wall',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.SKYBOX,
        estateKitType = EstateKitType.EXTERIOR,
        maxItems = 1,
        skyPath = 'phase_3.5/models/props/TT_sky',
    ),
    FurnitureItemType.SkyProjector_Cloudy: FurnitureDefinition(
        name = 'Cloudy Sky Projector',
        description = 'brrrgh sky',
        modelName = 'speaker_wall',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.SKYBOX,
        estateKitType = EstateKitType.EXTERIOR,
        maxItems = 1,
        skyPath = 'phase_3.5/models/props/BR_sky',
    ),
    FurnitureItemType.SkyProjector_Night: FurnitureDefinition(
        name = 'Night Sky Projector',
        description = 'ddl sky',
        modelName = 'speaker_wall',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.SKYBOX,
        estateKitType = EstateKitType.EXTERIOR,
        maxItems = 1,
        skyPath = 'phase_8/models/props/DL_sky',
    ),
    FurnitureItemType.SkyProjector_Pink: FurnitureDefinition(
        name = 'Pink Sky Projector',
        description = 'yott sky',
        modelName = 'speaker_wall',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.SKYBOX,
        estateKitType = EstateKitType.EXTERIOR,
        maxItems = 1,
        skyPath = 'phase_7/models/props/OT_sky',
    ),
    FurnitureItemType.SkyProjector_Purple: FurnitureDefinition(
        name = 'Purple Sky Projector',
        description = 'mml sky',
        modelName = 'speaker_wall',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.SKYBOX,
        estateKitType = EstateKitType.EXTERIOR,
        maxItems = 1,
        skyPath = 'phase_6/models/props/MM_sky',
    ),
    # endregion

    ### Fast Asleep All Star Suite Props ###
    # region
    FurnitureItemType.Prop_Fassuite_Lamp_Lava: FurnitureDefinition(
        name = 'Lava Lamp',
        description = 'Harness the power of lava, right at home!',
        modelName = '',
        estateItemType = EstateItemType.LAVA_LAMP,
    ),
    FurnitureItemType.Prop_Fassuite_Bell: FurnitureDefinition(
        name = 'Bell',
        description = 'Bouncy!',
        modelName = 'bell',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        modelScale = 1.0,
        estateItemType = EstateItemType.GENERIC,
    ),

    FurnitureItemType.Prop_Fassuite_Bench_Wood: FurnitureDefinition(
        name = 'Warm-up Bench',
        description = 'Bouncy!',
        modelName = 'bench_wood',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        modelScale = 0.7,
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Desk_Curved: FurnitureDefinition(
        name = 'Curved Desk',
        description = 'Bouncy!',
        modelName = 'desk_curved',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Wall_Fassuite_Speaker: FurnitureDefinition(
        name = 'Wall Speaker',
        description = 'Bouncy!',
        modelName = 'speaker_wall',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Speaker_Small: FurnitureDefinition(
        name = 'Small Speaker',
        description = 'Bouncy!',
        modelName = 'speaker_small',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Speaker_Tall: FurnitureDefinition(
        name = 'Tall Speaker',
        description = 'Bouncy!',
        modelName = 'speaker_tall',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Speaker_Skinny: FurnitureDefinition(
        name = 'Skinny Speaker',
        description = 'Bouncy!',
        modelName = 'speaker_skinny',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Speaker_Amp: FurnitureDefinition(
        name = 'Guitar Amplifier',
        description = 'Bouncy!',
        modelName = 'speaker_amp',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Table_Round_Small: FurnitureDefinition(
        name = 'Bell',
        description = 'Bouncy!',
        modelName = 'table_round_small',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Table_Round_Large: FurnitureDefinition(
        name = 'Round Table',
        description = 'Bouncy!',
        modelName = 'table_round_large',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Sofa_Curved_45: FurnitureDefinition(
        name = 'All-Star Couch',
        description = 'Bouncy!',
        modelName = 'sofa_curved_45',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Sofa_Curved_180: FurnitureDefinition(
        name = 'All-Star Sofa',
        description = 'Approximately 1 mile long!',
        modelName = 'sofa_curved_180',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Sign_PaceCorner: FurnitureDefinition(
        name = 'The Pace Corner',
        description = 'Bouncy!',
        modelName = 'sign_pacecorner',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Sign_Desk: FurnitureDefinition(
        name = 'Silver Sign',
        description = 'Bouncy!',
        modelName = 'sign_desk',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Weight_Barbell: FurnitureDefinition(
        name = 'Barbell',
        description = 'Bouncy!',
        modelName = 'weight_barbell',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Weight_Circles: FurnitureDefinition(
        name = 'Circular Weights',
        description = 'Bouncy!',
        modelName = 'weight_circles',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Weight_Stand_Mini: FurnitureDefinition(
        name = 'Mini Weight Stand',
        description = 'Bouncy!',
        modelName = 'weight_stand_mini',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Ropes: FurnitureDefinition(
        name = 'Velvet Ropes',
        description = 'Bouncy!',
        modelName = 'ropes',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Wall_Fassuite_Sweatband: FurnitureDefinition(
        name = 'Prop_Fassuite_Sweatband_Wall',
        description = 'Bouncy!',
        modelName = 'sweatband_wall',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Wall_Fassuite_Vinyl: FurnitureDefinition(
        name = 'Prop_Fassuite_Vinyl_Wall',
        description = 'Bouncy!',
        modelName = 'vinyl_1',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Ceiling_Fassuite_Lights_1: FurnitureDefinition(
        name = 'Ceiling_Fassuite_Lights_1',
        description = 'Bouncy!',
        modelName = 'lights_ceiling_1',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Ceiling_Fassuite_Lights_2: FurnitureDefinition(
        name = 'Ceiling_Fassuite_Lights_2',
        description = 'Bouncy!',
        modelName = 'lights_ceiling_2',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Wall_Fassuite_Lights_Neon_Circle: FurnitureDefinition(
        name = 'Wall_Fassuite_Lights_Neon_Circle',
        description = 'Bouncy!',
        modelName = 'lights_neon_circle',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Wall_Fassuite_Lights_Neon_Strip: FurnitureDefinition(
        name = 'Wall_Fassuite_Lights_Neon_Strip',
        description = 'Bouncy!',
        modelName = 'lights_neon_strip',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Ceiling_Fassuite_Spotlights_1: FurnitureDefinition(
        name = 'Ceiling_Fassuite_Spotlights_1',
        description = 'Bouncy!',
        modelName = 'spotlights_ceiling',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Prop_Fassuite_Fountain: FurnitureDefinition(
        name = 'Prop_Fassuite_Fountain',
        description = 'Bouncy!',
        modelName = 'waterfountain',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.GENERIC,
    ),
    FurnitureItemType.Wall_Fassuite_Lights_Neon_Strip_Desat: FurnitureDefinition(
        name = 'Wall_Fassuite_Lights_Neon_Strip_Desat',
        description = 'Bouncy!',
        modelName = 'lights_neon_strip_desat',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        modelNamePrefix = 'ara_fassuite_int_prp_',
        estateItemType = EstateItemType.PROP_LIGHT_NEON,
    ),
    # endregion

    FurnitureItemType.Prop_Pier_Fishing: FurnitureDefinition(
        name = 'Prop_Pier_Fishing',
        description = 'Bouncy!',
        modelName = 'piers_tt',
        modelPath = "phase_4/models/props/",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
    ),


}

# The registry dictionary for furniture.
