"""
This module contains the item data for glasses.
"""
from __future__ import annotations
from panda3d.core import NodePath

from toontown.inventory.base.InventoryItem import InventoryItem
from typing import Dict, Optional
from enum import IntEnum, auto

from toontown.inventory.definitions.AccessoryDefinition import AccessoryDefinition
from toontown.inventory.enums.ItemEnums import GlassesItemType
from toontown.inventory.enums.ItemTags import ItemTag
from toontown.toon.accessories.ToonActorAccessory import ToonActorAccessory
from toontown.toon.accessories.glasses.AnimatedHypno import AnimatedHypno
from toontown.toon.accessories.glasses.GlassesHideEyes import GlassesHideEyes
from toontown.toon.accessories.glasses.GlassesHideLashes import GlassesHideLashes
from toontown.toon.accessories.glasses.PirateGhostMask import PirateGhostMask
from toontown.toon.accessories.glasses.ScifiGlasses import ScifiGlasses

class GlassesClassEnum(IntEnum):
    Default = auto()
    GlassesHideEyes = auto()
    GlassesHideLashes = auto()
    AnimatedHypno = auto()
    ScifiGlasses = auto()
    PirateGhostMask = auto()


baseTexturePath = "cosmetics/"
baseModelPath = "cosmetics/"
textureExtension = ".png"


