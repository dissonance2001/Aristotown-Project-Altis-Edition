"""
This module contains the item data for shoes.
"""
from __future__ import annotations
from panda3d.core import NodePath, Texture

from toontown.inventory.base.InventoryItem import InventoryItem
from typing import Dict, Optional
from strenum import StrEnum

from toontown.inventory.definitions.AccessoryDefinition import AccessoryDefinition
from toontown.inventory.enums.ItemEnums import ShoeItemType
from toontown.inventory.enums.ItemTags import ItemTag
from toontown.toonbase import ProcessGlobals


class ShoeType(StrEnum):
    Shoes       = 'shoes'
    BootsShort  = 'boots_short'
    BootsLong   = 'boots_long'


baseTexturePath = "cosmetics/shoes/maps/"
baseModelPath = "cosmetics/"
textureExtension = ".png"


class ShoeItemDefinition(AccessoryDefinition):
    """
    The definition structure for eating a shoe.
    """
    # preload leg model for optimization purposes
    if ProcessGlobals.getCurrentProcess() == ProcessGlobals.Process.Client:
        legModel = loader.loadModel('phase_3/models/char/toons/legs/tt_a_chr_dgm_shorts_legs_1000')

    def __init__(self,
                 textureName,
                 shoeType: ShoeType,
                 textureNameBootsShort: str | None = None,
                 textureNameBootsLong: str | None = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.shoeType = shoeType
        self.textureName = textureName

        # Specific texpath overrides for BootsShort and BootsLong
        self.textureNameBootsShort = textureNameBootsShort
        self.textureNameBootsLong = textureNameBootsLong

    def getItemTypeName(self):
        return 'Shoes'

    def getShoeType(self) -> ShoeType:
        return self.shoeType

    def getTexturePath(self):
        if self.getShoeType() == ShoeType.BootsShort and self.textureNameBootsShort:
            return baseTexturePath + self.textureNameBootsShort + textureExtension
        if self.getShoeType() == ShoeType.BootsLong and self.textureNameBootsLong:
            return baseTexturePath + self.textureNameBootsLong + textureExtension
        return baseTexturePath + self.textureName + textureExtension

    def getTags(self, item: 'InventoryItem') -> set[ItemTag]:
        tags = super().getTags(item)
        tags.add(ItemTag.Shoes)
        return tags

    def makeItemModel(self, *extraArgs, item: Optional[InventoryItem] = None) -> NodePath:
        # Load model.
        model = NodePath('feet')
        found = self.legModel.find('**/' + str(self.getShoeType()))
        if found.isEmpty():
            # NOTE: asset-content gap, not a code bug -- see ProfileBackgroundRegistry.
            return model
        model = found.copyTo(model)

        # Apply texture if need be.
        textureName = self.getTexturePath()
        if textureName:
            texture = loader.loadTexture(textureName)
            texture.setMinfilter(Texture.FTLinearMipmapLinear)
            texture.setMagfilter(Texture.FTLinear)
            model.setTexture(texture, 1)

        # Return model.
        return model


# The registry dictionary for shoes.
ShoeRegistry: Dict[ShoeItemType, ShoeItemDefinition] = {
    ShoeItemType.GreenAthleticShoes: ShoeItemDefinition(
        name="Green Athletic Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_athleticGreen",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.RedAthleticShoes: ShoeItemDefinition(
        name="Red Athletic Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_athleticRed",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.GreenToonBoots: ShoeItemDefinition(
        name="Green Toon Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_docMartinBootsGreen",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_docMartinBootsGreenLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.GreenSneakers: ShoeItemDefinition(
        name="Green Sneakers",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_converseStyleGreen",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.BoatShoes: ShoeItemDefinition(
        name="Boat Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_deckShoes",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.YellowAthleticShoes: ShoeItemDefinition(
        name="Yellow Athletic Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_athleticYellow",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.BlackSneakers: ShoeItemDefinition(
        name="Black Sneakers",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_converseStyleBlack",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.WhiteSneakers: ShoeItemDefinition(
        name="White Sneakers",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_converseStyleWhite",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.PinkSneakers: ShoeItemDefinition(
        name="Pink Sneakers",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_converseStylePink",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.CowboyBoots: ShoeItemDefinition(
        name="Cowboy Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_cowboyBoots",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_cowboyBootsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.GreenHiTops: ShoeItemDefinition(
        name="Green Hi-Tops",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_hiTopSneakers",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.RedSuperToonBoots: ShoeItemDefinition(
        name="Red Super Toon Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_superToonRedBoots",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_superToonRedBootsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.GreenTennisShoes: ShoeItemDefinition(
        name="Green Tennis Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_tennisShoesGreen",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.PinkTennisShoes: ShoeItemDefinition(
        name="Pink Tennis Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_tennisShoesPink",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.RedSneakers: ShoeItemDefinition(
        name="Red Sneakers",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_converseStyleRed",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.AquaToonBoots: ShoeItemDefinition(
        name="Aqua Toon Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_docMartinBootsAqua",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_docMartinBootsAquaLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.BrownToonBoots: ShoeItemDefinition(
        name="Brown Toon Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_docMartinBootsBrown",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_docMartinBootsBrownLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.YellowToonBoots: ShoeItemDefinition(
        name="Yellow Toon Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_docMartinBootsYellow",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_docMartinBootsYellowLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.Loafers: ShoeItemDefinition(
        name="Loafers",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_loafers",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.MotorcycleBoots: ShoeItemDefinition(
        name="Motorcycle Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_motorcycleBoots",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_motorcycleBootsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.Oxfords: ShoeItemDefinition(
        name="Oxfords",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_oxfords",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.PinkRainBoots: ShoeItemDefinition(
        name="Pink Rain Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_rainBootsPink",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_rainBootsPinkLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.JollyBoots: ShoeItemDefinition(
        name="Jolly Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_santaBoots",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_santaBootsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.BeigeWinterBoots: ShoeItemDefinition(
        name="Beige Winter Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_winterBootsBeige",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_winterBootsBeigeLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.PinkWinterBoots: ShoeItemDefinition(
        name="Pink Winter Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_winterBootsPink",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_winterBootsPinkLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.WorkBoots: ShoeItemDefinition(
        name="Work Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_workBoots",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.YellowSneakers: ShoeItemDefinition(
        name="Yellow Sneakers",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_converseStyleYellow",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.PinkToonBoots: ShoeItemDefinition(
        name="Pink Toon Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_docMartinBootsPink",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_docMartinBootsPinkLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.PinkHiTops: ShoeItemDefinition(
        name="Pink Hi-Tops",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_hiTopSneakersPink",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.RedDotsRainBoots: ShoeItemDefinition(
        name="Red Dots Rain Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_rainBootsRedDots",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_rainBootsRedDotsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.PurpleTennisShoes: ShoeItemDefinition(
        name="Purple Tennis Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_tennisShoesPurple",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.VioletTennisShoes: ShoeItemDefinition(
        name="Violet Tennis Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_tennisShoesViolet",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.YellowTennisShoes: ShoeItemDefinition(
        name="Yellow Tennis Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_tennisShoesYellow",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.BlueRainBoots: ShoeItemDefinition(
        name="Blue Rain Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_rainBootsBlue",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_rainBootsBlueLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.YellowRainBoots: ShoeItemDefinition(
        name="Yellow Rain Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_rainBootsYellow",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_rainBootsYellowLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.BlackAthleticShoes: ShoeItemDefinition(
        name="Black Athletic Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_athleticBlack",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.PirateShoes: ShoeItemDefinition(
        name="Pirate Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_pirate",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_pirateLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.ToonosaurFeet: ShoeItemDefinition(
        name="Toonosaur Feet",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_dinosaur",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_dinosaurLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.Wingtips: ShoeItemDefinition(
        name="Wingtips",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_wingtips",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.BlackFancyShoes: ShoeItemDefinition(
        name="Black Fancy Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_maryJaneShoes",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.PurpleBoots: ShoeItemDefinition(
        name="Purple Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_fashionBootsPurple",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_fashionBootsPurpleLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.BrownFancyShoes: ShoeItemDefinition(
        name="Brown Fancy Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_maryJaneShoesBrown",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.RedFancyShoes: ShoeItemDefinition(
        name="Red Fancy Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_maryJaneShoesRed",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.BlueSquareBoots: ShoeItemDefinition(
        name="Blue Square Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_fashionBootsBlueSquares",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_fashionBootsBlueSquaresLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.GreenHeartsBoots: ShoeItemDefinition(
        name="Green Hearts Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_fashionBootsGreenHearts",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_fashionBootsGreenHeartsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.GreyDotsBoots: ShoeItemDefinition(
        name="Grey Dots Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_fashionBootsGreyDots",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_fashionBootsGreyDotsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.OrangeStarsBoots: ShoeItemDefinition(
        name="Orange Stars Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_fashionBootsOrangeStars",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_fashionBootsOrangeStarsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.PinkStarsBoots: ShoeItemDefinition(
        name="Pink Stars Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_fashionBootsPinkStars",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_fashionBootsPinkStarsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.PurpleFancyShoes: ShoeItemDefinition(
        name="Purple Fancy Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_maryJaneShoesPurple",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.SpaceBoots: ShoeItemDefinition(
        name="Space Boots",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_space_boots",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.WitchShoes: ShoeItemDefinition(
        name="Witch Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_witch",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_witchLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.SkeletonShoes: ShoeItemDefinition(
        name="Skeleton Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_skeleton",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.AlchemistShoes: ShoeItemDefinition(
        name="Alchemist Shoes",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_alchemist",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_alchemistLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.HumbleRagdoll: ShoeItemDefinition(
        name="Humble Ragdoll",
        description="No Description",
        textureName="humble-ragdoll-shoes",
        textureNameBootsLong="humble-ragdoll-shoesLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.RegalRagdoll: ShoeItemDefinition(
        name="Regal Ragdoll",
        description="No Description",
        textureName="regal-ragdoll-shoes",
        textureNameBootsLong="regal-ragdoll-shoesLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.TraditionalRagdoll: ShoeItemDefinition(
        name="Traditional Ragdoll",
        description="No Description",
        textureName="tradi-ragdoll-shoes",
        textureNameBootsLong="tradi-ragdoll-shoesLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.HumbleTin: ShoeItemDefinition(
        name="Humble Tin",
        description="No Description",
        textureName="humble-tinsoldier-shoes",
        textureNameBootsLong="humble-tinsoldier-shoesLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.RegalTin: ShoeItemDefinition(
        name="Regal Tin",
        description="No Description",
        textureName="regal-tinsoldier-shoes",
        textureNameBootsLong="regal-tinsoldier-shoesLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.TraditionalTin: ShoeItemDefinition(
        name="Traditional Tin",
        description="No Description",
        textureName="tradi-tinsoldier-shoes",
        textureNameBootsLong="tradi-tinsoldier-shoesLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.VintageSnow: ShoeItemDefinition(
        name="Vintage Snow",
        description="No Description",
        textureName="tt_t_chr_avt_acc_sho_vintage_snow",
        textureNameBootsLong="tt_t_chr_avt_acc_sho_vintage_snowLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.AviatorBoots: ShoeItemDefinition(
        name="Aviator Boots",
        description="Sky Clan, here we come!",
        textureName="aviator_boots",
        textureNameBootsLong="aviator_bootsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.WingsuitBoots: ShoeItemDefinition(
        name="Wingsuit Boots",
        description="It might allow you to fly... not Loony Labs certified.",
        textureName="wingsuit_boots",
        textureNameBootsLong="wingsuit_bootsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.OutbackShoes: ShoeItemDefinition(
        name="Outback Shoes",
        description="Perfect for an outback adventure!",
        textureName="outback_shoes",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.PumpkinShoes: ShoeItemDefinition(
        name="Pumpkin Shoes",
        description="No Description",
        textureName="pumpkin_shoes",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.LazyBonesSlippers: ShoeItemDefinition(
        name="Lazy Bones Slippers",
        description="No Description",
        textureName="lazy_bones_shoes",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.HomemadeRagdoll: ShoeItemDefinition(
        name="Homemade Ragdoll",
        description="No Description",
        textureName="ragdoll_homemade_boots",
        textureNameBootsLong="ragdoll_homemade_bootsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.HomemadeTin: ShoeItemDefinition(
        name="Homemade Tin",
        description="No Description",
        textureName="soldier_homemade_boots",
        textureNameBootsLong="soldier_homemade_bootsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.RetroWinterSuit: ShoeItemDefinition(
        name="Retro Winter Suit",
        description="No Description",
        textureName="wintersuit_shoes",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.RetroWinterDress: ShoeItemDefinition(
        name="Retro Winter Dress",
        description="No Description",
        textureName="winterdress_shoes",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.BreaktheLawShoes: ShoeItemDefinition(
        name="Break the Law Shoes",
        description="No Description",
        textureName="btl_lbhq_shoes",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.TripleRainbowShoes: ShoeItemDefinition(
        name="Triple Rainbow Shoes",
        description="Triple rainbow! What does it mean?",
        textureName="triplerainbow_shoes",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.ChairmanShoes: ShoeItemDefinition(
        name="Chairman Shoes",
        description="No Description",
        textureName="cc_t_acc_sho_promo_chairman",
        shoeType=ShoeType.Shoes,
    ),
    ShoeItemType.PhantoonShoes: ShoeItemDefinition(
        name="Phantoon Shoes",
        description="No Description",
        textureName="phantoon_boots",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.TumblesShoes: ShoeItemDefinition(
        name="Tumbles' Shoes",
        description="No Description",
        textureName="tumbles_shoes",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.HallowopolisBoots: ShoeItemDefinition(
        name="Hallowopolis Boots",
        description="No Description",
        textureName="hwtown_boots",
        textureNameBootsLong="hwtown_bootsLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.DiverBoots: ShoeItemDefinition(
        name="Diver Boots",
        description="No Description",
        textureName="shoes_diver",
        textureNameBootsLong="shoes_diverLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.TrolleyEngineerBoots: ShoeItemDefinition(
        name="Trolley Engineer Boots",
        description="All aboard!",
        textureName="ttcc_acc_engineer_shoes",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.FruitPieShoes: ShoeItemDefinition(
        name="Fruit Pie Shoes",
        description="Tastes good, too!",
        textureName="ttcc_acc_fruitpieshoes",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.CardSuitShoesRed: ShoeItemDefinition(
        name="Red Card Suit Shoes",
        description="Not to be shuffled, but used to shuffle.",
        textureName="ttcc_acc_cardBoots_red",
        textureNameBootsLong="ttcc_acc_cardBoots_redLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.CardSuitShoesBlack: ShoeItemDefinition(
        name="Black Card Suit Shoes",
        description="Not to be shuffled, but used to shuffle.",
        textureName="ttcc_acc_cardBoots_black",
        textureNameBootsLong="ttcc_acc_cardBoots_blackLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.GatorSlippers: ShoeItemDefinition(
        name="Gator Slippers",
        description="They aren't crocodiles!",
        textureName="ttcc_acc_gator_shoes",
        textureNameBootsLong="ttcc_acc_gator_shoesLL",
        shoeType=ShoeType.BootsLong,
    ),
    ShoeItemType.PaintersMocasins: ShoeItemDefinition(
        name="Painter's Mocasins",
        description="Paint not included.",
        textureName="ttcc_acc_painter_shoes",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.ArmoredGreaves: ShoeItemDefinition(
        name="Armored Greaves",
        description="No Description",
        textureName="ttcc_acc_armored_boots",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.CybertoonShoes: ShoeItemDefinition(
        name="Cybertoon Shoes",
        description="No Description",
        textureName="cc_t_acc_shoes_cyberpunk",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.ShoesPirateGhost: ShoeItemDefinition(
        name="Pirate Ghost Shoes",
        description="No Description",
        textureName="cc_t_acc_sho_md_pirate_ghost_green",
        shoeType=ShoeType.BootsShort,
    ),
    ShoeItemType.ShoesSpy: ShoeItemDefinition(
        name="Spy Shoes",
        description="No Description",
        textureName="cc_t_acc_sho_md_spy_purple",
        shoeType=ShoeType.BootsShort,
    ),
}
