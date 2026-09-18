"""
This module contains the item data for clothing bottoms.
"""
from __future__ import annotations
from panda3d.core import NodePath, Texture, LVecBase4f

from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.base.ItemDefinition import ItemDefinition
from typing import Dict, Optional
from enum import IntEnum

from toontown.inventory.enums.ItemAttribute import ItemAttribute
from toontown.inventory.enums.ItemEnums import ClothingBottomItemType

from toontown.toon import ToonGlobals
from toontown.toon.ClothingGlobals import ClothingBottomType, BaseTexturePath, BaseTextureExtension
from toontown.toonbase import ProcessGlobals


class ClothingBottomItemDefinition(ItemDefinition):
    """
    The definition structure for clothing bottoms.
    """
    # Need to pre-load the model, or hammerspace item previews get very laggy
    if ProcessGlobals.getCurrentProcess() == ProcessGlobals.Process.Client:
        ShortsModel = NodePath('ClothingBottomRegistry-ShortsModel')
        tempTorso = loader.loadModel(f"phase_3/{ToonGlobals.TorsoDict['ms']}1000")
        tempTorso.find('**/torso-bot').copyTo(ShortsModel)
        tempTorso.removeNode()

        SkirtModel = NodePath('ClothingBottomRegistry-SkirtModel')
        tempTorso = loader.loadModel(f"phase_3/{ToonGlobals.TorsoDict['md']}1000")
        tempTorso.find('**/torso-bot').copyTo(SkirtModel)
        tempTorso.removeNode()

        del tempTorso

    def __init__(self,
                 textureName: str,
                 texturePath: str = "",
                 bottomType: ClothingBottomType = ClothingBottomType.Shorts,
                 dyeable: bool = False,
                 **kwargs):
        super().__init__(**kwargs)

        # Can this top have a custom colorScale set on it? Often used for desat textures.
        self.dyeable = dyeable

        # cc_t_clth_shorts_
        self.textureNamePrefix = f"cc_t_clth_{bottomType.value}_"

        self.bottomType = bottomType

        # If top texture name was defined with the extension, remove it to prevent redundancy
        # (unlike loading models, we must explicitly pass the file extension bit as well)
        self.textureName = textureName
        self.textureName.replace(BaseTextureExtension, "")

        if not texturePath:
            texturePath = BaseTexturePath
        self.texturePath = texturePath

    def getItemTypeName(self):
        return 'Shorts'

    def getRewardName(self, item: Optional[InventoryItem] = None):
        return f'{self.getName()} Shorts'

    def getTexture(self) -> Texture:
        tex = loader.loadTexture(
            f"{self.texturePath}{self.textureNamePrefix}{self.textureName}{BaseTextureExtension}"
        )
        return tex

    def getColor(self, item: Optional[InventoryItem] = None):
        if item is None or not self.dyeable:
            return LVecBase4f(1, 1, 1, 1)
        r, g, b, *_ = item.getAttribute(ItemAttribute.CLOTHES_PRIMARY_COL, (1, 1, 1))
        return LVecBase4f(r, g, b, 1)

    def makeItemModel(self, *extraArgs, item: Optional[InventoryItem] = None) -> NodePath:
        if self.isShorts():
            newNode = self.ShortsModel.copyTo(NodePath())
        else:
            newNode = self.SkirtModel.copyTo(NodePath())

        newNode.setTexture(self.getTexture(), 1)
        newNode.setColor(self.getColor(item = item))

        return newNode

    def isSkirt(self) -> bool:
        return self.bottomType.value == ClothingBottomType.Skirt

    def isShorts(self) -> bool:
        return self.bottomType.value == ClothingBottomType.Shorts

    def makeGuiItemModel(self) -> NodePath:
        """
        Creates the GUI item model to be used.
        """
        model = self.makeItemModel()
        for node in model.findAllMatches('*'):
            node.setH(180)
        model.flattenStrong()
        return model


