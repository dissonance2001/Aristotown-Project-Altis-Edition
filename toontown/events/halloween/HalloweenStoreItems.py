from toontown.crafting import CraftingGlobals
from toontown.crafting.CraftingGlobals import HalloweenMaterial
from toontown.inventory.enums.ItemEnums import ClothingTopItemType, ClothingBottomItemType, ShoeItemType, HatItemType, BackpackItemType, GlassesItemType, NeckItemType, BackgroundItemType, NameplateItemType, NametagFontItemType, ProfilePoseItemType, FurnitureItemType
from toontown.shop.base.ShopItemCatalogue import ShopItemCatalogue
from toontown.shop.cost.HalloweenPriceTag import HalloweenPriceTag
from toontown.shop.item.InventoryShopItem import InventoryShopItem


# TODO - report this module

"""
ideal order (but not mandatory): 
----------------------
|  hat   |  glasses  |
----------------------
| shirt  |  backpack |
----------------------
| bottom |   shoes   |
----------------------

hat, shirt, bottom, glasses, backpack, shoes
"""

HalloweenShopItems: ShopItemCatalogue = ShopItemCatalogue({i: itemList for i, itemList in enumerate([
    #
    # # Page 1 - Robo and Alien outfit
    # [
    #     # Robo Headband
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(1031),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_LIGHTNING_BOLT, cost = 20)
    #     ),
    #     # Shirt
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4284, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BOLT_HALLOWEEN, cost = 20)
    #     ),
    #     # Shorts
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4286, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BOLT_HALLOWEEN, cost = 20)
    #     ),
    #
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(1017),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_ROCKET, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4274, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_ROCKET, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4276, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_ROCKET, cost = 20)
    #     ),
    #
    # ],
    #
    # # Page 2 - Space Outfit (and Alien backpack)
    # [
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(176),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_ROCKET, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4171, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_ROCKET, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4173, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_ROCKET, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(331),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_ROCKET, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(450),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_ROCKET, cost = 20)
    #     ),
    #     # Alien Backpack
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(360),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_ROCKET, cost = 20)
    #     ),
    #
    # ],
    #
    # # Page 3 - Alice in Wonderland & Skeletoon
    # [
    #     # bow, shirt, skirt/shorts
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(1013),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EAT_ME_COOKIE, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4180, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EAT_ME_COOKIE, cost = 20)
    #     ),
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4182, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EAT_ME_COOKIE, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4181, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EAT_ME_COOKIE, cost = 20)
    #         ),
    #     ],
    #     # skele shirt, skele short/skirt, skele shoes
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(1743, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BONE, cost = 20)
    #     ),
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1747, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BONE, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1746, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BONE, cost = 20)
    #         ),
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(452),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BONE, cost = 20)
    #     ),
    # ],
    #
    # # Page 4 - Candycorn and Scarecrow
    # [
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(1034),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EAT_ME_COOKIE, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4277, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EAT_ME_COOKIE, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4279, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EAT_ME_COOKIE, cost = 20)
    #     ),
    #
    #     # crow hat, crow shirts, crow skirts
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(181),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAG_OF_STRAW, cost = 20)
    #     ),
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4186, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAG_OF_STRAW, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4187, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAG_OF_STRAW, cost = 20)
    #         ),
    #     ],
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4188, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAG_OF_STRAW, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4189, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAG_OF_STRAW, cost = 20)
    #         ),
    #     ],
    # ],
    #
    # # Page 5 - Witch/Wizard Outfit
    # [
    #     # witch hats, shirt, short/skirt, cauldron, broomstick, toes
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(151),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(182),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(183),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(184),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(185),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(186),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(1173),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #         ),
    #         # Show witch hat last
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(150),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #         ),
    #
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4190, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #     ),
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4191, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4192, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #         ),
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(178),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(332),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(451),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 20)
    #     ),
    # ],
    #
    # # Page 6 - Spy outfit
    # [
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(1174),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BOLT_HALLOWEEN, cost = 25)
    #     ),  # headset
    #
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4494, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BOLT_HALLOWEEN, cost = 25)
    #     ),  # shirt
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4495, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BOLT_HALLOWEEN, cost = 25)
    #         ),  # shorts
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4496, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BOLT_HALLOWEEN, cost = 25)
    #         ),  # skirt
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(296),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BOLT_HALLOWEEN, cost = 25)
    #     ),  # glasses
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(486),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BOLT_HALLOWEEN, cost = 25)
    #     ),  # shoes
    # ],
    #
    # # Page 7 - Frankenstein & Mad Scientist Outfit
    # [
    #     # frank head, shirt, shorts, screws
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(187),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BOLT_HALLOWEEN, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4168, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BOLT_HALLOWEEN, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4170, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BOLT_HALLOWEEN, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(179),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BOLT_HALLOWEEN, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4174, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4176, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #     ),
    # ],
    #
    # # Page 8 - Alchemist Outfit & Witch Polo
    # [
    #     # alchemist goggles (hat)
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(1012),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #     ),
    #
    #     # both shirt variations
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4164, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4165, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #         ),
    #     ],
    #     # shorts/skirt
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4166, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4167, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #         ),
    #
    #     ],
    #     # potion bag
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(336),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #     ),
    #     # shoes
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(453),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #     ),
    #     # Witch Polo
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(1790, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BROOMSTICK, cost = 10)
    #     ),
    #
    # ],
    #
    # # Page 9 - Dracula/Vampire Outfit
    # [
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(177),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 20)
    #     ),
    #
    #     # Vampire Shirts
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1112, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1770, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 20)
    #         ),
    #
    #     ],
    #
    #     # Vampire Shorts
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1124, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1773, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 20)
    #         ),
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(334),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 20)
    #     ),
    #
    #     # Batty Moon Shirt
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(1796, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 10)
    #     ),
    #
    # ],
    #
    # # Page 10 - SuperToon Outfit
    # [
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(216),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #     ),
    #
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(1724, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #     ),
    #     # Bottoms
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1735, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1740, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #         ),
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(325),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(417),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #     ),
    # ],
    #
    # # Page 11 - PhanToon Outfit
    # [
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(215),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #     ),
    #     # phantoon shirt, phantoon shorts, phantoon boots
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4394, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4396, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(326),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(473),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #     ),
    # ],
    #
    # # Page 12 - Bugs I, Bee
    # [
    #     # Antenna, shirts, shorts
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(134),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #     ),
    #
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(1723, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #     ),
    #     # Bottoms
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1739, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1734, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #         ),
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(214),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #     ),
    #
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(307),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #     ),
    # ],
    #
    # # Page 13 - Bugs II, Spider
    # [
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(147),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #     ),
    #
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(1744, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #     ),
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1748, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #         )
    #         ,
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1745, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #         ),
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(227),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(318),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #     ),
    #
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(3021),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #     ),
    #
    # ],
    #
    # # Page 14 - Reaper & Ghost
    # [
    #     # scarf, shirt, skirt/shorts, bug antannae, candy bag
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(333),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4183, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 20)
    #     ),
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4185, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 20)
    #         )
    #         ,
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4184, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 20)
    #         ),
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(3020),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(1001, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #     ),
    #
    # ],
    #
    # # Page 15 - Dinosaur Outfit
    # [
    #     # dino hat, dino shirt, dino shorts, dino tail, dino feet
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(172),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(1113, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(1125, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(327),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(449),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 20)
    #     ),
    # ],
    #
    # # Page 16 - Riding Hood & Turtle outfit
    # [
    #     # shirt, shorts, skirt, hood, cloak
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(1030),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4287, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAG_OF_STRAW, cost = 20)
    #     ),
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4288, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAG_OF_STRAW, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4289, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAG_OF_STRAW, cost = 20)
    #         ),
    #     ],
    #
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(373),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 20)
    #     ),
    #
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(1771, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(1775, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 20)
    #     ),
    # ],
    #
    # # Page 17 - Pirate Outfit
    # [
    #     # pirate bandana, pirate shirt, pirate short/skirt, pirate eyepatch, pirate shoes
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(171),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(1778, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 20)
    #     ),
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1122, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(1123, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 20)
    #         ),
    #     ],
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(224),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(223),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 20)
    #         ),
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(448),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 20)
    #     ),
    #
    # ],
    #
    # # Page 18 - Ghost Pirate outfit
    # [
    #     # hat
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(1175, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 25)
    #     ),
    #     # shirt
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4491, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 25)
    #     ),
    #     [
    #         # shorts
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4492, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 25)
    #         ),
    #         # skirt
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4493, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 25)
    #         ),
    #     ],
    #     # glasses
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(295),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 25)
    #     ),
    #     # backpack
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(3106),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 25)
    #     ),
    #     # shoes
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(485),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 25)
    #     ),
    # ],
    #
    # # Page 19 - Pumpkin Outfit
    # [
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(180),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_PUMPKIN, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(1002, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_PUMPKIN, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(464),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_PUMPKIN, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(3022),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_PUMPKIN, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(335),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_PUMPKIN, cost = 20)
    #     ),
    #
    # ],
    #
    # # Page 20 - Clown Outfit & Hypno Goggles
    # [
    #     # clown hat, clown shirt, clown shorts
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(159),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CLOWN_NOSE, cost = 20)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4177, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CLOWN_NOSE, cost = 20)
    #     ),
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4178, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CLOWN_NOSE, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4179, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CLOWN_NOSE, cost = 20)
    #         ),
    #     ],
    #     # hypnos
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(260),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(261),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(262),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(263),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(264),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(265),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(266),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(241),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 10)
    #         ),
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(267),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EGG_HALLOWEEN, cost = 30)
    #     ),
    # ],
    #
    # # Page 21 - Angel/Demon
    # [
    #     # angel halos, angel wings, more wings, demon horns, demon wings
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(1018),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(1019),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(1020),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(1021),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(1022),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(1023),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 20)
    #         ),
    #     ],
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(361),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(362),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(363),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(364),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(365),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(366),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 20)
    #         ),
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(311),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EAT_ME_COOKIE, cost = 20)
    #     ),
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(1024),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(1025),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(1026),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(1027),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(1028),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(1029),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 20)
    #         ),
    #     ],
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(367),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(368),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(369),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(370),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(371),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(372),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 20)
    #         ),
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(306),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 20)
    #     ),
    #
    # ],
    #
    # # Page 22 - Golden Angel/Demon
    # [
    #     # gold halo, gold wings, rainbow angel wings, horns, demon wings
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(1035),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_SUPERTOON_EMBLEM, cost = 100)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(376),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_POTION, cost = 100)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(312),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_EAT_ME_COOKIE, cost = 50)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(1056),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_CREEPY_CRAWLY, cost = 100)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(377),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BAT, cost = 100)
    #     ),
    # ],
    #
    # # Page 23 - Sailor Outfits
    # [
    #     # M ribbon shirt short, F ribbon shirt skirt
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(378),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(379),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(380),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(381),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(382),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(383),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(384),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(385),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(386),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #     ],
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4297, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4301, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4305, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4309, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4313, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4317, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4321, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4325, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4329, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #     ],
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4298, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4302, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4306, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4310, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4314, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4318, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4322, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4326, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4330, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #     ],
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(388),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(389),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(390),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(391),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(392),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(393),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(394),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(395),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogAccessoryItem(396),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 10)
    #         ),
    #     ],
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4296, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4300, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4304, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4308, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4312, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4316, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4320, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4324, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4328, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #     ],
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4299, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4303, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4307, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4311, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4315, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4319, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4323, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4327, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogClothingItem(4331, 0),
    #             priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 5)
    #         ),
    #     ],
    # ],
    #
    # # Page 24 - Gold Sailor outfits
    # [
    #     # M ribbon shirt short, F ribbon shirt skirt
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(387),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 75)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4333, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 50)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4334, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 50)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(397),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TATTERED_CLOTH, cost = 75)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4332, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 50)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4335, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_TREASURE, cost = 50)
    #     ),
    # ],
    #
    # # Page 25 - Sads stuff
    # [
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4293, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BONE, cost = 50)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogClothingItem(4295, 0),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BONE, cost = 50)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogAccessoryItem(465),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BONE, cost = 50)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogBackgroundItem(31),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BONE, cost = 100)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogNameplateItem(30),
    #         priceTags = HalloweenPriceTag(HalloweenMaterial.CRAFT_MAT_BONE, cost = 100)
    #     ),
    # ],
    #
    # # Page 26 - Misc stuff
    # [
    #     [
    #         CatalogShopItem(
    #             catalogItem = CatalogNameplateItem(38),
    #             priceTags = HalloweenPriceTag(CraftingGlobals.CRAFT_MAT_ALL, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogNameplateItem(39),
    #             priceTags = HalloweenPriceTag(CraftingGlobals.CRAFT_MAT_ALL, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogNameplateItem(40),
    #             priceTags = HalloweenPriceTag(CraftingGlobals.CRAFT_MAT_ALL, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogNameplateItem(41),
    #             priceTags = HalloweenPriceTag(CraftingGlobals.CRAFT_MAT_ALL, cost = 20)
    #         ),
    #         CatalogShopItem(
    #             catalogItem = CatalogNameplateItem(42),
    #             priceTags = HalloweenPriceTag(CraftingGlobals.CRAFT_MAT_ALL, cost = 20)
    #         ),
    #     ],
    #     CatalogShopItem(
    #         catalogItem = CatalogNametagItem(10),
    #         priceTags = HalloweenPriceTag(CraftingGlobals.CRAFT_MAT_ALL, cost = 40)
    #     ),
    #     CatalogShopItem(
    #         catalogItem = CatalogPoseItem(27),
    #         priceTags = HalloweenPriceTag(CraftingGlobals.CRAFT_MAT_ALL, cost = 35)
    #     ),
    #     # HW Backgrounds
    #     [
    #         # Town
    #         CatalogShopItem(
    #             catalogItem = CatalogBackgroundItem(38),
    #             priceTags = HalloweenPriceTag(CraftingGlobals.CRAFT_MAT_ALL, cost = 35)
    #         ),
    #         # Witch
    #         CatalogShopItem(
    #             catalogItem = CatalogBackgroundItem(50),
    #             priceTags = HalloweenPriceTag(CraftingGlobals.CRAFT_MAT_ALL, cost = 35)
    #         ),
    #     ],
    #     # HW Nameplates
    #     [
    #         # Bats
    #         CatalogShopItem(
    #             catalogItem = CatalogNameplateItem(43),
    #             priceTags = HalloweenPriceTag(CraftingGlobals.CRAFT_MAT_ALL, cost = 35)
    #         ),
    #         # Witch
    #         CatalogShopItem(
    #             catalogItem = CatalogNameplateItem(56),
    #             priceTags = HalloweenPriceTag(CraftingGlobals.CRAFT_MAT_ALL, cost = 35)
    #         ),
    #     ],
    #     # Furniture Paintings
    #     [
    #         # Chup Painting
    #         CatalogShopItem(
    #             catalogItem = CatalogFurnitureItem(1445),
    #             priceTags = HalloweenPriceTag(CraftingGlobals.CRAFT_MAT_ALL, cost = 20)
    #         ),
    #         # Count Erclaim Painting
    #         CatalogShopItem(
    #             catalogItem = CatalogFurnitureItem(1446),
    #             priceTags = HalloweenPriceTag(CraftingGlobals.CRAFT_MAT_ALL, cost = 20)
    #         ),
    #     ],
    # ],
])})
