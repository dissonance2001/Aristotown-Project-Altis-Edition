"""
This module contains the item data for clothing tops.
"""
from __future__ import annotations
from panda3d.core import NodePath, Texture, LVecBase4f

from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.base.ItemDefinition import ItemDefinition
from typing import Dict, Optional
from enum import IntEnum

from toontown.inventory.enums.ItemAttribute import ItemAttribute
from toontown.inventory.enums.ItemEnums import ClothingTopItemType

from toontown.toon import ToonGlobals
from toontown.toon.ClothingGlobals import ClothingTopType, BaseTexturePath, BaseTextureExtension
from toontown.toonbase import ProcessGlobals


class ClothingTopItemDefinition(ItemDefinition):
    """
    The definition structure for shirts.
    """
    # Need to pre-load the model, or hammerspace item previews get very laggy
    if ProcessGlobals.getCurrentProcess() == ProcessGlobals.Process.Client:
        ShirtModel = NodePath('ClothingTopRegistry-ShirtModel')
        tempTorso = loader.loadModel(f"phase_3/{ToonGlobals.TorsoDict['ms']}1000")
        tempTorso.find('**/torso-top').copyTo(ShirtModel)
        tempTorso.find('**/sleeves').copyTo(ShirtModel)
        tempTorso.removeNode()
        del tempTorso

    def __init__(self,
                 topTextureName: str,
                 topSleeveTextureName: str = "",
                 topTexturePath: str = "",
                 topSleeveTexturePath: str = "",
                 dyeable: bool = False,
                 topType: ClothingTopType = ClothingTopType.Shirt,
                 **kwargs):
        """
        :param str topSleeveTextureName: Default: topTextureName_sleeve
        :param str topTexturePath:  Default: cosmetics/clothing/maps/
        :param str topSleeveTexturePath: Default: cosmetics/clothing/maps/
        """
        super().__init__(**kwargs)
        # This attribute isn't currently utilized, but is here for any future clothing expansions.
        self.topType = topType

        # Can this top have a custom colorScale set on it? Often used for desat textures.
        self.dyeable = dyeable

        # cc_t_clth_shirt_
        self.textureNamePrefix = f"cc_t_clth_{topType.value}_"

        if not topTexturePath:
            topTexturePath = BaseTexturePath
        if not topSleeveTexturePath:
            topSleeveTexturePath = BaseTexturePath
        self.topTexturePath = topTexturePath

        # If top texture name was defined with the extension, remove it to prevent redundancy
        # (unlike loading models, we must explicitly pass the file extension bit as well)
        self.topTextureName = topTextureName
        self.topTextureName.replace(BaseTextureExtension, "")

        # Most top sleeve textures will be the top tex name + "_sleeve", but there are some that don't follow this
        # such as shirts that share the same sleeve texture
        if not topSleeveTextureName:
            topSleeveTextureName = topTextureName

        self.topSleeveTextureName = topSleeveTextureName
        # Same deal with defining sleeve textures, remove the extension if it was placed...
        self.topSleeveTextureName.replace(BaseTextureExtension, "")
        self.topSleeveTexturePath = topSleeveTexturePath
        # For now, ALL sleeve textures will be suffixed with "_sleeve" before the file extension.
        if not self.topSleeveTextureName.endswith("_sleeve"):
            self.topSleeveTextureName += "_sleeve"

    def getItemTypeName(self):
        return 'Shirt'

    def getRewardName(self, item: Optional[InventoryItem] = None):
        return f'{self.getName()} Shirt'

    def getTexture(self) -> Texture:
        tex = loader.loadTexture(
            f"{self.topTexturePath}{self.textureNamePrefix}{self.topTextureName}{BaseTextureExtension}"
        )
        return tex

    def getSleeveTexture(self):
        tex = loader.loadTexture(
            f"{self.topTexturePath}{self.textureNamePrefix}{self.topSleeveTextureName}{BaseTextureExtension}"
        )
        return tex

    def getColor(self, item: Optional[InventoryItem] = None):
        if item is None or not self.dyeable:
            return LVecBase4f(1, 1, 1, 1)
        r, g, b, *_ = item.getAttribute(ItemAttribute.CLOTHES_PRIMARY_COL, (1, 1, 1))
        return LVecBase4f(r, g, b, 1)

    def getSleeveColor(self, item: Optional[InventoryItem] = None):
        if item is None or not self.dyeable:
            return LVecBase4f(1, 1, 1, 1)
        r, g, b, *_ = item.getAttribute(ItemAttribute.CLOTHES_SECONDARY_COL,
                                        item.getAttribute(ItemAttribute.CLOTHES_PRIMARY_COL, (1, 1, 1)))
        return LVecBase4f(r, g, b, 1)

    def isDyeable(self) -> bool:
        return self.dyeable

    def makeItemModel(self, *extraArgs, item: Optional[InventoryItem] = None) -> NodePath:
        newNode = self.ShirtModel.copyTo(NodePath())

        newNode.find('**/torso-top').setTexture(self.getTexture(), 1)
        newNode.find('**/torso-top').setColor(self.getColor(item=item))
        newNode.find('**/sleeves').setTexture(self.getSleeveTexture(), 1)
        newNode.find('**/sleeves').setColor(self.getSleeveColor(item=item))

        return newNode

    def makeGuiItemModel(self) -> NodePath:
        """
        Creates the GUI item model to be used.
        """
        model = self.makeItemModel()
        for node in model.findAllMatches('*'):
            node.setH(180)
        model.flattenStrong()
        return model