class GlassesItemDefinition(AccessoryDefinition):
    """
    The definition structure for glasses.
    """

    GlassesClasses = {
        GlassesClassEnum.GlassesHideEyes: GlassesHideEyes,
        GlassesClassEnum.GlassesHideLashes: GlassesHideLashes,
        GlassesClassEnum.AnimatedHypno: AnimatedHypno,
        GlassesClassEnum.ScifiGlasses: ScifiGlasses,
        GlassesClassEnum.PirateGhostMask: PirateGhostMask,
    }

    def __init__(self,
                 modelName,
                 textureName=None,
                 accessoryClass=GlassesClassEnum.Default,
                 accFileType=('face', 'face'),  # cc_t_acc_XXX_
                 accFilePath=('face', 'face'),  # cosmetics/maps/XXX
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
        return 'Glasses'

    def getRewardName(self, item: Optional[InventoryItem] = None):
        return f'{self.getName()} Glasses'

    def getModelPath(self):
        if not self.modelName:
            return None
        return f"{self.modelPath}{self.baseModelPrefix}{self.modelName}"

    def getTexturePath(self):
        if not self.textureName:
            return None
        return f"{self.texturePath}{self.baseTexturePrefix}{self.textureName}{textureExtension}"

    def getAccessoryClass(self):
        return self.GlassesClasses.get(self.accessoryClass, super().getAccessoryClass())

    def getTags(self, item: 'InventoryItem') -> set[ItemTag]:
        tags = super().getTags(item)
        tags.add(ItemTag.Glasses)
        return tags


# The registry dictionary for glasses.
GlassesRegistry: Dict[IntEnum, GlassesItemDefinition] = {
    GlassesItemType.Glasses_Round_Classic: GlassesItemDefinition(
        name="Round Glasses",
        description='Todo!',
        modelName='gl_round_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Miniblinds_Classic_White: GlassesItemDefinition(
        name="White Mini Blinds",
        description='Todo!',
        modelName='gl_miniblinds_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Shades_Hollywood_Classic: GlassesItemDefinition(
        name="Hollywood Shades",
        description='Even the Cogs admit, this one looks good.',
        modelName='gl_narrow_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Star_Classic: GlassesItemDefinition(
        name="Yellow Star Glasses",
        description='Todo!',
        modelName='gl_star_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Movie_Classic: GlassesItemDefinition(
        name="Movie Glasses",
        description='Todo!',
        modelName='gl_3d_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Aviator_Classic: GlassesItemDefinition(
        name="Aviator",
        description='Sky Clan, here we come!',
        modelName='gl_aviator_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Shades_Celebrity_Classic: GlassesItemDefinition(
        name="Celebrity Shades",
        description='Todo!',
        modelName='gl_jackieo_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Mask_Scuba_Classic: GlassesItemDefinition(
        name="Scuba Mask",
        description='Todo!',
        modelName='gl_goggles_scuba_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.GlassesHideEyes
    ),
    GlassesItemType.Glasses_Goggles_Classic: GlassesItemDefinition(
        name="Goggles",
        description='Todo!',
        modelName='gl_goggles_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_Groucho_Classic: GlassesItemDefinition(
        name="Groucho Glasses",
        description='Todo!',
        modelName='gl_groucho_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_Heart_Classic: GlassesItemDefinition(
        name="Heart Glasses",
        description='Todo!',
        modelName='gl_heart_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Bugeye_Classic: GlassesItemDefinition(
        name="Bug Eye Glasses",
        description='Todo!',
        modelName='gl_insect_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Mask_Identity_Classic_Black: GlassesItemDefinition(
        name="Black Super Toon Mask",
        description='Todo!',
        modelName='msk_ident_classic',
        textureName='msk_ident_classic_black',
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Mask_Identity_Classic_Blue: GlassesItemDefinition(
        name="Blue Super Toon Mask",
        description='Todo!',
        modelName='msk_ident_classic',
        textureName='msk_ident_classic_blue',
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Mask_Carnivale_Classic_Blue: GlassesItemDefinition(
        name="Blue Carnivale Mask",
        description='Todo!',
        modelName='msk_carnival_classic',
        textureName='msk_carnival_classic_blue',
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Mask_Carnivale_Classic_Purple: GlassesItemDefinition(
        name="Purple Carnivale Mask",
        description='Todo!',
        modelName='msk_carnival_classic',
        textureName='msk_carnival_classic_purple',
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Mask_Carnivale_Classic_Aqua: GlassesItemDefinition(
        name="Aqua Carnivale Mask",
        description='Todo!',
        modelName='msk_carnival_classic',
        textureName='msk_carnival_classic_green',
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_Monocle_Classic: GlassesItemDefinition(
        name="Monocle",
        description='Todo!',
        modelName='gl_monocle_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Smooch_Classic: GlassesItemDefinition(
        name="Smooch Glasses",
        description='Todo!',
        modelName='gl_mouth_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_SquareFrames_Classic: GlassesItemDefinition(
        name="Square Frame Glasses",
        description='Todo!',
        modelName='gl_square_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Cateye_Classic: GlassesItemDefinition(
        name="Cateye Glasses",
        description='Todo!',
        modelName='gl_cateye_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Nerd_Classic: GlassesItemDefinition(
        name="Nerd Glasses",
        description='Todo!',
        modelName='gl_dork_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Alien_Classic: GlassesItemDefinition(
        name="Alien Eyes",
        description='Todo!',
        modelName='gl_alien_classic',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Eyepatch_Classic_Skull: GlassesItemDefinition(
        name="Skull Eyepatch",
        description='Todo!',
        modelName='gl_eyepatch_classic',
        textureName='gl_eyepatch_classic_skull',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Eyepatch_Classic_Gem: GlassesItemDefinition(
        name="Gem Eyepatch",
        description='Todo!',
        modelName='gl_eyepatch_classic',
        textureName='gl_eyepatch_classic_gem',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Eyepatch_Classic_Desat: GlassesItemDefinition(
        name="Limey's Eyepatch",
        description='Todo!',
        modelName='gl_eyepatch_classic',
        textureName='gl_eyepatch_classic_gem',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Mask_Spider: GlassesItemDefinition(
        name="Spider Glasses",
        description='Todo!',
        modelName='msk_spider',
        textureName=None,
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_Hypno_Zany: GlassesItemDefinition(
        name="Hypno Glasses 2018",
        description='Todo!',
        modelName='gl_hypno',
        textureName='gl_hypno_zany',
        accessoryClass=GlassesClassEnum.AnimatedHypno
    ),
    GlassesItemType.Glasses_Goggles_SnowBlue: GlassesItemDefinition(
        name="Blue Snow Goggles",
        description='Todo!',
        modelName='gl_goggles_ski',
        textureName='gl_goggles_ski_blue',
        accessoryClass=GlassesClassEnum.GlassesHideEyes
    ),
    GlassesItemType.Glasses_Goggles_SnowGreen: GlassesItemDefinition(
        name="Green Snow Goggles",
        description='Todo!',
        modelName='gl_goggles_ski',
        textureName='gl_goggles_ski_green',
        accessoryClass=GlassesClassEnum.GlassesHideEyes
    ),
    GlassesItemType.Glasses_Goggles_SnowGrey: GlassesItemDefinition(
        name="Grey Snow Goggles",
        description='Todo!',
        modelName='gl_goggles_ski',
        textureName='gl_goggles_ski_gray',
        accessoryClass=GlassesClassEnum.GlassesHideEyes
    ),
    GlassesItemType.Glasses_Goggles_SnowPink: GlassesItemDefinition(
        name="Pink Snow Goggles",
        description='Todo!',
        modelName='gl_goggles_ski',
        textureName='gl_goggles_ski_pink',
        accessoryClass=GlassesClassEnum.GlassesHideEyes
    ),
    GlassesItemType.Glasses_Goggles_SnowRainbow: GlassesItemDefinition(
        name="Rainbow Snow Goggles",
        description='Todo!',
        modelName='gl_goggles_ski',
        textureName='gl_goggles_ski_rainbow',
        accessoryClass=GlassesClassEnum.GlassesHideEyes
    ),
    GlassesItemType.Glasses_Goggles_SnowRed: GlassesItemDefinition(
        name="Red Snow Goggles",
        description='Todo!',
        modelName='gl_goggles_ski',
        textureName='gl_goggles_ski_red',
        accessoryClass=GlassesClassEnum.GlassesHideEyes
    ),
    GlassesItemType.Glasses_Goggles_SnowVintage: GlassesItemDefinition(
        name="Vintage Snow Goggles",
        description='Todo!',
        modelName='gl_goggles_ski',
        textureName='gl_goggles_ski_vintage',
        accessoryClass=GlassesClassEnum.GlassesHideEyes
    ),
    GlassesItemType.Glasses_NYE_2019: GlassesItemDefinition(
        name="2019 Glasses",
        description='Todo!',
        modelName='gl_nye_19',
        textureName=None,
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_Flunky: GlassesItemDefinition(
        name="Flunky Glasses",
        description='Smells like morning cogfee.',
        modelName='gl_flunky',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_EyeSprings: GlassesItemDefinition(
        name="Eye Spring Glasses",
        description='Perfect prescription.',
        modelName='gl_eyespring',
        textureName=None,
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_Goggles_Flight: GlassesItemDefinition(
        name="Flight Goggles",
        description='Sky Clan, here we come!',
        modelName='gl_goggles_flight',
        textureName=None,
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_Outback_Sunny: GlassesItemDefinition(
        name="Outback Sunnyglasses",
        description='Let that sun shine!',
        modelName='gl_sunny',
        textureName=None,
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_Hypno_Green: GlassesItemDefinition(
        name="Hypno Glasses 2019",
        description='oOoOoOoOh... You want to buy these glasses...',
        modelName='gl_hypno',
        textureName='gl_hypno_green',
        accessoryClass=GlassesClassEnum.AnimatedHypno
    ),
    GlassesItemType.Glasses_X_Black: GlassesItemDefinition(
        name="Black Sad Glasses",
        description='You might be sad, but at least you\'re stylish!',
        modelName='gl_x',
        textureName='gl_x_black',
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_X_Gold: GlassesItemDefinition(
        name="Gold Sad Glasses",
        description='You might be sad, but at least you\'re stylish!',
        modelName='gl_x',
        textureName='gl_x_gold',
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_X_Green: GlassesItemDefinition(
        name="Green Sad Glasses",
        description='You might be sad, but at least you\'re stylish!',
        modelName='gl_x',
        textureName='gl_x_green',
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_X_Rainbow: GlassesItemDefinition(
        name="Rainbow Sad Glasses",
        description='You might be sad, but at least you\'re stylish!',
        modelName='gl_x',
        textureName='gl_x_rainbow',
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_X_Red: GlassesItemDefinition(
        name="Red Sad Glasses",
        description='You might be sad, but at least you\'re stylish!',
        modelName='gl_x',
        textureName='gl_x_red',
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_Gift_ActualBlue: GlassesItemDefinition(
        name="Gift Glasses",
        description='Todo!',
        modelName='gl_gift',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Gift_Blue: GlassesItemDefinition(
        name="Blue Gift Glasses",
        description='Todo!',
        modelName='gl_gift',
        textureName='gl_gift_blue',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Gift_Cyan: GlassesItemDefinition(
        name="Cyan Gift Glasses",
        description='Todo!',
        modelName='gl_gift',
        textureName='gl_gift_cyan',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Gift_Green: GlassesItemDefinition(
        name="Green Gift Glasses",
        description='Todo!',
        modelName='gl_gift',
        textureName='gl_gift_green',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Gift_Orange: GlassesItemDefinition(
        name="Orange Gift Glasses",
        description='Todo!',
        modelName='gl_gift',
        textureName='gl_gift_orange',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Gift_Pink: GlassesItemDefinition(
        name="Pink Gift Glasses",
        description='Todo!',
        modelName='gl_gift',
        textureName='gl_gift_pink',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Gift_Purple: GlassesItemDefinition(
        name="Purple Gift Glasses",
        description='Todo!',
        modelName='gl_gift',
        textureName='gl_gift_purple',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Gift_Red: GlassesItemDefinition(
        name="Red Gift Glasses",
        description='Todo!',
        modelName='gl_gift',
        textureName='gl_gift_red',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Gift_Yellow: GlassesItemDefinition(
        name="Yellow Gift Glasses",
        description='Todo!',
        modelName='gl_gift',
        textureName='gl_gift_yellow',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_NYE_2020: GlassesItemDefinition(
        name="2020 New Year's Glasses",
        description='Todo!',
        modelName='gl_nye_20',
        textureName=None,
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_Hypno_Red: GlassesItemDefinition(
        name="Red Hypno Glasses",
        description='oOoOoOoOh... You want to buy these glasses...',
        modelName='gl_hypno',
        textureName='gl_hypno_red_7',
        accessoryClass=GlassesClassEnum.AnimatedHypno
    ),
    GlassesItemType.Mustache_Vinny: GlassesItemDefinition(
        name="Vinny's Facial Hair",
        description='Todo!',
        modelName='mustache_vinny',
        textureName=None,
        accessoryClass=GlassesClassEnum.GlassesHideEyes
    ),
    GlassesItemType.Glasses_Chairman: GlassesItemDefinition(
        name="Chairman Glasses",
        description='Todo!',
        modelName='gl_chairman',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Hypno_Blue: GlassesItemDefinition(
        name="Blue Hypno",
        description='oOoOoOoOh... You want to buy these glasses...',
        modelName='gl_hypno',
        textureName='gl_hypno_blue',
        accessoryClass=GlassesClassEnum.AnimatedHypno
    ),
    GlassesItemType.Glasses_Hypno_LightBlue: GlassesItemDefinition(
        name="Light-Blue Hypno",
        description='oOoOoOoOh... You want to buy these glasses...',
        modelName='gl_hypno',
        textureName='gl_hypno_cyan',
        accessoryClass=GlassesClassEnum.AnimatedHypno
    ),
    GlassesItemType.Glasses_Hypno_Orange: GlassesItemDefinition(
        name="Orange Hypno",
        description='oOoOoOoOh... You want to buy these glasses...',
        modelName='gl_hypno',
        textureName='gl_hypno_orange',
        accessoryClass=GlassesClassEnum.AnimatedHypno
    ),
    GlassesItemType.Glasses_Hypno_Pink: GlassesItemDefinition(
        name="Pink Hypno",
        description='oOoOoOoOh... You want to buy these glasses...',
        modelName='gl_hypno',
        textureName='gl_hypno_pink',
        accessoryClass=GlassesClassEnum.AnimatedHypno
    ),
    GlassesItemType.Glasses_Hypno_Yellow: GlassesItemDefinition(
        name="Yellow Hypno",
        description='oOoOoOoOh... You want to buy these glasses...',
        modelName='gl_hypno',
        textureName='gl_hypno_yellow',
        accessoryClass=GlassesClassEnum.AnimatedHypno
    ),
    GlassesItemType.Glasses_Hypno_Purple: GlassesItemDefinition(
        name="Purple Hypno",
        description='oOoOoOoOh... You want to buy these glasses...',
        modelName='gl_hypno',
        textureName='gl_hypno_pink',
        accessoryClass=GlassesClassEnum.AnimatedHypno
    ),
    GlassesItemType.Glasses_Hypno_DarkPurple: GlassesItemDefinition(
        name="Dark-Purple Hypno",
        description='oOoOoOoOh... You want to buy these glasses...',
        modelName='gl_hypno',
        textureName='gl_hypno_purple',
        accessoryClass=GlassesClassEnum.AnimatedHypno
    ),
    GlassesItemType.Glasses_Hypno_Rainbow: GlassesItemDefinition(
        name="Rainbow Hypno",
        description='oOoOoOoOh... You want to buy these glasses...',
        modelName='gl_hypno',
        textureName='gl_hypno_rainbow',
        accessoryClass=GlassesClassEnum.AnimatedHypno
    ),
    GlassesItemType.Glasses_Ornament_Black: GlassesItemDefinition(
        name="Black Ornament",
        description='Todo!',
        modelName='gl_ornament',
        textureName='gl_orn_black',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Ornament_Blue: GlassesItemDefinition(
        name="Blue Ornament",
        description='Todo!',
        modelName='gl_ornament',
        textureName='gl_orn_blue',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Ornament_Cyan: GlassesItemDefinition(
        name="Cyan Ornament",
        description='Todo!',
        modelName='gl_ornament',
        textureName='gl_orn_cyan',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Ornament_Green: GlassesItemDefinition(
        name="Green Ornament",
        description='Todo!',
        modelName='gl_ornament',
        textureName='gl_orn_green',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Ornament_Orange: GlassesItemDefinition(
        name="Orange Ornament",
        description='Todo!',
        modelName='gl_ornament',
        textureName='gl_orn_orange',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Ornament_Pink: GlassesItemDefinition(
        name="Pink Ornament",
        description='Todo!',
        modelName='gl_ornament',
        textureName='gl_orn_pink',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Ornament_Purple: GlassesItemDefinition(
        name="Purple Ornament",
        description='Todo!',
        modelName='gl_ornament',
        textureName='gl_orn_purple',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Ornament_Rainbow: GlassesItemDefinition(
        name="Rainbow Ornament",
        description='Todo!',
        modelName='gl_ornament',
        textureName='gl_orn_rainbow',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Ornament_Red: GlassesItemDefinition(
        name="Red Ornament",
        description='Todo!',
        modelName='gl_ornament',
        textureName='gl_orn_red',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Ornament_White: GlassesItemDefinition(
        name="White Ornament",
        description='Todo!',
        modelName='gl_ornament',
        textureName='gl_orn_white',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Ornament_Yellow: GlassesItemDefinition(
        name="Yellow Ornament",
        description='Todo!',
        modelName='gl_ornament',
        textureName='gl_orn_yellow',
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Mask_HWTown: GlassesItemDefinition(
        name="Hallowopolis Mask",
        description='Todo!',
        modelName='msk_hwtown',
        textureName=None,
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Mask_Count: GlassesItemDefinition(
        name="Count Mask",
        description='Todo!',
        modelName='msk_count',
        textureName=None,
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_NYE_2022: GlassesItemDefinition(
        name="2022 Glasses",
        description='Todo!',
        modelName='gl_nye_20',
        textureName=None,
        accessoryClass=GlassesClassEnum.GlassesHideLashes
    ),
    GlassesItemType.Glasses_Visor_SciFi: GlassesItemDefinition(
        name="Space-Age Visor",
        description='Todo!',
        modelName='gl_visor_scifi',
        textureName=None,
        accessoryClass=GlassesClassEnum.ScifiGlasses
    ),
    GlassesItemType.Glasses_Brovinci: GlassesItemDefinition(
        name="Bro's Glasses",
        description='Todo!',
        modelName='gl_bro',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Mouthpiece: GlassesItemDefinition(
        name="Mouthpiece's Glasses",
        description='Todo!',
        modelName='gl_mouthpiece',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Funky: GlassesItemDefinition(
        name="Retro Glasses",
        description='Friday night fever!',
        modelName='gl_funky',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Mask_Sleepwalker: GlassesItemDefinition(
        name="Sleepwalker Mask",
        description='Sleep tight!',
        modelName='msk_sleepy',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Pacesetter: GlassesItemDefinition(
        name="Pacesetter's Glasses",
        description='Todo!',
        modelName='gl_pacesetter',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Card_Black: GlassesItemDefinition(
        name="Card Suit Glasses",
        description="Don't tap on the glass.",
        modelName='gl_card_black',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Card_Red: GlassesItemDefinition(
        name="Card Suit Glasses",
        description="Don't tap on the glass.",
        modelName='gl_card_red',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Cookie: GlassesItemDefinition(
        name="Cookie Glasses",
        description='Don\'t get all dough-eyed on me!',
        modelName='gl_cookie',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_LowBaller: GlassesItemDefinition(
        name="Low Baller Glasses",
        description='Todo!',
        modelName='gl_lowball',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Glasses_Visor_Cybertoon: GlassesItemDefinition(
        name="Cyberpunk Glasses",
        description='Todo!',
        modelName='gl_visor_cyber',
        textureName=None,
        accessoryClass=GlassesClassEnum.Default
    ),
    GlassesItemType.Mask_Pirate_Ghost: GlassesItemDefinition(
        name="Ghost Pirate Mask",
        description='Todo!',
        modelName='msk_pirate_ghost',
        accessoryClass=GlassesClassEnum.PirateGhostMask
    ),
    GlassesItemType.Glasses_Goggles_Spy: GlassesItemDefinition(
        name="Spy Goggles",
        description='Todo!',
        modelName='gl_goggles_spy',
    ),
}
