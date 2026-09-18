"""
This module contains the item data for estate styles.
"""
from __future__ import annotations
from panda3d.core import NodePath

from toontown.estate.EstateGlobals import EstateKitType
from toontown.estate.zones.EstateDoorGlobals import EstateDoorType
from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.base.ItemDefinition import ItemDefinition
from typing import Dict, Optional
from enum import IntEnum

from toontown.inventory.enums.ItemEnums import EstateStyleItemType
from toontown.utils import ColorHelper


class EstateStyleDefinition(ItemDefinition):
    """
    The definition structure for furniture.
    """

    kitType2Prefix = {
        EstateKitType.INTERIOR: "int",
        EstateKitType.EXTERIOR: "ext",
        EstateKitType.STANDARD: "",
    }

    def __init__(self,
                 modelName: str,
                 modelPath: str = "",
                 modelNamePrefix: str = "",
                 overrideDefaultModelPrefix: bool = False,
                 modelScale: float = 1.0,
                 estateKitType: EstateKitType = EstateKitType.STANDARD,
                 doorType: EstateDoorType = EstateDoorType.DEBUG,
                 doorOrigin: str = '',
                 doorColor: str = 'ffffff',
                 doorPosHprScale: tuple = (0, 0, 0, 0, 0, 0, 1.0, 1.0, 1.0),
                 **kwargs):
        super().__init__(**kwargs)
        self.estateKitType = estateKitType
        self.modelName = modelName
        self.modelPath = modelPath
        self.modelScale = modelScale
        if not self.modelPath:
            self.modelPath = "areas/estate/kits/models/"

        if not modelNamePrefix and not overrideDefaultModelPrefix:
            modelNamePrefix = f"ara_est_kit_{self.kitType2Prefix[self.estateKitType]}"
        if modelNamePrefix and not modelNamePrefix.endswith("_"):
            modelNamePrefix += "_"

        if not overrideDefaultModelPrefix:
            self.baseModelPrefix = f"cc_m_{modelNamePrefix}"
        else:
            self.baseModelPrefix = modelNamePrefix

        self.doorType = doorType
        self.doorOrigin = doorOrigin
        self.doorColor = doorColor
        self.doorPosHprScale = doorPosHprScale

    def getModelPath(self):
        if not self.modelName:
            return None
        return f"{self.modelPath}{self.baseModelPrefix}{self.modelName}"

    def getModelScale(self) -> float:
        return self.modelScale

    def getDoorType(self) -> EstateDoorType:
        return self.doorType

    def getDoorOrigin(self) -> str:
        return self.doorOrigin

    def getDoorColor(self) -> tuple:
        return ColorHelper.hexToPCol(self.doorColor)

    def getDoorPosHprScale(self) -> tuple:
        return self.doorPosHprScale

    def getEstateKitType(self) -> EstateKitType:
        return self.estateKitType

    def getItemTypeName(self):
        return 'Estate Kit'

    def getRewardName(self, item: Optional[InventoryItem] = None):
        return f'{self.getName()} Estate Kit'

    def makeItemModel(self, *extraArgs, item: Optional[InventoryItem] = None) -> NodePath:
        """
        Returns a nodepath that represents this item.
        """
        model = loader.loadModel(self.getModelPath())
        model.setScale(self.getModelScale())
        model.flattenLight()  # apply scale so our children dont inherit achondroplasia
        return model

    def createGeomList(self, *extraArgs, item) -> list:
        """
        Creates the geometry for the Estate.
        """
        model = self.getItemModel(*extraArgs, item)
        model.reparentTo(render)
        model.show()
        return [model]

    def cleanupGeom(self, item, geomList: list):
        """
        Cleans up the geometry for the Estate.
        """
        for geom in geomList:
            geom.removeNode()