# The registry dictionary for shirts.
ClothingTopRegistry: Dict[IntEnum, ClothingTopItemDefinition] = {
    ClothingTopItemType.Shirt_Desat_Classic_Plain: ClothingTopItemDefinition(
        name="Plain",
        description="No Description",
        topTextureName="desat_classic_blank",
        dyeable=True,
    ),
    ClothingTopItemType.Shirt_Desat_Classic_StripeSingle: ClothingTopItemDefinition(
        name="Bottom Stripe",
        description="No Description",
        topTextureName="desat_classic_stripe_one",
        dyeable=True,
    ),
    ClothingTopItemType.Shirt_Desat_Classic_ButtonUp: ClothingTopItemDefinition(
        name="Button-Up",
        description="No Description",
        topTextureName="desat_classic_buttonup",
        dyeable=True,
    ),
    ClothingTopItemType.Shirt_Desat_Classic_StripeDouble: ClothingTopItemDefinition(
        name="Double Striped",
        description="No Description",
        topTextureName="desat_classic_stripe_two",
        dyeable=True,
    ),
    ClothingTopItemType.Shirt_Desat_Classic_StripeMany: ClothingTopItemDefinition(
        name="Striped",
        description="No Description",
        topTextureName="desat_classic_stripe_many",
        dyeable=True,
    ),
    ClothingTopItemType.Shirt_Desat_Classic_PocketPolo: ClothingTopItemDefinition(
        name="Pocket Polo",
        description="No Description",
        topTextureName="desat_classic_pocket",
        dyeable=True,
    ),
    ClothingTopItemType.Feather: ClothingTopItemDefinition(
        name="Feather",
        description="No Description",
        topTextureName="desat_classic_feather",
        dyeable=True,
    ),
    ClothingTopItemType.Dress: ClothingTopItemDefinition(
        name="Dress",
        description="No Description",
        topTextureName="desat_classic_button_up",
        dyeable=True,
    ),
    ClothingTopItemType.TwoToneButtonUp: ClothingTopItemDefinition(
        name="Two-Tone Button-Up",
        description="No Description",
        topTextureName="desat_classic_buttonup_twotone",
        topSleeveTextureName="desat_classic_blank_sleeve",
        dyeable=True,
    ),
    ClothingTopItemType.Vest: ClothingTopItemDefinition(
        name="Vest",
        description="No Description",
        topTextureName="desat_classic_vest",
        topSleeveTextureName="desat_classic_blank_sleeve",
        dyeable=True,
    ),
    ClothingTopItemType.ButtonUpB: ClothingTopItemDefinition(
        name="Button-Up",
        description="No Description",
        topTextureName="desat_classic_blouse",
        dyeable=True,
    ),
    ClothingTopItemType.Soccer: ClothingTopItemDefinition(
        name="Soccer",
        description="No Description",
        topTextureName="desat_classic_soccer",
        dyeable=True,
    ),
    ClothingTopItemType.LightningBolt: ClothingTopItemDefinition(
        name="Lightning Bolt",
        description="No Description",
        topTextureName="desat_classic_bolt",
        topSleeveTextureName="desat_classic_blank_sleeve",
        dyeable=True,
    ),
    ClothingTopItemType.No19: ClothingTopItemDefinition(
        name="#19",
        description="No Description",
        topTextureName="desat_classic_number",
        topSleeveTextureName="desat_classic_blank_sleeve",
        dyeable=True,
    ),
    ClothingTopItemType.Guayabera: ClothingTopItemDefinition(
        name="Guayabera",
        description="No Description",
        topTextureName="desat_classic_guayabera",
        dyeable=True,
    ),
    ClothingTopItemType.Shirt_Desat_Classic_FlowersMany: ClothingTopItemDefinition(
        name="Flower",
        description="No Description",
        topTextureName="desat_classic_flowers_many",
        dyeable=True,
    ),
    ClothingTopItemType.Shirt_Desat_Classic_FlowersStripe: ClothingTopItemDefinition(
        name="Flower Stripe",
        description="No Description",
        topTextureName="desat_classic_flower_stripe",
        dyeable=True,
    ),
    ClothingTopItemType.DenimVest: ClothingTopItemDefinition(
        name="Denim Vest",
        description="No Description",
        topTextureName="desat_classic_vest_denim",
        topSleeveTextureName="desat_classic_blank_sleeve",
    ),
    ClothingTopItemType.CuffedBlouse: ClothingTopItemDefinition(
        name="Cuffed Blouse",
        description="No Description",
        topTextureName="desat_classic_cuffed",
        topSleeveTextureName="desat_classic_peplum_sleeve",
        dyeable=True,
    ),
    ClothingTopItemType.Peplum: ClothingTopItemDefinition(
        name="Peplum",
        description="No Description",
        topTextureName="desat_classic_peplum",
        dyeable=True,
    ),
    ClothingTopItemType.Hearts: ClothingTopItemDefinition(
        name="Hearts",
        description="No Description",
        topTextureName="desat_classic_three_hearts",
        topSleeveTextureName="desat_classic_blank_sleeve",
        dyeable=True,
    ),
    ClothingTopItemType.Stars: ClothingTopItemDefinition(
        name="Stars",
        description="No Description",
        topTextureName="desat_classic_stars",
        topSleeveTextureName="desat_classic_blank_sleeve",
        dyeable=True,
    ),
    ClothingTopItemType.Shirt_Desat_Classic_FlowersSingle: ClothingTopItemDefinition(
        name="Single Flower",
        description="No Description",
        topTextureName="desat_classic_flower",
        topSleeveTextureName="desat_classic_blank_sleeve",
        dyeable=True,
    ),
    ClothingTopItemType.ZipUpHoodie: ClothingTopItemDefinition(
        name="Zip-Up Hoodie",
        description="No Description",
        topTextureName="jacket_classic_orange",
    ),
    ClothingTopItemType.Island: ClothingTopItemDefinition(
        name="Island",
        description="No Description",
        topTextureName="island_classic_yellow",
    ),
    ClothingTopItemType.PurpleStars: ClothingTopItemDefinition(
        name="Purple Stars",
        description="No Description",
        topTextureName="stars_classic_purple",
    ),
    ClothingTopItemType.WinterStripes: ClothingTopItemDefinition(
        name="Winter Stripes",
        description="No Description",
        topTextureName="stripe_blue",
    ),
    ClothingTopItemType.No1: ClothingTopItemDefinition(
        name="#1",
        description="No Description",
        topTextureName="number_one",
    ),
    ClothingTopItemType.GreenStripe: ClothingTopItemDefinition(
        name="Green Stripe",
        description="No Description",
        topTextureName="vine",
    ),
    ClothingTopItemType.Shirt_Kimono_Classic_Red: ClothingTopItemDefinition(
        name="Red Checkerboard Kimono",
        description="No Description",
        topTextureName="stripe_checkers",
    ),
    ClothingTopItemType.GoldenStripes: ClothingTopItemDefinition(
        name="Golden Stripes",
        description="No Description",
        topTextureName="wavy",
    ),
    ClothingTopItemType.PinkBow: ClothingTopItemDefinition(
        name="Pink Bow",
        description="No Description",
        topTextureName="princess",
    ),
    ClothingTopItemType.TiedDress: ClothingTopItemDefinition(
        name="Tied Dress",
        description="No Description",
        topTextureName="ballerina_classic_blue",
    ),
    ClothingTopItemType.WinterStripe: ClothingTopItemDefinition(
        name="Winter Stripe",
        description="No Description",
        topTextureName="white_stripe",
    ),
    ClothingTopItemType.TieDye: ClothingTopItemDefinition(
        name="Tie-Dye",
        description="No Description",
        topTextureName="tiedye_classic",
    ),
    ClothingTopItemType.Sheriff: ClothingTopItemDefinition(
        name="Sheriff",
        description="No Description",
        topTextureName="cowboy_classic_vest",
    ),
    ClothingTopItemType.CheckeredCowboy: ClothingTopItemDefinition(
        name="Checkered Cowboy",
        description="No Description",
        topTextureName="cowboy_classic_bandana_blue",
    ),
    ClothingTopItemType.CactusCowboy: ClothingTopItemDefinition(
        name="Cactus Cowboy",
        description="No Description",
        topTextureName="cowboy_classic_bandana_red",
    ),
    ClothingTopItemType.CowboyVest: ClothingTopItemDefinition(
        name="Cowboy Vest",
        description="No Description",
        topTextureName="cowboy_classic_bandana_purple",
    ),
    ClothingTopItemType.GreenDrawstring: ClothingTopItemDefinition(
        name="Green Drawstring",
        description="No Description",
        topTextureName="cowboy_classic_green",
    ),
    ClothingTopItemType.BlueDrawstring: ClothingTopItemDefinition(
        name="Blue Drawstring",
        description="No Description",
        topTextureName="cowboy_classic_blue",
    ),
    ClothingTopItemType.Ghost: ClothingTopItemDefinition(
        name="Ghost",
        description="No Description",
        topTextureName="ghost_classic_purple",
    ),
    ClothingTopItemType.Pumpkin: ClothingTopItemDefinition(
        name="Pumpkin",
        description="No Description",
        topTextureName="pumpkin_classic_orange",
    ),
    ClothingTopItemType.VampireA: ClothingTopItemDefinition(
        name="Vampire",
        description="No Description",
        topTextureName="vampire_classic_red_cape",
    ),
    ClothingTopItemType.Turtle: ClothingTopItemDefinition(
        name="Turtle",
        description="No Description",
        topTextureName="turtle_classic_green",
    ),
    ClothingTopItemType.VampireB: ClothingTopItemDefinition(
        name="Vampire",
        description="No Description",
        topTextureName="vampire_classic_red",
    ),
    ClothingTopItemType.Toonosaur: ClothingTopItemDefinition(
        name="Toonosaur",
        description="No Description",
        topTextureName="dinosaur_classic_green",
    ),
    ClothingTopItemType.FishingBubble: ClothingTopItemDefinition(
        name="Fishing Bubble",
        description="No Description",
        topTextureName="fish_clown_bubbles",
    ),
    ClothingTopItemType.FORE: ClothingTopItemDefinition(
        name="FORE!",
        description="No Description",
        topTextureName="golf_hole",
    ),
    ClothingTopItemType.GearBusting: ClothingTopItemDefinition(
        name="Gear Busting",
        description="No Description",
        topTextureName="cog_gears",
    ),
    ClothingTopItemType.Snowman: ClothingTopItemDefinition(
        name="Classic Snowman",
        description="No Description",
        topTextureName="snowman_classic_blue",
    ),
    ClothingTopItemType.Snowflakes: ClothingTopItemDefinition(
        name="Classic Snowflakes",
        description="No Description",
        topTextureName="snowflakes_classic_blue",
        topSleeveTextureName="snowman_classic_blue_sleeve",
    ),
    ClothingTopItemType.CandyCaneHearts: ClothingTopItemDefinition(
        name="Candy Cane Hearts",
        description="No Description",
        topTextureName="snowycane_classic_white",
        topSleeveTextureName = "snowyscarf_classic_white_sleeve",
    ),
    ClothingTopItemType.WinterScarf: ClothingTopItemDefinition(
        name="Winter Scarf",
        description="No Description",
        topTextureName="snowyscarf_classic_white",
    ),
    ClothingTopItemType.PinkHeart: ClothingTopItemDefinition(
        name="Pink Heart",
        description="No Description",
        topTextureName="valentoons_heart_pink",
    ),
    ClothingTopItemType.RedHeart: ClothingTopItemDefinition(
        name="Red Heart",
        description="No Description",
        topTextureName="valentoons_heart_pair",
    ),
    ClothingTopItemType.WingedHeart: ClothingTopItemDefinition(
        name="Winged Heart",
        description="No Description",
        topTextureName="valentoons_heart_wings",
    ),
    ClothingTopItemType.FieryHeart: ClothingTopItemDefinition(
        name="Fiery Heart",
        description="No Description",
        topTextureName="valentoons_heart_cool",
    ),
    ClothingTopItemType.Cupid: ClothingTopItemDefinition(
        name="Cupid",
        description="No Description",
        topTextureName="valentoons_cupid_heart",
        topSleeveTextureName="valentoons_cupid_sleeve",
    ),
    ClothingTopItemType.DottedHearts: ClothingTopItemDefinition(
        name="Dotted Hearts",
        description="No Description",
        topTextureName="valentoons_heart_blue",
    ),
    ClothingTopItemType.RedBow: ClothingTopItemDefinition(
        name="Red Bow",
        description="No Description",
        topTextureName="valentoons_bow_wings",
    ),
    ClothingTopItemType.LuckyClover: ClothingTopItemDefinition(
        name="Lucky Clover",
        description="No Description",
        topTextureName="stpat_clover",
    ),
    ClothingTopItemType.PotOGold: ClothingTopItemDefinition(
        name="Pot O' Gold",
        description="No Description",
        topTextureName="stpat_rainbow",
    ),
    ClothingTopItemType.IdesofMarch: ClothingTopItemDefinition(
        name="Ides of March",
        description="No Description",
        topTextureName="stpat_suit",
    ),
    ClothingTopItemType.Fisherman: ClothingTopItemDefinition(
        name="Fisherman",
        description="No Description",
        topTextureName="fish_vest",
    ),
    ClothingTopItemType.Goldfish: ClothingTopItemDefinition(
        name="Goldfish",
        description="No Description",
        topTextureName="pets_fish",
    ),
    ClothingTopItemType.Pawprint: ClothingTopItemDefinition(
        name="Pawprint",
        description="No Description",
        topTextureName="pets_pawprint",
    ),
    ClothingTopItemType.BackpackAndShades: ClothingTopItemDefinition(
        name="Backpack & Shades",
        description="No Description",
        topTextureName="backpack",
    ),
    ClothingTopItemType.Lederhosen: ClothingTopItemDefinition(
        name="Lederhosen",
        description="No Description",
        topTextureName="leder",
    ),
    ClothingTopItemType.Watermelon: ClothingTopItemDefinition(
        name="Watermelon",
        description="No Description",
        topTextureName="watermelon",
    ),
    ClothingTopItemType.RacingFlag: ClothingTopItemDefinition(
        name="Racing Flag",
        description="No Description",
        topTextureName="racing_icon",
    ),
    ClothingTopItemType.AmericanFlag: ClothingTopItemDefinition(
        name="American Flag",
        description="No Description",
        topTextureName="july4_flag",
    ),
    ClothingTopItemType.Fireworks: ClothingTopItemDefinition(
        name="Fireworks",
        description="No Description",
        topTextureName="july4_fireworks",
    ),
    ClothingTopItemType.GreenButtonUp: ClothingTopItemDefinition(
        name="Green Button-Up",
        description="No Description",
        topTextureName="buttonup",
    ),
    ClothingTopItemType.Daisy: ClothingTopItemDefinition(
        name="Daisy",
        description="No Description",
        topTextureName="flower",
    ),
    ClothingTopItemType.BananaPeel: ClothingTopItemDefinition(
        name="Banana Peel",
        description="No Description",
        topTextureName="gag_banana",
    ),
    ClothingTopItemType.BikeHorn: ClothingTopItemDefinition(
        name="Bike Horn",
        description="No Description",
        topTextureName="gag_bikehorn",
    ),
    ClothingTopItemType.HypnoGoggles: ClothingTopItemDefinition(
        name="Hypno Goggles",
        description="No Description",
        topTextureName="gag_goggles",
    ),
    ClothingTopItemType.ClownFish: ClothingTopItemDefinition(
        name="Clown Fish",
        description="Better get your jokebook at the ready!",
        topTextureName="fish_clown",
    ),
    ClothingTopItemType.OldBootA: ClothingTopItemDefinition(
        name="Old Boot",
        description="Pulled right out of the pond!",
        topTextureName="fish_boot_print",
        topSleeveTextureName = "fish_boot_sleeve",
    ),
    ClothingTopItemType.Shirt_GardenMole_Classic: ClothingTopItemDefinition(
        name="Mole",
        description="No Description",
        topTextureName="garden_mole",
    ),
    ClothingTopItemType.Gardening: ClothingTopItemDefinition(
        name="Gardening",
        description="No Description",
        topTextureName="garden_overalls_carrot",
    ),
    ClothingTopItemType.Cupcake: ClothingTopItemDefinition(
        name="Cupcake",
        description="No Description",
        topTextureName="party_cupcake",
    ),
    ClothingTopItemType.PartyHat: ClothingTopItemDefinition(
        name="Party Hat",
        description="No Description",
        topTextureName="party_hat",
    ),
    ClothingTopItemType.RoadsterRaceway: ClothingTopItemDefinition(
        name="Roadster Raceway",
        description="No Description",
        topTextureName="racing_kart",
    ),
    ClothingTopItemType.Roadster: ClothingTopItemDefinition(
        name="Roadster",
        description="No Description",
        topTextureName="racing_roadster",
    ),
    ClothingTopItemType.CoolSun: ClothingTopItemDefinition(
        name="Cool Sun",
        description="No Description",
        topTextureName="summer_sun",
    ),
    ClothingTopItemType.Beachball: ClothingTopItemDefinition(
        name="Red Beach ball",
        description="No Description",
        topTextureName="summer_beach",
    ),
    ClothingTopItemType.DiamondPolo: ClothingTopItemDefinition(
        name="Diamond Polo",
        description="Perfect for when you're batting on the diamond-- Wait, this isn't baseball.",
        topTextureName="golf_checker",
    ),
    ClothingTopItemType.DottedPolo: ClothingTopItemDefinition(
        name="Dotted Polo",
        description="Dots, which are circles, which are like golf balls! It makes sense.",
        topTextureName="golf_bubbles",
    ),
    ClothingTopItemType.GoldMedal: ClothingTopItemDefinition(
        name="Gold Medal",
        description="No Description",
        topTextureName="medal_victory_blue",
    ),
    ClothingTopItemType.SaveTheBuildings: ClothingTopItemDefinition(
        name="Save The Buildings",
        description="No Description",
        topTextureName="no_bldg_law_1",
    ),
    ClothingTopItemType.SaveTheBuildingsNo2: ClothingTopItemDefinition(
        name="Save The Buildings #2",
        description="No Description",
        topTextureName="buildings",
    ),
    ClothingTopItemType.ToontaskCompleter: ClothingTopItemDefinition(
        name="Toontask Completer",
        description="No Description",
        topTextureName="task_hq",
    ),
    ClothingTopItemType.ToontaskCompleterNo2: ClothingTopItemDefinition(
        name="Toontask Completer #2",
        description="No Description",
        topTextureName="task_done",
    ),
    ClothingTopItemType.Trolley: ClothingTopItemDefinition(
        name="Trolley",
        description="No Description",
        topTextureName="trolley_1",
    ),
    ClothingTopItemType.TrolleyNo2: ClothingTopItemDefinition(
        name="Trolley #2",
        description="No Description",
        topTextureName="trolley_2",
    ),
    ClothingTopItemType.WinterGift: ClothingTopItemDefinition(
        name="Winter Gift",
        description="No Description",
        topTextureName="giftbox_classic_blue",
    ),
    ClothingTopItemType.Skeletoon: ClothingTopItemDefinition(
        name="Skeletoon",
        description="No Description",
        topTextureName="skeleton_classic_black",
    ),
    ClothingTopItemType.Cobweb: ClothingTopItemDefinition(
        name="Cobweb",
        description="No Description",
        topTextureName="spider_classic_black",
    ),
    ClothingTopItemType.MostCogsDefeatedA: ClothingTopItemDefinition(
        name="Most Cogs Defeated",
        description="No Description",
        topTextureName="no_cogs_2",
    ),
    ClothingTopItemType.MostVPsDefeated: ClothingTopItemDefinition(
        name="Most VP's Defeated",
        description="No Description",
        topTextureName="icon_vp_purple",
    ),
    ClothingTopItemType.SellbotSmasher: ClothingTopItemDefinition(
        name="Sellbot Smasher",
        description="No Description",
        topTextureName="crusher_sellbot",
    ),
    ClothingTopItemType.Pirate: ClothingTopItemDefinition(
        name="Pirate",
        description="No Description",
        topTextureName="pirate_classic_blue",
        topSleeveTextureName="pirate_classic_white_sleeve",
    ),
    ClothingTopItemType.Supertoon: ClothingTopItemDefinition(
        name="Supertoon",
        description="No Description",
        topTextureName="supertoon_classic_blue",
    ),
    ClothingTopItemType.RacerJumpsuit: ClothingTopItemDefinition(
        name="Racer Jumpsuit",
        description="Guaranteed to be fireproof, bananaproof, and pieproof!",
        topTextureName="racing_prix",
    ),
    ClothingTopItemType.NoTimeforCogBuildings: ClothingTopItemDefinition(
        name="No Time for Cog Buildings",
        description="No Description",
        topTextureName="no_bldg_cash_2",
    ),
    ClothingTopItemType.TrolleyGang: ClothingTopItemDefinition(
        name="Trolley Gang",
        description="No Description",
        topTextureName="trolley_4",
    ),
    ClothingTopItemType.OldBootB: ClothingTopItemDefinition(
        name="Old Boot",
        description="No Description",
        topTextureName="fish_boot",
    ),
    ClothingTopItemType.WitchPolo: ClothingTopItemDefinition(
        name="Witch Polo",
        description="No Description",
        topTextureName="witch_classic_blue",
    ),
    ClothingTopItemType.Sledding: ClothingTopItemDefinition(
        name="Sledding",
        description="No Description",
        topTextureName="sled_classic_blue",
    ),
    ClothingTopItemType.Bat: ClothingTopItemDefinition(
        name="Batty Moon",
        description="No Description",
        topTextureName="bats_classic_purple",
    ),
    ClothingTopItemType.Mittens: ClothingTopItemDefinition(
        name="Mittens",
        description="No Description",
        topTextureName="mittens_classic_blue",
    ),
    ClothingTopItemType.PoolShark: ClothingTopItemDefinition(
        name="Pool Shark",
        description="No Description",
        topTextureName="fish_poolshark",
    ),
    ClothingTopItemType.PianoTuna: ClothingTopItemDefinition(
        name="Piano Tuna",
        description="No Description",
        topTextureName="fish_pianotuna",
    ),
    ClothingTopItemType.GolfStripes: ClothingTopItemDefinition(
        name="Golf Stripes",
        description="No Description",
        topTextureName="golf_stripes",
    ),
    ClothingTopItemType.DummyCogPolo: ClothingTopItemDefinition(
        name="Dummy Cog Polo",
        description="No Description",
        topTextureName="cog_dummy",
    ),
    ClothingTopItemType.MostCogsDefeatedforAnts: ClothingTopItemDefinition(
        name="Most Cogs Defeated for Ants",
        description="No Description",
        topTextureName="no_cogs_1",
    ),
    ClothingTopItemType.TrolleyForAnts: ClothingTopItemDefinition(
        name="Trolley For Ants",
        description="No Description",
        topTextureName="trolley_3",
    ),
    ClothingTopItemType.TrolleySideways: ClothingTopItemDefinition(
        name="Trolley Sideways",
        description="No Description",
        topTextureName="trolley_2",
    ),
    ClothingTopItemType.MostBuildingsDefeated: ClothingTopItemDefinition(
        name="Most Buildings Defeated",
        description="No Description",
        topTextureName="no_bldg_cash_1",
    ),
    ClothingTopItemType.MostCogsDefeatedB: ClothingTopItemDefinition(
        name="Most Cogs Defeated",
        description="No Description",
        topTextureName="no_bldg_law_2",
    ),
    ClothingTopItemType.BirthdayCake: ClothingTopItemDefinition(
        name="Birthday Cake",
        description="No Description",
        topTextureName="anniversary_classic",
    ),
    ClothingTopItemType.LoonyLabsScientistA: ClothingTopItemDefinition(
        name="Loony Labs Scientist A",
        description="No Description",
        topTextureName="scientist_loony_red",
        topSleeveTextureName="scientist_loony_sleeve",
    ),
    ClothingTopItemType.LoonyLabsScientistB: ClothingTopItemDefinition(
        name="Loony Labs Scientist B",
        description="No Description",
        topTextureName="scientist_loony_purple",
        topSleeveTextureName="scientist_loony_sleeve",
    ),
    ClothingTopItemType.LoonyLabsScientistC: ClothingTopItemDefinition(
        name="Loony Labs Scientist C",
        description="No Description",
        topTextureName="scientist_loony_green",
        topSleeveTextureName="scientist_loony_sleeve",
    ),
    ClothingTopItemType.SillyMailbox: ClothingTopItemDefinition(
        name="Silly Mailbox",
        description="No Description",
        topTextureName="loony_mailbox",
    ),
    ClothingTopItemType.SillyTrashCan: ClothingTopItemDefinition(
        name="Silly Trash Can",
        description="No Description",
        topTextureName="loony_trashcan",
    ),
    ClothingTopItemType.LoonyLabsLogo: ClothingTopItemDefinition(
        name="Loony Labs Logo",
        description="No Description",
        topTextureName="loony_logo",
    ),
    ClothingTopItemType.SillyHydrant: ClothingTopItemDefinition(
        name="Silly Hydrant",
        description="A hilariously humorous hydrant!",
        topTextureName="loony_hydrant",
    ),
    ClothingTopItemType.SillyMeterWhistle: ClothingTopItemDefinition(
        name="Silly Whistle",
        description="No Description",
        topTextureName="loony_whistle",
    ),
    ClothingTopItemType.CogCrusherShirt: ClothingTopItemDefinition(
        name="Cog-Crusher Shirt",
        description="The suit for the most masterful of Gag-wielding! If you don't mind looking like a banana.",
        topTextureName="cogCrusher_yellow",
    ),
    ClothingTopItemType.NoMoreCheese: ClothingTopItemDefinition(
        name="No More Cheese!",
        description="Whether you are lactose intolerant, or just don't like Cogs, this is the shirt for you.",
        topTextureName="no_cheese",
    ),
    ClothingTopItemType.FlunkyFlannel: ClothingTopItemDefinition(
        name="Flunky Flannel",
        description="Real spunky.",
        topTextureName="no_flunky",
    ),
    ClothingTopItemType.DefeatedSellbots: ClothingTopItemDefinition(
        name="Defeated Sellbots",
        description="No Description",
        topTextureName="sellbot_logo",
    ),
    ClothingTopItemType.JellybeanJar: ClothingTopItemDefinition(
        name="Jellybean Jar",
        description="No Description",
        topTextureName="jellybeans_classic",
    ),
    ClothingTopItemType.Doodle: ClothingTopItemDefinition(
        name="Doodle",
        description="No Description",
        topTextureName="pets_doodle_classic",
        topSleeveTextureName = "jellybeans_classic",
    ),
    ClothingTopItemType.GetConnected: ClothingTopItemDefinition(
        name="Get Connected",
        description="No Description",
        topTextureName="promo_sbfo",
    ),
    ClothingTopItemType.Bee: ClothingTopItemDefinition(
        name="Bee",
        description="No Description",
        topTextureName="bee_yellow",
    ),
    ClothingTopItemType.Meatballs: ClothingTopItemDefinition(
        name="Meatballs",
        description="You can't actually eat this. Well you COULD, but...",
        topTextureName="meatball_yellow",
    ),
    ClothingTopItemType.TrashcatsRags: ClothingTopItemDefinition(
        name="Trashcat's Rags",
        description="No Description",
        topTextureName="npc_travis",
    ),
    ClothingTopItemType.DrowsyDreamland: ClothingTopItemDefinition(
        name="Drowsy Dreamland",
        description="No Description",
        topTextureName="dreamland",
    ),
    ClothingTopItemType.BetaToon: ClothingTopItemDefinition(
        name="Purple Beta Toon",
        description="No Description",
        topTextureName="beta_purple",
    ),
    ClothingTopItemType.YOTTKnight: ClothingTopItemDefinition(
        name="YOTT Knight",
        description="No Description",
        topTextureName="knight",
    ),
    ClothingTopItemType.BBSailor: ClothingTopItemDefinition(
        name="BB Sailor",
        description="No Description",
        topTextureName="boatyard_sailor_blue",
    ),
    ClothingTopItemType.DGGardening: ClothingTopItemDefinition(
        name="DG Gardening",
        description="No Description",
        topTextureName="garden_outfit",
    ),
    ClothingTopItemType.Shirt_TTC_Firefighter: ClothingTopItemDefinition(
        name="TTC Firefighter",
        description="No Description",
        topTextureName="ttc_firefighter",
    ),
    ClothingTopItemType.MMLBand: ClothingTopItemDefinition(
        name="MML Band",
        description="No Description",
        topTextureName="mml_band",
    ),
    ClothingTopItemType.TeamBarnyard: ClothingTopItemDefinition(
        name="Team Barnyard",
        description="No Description",
        topTextureName="barnyard_overalls",
    ),
    ClothingTopItemType.TeamOutback: ClothingTopItemDefinition(
        name="Team Outback",
        description="No Description",
        topTextureName="outback_outfit",
    ),
    ClothingTopItemType.BarnyardVacation: ClothingTopItemDefinition(
        name="Barnyard Vacation",
        description="No Description",
        topTextureName="barnyard_victory_red",
    ),
    ClothingTopItemType.OutbackVacation: ClothingTopItemDefinition(
        name="Outback Vacation",
        description="No Description",
        topTextureName="outback_victory",
    ),
    ClothingTopItemType.AAParkRanger: ClothingTopItemDefinition(
        name="AA Park Ranger",
        description="No Description",
        topTextureName="ranger",
    ),
    ClothingTopItemType.BrrrghSnowflakes: ClothingTopItemDefinition(
        name="Brrrgh Snowflakes",
        description="No Description",
        topTextureName="sweater_brrrgh_blue",
    ),
    ClothingTopItemType.Alchemist: ClothingTopItemDefinition(
        name="Alchemist",
        description="No Description",
        topTextureName="alchemist_straps_blue",
        topSleeveTextureName="alchemist_blue_sleeve",
    ),
    ClothingTopItemType.AlchemistOveralls: ClothingTopItemDefinition(
        name="Alchemist Overalls",
        description="No Description",
        topTextureName="alchemist_overalls_blue",
        topSleeveTextureName="alchemist_blue_sleeve",
    ),
    ClothingTopItemType.Frankentoon: ClothingTopItemDefinition(
        name="Frankentoon",
        description="No Description",
        topTextureName="frankenstein_green",
    ),
    ClothingTopItemType.Spacetoon: ClothingTopItemDefinition(
        name="Spacetoon",
        description="No Description",
        topTextureName="moonsuit_white",
    ),
    ClothingTopItemType.MadScientist: ClothingTopItemDefinition(
        name="Mad Scientist",
        description="No Description",
        topTextureName="scientist_mad_white",
    ),
    ClothingTopItemType.Clown: ClothingTopItemDefinition(
        name="Clown",
        description="No Description",
        topTextureName="clown_suspenders_rainbow",
    ),
    ClothingTopItemType.Wonderland: ClothingTopItemDefinition(
        name="Wonderland",
        description="No Description",
        topTextureName="wonderland_blue",
    ),
    ClothingTopItemType.Reaper: ClothingTopItemDefinition(
        name="Reaper",
        description="No Description",
        topTextureName="reaper_purple",
    ),
    ClothingTopItemType.Scarecrow: ClothingTopItemDefinition(
        name="Scarecrow",
        description="No Description",
        topTextureName="scarecrow_jacket_1",
        topSleeveTextureName="scarecrow_1_sleeve",
    ),
    ClothingTopItemType.ScarecrowOveralls: ClothingTopItemDefinition(
        name="Scarecrow Overalls",
        description="No Description",
        topTextureName="scarecrow_overalls_1",
        topSleeveTextureName="scarecrow_1_sleeve",
    ),
    ClothingTopItemType.Wizard: ClothingTopItemDefinition(
        name="Purple Witch Outfit",
        description="No Description",
        topTextureName="witch_purple",
    ),
    ClothingTopItemType.GreenElfShirt: ClothingTopItemDefinition(
        name="Green Elf Shirt",
        description="No Description",
        topTextureName="elf_green",
    ),
    ClothingTopItemType.RedElfShirt: ClothingTopItemDefinition(
        name="Red Elf Shirt",
        description="No Description",
        topTextureName="elf_red",
    ),
    ClothingTopItemType.GingerbreadA: ClothingTopItemDefinition(
        name="Gingerbread",
        description="No Description",
        topTextureName="gingerbread_1",
        topSleeveTextureName="gingerbread_sleeve",
    ),
    ClothingTopItemType.GingerbreadB: ClothingTopItemDefinition(
        name="Gingerbread",
        description="No Description",
        topTextureName="gingerbread_2",
        topSleeveTextureName="gingerbread_sleeve",
    ),
    ClothingTopItemType.PresentUniform: ClothingTopItemDefinition(
        name="Present Uniform",
        description="No Description",
        topTextureName="santa_red",
    ),
    ClothingTopItemType.RagdollHumble: ClothingTopItemDefinition(
        name="Ragdoll Humble",
        description="No Description",
        topTextureName="ragdoll_humble_blue",
    ),
    ClothingTopItemType.RagdollRegal: ClothingTopItemDefinition(
        name="Ragdoll Regal",
        description="No Description",
        topTextureName="ragdoll_regal_green",
    ),
    ClothingTopItemType.RagdollTraditional: ClothingTopItemDefinition(
        name="Ragdoll Traditional",
        description="No Description",
        topTextureName="ragdoll_tradi_red",
    ),
    ClothingTopItemType.Reindeer: ClothingTopItemDefinition(
        name="Reindeer",
        description="No Description",
        topTextureName="reindeer",
    ),
    ClothingTopItemType.TinSoldierHumble: ClothingTopItemDefinition(
        name="Tin Soldier Humble",
        description="No Description",
        topTextureName="soldier_humble_blue",
    ),
    ClothingTopItemType.TinSoldierRegal: ClothingTopItemDefinition(
        name="Tin Soldier Regal",
        description="No Description",
        topTextureName="soldier_regal_green",
    ),
    ClothingTopItemType.TinSoldierTraditional: ClothingTopItemDefinition(
        name="Tin Soldier Traditional",
        description="No Description",
        topTextureName="soldier_tradi_red",
    ),
    ClothingTopItemType.UglySweater: ClothingTopItemDefinition(
        name="Ugly Sweater",
        description="No Description",
        topTextureName="sweater_xmasdeer_green",
    ),
    ClothingTopItemType.VintageSnowShirt: ClothingTopItemDefinition(
        name="Vintage Snow Shirt",
        description="No Description",
        topTextureName="vintage_ski_purple",
    ),
    ClothingTopItemType.NY2019Suit: ClothingTopItemDefinition(
        name="2019 Suit",
        description="No Description",
        topTextureName="nye_19_suit",
    ),
    ClothingTopItemType.NY2019Dress: ClothingTopItemDefinition(
        name="2019 Dress",
        description="No Description",
        topTextureName="nye_19_dress",
    ),
    ClothingTopItemType.CupidOutfit: ClothingTopItemDefinition(
        name="Cupid Outfit",
        description="No Description",
        topTextureName="valentoons_cupid",
    ),
    ClothingTopItemType.DoesShirt: ClothingTopItemDefinition(
        name="Doe's Shirt",
        description="No Description",
        topTextureName="npc_doe",
    ),
    ClothingTopItemType.WebstersShirt: ClothingTopItemDefinition(
        name="Webster's Shirt",
        description="No Description",
        topTextureName="npc_webster",
    ),
    ClothingTopItemType.AngelWings: ClothingTopItemDefinition(
        name="Angel Wings",
        description="No Description",
        topTextureName="wings_angel_blue",
    ),
    ClothingTopItemType.AviatorShirt: ClothingTopItemDefinition(
        name="Aviator Shirt",
        description="Sky Clan, here we come!",
        topTextureName="aviator_brown",
    ),
    ClothingTopItemType.WingsuitShirt: ClothingTopItemDefinition(
        name="Wingsuit Shirt",
        description="It might allow you to fly... not Loony Labs certified.",
        topTextureName="wingsuit",
    ),
    ClothingTopItemType.DragonWings: ClothingTopItemDefinition(
        name="Dragon Wings",
        description="No Description",
        topTextureName="wings_dragon_green",
    ),
    ClothingTopItemType.ChibiWings: ClothingTopItemDefinition(
        name="Chibi Wings",
        description="No Description",
        topTextureName="wings_chibi_red",
    ),
    ClothingTopItemType.BurgerShirt: ClothingTopItemDefinition(
        name="Burger Shirt",
        description="No Description",
        topTextureName="hamburger",
    ),
    ClothingTopItemType.SellbotSeeker: ClothingTopItemDefinition(
        name="Sellbot Seeker",
        description="No Description",
        topTextureName="dept_sellbot",
    ),
    ClothingTopItemType.CashbotCatcher: ClothingTopItemDefinition(
        name="Cashbot Catcher",
        description="No Description",
        topTextureName="dept_cashbot",
    ),
    ClothingTopItemType.LawbotLiberator: ClothingTopItemDefinition(
        name="Lawbot Liberator",
        description="No Description",
        topTextureName="dept_lawbot",
    ),
    ClothingTopItemType.BossbotBasher: ClothingTopItemDefinition(
        name="Bossbot Basher ",
        description="No Description",
        topTextureName="dept_bossbot",
    ),
    ClothingTopItemType.OutbackUniform: ClothingTopItemDefinition(
        name="Outback Uniform",
        description="No Description",
        topTextureName="outback_uniform",
    ),
    ClothingTopItemType.OutbackDenim: ClothingTopItemDefinition(
        name="Outback Denim",
        description="No Description",
        topTextureName="outback_jacket",
    ),
    ClothingTopItemType.AlienShirt: ClothingTopItemDefinition(
        name="Alien Shirt",
        description="No Description",
        topTextureName="alien_purple",
    ),
    ClothingTopItemType.CandyCornShirt: ClothingTopItemDefinition(
        name="Candy Corn Shirt",
        description="No Description",
        topTextureName="candycorn_1",
    ),
    ClothingTopItemType.Busted: ClothingTopItemDefinition(
        name="Busted!",
        description="No Description",
        topTextureName="btl_jail",
    ),
    ClothingTopItemType.LawbotResistance: ClothingTopItemDefinition(
        name="Lawbot Resistance",
        description="No Description",
        topTextureName="crusher_lawbot",
    ),
    ClothingTopItemType.RetroRobotShirt: ClothingTopItemDefinition(
        name="Retro Robot Shirt",
        description="No Description",
        topTextureName="retrobot_teal",
    ),
    ClothingTopItemType.RidingHoodShirt: ClothingTopItemDefinition(
        name="Riding Hood Shirt",
        description="No Description",
        topTextureName="ridinghood_red",
    ),
    ClothingTopItemType.NurseShirt: ClothingTopItemDefinition(
        name="Nurse Shirt",
        description="Laugh your way to good laff!",
        topTextureName="nurse_white",
    ),
    ClothingTopItemType.LazyBonesShirt: ClothingTopItemDefinition(
        name="Lazy Bones Shirt",
        description="No Description",
        topTextureName="sans_blue",
    ),
    ClothingTopItemType.SailorShirtA: ClothingTopItemDefinition(
        name="Sailor Shirt A",
        description="No Description",
        topTextureName="sailor_white",
    ),
    ClothingTopItemType.SailorShirtB: ClothingTopItemDefinition(
        name="Sailor Shirt B",
        description="No Description",
        topTextureName="sailor_button_white",
        topSleeveTextureName = "sailor_white_sleeve",
    ),
    ClothingTopItemType.BlueSailorShirtA: ClothingTopItemDefinition(
        name="Blue Sailor Shirt A",
        description="No Description",
        topTextureName="sailor_blue",
    ),
    ClothingTopItemType.BlueSailorShirtB: ClothingTopItemDefinition(
        name="Blue Sailor Shirt B",
        description="No Description",
        topTextureName="sailor_button_blue",
        topSleeveTextureName = "sailor_blue",
    ),
    ClothingTopItemType.CyanSailorShirtA: ClothingTopItemDefinition(
        name="Cyan Sailor Shirt A",
        description="No Description",
        topTextureName="sailor_cyan",
    ),
    ClothingTopItemType.CyanSailorShirtB: ClothingTopItemDefinition(
        name="Cyan Sailor Shirt B",
        description="No Description",
        topTextureName="sailor_button_cyan",
        topSleeveTextureName = "sailor_cyan",
    ),
    ClothingTopItemType.GreenSailorShirtA: ClothingTopItemDefinition(
        name="Green Sailor Shirt A",
        description="No Description",
        topTextureName="sailor_green",
    ),
    ClothingTopItemType.GreenSailorShirtB: ClothingTopItemDefinition(
        name="Green Sailor Shirt B",
        description="No Description",
        topTextureName="sailor_button_green",
        topSleeveTextureName = "sailor_green",
    ),
    ClothingTopItemType.OrangeSailorShirtA: ClothingTopItemDefinition(
        name="Orange Sailor Shirt A",
        description="No Description",
        topTextureName="sailor_orange",
    ),
    ClothingTopItemType.OrangeSailorShirtB: ClothingTopItemDefinition(
        name="Orange Sailor Shirt B",
        description="No Description",
        topTextureName="sailor_button_orange",
        topSleeveTextureName = "sailor_orange",
    ),
    ClothingTopItemType.PinkSailorShirtA: ClothingTopItemDefinition(
        name="Pink Sailor Shirt A",
        description="No Description",
        topTextureName="sailor_pink",
    ),
    ClothingTopItemType.PinkSailorShirtB: ClothingTopItemDefinition(
        name="Pink Sailor Shirt B",
        description="No Description",
        topTextureName="sailor_button_pink",
        topSleeveTextureName = "sailor_pink",

    ),
    ClothingTopItemType.PurpleSailorShirtA: ClothingTopItemDefinition(
        name="Purple Sailor Shirt A",
        description="No Description",
        topTextureName="sailor_purple",
    ),
    ClothingTopItemType.PurpleSailorShirtB: ClothingTopItemDefinition(
        name="Purple Sailor Shirt B",
        description="No Description",
        topSleeveTextureName = "sailor_purple",
        topTextureName="sailor_button_purple",
    ),
    ClothingTopItemType.RedSailorShirtA: ClothingTopItemDefinition(
        name="Red Sailor Shirt A",
        description="No Description",
        topTextureName="sailor_red",
    ),
    ClothingTopItemType.RedSailorShirtB: ClothingTopItemDefinition(
        name="Red Sailor Shirt B",
        description="No Description",
        topTextureName="sailor_button_red",
        topSleeveTextureName = "sailor_red",
    ),
    ClothingTopItemType.BlackSailorShirtA: ClothingTopItemDefinition(
        name="Black Sailor Shirt A",
        description="No Description",
        topTextureName="sailor_black",
    ),
    ClothingTopItemType.BlackSailorShirtB: ClothingTopItemDefinition(
        name="Black Sailor Shirt B",
        description="No Description",
        topTextureName="sailor_button_black",
        topSleeveTextureName = "sailor_black",
    ),
    ClothingTopItemType.GoldenSailorShirtA: ClothingTopItemDefinition(
        name="Golden Sailor Shirt A",
        description="No Description",
        topTextureName="sailor_yellow",
    ),
    ClothingTopItemType.GoldenSailorShirtB: ClothingTopItemDefinition(
        name="Golden Sailor Shirt B",
        description="No Description",
        topTextureName="sailor_button_yellow",
        topSleeveTextureName = "sailor_yellow",
    ),
    ClothingTopItemType.TeamTreesShirt: ClothingTopItemDefinition(
        name="Team Trees Shirt",
        description="No Description",
        topTextureName="tree",
    ),
    ClothingTopItemType.HomemadeRagdoll: ClothingTopItemDefinition(
        name="Homemade Ragdoll",
        description="No Description",
        topTextureName="ragdoll_homemade_yellow",
    ),
    ClothingTopItemType.HomemadeSoldier: ClothingTopItemDefinition(
        name="Homemade Soldier",
        description="No Description",
        topTextureName="soldier_homemade_yellow",
    ),
    ClothingTopItemType.RetroWinterSuit: ClothingTopItemDefinition(
        name="Retro Winter Suit",
        description="No Description",
        topTextureName="retrowin_green_1",
        topSleeveTextureName = "retrowin_green_sleeve",
    ),
    ClothingTopItemType.RetroWinterDress: ClothingTopItemDefinition(
        name="Retro Winter Dress",
        description="No Description",
        topTextureName="retrowin_green_2",
        topSleeveTextureName = "retrowin_green_sleeve",
    ),
    ClothingTopItemType.SnowmanShirt: ClothingTopItemDefinition(
        name="Snowman Shirt",
        description="No Description",
        topTextureName="snowtoon",
    ),
    ClothingTopItemType.NewYears2020: ClothingTopItemDefinition(
        name="New Year's 2020",
        description="No Description",
        topTextureName="nye_20",
    ),
    ClothingTopItemType.ValentoonsShirt: ClothingTopItemDefinition(
        name="Valentoon's Shirt",
        description="No Description",
        topTextureName="valentoons_luretrap",
    ),
    ClothingTopItemType.AgentSevensShirt: ClothingTopItemDefinition(
        name="Agent Seven's Shirt",
        description="No Description",
        topTextureName="agent_seven_red",
    ),
    ClothingTopItemType.StPats2020: ClothingTopItemDefinition(
        name="St. Pat's 2020",
        description="No Description",
        topTextureName="stpat_lucky",
    ),
    ClothingTopItemType.ClownShirt: ClothingTopItemDefinition(
        name="Clown Shirt",
        description="Who thought Toons could get any sillier?",
        topTextureName="clown_strap_red",
    ),
    ClothingTopItemType.SevenStriped: ClothingTopItemDefinition(
        name="Seven Striped",
        description="Jackpot!",
        topTextureName="jersey_seven_green",
    ),
    ClothingTopItemType.TripleRainbow: ClothingTopItemDefinition(
        name="Triple Rainbow",
        description="Triple rainbow! What does it mean?",
        topTextureName="jacket_tripRainbow_blue",
    ),
    ClothingTopItemType.BoardbotShirt: ClothingTopItemDefinition(
        name="Boardbot Shirt",
        description="No Description",
        topTextureName="suit_boardbot_teal",
    ),
    ClothingTopItemType.BoredbotShirt: ClothingTopItemDefinition(
        name="Boredbot Shirt",
        description="No Description",
        topTextureName="boredbot_black",
    ),
    ClothingTopItemType.JesterShirt: ClothingTopItemDefinition(
        name="Jester Shirt",
        description="Popularized in Ye Olde Toontowne!",
        topTextureName="jester_red",
    ),
    ClothingTopItemType.BlackJesterShirt: ClothingTopItemDefinition(
        name="Black Jester Shirt",
        description="Popularized in Ye Olde Toontowne!",
        topTextureName="jester_black",
    ),
    ClothingTopItemType.Easter2020: ClothingTopItemDefinition(
        name="Easter 2020",
        description="No Description",
        topTextureName="easter_bunny",
    ),
    ClothingTopItemType.ExecutiveBoardbot: ClothingTopItemDefinition(
        name="Executive Boardbot",
        description="No Description",
        topTextureName="suit_boardbot_black",
    ),
    ClothingTopItemType.LawbotSuitTop: ClothingTopItemDefinition(
        name="Lawbot Suit Top",
        description="No Description",
        topTextureName="suit_lawbot_blue",
    ),
    ClothingTopItemType.CooktheCogsShirt: ClothingTopItemDefinition(
        name="Cook the Cogs Shirt",
        description="No Description",
        topTextureName="july4_cook",
    ),
    ClothingTopItemType.VacationFroge: ClothingTopItemDefinition(
        name="Vacation Froge",
        description="No Description",
        topTextureName="froge_purple",
    ),
    ClothingTopItemType.PhantoonShirt: ClothingTopItemDefinition(
        name="Phantoon Shirt",
        description="No Description",
        topTextureName="phantoon_black",
    ),
    ClothingTopItemType.VolunteerRanger: ClothingTopItemDefinition(
        name="Volunteer Ranger",
        description="No Description",
        topTextureName="btl_volunteer",
    ),
    ClothingTopItemType.ToonsmasPast: ClothingTopItemDefinition(
        name="Toonsmas Past",
        description="No Description",
        topTextureName="past_yellow",
    ),
    ClothingTopItemType.ToonsmasPresent: ClothingTopItemDefinition(
        name="Toonsmas Present",
        description="No Description",
        topTextureName="present_green",
    ),
    ClothingTopItemType.ToonsmasFuture: ClothingTopItemDefinition(
        name="Toonsmas Future",
        description="No Description",
        topTextureName="future_black",
    ),
    ClothingTopItemType.NewYears2021: ClothingTopItemDefinition(
        name="New Year's 2021",
        description="No Description",
        topTextureName="nye_21",
    ),
    ClothingTopItemType.TumblesShirt: ClothingTopItemDefinition(
        name="Tumbles' Shirt",
        description="No Description",
        topTextureName="tumbles_green",
    ),
    ClothingTopItemType.Valentoons2021: ClothingTopItemDefinition(
        name="Valentoon's 2021",
        description="No Description",
        topTextureName="valentoons_strawberry",
    ),
    ClothingTopItemType.HallowopolisShirt: ClothingTopItemDefinition(
        name="Hallowopolis Shirt",
        description="No Description",
        topTextureName="hwtown_black",
    ),
    ClothingTopItemType.Detective: ClothingTopItemDefinition(
        name="Detective",
        description="No Description",
        topTextureName="detective_brown",
    ),
    ClothingTopItemType.TwoPocketCargo: ClothingTopItemDefinition(
        name="Two-Pocket Cargo",
        description="No Description",
        topTextureName="cargo_blue",
    ),
    ClothingTopItemType.JacketAndFlannel: ClothingTopItemDefinition(
        name="Jacket + Flannel",
        description="No Description",
        topTextureName="flyjacket_red",
    ),
    ClothingTopItemType.BlueNewstoon: ClothingTopItemDefinition(
        name="Blue Newstoon",
        description="No Description",
        topTextureName="newstoon_blue",
    ),
    ClothingTopItemType.GrayNewstoon: ClothingTopItemDefinition(
        name="Gray Newstoon",
        description="No Description",
        topTextureName="newstoon_gray",
    ),
    ClothingTopItemType.ChupShirt: ClothingTopItemDefinition(
        name="Chup Shirt",
        description="No Description",
        topTextureName="chupbottle",
    ),
    ClothingTopItemType.NewYears2022: ClothingTopItemDefinition(
        name="New Year's 2022",
        description="No Description",
        topTextureName="nye_22",
    ),
    ClothingTopItemType.Valentoons2022: ClothingTopItemDefinition(
        name="Valentoon's 2022",
        description="No Description",
        topTextureName="valentoons_jacket",
    ),
    ClothingTopItemType.DoctorToonShirt: ClothingTopItemDefinition(
        name="Doctor Toon Shirt",
        description="No Description",
        topTextureName="doctor_toon",
    ),
    ClothingTopItemType.TrolleyEngineerShirt: ClothingTopItemDefinition(
        name="Trolley Engineer Shirt",
        description="All aboard!",
        topTextureName="engineer",
    ),
    ClothingTopItemType.ArtisticShirt: ClothingTopItemDefinition(
        name="Artistic Shirt",
        description="Show off your true artistic passion!",
        topTextureName="artistic",
    ),
    ClothingTopItemType.StarstruckShirt: ClothingTopItemDefinition(
        name="Starstruck Shirt",
        description="You'll outshine the moon with this one!",
        topTextureName="moon",
    ),
    ClothingTopItemType.RetroShirt: ClothingTopItemDefinition(
        name="Retro Shirt",
        description="Friday night fever!",
        topTextureName="funky",
    ),
    ClothingTopItemType.BattleJacket: ClothingTopItemDefinition(
        name="Battle Jacket",
        description="Seek and destroy the cogs!",
        topTextureName="battlejacket",
    ),
    ClothingTopItemType.GumballMachineShirt: ClothingTopItemDefinition(
        name="Gumball Machine Shirt",
        description="Full of flavor!",
        topTextureName="gumball",
    ),
    ClothingTopItemType.CardSuitShirtA: ClothingTopItemDefinition(
        name="Card Suit Shirt",
        description="Got a card up your sleeve?",
        topTextureName="cards_tie",
    ),
    ClothingTopItemType.CardSuitShirtB: ClothingTopItemDefinition(
        name="Card Suit Shirt",
        description="Got a card up your sleeve?",
        topTextureName="cards_vest",
    ),
    ClothingTopItemType.SchoolhouseFlannel: ClothingTopItemDefinition(
        name="Schoolhouse Flannel",
        description="Show your school spirit!",
        topTextureName="flannel_schoolhouse",
    ),
    ClothingTopItemType.SleepwalkerShirt: ClothingTopItemDefinition(
        name="Sleepwalker Shirt",
        description="Sleep tight!",
        topTextureName="sleepwalker",
    ),
    ClothingTopItemType.FruitPieShirt: ClothingTopItemDefinition(
        name="Fruit Pie Shirt",
        description="Tastes good, too!",
        topTextureName="fruitpie",
    ),
    ClothingTopItemType.Shirt_Donut_Pink: ClothingTopItemDefinition(
        name="Pink Donut Shirt",
        description="Frosted to perfection!",
        topTextureName="donut_pink",
    ),
    ClothingTopItemType.Shirt_Donut_Blue: ClothingTopItemDefinition(
        name="Blue Donut Shirt",
        description="Frosted to perfection!",
        topTextureName="donut_blue",
    ),
    ClothingTopItemType.Shirt_Donut_Chocolate: ClothingTopItemDefinition(
        name="Chocolate Donut Shirt",
        description="Frosted to perfection!",
        topTextureName="donut_chocolate",
    ),
    ClothingTopItemType.Shirt_Donut_Lemon: ClothingTopItemDefinition(
        name="Lemon Donut Shirt",
        description="Frosted to perfection!",
        topTextureName="donut_lemon",
    ),
    ClothingTopItemType.Shirt_Donut_Vanilla: ClothingTopItemDefinition(
        name="Vanilla Donut Shirt",
        description="Frosted to perfection!",
        topTextureName="donut_vanilla",
    ),
    ClothingTopItemType.BluePainter: ClothingTopItemDefinition(
        name="Blue Painter",
        description="Paint not included.",
        topTextureName="painter_blue",
    ),
    ClothingTopItemType.RedPainter: ClothingTopItemDefinition(
        name="Red Painter",
        description="Paint not included.",
        topTextureName="painter_red",
    ),
    ClothingTopItemType.GreenPainter: ClothingTopItemDefinition(
        name="Green Painter",
        description="Paint not included.",
        topTextureName="painter_green",
    ),
    ClothingTopItemType.YellowPainter: ClothingTopItemDefinition(
        name="Yellow Painter",
        description="Paint not included.",
        topTextureName="painter_yellow",
    ),
    ClothingTopItemType.ChefCoat: ClothingTopItemDefinition(
        name="Chef Coat",
        description="No Description",
        topTextureName="chef",
    ),
    ClothingTopItemType.NewYears2023: ClothingTopItemDefinition(
        name="New Year's 2023",
        description="No Description",
        topTextureName="nye_23",
    ),
    ClothingTopItemType.ArmoredChestplate: ClothingTopItemDefinition(
        name="Armored Chestplate",
        description="No Description",
        topTextureName="miniboss_armor",
    ),
    ClothingTopItemType.RejectedSweater: ClothingTopItemDefinition(
        name="Rejected Sweater",
        description="No Description",
        topTextureName="sweater_plants",
    ),
    ClothingTopItemType.HighRollersSuit: ClothingTopItemDefinition(
        name="High Roller's Suit",
        description="No Description",
        topTextureName="suit_hroller_white",
    ),
    ClothingTopItemType.HighRollersProdigalSuit: ClothingTopItemDefinition(
        name="High Roller's Prodigal Suit",
        description="No Description",
        topTextureName="suit_hroller_black",
    ),
    ClothingTopItemType.CybertoonShirt: ClothingTopItemDefinition(
        name="CyberToon Shirt",
        description="No Description",
        topTextureName="cyberpunk",
    ),
    ClothingTopItemType.BroVinci: ClothingTopItemDefinition(
        name="Bro Vinci's Shirt",
        description="No Description",
        topTextureName="npc_bro",
    ),
    ClothingTopItemType.GhostPirateShirt: ClothingTopItemDefinition(
        name="Ghost Pirate Shirt",
        description="No Description",
        topTextureName="pirate_ghost_green",
    ),
    ClothingTopItemType.ToonSpyShirt: ClothingTopItemDefinition(
        name="Toon Spy Shirt",
        description="No Description",
        topTextureName="spy_purple",
    ),
    ClothingTopItemType.NewYears2024: ClothingTopItemDefinition(
        name="New Year's 2024",
        description="No Description",
        topTextureName="nye_24",
    ),
}
