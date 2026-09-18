"""
This module contains the item data for hats.
"""
from __future__ import annotations
from panda3d.core import NodePath

from toontown.inventory.base.InventoryItem import InventoryItem
from typing import Dict, Optional
from enum import IntEnum, auto

from toontown.inventory.definitions.AccessoryDefinition import AccessoryDefinition
from toontown.inventory.enums.ItemEnums import HatItemType
from toontown.inventory.enums.ItemTags import ItemTag
from toontown.toon.accessories.ToonActorAccessory import ToonActorAccessory
from toontown.toon.accessories.hats.ChainsawConsultantHat import ChainsawConsultantHat
from toontown.toon.accessories.hats.ClashBirthday import ClashBirthdayHat
from toontown.toon.accessories.hats.GhostTophat import GhostTophat
from toontown.toon.accessories.hats.HatFreezeHead import HatFreezeHead
from toontown.toon.accessories.hats.HatHideEars import HatHideEars, OttomanNumberOnePlantHat, Beret
from toontown.toon.accessories.hats.HighRollerHat import HighRollerHat
from toontown.toon.accessories.hats.StormCloudHat import StormCloudHat


class HatClassEnum(IntEnum):
    Default = auto()
    HatHideEars = auto()
    ClashBirthdayHat = auto()
    GhostTophat = auto()
    OttomanNumberOnePlantHat = auto()
    HatFreezeHead = auto()
    ChainsawConsultantHat = auto()
    Beret = auto()
    StormCloudHat = auto()
    HighRollerHat = auto()


baseTexturePath = "cosmetics/"
baseModelPath = "cosmetics/"
textureExtension = ".png"


class HatItemDefinition(AccessoryDefinition):
    """
    The definition structure for hats.
    """

    HatClasses = {
        HatClassEnum.HatHideEars: HatHideEars,
        HatClassEnum.ClashBirthdayHat: ClashBirthdayHat,
        HatClassEnum.GhostTophat: GhostTophat,
        HatClassEnum.OttomanNumberOnePlantHat: OttomanNumberOnePlantHat,
        HatClassEnum.HatFreezeHead: HatFreezeHead,
        HatClassEnum.ChainsawConsultantHat: ChainsawConsultantHat,
        HatClassEnum.Beret: Beret,
        HatClassEnum.StormCloudHat: StormCloudHat,
        HatClassEnum.HighRollerHat: HighRollerHat,
    }

    def __init__(self,
                 modelName,
                 textureName=None,
                 accessoryClass=HatClassEnum.Default,
                 accFileType=('hat', 'hat'),  # cc_t_acc_XXX_
                 accFilePath=('hat', 'hat'),  # cosmetics/XXX/maps/
                 modelPath="",  # Manual overrides
                 texturePath="",
                 **kwargs):
        super().__init__(**kwargs)
        self.modelName = modelName
        self.textureName = textureName
        self.accessoryClass = accessoryClass

        modelType = "a" if issubclass(self.getAccessoryClass(), ToonActorAccessory) else "m"

        mdlFileType, texFileType = accFileType
        mdlFilePath, texFilePath = accFilePath

        self.baseModelPrefix = f"cc_{modelType}_acc_{mdlFileType}_"
        self.baseTexturePrefix = f"cc_t_acc_{texFileType}_"

        # If we passed a custom model/texture path, we can just use that one
        # But, if not, we can just define it ourselves.
        self.texturePath = texturePath if texturePath else f"{baseTexturePath}{texFilePath}/maps/"
        self.modelPath = modelPath if modelPath else f"{baseModelPath}{mdlFilePath}/models/"

    def getItemTypeName(self):
        return 'Head'

    def getModelPath(self):
        if not self.modelName:
            return None
        return f"{self.modelPath}{self.baseModelPrefix}{self.modelName}"

    def getTexturePath(self):
        if not self.textureName:
            return None
        return f"{self.texturePath}{self.baseTexturePrefix}{self.textureName}{textureExtension}"

    def getAccessoryClass(self):
        return self.HatClasses.get(self.accessoryClass, super().getAccessoryClass())

    def getTags(self, item: 'InventoryItem') -> set[ItemTag]:
        tags = super().getTags(item)
        tags.add(ItemTag.Hat)
        return tags