# The registry dictionary for furniture.
EstateStyleRegistry: Dict[IntEnum, EstateStyleDefinition] = {
    ### Debug Estate Kits ###
    EstateStyleItemType.Debug_TT_Flatgrass_1: EstateStyleDefinition(
        name = 'TT Flatgrass',
        description = 'A beautiful domain of flat grass.',
        modelPath = 'activity/trolley/models/',
        modelName = "cc_m_mg_tag_arena_circle",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR,
    ),
    EstateStyleItemType.Debug_Funny_Rural: EstateStyleDefinition(
        name = 'Funny Rural',
        description = 'Is soo silly',
        modelPath = 'phase_8/models/minigames/',
        modelName = "tag_arena_BR",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR,
    ),
    EstateStyleItemType.Debug_Test_Area_1: EstateStyleDefinition(
        name = 'Test area 1',
        description = 'Is soo silly',
        modelPath = 'areas/test/models/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "cc_m_test_ara_est_ext_scale",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR,
    ),
    EstateStyleItemType.Debug_Terrain_300x300_Uneven: EstateStyleDefinition(
        name = 'terrain 300x300 uneven',
        description = 'Is soo silly',
        modelPath = 'areas/test/models/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "cc_m_test_terrain_300_uneven",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR,
    ),
    EstateStyleItemType.Debug_Terrain_300x300_Flat: EstateStyleDefinition(
        name = 'Test area 300 flat',
        description = 'Is soo silly',
        modelPath = 'areas/test/models/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "cc_m_test_terrain_300_flat",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR,
    ),
    EstateStyleItemType.Debug_Terrain_150x150_Flat: EstateStyleDefinition(
        name = 'cc_m_test_terrain_150_flat',
        description = 'Is soo silly',
        modelPath = 'areas/test/models/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "cc_m_test_terrain_150_flat",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR,
    ),
    EstateStyleItemType.Debug_Terrain_150x150_Uneven: EstateStyleDefinition(
        name = 'cc_m_test_terrain_150_uneven',
        description = 'Is soo silly',
        modelPath = 'areas/test/models/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "cc_m_test_terrain_150_uneven",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR,
    ),
    EstateStyleItemType.Debug_RuralTrack_1: EstateStyleDefinition(
        name = 'Debug_RuralTrack_1',
        description = 'Is soo silly',
        modelPath = 'phase_6/models/karting/',
        doorType = EstateDoorType.DEBUG,
        modelName = "RT_RuralB",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR,
    ),
    EstateStyleItemType.Debug_RuralTrack_2: EstateStyleDefinition(
        name = 'Debug_RuralTrack_2',
        description = 'Is soo silly',
        modelPath = 'phase_6/models/karting/',
        doorType = EstateDoorType.DEBUG,
        modelName = "RT_RuralB2",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR,
    ),
    EstateStyleItemType.Debug_SellbotFactory: EstateStyleDefinition(
        name = 'Debug_SellbotFactory',
        description = 'Is soo silly',
        modelPath = 'phase_9/models/cogHQ/',
        modelName = "SelbotLegFactory",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
    ),
    EstateStyleItemType.Debug_CLOBossRoom: EstateStyleDefinition(
        name = 'Debug_CLOBossRoom',
        description = 'Is soo silly',
        modelPath = 'phase_11/models/lawbotHQ/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "LawbotBossRoom",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.INTERIOR,
    ),
    EstateStyleItemType.Debug_Lawfice: EstateStyleDefinition(
        name = 'Debug_Lawfice',
        description = 'Is soo silly',
        modelPath = 'phase_11/models/lawbotHQ/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "LawficeA",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.INTERIOR,
    ),
    EstateStyleItemType.Debug_OCLOLobby: EstateStyleDefinition(
        name = 'LB_CH_Hard_Lobby',
        description = 'Is soo silly',
        modelPath = 'phase_11/models/lawbotHQ/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "LB_CH_Hard_Lobby",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.INTERIOR,
    ),
    EstateStyleItemType.Debug_Lawfice_Lobby: EstateStyleDefinition(
        name = 'Debug_Lawfice_Lobby',
        description = 'Is soo silly',
        modelPath = 'phase_11/models/lawbotHQ/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "cc_m_ara_lbhq_int_lawfice_lobby",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.INTERIOR,
    ),

    EstateStyleItemType.Debug_BanquetInterior: EstateStyleDefinition(
        name = 'BanquetInterior_1',
        description = 'Is soo silly',
        modelPath = 'phase_12/models/bossbotHQ/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "BanquetInterior_1",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.INTERIOR,
    ),
    EstateStyleItemType.Debug_CEOLobby: EstateStyleDefinition(
        name = 'BossbotLobby',
        description = 'Is soo silly',
        modelPath = 'phase_12/models/bossbotHQ/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = 'door_origin_0',
        modelScale = 0.45,
        modelName = "BossbotLobby",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.INTERIOR,
    ),
    EstateStyleItemType.Debug_TrainStation: EstateStyleDefinition(
        name = 'Debug_TrainStation',
        description = 'Is soo silly',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "station",
        modelNamePrefix = "ara_cashbotHQ_",
        modelPath = "areas/coghq/models/",
        estateKitType = EstateKitType.EXTERIOR,
    ),
    EstateStyleItemType.Exterior_YOTT_Playground: EstateStyleDefinition(
        name = 'Yott Playground',
        description = 'Is soo silly',
        modelPath = 'phase_7/models/neighborhoods/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "olde_toontown",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR,
    ),
    EstateStyleItemType.Exterior_AA_Playground: EstateStyleDefinition(
        name = 'AA Playground',
        description = 'Is soo silly',
        modelPath = 'phase_6/models/neighborhoods/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "acorn_acres",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR,
    ),
    EstateStyleItemType.Exterior_TB_Playground: EstateStyleDefinition(
        name = 'AA the_burrrgh',
        description = 'Is soo silly',
        modelPath = 'phase_8/models/neighborhoods/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "the_burrrgh",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR,
    ),
    EstateStyleItemType.Exterior_DG_TagGame: EstateStyleDefinition(
        name = 'AA tag_arena_DG',
        description = 'Is soo silly',
        modelPath = 'phase_8/models/minigames/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "tag_arena_DG",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR,
    ),

    ### Interior Estate Kits ###
    EstateStyleItemType.Interior_Classic: EstateStyleDefinition(
        name = 'Vintage Interior',
        description = 'The classics never die.',
        modelName = 'default',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        doorOrigin = 'door_origin',
        doorPosHprScale = (-0.20, 0, 0, -90, 0, 0, 0.8, 0.8, 0.8),
        estateKitType = EstateKitType.INTERIOR
    ),

    EstateStyleItemType.Interior_FAASSuite_Lobby: EstateStyleDefinition(
        name = 'Fassuites',
        description = 'Is soo silly',
        modelPath = 'areas/drowsy_dreamland/interiors/models/',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        modelName = "cc_m_ara_fassuite_int_lobby_base",
        modelNamePrefix = "",
        overrideDefaultModelPrefix = True,
        estateKitType = EstateKitType.EXTERIOR
    ),

    ### Exterior Estate Kits ###
    EstateStyleItemType.Exterior_Default: EstateStyleDefinition(
        name = 'Default Exterior Estate Kit',
        description = 'Is soo silly',
        modelName = 'default',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        estateKitType = EstateKitType.EXTERIOR
    ),
    EstateStyleItemType.Exterior_Classic: EstateStyleDefinition(
        name = 'Classic Exterior Estate Kit',
        description = 'Is soo silly',
        modelName = 'default',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        estateKitType = EstateKitType.EXTERIOR

    ),
    EstateStyleItemType.Exterior_AA_Park: EstateStyleDefinition(
        name = 'Exterior_AA_Park',
        description = 'Is soo silly',
        modelName = 'aa',
        doorType = EstateDoorType.CLASSIC_DOUBLE_ROUND_UR,
        estateKitType = EstateKitType.EXTERIOR,

    ),
}