# The registry dictionary for shorts.
ClothingBottomRegistry: Dict[IntEnum, ClothingBottomItemDefinition] = {
    ClothingBottomItemType.ShortswithBelt: ClothingBottomItemDefinition(
        name = "Shorts with Belt",
        description = "No Description",
        textureName = "desat_classic_belt",
        dyeable = True,
    ),
    ClothingBottomItemType.BigPocketsShorts: ClothingBottomItemDefinition(
        name = "Big Pockets",
        description = "No Description",
        textureName = "desat_classic_pockets",
        dyeable = True,
    ),
    ClothingBottomItemType.FeatherShorts: ClothingBottomItemDefinition(
        name = "Feather",
        description = "No Description",
        textureName = "desat_classic_feather",
        dyeable = True,
    ),
    ClothingBottomItemType.SidestripedShorts: ClothingBottomItemDefinition(
        name = "Side-striped",
        description = "No Description",
        textureName = "desat_classic_stripe_side",
        dyeable = True,
    ),
    ClothingBottomItemType.AthleticShortsA: ClothingBottomItemDefinition(
        name = "Athletic",
        description = "No Description",
        textureName = "desat_classic_athletic",
        dyeable = True,
    ),
    ClothingBottomItemType.FieryShorts: ClothingBottomItemDefinition(
        name = "Fiery",
        description = "No Description",
        textureName = "desat_classic_flame",
        dyeable = True,
    ),
    ClothingBottomItemType.JeanShorts: ClothingBottomItemDefinition(
        name = "Jean",
        description = "No Description",
        textureName = "desat_classic_jeans",
        dyeable = True,
    ),
    ClothingBottomItemType.Shorts_Valentoons_Pink: ClothingBottomItemDefinition(
        name = "Valentoon's Pink",
        description = "No Description",
        textureName = "valentoons_cupid_pink",
    ),
    ClothingBottomItemType.Shorts_Valentoons_Green: ClothingBottomItemDefinition(
        name = "Valentoon's Green",
        description = "No Description",
        textureName = "valentoons_cupid_green",
    ),
    ClothingBottomItemType.JeanHeartShorts: ClothingBottomItemDefinition(
        name = "Jean Heart Shorts",
        description = "No Description",
        textureName = "valentoons_heart_blue",
    ),
    ClothingBottomItemType.AthleticShortsB: ClothingBottomItemDefinition(
        name = "Athletic",
        description = "No Description",
        textureName = "sunset",
    ),
    ClothingBottomItemType.TealAndYellowShorts: ClothingBottomItemDefinition(
        name = "Teal & Yellow",
        description = "No Description",
        textureName = "yellow_stripe",
    ),
    ClothingBottomItemType.GreenAndYellowShorts: ClothingBottomItemDefinition(
        name = "Green & Yellow",
        description = "No Description",
        textureName = "green_pocket",
    ),
    ClothingBottomItemType.IdesofMarchShorts: ClothingBottomItemDefinition(
        name = "Ides of March",
        description = "No Description",
        textureName = "stpat_suit",
    ),
    ClothingBottomItemType.SnowmanShortsA: ClothingBottomItemDefinition(
        name = "Snowman",
        description = "No Description",
        textureName = "snowman_classic_blue",
    ),
    ClothingBottomItemType.SnowflakeShorts: ClothingBottomItemDefinition(
        name = "Snowflake",
        description = "No Description",
        textureName = "snowflakes_classic_blue",
    ),
    ClothingBottomItemType.PeppermintShorts: ClothingBottomItemDefinition(
        name = "Peppermint",
        description = "No Description",
        textureName = "peppermint_classic_red",
    ),
    ClothingBottomItemType.FestiveWinterShorts: ClothingBottomItemDefinition(
        name = "Festive Winter",
        description = "No Description",
        textureName = "plaid_classic_red",
    ),
    ClothingBottomItemType.Shorts_Supertoon_Classic: ClothingBottomItemDefinition(
        name = "Supertoon",
        description = "No Description",
        textureName = "supertoon_classic_red",
    ),
    ClothingBottomItemType.GolfingShorts: ClothingBottomItemDefinition(
        name = "Golfing",
        description = "No Description",
        textureName = "golf_color",
    ),
    ClothingBottomItemType.PleatedSkirt: ClothingBottomItemDefinition(
        name = "Pleated",
        description = "No Description",
        textureName = "desat_classic_blank",
        bottomType = ClothingBottomType.Skirt,
        dyeable = True,
    ),
    ClothingBottomItemType.PolkaDotSkirt: ClothingBottomItemDefinition(
        name = "Polka Dot",
        description = "No Description",
        textureName = "desat_classic_polka_dot",
        bottomType = ClothingBottomType.Skirt,
        dyeable = True,
    ),
    ClothingBottomItemType.StripedSkirt: ClothingBottomItemDefinition(
        name = "Striped",
        description = "No Description",
        textureName = "desat_classic_stripe_many",
        bottomType = ClothingBottomType.Skirt,
        dyeable = True,
    ),
    ClothingBottomItemType.BottomStripeSkirt: ClothingBottomItemDefinition(
        name = "Bottom Stripe",
        description = "No Description",
        textureName = "desat_classic_stripe_bottom",
        bottomType = ClothingBottomType.Skirt,
        dyeable = True,
    ),
    ClothingBottomItemType.FlowersSkirt: ClothingBottomItemDefinition(
        name = "Flowers",
        description = "No Description",
        textureName = "desat_classic_flowers",
        bottomType = ClothingBottomType.Skirt,
        dyeable = True,
    ),
    ClothingBottomItemType.JeanPocketsSkirt: ClothingBottomItemDefinition(
        name = "Jean Pockets",
        description = "No Description",
        textureName = "desat_classic_blank",
        bottomType = ClothingBottomType.Skirt,
        dyeable = True,
    ),
    ClothingBottomItemType.DenimSkirt: ClothingBottomItemDefinition(
        name = "Denim",
        description = "No Description",
        textureName = "desat_classic_jeans",
        bottomType = ClothingBottomType.Skirt,
        dyeable = True,
    ),
    ClothingBottomItemType.HighPocketsShorts: ClothingBottomItemDefinition(
        name = "High Pockets",
        description = "No Description",
        textureName = "desat_classic_blank",
        dyeable = True,
    ),
    ClothingBottomItemType.FlowerShorts: ClothingBottomItemDefinition(
        name = "Flower",
        description = "No Description",
        textureName = "desat_classic_flower",
        dyeable = True,
    ),
    ClothingBottomItemType.BlueAndGoldSkirt: ClothingBottomItemDefinition(
        name = "Blue & Gold",
        description = "No Description",
        textureName = "yellow_stripe",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.PinkBowSkirt: ClothingBottomItemDefinition(
        name = "Pink Bow",
        description = "No Description",
        textureName = "purple_bow",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.BlueGreenStarSkirt: ClothingBottomItemDefinition(
        name = "Blue-Green Star",
        description = "No Description",
        textureName = "green_star",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.RedAndWhiteHeartsSkirt: ClothingBottomItemDefinition(
        name = "Red & White Hearts",
        description = "No Description",
        textureName = "valentoons_heart",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.ValentoonsHeartsSkirt: ClothingBottomItemDefinition(
        name = "Valentoon's Hearts",
        description = "No Description",
        textureName = "valentoons_cupid_pink",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.JeanHeartSkirt: ClothingBottomItemDefinition(
        name = "Jean Heart Skirt",
        description = "No Description",
        textureName = "valentoons_heart_blue",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Skirt_Rainbow_Classic: ClothingBottomItemDefinition(
        name = "Rainbow",
        description = "No Description",
        textureName = "rainbow",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_LuckyClover_Classic: ClothingBottomItemDefinition(
        name = "Lucky Clover",
        description = "No Description",
        textureName = "stpat_rainbow",
    ),
    ClothingBottomItemType.IdesofMarchSkirt: ClothingBottomItemDefinition(
        name = "Ides of March",
        description = "No Description",
        textureName = "stpat_suit",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.WesternSkirt: ClothingBottomItemDefinition(
        name = "Western",
        description = "No Description",
        textureName = "cowboy_classic_yellow",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.ZestyWesternSkirt: ClothingBottomItemDefinition(
        name = "Zesty Western",
        description = "No Description",
        textureName = "cowboy_classic_blue",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_GoldBuckle_Classic: ClothingBottomItemDefinition(
        name = "Gold Buckle",
        description = "No Description",
        textureName = "cowboy_classic_boot",
    ),
    ClothingBottomItemType.Shorts_SilverBuckle_Classic: ClothingBottomItemDefinition(
        name = "Silver Buckle",
        description = "No Description",
        textureName = "cowboy_classic_horns",
    ),
    ClothingBottomItemType.Shorts_Stars_Classic: ClothingBottomItemDefinition(
        name = "July 4th",
        description = "No Description",
        textureName = "july4_stars",
    ),
    ClothingBottomItemType.Skirt_Stars_Classic: ClothingBottomItemDefinition(
        name = "July 4th",
        description = "No Description",
        textureName = "july4_stars",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.DaisySkirt: ClothingBottomItemDefinition(
        name = "Daisy",
        description = "No Description",
        textureName = "blue_flower",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Gag_Classic_BananaPeel: ClothingBottomItemDefinition(
        name = "Banana Peel",
        description = "No Description",
        textureName = "gag_banana",
    ),
    ClothingBottomItemType.Shorts_Gag_Classic_BikeHorn: ClothingBottomItemDefinition(
        name = "Bike Horn",
        description = "No Description",
        textureName = "gag_bikehorn",
    ),
    ClothingBottomItemType.Shorts_Gag_Classic_HypnoGoggles: ClothingBottomItemDefinition(
        name = "Hypno Goggles",
        description = "No Description",
        textureName = "gag_goggles",
    ),
    ClothingBottomItemType.Skirt_Snowman: ClothingBottomItemDefinition(
        name = "Snowman",
        description = "No Description",
        textureName = "snowman_classic_blue",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.SnowflakesSkirt: ClothingBottomItemDefinition(
        name = "Snowflakes",
        description = "No Description",
        textureName = "snowflakes_classic_blue",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.PeppermintSkirt: ClothingBottomItemDefinition(
        name = "Peppermint",
        description = "No Description",
        textureName = "peppermint_classic_red",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.FestiveWinterSkirt: ClothingBottomItemDefinition(
        name = "Festive Winter",
        description = "No Description",
        textureName = "plaid_classic_red",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.FishingShorts: ClothingBottomItemDefinition(
        name = "Fishing",
        description = "No Description",
        textureName = "fish_group",
    ),
    ClothingBottomItemType.GardeningShorts: ClothingBottomItemDefinition(
        name = "Gardening",
        description = "No Description",
        textureName = "garden_overalls",
    ),
    ClothingBottomItemType.Shorts_Party: ClothingBottomItemDefinition(
        name = "Party",
        description = "You'll be the life of the party!",
        textureName = "confetti",
    ),
    ClothingBottomItemType.CheckeredRacingShorts: ClothingBottomItemDefinition(
        name = "Checkered Racing",
        description = "No Description",
        textureName = "racing_roadster",
    ),
    ClothingBottomItemType.GoldfishShorts: ClothingBottomItemDefinition(
        name = "Goldfish",
        description = "No Description",
        textureName = "fish_mini",
    ),
    ClothingBottomItemType.GreenPlaidGolfingShorts: ClothingBottomItemDefinition(
        name = "Green Plaid Golfing",
        description = "Great for camouflage!",
        textureName = "golf_stripes",
    ),
    ClothingBottomItemType.Shorts_Bee_Classic: ClothingBottomItemDefinition(
        name = "Bee",
        description = "No Description",
        textureName = "bee_yellow",
    ),
    ClothingBottomItemType.SaveTheBuildingsShorts: ClothingBottomItemDefinition(
        name = "Save The Buildings",
        description = "No Description",
        textureName = "building_1",
    ),
    ClothingBottomItemType.TrolleyShorts: ClothingBottomItemDefinition(
        name = "Trolley",
        description = "No Description",
        textureName = "jellybeans",
    ),
    ClothingBottomItemType.Shorts_Spider_Classic: ClothingBottomItemDefinition(
        name = "Spider",
        description = "No Description",
        textureName = "spider_classic_black",
    ),
    ClothingBottomItemType.Shorts_Skeletoon_Classic: ClothingBottomItemDefinition(
        name = "Skeletoon",
        description = "No Description",
        textureName = "skeleton_classic_black",
    ),
    ClothingBottomItemType.BlueRacingShorts: ClothingBottomItemDefinition(
        name = "Blue Racing",
        description = "No Description",
        textureName = "racing_prix",
    ),
    ClothingBottomItemType.IndigoRacingShorts: ClothingBottomItemDefinition(
        name = "Indigo Racing",
        description = "No Description",
        textureName = "racing_3",
    ),
    ClothingBottomItemType.TanGolfingShorts: ClothingBottomItemDefinition(
        name = "Tan Golfing",
        description = "No Description",
        textureName = "golf_tan",
    ),
    ClothingBottomItemType.CheckeredGolfShorts: ClothingBottomItemDefinition(
        name = "Checkered Golf",
        description = "No Description",
        textureName = "golf_checker",
    ),
    ClothingBottomItemType.DarkBlueRacingShorts: ClothingBottomItemDefinition(
        name = "Dark Blue Racing",
        description = "No Description",
        textureName = "racing_2",
    ),
    ClothingBottomItemType.RacingStripeShorts: ClothingBottomItemDefinition(
        name = "Racing w/ Stripe",
        description = "No Description",
        textureName = "racing_1",
    ),
    ClothingBottomItemType.FishingSkirt: ClothingBottomItemDefinition(
        name = "Fishing",
        description = "No Description",
        textureName = "fishing_hook",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.GardeningSkirt: ClothingBottomItemDefinition(
        name = "Gardening",
        description = "No Description",
        textureName = "garden_vegetables",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.PartySkirt: ClothingBottomItemDefinition(
        name = "Party",
        description = "For when you want that extra swish when you dance!",
        textureName = "party_cupcake",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.RedCheckeredSkirt: ClothingBottomItemDefinition(
        name = "Red Checkered",
        description = "No Description",
        textureName = "racing_roadster",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.GrassSkirt: ClothingBottomItemDefinition(
        name = "Grass",
        description = "No Description",
        textureName = "summer_hula",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.PinkPlaidGolfSkirt: ClothingBottomItemDefinition(
        name = "Pink Plaid Golf",
        description = "Not great for camouflage!",
        textureName = "golf_stripes",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Skirt_Bee_Classic: ClothingBottomItemDefinition(
        name = "Bee",
        description = "No Description",
        textureName = "bee_yellow",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Skirt_Supertoon_Classic: ClothingBottomItemDefinition(
        name = "Supertoon",
        description = "No Description",
        textureName = "supertoon_classic_red",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.SaveTheBuildingsSkirt: ClothingBottomItemDefinition(
        name = "Save The Buildings",
        description = "No Description",
        textureName = "building_1",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.TrolleySkirt: ClothingBottomItemDefinition(
        name = "Trolley",
        description = "No Description",
        textureName = "jellybeans",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Skirt_Skeletoon_Classic: ClothingBottomItemDefinition(
        name = "Skeletoon",
        description = "No Description",
        textureName = "skeleton_classic_black",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Skirt_Spider_Classic: ClothingBottomItemDefinition(
        name = "Spider",
        description = "No Description",
        textureName = "spider_classic_black",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.CogCrusherShorts: ClothingBottomItemDefinition(
        name = "Cog-Crusher Shorts",
        description = "The suit for the most masterful of Gag-wielding! If you don't mind looking like a banana.",
        textureName = "cogCrusher_yellow",
    ),
    ClothingBottomItemType.SellbotCrusherShorts: ClothingBottomItemDefinition(
        name = "Sellbot Crusher",
        description = "No Description",
        textureName = "crusher_sellbot",
    ),
    ClothingBottomItemType.BlueCheckeredRacingSkirt: ClothingBottomItemDefinition(
        name = "Blue Checkered Racing",
        description = "No Description",
        textureName = "racing_prix",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.StarryGolfingSkirt: ClothingBottomItemDefinition(
        name = "Starry Golfing",
        description = "No Description",
        textureName = "golf_flower",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.IndigoRacingSkirt: ClothingBottomItemDefinition(
        name = "Indigo Racing",
        description = "No Description",
        textureName = "racing_3",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.RainbowGolfingSkirt: ClothingBottomItemDefinition(
        name = "Rainbow Golfing",
        description = "No Description",
        textureName = "golf_rainbow",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.BluePlaidGolfingSkirt: ClothingBottomItemDefinition(
        name = "Blue Plaid Golfing",
        description = "No Description",
        textureName = "golf_checker",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.DarkBlueRacingSkirt: ClothingBottomItemDefinition(
        name = "Dark Blue Racing",
        description = "No Description",
        textureName = "racing_2",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.RacingStripeSkirt: ClothingBottomItemDefinition(
        name = "Racing w/ Stripe",
        description = "No Description",
        textureName = "racing_1",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.ScientistAShorts: ClothingBottomItemDefinition(
        name = "Scientist A",
        description = "No Description",
        textureName = "scientist_loony_green",
    ),
    ClothingBottomItemType.ScientistBShorts: ClothingBottomItemDefinition(
        name = "Scientist B",
        description = "No Description",
        textureName = "scientist_loony_orange",
    ),
    ClothingBottomItemType.ScientistCShorts: ClothingBottomItemDefinition(
        name = "Scientist C",
        description = "No Description",
        textureName = "scientist_loony_blue",
    ),
    ClothingBottomItemType.OvercoatVampireShorts: ClothingBottomItemDefinition(
        name = "Overcoat Vampire",
        description = "No Description",
        textureName = "vampire_classic_red_cape",
    ),
    ClothingBottomItemType.Shorts_Turtle_Classic: ClothingBottomItemDefinition(
        name = "Turtle",
        description = "No Description",
        textureName = "turtle_classic_green",
    ),
    ClothingBottomItemType.Shorts_Pirate_Classic: ClothingBottomItemDefinition(
        name = "Pirate",
        description = "No Description",
        textureName = "pirate_classic_red",
    ),
    ClothingBottomItemType.Skirt_Pirate_Classic: ClothingBottomItemDefinition(
        name = "Pirate",
        description = "No Description",
        textureName = "pirate_classic_red",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Vampire_Classic: ClothingBottomItemDefinition(
        name = "Vampire",
        description = "No Description",
        textureName = "vampire_classic",
    ),
    ClothingBottomItemType.Shorts_Toonosaur_Classic: ClothingBottomItemDefinition(
        name = "Toonosaur",
        description = "No Description",
        textureName = "dinosaur_classic_green",
    ),
    ClothingBottomItemType.Shorts_Meatballs: ClothingBottomItemDefinition(
        name = "Meatballs",
        description = "No really, don't eat it. It's fabric.",
        textureName = "meatball",
    ),
    ClothingBottomItemType.Shorts_Travis_Rags: ClothingBottomItemDefinition(
        name = "Trashcat's Rags",
        description = "No Description",
        textureName = "npc_travis",
    ),
    ClothingBottomItemType.Shorts_DDL_Sleeper: ClothingBottomItemDefinition(
        name = "Drowsy Dreamland",
        description = "No Description",
        textureName = "dreamland",
    ),
    ClothingBottomItemType.Shorts_BetaToon: ClothingBottomItemDefinition(
        name = "Beta Toon",
        description = "No Description",
        textureName = "beta_purple",
    ),
    ClothingBottomItemType.Skirt_BetaToon: ClothingBottomItemDefinition(
        name = "Beta Toon",
        description = "No Description",
        textureName = "beta_purple",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_YOTT_Knight: ClothingBottomItemDefinition(
        name = "YOTT Knight",
        description = "No Description",
        textureName = "knight",
    ),
    ClothingBottomItemType.Skirt_YOTT_Knight: ClothingBottomItemDefinition(
        name = "YOTT Knight",
        description = "No Description",
        textureName = "knight",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_BB_Sailor: ClothingBottomItemDefinition(
        name = "BB Sailor",
        description = "No Description",
        textureName = "boatyard_sailor_blue",
    ),
    ClothingBottomItemType.Skirt_BB_Sailor: ClothingBottomItemDefinition(
        name = "BB Sailor",
        description = "No Description",
        textureName = "boatyard_sailor_blue",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_DG_Gardening: ClothingBottomItemDefinition(
        name = "DG Gardening",
        description = "No Description",
        textureName = "garden_outfit",
    ),
    ClothingBottomItemType.Skirt_DG_Gardening: ClothingBottomItemDefinition(
        name = "DG Gardening",
        description = "No Description",
        textureName = "garden_outfit",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_TTC_Firefighter: ClothingBottomItemDefinition(
        name = "TTC Firefighter",
        description = "No Description",
        textureName = "ttc_firefighter",
    ),
    ClothingBottomItemType.Skirt_TTC_Firefighter: ClothingBottomItemDefinition(
        name = "TTC Firefighter",
        description = "No Description",
        textureName = "ttc_firefighter",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_MML_Band: ClothingBottomItemDefinition(
        name = "MML Band",
        description = "No Description",
        textureName = "mml_band",
    ),
    ClothingBottomItemType.Shorts_Barnyard: ClothingBottomItemDefinition(
        name = "Team Barnyard",
        description = "No Description",
        textureName = "barnyard_overalls",
    ),
    ClothingBottomItemType.Skirt_Barnyard: ClothingBottomItemDefinition(
        name = "Team Barnyard",
        description = "No Description",
        textureName = "barnyard_overalls",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Outback: ClothingBottomItemDefinition(
        name = "Team Outback",
        description = "No Description",
        textureName = "outback_outfit",
    ),
    ClothingBottomItemType.Skirt_Outback: ClothingBottomItemDefinition(
        name = "Team Outback",
        description = "No Description",
        textureName = "outback_outfit",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_AA_ParkRanger: ClothingBottomItemDefinition(
        name = "AA Park Ranger",
        description = "No Description",
        textureName = "ranger",
    ),
    ClothingBottomItemType.Shorts_TB_Sweater: ClothingBottomItemDefinition(
        name = "TB Snowflake",
        description = "No Description",
        textureName = "sweater_brrrgh_blue",
    ),
    ClothingBottomItemType.Skirt_TB_Sweater: ClothingBottomItemDefinition(
        name = "TB Snowflake",
        description = "No Description",
        textureName = "sweater_brrrgh_blue",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Alchemist: ClothingBottomItemDefinition(
        name = "Alchemist",
        description = "No Description",
        textureName = "alchemist_blue",
    ),
    ClothingBottomItemType.Skirt_Alchemist: ClothingBottomItemDefinition(
        name = "Alchemist",
        description = "No Description",
        textureName = "alchemist_blue",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Frankenstein: ClothingBottomItemDefinition(
        name = "Frankentoon",
        description = "No Description",
        textureName = "frankenstein_orange",
    ),
    ClothingBottomItemType.SpacetoonShorts: ClothingBottomItemDefinition(
        name = "Spacetoon",
        description = "No Description",
        textureName = "moonsuit_white",
    ),
    ClothingBottomItemType.MadScientistShorts: ClothingBottomItemDefinition(
        name = "Mad Scientist",
        description = "No Description",
        textureName = "scientist_mad_orange",
    ),
    ClothingBottomItemType.ClownShortsA: ClothingBottomItemDefinition(
        name = "Clown",
        description = "No Description",
        textureName = "clown_rainbow",
    ),
    ClothingBottomItemType.ClownSkirtA: ClothingBottomItemDefinition(
        name = "Clown",
        description = "No Description",
        textureName = "clown_rainbow",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Wonderland: ClothingBottomItemDefinition(
        name = "Wonderland",
        description = "No Description",
        textureName = "wonderland_black",
    ),
    ClothingBottomItemType.Skirt_Wonderland: ClothingBottomItemDefinition(
        name = "Wonderland",
        description = "No Description",
        textureName = "wonderland_blue",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Reaper: ClothingBottomItemDefinition(
        name = "Reaper",
        description = "No Description",
        textureName = "reaper_purple",
    ),
    ClothingBottomItemType.Skirt_Reaper: ClothingBottomItemDefinition(
        name = "Reaper",
        description = "No Description",
        textureName = "reaper_purple",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Scarecrow: ClothingBottomItemDefinition(
        name = "Scarecrow Shorts",
        description = "No Description",
        textureName = "scarecrow_blue",
    ),
    ClothingBottomItemType.Skirt_Scarecrow: ClothingBottomItemDefinition(
        name = "Scarecrow Skirt",
        description = "No Description",
        textureName = "scarecrow_blue",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Witch: ClothingBottomItemDefinition(
        name = "Witch",
        description = "No Description",
        textureName = "witch_purple",
    ),
    ClothingBottomItemType.Skirt_Witch: ClothingBottomItemDefinition(
        name = "Witch",
        description = "No Description",
        textureName = "witch_purple",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Elf_Green: ClothingBottomItemDefinition(
        name = "Green Elf",
        description = "No Description",
        textureName = "elf_green",
    ),
    ClothingBottomItemType.Shorts_Elf_Red: ClothingBottomItemDefinition(
        name = "Red Elf",
        description = "No Description",
        textureName = "elf_red",
    ),
    ClothingBottomItemType.Skirt_Elf_Green: ClothingBottomItemDefinition(
        name = "Green Elf",
        description = "No Description",
        textureName = "elf_green",
    ),
    ClothingBottomItemType.Skirt_Elf_Red: ClothingBottomItemDefinition(
        name = "Red Elf",
        description = "No Description",
        textureName = "elf_red",
    ),
    ClothingBottomItemType.Shorts_Gingerbread: ClothingBottomItemDefinition(
        name = "Gingerbread",
        description = "No Description",
        textureName = "gingerbread",
    ),
    ClothingBottomItemType.Skirt_Gingerbread: ClothingBottomItemDefinition(
        name = "Gingerbread Skirt",
        description = "No Description",
        textureName = "gingerbread",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.PresentUniformShorts: ClothingBottomItemDefinition(
        name = "Present Uniform",
        description = "No Description",
        textureName = "santa_red",
    ),
    ClothingBottomItemType.PresentUniformSkirt: ClothingBottomItemDefinition(
        name = "Present Uniform",
        description = "No Description",
        textureName = "santa_red",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Skirt_Ragdoll_Humble: ClothingBottomItemDefinition(
        name = "Ragdoll Humble",
        description = "No Description",
        textureName = "ragdoll_humble_blue",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Skirt_Ragdoll_Regal: ClothingBottomItemDefinition(
        name = "Ragdoll Regal",
        description = "No Description",
        textureName = "ragdoll_regal_green",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Skirt_Ragdoll_Traditional: ClothingBottomItemDefinition(
        name = "Ragdoll Traditional",
        description = "No Description",
        textureName = "ragdoll_tradi_green",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Skirt_Reindeer: ClothingBottomItemDefinition(
        name = "Reindeer",
        description = "No Description",
        textureName = "reindeer",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Reindeer: ClothingBottomItemDefinition(
        name = "Reindeer",
        description = "No Description",
        textureName = "reindeer",
    ),
    ClothingBottomItemType.VintageSnowShorts: ClothingBottomItemDefinition(
        name = "Vintage Snow",
        description = "No Description",
        textureName = "vintage_ski_purple",
    ),
    ClothingBottomItemType.Shorts_Ragdoll_Humble: ClothingBottomItemDefinition(
        name = "Ragdoll Humble",
        description = "No Description",
        textureName = "ragdoll_humble_blue",
    ),
    ClothingBottomItemType.Shorts_Ragdoll_Regal: ClothingBottomItemDefinition(
        name = "Ragdoll Regal",
        description = "No Description",
        textureName = "ragdoll_regal_yellow",
    ),
    ClothingBottomItemType.Shorts_Ragdoll_Traditional: ClothingBottomItemDefinition(
        name = "Ragdoll Traditional",
        description = "No Description",
        textureName = "ragdoll_tradi_green",
    ),
    ClothingBottomItemType.Shorts_Soldier_Humble: ClothingBottomItemDefinition(
        name = "Tin Humble",
        description = "No Description",
        textureName = "soldier_humble_blue",
    ),
    ClothingBottomItemType.Shorts_Soldier_Regal: ClothingBottomItemDefinition(
        name = "Tin Regal",
        description = "No Description",
        textureName = "soldier_regal_green",
    ),
    ClothingBottomItemType.Shorts_Soldier_Traditional: ClothingBottomItemDefinition(
        name = "Tin Traditional",
        description = "No Description",
        textureName = "soldier_tradi_red",
    ),
    ClothingBottomItemType.Shorts_NYE_2019: ClothingBottomItemDefinition(
        name = "2019 Suit",
        description = "No Description",
        textureName = "nye_19",
    ),
    ClothingBottomItemType.Skirt_NYE_2019: ClothingBottomItemDefinition(
        name = "2019 Dress",
        description = "No Description",
        textureName = "nye_19",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.CupidShorts: ClothingBottomItemDefinition(
        name = "Cupid Shorts",
        description = "No Description",
        textureName = "valentoons_cupid_green",
    ),
    ClothingBottomItemType.CupidSkirt: ClothingBottomItemDefinition(
        name = "Cupid Skirt",
        description = "No Description",
        textureName = "valentoons_cupid_green",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Webster: ClothingBottomItemDefinition(
        name = "Webster's Shorts",
        description = "No Description",
        textureName = "npc_webster",
    ),
    ClothingBottomItemType.Skirt_Doe: ClothingBottomItemDefinition(
        name = "Doe's Skirt",
        description = "No Description",
        textureName = "npc_doe",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.AviatorShorts: ClothingBottomItemDefinition(
        name = "Aviator Shorts",
        description = "Sky Clan, here we come!",
        textureName = "aviator_brown",
    ),
    ClothingBottomItemType.WingsuitShorts: ClothingBottomItemDefinition(
        name = "Wingsuit Shorts",
        description = "It might allow you to fly... not Loony Labs certified.",
        textureName = "wingsuit",
    ),
    ClothingBottomItemType.Skirt_SellbotSeeker: ClothingBottomItemDefinition(
        name = "Sellbot Seeker",
        description = "No Description",
        textureName = "dept_sellbot",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_SellbotSeeker: ClothingBottomItemDefinition(
        name = "Sellbot Seeker",
        description = "No Description",
        textureName = "dept_sellbot",
    ),
    ClothingBottomItemType.Skirt_CashbotCatcher: ClothingBottomItemDefinition(
        name = "Cashbot Catcher",
        description = "No Description",
        textureName = "dept_cashbot",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_CashbotCatcher: ClothingBottomItemDefinition(
        name = "Cashbot Catcher",
        description = "No Description",
        textureName = "dept_cashbot",
    ),
    ClothingBottomItemType.Skirt_LawbotLiberator: ClothingBottomItemDefinition(
        name = "Lawbot Liberator",
        description = "No Description",
        textureName = "dept_lawbot",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_LawbotLiberator: ClothingBottomItemDefinition(
        name = "Lawbot Liberator",
        description = "No Description",
        textureName = "dept_lawbot",
    ),
    ClothingBottomItemType.Skirt_BossbotBasher: ClothingBottomItemDefinition(
        name = "Bossbot Basher",
        description = "No Description",
        textureName = "dept_bossbot",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_BossbotBasher: ClothingBottomItemDefinition(
        name = "Bossbot Basher",
        description = "No Description",
        textureName = "dept_bossbot",
    ),
    ClothingBottomItemType.OutbackUniformShorts: ClothingBottomItemDefinition(
        name = "Outback Uniform",
        description = "No Description",
        textureName = "outback_uniform",
    ),
    ClothingBottomItemType.OutbackUniformSkirt: ClothingBottomItemDefinition(
        name = "Outback Uniform",
        description = "No Description",
        textureName = "outback_uniform",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Alien: ClothingBottomItemDefinition(
        name = "Alien Shorts",
        description = "No Description",
        textureName = "alien_black",
    ),
    ClothingBottomItemType.Shorts_CandyCorn: ClothingBottomItemDefinition(
        name = "Candy Corn Shorts",
        description = "No Description",
        textureName = "candycorn_brown",
    ),
    ClothingBottomItemType.LawbotResistanceShorts: ClothingBottomItemDefinition(
        name = "Lawbot Resistance",
        description = "No Description",
        textureName = "crusher_lawbot",
    ),
    ClothingBottomItemType.LawbotResistanceSkirt: ClothingBottomItemDefinition(
        name = "Lawbot Resistance",
        description = "No Description",
        textureName = "crusher_lawbot",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_RetroRobot: ClothingBottomItemDefinition(
        name = "Retro Robot Shorts",
        description = "No Description",
        textureName = "retrobot_teal",
    ),
    ClothingBottomItemType.Shorts_RidingHood: ClothingBottomItemDefinition(
        name = "Riding Hood",
        description = "No Description",
        textureName = "ridinghood_red",
    ),
    ClothingBottomItemType.Skirt_RidingHood: ClothingBottomItemDefinition(
        name = "Riding Hood",
        description = "No Description",
        textureName = "ridinghood_red",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Nurse: ClothingBottomItemDefinition(
        name = "Nurse Shorts",
        description = "Laugh your way to good laff!",
        textureName = "nurse_white",
    ),
    ClothingBottomItemType.Skirt_Nurse: ClothingBottomItemDefinition(
        name = "Nurse Skirt",
        description = "Laugh your way to good laff!",
        textureName = "nurse_white",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_LazyBones: ClothingBottomItemDefinition(
        name = "Lazy Bones",
        description = "No Description",
        textureName = "sans_black",
    ),
    ClothingBottomItemType.Shorts_Sailor_White: ClothingBottomItemDefinition(
        name = "Sailor Shorts",
        description = "No Description",
        textureName = "sailor_white",
    ),
    ClothingBottomItemType.Skirt_Sailor_White: ClothingBottomItemDefinition(
        name = "Sailor Skirt",
        description = "No Description",
        textureName = "sailor_white",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Sailor_Blue: ClothingBottomItemDefinition(
        name = "Blue Sailor Shorts",
        description = "No Description",
        textureName = "sailor_blue",
    ),
    ClothingBottomItemType.Skirt_Sailor_Blue: ClothingBottomItemDefinition(
        name = "Blue Sailor Skirt",
        description = "No Description",
        textureName = "sailor_blue",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Sailor_Cyan: ClothingBottomItemDefinition(
        name = "Cyan Sailor Shorts",
        description = "No Description",
        textureName = "sailor_cyan",
    ),
    ClothingBottomItemType.Skirt_Sailor_Cyan: ClothingBottomItemDefinition(
        name = "Cyan Sailor Skirt",
        description = "No Description",
        textureName = "sailor_cyan",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Sailor_Green: ClothingBottomItemDefinition(
        name = "Green Sailor Shorts",
        description = "No Description",
        textureName = "sailor_green",
    ),
    ClothingBottomItemType.Skirt_Sailor_Green: ClothingBottomItemDefinition(
        name = "Green Sailor Skirt",
        description = "No Description",
        textureName = "sailor_green",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Sailor_Orange: ClothingBottomItemDefinition(
        name = "Orange Sailor Shorts",
        description = "No Description",
        textureName = "sailor_orange",
    ),
    ClothingBottomItemType.Skirt_Sailor_Orange: ClothingBottomItemDefinition(
        name = "Orange Sailor Skirt",
        description = "No Description",
        textureName = "sailor_orange",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Sailor_Pink: ClothingBottomItemDefinition(
        name = "Pink Sailor Shorts",
        description = "No Description",
        textureName = "sailor_pink",
    ),
    ClothingBottomItemType.Skirt_Sailor_Pink: ClothingBottomItemDefinition(
        name = "Pink Sailor Skirt",
        description = "No Description",
        textureName = "sailor_pink",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Sailor_Purple: ClothingBottomItemDefinition(
        name = "Purple Sailor Shorts",
        description = "No Description",
        textureName = "sailor_purple",
    ),
    ClothingBottomItemType.Skirt_Sailor_Purple: ClothingBottomItemDefinition(
        name = "Purple Sailor Skirt",
        description = "No Description",
        textureName = "sailor_purple",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Sailor_Red: ClothingBottomItemDefinition(
        name = "Red Sailor Shorts",
        description = "No Description",
        textureName = "sailor_red",
    ),
    ClothingBottomItemType.Skirt_Sailor_Red: ClothingBottomItemDefinition(
        name = "Red Sailor Skirt",
        description = "No Description",
        textureName = "sailor_red",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Sailor_Black: ClothingBottomItemDefinition(
        name = "Black Sailor Shorts",
        description = "No Description",
        textureName = "sailor_black",
    ),
    ClothingBottomItemType.Skirt_Sailor_Black: ClothingBottomItemDefinition(
        name = "Black Sailor Skirt",
        description = "No Description",
        textureName = "sailor_black",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Sailor_Yellow: ClothingBottomItemDefinition(
        name = "Golden Sailor Shorts",
        description = "No Description",
        textureName = "sailor_yellow",
    ),
    ClothingBottomItemType.Skirt_Sailor_Yellow: ClothingBottomItemDefinition(
        name = "Golden Sailor Skirt",
        description = "No Description",
        textureName = "sailor_yellow",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_TeamTrees: ClothingBottomItemDefinition(
        name = "Team Trees",
        description = "No Description",
        textureName = "tree",
    ),
    ClothingBottomItemType.Shorts_Ragdoll_Homemade: ClothingBottomItemDefinition(
        name = "Homemade Ragdoll",
        description = "No Description",
        textureName = "ragdoll_homemade_yellow",
    ),
    ClothingBottomItemType.Skirt_Ragdoll_Homemade: ClothingBottomItemDefinition(
        name = "Homemade Ragdoll",
        description = "No Description",
        textureName = "ragdoll_homemade_yellow",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Soldier_Homemade: ClothingBottomItemDefinition(
        name = "Homemade Soldier",
        description = "No Description",
        textureName = "soldier_homemade_yellow",
    ),
    ClothingBottomItemType.RetroWinterShorts: ClothingBottomItemDefinition(
        name = "Retro Winter",
        description = "No Description",
        textureName = "retrowin_red",
    ),
    ClothingBottomItemType.RetroWinterSkirt: ClothingBottomItemDefinition(
        name = "Retro Winter",
        description = "No Description",
        textureName = "retrowin_red",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.SnowmanShortsB: ClothingBottomItemDefinition(
        name = "Snowman",
        description = "No Description",
        textureName = "snowtoon",
    ),
    ClothingBottomItemType.Shorts_NYE_2020: ClothingBottomItemDefinition(
        name = "New Year's 2020",
        description = "No Description",
        textureName = "nye_20",
    ),
    ClothingBottomItemType.Skirt_NYE_2020: ClothingBottomItemDefinition(
        name = "New Year's 2020",
        description = "No Description",
        textureName = "nye_20",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.AgentSevenSkirt: ClothingBottomItemDefinition(
        name = "Agent Seven",
        description = "No Description",
        textureName = "agent_seven_red",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.StPattys2020Skirt: ClothingBottomItemDefinition(
        name = "St. Patty's 2020",
        description = "No Description",
        textureName = "stpat_lucky",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.StPattys2020Shorts: ClothingBottomItemDefinition(
        name = "St. Patty's 2020",
        description = "No Description",
        textureName = "stpat_lucky",
    ),
    ClothingBottomItemType.ClownSkirtB: ClothingBottomItemDefinition(
        name = "Clown",
        description = "Who thought Toons could get any sillier?",
        textureName = "clown_red",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.ClownShortsB: ClothingBottomItemDefinition(
        name = "Clown",
        description = "Who thought Toons could get any sillier?",
        textureName = "clown_red",
    ),
    ClothingBottomItemType.Skirt_SevenStriped: ClothingBottomItemDefinition(
        name = "Seven Striped",
        description = "Jackpot!",
        textureName = "jersey_seven_green",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_SevenStriped: ClothingBottomItemDefinition(
        name = "Seven Striped",
        description = "Jackpot!",
        textureName = "jersey_seven_green",
    ),
    ClothingBottomItemType.Skirt_TripleRainbow: ClothingBottomItemDefinition(
        name = "Triple Rainbow",
        description = "Triple rainbow! What does it mean?",
        textureName = "jacket_tripRainbow_blue",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_TripleRainbow: ClothingBottomItemDefinition(
        name = "Triple Rainbow",
        description = "Triple rainbow! What does it mean?",
        textureName = "jacket_tripRainbow_blue",
    ),
    ClothingBottomItemType.Shorts_Suit_Boardbot: ClothingBottomItemDefinition(
        name = "Boardbot",
        description = "No Description",
        textureName = "suit_boardbot_teal",
    ),
    ClothingBottomItemType.Skirt_Jester_Red: ClothingBottomItemDefinition(
        name = "Jester",
        description = "Popularized in Ye Olde Toontowne!",
        textureName = "jester_red",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Jester_Red: ClothingBottomItemDefinition(
        name = "Jester",
        description = "Popularized in Ye Olde Toontowne!",
        textureName = "jester_red",
    ),
    ClothingBottomItemType.Skirt_Jester_Black: ClothingBottomItemDefinition(
        name = "Black Jester Skirt",
        description = "Popularized in Ye Olde Toontowne!",
        textureName = "jester_black",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Jester_Black: ClothingBottomItemDefinition(
        name = "Black Jester Shorts",
        description = "Popularized in Ye Olde Toontowne!",
        textureName = "jester_black",
    ),
    ClothingBottomItemType.Easter2020Shorts: ClothingBottomItemDefinition(
        name = "Easter 2020",
        description = "No Description",
        textureName = "easter_bunny",
    ),
    ClothingBottomItemType.Easter2020Skirt: ClothingBottomItemDefinition(
        name = "Easter 2020",
        description = "No Description",
        textureName = "easter_bunny",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Suit_Lawbot: ClothingBottomItemDefinition(
        name = "Lawbot Suit Pants",
        description = "No Description",
        textureName = "suit_lawbot_blue",
    ),
    ClothingBottomItemType.CooktheCogsShorts: ClothingBottomItemDefinition(
        name = "Cook the Cogs",
        description = "No Description",
        textureName = "july4_cook",
    ),
    ClothingBottomItemType.CooktheCogsSkirt: ClothingBottomItemDefinition(
        name = "Cook the Cogs",
        description = "No Description",
        textureName = "july4_cook",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Suit_Boardbot_Executive: ClothingBottomItemDefinition(
        name = "Executive Boardbot",
        description = "No Description",
        textureName = "suit_boardbot_black",
    ),
    ClothingBottomItemType.Shorts_Phantoon: ClothingBottomItemDefinition(
        name = "Phantoon",
        description = "No Description",
        textureName = "phantoon_black",
    ),
    ClothingBottomItemType.Skirt_ToonsmasPast: ClothingBottomItemDefinition(
        name = "Toonsmas Past",
        description = "No Description",
        textureName = "past_yellow",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_ToonsmasPast: ClothingBottomItemDefinition(
        name = "Toonsmas Past",
        description = "No Description",
        textureName = "past_yellow",
    ),
    ClothingBottomItemType.Skirt_ToonsmasPresent: ClothingBottomItemDefinition(
        name = "Toonsmas Present",
        description = "No Description",
        textureName = "present_green",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_ToonsmasPresent: ClothingBottomItemDefinition(
        name = "Toonsmas Present",
        description = "No Description",
        textureName = "present_green",
    ),
    ClothingBottomItemType.Skirt_ToonsmasFuture: ClothingBottomItemDefinition(
        name = "Toonsmas Future",
        description = "No Description",
        textureName = "future_black",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_ToonsmasFuture: ClothingBottomItemDefinition(
        name = "Toonsmas Future",
        description = "No Description",
        textureName = "future_black",
    ),
    ClothingBottomItemType.Skirt_NYE_2021: ClothingBottomItemDefinition(
        name = "New Year's 2021",
        description = "No Description",
        textureName = "nye_21",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_NYE_2021: ClothingBottomItemDefinition(
        name = "New Year's 2021",
        description = "No Description",
        textureName = "nye_21",
    ),
    ClothingBottomItemType.Shorts_Tumbles: ClothingBottomItemDefinition(
        name = "Tumbles' Shorts",
        description = "No Description",
        textureName = "tumbles",
    ),
    ClothingBottomItemType.HallowopolisShorts: ClothingBottomItemDefinition(
        name = "Hallowopolis Shorts",
        description = "No Description",
        textureName = "hwtown_black",
    ),
    ClothingBottomItemType.DetectiveShorts: ClothingBottomItemDefinition(
        name = "Detective",
        description = "No Description",
        textureName = "detective_brown",
    ),
    ClothingBottomItemType.FloralShorts: ClothingBottomItemDefinition(
        name = "Floral Shorts",
        description = "No Description",
        textureName = "floral_green",
    ),
    ClothingBottomItemType.Shorts_Newstoon_Blue: ClothingBottomItemDefinition(
        name = "Blue Newstoon Shorts",
        description = "No Description",
        textureName = "newstoon_blue",
    ),
    ClothingBottomItemType.Skirt_Newstoon_Blue: ClothingBottomItemDefinition(
        name = "Blue Newstoon Skirt",
        description = "No Description",
        textureName = "newstoon_blue",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Newstoon_Gray: ClothingBottomItemDefinition(
        name = "Gray Newstoon Shorts",
        description = "No Description",
        textureName = "newstoon_gray",
    ),
    ClothingBottomItemType.Skirt_Newstoon_Gray: ClothingBottomItemDefinition(
        name = "Gray Newstoon Skirt",
        description = "No Description",
        textureName = "newstoon_gray",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.ChupShorts: ClothingBottomItemDefinition(
        name = "Chup Shorts",
        description = "No Description",
        textureName = "chupbottle",
    ),
    ClothingBottomItemType.ChupSkirt: ClothingBottomItemDefinition(
        name = "Chup Skirt",
        description = "No Description",
        textureName = "chupbottle",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_NYE_2022: ClothingBottomItemDefinition(
        name = "New Year's 2022",
        description = "No Description",
        textureName = "nye_22",
    ),
    ClothingBottomItemType.Skirt_NYE_2022: ClothingBottomItemDefinition(
        name = "New Year's 2022",
        description = "No Description",
        textureName = "nye_22",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.DoctorToonShorts: ClothingBottomItemDefinition(
        name = "Doctor Toon Shorts",
        description = "No Description",
        textureName = "doctor_toon",
    ),
    ClothingBottomItemType.DoctorToonSkirt: ClothingBottomItemDefinition(
        name = "Doctor Toon Skirt",
        description = "No Description",
        textureName = "doctor_toon",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_TrolleyEngineer: ClothingBottomItemDefinition(
        name = "Trolley Engineer Shorts",
        description = "All aboard!",
        textureName = "engineer",
    ),
    ClothingBottomItemType.Skirt_TrolleyEngineer: ClothingBottomItemDefinition(
        name = "Trolley Engineer Skirt",
        description = "All aboard!",
        textureName = "engineer",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.StarstruckSkirt: ClothingBottomItemDefinition(
        name = "Starstruck Skirt",
        description = "You'll outshine the moon with this one!",
        textureName = "moon",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.RetroShorts: ClothingBottomItemDefinition(
        name = "Retro Shorts",
        description = "Friday night fever!",
        textureName = "funky",
    ),
    ClothingBottomItemType.StarstruckShorts: ClothingBottomItemDefinition(
        name = "Starstruck Shorts",
        description = "You'll outshine the moon with this one!",
        textureName = "moon",
    ),
    ClothingBottomItemType.SleepwalkerShorts: ClothingBottomItemDefinition(
        name = "Sleepwalker Shorts",
        description = "Sleep tight!",
        textureName = "sleepwalker",
    ),
    ClothingBottomItemType.FruitPieShorts: ClothingBottomItemDefinition(
        name = "Fruit Pie Shorts",
        description = "Tastes good, too!",
        textureName = "fruitpie",
    ),
    ClothingBottomItemType.FruitPieSkirt: ClothingBottomItemDefinition(
        name = "Fruit Pie Skirt",
        description = "Tastes good, too!",
        textureName = "fruitpie",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.GumballMachineShorts: ClothingBottomItemDefinition(
        name = "Gumball Machine Shorts",
        description = "Full of flavor!",
        textureName = "gumball",
    ),
    ClothingBottomItemType.GumballMachineSkirt: ClothingBottomItemDefinition(
        name = "Gumball Machine Skirt",
        description = "Full of flavor!",
        textureName = "gumball",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.CardSuitShorts: ClothingBottomItemDefinition(
        name = "Card Suit Shorts",
        description = "You've got to know when to hold 'em and when to fold 'em.",
        textureName = "cards",
    ),
    ClothingBottomItemType.CardSuitSkirt: ClothingBottomItemDefinition(
        name = "Card Suit Skirt",
        description = "You've got to know when to hold 'em and when to fold 'em.",
        textureName = "cards",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.PainterShorts: ClothingBottomItemDefinition(
        name = "Painter Shorts",
        description = "Paint not included.",
        textureName = "painter",
    ),
    ClothingBottomItemType.PainterSkirt: ClothingBottomItemDefinition(
        name = "Painter Skirt",
        description = "Paint not included.",
        textureName = "painter",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Chef: ClothingBottomItemDefinition(
        name = "Chef Shorts",
        description = "No Description",
        textureName = "chef",
    ),
    ClothingBottomItemType.Skirt_Chef: ClothingBottomItemDefinition(
        name = "Chef Skirt",
        description = "No Description",
        textureName = "chef",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_NYE_2023: ClothingBottomItemDefinition(
        name = "New Year's 2023",
        description = "No Description",
        textureName = "nye_23",
    ),
    ClothingBottomItemType.Skirt_NYE_2023: ClothingBottomItemDefinition(
        name = "New Year's 2023",
        description = "No Description",
        textureName = "nye_23",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.Shorts_Armor: ClothingBottomItemDefinition(
        name = "Armored Pants",
        description = "No Description",
        textureName = "miniboss_armor",
    ),
    ClothingBottomItemType.Skirt_Armor: ClothingBottomItemDefinition(
        name = "Armored Skirt",
        description = "No Description",
        textureName = "miniboss_armor",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.HighRollersSuitShorts: ClothingBottomItemDefinition(
        name = "High Roller's Suit",
        description = "No Description",
        textureName = "suit_hroller_white",
    ),
    ClothingBottomItemType.HighRollersProdigalSuitShorts: ClothingBottomItemDefinition(
        name = "High Roller's Prodigal Suit",
        description = "No Description",
        textureName = "suit_hroller_black",
    ),
    ClothingBottomItemType.Shorts_Cybertoon: ClothingBottomItemDefinition(
        name = "Cybertoon Shorts",
        description = "No Description",
        textureName = "cyberpunk",
    ),
    ClothingBottomItemType.Skirt_Cybertoon: ClothingBottomItemDefinition(
        name = "Cybertoon Skirt",
        description = "No Description",
        textureName = "cyberpunk",
        bottomType = ClothingBottomType.Skirt,
    ),
    ClothingBottomItemType.BroVinci: ClothingBottomItemDefinition(
        name = "Bro Vinci",
        description = "No Description",
        textureName = "npc_bro",
    ),
    ClothingBottomItemType.Shorts_Pirate_Ghost: ClothingBottomItemDefinition(
        name = "Ghost Pirate Shorts",
        description = "No Description",
        textureName = "pirate_ghost_green",
    ),
    ClothingBottomItemType.Skirt_Pirate_Ghost: ClothingBottomItemDefinition(
        name = "Ghost Pirate Skirt",
        description = "No Description",
        textureName = "pirate_ghost_green",
    ),
    ClothingBottomItemType.Shorts_Spytoon: ClothingBottomItemDefinition(
        name = "Toon Spy Shorts",
        description = "No Description",
        textureName = "spy_purple",
    ),
    ClothingBottomItemType.Skirt_Spytoon: ClothingBottomItemDefinition(
        name = "Toon Spy Skirt",
        description = "No Description",
        textureName = "spy_purple",
    ),
    ClothingBottomItemType.Shorts_NYE_2024: ClothingBottomItemDefinition(
        name = "New Year's 2024 Shorts",
        description = "No Description",
        textureName = "nye_24",
    ),
    ClothingBottomItemType.Skirt_NYE_2024: ClothingBottomItemDefinition(
        name = "New Year's 2024 Skirt",
        description = "No Description",
        textureName = "nye_24",
        bottomType = ClothingBottomType.Skirt,
    ),
}