# The registry dictionary for hats.
HatRegistry: Dict[IntEnum, HatItemDefinition] = {
    HatItemType.Hat_BaseballCap_Classic_Green: HatItemDefinition(
        name="Green Baseball Cap",
        description='Todo!',
        modelName='baseball_classic',
        textureName='baseball_classic_green',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Safari_Classic_Beige: HatItemDefinition(
        name="Beige Safari Hat",
        description='Todo!',
        modelName='safari_classic',
        textureName='safari_classic_beige',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Safari_Classic_Brown: HatItemDefinition(
        name="Brown Safari Hat",
        description='Todo!',
        modelName='safari_classic',
        textureName='safari_classic_brown',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Safari_Classic_Green: HatItemDefinition(
        name="Green Safari Hat",
        description='Todo!',
        modelName='safari_classic',
        textureName='safari_classic_green',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Hearts_Classic_Pink: HatItemDefinition(
        name="Pink Heart",
        description='Todo!',
        modelName='headband_heart_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Hearts_Classic_Yellow: HatItemDefinition(
        name="Yellow Heart",
        description='Todo!',
        modelName='headband_heart_classic',
        textureName='headband_heart_classic_yellow',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Top_Classic_Black: HatItemDefinition(
        name="Black Top Hat",
        description='Todo!',
        modelName='tophat_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Top_Classic_Blue: HatItemDefinition(
        name="Blue Top Hat",
        description='Todo!',
        modelName='tophat_classic',
        textureName='tophat_classic_blue_squares',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Gag_Classic_Anvil: HatItemDefinition(
        name="Anvil Hat",
        description='Right out of the forges from Ye Olde Toontowne!',
        modelName='gag_anvil_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Gag_Classic_FlowerPot: HatItemDefinition(
        name="Flower Hat",
        description='Todo!',
        modelName='gag_flowerpot_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Gag_Classic_Sandbag: HatItemDefinition(
        name="Sandbag Hat",
        description='Filled on the shores of Barnacle Boatyard!',
        modelName='gag_sandbag_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Gag_Classic_BigWeight: HatItemDefinition(
        name="Weight Hat",
        description='A gift from Franz himself!',
        modelName='gag_weight_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Fez_Classic: HatItemDefinition(
        name="Fez Hat",
        description='Todo!',
        modelName='fez_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Golf_Classic: HatItemDefinition(
        name="Golf Hat",
        description='Todo!',
        modelName='golf_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Party_Classic_Blue: HatItemDefinition(
        name="Party Hat",
        description='Todo!',
        modelName='party_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Party_Classic_Anniversary: HatItemDefinition(
        name="Toon Party Hat",
        description='Todo!',
        modelName='party_classic',
        textureName='party_classic_anniversary10',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Fancy_Classic: HatItemDefinition(
        name="Fancy Hat",
        description='Todo!',
        modelName='pillbox_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Classic: HatItemDefinition(
        name="Crown",
        description='Todo!',
        modelName='crown_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_BaseballCap_Classic_Blue: HatItemDefinition(
        name="Blue Baseball Cap",
        description='Todo!',
        modelName='baseball_classic',
        textureName='baseball_classic_blue',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_BaseballCap_Classic_Orange: HatItemDefinition(
        name="Orange Baseball Cap",
        description='Todo!',
        modelName='baseball_classic',
        textureName='baseball_classic_orange',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Cowboy_Classic: HatItemDefinition(
        name="Cowboy Hat",
        description='Todo!',
        modelName='cowboy_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Pirate_Classic: HatItemDefinition(
        name="Pirate Hat",
        description='Todo!',
        modelName='pirate_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Propeller_Classic: HatItemDefinition(
        name="Propeller Hat",
        description='Todo!',
        modelName='propeller_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Fishing_Classic: HatItemDefinition(
        name="Fishing Hat",
        description='Todo!',
        modelName='fishing_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Sombrero_Classic: HatItemDefinition(
        name="Sombrero Hat",
        description='Todo!',
        modelName='sombrero_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Straw_Classic: HatItemDefinition(
        name="Straw Hat",
        description='Todo!',
        modelName='straw_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Antenna_Spider_Classic: HatItemDefinition(
        name="Bug Antenna",
        description='Todo!',
        modelName='antenna_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hair_Beehive_Classic: HatItemDefinition(
        name="Beehive Hairdo",
        description='You\'ll be the buzz around town!',
        modelName='hair_beehive_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Bowler_Classic: HatItemDefinition(
        name="Bowler Hat",
        description='Todo!',
        modelName='bowler_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Chef_Classic: HatItemDefinition(
        name="Chef Hat",
        description='Todo!',
        modelName='chef_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Detective_Classic: HatItemDefinition(
        name="Detective Hat",
        description='Todo!',
        modelName='detective_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Feathers_Classic: HatItemDefinition(
        name="Fancy Feathers Hat",
        description='Todo!',
        modelName='headband_feathers_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Fedora_Classic: HatItemDefinition(
        name="Hat_Fedora_Classic",
        description='Todo!',
        modelName='fedora_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Shako_Classic: HatItemDefinition(
        name="Superficial Shako Hat",
        description='Todo!',
        modelName='shako_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Sweatband: HatItemDefinition(
        name="Headband_Sweatband",
        description='Todo!',
        modelName='headband_sweatband',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hair_Pompadour_Classic: HatItemDefinition(
        name="Pompadour Hairdo",
        description='Todo!',
        modelName='hair_pompador_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Archer_Classic: HatItemDefinition(
        name="Archer Hat",
        description='Todo!',
        modelName='robinhood_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Helmet_Roman_Classic: HatItemDefinition(
        name="Roman Helmet",
        description='Todo!',
        modelName='helmet_roman_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Antenna_Webbed_Classic: HatItemDefinition(
        name="Webbed Bug Antenna",
        description='Todo!',
        modelName='antenna_spider_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Tiara_Pink: HatItemDefinition(
        name="Tiara",
        description='Todo!',
        modelName='crown_tiara_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Viking_Classic: HatItemDefinition(
        name="Viking Helmet",
        description='Todo!',
        modelName='helmet_viking_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Witch_Classic: HatItemDefinition(
        name="Witch Hat",
        description='Todo!',
        modelName='witch_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Wizard_Enchanted_Stars_Purple: HatItemDefinition(
        name="Wizard Hat",
        description='Todo!',
        modelName='wizard_enchanted',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Helmet_Conquistador_Classic: HatItemDefinition(
        name="Conquistador Helmet",
        description='Todo!',
        modelName='helmet_conquistador_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Helmet_Firefighter_Classic: HatItemDefinition(
        name="Firefighter Helmet",
        description='Todo!',
        modelName='firefighter_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_TinFoil_Classic: HatItemDefinition(
        name="Anti-Cog Control Hat",
        description='Todo!',
        modelName='foil_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Helmet_Miner_Classic: HatItemDefinition(
        name="Miner Hat",
        description='Todo!',
        modelName='miner_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Napoleon_Classic: HatItemDefinition(
        name="Napoleon Hat",
        description='Todo!',
        modelName='napoleon_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Pilot_Classic: HatItemDefinition(
        name="Pilot Cap",
        description='Todo!',
        modelName='pilot_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Cop_Classic: HatItemDefinition(
        name="Cop Hat",
        description='Todo!',
        modelName='police_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hair_Wig_Classic_Rainbow: HatItemDefinition(
        name="Rainbow Wacky Wig",
        description='Todo!',
        modelName='hair_afro_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_BaseballCap_Classic_Yellow: HatItemDefinition(
        name="Yellow Baseball Cap",
        description='Todo!',
        modelName='baseball_classic',
        textureName='baseball_classic_yellow',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_BaseballCap_Classic_Red: HatItemDefinition(
        name="Red Baseball Cap",
        description='Todo!',
        modelName='baseball_classic',
        textureName='baseball_classic_red',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_BaseballCap_Classic_Aqua: HatItemDefinition(
        name="Aqua Baseball Cap",
        description='Todo!',
        modelName='baseball_classic',
        textureName='baseball_classic_teal',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Sailor_Classic: HatItemDefinition(
        name="Sailor Hat",
        description='Todo!',
        modelName='paper_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Samba_Classic: HatItemDefinition(
        name="Samba Hat",
        description='Todo!',
        modelName='fruits_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Bobby_Classic: HatItemDefinition(
        name="Bobby Hat",
        description='Todo!',
        modelName='bobby_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Jughead_Classic: HatItemDefinition(
        name="Jester Hat",
        description='Todo!',
        modelName='jughead_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_BaseballCap_Classic_Purple: HatItemDefinition(
        name="Purple Baseball Cap",
        description='Todo!',
        modelName='baseball_classic',
        textureName='baseball_classic_purple',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Winter_Classic: HatItemDefinition(
        name="Winter Hat",
        description='Todo!',
        modelName='winter_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Toonosaur_Classic: HatItemDefinition(
        name="Toonosaur Hat",
        description='Todo!',
        modelName='dinosaur_classic',
        textureName=None,
        accessoryClass=HatClassEnum.HatHideEars
    ),
    HatItemType.Hat_Jamboree_Classic: HatItemDefinition(
        name="Jamboree Hat",
        description='Todo!',
        modelName='band_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Bird_Classic: HatItemDefinition(
        name="Bird Hat",
        description='Todo!',
        modelName='birdnest_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Classic_Pink: HatItemDefinition(
        name="Pink Bow",
        description='Todo!',
        modelName='bow_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Classic_RedPolkaLg: HatItemDefinition(
        name="Red Bow",
        description='Todo!',
        modelName='bow_classic',
        textureName='bow_classic_polka_lg_red',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Classic_PurplePolkaSm: HatItemDefinition(
        name="Purple Bow",
        description='Todo!',
        modelName='bow_classic',
        textureName='bow_classic_polka_sm_purple',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Sun_Classic: HatItemDefinition(
        name="Sun Hat",
        description='Todo!',
        modelName='sun_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Classic_Yellow: HatItemDefinition(
        name="Yellow Bow",
        description='Todo!',
        modelName='bow_classic',
        textureName='bow_classic_col_yellow',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Classic_BlueChecker: HatItemDefinition(
        name="Checker Bow",
        description='Todo!',
        modelName='bow_classic',
        textureName='bow_classic_checker_blue',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Classic_Red: HatItemDefinition(
        name="Light Red Bow",
        description='Todo!',
        modelName='bow_classic',
        textureName='bow_classic_col_red',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Classic_Rainbow: HatItemDefinition(
        name="Rainbow Bow",
        description='Todo!',
        modelName='bow_classic',
        textureName='bow_classic_col_rainbow',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Princess_Classic: HatItemDefinition(
        name="Princess Hat",
        description='Todo!',
        modelName='princess_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Classic_PinkPolka: HatItemDefinition(
        name="Pink Dots Bow",
        description='Todo!',
        modelName='bow_classic',
        textureName='bow_classic_polka_md_pink',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Classic_GreenChecker: HatItemDefinition(
        name="Green Checker Bow",
        description='Todo!',
        modelName='bow_classic',
        textureName='bow_classic_checker_yellow',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Pirate_Bandana_Classic: HatItemDefinition(
        name="Bandana",
        description='Todo!',
        modelName='bandana_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Overhead_SpaceHelmet: HatItemDefinition(
        name="Moon Suit Helmet",
        description='Todo!',
        modelName='over_helmet_space',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Bat: HatItemDefinition(
        name="Bat Bow",
        description='Todo!',
        modelName='bow_bat',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Cauldron: HatItemDefinition(
        name="Cauldron Hat",
        description='Todo!',
        modelName='cauldron',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_ElectricBolts: HatItemDefinition(
        name="Electric Bolts",
        description='Todo!',
        modelName='headband_bolts',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_PumpkinBucket: HatItemDefinition(
        name="Pumpkin Bucket Hat",
        description='Todo!',
        modelName='bucket_pumpkin',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Scarecrow: HatItemDefinition(
        name="Scarecrow Hat",
        description='Todo!',
        modelName='scarecrow',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Wizard_Enchanted_Stars_Black: HatItemDefinition(
        name="Black Wizard Hat",
        description='Todo!',
        modelName='wizard_enchanted',
        textureName='wizard_enchanted_stars_black',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Wizard_Enchanted_Stars_Pink: HatItemDefinition(
        name="Pink Wizard Hat",
        description='Todo!',
        modelName='wizard_enchanted',
        textureName='wizard_enchanted_stars_pink',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Wizard_Enchanted_Stars_Red: HatItemDefinition(
        name="Red Wizard Hat",
        description='Todo!',
        modelName='wizard_enchanted',
        textureName='wizard_enchanted_stars_red',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Wizard_Enchanted_Stars_Green: HatItemDefinition(
        name="Green Wizard Hat",
        description='Todo!',
        modelName='wizard_enchanted',
        textureName='wizard_enchanted_stars_green',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Wizard_Enchanted_Stars_Blue: HatItemDefinition(
        name="Blue Wizard Hat",
        description='Todo!',
        modelName='wizard_enchanted',
        textureName='wizard_enchanted_stars_blue',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Frankenstein: HatItemDefinition(
        name="Frankenstein Head",
        description='Todo!',
        modelName='frankenstein_classic',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Alchemist_Goggles: HatItemDefinition(
        name="Alchemist Goggles",
        description='Todo!',
        modelName='headband_alchemist',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Classic_Black: HatItemDefinition(
        name="Wonderland Bow",
        description='Todo!',
        modelName='bow_classic',
        textureName='bow_classic_col_black',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Beanie_Bobble_Blue: HatItemDefinition(
        name="Blue Bobble Hat",
        description='Todo!',
        modelName='beanie_winter',
        textureName='beanie_winter_storm',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Beanie_Bobble_Green: HatItemDefinition(
        name="Green Bobble Hat",
        description='Todo!',
        modelName = 'beanie_winter',
        textureName='beanie_winter_green',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Beanie_Bobble_Grey: HatItemDefinition(
        name="Gray Bobble Hat",
        description='Todo!',
        modelName = 'beanie_winter',
        textureName='beanie_winter_gray',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Beanie_Bobble_Pink: HatItemDefinition(
        name="Pink Bobble Hat",
        description='Todo!',
        modelName = 'beanie_winter',
        textureName='beanie_winter_pink',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Beanie_Bobble_Rainbow: HatItemDefinition(
        name="Rainbow Bobble Hat",
        description='Todo!',
        modelName = 'beanie_winter',
        textureName='beanie_winter_rainbow',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Beanie_Bobble_Red: HatItemDefinition(
        name="Red Bobble Hat",
        description='Todo!',
        modelName = 'beanie_winter',
        textureName='beanie_winter_red',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Santa_Red: HatItemDefinition(
        name="Classic Santa Hat",
        description='Todo!',
        modelName='winter_santa',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Santa_Rainbow: HatItemDefinition(
        name="Rainbow Santa Hat",
        description='Todo!',
        modelName='winter_santa',
        textureName='winter_santa_col_rainbow',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Santa_Green: HatItemDefinition(
        name="Green Santa Hat",
        description='Todo!',
        modelName='winter_santa',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Elf_Red: HatItemDefinition(
        name="Jolly Red Elf Hat",
        description='Todo!',
        modelName='elf',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Elf_Green: HatItemDefinition(
        name = "Jolly Green Elf Hat",
        description = 'Todo!',
        modelName = 'elf',
        textureName = 'elf_redGreen',
        accessoryClass = HatClassEnum.Default
    ),
    HatItemType.Hat_Star: HatItemDefinition(
        name="Tree Topper",
        description='Todo!',
        modelName='star',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Soldier_Humble: HatItemDefinition(
        name="Humble Tin Soldier Hat",
        description='Todo!',
        modelName='soldier_humble',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Soldier_Regal: HatItemDefinition(
        name="Regal Tin Soldier Hat",
        description='Todo!',
        modelName='soldier_regal',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Soldier_Tradi: HatItemDefinition(
        name="Traditional Tin Soldier Hat",
        description='Todo!',
        modelName='soldier_tradi',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Ragdoll_Humble: HatItemDefinition(
        name="Humble Ragdoll Hat",
        description='Todo!',
        modelName='ragdoll_humble',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Ragdoll_Tradi: HatItemDefinition(
        name="Traditional Ragdoll Hat",
        description='Todo!',
        modelName='ragdoll_tradi',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Ragdoll_Regal: HatItemDefinition(
        name="Regal Ragdoll Hat",
        description='Todo!',
        modelName='ragdoll_regal',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Antlers: HatItemDefinition(
        name="Headband_Antlers",
        description='Todo!',
        modelName='headband_antlers_small',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Beanie_Doe_Yellow: HatItemDefinition(
        name="Yellow Beanie",
        description='Perfect for The Brrrgh!',
        modelName='beanie_doe',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Books_Webster: HatItemDefinition(
        name="Book Stack",
        description='Books! Pete would be so proud! Maybe..?',
        modelName='books_stack',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Umbrella: HatItemDefinition(
        name="Umbrella Hat",
        description='Todo!',
        modelName='umbrella',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Aviator: HatItemDefinition(
        name="Aviator Cap",
        description='Sky Clan, here we come!',
        modelName='helmet_aviator',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Top_Cake_Anniversary: HatItemDefinition(
        name="The Clash Bash",
        description='Todo!',
        modelName='top_cake_ani',
        textureName=None,
        accessoryClass=HatClassEnum.ClashBirthdayHat
    ),
    HatItemType.Hat_Outback_Slouch: HatItemDefinition(
        name="Outback Slouch Hat",
        description='Perfect for an outback adventure!',
        modelName='slouch',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Outback_Cork: HatItemDefinition(
        name="Outback Cork Hat",
        description='Quit whining about it!',
        modelName='cork',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Outback_Gecko: HatItemDefinition(
        name="Outback Gecko Hat",
        description='Friend included!',
        modelName='gecko',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Alien: HatItemDefinition(
        name="Alien Hat",
        description='Todo!',
        modelName='alien',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Top_Halo_White: HatItemDefinition(
        name="Halo",
        description='Todo!',
        modelName='top_halo',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Top_Halo_Blue: HatItemDefinition(
        name="Blue Halo",
        description='Todo!',
        modelName='top_halo',
        textureName='top_halo_blue',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Top_Halo_Green: HatItemDefinition(
        name="Green Halo",
        description='Todo!',
        modelName='top_halo',
        textureName='top_halo_green',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Top_Halo_Orange: HatItemDefinition(
        name="Orange Halo",
        description='Todo!',
        modelName='top_halo',
        textureName='top_halo_orange',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Top_Halo_Purple: HatItemDefinition(
        name="Purple Halo",
        description='Todo!',
        modelName='top_halo',
        textureName='top_halo_purple',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Top_Halo_Red: HatItemDefinition(
        name="Red Halo",
        description='Todo!',
        modelName='top_halo',
        textureName='top_halo_red',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Horns_Black: HatItemDefinition(
        name="Horns",
        description='Todo!',
        modelName='headband_horns',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Horns_Blue: HatItemDefinition(
        name="Blue Horns",
        description='Todo!',
        modelName='headband_horns',
        textureName='headband_horns_blue',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Horns_Green: HatItemDefinition(
        name="Green Horns",
        description='Todo!',
        modelName='headband_horns',
        textureName='headband_horns_green',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Horns_Orange: HatItemDefinition(
        name="Orange Horns",
        description='Todo!',
        modelName='headband_horns',
        textureName='headband_horns_orange',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Horns_Purple: HatItemDefinition(
        name="Purple Horns",
        description='Todo!',
        modelName='headband_horns',
        textureName='headband_horns_purple',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Horns_Red: HatItemDefinition(
        name="Red Horns",
        description='Todo!',
        modelName='headband_horns',
        textureName='headband_horns_red',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hood_Riding: HatItemDefinition(
        name="Riding Hood",
        description='Todo!',
        modelName='hood_riding',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Robophones: HatItemDefinition(
        name="Retro Headband_Robophones",
        description='Todo!',
        modelName='headphones_robo',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Nurse: HatItemDefinition(
        name="Nurse Hat",
        description='Laugh your way to good laff!',
        modelName='paper_classic',
        textureName='paper_classic_nurse_blue',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_SpinDoctor: HatItemDefinition(
        name="Doctor's Headband",
        description='Tickle feathers can cure anything!',
        modelName='headband_mirror',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Classic_CandyCorn: HatItemDefinition(
        name="Candy Corn Bow",
        description='Todo!',
        modelName='bow_classic',
        textureName='bow_classic_candycorn',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Top_Halo_Yellow: HatItemDefinition(
        name="Golden Halo",
        description='Todo!',
        modelName='top_halo',
        textureName='top_halo_yellow',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Horns_Yellow: HatItemDefinition(
        name="Golden Horns",
        description='Todo!',
        modelName='headband_horns',
        textureName='headband_horns_yellow',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Gag_BowlingBall: HatItemDefinition(
        name="Bowling Ball Hat",
        description='STRIKE!',
        modelName='gag_bowlingball',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Gag_FruitPie: HatItemDefinition(
        name="Fruit Pie Hat",
        description='Tastes good, too!',
        modelName='gag_fruitpie',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Ragdoll_Homemade: HatItemDefinition(
        name="Homemade Ragdoll Hat",
        description='Todo!',
        modelName='ragdoll_homemade',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Helmet_Ski_Vintage: HatItemDefinition(
        name="Ski Helmet",
        description='Todo!',
        modelName='helmet_ski',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Helmet_Ski_Blue: HatItemDefinition(
        name="Blue Ski Helmet",
        description='Todo!',
        modelName='helmet_ski',
        textureName='helmet_ski_col_blue',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Helmet_Ski_Green: HatItemDefinition(
        name="Green Ski Helmet",
        description='Todo!',
        modelName='helmet_ski',
        textureName='helmet_ski_col_green',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Helmet_Ski_Gray: HatItemDefinition(
        name="Gray Ski Helmet",
        description='Todo!',
        modelName='helmet_ski',
        textureName='helmet_ski_col_gray',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Helmet_Ski_Pink: HatItemDefinition(
        name="Pink Ski Helmet",
        description='Todo!',
        modelName='helmet_ski',
        textureName='helmet_ski_col_pink',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Helmet_Ski_Rainbow: HatItemDefinition(
        name="Rainbow Ski Helmet",
        description='Todo!',
        modelName='helmet_ski',
        textureName='helmet_ski_col_rainbow',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Helmet_Ski_Red: HatItemDefinition(
        name="Red Ski Helmet",
        description='Todo!',
        modelName='helmet_ski',
        textureName='helmet_ski_col_red',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Snowman: HatItemDefinition(
        name="Snowman Hat",
        description='Todo!',
        modelName='snowman',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Soldier_Homemade: HatItemDefinition(
        name="Homemade Soldier Hat",
        description='Todo!',
        modelName='soldier_homemade',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Gag_TV: HatItemDefinition(
        name="Broken TV Hat",
        description='Did you try plugging it in again..?',
        modelName='gag_tv',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Fedora_Classic_AgentSeven: HatItemDefinition(
        name="Agent Seven's Hat_Fedora_Classic",
        description='Todo!',
        modelName='fedora_classic',
        textureName='fedora_classic_agent7',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Top_Lucky: HatItemDefinition(
        name="St. Pat's Lucky Tophat",
        description='Todo!',
        modelName='tophat_lucky',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Top_Tartan: HatItemDefinition(
        name="St. Pat's Tartan Tophat",
        description='Todo!',
        modelName='tophat_tartan',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_LuckyClover: HatItemDefinition(
        name="St. Pat's Clover Headband",
        description='Todo!',
        modelName='headband_lucky_clover',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_LuckyClip: HatItemDefinition(
        name="St. Pat's Clover Hairclip",
        description='Todo!',
        modelName='headband_lucky_clip',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_RainbowPhones: HatItemDefinition(
        name="Triple Rainbow Headphones",
        description='Triple rainbow! What does it mean?',
        modelName='headphones_rainbow',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Bowler_Clown: HatItemDefinition(
        name="Clown Hat",
        description='Todo!',
        modelName='bowler_clown',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Jester_Red: HatItemDefinition(
        name="Jester Hat",
        description='Popularized in Ye Olde Toontowne!',
        modelName='jester',
        textureName='jester_red',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Jester_Black: HatItemDefinition(
        name="Black Jester Hat",
        description='Popularized in Ye Olde Toontowne!',
        modelName='jester',
        textureName='jester_black',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Beanie_Easter: HatItemDefinition(
        name="Easter 2020 Beanie",
        description='Todo!',
        modelName='beanie_easter',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Skelecog_Blue: HatItemDefinition(
        name="Witness Stand-In Hat",
        description='Todo!',
        modelName='skelecog',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Diploma: HatItemDefinition(
        name="Wing Hairbow_Diploma Bow",
        description='Todo!',
        modelName='bow_diploma',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Grill: HatItemDefinition(
        name="Hat_Grill Hat",
        description='Todo!',
        modelName='grill',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Leaf_Autumn: HatItemDefinition(
        name="Leaf Hat",
        description='Todo!',
        modelName='leaf',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Candle: HatItemDefinition(
        name="Toonsmas Past Candle",
        description='Todo!',
        modelName='candle_past',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Present: HatItemDefinition(
        name="Toonsmas Present Headband",
        description='Todo!',
        modelName='crown_holly',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hood_Future: HatItemDefinition(
        name="Toonsmas Future Hood",
        description='Todo!',
        modelName='hood_xmas_future',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Plant_Fern: HatItemDefinition(
        name="Plant Hat",
        description='Todo!',
        modelName='plant_fern',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Fancy_Grayscale: HatItemDefinition(
        name="Gray Newstoon Bow",
        description='Todo!',
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_GhostlyGibus: HatItemDefinition(
        name="Ghastly Tophat",
        description='Todo!',
        modelName='gibus',
        textureName=None,
        accessoryClass=HatClassEnum.GhostTophat
    ),
    HatItemType.Hat_Plant_NumberOne: HatItemDefinition(
        name="#1 Hat",
        description='Todo!',
        modelName='drink_planter',
        textureName=None,
        accessoryClass=HatClassEnum.OttomanNumberOnePlantHat
    ),
    HatItemType.Hairbow_Classic_BluePolkaSm: HatItemDefinition(
        name="Blue Ribbon",
        description='Todo!',
        modelName='bow_classic',
        textureName='bow_classic_polka_sm_blue',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Headband_Bandana_Deluxe: HatItemDefinition(
        name="Deluxe Bandana",
        description='Todo!',
        modelName='headband_bandana',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hair_Brovinci: HatItemDefinition(
        name="Bro's Hair",
        description='Todo!',
        modelName='hair_bro',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Overhead_Icecube: HatItemDefinition(
        name="Brain Freeze",
        description='Todo!',
        modelName='over_icecube',
        textureName=None,
        accessoryClass=HatClassEnum.HatFreezeHead
    ),
    HatItemType.Hat_SmartCap: HatItemDefinition(
        name="Smart Cap",
        description='Todo!',
        modelName='grad',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Beanie_Clownfish: HatItemDefinition(
        name="Clownfish Beanie",
        description='Fills your head with jokes!',
        modelName='beanie_clownfish',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Gag_BananaPeel: HatItemDefinition(
        name="Banana Peel Hat",
        description='Don\'t slip!',
        modelName='gag_banana',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Helmet_WingSuit: HatItemDefinition(
        name="Wingsuit Helmet",
        description='It might allow you to fly... not Loony Labs certified.',
        modelName='helmet_wingsuit',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Engineer_Trolley: HatItemDefinition(
        name="Trolley Engineer Cap",
        description='All aboard!',
        modelName='engineer_trolley',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Donut_Pink: HatItemDefinition(
        name="Pink Donut",
        description='With sprinkles on top, please!',
        modelName='donut',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Donut_Blue: HatItemDefinition(
        name="Blue Donut",
        description='With sprinkles on top, please!',
        modelName='donut',
        textureName='donut_blue',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Donut_Chocolate: HatItemDefinition(
        name="Chocolate Donut",
        description='With sprinkles on top, please!',
        modelName='donut',
        textureName='donut_chocolate',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Donut_Lemon: HatItemDefinition(
        name="Lemon Donut",
        description='With sprinkles on top, please!',
        modelName='donut',
        textureName='donut_lemon',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Donut_Vanilla: HatItemDefinition(
        name="Vanilla Donut",
        description='With sprinkles on top, please!',
        modelName='donut',
        textureName='donut_vanilla',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Beret_Cruller: HatItemDefinition(
        name="Cruller Beret",
        description='Hold the sprinkles, please.',
        modelName='beret_cruller',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Flower_White: HatItemDefinition(
        name="White Flower Crown",
        description='Daffodil Gardens specialty!',
        modelName='crown_flower',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Flower_Blue: HatItemDefinition(
        name="Blue Flower Crown",
        description='Daffodil Gardens specialty!',
        modelName='crown_flower',
        textureName='crown_flower_blue',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Flower_Cyan: HatItemDefinition(
        name="Cyan Flower Crown",
        description='Daffodil Gardens specialty!',
        modelName='crown_flower',
        textureName='crown_flower_cyan',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Flower_Cyanpurple: HatItemDefinition(
        name="Purple Flower Crown",
        description='Daffodil Gardens specialty!',
        modelName='crown_flower',
        textureName='crown_flower_cyanpurple',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Flower_Green: HatItemDefinition(
        name="Green Flower Crown",
        description='Daffodil Gardens specialty!',
        modelName='crown_flower',
        textureName='crown_flower_green',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Flower_Orange: HatItemDefinition(
        name="Orange Flower Crown",
        description='Daffodil Gardens specialty!',
        modelName='crown_flower',
        textureName='crown_flower_orange',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Flower_Orangepink: HatItemDefinition(
        name="Orangepink Flower Crown",
        description='Daffodil Gardens specialty!',
        modelName='crown_flower',
        textureName='crown_flower_orangepink',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Flower_Pink: HatItemDefinition(
        name="Pink Flower Crown",
        description='Daffodil Gardens specialty!',
        modelName='crown_flower',
        textureName='crown_flower_pink',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Flower_Pinkblue: HatItemDefinition(
        name="Pinkblue Flower Crown",
        description='Daffodil Gardens specialty!',
        modelName='crown_flower',
        textureName='crown_flower_pinkblue',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Flower_Purple: HatItemDefinition(
        name="Purple Flower Crown",
        description='Daffodil Gardens specialty!',
        modelName='crown_flower',
        textureName='crown_flower_purple',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Flower_Red: HatItemDefinition(
        name="Red Flower Crown",
        description='Daffodil Gardens specialty!',
        modelName='crown_flower',
        textureName='crown_flower_red',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Flower_Redyellow: HatItemDefinition(
        name="Redyellow Flower Crown",
        description='Daffodil Gardens specialty!',
        modelName='crown_flower',
        textureName='crown_flower_redyellow',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Flower_Yellow: HatItemDefinition(
        name="Yellow Flower Crown",
        description='Daffodil Gardens specialty!',
        modelName='crown_flower',
        textureName='crown_flower_yellow',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Rose_White: HatItemDefinition(
        name="White Rose Crown",
        description='Picked right off the bouquet!',
        modelName='crown_rose',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Rose_Blue: HatItemDefinition(
        name="Blue Rose Crown",
        description='Picked right off the bouquet!',
        modelName='crown_rose',
        textureName='crown_rose_blue',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Rose_Cyan: HatItemDefinition(
        name="Cyan Rose Crown",
        description='Picked right off the bouquet!',
        modelName='crown_rose',
        textureName='crown_rose_cyan',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Rose_Green: HatItemDefinition(
        name="Green Rose Crown",
        description='Picked right off the bouquet!',
        modelName='crown_rose',
        textureName='crown_rose_green',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Rose_Orange: HatItemDefinition(
        name="Orange Rose Crown",
        description='Picked right off the bouquet!',
        modelName='crown_rose',
        textureName='crown_rose_orange',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Rose_Pink: HatItemDefinition(
        name="Pink Rose Crown",
        description='Picked right off the bouquet!',
        modelName='crown_rose',
        textureName='crown_rose_pink',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Rose_Purple: HatItemDefinition(
        name="Purple Rose Crown",
        description='Picked right off the bouquet!',
        modelName='crown_rose',
        textureName='crown_rose_purple',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Rose_Red: HatItemDefinition(
        name="Red Rose Crown",
        description='Picked right off the bouquet!',
        modelName='crown_rose',
        textureName='crown_rose_red',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Rose_Yellow: HatItemDefinition(
        name="Yellow Rose Crown",
        description='Picked right off the bouquet!',
        modelName='crown_rose',
        textureName='crown_rose_yellow',
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Chainsaw: HatItemDefinition(
        name="Chainsaw Consultant's Hat",
        description='Todo!',
        modelName='chainsaw',
        textureName=None,
        accessoryClass=HatClassEnum.ChainsawConsultantHat
    ),
    HatItemType.Hat_Multislacker: HatItemDefinition(
        name="Multislacker's Hat",
        description='Todo!',
        modelName='multislacker',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Treekiller: HatItemDefinition(
        name="Stump Hat",
        description='Todo!',
        modelName='helmet_treestump',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Featherbedder: HatItemDefinition(
        name="Feather Unibrow",
        description='Todo!',
        modelName = 'brow_fbedder',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_NightCap: HatItemDefinition(
        name="Sleepwalker Nightcap",
        description='Sleep tight!',
        modelName='nightcap',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Beret_Simple_Black: HatItemDefinition(
        name="Beret",
        description='Un brush and un beret.',
        modelName='beret',
        textureName=None,
        accessoryClass=HatClassEnum.Beret
    ),
    HatItemType.Overhead_Gumball: HatItemDefinition(
        name="Gumball Machine Hat",
        description='Fits like a... gumball machine?',
        modelName='over_gumball',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Crown_Card: HatItemDefinition(
        name="Card Suit Crown",
        description='Raise the stakes!',
        modelName='crown_card',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Top_Card: HatItemDefinition(
        name="Card Suit Hat",
        description='Raise the stakes!',
        modelName='tophat_card',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Butter: HatItemDefinition(
        name="Butter Hat",
        description='Hat with the \1TextTitle\1Butter.\2',
        modelName='butter',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Top_Raincloud: HatItemDefinition(
        name="Storm Cloud",
        description='Todo!',
        modelName='top_cloud_rain',
        textureName=None,
        accessoryClass=HatClassEnum.StormCloudHat
    ),
    HatItemType.Hairbow_Ribbon_Red: HatItemDefinition(
        name="Hairbow",
        description='Classy and classic!',
        modelName="bow_hair",
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Firestarter: HatItemDefinition(
        name="Firestarter Helmet",
        description='Todo!',
        modelName='firestarter',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hat_Beret_Painter: HatItemDefinition(
        name="Painter's Beret",
        description='Paint not included.',
        modelName='beret_painter',
        textureName=None,
        accessoryClass=HatClassEnum.Default
    ),
    HatItemType.Hairbow_Ribbon_Blue: HatItemDefinition(
        name="Blue Ribbon Hairbow",
        description="Classy and classic!",
        modelName="bow_hair",
        textureName="bow_hair_blue",
    ),
    HatItemType.Hairbow_Ribbon_Brown: HatItemDefinition(
        name="Brown Ribbon Hairbow",
        description="Classy and classic!",
        modelName="bow_hair",
        textureName="bow_hair_brown",
    ),
    HatItemType.Hairbow_Ribbon_Green: HatItemDefinition(
        name="Green Ribbon Hairbow",
        description="Classy and classic!",
        modelName="bow_hair",
        textureName="bow_hair_green",
    ),
    HatItemType.Hairbow_Ribbon_Orange: HatItemDefinition(
        name="Orange Ribbon Hairbow",
        description="Classy and classic!",
        modelName="bow_hair",
        textureName="bow_hair_orange",
    ),
    HatItemType.Hairbow_Ribbon_Pink: HatItemDefinition(
        name="Pink Ribbon Hairbow",
        description="Classy and classic!",
        modelName="bow_hair",
        textureName="bow_hair_pink",
    ),
    HatItemType.Hairbow_Ribbon_Purple: HatItemDefinition(
        name="Purple Ribbon Hairbow",
        description="Classy and classic!",
        modelName="bow_hair",
        textureName="bow_hair_purple",
    ),
    HatItemType.Hairbow_Ribbon_Rainbow: HatItemDefinition(
        name="Rainbow Ribbon Hairbow",
        description="Classy, classic, and chromatic!",
        modelName="bow_hair",
        textureName="bow_hair_rainbow",
    ),
    HatItemType.Hat_Witchhunter: HatItemDefinition(
        name="Caddish Chapeau",
        description="No Description",
        modelName="witchhunter",
    ),
    HatItemType.Hat_GoonPatrol_Yellow: HatItemDefinition(
        name="Yellow Goon Hardhat",
        description="No Description",
        modelName="goon_patrol_classic",
    ),
    HatItemType.Hat_GoonPatrol_Orange: HatItemDefinition(
        name="Orange Goon Hardhat",
        description="No Description",
        modelName="goon_patrol_classic",
        textureName="goon_patrol_classic_orange",
    ),
    HatItemType.Hat_GoonPatrol_Red: HatItemDefinition(
        name="Red Goon Hardhat",
        description="No Description",
        modelName="goon_patrol_classic",
        textureName="goon_patrol_classic_red",
    ),
    HatItemType.Hat_GoonPatrol_Purple: HatItemDefinition(
        name="Purple Goon Hardhat",
        description="No Description",
        modelName="goon_patrol_classic",
        textureName="goon_patrol_classic_purple",
    ),
    HatItemType.Hat_GoonSecurity: HatItemDefinition(
        name="Security Goon Hat",
        description="No Description",
        modelName="goon_security_classic",
    ),
    HatItemType.Hat_Skelecog_Purple: HatItemDefinition(
        name="Factory Foreman Hat",
        description="No Description",
        modelName="skelecog",
        textureName="skel_purple",
    ),
    HatItemType.Hat_CogBucket: HatItemDefinition(
        name="Cog Bucket Hat",
        description="No Description",
        modelName="bucket_cog",
    ),
    HatItemType.Hat_LowBaller: HatItemDefinition(
        name="Low Baller Hat",
        description="No Description",
        modelName="lowballer",
    ),
    HatItemType.Hat_HighRoller: HatItemDefinition(
        name="High Roller's Hat",
        description="No Description",
        modelName="highroller",
        accessoryClass=HatClassEnum.HighRollerHat,
    ),
    HatItemType.Hairbow_Fancy_Black: HatItemDefinition(
        name="Black Hairbow",
        description="Fashionable!",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_col_black",
    ),
    HatItemType.Hairbow_Fancy_Blackwhite: HatItemDefinition(
        name="Zebrastripe Hairbow",
        description="Kinda tacky, but fashionable!",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_striped_black_white",
    ),
    HatItemType.Hairbow_Fancy_Blue: HatItemDefinition(
        name="Blue Hairbow",
        description="Boldly blue!",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_col_blue",
    ),
    HatItemType.Hairbow_Fancy_Gray: HatItemDefinition(
        name="Gray Hairbow",
        description="Drab... still fashionable!",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_col_gray",
    ),
    HatItemType.Hairbow_Fancy_Green: HatItemDefinition(
        name="Green Hairbow",
        description="Mint condition!",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_col_green",
    ),
    HatItemType.Hairbow_Fancy_Orange: HatItemDefinition(
        name="Orange Hairbow",
        description="Looks like sunshine! And fashion!",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_col_orange",
    ),
    HatItemType.Hairbow_Fancy_Pink: HatItemDefinition(
        name="Pink Hairbow",
        description="It's pink!",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_col_pink",
    ),
    HatItemType.Hairbow_Fancy_Pinkblack: HatItemDefinition(
        name="Radical Hairbow",
        description="Perfect for running!",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_striped_pink_black",
    ),
    HatItemType.Hairbow_Fancy_Polkadot: HatItemDefinition(
        name="Polkadot Hairbow",
        description="Unpredictably wacky!",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_polka_white",
    ),
    HatItemType.Hairbow_Fancy_Purple: HatItemDefinition(
        name="Grape Hairbow",
        description="Deceptively Sweet!",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_col_purple",
    ),
    HatItemType.Hairbow_Fancy_Purpleorange: HatItemDefinition(
        name="PBJ Hairbow",
        description="Tasty, and fashionable!",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_striped_purple_orange",
    ),
    HatItemType.Hairbow_Fancy_Red: HatItemDefinition(
        name="Red Hairbow",
        description="Regular red hairbow!",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_col_red",
    ),
    HatItemType.Hairbow_Fancy_Yellow: HatItemDefinition(
        name="Yellow Hairbow",
        description="Oh so bright! And fashionable!",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_col_yellow",
    ),
    HatItemType.Hairbow_Fancy_Yellowblack: HatItemDefinition(
        name="Stinging Hairbow",
        description="\1TextTitle\1Yeouch!\2",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_striped_yellow_black",
    ),
    HatItemType.Hairbow_Pride_Ace: HatItemDefinition(
        name="Ace Pride Hairbow",
        description="No Description",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_pride_ace",
    ),
    HatItemType.Hairbow_Pride_Aro: HatItemDefinition(
        name="Aromantic Pride Hairbow",
        description="No Description",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_pride_aro",
    ),
    HatItemType.Hairbow_Pride_Bi: HatItemDefinition(
        name="Bi Pride Hairbow",
        description="No Description",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_pride_bi",
    ),
    HatItemType.Hairbow_Pride_Gay: HatItemDefinition(
        name="Gay Pride Hairbow",
        description="No Description",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_pride_gay",
    ),
    HatItemType.Hairbow_Pride_Genderfluid: HatItemDefinition(
        name="Genderfluid Pride Hairbow",
        description="No Description",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_pride_gfld",
    ),
    HatItemType.Hairbow_Pride_Lesbian: HatItemDefinition(
        name="Lesbian Pride Hairbow",
        description="No Description",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_pride_lsbn",
    ),
    HatItemType.Hairbow_Pride_Lgbt: HatItemDefinition(
        name="Pride Hairbow",
        description="No Description",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_pride_lgbt",
    ),
    HatItemType.Hairbow_Pride_Nb: HatItemDefinition(
        name="Non-Binary Pride Hairbow",
        description="No Description",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_pride_nb",
    ),
    HatItemType.Hairbow_Pride_Pan: HatItemDefinition(
        name="Pan Pride Hairbow",
        description="No Description",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_pride_pan",
    ),
    HatItemType.Hairbow_Pride_Trans: HatItemDefinition(
        name="Trans Pride Hairbow",
        description="No Description",
        modelName='bowtie_fancy',
        accFileType=('nec', 'nec'),
        accFilePath = ('neck', 'neck'),
        textureName="bowtie_fancy_pride_trans",
    ),
    HatItemType.Hat_Cyberpunk: HatItemDefinition(
        name="Cybertoon Visor",
        description="No Description",
        modelName="visor_cyber",
    ),
    HatItemType.Hat_MuzzleRose: HatItemDefinition(
        name="Solemn Rose",
        description='No Description',
        modelName='rose',
    ),
    HatItemType.Hat_PainterBrush: HatItemDefinition(
        name="Painter's Brush",
        description='Paint not included.',
        modelName='painter_brush',
    ),
    HatItemType.Hat_Wizard_Enchanted_Traffic_Orange: HatItemDefinition(
        name="Wizard Traffic Orange",
        description='Todo',
        modelName='',
    ),
    HatItemType.Headband_SpyHeadset: HatItemDefinition(
        name="Spy Headset",
        description='Todo',
        modelName='phones_spy',
    ),
    HatItemType.Hat_Pirate_Ghost: HatItemDefinition(
        name="Ghost Pirate Hat",
        description='Todo',
        modelName='pirate_ghost',
    ),

    HatItemType.Overhead_Pumpkin_Classic_Short: HatItemDefinition(
        name = "Classic Pumpkin (Short)",
        description = 'Todo',
        modelName = 'over_pumpkin_short',
    ),
    HatItemType.Overhead_Pumpkin_2018_Short: HatItemDefinition(
        name="2018 Pumpkin (Short)",
        description='Todo',
        modelName='over_pumpkin_short',
    ),
    HatItemType.Overhead_Pumpkin_2018_Tall: HatItemDefinition(
        name = "2018 Pumpkin (Tall)",
        description = 'Todo',
        modelName = 'over_pumpkin_tall',
    ),
    HatItemType.Overhead_Pumpkin_2019_Short: HatItemDefinition(
        name="2019 Pumpkin (Short)",
        description='Todo',
        modelName='over_pumpkin_short',
    ),
    HatItemType.Overhead_Pumpkin_2019_Tall: HatItemDefinition(
        name = "2019 Pumpkin (Tall)",
        description = 'Todo',
        modelName = 'over_pumpkin_tall',
    ),
    HatItemType.Overhead_Pumpkin_2020_Short: HatItemDefinition(
        name="2020 Pumpkin (Short)",
        description='Todo',
        modelName='over_pumpkin_short',
    ),
    HatItemType.Overhead_Pumpkin_2020_Tall: HatItemDefinition(
        name = "2020 Pumpkin (Tall)",
        description = 'Todo',
        modelName = 'over_pumpkin_tall',
    ),
    HatItemType.Overhead_Pumpkin_2021_Short: HatItemDefinition(
        name="2021 Pumpkin (Short)",
        description='Todo',
        modelName='over_pumpkin_short',
    ),
    HatItemType.Overhead_Pumpkin_2021_Tall: HatItemDefinition(
        name = "2021 Pumpkin (Tall)",
        description = 'Todo',
        modelName = 'over_pumpkin_tall',
    ),
    HatItemType.Overhead_Pumpkin_2023_Short: HatItemDefinition(
        name="2023 Pumpkin (Short)",
        description='Todo',
        modelName='over_pumpkin_short',
    ),
    HatItemType.Overhead_Pumpkin_2023_Tall: HatItemDefinition(
        name = "2023 Pumpkin (Tall)",
        description = 'Todo',
        modelName = 'over_pumpkin_tall',
    ),
}
