"""
A module file containing several enums for item representation.
Includes the high-level types (hats, glasses, etc) and their subtypes.
"""
from enum import IntEnum
from typing import Type, Dict

from toontown.utils.EnhancedIntEnum import EnhancedIntEnum

_ItemTypeToSubtypeClass: Dict['ItemType', Type['ItemType']] = {}
_SubtypeClassToItemType: Dict[Type['IntEnum'], 'ItemType'] = {}


def defineItemSubtypeEnum(itemType: 'ItemType'):
    """
    A decorator to define an item subtype enum.
    """

    def wrapper(cls):
        _ItemTypeToSubtypeClass[itemType] = cls
        _SubtypeClassToItemType[cls] = itemType
        return cls

    return wrapper


class ItemType(IntEnum):
    """
    The highest-level enum which holds each "category" of item.
    These reflect all of the generic kinds of items.
    """
    # Cosmetics
    Cosmetic_Clothing_Top           = 1000
    Cosmetic_Clothing_Bottom          = 1001
    Cosmetic_Hat             = 1002
    Cosmetic_Glasses         = 1003
    Cosmetic_Backpack        = 1004
    Cosmetic_Shoes           = 1005
    Cosmetic_Neck            = 1006

    # Social
    Social_NametagFont     = 2000
    Social_CheesyEffect    = 2001
    Social_CustomSpeedchat = 2002
    Social_ChatStickers    = 2003
    Social_Emote           = 2004

    # Profile Items
    Profile_Nameplate  = 3000
    Profile_Background = 3001
    Profile_Pose       = 3002

    # Fishing
    Fishing_Rod    = 4000

    # Estate Items
    Estate_Furniture = 5000
    Estate_Style     = 5001
    Estate_Texture   = 5002
    Estate_Ticket    = 5003

    # Consumables
    Consumable_Boosters = 6000

    # Misc
    Material = 7000
    Trophy   = 7001
    Music_Disc = 7002
    Unite    = 7100
    IOU      = 7101

    """
    Item type class accessors
    """

    @staticmethod
    def getSubtypeClass(itemType: 'ItemType') -> Type['ItemType']:
        """
        Gets the item subtype given a specified ItemType.
        """
        assert itemType in _ItemTypeToSubtypeClass, \
            f"itemType {itemType} does not have a specified subtype."
        return _ItemTypeToSubtypeClass.get(itemType)

    @staticmethod
    def getItemType(subtypeCls: Type['IntEnum']) -> 'ItemType':
        """
        Gets the item type given a specified item subtype.
        """
        assert subtypeCls in _SubtypeClassToItemType, \
            f"subtypeCls {subtypeCls} does not have a specified item type."
        return _SubtypeClassToItemType.get(subtypeCls)


"""Cosmetic ItemTypes"""


@defineItemSubtypeEnum(ItemType.Cosmetic_Clothing_Top)
class ClothingTopItemType(IntEnum):
    """
    Item subtype enum for Shirts.
    """
    Shirt_Desat_Classic_Plain = 1         # old: 0
    Shirt_Desat_Classic_StripeSingle = 2     # old: 1
    Shirt_Desat_Classic_ButtonUp = 3                   # old: 2
    Shirt_Desat_Classic_StripeDouble = 4     # old: 3
    Shirt_Desat_Classic_StripeMany = 5    # old: 4
    Shirt_Desat_Classic_PocketPolo = 6    # old: 5
    Feather = 7                     # old: 8
    Dress = 8                       # old: 9
    TwoToneButtonUp = 9             # old: 10
    Vest = 10                       # old: 11
    ButtonUpB = 11                  # old: 14
    Soccer = 12                     # old: 16
    LightningBolt = 13              # old: 17
    No19 = 14                       # old: 18
    Guayabera = 15                  # old: 19
    Shirt_Desat_Classic_FlowersSingle = 23               # old: 22
    Shirt_Desat_Classic_FlowersMany = 16  # old: 6
    Shirt_Desat_Classic_FlowersStripe = 17               # old: 7
    DenimVest = 18                  # old: 12
    CuffedBlouse = 19               # old: 13
    Peplum = 20                     # old: 15
    Hearts = 21                     # old: 20
    Stars = 22                      # old: 21
    ZipUpHoodie = 24                # old: 25
    Island = 25                     # old: 27
    PurpleStars = 26                # old: 38
    WinterStripes = 27              # old: 26
    No1 = 29                        # old: 28
    GreenStripe = 30                # old: 37
    Shirt_Kimono_Classic_Red = 31      # old: 39
    GoldenStripes = 32              # old: 23
    PinkBow = 34                    # old: 24
    TiedDress = 35                  # old: 36
    WinterStripe = 36               # old: 40
    TieDye = 37                     # old: 45
    Sheriff = 38                    # old: 52
    CheckeredCowboy = 39            # old: 53
    CactusCowboy = 40               # old: 54
    CowboyVest = 41                 # old: 55
    GreenDrawstring = 42            # old: 56
    BlueDrawstring = 43             # old: 57
    Ghost = 44                      # old: 29
    Pumpkin = 45                    # old: 30
    VampireA = 46                   # old: 114
    Turtle = 47                     # old: 115
    VampireB = 48                   # old: 122
    Toonosaur = 49                  # old: 123
    FishingBubble = 50              # old: 124
    FORE = 51                       # old: 125
    GearBusting = 52                # old: 126
    Snowman = 53                    # old: 31
    Snowflakes = 54                 # old: 32
    CandyCaneHearts = 55            # old: 33
    WinterScarf = 56                # old: 34
    PinkHeart = 57                  # old: 41
    RedHeart = 58                   # old: 42
    WingedHeart = 59                # old: 43
    FieryHeart = 60                 # old: 44
    Cupid = 61                      # old: 69
    DottedHearts = 62               # old: 70
    RedBow = 63                     # old: 96
    LuckyClover = 64                # old: 47
    PotOGold = 65                   # old: 48
    IdesofMarch = 66                # old: 116
    Fisherman = 67                  # old: 49
    Goldfish = 68                   # old: 50
    Pawprint = 69                   # old: 51
    BackpackAndShades = 70          # old: 62
    Lederhosen = 71                 # old: 63
    Watermelon = 72                 # old: 64
    RacingFlag = 73                 # old: 65
    AmericanFlag = 74               # old: 58
    Fireworks = 75                  # old: 59
    GreenButtonUp = 76              # old: 60
    Daisy = 77                      # old: 61
    BananaPeel = 78                 # old: 66
    BikeHorn = 79                   # old: 67
    HypnoGoggles = 80               # old: 68
    ClownFish = 81                  # old: 72
    OldBootA = 82                   # old: 73
    Shirt_GardenMole_Classic = 83   # old: 74
    Gardening = 84                  # old: 75
    Cupcake = 85                    # old: 76
    PartyHat = 86                   # old: 77
    RoadsterRaceway = 87            # old: 78
    Roadster = 88                   # old: 79
    CoolSun = 89                    # old: 80
    Beachball = 90                  # old: 81
    DiamondPolo = 91                # old: 82
    DottedPolo = 92                 # old: 83
    GoldMedal = 93                  # old: 86
    SaveTheBuildings = 94           # old: 87
    SaveTheBuildingsNo2 = 95        # old: 88
    ToontaskCompleter = 96          # old: 89
    ToontaskCompleterNo2 = 97       # old: 90
    Trolley = 98                    # old: 91
    TrolleyNo2 = 99                 # old: 92
    WinterGift = 100                # old: 93
    Skeletoon = 101                 # old: 94
    Cobweb = 102                    # old: 95
    MostCogsDefeatedA = 103         # old: 106
    MostVPsDefeated = 104           # old: 110
    SellbotSmasher = 105            # old: 111
    Pirate = 106                    # old: 120
    Supertoon = 107                 # old: 121
    RacerJumpsuit = 108             # old: 118
    NoTimeforCogBuildings = 109     # old: 128
    TrolleyGang = 110               # old: 129
    OldBootB = 111                  # old: 130
    WitchPolo = 112                 # old: 132
    Sledding = 113                  # old: 133
    Bat = 114                       # old: 134
    Mittens = 115                   # old: 135
    PoolShark = 116                 # old: 136
    PianoTuna = 117                 # old: 137
    GolfStripes = 118               # old: 138
    DummyCogPolo = 119              # old: 141
    MostCogsDefeatedforAnts = 120   # old: 142
    TrolleyForAnts = 121            # old: 143
    TrolleySideways = 122           # old: 144
    MostBuildingsDefeated = 123     # old: 145
    MostCogsDefeatedB = 124         # old: 146
    BirthdayCake = 125              # old: 147
    LoonyLabsScientistA = 126       # old: 97
    LoonyLabsScientistB = 127       # old: 98
    LoonyLabsScientistC = 128       # old: 99
    SillyMailbox = 129              # old: 100
    SillyTrashCan = 130             # old: 101
    LoonyLabsLogo = 131             # old: 102
    SillyHydrant = 132              # old: 103
    SillyMeterWhistle = 133         # old: 104
    CogCrusherShirt = 134           # old: 105
    NoMoreCheese = 135              # old: 107
    FlunkyFlannel = 136             # old: 108
    DefeatedSellbots = 137          # old: 109
    JellybeanJar = 138              # old: 112
    Doodle = 139                    # old: 113
    GetConnected = 140              # old: 117
    Bee = 141                       # old: 119
    Meatballs = 142                 # old: 148
    TrashcatsRags = 143             # old: 149
    DrowsyDreamland = 144           # old: 150
    BetaToon = 145                  # old: 151
    YOTTKnight = 146                # old: 152
    BBSailor = 147                  # old: 153
    DGGardening = 148               # old: 154
    Shirt_TTC_Firefighter = 149            # old: 155
    MMLBand = 150                   # old: 156
    TeamBarnyard = 151              # old: 157
    TeamOutback = 152               # old: 158
    BarnyardVacation = 153          # old: 159
    OutbackVacation = 154           # old: 160
    AAParkRanger = 155              # old: 161
    BrrrghSnowflakes = 156          # old: 162
    Alchemist = 157                 # old: 163
    AlchemistOveralls = 158         # old: 164
    Frankentoon = 159               # old: 165
    Spacetoon = 160                 # old: 166
    MadScientist = 161              # old: 167
    Clown = 162                     # old: 168
    Wonderland = 163                # old: 169
    Reaper = 164                    # old: 170
    Scarecrow = 165                 # old: 171
    ScarecrowOveralls = 166         # old: 172
    Wizard = 167                    # old: 173
    GreenElfShirt = 168             # old: 174
    RedElfShirt = 169               # old: 175
    GingerbreadA = 170              # old: 176
    GingerbreadB = 171              # old: 177
    PresentUniform = 172            # old: 178
    RagdollHumble = 173             # old: 179
    RagdollRegal = 174              # old: 180
    RagdollTraditional = 175        # old: 181
    Reindeer = 176                  # old: 182
    TinSoldierHumble = 177          # old: 183
    TinSoldierRegal = 178           # old: 184
    TinSoldierTraditional = 179     # old: 185
    UglySweater = 180               # old: 186
    VintageSnowShirt = 181          # old: 187
    NY2019Suit = 182                # old: 188
    NY2019Dress = 183               # old: 189
    CupidOutfit = 184               # old: 190
    DoesShirt = 185                 # old: 191
    WebstersShirt = 186             # old: 192
    AngelWings = 187                # old: 193
    AviatorShirt = 188              # old: 194
    WingsuitShirt = 189             # old: 195
    DragonWings = 190               # old: 196
    ChibiWings = 191                # old: 197
    BurgerShirt = 192               # old: 198
    SellbotSeeker = 193             # old: 199
    CashbotCatcher = 194            # old: 200
    LawbotLiberator = 195           # old: 201
    BossbotBasher = 196             # old: 202
    OutbackUniform = 197            # old: 203
    OutbackDenim = 198              # old: 204
    AlienShirt = 199                # old: 205
    CandyCornShirt = 200            # old: 206
    Busted = 201                    # old: 207
    LawbotResistance = 202          # old: 208
    RetroRobotShirt = 203           # old: 209
    RidingHoodShirt = 204           # old: 210
    NurseShirt = 205                # old: 211
    LazyBonesShirt = 206            # old: 212
    SailorShirtA = 207              # old: 213
    SailorShirtB = 208              # old: 214
    BlueSailorShirtA = 209          # old: 215
    BlueSailorShirtB = 210          # old: 216
    CyanSailorShirtA = 211          # old: 217
    CyanSailorShirtB = 212          # old: 218
    GreenSailorShirtA = 213         # old: 219
    GreenSailorShirtB = 214         # old: 220
    OrangeSailorShirtA = 215        # old: 221
    OrangeSailorShirtB = 216        # old: 222
    PinkSailorShirtA = 217          # old: 223
    PinkSailorShirtB = 218          # old: 224
    PurpleSailorShirtA = 219        # old: 225
    PurpleSailorShirtB = 220        # old: 226
    RedSailorShirtA = 221           # old: 227
    RedSailorShirtB = 222           # old: 228
    BlackSailorShirtA = 223         # old: 229
    BlackSailorShirtB = 224         # old: 230
    GoldenSailorShirtA = 225        # old: 231
    GoldenSailorShirtB = 226        # old: 232
    TeamTreesShirt = 227            # old: 233
    HomemadeRagdoll = 228           # old: 234
    HomemadeSoldier = 229           # old: 235
    RetroWinterSuit = 230           # old: 236
    RetroWinterDress = 231          # old: 237
    SnowmanShirt = 232              # old: 238
    NewYears2020 = 233              # old: 239
    ValentoonsShirt = 234           # old: 240
    AgentSevensShirt = 235          # old: 241
    StPats2020 = 236                # old: 242
    ClownShirt = 237                # old: 243
    SevenStriped = 238              # old: 244
    TripleRainbow = 239             # old: 245
    BoardbotShirt = 240             # old: 246
    BoredbotShirt = 241             # old: 247
    JesterShirt = 242               # old: 248
    BlackJesterShirt = 243          # old: 249
    Easter2020 = 244                # old: 250
    ExecutiveBoardbot = 245         # old: 251
    LawbotSuitTop = 246             # old: 252
    CooktheCogsShirt = 247          # old: 253
    VacationFroge = 248             # old: 254
    PhantoonShirt = 249             # old: 255
    VolunteerRanger = 250           # old: 256
    ToonsmasPast = 251              # old: 257
    ToonsmasPresent = 252           # old: 258
    ToonsmasFuture = 253            # old: 259
    NewYears2021 = 254              # old: 260
    TumblesShirt = 255              # old: 261
    Valentoons2021 = 256            # old: 262
    HallowopolisShirt = 257         # old: 263
    Detective = 258                 # old: 264
    TwoPocketCargo = 259            # old: 265
    JacketAndFlannel = 260          # old: 266
    BlueNewstoon = 261              # old: 267
    GrayNewstoon = 262              # old: 268
    ChupShirt = 263                 # old: 269
    NewYears2022 = 264              # old: 270
    Valentoons2022 = 265            # old: 271
    DoctorToonShirt = 266           # old: 272
    TrolleyEngineerShirt = 267      # old: 274
    ArtisticShirt = 268             # old: 275
    StarstruckShirt = 269           # old: 276
    RetroShirt = 270                # old: 277
    BattleJacket = 271              # old: 278
    GumballMachineShirt = 272       # old: 279
    CardSuitShirtA = 273            # old: 280
    CardSuitShirtB = 274            # old: 289
    SchoolhouseFlannel = 275        # old: 281
    SleepwalkerShirt = 276          # old: 282
    FruitPieShirt = 277             # old: 283
    Shirt_Donut_Pink = 278            # old: 284
    Shirt_Donut_Blue = 279            # old: 285
    Shirt_Donut_Chocolate = 280       # old: 286
    Shirt_Donut_Lemon = 281           # old: 287
    Shirt_Donut_Vanilla = 282         # old: 288
    BluePainter = 283               # old: 290
    RedPainter = 284                # old: 291
    GreenPainter = 285              # old: 292
    YellowPainter = 286             # old: 293
    ChefCoat = 287                  # old: 294
    NewYears2023 = 288              # old: 295
    ArmoredChestplate = 289         # old: 296
    RejectedSweater = 290           # old: 297
    HighRollersSuit = 291           # old: 298
    HighRollersProdigalSuit = 292   # old: 299
    CybertoonShirt = 293            # old: 300
    BroVinci = 294                  # old: 273
    GhostPirateShirt = 295          # old: 301
    ToonSpyShirt = 296              # old: 302
    ClowndeerSweaterShirt = 297     # old: 303
    NewYears2024 = 298              # old: 304


@defineItemSubtypeEnum(ItemType.Cosmetic_Clothing_Bottom)
class ClothingBottomItemType(IntEnum):
    """
    Item subtype enum for Shorts.
    """
    ShortswithBelt = 1		                # old: 156
    BigPocketsShorts = 2		            # old: 157
    FeatherShorts = 3		                # old: 158
    SidestripedShorts = 4		            # old: 159
    AthleticShortsA = 5		                # old: 160
    FieryShorts = 6		                    # old: 161
    JeanShorts = 7		                    # old: 162
    Shorts_Valentoons_Pink = 8		        # old: 163
    Shorts_Valentoons_Green = 9		        # old: 178
    JeanHeartShorts = 10		            # old: 179
    AthleticShortsB = 11		            # old: 164
    TealAndYellowShorts = 12		        # old: 165
    GreenAndYellowShorts = 13		        # old: 170
    IdesofMarchShorts = 14		            # old: 199
    SnowmanShortsA = 15		                # old: 174
    SnowflakeShorts = 16		            # old: 175
    PeppermintShorts = 17		            # old: 176
    FestiveWinterShorts = 18		        # old: 177
    GolfingShorts = 20		                # old: 206
    PleatedSkirt = 21		                # old: 0
    PolkaDotSkirt = 22		                # old: 1
    StripedSkirt = 23		                # old: 2
    BottomStripeSkirt = 24		            # old: 3
    FlowersSkirt = 25		                # old: 4
    JeanPocketsSkirt = 26		            # old: 7
    DenimSkirt = 27		                    # old: 8
    HighPocketsShorts = 28		            # old: 5
    FlowerShorts = 29		                # old: 6
    BlueAndGoldSkirt = 30		            # old: 10
    PinkBowSkirt = 31		                # old: 11
    BlueGreenStarSkirt = 32		            # old: 12
    RedAndWhiteHeartsSkirt = 33		        # old: 13
    ValentoonsHeartsSkirt = 34		        # old: 27
    JeanHeartSkirt = 35		                # old: 28
    Skirt_Rainbow_Classic = 36		                # old: 14
    Shorts_LuckyClover_Classic = 37		            # old: 15
    IdesofMarchSkirt = 38		            # old: 48

    Shorts_GoldBuckle_Classic = 41		            # old: 167
    ZestyWesternSkirt = 40		            # old: 17

    Shorts_SilverBuckle_Classic = 42		            # old: 168
    WesternSkirt = 39		                # old: 16

    Shorts_Stars_Classic = 43		                # old: 169
    Skirt_Stars_Classic = 44		                # old: 18
    DaisySkirt = 45		                    # old: 19
    Shorts_Gag_Classic_BananaPeel = 46		            # old: 20
    Shorts_Gag_Classic_BikeHorn = 47		                # old: 21
    Shorts_Gag_Classic_HypnoGoggles = 48		            # old: 22
    Skirt_Snowman = 49		                # old: 23
    SnowflakesSkirt = 50		            # old: 24
    PeppermintSkirt = 51		            # old: 25
    FestiveWinterSkirt = 52		            # old: 26
    FishingShorts = 53		                # old: 180
    GardeningShorts = 54		            # old: 181
    Shorts_Party = 55		                # old: 182
    CheckeredRacingShorts = 56		        # old: 183
    GoldfishShorts = 57		                # old: 184
    GreenPlaidGolfingShorts = 58		    # old: 185

    ### Costumes ###

    Shorts_Bee_Classic = 59		                    # old: 50
    Skirt_Bee_Classic = 76		                    # old: 35
    Shorts_Supertoon_Classic = 19		            # old: 53
    Skirt_Supertoon_Classic = 77		                # old: 36
    Shorts_Spider_Classic = 62		                # old: 190
    Skirt_Spider_Classic = 81		                # old: 40
    Shorts_Skeletoon_Classic = 63		            # old: 191
    Skirt_Skeletoon_Classic = 80		                # old: 39

    Shorts_Pirate_Classic = 96		                # old: 51
    Skirt_Pirate_Classic = 97		                # old: 52
    Shorts_Pirate_Ghost = 279                 # old: 326
    Skirt_Pirate_Ghost = 280                  # old: 327

    Shorts_Spytoon = 281                     # old: 328
    Skirt_Spytoon = 282                      # old: 329

    Shorts_Turtle_Classic = 95  # old: 47
    Shorts_Vampire_Classic = 98  # old: 54
    Shorts_Toonosaur_Classic = 99  # old: 55

    Shorts_Alchemist = 121  # old: 225
    Skirt_Alchemist = 122  # old: 75
    Shorts_Frankenstein = 123  # old: 76
    SpacetoonShorts = 124  # old: 77
    MadScientistShorts = 125  # old: 78
    ClownShortsA = 126  # old: 229
    ClownSkirtA = 127  # old: 79
    Shorts_Wonderland = 128  # old: 230
    Skirt_Wonderland = 129  # old: 80
    Shorts_Reaper = 130  # old: 231
    Skirt_Reaper = 131  # old: 81
    Shorts_Scarecrow = 132  # old: 232
    Skirt_Scarecrow = 133  # old: 82
    Shorts_Witch = 134  # old: 233
    Skirt_Witch = 135   # old: 83

    Shorts_Cybertoon = 276		            # old: 324
    Skirt_Cybertoon = 277		            # old: 325

    SaveTheBuildingsShorts = 60		        # old: 188
    TrolleyShorts = 61		                # old: 189
    BlueRacingShorts = 64		            # old: 200
    IndigoRacingShorts = 65		            # old: 207
    TanGolfingShorts = 66		            # old: 208
    CheckeredGolfShorts = 67		        # old: 209
    DarkBlueRacingShorts = 68		        # old: 210
    RacingStripeShorts = 69		            # old: 211
    FishingSkirt = 70		                # old: 29
    GardeningSkirt = 71		                # old: 30
    PartySkirt = 72		                    # old: 31
    RedCheckeredSkirt = 73		            # old: 32
    GrassSkirt = 74		                    # old: 33
    PinkPlaidGolfSkirt = 75		            # old: 34
    SaveTheBuildingsSkirt = 78		        # old: 37
    TrolleySkirt = 79		                # old: 38
    CogCrusherShorts = 82		            # old: 44
    SellbotCrusherShorts = 83		        # old: 45
    BlueCheckeredRacingSkirt = 84		    # old: 49
    StarryGolfingSkirt = 85		            # old: 56
    IndigoRacingSkirt = 86		            # old: 57
    RainbowGolfingSkirt = 87		        # old: 58
    BluePlaidGolfingSkirt = 88		        # old: 59
    DarkBlueRacingSkirt = 89		        # old: 60
    RacingStripeSkirt = 90		            # old: 61
    ScientistAShorts = 91		            # old: 41
    ScientistBShorts = 92		            # old: 42
    ScientistCShorts = 93		            # old: 43
    OvercoatVampireShorts = 94		        # old: 46

    Shorts_Meatballs = 100		            # old: 62
    Shorts_BetaToon = 103		            # old: 215
    Skirt_BetaToon = 104		                # old: 65

    Shorts_TTC_Firefighter = 111		        # old: 219
    Skirt_TTC_Firefighter = 112		        # old: 69
    Shorts_BB_Sailor = 107		            # old: 217
    Skirt_BB_Sailor = 108		                # old: 67
    Shorts_DG_Gardening = 109		            # old: 218
    Skirt_DG_Gardening = 110		            # old: 68
    Shorts_YOTT_Knight = 105		            # old: 216
    Skirt_YOTT_Knight = 106		            # old: 66
    Shorts_MML_Band = 113		                # old: 70
    Shorts_TB_Sweater = 119  # old: 224
    Skirt_TB_Sweater = 120  # old: 74
    Shorts_AA_ParkRanger = 118		        # old: 73
    Shorts_DDL_Sleeper = 102		        # old: 64

    Shorts_Barnyard = 114		        # old: 221
    Skirt_Barnyard = 115		            # old: 71
    Shorts_Outback = 116		            # old: 222
    Skirt_Outback = 117		            # old: 72

    Shorts_Elf_Green = 136		            # old: 84
    Skirt_Elf_Green = 136                     # old: 330
    Shorts_Elf_Red = 137		                # old: 85
    Skirt_Elf_Red = 137                       # old: 331

    Shorts_Gingerbread = 138		            # old: 236
    Skirt_Gingerbread = 139		            # old: 86
    PresentUniformShorts = 140		        # old: 237
    PresentUniformSkirt = 141		        # old: 87

    Skirt_Reindeer = 145		                # old: 91
    Shorts_Reindeer = 146		            # old: 238
    VintageSnowShorts = 147		            # old: 92

    Shorts_Ragdoll_Humble = 148		        # old: 243
    Skirt_Ragdoll_Humble = 142  # old: 88
    Shorts_Ragdoll_Regal = 149		        # old: 244
    Skirt_Ragdoll_Regal = 143  # old: 89
    Shorts_Ragdoll_Traditional = 150		    # old: 245
    Skirt_Ragdoll_Traditional = 144  # old: 90
    Shorts_Ragdoll_Homemade = 203		        # old: 274
    Skirt_Ragdoll_Homemade = 204		        # old: 128

    Shorts_Soldier_Humble = 151		            # old: 93
    Shorts_Soldier_Regal = 152		            # old: 94
    Shorts_Soldier_Traditional = 153		        # old: 95
    Shorts_Soldier_Homemade = 205		        # old: 129

    CupidShorts = 156		                # old: 247
    CupidSkirt = 157		                # old: 97

    AviatorShorts = 160		                # old: 99
    WingsuitShorts = 161		            # old: 100
    Skirt_SellbotSeeker = 162		        # old: 101
    Shorts_SellbotSeeker = 163		        # old: 102
    Skirt_CashbotCatcher = 164		        # old: 103
    Shorts_CashbotCatcher = 165		        # old: 104
    Skirt_LawbotLiberator = 166		        # old: 105
    Shorts_LawbotLiberator = 167		        # old: 106
    Skirt_BossbotBasher = 168		        # old: 107
    Shorts_BossbotBasher = 169		        # old: 108
    OutbackUniformShorts = 170		        # old: 255
    OutbackUniformSkirt = 171		        # old: 109
    Shorts_Alien = 172		                # old: 110
    Shorts_CandyCorn = 173		            # old: 111
    LawbotResistanceShorts = 174		    # old: 258
    LawbotResistanceSkirt = 175		        # old: 112
    Shorts_RetroRobot = 176		            # old: 113
    Shorts_RidingHood = 177		            # old: 260
    Skirt_RidingHood = 178		            # old: 114
    Shorts_Nurse = 179		                # old: 261
    Skirt_Nurse = 180		                # old: 115
    Shorts_LazyBones = 181		            # old: 116
    ## Sailor outfits
    # region
    Shorts_Sailor_White = 182		                # old: 263
    Skirt_Sailor_White = 183		                # old: 117
    Shorts_Sailor_Blue = 184		            # old: 264
    Skirt_Sailor_Blue = 185		            # old: 118
    Shorts_Sailor_Cyan = 186		            # old: 265
    Skirt_Sailor_Cyan = 187		            # old: 119
    Shorts_Sailor_Green = 188		            # old: 266
    Skirt_Sailor_Green = 189		            # old: 120
    Shorts_Sailor_Orange = 190		        # old: 267
    Skirt_Sailor_Orange = 191		            # old: 121
    Shorts_Sailor_Pink = 192		            # old: 268
    Skirt_Sailor_Pink = 193		            # old: 122
    Shorts_Sailor_Purple = 194		        # old: 269
    Skirt_Sailor_Purple = 195		            # old: 123
    Shorts_Sailor_Red = 196		            # old: 270
    Skirt_Sailor_Red = 197		            # old: 124
    Shorts_Sailor_Black = 198		            # old: 271
    Skirt_Sailor_Black = 199		            # old: 125
    Shorts_Sailor_Yellow = 200		        # old: 272
    Skirt_Sailor_Yellow = 201		            # old: 126
    # endregion

    Shorts_TeamTrees = 202		            # old: 127

    RetroWinterShorts = 206		            # old: 276
    RetroWinterSkirt = 207		            # old: 130
    SnowmanShortsB = 208		            # old: 131

    ### NYE Outfits ###
    Shorts_NYE_2019 = 154		            # old: 246
    Skirt_NYE_2019 = 155		            # old: 96
    Shorts_NYE_2020 = 209		        # old: 278
    Skirt_NYE_2020 = 210		            # old: 132
    Shorts_NYE_2021 = 239		        # old: 153
    Skirt_NYE_2021 = 238		            # old: 152
    Shorts_NYE_2022 = 250		        # old: 297
    Skirt_NYE_2022 = 251		            # old: 298
    Shorts_NYE_2023 = 270		        # old: 318
    Skirt_NYE_2023 = 271		            # old: 319
    Shorts_NYE_2024 = 283                # old: 332
    Skirt_NYE_2024 = 284                 # old: 333

    AgentSevenSkirt = 211		            # old: 133
    StPattys2020Skirt = 212		            # old: 134
    StPattys2020Shorts = 213		        # old: 279
    ClownSkirtB = 214		                # old: 135
    ClownShortsB = 215		                # old: 280
    Skirt_SevenStriped = 216		            # old: 136
    Shorts_SevenStriped = 217		        # old: 281
    Skirt_TripleRainbow = 218		        # old: 137
    Shorts_TripleRainbow = 219		        # old: 282
    Skirt_Jester_Red = 221		                # old: 139
    Shorts_Jester_Red = 222		                # old: 284
    Skirt_Jester_Black = 223		            # old: 140
    Shorts_Jester_Black = 224		            # old: 285
    Easter2020Shorts = 225		            # old: 286
    Easter2020Skirt = 226		            # old: 141
    CooktheCogsShorts = 228		            # old: 288
    CooktheCogsSkirt = 229		            # old: 143

    Shorts_Suit_Boardbot = 220		            # old: 138
    Shorts_Suit_Boardbot_Executive = 230		    # old: 144
    Shorts_Suit_Lawbot = 227		            # old: 142

    Shorts_Phantoon = 231		            # old: 145
    Skirt_ToonsmasPast = 232		            # old: 146
    Shorts_ToonsmasPast = 233		        # old: 147
    Skirt_ToonsmasPresent = 234		        # old: 148
    Shorts_ToonsmasPresent = 235		        # old: 149
    Skirt_ToonsmasFuture = 236		        # old: 150
    Shorts_ToonsmasFuture = 237		        # old: 151

    HallowopolisShorts = 241		        # old: 155
    DetectiveShorts = 242		            # old: 289
    FloralShorts = 243		                # old: 290
    Shorts_Newstoon_Blue = 244		        # old: 291
    Skirt_Newstoon_Blue = 245		            # old: 292
    Shorts_Newstoon_Gray = 246		        # old: 293
    Skirt_Newstoon_Gray = 247		            # old: 294
    ChupShorts = 248		                # old: 295
    ChupSkirt = 249		                    # old: 296

    DoctorToonShorts = 252		            # old: 299
    DoctorToonSkirt = 253		            # old: 300
    Shorts_TrolleyEngineer = 254		        # old: 302
    Skirt_TrolleyEngineer = 255		        # old: 303
    StarstruckSkirt = 256		            # old: 304
    RetroShorts = 257		                # old: 305
    StarstruckShorts = 258		            # old: 306
    SleepwalkerShorts = 259		            # old: 307
    FruitPieShorts = 260		            # old: 308
    FruitPieSkirt = 261		                # old: 309
    GumballMachineShorts = 262		        # old: 310
    GumballMachineSkirt = 263		        # old: 311
    CardSuitShorts = 264		            # old: 312
    CardSuitSkirt = 265		                # old: 313
    PainterShorts = 266		                # old: 314
    PainterSkirt = 267		                # old: 315
    Shorts_Chef = 268		                # old: 316
    Skirt_Chef = 269		                    # old: 317

    Shorts_Armor = 272		                # old: 320
    Skirt_Armor = 273		                # old: 321
    HighRollersSuitShorts = 274		        # old: 322
    HighRollersProdigalSuitShorts = 275		# old: 323

    ### NPC Clothing (Not event specific) ###
    # Players can acquire these, however they were specifically designed around the NPC character.
    Shorts_Travis_Rags = 101		        # old: 63
    Shorts_Tumbles = 240		                # old: 154
    Shorts_Webster = 158		            # old: 248
    Skirt_Doe = 159		                    # old: 98
    BroVinci = 278                          # old: 301


@defineItemSubtypeEnum(ItemType.Cosmetic_Hat)
class HatItemType(IntEnum):
    """
    Item subtype enum for Hats.
    """
    """
    It's super important to use a Hat_ prefix (or similar) when defining new hat items.
    Otherwise, it may end up causing a name collision with other items, and that's annoying to deal with.
    Additionally, any color/pattern variations should have their color/pattern as the suffix
    """

    ### Hair ###
    Hair_Pompadour_Classic = 36                  # old: [31, 0, 0], hat
    Hair_Wig_Classic_Rainbow = 51                 # old: [47, 0, 0], hat
    Hair_Brovinci = 172              # old: [124, 0, 0], hat
    Hair_Beehive_Classic = 28                # old: [23, 0, 0], hat

    ### Hairbows ###
    # region
    ## Classic Bows ##
    # region
    Hairbow_Classic_RedPolkaLg = 65                     # old: [3, 1, 0], hat
    Hairbow_Classic_PurplePolkaSm = 66                  # old: [3, 2, 0], hat
    Hairbow_Classic_Black = 89                     # old: [3, 28, 0], hat
    Hairbow_Classic_Yellow = 68  # old: [3, 9, 0], hat
    Hairbow_Classic_BlueChecker = 69  # old: [3, 10, 0], hat
    Hairbow_Classic_Red = 70  # old: [3, 11, 0], hat
    Hairbow_Classic_Rainbow = 71  # old: [3, 12, 0], hat
    Hairbow_Classic_PinkPolka = 73                 # old: [3, 16, 0], hat
    Hairbow_Classic_GreenChecker = 74            # old: [3, 18, 0], hat
    Hairbow_Classic_Pink = 64      # old: [3, 0, 0], hat
    Hairbow_Classic_BluePolkaSm = 170                # old: [3, 49, 0], hat
    Hairbow_Classic_CandyCorn = 133              # old: [3, 36, 0], hat
    # endregion
    
    ## Modern Fancy Bows ##
    Hairbow_Fancy_Black = 238            # old: [120, 85, 0], hat
    Hairbow_Fancy_Blackwhite = 239       # old: [120, 86, 0], hat
    Hairbow_Fancy_Blue = 240             # old: [120, 87, 0], hat
    Hairbow_Fancy_Gray = 241             # old: [120, 88, 0], hat
    Hairbow_Fancy_Green = 242            # old: [120, 89, 0], hat
    Hairbow_Fancy_Orange = 243           # old: [120, 90, 0], hat
    Hairbow_Fancy_Pink = 244             # old: [120, 91, 0], hat
    Hairbow_Fancy_Pinkblack = 245        # old: [120, 92, 0], hat
    Hairbow_Fancy_Polkadot = 246         # old: [120, 93, 0], hat
    Hairbow_Fancy_Purple = 247           # old: [120, 94, 0], hat
    Hairbow_Fancy_Purpleorange = 248     # old: [120, 95, 0], hat
    Hairbow_Fancy_Red = 249              # old: [120, 96, 0], hat
    Hairbow_Fancy_Yellow = 250           # old: [120, 97, 0], hat
    Hairbow_Fancy_Yellowblack = 251      # old: [120, 98, 0], hat
    Hairbow_Fancy_Grayscale = 167           # old: [120, 0, 0], hat

    Hairbow_Ribbon_Red = 218         # old: [146, 0, 0], hat
    Hairbow_Ribbon_Blue = 221  # old: [146, 74, 0], hat
    Hairbow_Ribbon_Brown = 222  # old: [146, 75, 0], hat
    Hairbow_Ribbon_Green = 223  # old: [146, 76, 0], hat
    Hairbow_Ribbon_Orange = 224  # old: [146, 77, 0], hat
    Hairbow_Ribbon_Pink = 225  # old: [146, 78, 0], hat
    Hairbow_Ribbon_Purple = 226  # old: [146, 79, 0], hat
    Hairbow_Ribbon_Rainbow = 227  # old: [146, 80, 0], hat

    Hairbow_Pride_Ace = 252           # old: [120, 99, 0], hat
    Hairbow_Pride_Aro = 253           # old: [120, 100, 0], hat
    Hairbow_Pride_Bi = 254            # old: [120, 101, 0], hat
    Hairbow_Pride_Gay = 255           # old: [120, 102, 0], hat
    Hairbow_Pride_Genderfluid = 256   # old: [120, 103, 0], hat
    Hairbow_Pride_Lesbian = 257       # old: [120, 104, 0], hat
    Hairbow_Pride_Lgbt = 258          # old: [120, 105, 0], hat
    Hairbow_Pride_Nb = 259            # old: [120, 106, 0], hat
    Hairbow_Pride_Pan = 260           # old: [120, 107, 0], hat
    Hairbow_Pride_Trans = 261         # old: [120, 108, 0], hat
    
    Hairbow_Bat = 77                     # old: [58, 0, 0], hat
    Hairbow_Diploma = 160                   # old: [113, 0, 0], hat

    # endregion

    ### Headbands ###
    # region
    Headband_Hearts_Classic_Pink = 5       # old: [4, 0, 0], hat
    Headband_Hearts_Classic_Yellow = 6                # old: [4, 3, 0], hat
    Headband_Antenna_Spider_Classic = 27                    # old: [22, 0, 0], hat
    Headband_Antenna_Webbed_Classic = 39              # old: [35, 0, 0], hat
    Headband_Feathers_Classic = 32            # old: [27, 0, 0], hat
    Headband_Sweatband = 35                  # old: [30, 0, 0], hat
    Headband_SpinDoctor = 132            # old: [96, 35, 0], hat
    Headband_SpyHeadset = 266                # old: [156, 0, 0], hat
    Headband_Robophones = 130                # old: [95, 0, 0], hat
    Headband_Alchemist_Goggles = 88           # old: [64, 0, 0], hat
    Headband_RainbowPhones = 154             # old: [108, 0, 0], hat
    Headband_ElectricBolts = 79              # old: [60, 0, 0], hat
    Headband_Antlers = 107                   # old: [82, 0, 0], hat
    Headband_Present = 164               # old: [117, 0, 0], hat
    Headband_LuckyClover = 152                # old: [106, 0, 0], hat
    Headband_LuckyClip = 153                # old: [107, 0, 0], hat
    
    Headband_Horns_Black = 123                # old: [93, 0, 0], hat
    Headband_Horns_Blue = 124            # old: [93, 29, 0], hat
    Headband_Horns_Green = 125           # old: [93, 30, 0], hat
    Headband_Horns_Orange = 126          # old: [93, 31, 0], hat
    Headband_Horns_Purple = 127          # old: [93, 32, 0], hat
    Headband_Horns_Red = 128             # old: [93, 33, 0], hat
    Headband_Horns_Yellow = 135          # old: [93, 37, 0], hat
    Headband_Bandana_Deluxe = 171             # old: [123, 0, 0], hat

    # endregion

    ### Helmets ###
    # region
    Helmet_Miner_Classic = 47                   # old: [43, 0, 0], hat
    Helmet_Conquistador_Classic = 44         # old: [40, 0, 0], hat
    Helmet_Firefighter_Classic = 45          # old: [41, 0, 0], hat
    Helmet_Roman_Classic = 38                # old: [34, 0, 0], hat

    Helmet_Ski_Vintage = 139  # old: [100, 0, 0], hat
    Helmet_Ski_Blue = 140  # old: [100, 38, 0], hat
    Helmet_Ski_Green = 141  # old: [100, 39, 0], hat
    Helmet_Ski_Gray = 142  # old: [100, 40, 0], hat
    Helmet_Ski_Pink = 143  # old: [100, 41, 0], hat
    Helmet_Ski_Rainbow = 144  # old: [100, 42, 0], hat
    Helmet_Ski_Red = 145  # old: [100, 43, 0], hat
    
    Helmet_WingSuit = 177         # old: [129, 0, 0], hat
    # endregion

    ### HATS ###
    # region
    ## Gag Hats ##
    Hat_Gag_Classic_Anvil = 9                    # old: [6, 0, 0], hat
    Hat_Gag_Classic_FlowerPot = 10                  # old: [7, 0, 0], hat
    Hat_Gag_Classic_Sandbag = 11                 # old: [8, 0, 0], hat
    Hat_Gag_Classic_BigWeight = 12                  # old: [9, 0, 0], hat
    Hat_Gag_BowlingBall = 136               # old: [97, 0, 0], hat
    Hat_Gag_FruitPie = 137                  # old: [98, 0, 0], hat
    Hat_Gag_TV = 148                     # old: [103, 0, 0], hat
    Hat_Gag_BananaPeel = 176              # old: [128, 0, 0], hat

    ## Crown Hats ##
    # region
    Hat_Crown_Classic = 18                      # old: [14, 0, 0], hat

    Hat_Crown_Tiara_Pink = 40                      # old: [36, 0, 0], hat

    Hat_Crown_Flower_White = 185  # old: [133, 0, 0], hat
    Hat_Crown_Flower_Blue = 186  # old: [133, 54, 0], hat
    Hat_Crown_Flower_Cyan = 187  # old: [133, 55, 0], hat
    Hat_Crown_Flower_Cyanpurple = 188  # old: [133, 56, 0], hat
    Hat_Crown_Flower_Green = 189  # old: [133, 57, 0], hat
    Hat_Crown_Flower_Orange = 190  # old: [133, 58, 0], hat
    Hat_Crown_Flower_Orangepink = 191  # old: [133, 59, 0], hat
    Hat_Crown_Flower_Pink = 192  # old: [133, 60, 0], hat
    Hat_Crown_Flower_Pinkblue = 193  # old: [133, 61, 0], hat
    Hat_Crown_Flower_Purple = 194  # old: [133, 62, 0], hat
    Hat_Crown_Flower_Red = 195  # old: [133, 63, 0], hat
    Hat_Crown_Flower_Redyellow = 196  # old: [133, 64, 0], hat
    Hat_Crown_Flower_Yellow = 197  # old: [133, 65, 0], hat
    
    Hat_Crown_Rose_White = 198  # old: [134, 0, 0], hat
    Hat_Crown_Rose_Blue = 199  # old: [134, 66, 0], hat
    Hat_Crown_Rose_Cyan = 200  # old: [134, 67, 0], hat
    Hat_Crown_Rose_Green = 201  # old: [134, 68, 0], hat
    Hat_Crown_Rose_Orange = 202  # old: [134, 69, 0], hat
    Hat_Crown_Rose_Pink = 203  # old: [134, 70, 0], hat
    Hat_Crown_Rose_Purple = 204  # old: [134, 71, 0], hat
    Hat_Crown_Rose_Red = 205  # old: [134, 72, 0], hat
    Hat_Crown_Rose_Yellow = 206  # old: [134, 73, 0], hat

    Hat_Crown_Card = 214              # old: [142, 0, 0], hat
    # endregion
    
    ## Baseball Hats ##
    Hat_BaseballCap_Classic_Green = 1                # old: [1, 0, 0], hat
    Hat_BaseballCap_Classic_Blue = 19                # old: [1, 7, 0], hat
    Hat_BaseballCap_Classic_Orange = 20              # old: [1, 8, 0], hat
    Hat_BaseballCap_Classic_Yellow = 52              # old: [1, 13, 0], hat
    Hat_BaseballCap_Classic_Red = 53                 # old: [1, 14, 0], hat
    Hat_BaseballCap_Classic_Aqua = 54                # old: [1, 15, 0], hat
    Hat_BaseballCap_Classic_Purple = 59              # old: [1, 17, 0], hat
    
    Hat_Safari_Classic_Beige = 2              # old: [2, 0, 0], hat
    Hat_Safari_Classic_Brown = 3              # old: [2, 5, 0], hat
    Hat_Safari_Classic_Green = 4              # old: [2, 6, 0], hat

    Hat_Top_Classic_Black = 7                 # old: [5, 0, 0], hat
    Hat_Top_Classic_Blue = 8                  # old: [5, 4, 0], hat
    Hat_Top_Lucky = 150            # old: [104, 0, 0], hat
    Hat_Top_Tartan = 151             # old: [105, 0, 0], hat
    Hat_Top_Card = 215             # old: [143, 0, 0], hat

    Hat_Fez_Classic = 13                     # old: [10, 0, 0], hat
    Hat_Golf_Classic = 14                    # old: [11, 0, 0], hat
    Hat_Party_Classic_Blue = 15                   # old: [12, 0, 0], hat
    Hat_Party_Classic_Anniversary = 16               # old: [12, 19, 0], hat
    Hat_Fancy_Classic = 17                   # old: [13, 0, 0], hat
    Hat_Cowboy_Classic = 21                  # old: [15, 0, 0], hat
    Hat_Propeller_Classic = 23               # old: [17, 0, 0], hat
    Hat_Fishing_Classic = 24                 # old: [18, 0, 0], hat
    Hat_Sombrero_Classic = 25                   # old: [19, 0, 0], hat
    Hat_Straw_Classic = 26                   # old: [20, 0, 0], hat

    Hat_Bowler_Classic = 29                  # old: [24, 0, 0], hat
    Hat_Bowler_Clown = 155                  # old: [109, 0, 0], hat

    Hat_Chef_Classic = 30                    # old: [25, 0, 0], hat
    Hat_Detective_Classic = 31               # old: [26, 0, 0], hat
    Hat_Fedora_Classic = 33                     # old: [28, 0, 0], hat
    Hat_Fedora_Classic_AgentSeven = 149               # old: [28, 44, 0], hat
    Hat_Shako_Classic = 34           # old: [29, 0, 0], hat
    Hat_Archer_Classic = 37                  # old: [33, 0, 0], hat
    Hat_Viking_Classic = 41               # old: [37, 0, 0], hat
    Hat_Witch_Classic = 42                   # old: [38, 0, 0], hat
    Hat_TinFoil_Classic = 46                 # old: [42, 0, 0], hat
    Hat_Napoleon_Classic = 48                # old: [44, 0, 0], hat
    Hat_Sailor_Classic = 55                  # old: [48, 0, 0], hat
    Hat_Samba_Classic = 56                   # old: [49, 0, 0], hat
    Hat_Bobby_Classic = 57                   # old: [50, 0, 0], hat
    Hat_Jughead_Classic = 58                 # old: [51, 0, 0], hat
    Hat_Winter_Classic = 60                  # old: [52, 0, 0], hat
    Hat_Toonosaur_Classic = 61               # old: [54, 0, 0], hat
    Hat_Jamboree_Classic = 62                # old: [55, 0, 0], hat
    Hat_Bird_Classic = 63                    # old: [56, 0, 0], hat
    Hat_Sun_Classic = 67                     # old: [21, 0, 0], hat
    Hat_Princess_Classic = 72                # old: [32, 0, 0], hat

    Hat_Pirate_Classic = 22                  # old: [16, 0, 0], hat
    Hat_Pirate_Bandana_Classic = 75                    # old: [53, 0, 0], hat
    Hat_Pirate_Ghost = 267            # old: [157, 0, 0], hat

    Hat_Cauldron = 78                # old: [59, 0, 0], hat
    Hat_PumpkinBucket = 80              # old: [61, 0, 0], hat
    Hat_Scarecrow = 81               # old: [62, 0, 0], hat
    Hat_Pilot_Classic = 49                   # old: [45, 0, 0], hat
    Hat_Cop_Classic = 50                     # old: [46, 0, 0], hat
    Hat_Engineer_Trolley = 178            # old: [130, 0, 0], hat
    Hat_Frankenstein = 87                  # old: [63, 0, 0], hat

    Hat_Wizard_Enchanted_Stars_Black = 82                # old: [39, 23, 0], hat
    Hat_Wizard_Enchanted_Stars_Pink = 83                 # old: [39, 26, 0], hat
    Hat_Wizard_Enchanted_Stars_Red = 84                  # old: [39, 25, 0], hat
    Hat_Wizard_Enchanted_Stars_Green = 85                # old: [39, 24, 0], hat
    Hat_Wizard_Enchanted_Stars_Blue = 86                 # old: [39, 22, 0], hat
    Hat_Wizard_Enchanted_Traffic_Orange = 265       # old: [39, 109, 0], hat
    Hat_Wizard_Enchanted_Stars_Purple = 43                  # old: [39, 0, 0], hat

    Hat_Santa_Red = 96                   # old: [71, 0, 0], hat
    Hat_Santa_Rainbow = 97               # old: [72, 0, 0], hat
    Hat_Santa_Green = 98                   # old: [73, 0, 0], hat
    Hat_Elf_Red = 99                     # old: [74, 0, 0], hat
    Hat_Elf_Green = 268            # old: [74, 111, 0]

    Hat_Star = 100                   # old: [75, 0, 0], hat

    Hat_Soldier_Humble = 101                 # old: [76, 0, 0], hat
    Hat_Soldier_Regal = 102                  # old: [77, 0, 0], hat
    Hat_Soldier_Tradi = 103                  # old: [78, 0, 0], hat
    Hat_Soldier_Homemade = 147                # old: [102, 0, 0], hat

    Hat_Ragdoll_Humble = 104             # old: [79, 0, 0], hat
    Hat_Ragdoll_Tradi = 105              # old: [80, 0, 0], hat
    Hat_Ragdoll_Regal = 106              # old: [81, 0, 0], hat
    Hat_Ragdoll_Homemade = 138                # old: [99, 0, 0], hat

    Hat_Books_Webster = 109            # old: [84, 0, 0], hat
    Hat_Umbrella = 110                  # old: [85, 0, 0], hat
    Hat_Aviator = 111                # old: [86, 0, 0], hat
    Hat_Outback_Slouch = 113                # old: [88, 0, 0], hat
    Hat_Outback_Cork = 114            # old: [89, 0, 0], hat
    Hat_Outback_Gecko = 115           # old: [90, 0, 0], hat
    Hat_Alien = 116                  # old: [91, 0, 0], hat

    Hood_Riding = 129            # old: [94, 0, 0], hat
    Hood_Future = 165                # old: [118, 0, 0], hat

    Hat_Nurse = 131                  # old: [48, 34, 0], hat
    Hat_Snowman = 146                # old: [101, 0, 0], hat

    Hat_Jester_Red = 156                 # old: [110, 45, 0], hat
    Hat_Jester_Black = 157                # old: [110, 46, 0], hat
    Hat_Grill = 161                     # old: [114, 48, 0], hat
    Hat_Leaf_Autumn = 162                   # old: [115, 0, 0], hat
    Hat_Candle = 163                 # old: [116, 0, 0], hat
    Hat_Plant_Fern = 166                  # old: [119, 0, 0], hat
    Hat_GhostlyGibus = 168                   # old: [121, 0, 0], hat
    Hat_Plant_NumberOne = 169                # old: [122, 0, 0], hat
    Hat_SmartCap = 174               # old: [126, 0, 0], hat
    
    Hat_Donut_Pink = 179              # old: [131, 0, 0], hat
    Hat_Donut_Blue = 180              # old: [131, 50, 0], hat
    Hat_Donut_Chocolate = 181         # old: [131, 51, 0], hat
    Hat_Donut_Lemon = 182             # old: [131, 52, 0], hat
    Hat_Donut_Vanilla = 183           # old: [131, 53, 0], hat
    
    Hat_Beret_Cruller = 184              # old: [132, 0, 0], hat
    Hat_Beret_Painter = 220              # old: [148, 0, 0], hat
    Hat_Beret_Simple_Black = 212             # old: [140, 0, 0], hat

    Hat_Beanie_Clownfish = 175            # old: [127, 0, 0], hat
    Hat_Beanie_Easter = 158              # old: [111, 0, 0], hat
    Hat_Beanie_Doe_Yellow = 108                 # old: [83, 0, 0], hat
    Hat_Beanie_Bobble_Blue = 90                 # old: [65, 0, 0], hat
    Hat_Beanie_Bobble_Green = 91                # old: [66, 0, 0], hat
    Hat_Beanie_Bobble_Grey = 92                 # old: [67, 0, 0], hat
    Hat_Beanie_Bobble_Pink = 93                 # old: [68, 0, 0], hat
    Hat_Beanie_Bobble_Rainbow = 94              # old: [69, 0, 0], hat
    Hat_Beanie_Bobble_Red = 95                  # old: [70, 0, 0], hat

    Hat_NightCap = 211               # old: [139, 0, 0], hat
    Hat_Butter = 216                 # old: [144, 0, 0], hat

    Hat_Chainsaw = 207               # old: [135, 0, 0], hat
    Hat_Multislacker = 208           # old: [136, 0, 0], hat
    Hat_Treekiller = 209             # old: [137, 0, 0], hat
    Hat_Featherbedder = 210          # old: [138, 0, 0], hat
    Hat_Firestarter = 219            # old: [147, 0, 0], hat
    Hat_Witchhunter = 228            # old: [149, 0, 0], hat
    
    Hat_Skelecog_Blue = 159                # old: [112, 47, 0], hat
    Hat_Skelecog_Purple = 234                # old: [112, 84, 0], hat

    Hat_GoonPatrol_Yellow = 229       # old: [150, 0, 0], hat
    Hat_GoonPatrol_Orange = 230       # old: [150, 81, 0], hat
    Hat_GoonPatrol_Red = 231          # old: [150, 82, 0], hat
    Hat_GoonPatrol_Purple = 232       # old: [150, 83, 0], hat
    Hat_GoonSecurity = 233           # old: [151, 0, 0], hat
    Hat_CogBucket = 235              # old: [152, 0, 0], hat
    Hat_LowBaller = 236              # old: [153, 0, 0], hat
    Hat_HighRoller = 237             # old: [154, 0, 0], hat

    Hat_Cyberpunk = 262              # old: [155, 0, 0], hat
    Hat_MuzzleRose = 263                # old: [53, 0, 0], glasses
    Hat_PainterBrush = 264              # old: [54, 0, 0], glasses
    # endregion

    ### Overheads ###
    # region
    ## Pumpkin Heads ##
    # region
    Overhead_Pumpkin_Classic_Short  = 1000  # old: 19, cheesy effect
    Overhead_Pumpkin_Classic_Tall  = 1001  # old: 19, cheesy effect
    Overhead_Pumpkin_2018_Short   = 1002  # old: 12, cheesy effect
    Overhead_Pumpkin_2018_Tall   = 1003  # old: 12, cheesy effect
    Overhead_Pumpkin_2019_Short   = 1004  # old: 16, cheesy effect
    Overhead_Pumpkin_2019_Tall   = 1005  # old: 16, cheesy effect
    Overhead_Pumpkin_2020_Short = 1006  # old: 17, cheesy effect
    Overhead_Pumpkin_2020_Tall = 1007  # old: 17, cheesy effect
    Overhead_Pumpkin_2021_Short  = 1008  # old: 18, cheesy effect
    Overhead_Pumpkin_2021_Tall  = 1009  # old: 18, cheesy effect
    # No 2022 pumpkin :V
    Overhead_Pumpkin_2023_Short   = 1010  # old: 24, cheesy effect
    Overhead_Pumpkin_2023_Tall   = 1011  # old: 24, cheesy effect
    # endregion
    Overhead_Icecube = 173                # old: [125, 0, 0], hat
    Overhead_SpaceHelmet = 76                  # old: [57, 0, 0], hat
    Overhead_Gumball = 213             # old: [141, 0, 0], hat

    # endregion

    ### Tops ###
    # region
    ## Halos ##
    Top_Halo_White = 117                 # old: [92, 0, 0], hat
    Top_Halo_Blue = 118             # old: [92, 29, 0], hat
    Top_Halo_Green = 119            # old: [92, 30, 0], hat
    Top_Halo_Orange = 120           # old: [92, 31, 0], hat
    Top_Halo_Purple = 121           # old: [92, 32, 0], hat
    Top_Halo_Red = 122              # old: [92, 33, 0], hat
    Top_Halo_Yellow = 134           # old: [92, 37, 0], hat

    Top_Raincloud = 217    # old: [145, 0, 0], hat
    Top_Cake_Anniversary = 112                   # old: [87, 0, 0], hat
    # endregion

    ### Altis legacy hat styles (auto-ported from ToonDNA.HatStyles) ###
    Altis_alchemist_goggles = 100000  # was ToonDNA style 'alchemist_goggles'
    Altis_alien_hat = 100001  # was ToonDNA style 'alien_hat'
    Altis_angel_halo = 100002  # was ToonDNA style 'angel_halo'
    Altis_angel_halo_blue = 100003  # was ToonDNA style 'angel_halo_blue'
    Altis_angel_halo_green = 100004  # was ToonDNA style 'angel_halo_green'
    Altis_angel_halo_orange = 100005  # was ToonDNA style 'angel_halo_orange'
    Altis_angel_halo_purple = 100006  # was ToonDNA style 'angel_halo_purple'
    Altis_angel_halo_red = 100007  # was ToonDNA style 'angel_halo_red'
    Altis_angel_halo_yellow = 100008  # was ToonDNA style 'angel_halo_yellow'
    Altis_antlers = 100009  # was ToonDNA style 'antlers'
    Altis_atticus_hat = 100010  # was ToonDNA style 'atticus_hat'
    Altis_aviator_hat = 100011  # was ToonDNA style 'aviator_hat'
    Altis_bandana_deluxe = 100012  # was ToonDNA style 'bandana-deluxe'
    Altis_bat_bow = 100013  # was ToonDNA style 'bat_bow'
    Altis_bobble_blue = 100014  # was ToonDNA style 'bobble_blue'
    Altis_bobble_green = 100015  # was ToonDNA style 'bobble_green'
    Altis_bobble_grey = 100016  # was ToonDNA style 'bobble_grey'
    Altis_bobble_pink = 100017  # was ToonDNA style 'bobble_pink'
    Altis_bobble_rainbow = 100018  # was ToonDNA style 'bobble_rainbow'
    Altis_bobble_red = 100019  # was ToonDNA style 'bobble_red'
    Altis_bowling_ball = 100020  # was ToonDNA style 'bowling_ball'
    Altis_brovinci_hair = 100021  # was ToonDNA style 'brovinci_hair'
    Altis_cake_hat = 100022  # was ToonDNA style 'cake_hat'
    Altis_candle_hat = 100023  # was ToonDNA style 'candle_hat'
    Altis_candycorn_bow = 100024  # was ToonDNA style 'candycorn_bow'
    Altis_cauldron_hat = 100025  # was ToonDNA style 'cauldron_hat'
    Altis_clown_hat = 100026  # was ToonDNA style 'clown_hat'
    Altis_cruller_beret = 100027  # was ToonDNA style 'cruller_beret'
    Altis_demon_horns = 100028  # was ToonDNA style 'demon_horns'
    Altis_demon_horns_blue = 100029  # was ToonDNA style 'demon_horns_blue'
    Altis_demon_horns_green = 100030  # was ToonDNA style 'demon_horns_green'
    Altis_demon_horns_orange = 100031  # was ToonDNA style 'demon_horns_orange'
    Altis_demon_horns_purple = 100032  # was ToonDNA style 'demon_horns_purple'
    Altis_demon_horns_red = 100033  # was ToonDNA style 'demon_horns_red'
    Altis_demon_horns_yellow = 100034  # was ToonDNA style 'demon_horns_yellow'
    Altis_diploma = 100035  # was ToonDNA style 'diploma'
    Altis_doe_beanie = 100036  # was ToonDNA style 'doe_beanie'
    Altis_donuthat_blue = 100037  # was ToonDNA style 'donuthat_blue'
    Altis_donuthat_chocolate = 100038  # was ToonDNA style 'donuthat_chocolate'
    Altis_donuthat_lemon = 100039  # was ToonDNA style 'donuthat_lemon'
    Altis_donuthat_pink = 100040  # was ToonDNA style 'donuthat_pink'
    Altis_donuthat_vanilla = 100041  # was ToonDNA style 'donuthat_vanilla'
    Altis_easter_beanie = 100042  # was ToonDNA style 'easter_beanie'
    Altis_electric_bolts = 100043  # was ToonDNA style 'electric_bolts'
    Altis_elf_green = 100044  # was ToonDNA style 'elf_green'
    Altis_elf_jolly_green = 100045  # was ToonDNA style 'elf_jolly_green'
    Altis_elf_red = 100046  # was ToonDNA style 'elf_red'
    Altis_flowercrown_blue = 100047  # was ToonDNA style 'flowercrown_blue'
    Altis_flowercrown_cyan = 100048  # was ToonDNA style 'flowercrown_cyan'
    Altis_flowercrown_cyanpurple = 100049  # was ToonDNA style 'flowercrown_cyanpurple'
    Altis_flowercrown_green = 100050  # was ToonDNA style 'flowercrown_green'
    Altis_flowercrown_orange = 100051  # was ToonDNA style 'flowercrown_orange'
    Altis_flowercrown_orangepink = 100052  # was ToonDNA style 'flowercrown_orangepink'
    Altis_flowercrown_pink = 100053  # was ToonDNA style 'flowercrown_pink'
    Altis_flowercrown_pinkblue = 100054  # was ToonDNA style 'flowercrown_pinkblue'
    Altis_flowercrown_purple = 100055  # was ToonDNA style 'flowercrown_purple'
    Altis_flowercrown_red = 100056  # was ToonDNA style 'flowercrown_red'
    Altis_flowercrown_redyellow = 100057  # was ToonDNA style 'flowercrown_redyellow'
    Altis_flowercrown_white = 100058  # was ToonDNA style 'flowercrown_white'
    Altis_flowercrown_yellow = 100059  # was ToonDNA style 'flowercrown_yellow'
    Altis_frank_head = 100060  # was ToonDNA style 'frank_head'
    Altis_fruit_pie = 100061  # was ToonDNA style 'fruit_pie'
    Altis_future_hood = 100062  # was ToonDNA style 'future_hood'
    Altis_gb_hairbow_black = 100063  # was ToonDNA style 'gb_hairbow_black'
    Altis_gb_hairbow_blackwhite = 100064  # was ToonDNA style 'gb_hairbow_blackwhite'
    Altis_gb_hairbow_blue = 100065  # was ToonDNA style 'gb_hairbow_blue'
    Altis_gb_hairbow_gray = 100066  # was ToonDNA style 'gb_hairbow_gray'
    Altis_gb_hairbow_green = 100067  # was ToonDNA style 'gb_hairbow_green'
    Altis_gb_hairbow_orange = 100068  # was ToonDNA style 'gb_hairbow_orange'
    Altis_gb_hairbow_pink = 100069  # was ToonDNA style 'gb_hairbow_pink'
    Altis_gb_hairbow_pinkblack = 100070  # was ToonDNA style 'gb_hairbow_pinkblack'
    Altis_gb_hairbow_polkadot = 100071  # was ToonDNA style 'gb_hairbow_polkadot'
    Altis_gb_hairbow_purple = 100072  # was ToonDNA style 'gb_hairbow_purple'
    Altis_gb_hairbow_purpleorange = 100073  # was ToonDNA style 'gb_hairbow_purpleorange'
    Altis_gb_hairbow_red = 100074  # was ToonDNA style 'gb_hairbow_red'
    Altis_gb_hairbow_yellow = 100075  # was ToonDNA style 'gb_hairbow_yellow'
    Altis_gb_hairbow_yellowblack = 100076  # was ToonDNA style 'gb_hairbow_yellowblack'
    Altis_grill = 100077  # was ToonDNA style 'grill'
    Altis_hat_number1 = 100078  # was ToonDNA style 'hat-number1'
    Altis_hat1 = 100079  # was ToonDNA style 'hat1'
    Altis_hat2 = 100080  # was ToonDNA style 'hat2'
    Altis_hat_bananahat = 100081  # was ToonDNA style 'hat_bananahat'
    Altis_hat_blackberet = 100082  # was ToonDNA style 'hat_blackberet'
    Altis_hat_butter = 100083  # was ToonDNA style 'hat_butter'
    Altis_hat_cardCrown = 100084  # was ToonDNA style 'hat_cardCrown'
    Altis_hat_cardTopHat = 100085  # was ToonDNA style 'hat_cardTopHat'
    Altis_hat_chainsaw = 100086  # was ToonDNA style 'hat_chainsaw'
    Altis_hat_clownbeanie = 100087  # was ToonDNA style 'hat_clownbeanie'
    Altis_hat_cog_bucket = 100088  # was ToonDNA style 'hat_cog_bucket'
    Altis_hat_cyberpunk = 100089  # was ToonDNA style 'hat_cyberpunk'
    Altis_hat_engineer_cap = 100090  # was ToonDNA style 'hat_engineer_cap'
    Altis_hat_featherbedder = 100091  # was ToonDNA style 'hat_featherbedder'
    Altis_hat_firestarter = 100092  # was ToonDNA style 'hat_firestarter'
    Altis_hat_foreman = 100093  # was ToonDNA style 'hat_foreman'
    Altis_hat_goon_patrol_orange = 100094  # was ToonDNA style 'hat_goon_patrol_orange'
    Altis_hat_goon_patrol_purple = 100095  # was ToonDNA style 'hat_goon_patrol_purple'
    Altis_hat_goon_patrol_red = 100096  # was ToonDNA style 'hat_goon_patrol_red'
    Altis_hat_goon_patrol_yellow = 100097  # was ToonDNA style 'hat_goon_patrol_yellow'
    Altis_hat_goon_security = 100098  # was ToonDNA style 'hat_goon_security'
    Altis_hat_gumball_hairbow = 100099  # was ToonDNA style 'hat_gumball_hairbow'
    Altis_hat_gumball_hairbow_b = 100100  # was ToonDNA style 'hat_gumball_hairbow_b'
    Altis_hat_gumball_hairbow_br = 100101  # was ToonDNA style 'hat_gumball_hairbow_br'
    Altis_hat_gumball_hairbow_g = 100102  # was ToonDNA style 'hat_gumball_hairbow_g'
    Altis_hat_gumball_hairbow_or = 100103  # was ToonDNA style 'hat_gumball_hairbow_or'
    Altis_hat_gumball_hairbow_p = 100104  # was ToonDNA style 'hat_gumball_hairbow_p'
    Altis_hat_gumball_hairbow_pu = 100105  # was ToonDNA style 'hat_gumball_hairbow_pu'
    Altis_hat_gumball_hairbow_rb = 100106  # was ToonDNA style 'hat_gumball_hairbow_rb'
    Altis_hat_gumballhat = 100107  # was ToonDNA style 'hat_gumballhat'
    Altis_hat_high_roller = 100108  # was ToonDNA style 'hat_high_roller'
    Altis_hat_icecube = 100109  # was ToonDNA style 'hat_icecube'
    Altis_hat_low_baller = 100110  # was ToonDNA style 'hat_low_baller'
    Altis_hat_multislacker = 100111  # was ToonDNA style 'hat_multislacker'
    Altis_hat_nightcap = 100112  # was ToonDNA style 'hat_nightcap'
    Altis_hat_pirate_ghost = 100113  # was ToonDNA style 'hat_pirate_ghost'
    Altis_hat_rainmaker_depression = 100114  # was ToonDNA style 'hat_rainmaker_depression'
    Altis_hat_smartcap = 100115  # was ToonDNA style 'hat_smartcap'
    Altis_hat_treekiller = 100116  # was ToonDNA style 'hat_treekiller'
    Altis_hat_wingsuit_helmet = 100117  # was ToonDNA style 'hat_wingsuit_helmet'
    Altis_hat_witchhunter = 100118  # was ToonDNA style 'hat_witchhunter'
    Altis_hav1 = 100119  # was ToonDNA style 'hav1'
    Altis_hbb1 = 100120  # was ToonDNA style 'hbb1'
    Altis_hbb2 = 100121  # was ToonDNA style 'hbb2'
    Altis_hbb3 = 100122  # was ToonDNA style 'hbb3'
    Altis_hbb4 = 100123  # was ToonDNA style 'hbb4'
    Altis_hbb5 = 100124  # was ToonDNA style 'hbb5'
    Altis_hbb6 = 100125  # was ToonDNA style 'hbb6'
    Altis_hbb7 = 100126  # was ToonDNA style 'hbb7'
    Altis_hbn1 = 100127  # was ToonDNA style 'hbn1'
    Altis_hbw1 = 100128  # was ToonDNA style 'hbw1'
    Altis_hby1 = 100129  # was ToonDNA style 'hby1'
    Altis_hch1 = 100130  # was ToonDNA style 'hch1'
    Altis_hcr1 = 100131  # was ToonDNA style 'hcr1'
    Altis_hcw1 = 100132  # was ToonDNA style 'hcw1'
    Altis_hdt1 = 100133  # was ToonDNA style 'hdt1'
    Altis_headset_spy = 100134  # was ToonDNA style 'headset_spy'
    Altis_hfd1 = 100135  # was ToonDNA style 'hfd1'
    Altis_hfp1 = 100136  # was ToonDNA style 'hfp1'
    Altis_hfp2 = 100137  # was ToonDNA style 'hfp2'
    Altis_hfr1 = 100138  # was ToonDNA style 'hfr1'
    Altis_hfs1 = 100139  # was ToonDNA style 'hfs1'
    Altis_hft1 = 100140  # was ToonDNA style 'hft1'
    Altis_hft2 = 100141  # was ToonDNA style 'hft2'
    Altis_hfz1 = 100142  # was ToonDNA style 'hfz1'
    Altis_hgf1 = 100143  # was ToonDNA style 'hgf1'
    Altis_hhd1 = 100144  # was ToonDNA style 'hhd1'
    Altis_hhd2 = 100145  # was ToonDNA style 'hhd2'
    Altis_hhm1 = 100146  # was ToonDNA style 'hhm1'
    Altis_hhm2 = 100147  # was ToonDNA style 'hhm2'
    Altis_hhm3 = 100148  # was ToonDNA style 'hhm3'
    Altis_hhm4 = 100149  # was ToonDNA style 'hhm4'
    Altis_hhm5 = 100150  # was ToonDNA style 'hhm5'
    Altis_hht1 = 100151  # was ToonDNA style 'hht1'
    Altis_hht2 = 100152  # was ToonDNA style 'hht2'
    Altis_hhw1 = 100153  # was ToonDNA style 'hhw1'
    Altis_hhw2 = 100154  # was ToonDNA style 'hhw2'
    Altis_hjh1 = 100155  # was ToonDNA style 'hjh1'
    Altis_hmk1 = 100156  # was ToonDNA style 'hmk1'
    Altis_hnp1 = 100157  # was ToonDNA style 'hnp1'
    Altis_hob1 = 100158  # was ToonDNA style 'hob1'
    Altis_hpb1 = 100159  # was ToonDNA style 'hpb1'
    Altis_hpc1 = 100160  # was ToonDNA style 'hpc1'
    Altis_hpc2 = 100161  # was ToonDNA style 'hpc2'
    Altis_hph1 = 100162  # was ToonDNA style 'hph1'
    Altis_hpp1 = 100163  # was ToonDNA style 'hpp1'
    Altis_hpr1 = 100164  # was ToonDNA style 'hpr1'
    Altis_hpt1 = 100165  # was ToonDNA style 'hpt1'
    Altis_hpt2 = 100166  # was ToonDNA style 'hpt2'
    Altis_hrb1 = 100167  # was ToonDNA style 'hrb1'
    Altis_hrb2 = 100168  # was ToonDNA style 'hrb2'
    Altis_hrb3 = 100169  # was ToonDNA style 'hrb3'
    Altis_hrb4 = 100170  # was ToonDNA style 'hrb4'
    Altis_hrb5 = 100171  # was ToonDNA style 'hrb5'
    Altis_hrb6 = 100172  # was ToonDNA style 'hrb6'
    Altis_hrb7 = 100173  # was ToonDNA style 'hrb7'
    Altis_hrb8 = 100174  # was ToonDNA style 'hrb8'
    Altis_hrb9 = 100175  # was ToonDNA style 'hrb9'
    Altis_hrh1 = 100176  # was ToonDNA style 'hrh1'
    Altis_hsb1 = 100177  # was ToonDNA style 'hsb1'
    Altis_hsf1 = 100178  # was ToonDNA style 'hsf1'
    Altis_hsf2 = 100179  # was ToonDNA style 'hsf2'
    Altis_hsf3 = 100180  # was ToonDNA style 'hsf3'
    Altis_hsg1 = 100181  # was ToonDNA style 'hsg1'
    Altis_hsl1 = 100182  # was ToonDNA style 'hsl1'
    Altis_hst1 = 100183  # was ToonDNA style 'hst1'
    Altis_hsu1 = 100184  # was ToonDNA style 'hsu1'
    Altis_htp1 = 100185  # was ToonDNA style 'htp1'
    Altis_htp2 = 100186  # was ToonDNA style 'htp2'
    Altis_htr1 = 100187  # was ToonDNA style 'htr1'
    Altis_hw_gibus = 100188  # was ToonDNA style 'hw_gibus'
    Altis_hwg1 = 100189  # was ToonDNA style 'hwg1'
    Altis_hwt1 = 100190  # was ToonDNA style 'hwt1'
    Altis_hwt2 = 100191  # was ToonDNA style 'hwt2'
    Altis_hwz1 = 100192  # was ToonDNA style 'hwz1'
    Altis_hwz2 = 100193  # was ToonDNA style 'hwz2'
    Altis_jester_b_hat = 100194  # was ToonDNA style 'jester_b_hat'
    Altis_jester_hat = 100195  # was ToonDNA style 'jester_hat'
    Altis_leaf_hat = 100196  # was ToonDNA style 'leaf_hat'
    Altis_newstoon_gray_bow = 100197  # was ToonDNA style 'newstoon_gray_bow'
    Altis_nurse_hat = 100198  # was ToonDNA style 'nurse_hat'
    Altis_outback_corkhat = 100199  # was ToonDNA style 'outback_corkhat'
    Altis_outback_geckohat = 100200  # was ToonDNA style 'outback_geckohat'
    Altis_outback_hat = 100201  # was ToonDNA style 'outback_hat'
    Altis_painter_beret = 100202  # was ToonDNA style 'painter_beret'
    Altis_plant_hat = 100203  # was ToonDNA style 'plant_hat'
    Altis_present_band = 100204  # was ToonDNA style 'present_band'
    Altis_pride_hairbow_ace = 100205  # was ToonDNA style 'pride_hairbow_ace'
    Altis_pride_hairbow_aro = 100206  # was ToonDNA style 'pride_hairbow_aro'
    Altis_pride_hairbow_bi = 100207  # was ToonDNA style 'pride_hairbow_bi'
    Altis_pride_hairbow_gay = 100208  # was ToonDNA style 'pride_hairbow_gay'
    Altis_pride_hairbow_genderfluid = 100209  # was ToonDNA style 'pride_hairbow_genderfluid'
    Altis_pride_hairbow_lesbian = 100210  # was ToonDNA style 'pride_hairbow_lesbian'
    Altis_pride_hairbow_lgbt = 100211  # was ToonDNA style 'pride_hairbow_lgbt'
    Altis_pride_hairbow_nb = 100212  # was ToonDNA style 'pride_hairbow_nb'
    Altis_pride_hairbow_pan = 100213  # was ToonDNA style 'pride_hairbow_pan'
    Altis_pride_hairbow_trans = 100214  # was ToonDNA style 'pride_hairbow_trans'
    Altis_pumpkin_bucket = 100215  # was ToonDNA style 'pumpkin_bucket'
    Altis_ragdoll_hat = 100216  # was ToonDNA style 'ragdoll_hat'
    Altis_ragdoll_humble = 100217  # was ToonDNA style 'ragdoll_humble'
    Altis_ragdoll_regal = 100218  # was ToonDNA style 'ragdoll_regal'
    Altis_ragdoll_tradi = 100219  # was ToonDNA style 'ragdoll_tradi'
    Altis_rainbow_phones = 100220  # was ToonDNA style 'rainbow_phones'
    Altis_ribbon_blue = 100221  # was ToonDNA style 'ribbon_blue'
    Altis_ridinghood_hood = 100222  # was ToonDNA style 'ridinghood_hood'
    Altis_robophones = 100223  # was ToonDNA style 'robophones'
    Altis_rosecrown_blue = 100224  # was ToonDNA style 'rosecrown_blue'
    Altis_rosecrown_cyan = 100225  # was ToonDNA style 'rosecrown_cyan'
    Altis_rosecrown_green = 100226  # was ToonDNA style 'rosecrown_green'
    Altis_rosecrown_orange = 100227  # was ToonDNA style 'rosecrown_orange'
    Altis_rosecrown_pink = 100228  # was ToonDNA style 'rosecrown_pink'
    Altis_rosecrown_purple = 100229  # was ToonDNA style 'rosecrown_purple'
    Altis_rosecrown_red = 100230  # was ToonDNA style 'rosecrown_red'
    Altis_rosecrown_white = 100231  # was ToonDNA style 'rosecrown_white'
    Altis_rosecrown_yellow = 100232  # was ToonDNA style 'rosecrown_yellow'
    Altis_santa_rainbow = 100233  # was ToonDNA style 'santa_rainbow'
    Altis_santa_red = 100234  # was ToonDNA style 'santa_red'
    Altis_scarecrow_hat = 100235  # was ToonDNA style 'scarecrow_hat'
    Altis_seven_fedora = 100236  # was ToonDNA style 'seven_fedora'
    Altis_ski_helmet = 100237  # was ToonDNA style 'ski_helmet'
    Altis_ski_helmet_blue = 100238  # was ToonDNA style 'ski_helmet_blue'
    Altis_ski_helmet_gray = 100239  # was ToonDNA style 'ski_helmet_gray'
    Altis_ski_helmet_green = 100240  # was ToonDNA style 'ski_helmet_green'
    Altis_ski_helmet_pink = 100241  # was ToonDNA style 'ski_helmet_pink'
    Altis_ski_helmet_rainbow = 100242  # was ToonDNA style 'ski_helmet_rainbow'
    Altis_ski_helmet_red = 100243  # was ToonDNA style 'ski_helmet_red'
    Altis_snowman_hat = 100244  # was ToonDNA style 'snowman_hat'
    Altis_soldier_hat = 100245  # was ToonDNA style 'soldier_hat'
    Altis_space_helm = 100246  # was ToonDNA style 'space_helm'
    Altis_spin_doctor_band = 100247  # was ToonDNA style 'spin_doctor_band'
    Altis_star_hat = 100248  # was ToonDNA style 'star_hat'
    Altis_stpats_band = 100249  # was ToonDNA style 'stpats_band'
    Altis_stpats_clip = 100250  # was ToonDNA style 'stpats_clip'
    Altis_stpats_top_lucky = 100251  # was ToonDNA style 'stpats_top_lucky'
    Altis_stpats_top_tart = 100252  # was ToonDNA style 'stpats_top_tart'
    Altis_tin_humble = 100253  # was ToonDNA style 'tin_humble'
    Altis_tin_regal = 100254  # was ToonDNA style 'tin_regal'
    Altis_tin_tradi = 100255  # was ToonDNA style 'tin_tradi'
    Altis_tiw_bow = 100256  # was ToonDNA style 'tiw_bow'
    Altis_tv_hat = 100257  # was ToonDNA style 'tv_hat'
    Altis_umbrella = 100258  # was ToonDNA style 'umbrella'
    Altis_webster_bookhat = 100259  # was ToonDNA style 'webster_bookhat'
    Altis_wizard_black = 100260  # was ToonDNA style 'wizard_black'
    Altis_wizard_blue = 100261  # was ToonDNA style 'wizard_blue'
    Altis_wizard_green = 100262  # was ToonDNA style 'wizard_green'
    Altis_wizard_pink = 100263  # was ToonDNA style 'wizard_pink'
    Altis_wizard_red = 100264  # was ToonDNA style 'wizard_red'
    Altis_wizard_traffic_orange = 100265  # was ToonDNA style 'wizard_traffic_orange'


@defineItemSubtypeEnum(ItemType.Cosmetic_Glasses)
class GlassesItemType(IntEnum):
    """
    Item subtype enum for Glasses.
    """

    ## Eyepatches ##
    Glasses_Eyepatch_Classic_Skull = 24          # old: [20, 0, 0], glasses
    Glasses_Eyepatch_Classic_Gem = 25            # old: [20, 4, 0], glasses
    Glasses_Eyepatch_Classic_Desat = 26          # old: [20, 5, 0], glasses
    
    ## Goggles ##
    Glasses_Goggles_Classic = 9  # old: [11, 0, 0], glasses
    Glasses_Goggles_Flight = 39          # old: [34, 0, 0], glasses
    Glasses_Goggles_Spy = 95      # old: [59, 0, 0], glasses

    ## Snow Goggles ##
    Glasses_Goggles_SnowBlue = 29        # old: [24, 0, 0], glasses
    Glasses_Goggles_SnowGreen = 30       # old: [25, 0, 0], glasses
    Glasses_Goggles_SnowGrey = 31        # old: [26, 0, 0], glasses
    Glasses_Goggles_SnowPink = 32        # old: [27, 0, 0], glasses
    Glasses_Goggles_SnowRainbow = 33     # old: [28, 0, 0], glasses
    Glasses_Goggles_SnowRed = 34         # old: [29, 0, 0], glasses
    Glasses_Goggles_SnowVintage = 35     # old: [30, 0, 0], glasses

    ## Hypno Glasses ##
    Glasses_Hypno_LightBlue = 61         # old: [23, 24, 0], glasses
    Glasses_Hypno_Blue = 60              # old: [23, 23, 0], glasses
    Glasses_Hypno_Orange = 62            # old: [23, 25, 0], glasses
    Glasses_Hypno_Zany = 28                  # old: [23, 0, 0], glasses
    Glasses_Hypno_Green = 41              # old: [23, 6, 0], glasses
    Glasses_Hypno_Red = 57           # old: [23, 20, 0], glasses
    Glasses_Hypno_Pink = 63  # old: [23, 26, 0], glasses
    Glasses_Hypno_Yellow = 64  # old: [23, 27, 0], glasses
    Glasses_Hypno_Purple = 65  # old: [23, 28, 0], glasses
    Glasses_Hypno_DarkPurple = 66  # old: [23, 29, 0], glasses
    Glasses_Hypno_Rainbow = 67  # old: [23, 30, 0], glasses

    ## X Glasses ##
    Glasses_X_Black = 42              # old: [36, 7, 0], glasses
    Glasses_X_Gold = 43             # old: [36, 8, 0], glasses
    Glasses_X_Green = 44             # old: [36, 9, 0], glasses
    Glasses_X_Rainbow = 45             # old: [36, 10, 0], glasses
    Glasses_X_Red = 46            # old: [36, 11, 0], glasses

    ## Gift Glasses ##
    Glasses_Gift_ActualBlue = 47            # old: [37, 0, 0], glasses
    Glasses_Gift_Blue = 48        # old: [37, 12, 0], glasses
    Glasses_Gift_Cyan = 49        # old: [37, 13, 0], glasses
    Glasses_Gift_Green = 50       # old: [37, 14, 0], glasses
    Glasses_Gift_Orange = 51      # old: [37, 15, 0], glasses
    Glasses_Gift_Pink = 52        # old: [37, 16, 0], glasses
    Glasses_Gift_Purple = 53      # old: [37, 17, 0], glasses
    Glasses_Gift_Red = 54         # old: [37, 18, 0], glasses
    Glasses_Gift_Yellow = 55      # old: [37, 19, 0], glasses

    ## NYE Glasses ##
    Glasses_NYE_2019 = 36            # old: [31, 0, 0], glasses
    Glasses_NYE_2020 = 56            # old: [38, 0, 0], glasses
    Glasses_NYE_2022 = 81            # old: [44, 0, 0], glasses

    ## Ornament Glasses ##
    Glasses_Ornament_Black = 68        # old: [41, 31, 0], glasses
    Glasses_Ornament_Blue = 69         # old: [41, 32, 0], glasses
    Glasses_Ornament_Cyan = 70         # old: [41, 33, 0], glasses
    Glasses_Ornament_Green = 71        # old: [41, 34, 0], glasses
    Glasses_Ornament_Orange = 72       # old: [41, 35, 0], glasses
    Glasses_Ornament_Pink = 73         # old: [41, 36, 0], glasses
    Glasses_Ornament_Purple = 74       # old: [41, 37, 0], glasses
    Glasses_Ornament_Rainbow = 75      # old: [41, 38, 0], glasses
    Glasses_Ornament_Red = 76          # old: [41, 39, 0], glasses
    Glasses_Ornament_White = 77        # old: [41, 40, 0], glasses
    Glasses_Ornament_Yellow = 78       # old: [41, 41, 0], glasses
    
    ## NPC ##
    Glasses_Brovinci = 83        # old: [46, 0, 0], glasses
    
    ## Suit ##
    Glasses_Mouthpiece = 84      # old: [47, 0, 0], glasses
    Glasses_Chairman = 59           # old: [40, 22, 0], glasses
    Glasses_Pacesetter = 87      # old: [50, 0, 0], glasses
    Glasses_LowBaller = 92       # old: [56, 0, 0], glasses
    Glasses_Flunky = 37          # old: [32, 0, 0], glasses

    ## Uncategorized ##
    Glasses_Round_Classic = 1  # old: [1, 0, 0], glasses
    Glasses_Miniblinds_Classic_White = 2  # old: [2, 0, 0], glasses
    Glasses_Shades_Hollywood_Classic = 3  # old: [3, 0, 0], glasses
    Glasses_Star_Classic = 4  # old: [4, 0, 0], glasses
    Glasses_Movie_Classic = 5  # old: [5, 0, 0], glasses
    Glasses_Aviator_Classic = 6  # old: [6, 0, 0], glasses
    Glasses_Shades_Celebrity_Classic = 7  # old: [9, 0, 0], glasses
    Glasses_Groucho_Classic = 10  # old: [12, 0, 0], glasses
    Glasses_Heart_Classic = 11  # old: [13, 0, 0], glasses
    Glasses_Bugeye_Classic = 12  # old: [14, 0, 0], glasses
    Glasses_Monocle_Classic = 18  # old: [17, 0, 0], glasses
    Glasses_Smooch_Classic = 19  # old: [18, 0, 0], glasses
    Glasses_SquareFrames_Classic = 20  # old: [19, 0, 0], glasses
    Glasses_Cateye_Classic = 21  # old: [7, 0, 0], glasses
    Glasses_Nerd_Classic = 22  # old: [8, 0, 0], glasses
    Glasses_Alien_Classic = 23  # old: [21, 0, 0], glasses
    Glasses_EyeSprings = 38              # old: [33, 0, 0], glasses
    Glasses_Outback_Sunny = 40    # old: [35, 0, 0], glasses
    Glasses_Funky = 85           # old: [48, 0, 0], glasses
    Glasses_Card_Black = 88       # old: [51, 0, 0], glasses
    Glasses_Card_Red = 89         # old: [52, 0, 0], glasses
    Glasses_Cookie = 91          # old: [55, 0, 0], glasses
    Glasses_Visor_Cybertoon = 93       # old: [57, 0, 0], glasses
    Glasses_Visor_SciFi = 82             # old: [45, 0, 0], glasses

    ### Masks ###
    Mask_Spider = 27          # old: [22, 0, 0], glasses
    Mask_Pirate_Ghost = 94      # old: [58, 0, 0], glasses
    Mask_Sleepwalker = 86        # old: [49, 0, 0], glasses
    Mask_HWTown = 79             # old: [42, 0, 0], glasses
    Mask_Count = 80              # old: [43, 0, 0], glasses
    Mask_Identity_Classic_Black = 13            # old: [15, 0, 0], glasses
    Mask_Identity_Classic_Blue = 14             # old: [15, 1, 0], glasses
    Mask_Carnivale_Classic_Blue = 15      # old: [16, 0, 0], glasses
    Mask_Carnivale_Classic_Purple = 16    # old: [16, 2, 0], glasses
    Mask_Carnivale_Classic_Aqua = 17      # old: [16, 3, 0], glasses
    Mask_Scuba_Classic = 8               # old: [10, 0, 0], glasses
    
    ### Mustache ###
    Mustache_Vinny = 58            # old: [39, 21, 0], glasses

    ### Altis legacy glasses styles (auto-ported from ToonDNA.GlassesStyles) ###
    Altis_2019_glasses = 100000  # was ToonDNA style '2019_glasses'
    Altis_2020_glasses = 100001  # was ToonDNA style '2020_glasses'
    Altis_2022_glasses = 100002  # was ToonDNA style '2022_glasses'
    Altis_brovinci_glasses = 100003  # was ToonDNA style 'brovinci_glasses'
    Altis_chair_glasses = 100004  # was ToonDNA style 'chair_glasses'
    Altis_cookie_glasses = 100005  # was ToonDNA style 'cookie_glasses'
    Altis_count_mask = 100006  # was ToonDNA style 'count_mask'
    Altis_ddl_sleepingmask = 100007  # was ToonDNA style 'ddl_sleepingmask'
    Altis_eye_spring = 100008  # was ToonDNA style 'eye_spring'
    Altis_flight_goggles = 100009  # was ToonDNA style 'flight_goggles'
    Altis_flunky_glasses = 100010  # was ToonDNA style 'flunky_glasses'
    Altis_g3d1 = 100011  # was ToonDNA style 'g3d1'
    Altis_gag1 = 100012  # was ToonDNA style 'gag1'
    Altis_gav1 = 100013  # was ToonDNA style 'gav1'
    Altis_gce1 = 100014  # was ToonDNA style 'gce1'
    Altis_gdk1 = 100015  # was ToonDNA style 'gdk1'
    Altis_ggl1 = 100016  # was ToonDNA style 'ggl1'
    Altis_ggm1 = 100017  # was ToonDNA style 'ggm1'
    Altis_ghg1 = 100018  # was ToonDNA style 'ghg1'
    Altis_ghw1 = 100019  # was ToonDNA style 'ghw1'
    Altis_ghw2 = 100020  # was ToonDNA style 'ghw2'
    Altis_ghw3 = 100021  # was ToonDNA style 'ghw3'
    Altis_gie1 = 100022  # was ToonDNA style 'gie1'
    Altis_gift_glasses = 100023  # was ToonDNA style 'gift_glasses'
    Altis_gift_glasses_blue = 100024  # was ToonDNA style 'gift_glasses_blue'
    Altis_gift_glasses_cyan = 100025  # was ToonDNA style 'gift_glasses_cyan'
    Altis_gift_glasses_green = 100026  # was ToonDNA style 'gift_glasses_green'
    Altis_gift_glasses_orange = 100027  # was ToonDNA style 'gift_glasses_orange'
    Altis_gift_glasses_pink = 100028  # was ToonDNA style 'gift_glasses_pink'
    Altis_gift_glasses_purple = 100029  # was ToonDNA style 'gift_glasses_purple'
    Altis_gift_glasses_red = 100030  # was ToonDNA style 'gift_glasses_red'
    Altis_gift_glasses_yellow = 100031  # was ToonDNA style 'gift_glasses_yellow'
    Altis_gjo1 = 100032  # was ToonDNA style 'gjo1'
    Altis_glasses_cardBlack = 100033  # was ToonDNA style 'glasses_cardBlack'
    Altis_glasses_cardRed = 100034  # was ToonDNA style 'glasses_cardRed'
    Altis_glasses_cyberpunk = 100035  # was ToonDNA style 'glasses_cyberpunk'
    Altis_glasses_funky = 100036  # was ToonDNA style 'glasses_funky'
    Altis_glasses_goggles_spy = 100037  # was ToonDNA style 'glasses_goggles_spy'
    Altis_glasses_low_baller = 100038  # was ToonDNA style 'glasses_low_baller'
    Altis_glasses_mouthpiece = 100039  # was ToonDNA style 'glasses_mouthpiece'
    Altis_glasses_pacesetter = 100040  # was ToonDNA style 'glasses_pacesetter'
    Altis_glasses_pirate_mask = 100041  # was ToonDNA style 'glasses_pirate_mask'
    Altis_gmb1 = 100042  # was ToonDNA style 'gmb1'
    Altis_gmn1 = 100043  # was ToonDNA style 'gmn1'
    Altis_gmo1 = 100044  # was ToonDNA style 'gmo1'
    Altis_gmt1 = 100045  # was ToonDNA style 'gmt1'
    Altis_gmt2 = 100046  # was ToonDNA style 'gmt2'
    Altis_gmt3 = 100047  # was ToonDNA style 'gmt3'
    Altis_gmt4 = 100048  # was ToonDNA style 'gmt4'
    Altis_gmt5 = 100049  # was ToonDNA style 'gmt5'
    Altis_gnr1 = 100050  # was ToonDNA style 'gnr1'
    Altis_grd1 = 100051  # was ToonDNA style 'grd1'
    Altis_gsb1 = 100052  # was ToonDNA style 'gsb1'
    Altis_gsr1 = 100053  # was ToonDNA style 'gsr1'
    Altis_gst1 = 100054  # was ToonDNA style 'gst1'
    Altis_hwtown_mask = 100055  # was ToonDNA style 'hwtown_mask'
    Altis_hypno = 100056  # was ToonDNA style 'hypno'
    Altis_hypno_2019 = 100057  # was ToonDNA style 'hypno_2019'
    Altis_hypno_blue = 100058  # was ToonDNA style 'hypno_blue'
    Altis_hypno_darkpurple = 100059  # was ToonDNA style 'hypno_darkpurple'
    Altis_hypno_lightblue = 100060  # was ToonDNA style 'hypno_lightblue'
    Altis_hypno_orange = 100061  # was ToonDNA style 'hypno_orange'
    Altis_hypno_pink = 100062  # was ToonDNA style 'hypno_pink'
    Altis_hypno_purple = 100063  # was ToonDNA style 'hypno_purple'
    Altis_hypno_rainbow = 100064  # was ToonDNA style 'hypno_rainbow'
    Altis_hypno_yellow = 100065  # was ToonDNA style 'hypno_yellow'
    Altis_muzzle_rose = 100066  # was ToonDNA style 'muzzle_rose'
    Altis_orn_glasses_black = 100067  # was ToonDNA style 'orn_glasses_black'
    Altis_orn_glasses_blue = 100068  # was ToonDNA style 'orn_glasses_blue'
    Altis_orn_glasses_cyan = 100069  # was ToonDNA style 'orn_glasses_cyan'
    Altis_orn_glasses_green = 100070  # was ToonDNA style 'orn_glasses_green'
    Altis_orn_glasses_orange = 100071  # was ToonDNA style 'orn_glasses_orange'
    Altis_orn_glasses_pink = 100072  # was ToonDNA style 'orn_glasses_pink'
    Altis_orn_glasses_purple = 100073  # was ToonDNA style 'orn_glasses_purple'
    Altis_orn_glasses_rainbow = 100074  # was ToonDNA style 'orn_glasses_rainbow'
    Altis_orn_glasses_red = 100075  # was ToonDNA style 'orn_glasses_red'
    Altis_orn_glasses_white = 100076  # was ToonDNA style 'orn_glasses_white'
    Altis_orn_glasses_yellow = 100077  # was ToonDNA style 'orn_glasses_yellow'
    Altis_outback_sunnyglasses = 100078  # was ToonDNA style 'outback_sunnyglasses'
    Altis_painter_brush = 100079  # was ToonDNA style 'painter_brush'
    Altis_scifi_visor = 100080  # was ToonDNA style 'scifi_visor'
    Altis_seven_glasses = 100081  # was ToonDNA style 'seven_glasses'
    Altis_snow_goggles_blue = 100082  # was ToonDNA style 'snow_goggles_blue'
    Altis_snow_goggles_green = 100083  # was ToonDNA style 'snow_goggles_green'
    Altis_snow_goggles_grey = 100084  # was ToonDNA style 'snow_goggles_grey'
    Altis_snow_goggles_pink = 100085  # was ToonDNA style 'snow_goggles_pink'
    Altis_snow_goggles_rainbow = 100086  # was ToonDNA style 'snow_goggles_rainbow'
    Altis_snow_goggles_red = 100087  # was ToonDNA style 'snow_goggles_red'
    Altis_snow_goggles_vintage = 100088  # was ToonDNA style 'snow_goggles_vintage'
    Altis_spider_glasses = 100089  # was ToonDNA style 'spider_glasses'
    Altis_vinny_stache = 100090  # was ToonDNA style 'vinny_stache'
    Altis_x_glasses_b = 100091  # was ToonDNA style 'x_glasses_b'
    Altis_x_glasses_go = 100092  # was ToonDNA style 'x_glasses_go'
    Altis_x_glasses_gr = 100093  # was ToonDNA style 'x_glasses_gr'
    Altis_x_glasses_ra = 100094  # was ToonDNA style 'x_glasses_ra'
    Altis_x_glasses_red = 100095  # was ToonDNA style 'x_glasses_red'


@defineItemSubtypeEnum(ItemType.Cosmetic_Backpack)
class BackpackItemType(IntEnum):
    """
    Item subtype enum for Backpacks.
    """
    BlueBackpack = 1                    # old: [1, 0, 0], backpack
    OrangeBackpack = 2                  # old: [1, 1, 0], backpack
    PurpleBackpack = 3                  # old: [1, 2, 0], backpack
    RedDotBackpack = 4                  # old: [1, 3, 0], backpack
    YellowDotBackpack = 5               # old: [1, 4, 0], backpack
    Backpack_ScubaTank_Classic = 9                       # old: [5, 0, 0], backpack
    Backpack_SharkFin_Classic = 10                       # old: [6, 0, 0], backpack

    Backpack_Toys_Classic = 13                    # old: [8, 0, 0], backpack
    
    ## Wings ##
    Backpack_Wings_Angel_Classic_White = 11              # old: [7, 0, 0], backpack
    Backpack_Wings_Angel_Classic_Rainbow = 12       # old: [7, 5, 0], backpack
    Backpack_Wings_Angel_Divine_White = 57                     # old: [55, 0, 0], backpack
    Backpack_Wings_Angel_Divine_Blue = 58                 # old: [55, 7, 0], backpack
    Backpack_Wings_Angel_Divine_Green = 59                # old: [55, 8, 0], backpack
    Backpack_Wings_Angel_Divine_Orange = 60               # old: [55, 9, 0], backpack
    Backpack_Wings_Angel_Divine_Purple = 61               # old: [55, 10, 0], backpack
    Backpack_Wings_Angel_Divine_Red = 62                  # old: [55, 11, 0], backpack
    Backpack_Wings_Angel_Divine_Yellow = 70               # old: [55, 14, 0], backpack
    
    Backpack_Wings_Butterfly_Classic = 14                 # old: [9, 0, 0], backpack
    Backpack_Wings_Pixie_Classic = 15                     # old: [9, 6, 0], backpack
    Backpack_Wings_Dragon_Classic = 16                    # old: [10, 0, 0], backpack
    Backpack_Wings_Bird_Classic = 20                      # old: [14, 0, 0], backpack
    Backpack_Wings_Dragonfly_Classic = 8                  # old: [4, 0, 0], backpack
    Backpack_Wings_Bee_Classic = 7                        # old: [3, 0, 0], backpack
    Backpack_Wings_Bat_Classic = 6                        # old: [2, 0, 0], backpack
    Backpack_Wings_Airplane_Classic = 23                     # old: [17, 0, 0], backpack
    Backpack_Wings_HangGlider = 50                     # old: [46, 0, 0], backpack
    Backpack_Wings_WingSuit = 113         # old: [99, 0, 0], backpack

    Backpack_JetPack_Classic = 17                        # old: [11, 0, 0], backpack
    Backpack_Bug_Classic = 18                    # old: [12, 0, 0], backpack
   
    PirateSword = 24                    # old: [18, 0, 0], backpack
    Backpack_Cape_Classic_Red = 25                  # old: [19, 0, 0], backpack
    Backpack_Cape_Classic_Black = 26                    # old: [20, 0, 0], backpack
    Backpack_Tail_Toonosaur_Classic = 27                  # old: [21, 0, 0], backpack
    Backpack_Jamboree = 28                   # old: [22, 0, 0], backpack
    GagAttackPack = 29                  # old: [23, 0, 0], backpack
    SpaceBack = 31                      # old: [25, 0, 0], backpack
    Backpack_WitchBroom = 32                     # old: [26, 0, 0], backpack
    Backpack_Cape_Reaper = 33                     # old: [27, 0, 0], backpack
    Backpack_Cape_Dracula = 34                    # old: [28, 0, 0], backpack
    TrickortreatBack = 35               # old: [29, 0, 0], backpack
    PotionBack = 36                     # old: [30, 0, 0], backpack
    
    TinTradi = 37                       # old: [31, 0, 0], backpack
    TinHumble = 38                      # old: [32, 0, 0], backpack
    TinRegal = 39                       # old: [33, 0, 0], backpack
    SoldierHomemadeKey = 78            # old: [31, 38, 0], backpack

    Backpack_Bow_Ragdoll_White = 40                  # old: [34, 0, 0], backpack
    Backpack_Bow_Ragdoll_Red = 41                   # old: [35, 0, 0], backpack
    Backpack_Bow_Ragdoll_Yellow = 42                   # old: [36, 0, 0], backpack
    Backpack_Bow_Ragdoll_Orange = 77            # old: [34, 37, 0], backpack

    PresentsSack = 43                   # old: [37, 0, 0], backpack
    Snowboard = 44                      # old: [38, 0, 0], backpack
    CandyCane = 45                      # old: [39, 0, 0], backpack
    CupidBow = 46                       # old: [41, 0, 0], backpack
    CupidBowQuiver = 47                 # old: [42, 0, 0], backpack
    PropPack = 48                       # old: [44, 0, 0], backpack
    Kite = 49                           # old: [45, 0, 0], backpack
    Telescope = 51                      # old: [48, 0, 0], backpack
    OutbackBackpack = 52                # old: [50, 0, 0], backpack
    OutbackBoomerang = 54               # old: [52, 0, 0], backpack
    OutbackDidgeridoo = 55              # old: [53, 0, 0], backpack
    Backpack_Alien = 56                  # old: [54, 0, 0], backpack

    DemonWings = 63                     # old: [56, 0, 0], backpack
    DemonWingsBlue = 64                 # old: [56, 7, 0], backpack
    DemonWingsGreen = 65                # old: [56, 8, 0], backpack
    DemonWingsOrange = 66               # old: [56, 9, 0], backpack
    DemonWingsPurple = 67               # old: [56, 10, 0], backpack
    DemonWingsRed = 68                  # old: [56, 11, 0], backpack
    DemonWingsYellow = 71               # old: [56, 14, 0], backpack

    RidinghoodCloak = 69                # old: [57, 0, 0], backpack
    Backpack_Backstabber = 72                       # old: [62, 34, 0], backpack
    Backpack_Gavel = 73                      # old: [63, 33, 0], backpack
    Backpack_Lawbook = 74                        # old: [64, 35, 0], backpack
    StonePack = 75                     # old: [65, 36, 0], backpack
    
    ## Gags ##
    Backpack_Gag_TNT = 76                       # old: [66, 0, 0], backpack
    Backpack_Gag_Seltzer = 79                   # old: [68, 0, 0], backpack
    Backpack_Gag_Magnet_Red = 80                       # old: [70, 40, 0], backpack
    Backpack_Gag_JoyBuzzer = 81                         # old: [71, 0, 0], backpack
    
    FusionPack = 82                    # old: [72, 0, 0], backpack
    Spatula = 85                       # old: [77, 44, 0], backpack
    Firework = 86                      # old: [78, 45, 0], backpack
    Spellbook = 87                     # old: [64, 46, 0], backpack
    Tombstone = 88                     # old: [65, 47, 0], backpack
    CandyPumpkin = 89                  # old: [79, 0, 0], backpack
    PlatePack = 90                     # old: [80, 0, 0], backpack
    Extinguisher = 91                  # old: [81, 0, 0], backpack
    PresentCorn = 92                   # old: [82, 0, 0], backpack
    FutureWing = 93                    # old: [83, 0, 0], backpack
    FutureCloak = 94                   # old: [84, 0, 0], backpack
    FutureWingCloak = 95               # old: [85, 0, 0], backpack
    Backpack_Cape_HwTown = 96                    # old: [87, 0, 0], backpack
    
    Backpack_Plushie_Flunky_Classic = 30                        # old: [24, 0, 0], backpack
    Backpack_Plushie_Chairman = 83                     # old: [74, 41, 0], backpack
    Backpack_Plushie_Sads = 97                      # old: [88, 0, 0], backpack
    
    Backpack_Newstoon_Suitcase = 98              # old: [91, 0, 0], backpack
    Backpack_Newstoon_Camera = 99                # old: [92, 0, 0], backpack
    
    Backpack_Cape_Pride_Lgbt = 100                 # old: [94, 0, 0], backpack
    Backpack_Cape_Pride_Trans = 101                # old: [94, 62, 0], backpack
    Backpack_Cape_Pride_Lesbian = 102              # old: [94, 63, 0], backpack
    Backpack_Cape_Pride_Pan = 103                  # old: [94, 64, 0], backpack
    Backpack_Cape_Pride_Bi = 104                   # old: [94, 65, 0], backpack
    Backpack_Cape_Pride_Nb = 105                   # old: [94, 66, 0], backpack
    Backpack_Cape_Pride_Ace = 106                  # old: [94, 67, 0], backpack
    Backpack_Cape_Pride_Fluid = 107                # old: [94, 68, 0], backpack
    Backpack_Cape_Pride_Aro = 108                  # old: [94, 69, 0], backpack
    Backpack_Cape_Pride_Gay = 109                     # old: [94, 87, 0], backpack
    
    Backpack_Stuffed_Doodle = 110                    # old: [95, 0, 0], backpack
    Backpack_Stuffed_Bear_Classic = 19  # old: [13, 0, 0], backpack
    Backpack_Stuffed_Cat_Classic = 21  # old: [15, 0, 0], backpack
    Backpack_Stuffed_Dog_Classic = 22  # old: [16, 0, 0], backpack
    Backpack_Stuffed_Bunny = 84                 # old: [76, 0, 0], backpack

    Backpack_MoneyBag = 111              # old: [97, 0, 0], backpack
    Backpack_PitchFork = 112             # old: [98, 0, 0], backpack
    Backpack_Pillow = 115                # old: [100, 0, 0], backpack
    Backpack_Saxophone = 116           # old: [102, 0, 0], backpack
    Backpack_Firestoker = 117           # old: [103, 0, 0], backpack
    Backpack_Shield = 118            # old: [104, 0, 0], backpack
    Backpack_FruitBasket = 119           # old: [105, 0, 0], backpack
    Backpack_RetroBag = 120              # old: [106, 0, 0], backpack
    Backpack_BreadBag = 121                    # old: [107, 0, 0], backpack
    Backpack_Paddle = 122                      # old: [109, 0, 0], backpack
    PainterPalette = 123                # old: [110, 0, 0], backpack
    Backpack_Guitar_Pacesetter = 125                 # old: [111, 0, 0], backpack
    FactoryGear = 126                   # old: [112, 0, 0], backpack
    Backpack_Cybertoon = 127             # old: [113, 0, 0], backpack
    Backpack_Pirate_Ghost = 128           # old: [114, 0, 0], backpack

    ### Altis legacy backpack styles (auto-ported from ToonDNA.BackpackStyles) ###
    Altis_2019_scarf = 100000  # was ToonDNA style '2019_scarf'
    Altis_2020_scarf = 100001  # was ToonDNA style '2020_scarf'
    Altis_2021_scarf = 100002  # was ToonDNA style '2021_scarf'
    Altis_2022_scarf = 100003  # was ToonDNA style '2022_scarf'
    Altis_2023_scarf = 100004  # was ToonDNA style '2023_scarf'
    Altis_2024_scarf = 100005  # was ToonDNA style '2024_scarf'
    Altis_alien_backpack = 100006  # was ToonDNA style 'alien_backpack'
    Altis_angel_wings = 100007  # was ToonDNA style 'angel_wings'
    Altis_angel_wings_blue = 100008  # was ToonDNA style 'angel_wings_blue'
    Altis_angel_wings_green = 100009  # was ToonDNA style 'angel_wings_green'
    Altis_angel_wings_orange = 100010  # was ToonDNA style 'angel_wings_orange'
    Altis_angel_wings_purple = 100011  # was ToonDNA style 'angel_wings_purple'
    Altis_angel_wings_red = 100012  # was ToonDNA style 'angel_wings_red'
    Altis_angel_wings_yellow = 100013  # was ToonDNA style 'angel_wings_yellow'
    Altis_aviator_scarf = 100014  # was ToonDNA style 'aviator_scarf'
    Altis_backpack_bellringer = 100015  # was ToonDNA style 'backpack_bellringer'
    Altis_backpack_cyberpunk = 100016  # was ToonDNA style 'backpack_cyberpunk'
    Altis_backpack_factory_gear = 100017  # was ToonDNA style 'backpack_factory_gear'
    Altis_backpack_firestarter = 100018  # was ToonDNA style 'backpack_firestarter'
    Altis_backpack_fruitbasket = 100019  # was ToonDNA style 'backpack_fruitbasket'
    Altis_backpack_gatekeeper = 100020  # was ToonDNA style 'backpack_gatekeeper'
    Altis_backpack_majorplayer = 100021  # was ToonDNA style 'backpack_majorplayer'
    Altis_backpack_moneybag = 100022  # was ToonDNA style 'backpack_moneybag'
    Altis_backpack_pacesetter = 100023  # was ToonDNA style 'backpack_pacesetter'
    Altis_backpack_pillow = 100024  # was ToonDNA style 'backpack_pillow'
    Altis_backpack_pirate_ghost = 100025  # was ToonDNA style 'backpack_pirate_ghost'
    Altis_backpack_pitchfork = 100026  # was ToonDNA style 'backpack_pitchfork'
    Altis_backpack_retrobag = 100027  # was ToonDNA style 'backpack_retrobag'
    Altis_backpack_wingsuit_wings = 100028  # was ToonDNA style 'backpack_wingsuit_wings'
    Altis_bandana_engineer = 100029  # was ToonDNA style 'bandana_engineer'
    Altis_bap1 = 100030  # was ToonDNA style 'bap1'
    Altis_baw1 = 100031  # was ToonDNA style 'baw1'
    Altis_baw2 = 100032  # was ToonDNA style 'baw2'
    Altis_bfg1 = 100033  # was ToonDNA style 'bfg1'
    Altis_bfl1 = 100034  # was ToonDNA style 'bfl1'
    Altis_bfn1 = 100035  # was ToonDNA style 'bfn1'
    Altis_bhw1 = 100036  # was ToonDNA style 'bhw1'
    Altis_bhw2 = 100037  # was ToonDNA style 'bhw2'
    Altis_bhw3 = 100038  # was ToonDNA style 'bhw3'
    Altis_bhw4 = 100039  # was ToonDNA style 'bhw4'
    Altis_bjp1 = 100040  # was ToonDNA style 'bjp1'
    Altis_blg1 = 100041  # was ToonDNA style 'blg1'
    Altis_bloodsucker_lollipop = 100042  # was ToonDNA style 'bloodsucker_lollipop'
    Altis_bob1 = 100043  # was ToonDNA style 'bob1'
    Altis_bowtie_elf_jolly = 100044  # was ToonDNA style 'bowtie_elf_jolly'
    Altis_bpb2 = 100045  # was ToonDNA style 'bpb2'
    Altis_bpb3 = 100046  # was ToonDNA style 'bpb3'
    Altis_bpd1 = 100047  # was ToonDNA style 'bpd1'
    Altis_bpd2 = 100048  # was ToonDNA style 'bpd2'
    Altis_brovinci_necklace = 100049  # was ToonDNA style 'brovinci_necklace'
    Altis_bsa1 = 100050  # was ToonDNA style 'bsa1'
    Altis_bsa2 = 100051  # was ToonDNA style 'bsa2'
    Altis_bsa3 = 100052  # was ToonDNA style 'bsa3'
    Altis_bst1 = 100053  # was ToonDNA style 'bst1'
    Altis_bunny_backpack = 100054  # was ToonDNA style 'bunny_backpack'
    Altis_bwg1 = 100055  # was ToonDNA style 'bwg1'
    Altis_bwg2 = 100056  # was ToonDNA style 'bwg2'
    Altis_bwg3 = 100057  # was ToonDNA style 'bwg3'
    Altis_bwg4 = 100058  # was ToonDNA style 'bwg4'
    Altis_bwg5 = 100059  # was ToonDNA style 'bwg5'
    Altis_bwg6 = 100060  # was ToonDNA style 'bwg6'
    Altis_bwg7 = 100061  # was ToonDNA style 'bwg7'
    Altis_bwt1 = 100062  # was ToonDNA style 'bwt1'
    Altis_candy_cane = 100063  # was ToonDNA style 'candy_cane'
    Altis_candy_pumpkin = 100064  # was ToonDNA style 'candy_pumpkin'
    Altis_chair_pack = 100065  # was ToonDNA style 'chair_pack'
    Altis_cj_pack = 100066  # was ToonDNA style 'cj_pack'
    Altis_cj_tie = 100067  # was ToonDNA style 'cj_tie'
    Altis_clown_bowtie = 100068  # was ToonDNA style 'clown_bowtie'
    Altis_cupid_bow = 100069  # was ToonDNA style 'cupid_bow'
    Altis_cupid_bow_quiver = 100070  # was ToonDNA style 'cupid_bow_quiver'
    Altis_demon_wings = 100071  # was ToonDNA style 'demon_wings'
    Altis_demon_wings_blue = 100072  # was ToonDNA style 'demon_wings_blue'
    Altis_demon_wings_green = 100073  # was ToonDNA style 'demon_wings_green'
    Altis_demon_wings_orange = 100074  # was ToonDNA style 'demon_wings_orange'
    Altis_demon_wings_purple = 100075  # was ToonDNA style 'demon_wings_purple'
    Altis_demon_wings_red = 100076  # was ToonDNA style 'demon_wings_red'
    Altis_demon_wings_yellow = 100077  # was ToonDNA style 'demon_wings_yellow'
    Altis_doe_bandana = 100078  # was ToonDNA style 'doe_bandana'
    Altis_doodle_pack = 100079  # was ToonDNA style 'doodle_pack'
    Altis_dracula_cape = 100080  # was ToonDNA style 'dracula_cape'
    Altis_ee_breadbag = 100081  # was ToonDNA style 'ee_breadbag'
    Altis_ee_chefscarf = 100082  # was ToonDNA style 'ee_chefscarf'
    Altis_ee_paddle = 100083  # was ToonDNA style 'ee_paddle'
    Altis_extinguisher = 100084  # was ToonDNA style 'extinguisher'
    Altis_eye_bowtie = 100085  # was ToonDNA style 'eye_bowtie'
    Altis_firework = 100086  # was ToonDNA style 'firework'
    Altis_flower_tie = 100087  # was ToonDNA style 'flower_tie'
    Altis_fusion_pack = 100088  # was ToonDNA style 'fusion_pack'
    Altis_future_cloak = 100089  # was ToonDNA style 'future_cloak'
    Altis_future_wing = 100090  # was ToonDNA style 'future_wing'
    Altis_future_wing_cloak = 100091  # was ToonDNA style 'future_wing_cloak'
    Altis_gavel_pack = 100092  # was ToonDNA style 'gavel_pack'
    Altis_gb_bowtie_black = 100093  # was ToonDNA style 'gb_bowtie_black'
    Altis_gb_bowtie_blackwhite = 100094  # was ToonDNA style 'gb_bowtie_blackwhite'
    Altis_gb_bowtie_blue = 100095  # was ToonDNA style 'gb_bowtie_blue'
    Altis_gb_bowtie_gray = 100096  # was ToonDNA style 'gb_bowtie_gray'
    Altis_gb_bowtie_green = 100097  # was ToonDNA style 'gb_bowtie_green'
    Altis_gb_bowtie_orange = 100098  # was ToonDNA style 'gb_bowtie_orange'
    Altis_gb_bowtie_pink = 100099  # was ToonDNA style 'gb_bowtie_pink'
    Altis_gb_bowtie_pinkblack = 100100  # was ToonDNA style 'gb_bowtie_pinkblack'
    Altis_gb_bowtie_polkadot = 100101  # was ToonDNA style 'gb_bowtie_polkadot'
    Altis_gb_bowtie_purple = 100102  # was ToonDNA style 'gb_bowtie_purple'
    Altis_gb_bowtie_purpleorange = 100103  # was ToonDNA style 'gb_bowtie_purpleorange'
    Altis_gb_bowtie_red = 100104  # was ToonDNA style 'gb_bowtie_red'
    Altis_gb_bowtie_yellow = 100105  # was ToonDNA style 'gb_bowtie_yellow'
    Altis_gb_bowtie_yellowblack = 100106  # was ToonDNA style 'gb_bowtie_yellowblack'
    Altis_hangglider = 100107  # was ToonDNA style 'hangglider'
    Altis_hwtown_cape = 100108  # was ToonDNA style 'hwtown_cape'
    Altis_jester_collar = 100109  # was ToonDNA style 'jester_collar'
    Altis_kite = 100110  # was ToonDNA style 'kite'
    Altis_law_bowtie = 100111  # was ToonDNA style 'law_bowtie'
    Altis_mini_mag = 100112  # was ToonDNA style 'mini_mag'
    Altis_mystery_bowtie = 100113  # was ToonDNA style 'mystery_bowtie'
    Altis_newstoon_blue_bowtie = 100114  # was ToonDNA style 'newstoon_blue_bowtie'
    Altis_newstoon_camera = 100115  # was ToonDNA style 'newstoon_camera'
    Altis_newstoon_suitcase = 100116  # was ToonDNA style 'newstoon_suitcase'
    Altis_ottoman_tie = 100117  # was ToonDNA style 'ottoman_tie'
    Altis_outback_backpack = 100118  # was ToonDNA style 'outback_backpack'
    Altis_outback_bandana = 100119  # was ToonDNA style 'outback_bandana'
    Altis_outback_boomerang = 100120  # was ToonDNA style 'outback_boomerang'
    Altis_outback_didgeridoo = 100121  # was ToonDNA style 'outback_didgeridoo'
    Altis_painter_palette = 100122  # was ToonDNA style 'painter_palette'
    Altis_pinwheel_bowtie = 100123  # was ToonDNA style 'pinwheel_bowtie'
    Altis_plate_pack = 100124  # was ToonDNA style 'plate_pack'
    Altis_potion_back = 100125  # was ToonDNA style 'potion_back'
    Altis_present_corn = 100126  # was ToonDNA style 'present_corn'
    Altis_presents_sack = 100127  # was ToonDNA style 'presents_sack'
    Altis_pride_bowtie_ace = 100128  # was ToonDNA style 'pride_bowtie_ace'
    Altis_pride_bowtie_aro = 100129  # was ToonDNA style 'pride_bowtie_aro'
    Altis_pride_bowtie_bi = 100130  # was ToonDNA style 'pride_bowtie_bi'
    Altis_pride_bowtie_gay = 100131  # was ToonDNA style 'pride_bowtie_gay'
    Altis_pride_bowtie_genderfluid = 100132  # was ToonDNA style 'pride_bowtie_genderfluid'
    Altis_pride_bowtie_lesbian = 100133  # was ToonDNA style 'pride_bowtie_lesbian'
    Altis_pride_bowtie_lgbt = 100134  # was ToonDNA style 'pride_bowtie_lgbt'
    Altis_pride_bowtie_nb = 100135  # was ToonDNA style 'pride_bowtie_nb'
    Altis_pride_bowtie_pan = 100136  # was ToonDNA style 'pride_bowtie_pan'
    Altis_pride_bowtie_trans = 100137  # was ToonDNA style 'pride_bowtie_trans'
    Altis_pride_cape_ace = 100138  # was ToonDNA style 'pride_cape_ace'
    Altis_pride_cape_aro = 100139  # was ToonDNA style 'pride_cape_aro'
    Altis_pride_cape_bi = 100140  # was ToonDNA style 'pride_cape_bi'
    Altis_pride_cape_fluid = 100141  # was ToonDNA style 'pride_cape_fluid'
    Altis_pride_cape_gay = 100142  # was ToonDNA style 'pride_cape_gay'
    Altis_pride_cape_lesbian = 100143  # was ToonDNA style 'pride_cape_lesbian'
    Altis_pride_cape_lgbt = 100144  # was ToonDNA style 'pride_cape_lgbt'
    Altis_pride_cape_nb = 100145  # was ToonDNA style 'pride_cape_nb'
    Altis_pride_cape_pan = 100146  # was ToonDNA style 'pride_cape_pan'
    Altis_pride_cape_trans = 100147  # was ToonDNA style 'pride_cape_trans'
    Altis_prop_pack = 100148  # was ToonDNA style 'prop_pack'
    Altis_ragdoll_homemade_bow = 100149  # was ToonDNA style 'ragdoll_homemade_bow'
    Altis_ragdoll_humble = 100150  # was ToonDNA style 'ragdoll_humble'
    Altis_ragdoll_regal = 100151  # was ToonDNA style 'ragdoll_regal'
    Altis_ragdoll_tradi = 100152  # was ToonDNA style 'ragdoll_tradi'
    Altis_reaper_cape = 100153  # was ToonDNA style 'reaper_cape'
    Altis_retro_scarf = 100154  # was ToonDNA style 'retro_scarf'
    Altis_ribbon_bowtie = 100155  # was ToonDNA style 'ribbon_bowtie'
    Altis_ribbon_bowtie_black = 100156  # was ToonDNA style 'ribbon_bowtie_black'
    Altis_ribbon_bowtie_blueChecker = 100157  # was ToonDNA style 'ribbon_bowtie_blueChecker'
    Altis_ribbon_bowtie_candycorn = 100158  # was ToonDNA style 'ribbon_bowtie_candycorn'
    Altis_ribbon_bowtie_greenChecker = 100159  # was ToonDNA style 'ribbon_bowtie_greenChecker'
    Altis_ribbon_bowtie_pinkDots = 100160  # was ToonDNA style 'ribbon_bowtie_pinkDots'
    Altis_ribbon_bowtie_purple = 100161  # was ToonDNA style 'ribbon_bowtie_purple'
    Altis_ribbon_bowtie_rainbow = 100162  # was ToonDNA style 'ribbon_bowtie_rainbow'
    Altis_ribbon_bowtie_red = 100163  # was ToonDNA style 'ribbon_bowtie_red'
    Altis_ribbon_bowtie_redPolka = 100164  # was ToonDNA style 'ribbon_bowtie_redPolka'
    Altis_ribbon_bowtie_yellow = 100165  # was ToonDNA style 'ribbon_bowtie_yellow'
    Altis_ribbpn_bowtie_blue = 100166  # was ToonDNA style 'ribbpn_bowtie_blue'
    Altis_ridinghood_cloak = 100167  # was ToonDNA style 'ridinghood_cloak'
    Altis_sailor_bow_black = 100168  # was ToonDNA style 'sailor_bow_black'
    Altis_sailor_bow_blue = 100169  # was ToonDNA style 'sailor_bow_blue'
    Altis_sailor_bow_cyan = 100170  # was ToonDNA style 'sailor_bow_cyan'
    Altis_sailor_bow_green = 100171  # was ToonDNA style 'sailor_bow_green'
    Altis_sailor_bow_orange = 100172  # was ToonDNA style 'sailor_bow_orange'
    Altis_sailor_bow_pink = 100173  # was ToonDNA style 'sailor_bow_pink'
    Altis_sailor_bow_purple = 100174  # was ToonDNA style 'sailor_bow_purple'
    Altis_sailor_bow_red = 100175  # was ToonDNA style 'sailor_bow_red'
    Altis_sailor_bow_white = 100176  # was ToonDNA style 'sailor_bow_white'
    Altis_sailor_bow_yellow = 100177  # was ToonDNA style 'sailor_bow_yellow'
    Altis_sailor_collar_black = 100178  # was ToonDNA style 'sailor_collar_black'
    Altis_sailor_collar_blue = 100179  # was ToonDNA style 'sailor_collar_blue'
    Altis_sailor_collar_cyan = 100180  # was ToonDNA style 'sailor_collar_cyan'
    Altis_sailor_collar_green = 100181  # was ToonDNA style 'sailor_collar_green'
    Altis_sailor_collar_orange = 100182  # was ToonDNA style 'sailor_collar_orange'
    Altis_sailor_collar_pink = 100183  # was ToonDNA style 'sailor_collar_pink'
    Altis_sailor_collar_purple = 100184  # was ToonDNA style 'sailor_collar_purple'
    Altis_sailor_collar_red = 100185  # was ToonDNA style 'sailor_collar_red'
    Altis_sailor_collar_white = 100186  # was ToonDNA style 'sailor_collar_white'
    Altis_sailor_collar_yellow = 100187  # was ToonDNA style 'sailor_collar_yellow'
    Altis_seltzer_pack = 100188  # was ToonDNA style 'seltzer_pack'
    Altis_skelecog_pack = 100189  # was ToonDNA style 'skelecog_pack'
    Altis_snowboard = 100190  # was ToonDNA style 'snowboard'
    Altis_soldier_homemade_key = 100191  # was ToonDNA style 'soldier_homemade_key'
    Altis_space_back = 100192  # was ToonDNA style 'space_back'
    Altis_spatula = 100193  # was ToonDNA style 'spatula'
    Altis_spellbook = 100194  # was ToonDNA style 'spellbook'
    Altis_stab_pack = 100195  # was ToonDNA style 'stab_pack'
    Altis_stone_pack = 100196  # was ToonDNA style 'stone_pack'
    Altis_taser = 100197  # was ToonDNA style 'taser'
    Altis_telescope = 100198  # was ToonDNA style 'telescope'
    Altis_tin_humble = 100199  # was ToonDNA style 'tin_humble'
    Altis_tin_regal = 100200  # was ToonDNA style 'tin_regal'
    Altis_tin_tradi = 100201  # was ToonDNA style 'tin_tradi'
    Altis_tnt_pack = 100202  # was ToonDNA style 'tnt_pack'
    Altis_tombstone = 100203  # was ToonDNA style 'tombstone'
    Altis_trickortreat_back = 100204  # was ToonDNA style 'trickortreat_back'
    Altis_witch_broom = 100205  # was ToonDNA style 'witch_broom'


@defineItemSubtypeEnum(ItemType.Cosmetic_Shoes)
class ShoeItemType(IntEnum):
    """
    Item subtype enum for Shoes.
    """
    GreenAthleticShoes = 1	    # old: [1, 0, 0]
    RedAthleticShoes = 2	    # old: [1, 1, 0]
    GreenToonBoots = 3		    # old: [3, 2, 0]
    GreenSneakers = 4		    # old: [2, 3, 0]
    BoatShoes = 5			    # old: [1, 6, 0]
    YellowAthleticShoes = 6	    # old: [1, 7, 0]
    BlackSneakers = 7		    # old: [2, 8, 0]
    WhiteSneakers = 8		    # old: [2, 9, 0]
    PinkSneakers = 9		    # old: [2, 10, 0]
    CowboyBoots = 10		    # old: [3, 11, 0]
    GreenHiTops = 11		    # old: [2, 13, 0]
    RedSuperToonBoots = 12	    # old: [3, 16, 0]
    GreenTennisShoes = 13	    # old: [1, 17, 0]
    PinkTennisShoes = 14	    # old: [1, 18, 0]
    RedSneakers = 15		    # old: [2, 19, 0]
    AquaToonBoots = 16		    # old: [3, 20, 0]
    BrownToonBoots = 17		    # old: [3, 21, 0]
    YellowToonBoots = 18	    # old: [3, 22, 0]
    Loafers = 19			    # old: [1, 28, 0]
    MotorcycleBoots = 20		# old: [3, 30, 0]
    Oxfords = 21			    # old: [1, 31, 0]
    PinkRainBoots = 22		    # old: [3, 32, 0]
    JollyBoots = 23			    # old: [3, 33, 0]
    BeigeWinterBoots = 24	    # old: [3, 34, 0]
    PinkWinterBoots = 25	    # old: [3, 35, 0]
    WorkBoots = 26			    # old: [2, 36, 0]
    YellowSneakers = 27		    # old: [2, 37, 0]
    PinkToonBoots = 28		    # old: [3, 38, 0]
    PinkHiTops = 29			    # old: [2, 39, 0]
    RedDotsRainBoots = 30	    # old: [3, 40, 0]
    PurpleTennisShoes = 31	    # old: [1, 41, 0]
    VioletTennisShoes = 32	    # old: [1, 42, 0]
    YellowTennisShoes = 33	    # old: [1, 43, 0]
    BlueRainBoots = 34		    # old: [3, 44, 0]
    YellowRainBoots = 35	    # old: [3, 45, 0]
    BlackAthleticShoes = 36	    # old: [1, 46, 0]
    PirateShoes = 37		    # old: [3, 47, 0]
    ToonosaurFeet = 38		    # old: [3, 48, 0]
    Wingtips = 39			    # old: [1, 4, 0]
    BlackFancyShoes = 40	    # old: [2, 5, 0]
    PurpleBoots = 41		    # old: [3, 12, 0]
    BrownFancyShoes = 42	    # old: [2, 14, 0]
    RedFancyShoes = 43		    # old: [2, 15, 0]
    BlueSquareBoots = 44	    # old: [3, 23, 0]
    GreenHeartsBoots = 45	    # old: [3, 24, 0]
    GreyDotsBoots = 46		    # old: [3, 25, 0]
    OrangeStarsBoots = 47	    # old: [3, 26, 0]
    PinkStarsBoots = 48		    # old: [3, 27, 0]
    PurpleFancyShoes = 49	    # old: [2, 29, 0]
    SpaceBoots = 50			    # old: [2, 49, 0]
    WitchShoes = 51			    # old: [3, 50, 0]
    SkeletonShoes = 52		    # old: [2, 51, 0]
    AlchemistShoes = 53		    # old: [3, 52, 0]
    HumbleRagdoll = 54		    # old: [3, 53, 0]
    RegalRagdoll = 55		    # old: [3, 54, 0]
    TraditionalRagdoll = 56	    # old: [3, 55, 0]
    HumbleTin = 57			    # old: [3, 56, 0]
    RegalTin = 58			    # old: [3, 57, 0]
    TraditionalTin = 59		    # old: [3, 58, 0]
    VintageSnow = 60		    # old: [3, 59, 0]
    AviatorBoots = 61		    # old: [3, 60, 0]
    WingsuitBoots = 62		    # old: [3, 61, 0]
    OutbackShoes = 63		    # old: [2, 62, 0]
    PumpkinShoes = 64		    # old: [2, 63, 0]
    LazyBonesSlippers = 65	    # old: [1, 64, 0]
    HomemadeRagdoll = 66	    # old: [3, 65, 0]
    HomemadeTin = 67		    # old: [3, 66, 0]
    RetroWinterSuit = 68	    # old: [2, 67, 0]
    RetroWinterDress = 69	    # old: [2, 68, 0]
    BreaktheLawShoes = 70	    # old: [2, 69, 0]
    TripleRainbowShoes = 71	    # old: [2, 70, 0]
    ChairmanShoes = 72		    # old: [1, 71, 0]
    PhantoonShoes = 73		    # old: [2, 72, 0]
    TumblesShoes = 74		    # old: [2, 73, 0]
    HallowopolisBoots = 75	    # old: [3, 74, 0]
    DiverBoots = 76			    # old: [3, 75, 0]
    TrolleyEngineerBoots = 77   # old: [2, 76, 0]
    FruitPieShoes = 78		    # old: [2, 77, 0]
    CardSuitShoesRed = 79	    # old: [3, 78, 0]
    CardSuitShoesBlack = 80	    # old: [3, 79, 0]
    GatorSlippers = 81		    # old: [3, 80, 0]
    PaintersMocasins = 82	    # old: [2, 81, 0]
    ArmoredGreaves = 83		    # old: [2, 82, 0]
    CybertoonShoes = 84		    # old: [2, 83, 0]
    ShoesPirateGhost = 85       # old: [2, 84, 0]
    ShoesSpy = 86               # old: [2, 85, 0]

    ### Altis legacy shoe styles (auto-ported from ToonDNA.ShoesStyles) ###
    Altis_alchemist_shoes = 100000  # was ToonDNA style 'alchemist_shoes'
    Altis_aviator_boots = 100001  # was ToonDNA style 'aviator_boots'
    Altis_chair_shoes = 100002  # was ToonDNA style 'chair_shoes'
    Altis_homemade_ragdoll_boots = 100003  # was ToonDNA style 'homemade_ragdoll_boots'
    Altis_homemade_soldier_boots = 100004  # was ToonDNA style 'homemade_soldier_boots'
    Altis_hwtown_boots = 100005  # was ToonDNA style 'hwtown_boots'
    Altis_law_shoes = 100006  # was ToonDNA style 'law_shoes'
    Altis_lazy_bones_shoes = 100007  # was ToonDNA style 'lazy_bones_shoes'
    Altis_outback_shoes = 100008  # was ToonDNA style 'outback_shoes'
    Altis_phantom_shoes = 100009  # was ToonDNA style 'phantom_shoes'
    Altis_pumpkin_shoes = 100010  # was ToonDNA style 'pumpkin_shoes'
    Altis_ragdoll_humble = 100011  # was ToonDNA style 'ragdoll_humble'
    Altis_ragdoll_regal = 100012  # was ToonDNA style 'ragdoll_regal'
    Altis_ragdoll_traditional = 100013  # was ToonDNA style 'ragdoll_traditional'
    Altis_rainbow_shoes = 100014  # was ToonDNA style 'rainbow_shoes'
    Altis_retro_winterdress_shoes = 100015  # was ToonDNA style 'retro_winterdress_shoes'
    Altis_retro_wintersuit_shoes = 100016  # was ToonDNA style 'retro_wintersuit_shoes'
    Altis_sat1 = 100017  # was ToonDNA style 'sat1'
    Altis_sat2 = 100018  # was ToonDNA style 'sat2'
    Altis_sat3 = 100019  # was ToonDNA style 'sat3'
    Altis_sat4 = 100020  # was ToonDNA style 'sat4'
    Altis_scb1 = 100021  # was ToonDNA style 'scb1'
    Altis_scs1 = 100022  # was ToonDNA style 'scs1'
    Altis_scs2 = 100023  # was ToonDNA style 'scs2'
    Altis_scs3 = 100024  # was ToonDNA style 'scs3'
    Altis_scs4 = 100025  # was ToonDNA style 'scs4'
    Altis_scs5 = 100026  # was ToonDNA style 'scs5'
    Altis_scs6 = 100027  # was ToonDNA style 'scs6'
    Altis_sdk1 = 100028  # was ToonDNA style 'sdk1'
    Altis_sfb1 = 100029  # was ToonDNA style 'sfb1'
    Altis_sfb2 = 100030  # was ToonDNA style 'sfb2'
    Altis_sfb3 = 100031  # was ToonDNA style 'sfb3'
    Altis_sfb4 = 100032  # was ToonDNA style 'sfb4'
    Altis_sfb5 = 100033  # was ToonDNA style 'sfb5'
    Altis_sfb6 = 100034  # was ToonDNA style 'sfb6'
    Altis_shoes_cardBlack = 100035  # was ToonDNA style 'shoes_cardBlack'
    Altis_shoes_cardRed = 100036  # was ToonDNA style 'shoes_cardRed'
    Altis_shoes_cyberpunk = 100037  # was ToonDNA style 'shoes_cyberpunk'
    Altis_shoes_diver = 100038  # was ToonDNA style 'shoes_diver'
    Altis_shoes_engineer = 100039  # was ToonDNA style 'shoes_engineer'
    Altis_shoes_fruitpie = 100040  # was ToonDNA style 'shoes_fruitpie'
    Altis_shoes_gatekeeper = 100041  # was ToonDNA style 'shoes_gatekeeper'
    Altis_shoes_gator = 100042  # was ToonDNA style 'shoes_gator'
    Altis_shoes_painter = 100043  # was ToonDNA style 'shoes_painter'
    Altis_shoes_pirate_ghost = 100044  # was ToonDNA style 'shoes_pirate_ghost'
    Altis_shoes_spy = 100045  # was ToonDNA style 'shoes_spy'
    Altis_sht1 = 100046  # was ToonDNA style 'sht1'
    Altis_sht2 = 100047  # was ToonDNA style 'sht2'
    Altis_shw1 = 100048  # was ToonDNA style 'shw1'
    Altis_shw2 = 100049  # was ToonDNA style 'shw2'
    Altis_skeleton_shoes = 100050  # was ToonDNA style 'skeleton_shoes'
    Altis_slf1 = 100051  # was ToonDNA style 'slf1'
    Altis_smb1 = 100052  # was ToonDNA style 'smb1'
    Altis_smb2 = 100053  # was ToonDNA style 'smb2'
    Altis_smb3 = 100054  # was ToonDNA style 'smb3'
    Altis_smb4 = 100055  # was ToonDNA style 'smb4'
    Altis_smb5 = 100056  # was ToonDNA style 'smb5'
    Altis_smj1 = 100057  # was ToonDNA style 'smj1'
    Altis_smj2 = 100058  # was ToonDNA style 'smj2'
    Altis_smj3 = 100059  # was ToonDNA style 'smj3'
    Altis_smj4 = 100060  # was ToonDNA style 'smj4'
    Altis_smt1 = 100061  # was ToonDNA style 'smt1'
    Altis_sox1 = 100062  # was ToonDNA style 'sox1'
    Altis_space_boots = 100063  # was ToonDNA style 'space_boots'
    Altis_srb1 = 100064  # was ToonDNA style 'srb1'
    Altis_srb2 = 100065  # was ToonDNA style 'srb2'
    Altis_srb3 = 100066  # was ToonDNA style 'srb3'
    Altis_srb4 = 100067  # was ToonDNA style 'srb4'
    Altis_ssb1 = 100068  # was ToonDNA style 'ssb1'
    Altis_sst1 = 100069  # was ToonDNA style 'sst1'
    Altis_sts1 = 100070  # was ToonDNA style 'sts1'
    Altis_sts2 = 100071  # was ToonDNA style 'sts2'
    Altis_sts3 = 100072  # was ToonDNA style 'sts3'
    Altis_sts4 = 100073  # was ToonDNA style 'sts4'
    Altis_sts5 = 100074  # was ToonDNA style 'sts5'
    Altis_swb1 = 100075  # was ToonDNA style 'swb1'
    Altis_swb2 = 100076  # was ToonDNA style 'swb2'
    Altis_swk1 = 100077  # was ToonDNA style 'swk1'
    Altis_swt1 = 100078  # was ToonDNA style 'swt1'
    Altis_tin_humble = 100079  # was ToonDNA style 'tin_humble'
    Altis_tin_regal = 100080  # was ToonDNA style 'tin_regal'
    Altis_tin_traditional = 100081  # was ToonDNA style 'tin_traditional'
    Altis_tumbles_shoes = 100082  # was ToonDNA style 'tumbles_shoes'
    Altis_vintage_snow_outfit = 100083  # was ToonDNA style 'vintage_snow_outfit'
    Altis_wingsuit_boots = 100084  # was ToonDNA style 'wingsuit_boots'
    Altis_witch_shoes = 100085  # was ToonDNA style 'witch_shoes'


@defineItemSubtypeEnum(ItemType.Cosmetic_Neck)
class NeckItemType(IntEnum):
    """
    Item subtype enum for Neck accessories (scarves, bowties, etc.).
    """
    Scarf_NYE_2019 = 1                   # old: [40, 0, 0], backpack
    DoeBandana = 2                  # old: [43, 0, 0], backpack
    Scarf_Aviator = 3                # old: [47, 0, 0], backpack
    Bowtie_Pinwheel = 4              # old: [49, 0, 0], backpack
    BloodsuckerLollipop = 5         # old: [58, 12, 0], backpack
    CjTie = 6                       # old: [59, 13, 0], backpack
    Collar_Sailor_White = 7           # old: [60, 0, 0], backpack
    Collar_Sailor_Blue = 8            # old: [60, 15, 0], backpack
    Collar_Sailor_Cyan = 9            # old: [60, 16, 0], backpack
    Collar_Sailor_Green = 10          # old: [60, 17, 0], backpack
    Collar_Sailor_Orange = 11         # old: [60, 18, 0], backpack
    Collar_Sailor_Pink = 12           # old: [60, 19, 0], backpack
    Collar_Sailor_Purple = 13         # old: [60, 20, 0], backpack
    Collar_Sailor_Red = 14            # old: [60, 21, 0], backpack
    Collar_Sailor_Black = 15          # old: [60, 22, 0], backpack
    Collar_Sailor_Yellow = 16         # old: [60, 23, 0], backpack
    Collar_Sailor_Bow_White = 17             # old: [61, 0, 0], backpack
    Collar_Sailor_Bow_Blue = 18              # old: [61, 24, 0], backpack
    Collar_Sailor_Bow_Cyan = 19              # old: [61, 25, 0], backpack
    Collar_Sailor_Bow_Green = 20             # old: [61, 26, 0], backpack
    Collar_Sailor_Bow_Orange = 21            # old: [61, 27, 0], backpack
    Collar_Sailor_Bow_Pink = 22              # old: [61, 28, 0], backpack
    Collar_Sailor_Bow_Purple = 23            # old: [61, 29, 0], backpack
    Collar_Sailor_Bow_Red = 24               # old: [61, 30, 0], backpack
    Collar_Sailor_Bow_Black = 25             # old: [61, 31, 0], backpack
    Collar_Sailor_Bow_Yellow = 26            # old: [61, 32, 0], backpack
    Scarf_Retro_Black = 27                 # old: [67, 0, 0], backpack
    Scarf_NYE_2020 = 28                  # old: [40, 39, 0], backpack
    FlowerTie = 29                  # old: [69, 0, 0], backpack
    Bowtie_Clown = 30                # old: [73, 0, 0], backpack
    JesterCollar = 31               # old: [75, 42, 0], backpack
    LawBowtie = 32                  # old: [73, 43, 0], backpack
    Scarf_NYE_2021 = 33                  # old: [40, 48, 0], backpack
    OttomanTie = 34                 # old: [86, 0, 0], backpack
    EyeBowtie = 35                  # old: [89, 0, 0], backpack
    MysteryBowtie = 36              # old: [90, 0, 0], backpack
    NewstoonBlueBowtie = 37         # old: [73, 49, 0], backpack
    Scarf_NYE_2022 = 38                  # old: [93, 0, 0], backpack
    Bowtie_Ribbon_Pink = 39               # old: [40, 50, 0], backpack
    Bowtie_Ribbon_Redpolka = 40       # old: [93, 51, 0], backpack
    Bowtie_Ribbon_Purple = 41         # old: [93, 52, 0], backpack
    Bowtie_Ribbon_Yellow = 42         # old: [93, 53, 0], backpack
    Bowtie_Ribbon_Bluechecker = 43    # old: [93, 54, 0], backpack
    Bowtie_Ribbon_Red = 44            # old: [93, 55, 0], backpack
    Bowtie_Ribbon_Rainbow = 45        # old: [93, 56, 0], backpack
    Bowtie_Ribbon_Pinkdots = 46       # old: [93, 57, 0], backpack
    Bowtie_Ribbon_Greenchecker = 47   # old: [93, 58, 0], backpack
    Bowtie_Ribbon_Blue = 48           # old: [93, 59, 0], backpack
    Bowtie_Ribbon_Candycorn = 49      # old: [93, 60, 0], backpack
    Bowtie_Ribbon_Black = 50          # old: [93, 61, 0], backpack
    Necklace_Brovinci = 51           # old: [96, 0, 0], backpack
    NeckCowbell = 52                # old: [101, 0, 0], backpack
    Bowtie_Fancy_Black = 53              # old: [73, 72, 0], backpack
    Bowtie_Fancy_Blackwhite = 54         # old: [73, 73, 0], backpack
    Bowtie_Fancy_Blue = 55               # old: [73, 74, 0], backpack
    Bowtie_Fancy_Gray = 56               # old: [73, 75, 0], backpack
    Bowtie_Fancy_Green = 57              # old: [73, 76, 0], backpack
    Bowtie_Fancy_Orange = 58             # old: [73, 77, 0], backpack
    Bowtie_Fancy_Pink = 59               # old: [73, 78, 0], backpack
    Bowtie_Fancy_Pinkblack = 60          # old: [73, 79, 0], backpack
    Bowtie_Fancy_Polkadot = 61           # old: [73, 80, 0], backpack
    Bowtie_Fancy_Purple = 62             # old: [73, 81, 0], backpack
    Bowtie_Fancy_Purpleorange = 63       # old: [73, 82, 0], backpack
    Bowtie_Fancy_Red = 64                # old: [73, 83, 0], backpack
    Bowtie_Fancy_Yellow = 65             # old: [73, 84, 0], backpack
    Bowtie_Fancy_Yellowblack = 66        # old: [73, 85, 0], backpack
    Scarf_Chef_Red = 67                # old: [108, 0, 0], backpack
    BandanaEngineer = 68            # old: [51, 71, 0], backpack
    Scarf_NYE_2023 = 69                  # old: [40, 86, 0], backpack
    OutbackBandana = 70             # old: [51, 0, 0], backpack
    Bowtie_Pride_Ace = 71             # old: [73, 88, 0], backpack
    Bowtie_Pride_Aro = 72             # old: [73, 89, 0], backpack
    Bowtie_Pride_Bi = 73              # old: [73, 90, 0], backpack
    Bowtie_Pride_Gay = 74             # old: [73, 91, 0], backpack
    Bowtie_Pride_Fluid = 75           # old: [73, 92, 0], backpack
    Bowtie_Pride_Lesbian = 76         # old: [73, 93, 0], backpack
    Bowtie_Pride_Lgbt = 77            # old: [73, 94, 0], backpack
    Bowtie_Pride_Nb = 78              # old: [73, 95, 0], backpack
    Bowtie_Pride_Pan = 79             # old: [73, 96, 0], backpack
    Bowtie_Pride_Trans = 80           # old: [73, 97, 0], backpack
    Bowtie_Elf = 81             # old: [115, 0, 0], backpack
    Scarf_NYE_2024 = 82         # old: [40, 98, 0], backpack


"""Social ItemTypes"""


@defineItemSubtypeEnum(ItemType.Social_CheesyEffect)
class CheesyEffectItemType(IntEnum):
    """
    Item subtype enum for Cheesy Effects.
    """

    BigHead = 1
    SmallHead = 2
    BigLegs = 3
    SmallLegs = 4
    BigToon = 5
    SmallToon = 6
    FlatPortrait = 7
    FlatProfile = 8
    Transparent = 9
    NoColor = 10
    Invisible = 11
    BigWhite = 13
    SnowMan = 14
    GreenToon = 15
    Spirit = 20
    Stomped = 21
    Backwards = 22
    Amogus = 23
    Wireframe = 77
    Fired = 78


@defineItemSubtypeEnum(ItemType.Social_CustomSpeedchat)
class CustomSpeedchatItemType(IntEnum):
    """
    Item subtype enum for custom Speedchat phrases.
    """
    OhWell = 10
    WhyNot = 20
    Naturally = 30
    ThatsTheWayToDoIt = 40
    RightOn = 50
    WhatUp = 60
    ButOfCourse = 70
    Bingo = 80
    YouveGotToBeKidding = 90
    SoundsGoodToMe = 100
    ThatsKooky = 110
    Awesome = 120
    ForCryingOutLoud = 130
    DontWorry = 140
    Grrrr = 150
    WhatsNew = 160
    HeyHeyHey = 170
    SeeYouTomorrow = 180
    SeeYouNextTime = 190
    SeeYaLaterAlligator = 200
    AfterAWhileCrocodile = 210
    INeedToGoSoon = 220
    IDontKnowAboutThis = 230
    YoureOuttaHere = 240
    OuchThatReallySmarts = 250
    Gotcha = 260
    Please = 270
    ThanksAMillion = 280
    YouAreStylin = 290
    ExcuseMe = 300
    CanIHelpYou = 310
    ThatsWhatImTalkingAbout = 320
    IfYouCantTakeTheHeatStayOutOfTheKitchen = 330
    WellShiverMeTimbers = 340
    WellIsntThatSpecial = 350
    QuitHorsingAround = 360
    CatGotYourTongue = 370
    YoureInTheDogHouseNow = 380
    LookWhatTheCatDraggedIn = 390
    INeedToGoSeeAToon = 400
    DontHaveACow = 410
    DontChickenOut = 420
    YoureASittingDuck = 430
    Whatever = 440
    Totally = 450
    Sweet = 460
    ThatRules = 470
    YeahBaby = 480
    CatchMeIfYouCan = 490
    YouNeedToHealFirst = 500
    YouNeedMoreLaffPoints = 510
    IllBeBackInAMinute = 520
    ImHungry = 530
    YeahRight = 540
    ImSleepy = 550
    ImReady = 560
    ImBored = 570
    ILoveIt = 580
    ThatWasExciting = 590
    Jump = 600
    GotGags = 610
    WhatsWrong = 620
    EasyDoesIt = 630
    SlowAndSteadyWinsTheRace = 640
    Touchdown = 650
    Ready = 660
    Set = 670
    Go = 680
    LetsGoThisWay = 690
    YouWon = 700
    IVoteYes = 710
    IVoteNo = 720
    CountMeIn = 730
    CountMeOut = 740
    StayHereIllBeBack = 750
    ThatWasQuick = 760
    DidYouSeeThat = 770
    WhatsThatSmell = 780
    ThatStinks = 790
    IDontCare = 800
    JustWhatTheDoctorOrdered = 810
    LetsGetThisPartyStarted = 820
    ThisWayEverybody = 830
    WhatInTheWorld = 840
    TheChecksInTheMail = 850
    IHeardThat = 860
    AreYouTalkingToMe = 870
    ThankYouIllBeHereAllWeek = 880
    Hmm = 890
    IllGetThisOne = 900
    IGotIt = 910
    ItsMine = 920
    PleaseTakeIt = 930
    StandBackThisCouldBeDangerous = 940
    NoWorries = 950
    OhMy = 960
    Whew = 970
    Owoooo = 980
    AllAboard = 990
    HotDiggityDog = 1000
    CuriosityKilledTheCat = 1010
    TeamworkMakesTheDreamWork = 1011
    EvenMiraclesTakeALittleTime = 1012
    SometimesTheRightPathIsNotTheEasiestOne = 1013
    TodayIsAGoodDayToTry = 1014
    TodayIsMyLuckyDay = 1015
    GetYourActTogether = 1016
    WellPlayItByEar = 1017
    APieInTheHandIsWorthTwoInTheOven = 1018
    ItsRainingCatsAndDogs = 1019
    IThinkIllCallItADay = 1020
    TakeThis = 1021
    TakeThat = 1022
    Electrifying = 1023
    BeBackInAJiffy = 1024
    IDontSeeWhyNot = 1025
    YouNeverKnowUnlessYouTry = 1026
    SmartMove = 1027
    ThatCantBeAGoodIdea = 1028
    ImDownForTheCount = 1029
    IThinkYouShouldSleepOnIt = 1030
    Valid = 1031
    EverybodyIsWelcome = 1032
    TheresAlwaysASpaceForYou = 1033
    IConcur = 1034
    KindnessIsTheBestPolicy = 1035
    HonestyIsTheBestPolicy = 1036
    ManyDifferentFlowersMakeABouquet = 1037
    GreatMindsThinkAlike = 1038
    IfYouWantToGoFarGoTogether = 1039
    IAmGoingToScream = 1040
    OhYoureApproachingMe = 1041
    Yeah = 1042
    ActYourAge = 2000
    AmIGladToSeeYou = 2010
    BeMyGuest = 2020
    BeenKeepingOutOfTrouble = 2030
    BetterLateThanNever = 2040
    Bravo = 2050
    ButSeriouslyFolks = 2060
    CareToJoinUs = 2070
    CatchYouLater = 2080
    ChangedYourMind = 2090
    ComeAndGetIt = 2100
    DearMe = 2110
    DelightedToMakeYourAcquaintance = 2120
    DontDoAnythingIWouldntDo = 2130
    DontEvenThinkAboutIt = 2140
    DontGiveUpTheShip = 2150
    DontHoldYourBreath = 2160
    DontAsk = 2170
    EasyForYouToSay = 2180
    EnoughIsEnough = 2190
    Excellent = 2200
    FancyMeetingYouHere = 2210
    GiveMeABreak = 2220
    GladToHearIt = 2230
    GoAheadMakeMyDay = 2240
    GoForIt = 2250
    GoodJob = 2260
    GoodToSeeYou = 2270
    GotToGetMoving = 2280
    GotToHitTheRoad = 2290
    HangInThere = 2300
    HangOnASecond = 2310
    HaveABall = 2320
    HaveFun = 2330
    HaventGotAllDay = 2340
    HoldYourHorses = 2350
    Horsefeathers = 2360
    IDontBelieveThis = 2370
    IDoubtIt = 2380
    IOweYouOne = 2390
    IReadYouLoudAndClear = 2400
    IThinkSo = 2410
    IllPass = 2420
    IWishIdSaidThat = 2430
    IWouldntIfIWereYou = 2440
    IdBeHappyTo = 2450
    ImHelpingMyFriend = 2460
    ImHereAllWeek = 2470
    ImagineThat = 2480
    InTheNickOfTime = 2490
    ItsNotOverTilItsOver = 2500
    JustThinkingOutLoud = 2510
    KeepInTouch = 2520
    LovelyWeatherForDucks = 2530
    MakeItSnappy = 2540
    MakeYourselfAtHome = 2550
    MaybeSomeOtherTime = 2560
    MindIfIJoinYou = 2570
    NicePlaceYouHaveHere = 2580
    NiceTalkingToYou = 2590
    NoDoubtAboutIt = 2600
    NoKidding = 2610
    NotByALongShot = 2620
    OfAllTheNerve = 2630
    OkayByMe = 2640
    Righto = 2650
    SayCheese = 2660
    SayWhat = 2670
    TahDah = 2680
    TakeItEasy = 2690
    TaTaForNow = 2700
    ThanksButNoThanks = 2710
    ThatTakesTheCake = 2720
    ThatsFunny = 2730
    ThatsTheTicket = 2740
    TheresACogInvasion = 2750
    Toodles = 2760
    WatchOut = 2770
    WellDone = 2780
    WhatsCooking = 2790
    WhatsHappening = 2800
    WorksForMe = 2810
    YesSirree = 2820
    YouBetcha = 2830
    YouDoTheMath = 2840
    YouLeavingSoSoon = 2850
    YouMakeMeLaugh = 2860
    YouTakeRight = 2870
    YoureGoingDown = 2880
    AnythingThatCanGoWrongWillGoWrong = 2881
    NeverInAMillionYears = 2882
    WouldYouLikeSomeJellybeansWithThat = 2883
    LetTheSleepingDogLie = 2884
    Jinx = 2885
    XMarksTheSpot = 2886
    IsThatLegal = 2887
    ThatIsIllegal = 2888
    IllBeTheJudgeOfThat = 2889
    YouBeTheJudge = 2890
    HowIsThatEvenPossible = 2891
    IDontThinkItMeansWhatYouThinkItMeans = 2892
    Wonderful = 2893
    Terrific = 2894
    Really = 2895
    Nope = 2896
    WithGreatPowerComesGreatResponsibility = 2897
    ItsYourTurn = 2898
    IveMadeUpMyMind = 2899
    SpeakOfTheDevilRay = 2900
    ThisIsAVrbys = 2901
    ThisIsFine = 2092
    BringItOnTinCan = 2093
    IBegYourPardon = 2094
    AnythingYouSay = 3000
    CareIfIJoinYou = 3010
    CheckPlease = 3020
    DontBeTooSure = 3030
    DontMindIfIDo = 3040
    DontSweatIt = 3050
    DontYouKnowIt = 3060
    DontMindMe = 3070
    Eureka = 3080
    FancyThat = 3090
    ForgetAboutIt = 3100
    GoingMyWay = 3110
    GoodForYou = 3120
    GoodGrief = 3130
    HaveAGoodOne = 3140
    HeadsUp = 3150
    HereWeGoAgain = 3160
    HowAboutThat = 3170
    HowDoYouLikeThat = 3180
    IBelieveSo = 3190
    IThinkNot = 3200
    IllGetBackToYou = 3210
    ImAllEars = 3220
    ImBusy = 3230
    ImNotKidding = 3240
    ImSpeechless = 3250
    KeepSmiling = 3260
    LetMeKnow = 3270
    LetThePieFly = 3280
    LikewiseImSure = 3290
    LookAlive = 3300
    MyHowTimeFlies = 3310
    NoComment = 3320
    NowYoureTalking = 3330
    OkayByMeDupe = 3340
    PleasedToMeetYou = 3350
    RightoDupe = 3360
    SureThing = 3370
    ThanksAMillionDupe = 3380
    ThatsMoreLikeIt = 3390
    ThatsTheStuff = 3400
    TimeForMeToHitTheHay = 3410
    TrustMe = 3420
    UntilNextTime = 3430
    WaitUp = 3440
    WayToGo = 3450
    WhatBringsYouHere = 3460
    WhatHappened = 3470
    WhatNow = 3480
    YouFirst = 3490
    YouTakeLeft = 3500
    YouWish = 3510
    YoureToast = 3520
    YoureTooMuch = 3530
    DontKeepMeWaiting = 3531
    DontJudgeABookByItsCover = 3532
    LongTimeNoSee = 3533
    PassTheSaltPlease = 3534
    ItsTimeForTea = 3535
    ThatsAWrap = 3536
    TryAgain = 3537
    GetInLine = 3538
    IsIt = 3539
    ProbablyNot = 3540
    Ding = 3541
    IVolunteer = 3542
    GoodToKnow = 3543
    YouHaveGoodTaste = 3544
    TheCogsAreNoMatchForUs = 3545
    DohIMissed = 3546
    ICantBelieveYouveDoneThis = 3547
    ItsOver = 3548
    ThisWasNotOurFinestMoment = 3549
    YoureNotMyBoss = 3550
    YouCanNeverBeTooSafe = 3551
    ToonsRule = 4000
    CogsDrool = 4010
    ToonsOfTheWorldUnite = 4020
    HowdyPartner = 4030
    MuchObliged = 4040
    GetAlongLittleDoggie = 4050
    ImGoingToHitTheHay = 4060
    ImChompingAtTheBit = 4070
    ThisTownIsntBigEnoughForTheTwoOfUs = 4080
    SaddleUp = 4090
    Draw = 4100
    TheresGoldInThemThereHills = 4110
    HappyTrails = 4120
    ThisIsWhereIRideOffIntoTheSunset = 4130
    LetsSkedaddle = 4140
    YouGotABeeInYourBonnet = 4150
    LandsSake = 4160
    RightAsRain = 4170
    IReckonSo = 4180
    LetsRide = 4190
    WellGoFigure = 4200
    ImBackInTheSaddleAgain = 4210
    RoundUpTheUsualSuspects = 4220
    Giddyup = 4230
    ReachForTheSky = 4240
    ImFixingTo = 4250
    HoldYourHorsesDupe = 4260
    ICantHitTheBroadSideOfABarn = 4270
    YallComeBackNow = 4280
    ItsARealBarnBurner = 4290
    DontBeAYellowBelly = 4300
    FeelingLucky = 4310
    WhatInSamHillsGoinOnHere = 4320
    ShakeYourTailFeathers = 4330
    WellDontThatTakeAll = 4340
    ThatsASightForSoreEyes = 4350
    PickinsIsMightySlimAroundHere = 4360
    TakeALoadOff = 4370
    ArentYouASight = 4380
    ThatllLearnYa = 4390
    Unforgivable = 4391
    IsThatIt = 4392
    ThatsIt = 4393
    ThatsEnoughForMe = 4394
    WeAreMintToBe = 4395
    LettuceCelebrate = 4396
    LetsTacoAboutIt = 4397
    Glue = 4398
    UnderstandableHaveANiceDay = 4399
    LoveThatForYou = 4400
    ComeToThinkOfIt = 4401
    AndFinally = 4402
    IWantCandy = 6000
    IveGotASweetTooth = 6010
    ThatsHalfBaked = 6020
    JustLikeTakingCandyFromABaby = 6030
    TheyreCheaperByTheDozen = 6040
    LetThemEatCake = 6050
    ThatsTheIcingOnTheCake = 6060
    YouCantHaveYourCakeAndEatItToo = 6070
    IFeelLikeAKidInACandyStore = 6080
    SixOfOneHalfADozenOfTheOther = 6090
    LetsKeepItShortAndSweet = 6100
    DoughnutMindIfIDo = 6110
    ThatsPieInTheSky = 6120
    ButItsWaferThin = 6130
    LetsGumUpTheWorks = 6140
    YoureOneToughCookie = 6150
    ThatsTheWayTheCookieCrumbles = 6160
    LikeWaterForChocolate = 6170
    AreYouTryingToSweetTalkMe = 6180
    ASpoonfulOfSugarHelpsTheMedicineGoDown = 6190
    YouAreWhatYouEat = 6200
    EasyAsPie = 6210
    DontBeASucker = 6220
    SugarAndSpiceAndEverythingNice = 6230
    ItsLikeButter = 6240
    TheCandymanCan = 6250
    WeAllScreamForIceCream = 6260
    LetsNotSugarCoatIt = 6270
    KnockKnock = 6280
    WhosThere = 6290
    Lit = 6291
    IllSitThisOneOut = 6292
    IfOnlyIHadAMillionJellybeans = 6293
    Foreshadowing = 6294
    YourePopular = 6295
    NotMe = 6296
    Kaboom = 6297
    AsAMatterOfFact = 6298
    IllComeBackToThatTomorrow = 6299
    ThisIsTooMuchForMe = 6300
    WereGoingToBeSafeAndSound = 6301
    HowArtThou = 6302
    Howdyeth = 6303
    DontBurnethTheCandleAtBothEnds = 6304
    WhatDostThouNeedeth = 6305
    AsIf = 6306
    Actually = 6307
    QuitMonkeyingAround = 7000
    ThatReallyThrowsAMonkeyWrenchInThings = 7010
    MonkeySeeMonkeyDo = 7020
    TheyMadeAMonkeyOutOfYou = 7030
    ThatSoundsLikeMonkeyBusiness = 7040
    ImJustMonkeyingWithYou = 7050
    WhosGonnaBeMonkeyInTheMiddle = 7060
    ThatsAMonkeyOffMyBack = 7070
    ThisIsMoreFunThanABarrelOfMonkeys = 7080
    WellIllBeAMonkeysUncle = 7090
    IveGotMonkeysOnTheBrain = 7100
    WhatsWithTheMonkeySuit = 7110
    HearNoEvil = 7120
    SeeNoEvil = 7130
    SpeakNoEvil = 7140
    LetsMakeLikeABananaAndSplit = 7150
    ItsAJungleOutThere = 7160
    YoureTheTopBanana = 7170
    CoolBananas = 7180
    ImGoingBananas = 7190
    LetsGetIntoTheSwingOfThings = 7200
    ThisPlaceIsSwinging = 7210
    ImDyingOnTheVine = 7220
    LetsMakeLikeATreeAndLeave = 7230
    ThisWholeAffairHasMeUpATree = 7235
    JellybeansDontGrowOnTrees = 7240
    ThatsNotReal = 7241
    YaLikeJazz = 7242
    LetThePiesFly = 7243
    WeDontSpeakOnThat = 7244
    AMagicianShallNeverRevealTheirSecrets = 7245
    OoohWhatDoesThisButtonDo = 7246
    BuhBye = 7247
    MyFavoriteDayIsSundae = 7248
    FingersCrossed = 7249
    ThatsCrazy = 7250
    Gadzooks = 7251
    AhoyMeHearties = 7252
    DontMissTheForestForTheTrees = 7253
    IAgreeWithYourStatement = 7256
    IDisagreeWithYourStatement = 7257
    TrueTrue = 7258
    ThisPlaceIsAGhostTown = 10000
    NiceCostume = 10001
    IThinkThisPlaceIsHaunted = 10002
    TrickOrTreat = 10003
    Boo = 10004
    HappyHaunting = 10005
    HappyHalloween = 10006
    ItsTimeForMeToTurnIntoAPumpkin = 10007
    Spooktastic = 10008
    Spooky = 10009
    ThatsCreepy = 10010
    IHateSpiders = 10011
    DidYouHearThat = 10012
    YouDontHaveAGhostOfAChance = 10013
    YouScaredMe = 10014
    ThatsSpooky = 10015
    ThatsFreaky = 10016
    ThatWasStrange = 10017
    SkeletonsInYourCloset = 10018
    DidIScareYou = 10019
    FlippyNeedsYourHelp = 10020
    HaveYouFoundTheScientistsYet = 10021
    HaveYouSeenTheNewSpookyBuildingOnPolarPlace = 10022
    Spooktacular = 10023
    ThatReallySendsAShiverDownMySpine = 10024
    ImTerrified = 10025
    DontBeAScaredyCat = 10026
    PleaseParkAllYourBroomsAndPumpkinCartsAtTheDoor = 10027
    EatDrinkAndBeScary = 10028
    WitchWayToTheTreats = 10029
    EnterIfYouDare = 10030
    BahHumbug = 11000
    BetterNotPout = 11001
    Brrr = 11002
    ChillOut = 11003
    ComeAndGetItDupe = 11004
    DontBeATurkey = 11005
    GobbleGobble = 11006
    HappyHolidays = 11007
    HappyNewYear = 11008
    HappyThanksgiving = 11009
    HappyTurkeyDay = 11010
    HoHoHo = 11011
    ItsSnowProblem = 11012
    ItsSnowWonder = 11013
    LetItSnow = 11014
    RakeEmIn = 11015
    SeasonsGreetings = 11016
    SnowDoubtAboutIt = 11017
    SnowFarSnowGood = 11018
    YuleBeSorry = 11019
    HaveAWonderfulWinter = 11020
    Festive = 11021
    IcyWhatYouDidThere = 11022
    AllIWantForChristmasIsEwe = 11023
    BeMine = 12000
    BeMySweetie = 12001
    HappyValentoonsDay = 12002
    AwwHowCute = 12003
    ImSweetOnYou = 12004
    ItsPuppyLove = 12005
    LoveYa = 12006
    WillYouBeMyValentoon = 12007
    YouAreASweetheart = 12008
    YouAreAsSweetAsPie = 12009
    YouAreCute = 12010
    YouNeedAHug = 12011
    Lovely = 12012
    ThatsDarling = 12013
    RosesAreRed = 12014
    VioletsAreBlue = 12015
    ThatsSweet = 12016
    ILoveYouMoreThanACogLovesOil = 12050
    YoureDynamite = 12051
    IOnlyHaveHypnoEyesForYou = 12052
    YoureSweeterThanAJellybean = 12053
    YoureValentoonTastic = 12054
    AKissARooFromMeToYou = 12055
    WeAreThePerfectPear = 12056
    YouArePurrFect = 12057
    ImYourBiggestFan = 12058
    YoureTheIcingOnTheCake = 12059
    YoureTheAppleOfMyEye = 12060
    TopOTheMorninToYou = 13000
    HappyStPatricksDay = 13001
    YoureNotWearingGreen = 13002
    ItsTheLuckOfTheIrish = 13003
    ImGreenWithEnvy = 13004
    YouLuckyDog = 13005
    YoureMyFourLeafClover = 13006
    YoureMyLuckyCharm = 13007


@defineItemSubtypeEnum(ItemType.Social_ChatStickers)
class ChatStickersItemType(EnhancedIntEnum):
    """
    Item subtype enum for Chat Stickers.
    """

    # Defaults
    DisgustGator = 0
    ConcernedDog = 1
    ConfusedKangaroo = 2
    CryCat = 3
    GriefKiwi = 4
    BlushBat = 5
    GrinDuck = 6
    HeartRabbit = 7
    GreenedCat = 8
    PensiveFox = 9
    PleadingDog = 10
    SadBat = 11
    SurprisedArmadillo = 12
    SurprisedRaccoon = 13
    SusBeaver = 14
    WinkDeer = 15

    # Regional managers
    Bellringer = 16
    ChainsawConsultant = 17
    DeepDiver = 18
    DuckShuffler = 19
    Featherbedder = 20
    Firestarter = 21
    Gatekeeper = 22
    MajorPlayer = 23
    Mouthpiece = 24
    Multislacker = 25
    Pacesetter = 26
    Plutocrat = 27
    Prethinker = 28
    Rainmaker = 29
    Treekiller = 30
    WitchHunter = 31

    SellbotEmblem = 32
    CashbotEmblem = 33
    LawbotEmblem = 34
    BossbotEmblem = 35
    BoardbotEmblem = 36

    DiceRoll = 40

    HighRoller = 50
    FrustratedForeman = 51

    Litigator = 52
    Stenographer = 53
    CaseManager = 54
    Scapegoat = 55


@defineItemSubtypeEnum(ItemType.Social_NametagFont)
class NametagFontItemType(IntEnum):
    """
    Item subtype enum for Nametag fonts
    """
    # Defaults
    Basic = 0
    Plain = 1
    Shivering = 2
    Wonky = 3
    Fancy = 4
    Silly = 5
    Zany = 6
    Practical = 7
    Nautical = 8
    Whimsical = 9
    Spooky = 10
    Action = 11
    Poetic = 12
    Boardwalk = 13
    Western = 14
    Abstract = 15

    # Kudos Fonts
    IceCream = 16
    Pirate = 17
    Medieval = 18
    Calligraphy = 19
    Playful = 20
    Comical = 21
    Arrogant = 22
    Cinema = 23


@defineItemSubtypeEnum(ItemType.Social_Emote)
class EmoteItemType(IntEnum):
    """
    Item subtype enum for Emotes.
    IDs are identical to the IDs for old emotes.
    """
    Wave = 0
    Happy = 1
    Sad = 2
    Angry = 3
    Sleepy = 4
    Shrug = 5
    Dance = 6
    Think = 7
    Bored = 8
    Applause = 9
    Cringe = 10
    Confused = 11
    BellyFlop = 12
    Bow = 13
    BananaPeel = 14
    ResistanceSalute = 15
    # Skipping 16. This was an unused variant of Laugh.
    LaughUNUSED = 16
    Yes = 17
    No = 18
    OK = 19
    Surprise = 20
    Cry = 21
    Delighted = 22
    Furious = 23
    Laugh = 24
    Taunt = 25
    Yawn = 26
    Shiver = 27


@defineItemSubtypeEnum(ItemType.Profile_Background)
class BackgroundItemType(IntEnum):
    """
    Item subtype enum for Backgrounds.
    """
    Default = 0  # from: 0

    PG_Sky_TTC = 100  # from: 1
    PG_Sky_BB = 101  # from: 23
    PG_Sky_YOTT = 102  # from: 25
    PG_Sky_DG = 103  # from: 24
    PG_Sky_MML = 104  # from: 2
    PG_Sky_TB = 105  # from: 3
    PG_Sky_AA = 106  # from: 26
    PG_Sky_DDL = 107  # from: 4

    PG_TTC = 200  # from: 5
    PG_BB = 201  # from: 6
    PG_YOTT = 202  # from: 8
    PG_DG = 203  # from: 7
    PG_MML = 204  # from: 9
    PG_TB = 205  # from: 10
    PG_AA = 206  # from: 11
    PG_DDL = 207  # from: 12

    HQ_Sellbot = 300  # from: 13
    HQ_Cashbot = 301  # from: 14
    HQ_Lawbot = 302  # from: 15
    HQ_Bossbot = 303  # from: 16
    HQ_Boardbot = 304  # from: 17

    Activity_Fishing = 400  # from: 18
    Activity_Golfing = 401  # from: 27
    Activity_Racing = 402  # from: 28
    Activity_Trolley = 403  # from: 29

    Tasks_Judy = 500  # from: 39

    Event_Winter2018_A = 600  # from: 19
    Event_Winter2018_B = 601  # from: 20
    Event_NewYears2019 = 602  # from: 21
    Event_SkyClan = 603  # from: 22
    Event_Outback = 604  # from: 30
    Event_GoldenCorridor = 605  # from: 31
    Event_NewYears2020 = 606  # from: 32
    Event_BTL = 607  # from: 33
    Event_Valentines2020 = 608  # from: 34
    Event_Easter2020 = 609  # from: 35
    Event_StandIn = 610  # from: 36
    Event_FourthJuly2020 = 611  # from: 37
    Event_Halloween2020 = 612  # from: 38
    Event_Electric      = 613  # from: 49
    Event_Witch         = 614  # from: 50

    Special_PaintMixer = 700  # from: 40

    Kudos_TTC = 800  # from: 41
    Kudos_BB = 801  # from: 42
    Kudos_YOTT = 802  # from: 43
    Kudos_DG = 803  # from: 44
    Kudos_MML = 804  # from: 45
    Kudos_TB = 805  # from: 46
    Kudos_AA = 806  # from: 47
    Kudos_DDL = 807  # from: 48


@defineItemSubtypeEnum(ItemType.Profile_Nameplate)
class NameplateItemType(IntEnum):
    """
    Item subtype enum for Nameplates.
    """
    DefaultBlue = 101  # from: 0
    DefaultGreen = 102  # from: 1 [do not give]
    DefaultPurple = 103  # from: 2 [do not give]
    DefaultRed = 104  # from: 3 [do not give]
    DefaultYellow = 105  # from: 4 [do not give]
    DefaultOrange = 106  # from: 5 [do not give]
    DefaultBlueB = 107  # from: 6 [do not give]
    DefaultDarkBlue = 108  # from: 7 [do not give]
    DefaultDarkGreen = 109  # from: 8 [do not give]

    PG_TTC = 200  # from: 20
    PG_BB = 201  # from: 25
    PG_YOTT = 202  # from: 26
    PG_DG = 203  # from: 10
    PG_MML = 204  # from: 27
    PG_TB = 205  # from: 28
    PG_AA = 206  # from: 29
    PG_DDL = 207  # from: 11

    Activity_Golfing = 300  # from: 22
    Activity_Trolley = 301  # from: 23
    Activity_Racing = 302  # from: 24

    Tasks_Judy = 400  # from: 44

    Special_Stars = 500  # from: 9
    Special_UnderTheSea = 501  # from: 12
    Special_Slippin = 502  # from: 19
    Special_UpToEleven = 503  # from: 37
    Special_SnowballFight = 504  # from: 45
    Special_SellbotPaint = 505  # from: 46

    Event_Tinsel = 600  # from: 13
    Event_Candy = 601  # from: 14
    Event_Wrapping = 602  # from: 15
    Event_NightLights = 603  # from: 16
    Event_NewYears2019 = 604  # from: 17
    Event_SkyClan = 605  # from: 18
    Event_Outback = 606  # from: 21
    Event_LazyBones = 607  # from: 30
    Event_Thanksgiving2019 = 608  # from: 31
    Event_NewYears2020 = 609  # from: 32
    Event_PinkSlip = 610  # from: 33
    Event_Easter2020 = 611  # from: 34
    Event_AtticusDesk = 612  # from: 35
    Event_FourthJuly2020 = 613  # from: 36
    Event_Electric = 614  # from: 55
    Event_Witch = 615  # from: 56
    Event_HighRoller = 615

    Halloween_CandyBlue = 700  # from: 38
    Halloween_CandyGreen = 701  # from: 39
    Halloween_CandyMagenta = 702  # from: 40
    Halloween_CandyPurple = 703  # from: 41
    Halloween_CandyRed = 704  # from: 42
    Halloween_SpookyBat = 705  # from: 43

    Kudos_TTC = 800  # from: 47
    Kudos_BB = 801  # from: 48
    Kudos_YOTT = 802  # from: 49
    Kudos_DG = 803  # from: 50
    Kudos_MML = 804  # from: 51
    Kudos_TB = 805  # from: 52
    Kudos_AA = 806  # from: 53
    Kudos_DDL = 807  # from: 54

    ### Makeship ###
    Makeship_DuckShufflerGreen = 616
    Makeship_DuckShufflerRed = 617
    Makeship_FirePace = 618


@defineItemSubtypeEnum(ItemType.Profile_Pose)
class ProfilePoseItemType(IntEnum):
    """
    Item subtype enum for profile poses.
    """
    Neutral = 0  # from: 0
    Wave = 1  # from: 1
    Sit = 2  # from: 2
    Applause = 3  # from: 3
    Thinking = 4  # from: 4
    Greened = 5  # from: 5
    Taunt = 6  # from: 6
    ImOuttaHere = 7  # from: 7
    Casting = 8  # from: 8
    Yippie = 9  # from: 9
    Selfie = 10  # from: 10
    ResistanceSalute = 11  # from: 11
    Throw = 12  # from: 12
    Hypnotizer = 13  # from: 13
    Running = 14  # from: 14
    Diving = 15  # from: 15
    WhatAreYouDoing = 16  # from: 16
    Slapped = 17  # from: 17
    Surprised = 18  # from: 18
    Presenting = 19  # from: 19
    Victory = 20  # from: 20
    Shrug = 21  # from: 21
    Upset = 22  # from: 22
    ToBeOrNotToBe = 23  # from: 23
    Spooky = 24  # from: 24
    Zombie = 25  # from: 25
    Yawn = 26  # from: 26
    Sinking = 27  # from: 27
    Megaphone = 28  # from: 28
    UpsideDown = 29  # from: 29
    Sideways = 30  # from: 30
    Small = 31  # from: 31
    SilentTreatment = 32  # from: 32
    Banana = 33  # from: 33
    SeltzerBottle = 34  # from: 34
    GagButton = 35  # from: 35
    PieToss = 36  # from: 36
    BecomeDuck = 37  # from: 37
    Treasure = 38  # from: 38
    AtTheGate = 39  # from: 39
    Elegance = 40  # from: 40
    PickUpThePhone = 41  # from: 41
    FireHands = 42  # from: 42
    Rolled = 43  # from: 43
    Naptime = 44  # from: 44


"""Fishing Item Types"""


@defineItemSubtypeEnum(ItemType.Fishing_Rod)
class FishingRodItemType(IntEnum):
    """
    Item subtype enum for fishing rods.
    """
    Cardboard = 1  # from 0
    Twig = 2  # from 1
    Bamboo = 3  # from 2
    Hardwood = 4  # from 3
    Steel = 5  # from 4
    Gold = 6  # from 5
    Platinum = 7  # from 6


"""Estate Item Types"""


@defineItemSubtypeEnum(ItemType.Estate_Furniture)
class FurnitureItemType(IntEnum):
    """
    Item subtype enum for furniture.
    """
    """
    DA RULEZ
    The following items are NOT allowed to be defined here !
    - Gags
    - Accessories
    
    0 - 9999 = reserved for debug
    >10k: debug
    10k: window views
    20k: houses/doorways
    30k: beginning of props
    30k - 60k: toon focused props
    60k - 90k: suit focused props
    """

    # 0 - 9999 = reserved for debug
    # Debug props (1XXX)
    Debug_Doorway = 1000
    # Debug floors 11XX
    Debug_Floor_Lava = 1100

    Debug_Scale_Interior_Small = 1110
    Debug_Scale_Interior_Medium = 1111
    Debug_Scale_Interior_Large = 1112
    Debug_Scale_Exterior_Small = 1113
    Debug_Scale_Exterior_Medium = 1114
    Debug_Scale_Exterior_Large = 1115

    # Debug primitive shapes (2XXX)
    Debug_Primitive_Cube_Floor = 2000
    Debug_Primitive_Cube_Wall = 2001
    Debug_Primitive_Sphere = 2002
    Debug_Primitive_Stair = 2003
    Debug_Primitive_Ramp = 2004
    Debug_Primitive_Cylinder = 2005

    ### Window Views ###
    Window_LargeGarden    = 10000
    Window_WildGarden     = 10001
    Window_GreekGarden    = 10002
    Window_Cityscape      = 10003
    Window_WildWest       = 10004
    Window_UnderTheSea    = 10005
    Window_TropicalIsland = 10006
    Window_StarryNight    = 10007
    Window_TikiPool       = 10008
    Window_FrozenFrontier = 10009
    Window_FarmCountry    = 10010
    Window_MainStreet     = 10011

    ### Sky Projectors ###
    SkyProjector_Blue = 10500
    SkyProjector_Cloudy = 10501
    SkyProjector_Night = 10502
    SkyProjector_Pink = 10503
    SkyProjector_Purple = 10504

    ### Doorways ###
    Doorway_DoubleRound = 21000
    Doorway_SellbotHQ = 21001

    # Houses (fancy doorways)
    House_Default = 22000  # Reserved for if we make a new default house

    House_Default_Classic = 22100
    House_Cabin_Classic = 22101
    # Doorway_House_Cupcake_Classic = 22102
    # Doorway_House_Castle_Classic = 22103
    # Doorway_House_Hut_Classic = 22104
    House_Yott_1 = 25000
    House_Yott_2 = 25001
    House_Yott_3 = 25002
    House_SkyClan_WatchTower = 26000
    House_SkyClan_WorkShop = 26001
    House_SkyClan_RepairShop = 26002
    House_SkyClan_Hangar = 26003
    House_SkyClan_FabricWorker = 26004
    House_SkyClan_Hall = 26005

    # Thematic Furniture #
    # region
    # Classic (default): 30000 - 30500
    Prop_Classic_GagFan = 30000
    Prop_Classic_Bed = 30001
    Prop_Classic_Couch = 30002
    Prop_Classic_Chair_Regal = 30003
    Prop_Classic_Chair_Dining = 30004
    Prop_Classic_Chair_Desk = 30005
    Prop_Classic_UmbrellaStand = 30006
    Prop_Classic_CoatRack = 30007
    Prop_Classic_TrashCan = 30008
    Prop_Classic_Lamp_Short = 30009
    Prop_Classic_Lamp_Tall = 30010
    Prop_Classic_Bed_Trolley = 30011
    Prop_Classic_TV = 30012
    Prop_Classic_Fireplace_Square = 30013
    Prop_Classic_Fireplace_Round = 30014
    Prop_Classic_Bed_Bathtub = 30015
    Prop_Classic_Piano = 30016
    Prop_Classic_Organ = 30017
    Prop_Classic_PopcornCart = 30018
    Prop_Classic_DisplayCabinet_Red = 30019
    Prop_Classic_DisplayCabinet_Yellow = 30020
    Prop_Classic_Bookcase_Tall = 30031
    Prop_Classic_Bookcase_Low = 30032
    Prop_Classic_Table_Coffee = 30033
    Prop_Classic_Table_Coffee_Red = 30034  # Texture
    Prop_Classic_Radio_A_Green = 30035
    Prop_Classic_Radio_B_Red = 30036
    Prop_Classic_Radio_C_Brown = 30037
    Prop_Classic_Chair_Cushioned = 30038
    Prop_Classic_Table_Bedroom = 30039
    Prop_Classic_Rug_Small = 30040
    Prop_Classic_Rug_Large = 30041
    Prop_Classic_Rug_Round = 30042
    Prop_Classic_Table_End = 30043
    Prop_Classic_Table_Small = 30044
    Prop_Classic_Desk = 30045
    Prop_Classic_Lamp_Table = 30046
    # Prop_Lamp_Table_Colorable = 30047
    Prop_Classic_Candle = 30048  #  note: will probably truncate candle and lit candle
    Prop_Classic_Candle_Lit = 30049
    Wall_Painting_CezanneToon = 30050
    Wall_Painting_Densunes = 30051
    Wall_Painting_Koza = 30052
    Wall_Painting_RembrantToon = 30053
    Wall_Painting_Toonscape = 30054
    Wall_Painting_Mechanicalhandz = 30055
    Wall_Painting_Mollyversus = 30056
    Wall_Painting_NotaPie = 30057
    Wall_Painting_Jacky = 30058
    Prop_Classic_Vase_Short_A = 30059
    Prop_Classic_Vase_Tall_A = 30060
    Prop_Classic_Vase_Short_B = 30061
    Prop_Classic_Vase_Tall_B = 30062
    Prop_Classic_Vase_Short_C = 30063
    Prop_Classic_Vase_Short_D = 30064
    Prop_Classic_InflatableTube = 90016
    Prop_Classic_DummyCog = 90017
    Prop_Classic_Dancefloor = 90015
    Prop_Classic_Garden_Wheelbarrow = 90023
    Prop_Classic_Trampoline = 90008
    Prop_Classic_Jukebox = 90002
    Prop_Classic_Wardrobe_Cool = 90011
    Prop_Classic_Wardrobe_Cute = 90012
    Prop_Classic_Trunk_Cool = 90013
    Prop_Classic_Trunk_Cute = 90014
    Prop_Classic_Mailbox = 90015


    ## Candy: 30500 - 30100
    Prop_Candy_Chair_Cupcake = 30500
    Prop_Candy_Bed_Icecream = 30501
    Prop_Candy_Fireplace_CaramelApple = 30502
    Prop_Candy_Couch_Twinkie = 30503
    Prop_Candy_Table_Cookie = 30504
    Prop_Candy_SwingSet = 30505
    Prop_Candy_CakeSlide = 30506
    Prop_Candy_BananaSplitTub = 30507
    Prop_Candy_SundaeChest = 30508

    # Underwater - 31000
    Prop_UW_Chair_Lobster = 31000
    Prop_UW_Chair_Lifejacket = 31001
    Prop_UW_Bed_Boat = 31002
    Prop_UW_Lamp_Jellyfish_Blue = 31003
    Prop_UW_Lamp_Jellyfish_Orange = 31004
    Prop_UW_CoralVase = 31005
    Prop_UW_ShellVase = 31006
    Prop_UW_Fireplace_Coral = 31007
    Wall_UW_Swordfish = 31008
    Wall_UW_Hammerhead = 31009
    Prop_UW_Statue_Fountain = 31010
    Prop_UW_WashingMachine = 31011
    Prop_UW_Table_Snorkel = 31012
    Prop_UW_Coatrack_Coral = 31013

    # Western - 31500
    Prop_Western_SaddleStool = 31500
    Prop_Western_Chair_Woven = 31501
    Prop_Western_Bed_CactusHammock = 31502
    Prop_Western_Couch_Hay = 31503
    Prop_Western_Lamp_Cowboy = 31504
    Wall_Western_HangingHorns = 31505
    Wall_Western_Sombrero_Simple = 31506
    Wall_Western_Sombrero_Fancy = 31507
    Wall_Western_Poster_Stars = 31508
    Wall_Western_Horseshoe = 31509
    Wall_Western_Portrait_Bison = 31510
    Prop_Western_BarrelStand = 31511
    Prop_Western_Plant_Cactus = 31512
    Prop_Western_Tent_Explorer = 31513
    Prop_Western_FishBowl_Skull = 31514
    Prop_Western_FishBowl_Lizard = 31515

    # Bug: 32000 - 32500
    Prop_Bug_Chair_Log = 32000
    Prop_Bug_Bed_Leaf = 32501
    Prop_Bug_Fireplace = 32502
    Prop_Bug_Lamp_Sunflower = 32503
    Prop_Bug_Lamp_Lilac = 32504
    Prop_Bug_TV = 32505
    Prop_Bug_Mushroom_Red = 32506
    Prop_Bug_Mushroom_Yellow = 32507
    Prop_Bug_Rug_LeafMat = 32508
    Prop_Bug_Desk_Log = 32509
    Prop_Bug_Ladybug = 32510

    # Princess/Fantasy: 32500 - 40000
    Prop_Fantasy_Bed = 32500
    Prop_Fantasy_Fireplace = 32501

    ### Holidays - 40000 to 47000 ###
    # region
    # Minor Q1: 40000
    ## Valentoons: 40500
    Prop_Val_Vase_Rose = 40500
    Prop_Val_Watercan_Rose = 40501
    Wall_Val_Painting_RoseSRRedd = 40502
    # Minor Q2 - 41000
    # Minor Q3 - 42000
    # Minor Q4 - 43000
    # April Toons - 44000

    # Halloween: 45000
    ## Pumpkins: 45000 - 45100
    # we will probably have to add in a new pumpkin entry for each year/variation
    Prop_HW_Pumpkin_Classic_Short = 45000
    Prop_HW_Pumpkin_Classic_Tall = 45001
    Wall_HW_Painting_AutographedErclaim = 45101
    Wall_HW_Painting_ChupDelight = 45102

    # Count Erclaim Area (Lobby is candlegame cdg)
    Wall_HW_Cerc_Lobby_Candle = 45200
    Wall_HW_Cerc_Lobby_Pipes_1 = 45201
    Wall_HW_Cerc_Lobby_Pipes_2 = 45202
    Wall_HW_Cerc_Lobby_Pipes_3 = 45203
    Wall_HW_Cerc_Lobby_Pipes_4 = 45204
    Wall_HW_Cerc_Lobby_Pipes_5 = 45205
    Wall_HW_Cerc_Lobby_Pipes_6 = 45206
    Wall_HW_Cerc_Lobby_Pipes_7 = 45207
    Wall_HW_Cerc_Lobby_Pipes_8 = 45208
    Wall_HW_Cerc_Lobby_Pipes_9 = 45209
    Wall_HW_Cerc_Lobby_Light = 25210
    Wall_HW_Cerc_Lobby_Fusebox = 25211
    Prop_HW_Cerc_Office_Chair = 45250
    Prop_HW_Cerc_Office_Desk = 45251
    Prop_HW_Cerc_Office_DeadTree = 45252
    Prop_HW_Cerc_Office_Bookshelf = 45253
    Prop_HW_Cerc_Office_InkPen = 45254

    # Winter - 46000
    Prop_Win_Presents_Stack = 46000
    Prop_Win_Sled = 46001  # (might be relocated) #
    Prop_Win_Tree_1 = 46002
    Wall_Win_Wreath = 46003
    # endregion
    # endregion

    # Toontown Central: 50000 - 52000
    # region

    # General
    Prop_TTC_BigPlanter = 50002
    Prop_TTC_StopSign = 50003
    Prop_TTC_CautionSign = 50004
    Prop_TTC_Gazebo = 50005
    Prop_TTC_Statue_Fountain = 50006
    Prop_TTC_Lamp_1 = 50007
    Prop_TTC_Lamp_2 = 50008
    Prop_TTC_Lamp_3 = 50009
    Prop_TTC_Mailbox = 50010
    Prop_TTC_Mailbox_Anim = 50011
    Prop_TTC_Mailbox_Hydrant_Anim = 50012
    Prop_TTC_Mailbox_Trashcan_Anim = 50013
    Prop_TTC_Statue_Horse = 50014

    ## Schoolhouse: 51000 - 51500
    # region
    # Classroom: 51000 - 51100
    Prop_Schoolhouse_Classroom_Canvas = 51000
    Prop_Schoolhouse_Classroom_Desk_Student = 51001
    Prop_Schoolhouse_Classroom_Shelf_1 = 51002  # Empty shelf
    Prop_Schoolhouse_Classroom_Shelf_2 = 51003  # Shelf with unmodifiable stuff
    Prop_Schoolhouse_Classroom_PencilCase_1 = 51004
    Wall_Schoolhouse_Classroom_Clock = 51005
    Prop_Schoolhouse_Classroom_Desk_Side = 51006
    Prop_Schoolhouse_Classroom_Bench_1 = 51007
    Prop_Schoolhouse_Classroom_Lockers_1 = 51008
    Prop_Schoolhouse_Classroom_Binder_1 = 51009
    Prop_Schoolhouse_Classroom_Rug = 51010

    # Training Room: 51100 - 51200
    Prop_Schoolhouse_Training_Bench = 51100
    Prop_Schoolhouse_Training_Watercooler = 51101
    Prop_Schoolhouse_Training_GagBarrel = 51102
    Prop_Schoolhouse_Training_Weights = 51103
    Prop_Schoolhouse_Training_PunchingBag_1 = 51104
    Prop_Schoolhouse_Training_Rug = 51105

    # Basement Room: 51200 - 51300
    Prop_Schoolhouse_Basement_Chair_1 = 51200
    Prop_Schoolhouse_Basement_Chair_2 = 51201  # Teacher chair?
    Prop_Schoolhouse_Basement_Desk_1 = 51202
    Prop_Schoolhouse_Basement_Bookstack_1 = 51203
    Wall_Schoolhouse_Basement_Clock_1 = 51204
    Wall_Schoolhouse_Basement_Chalkboard_1 = 51205
    Prop_Schoolhouse_Basement_Bookcase_1 = 51206
    Wall_Schoolhouse_Basement_Frame_1 = 51207
    Prop_Schoolhouse_Basement_Trashcan_1 = 51208

    # Misc: 51300 - 51500

    # endregion

    ## Toonhall: 51500 - 51600
    Prop_ToonHall_Chair_Space = 51500
    Prop_ToonHall_Desk_Lamp_Space = 51501
    Prop_ToonHall_Lamp_Space = 51502
    Prop_ToonHall_Sofa_Space = 51503
    Prop_ToonHall_Desk_Curved = 51504
    Prop_ToonHall_Chalkboard = 51505
    Wall_ToonHall_Bookshelf = 51506
    Prop_ToonHall_FlippyPortrait = 51507
    Prop_ToonHall_Pillar_Int = 51508
    Prop_ToonHall_Display_Anvil = 51509
    Prop_ToonHall_Display_BananaPeel = 51510
    Prop_ToonHall_Display_BikeHorn = 51511
    Prop_ToonHall_Display_CreamPie = 51512
    Prop_ToonHall_Display_LipStick = 51513
    Prop_ToonHall_Display_Magnet = 51514
    Prop_ToonHall_Display_TNT = 51515
    Prop_ToonHall_Display_WaterGlass = 51516

    ## Gagsoline: 51600 - 51700
    Prop_Gagsoline_Lobby_Chair = 51600
    Prop_Gagsoline_Lobby_Couch = 51601
    Prop_Gagsoline_Lobby_Lamp = 51602
    Wall_Gagsoline_Lobby_Clock = 51603
    Prop_Gagsoline_Office_Chair = 51650
    Prop_Gagsoline_Office_Phone = 51651
    Prop_Gagsoline_Office_Lamp = 51652
    Prop_Gagsoline_Office_Desk = 51653
    Prop_Gagsoline_Office_FileCabinet_1 = 51654
    Prop_Gagsoline_Office_FileCabinet_2 = 51655
    Prop_Gagsoline_Office_FileCabinet_3 = 51656

    # endregion

    # Barnacle Boatyard - 52000
    Prop_BB_PalmTreeFlat = 52000
    Prop_BB_Streetlight = 52001
    Prop_BB_Trashcan = 52002
    Prop_BB_Trashcan_Anim = 52003
    Prop_BB_Mailbox = 52004
    Prop_BB_Mailbox_Anim = 52005
    Prop_BB_PalmTree_1_Full = 52006
    Prop_BB_Crate_1 = 52007
    Prop_BB_Barrel_Small_1 = 52008
    Prop_BB_Boat_1 = 52009

    # Ye Olde Toontowne - 54000
    Prop_YOTT_Barrel_Ext = 54000
    Prop_YOTT_Barrel_Plant = 54001
    Prop_YOTT_Cart_Ext = 54003
    Prop_YOTT_Logstack_Ext = 54004
    Prop_YOTT_Well = 54005
    Prop_YOTT_Trashcan = 54006
    Prop_YOTT_Hydrant = 54007
    Prop_YOTT_Mailbox = 54008
    Prop_YOTT_Lamp_1 = 54009
    Prop_YOTT_Lamp_2 = 54010
    Prop_YOTT_Lamp_3 = 54011
    # Not used but wanting to put them here to see how it resonates
    Doorway_YOTT_House_1 = 54012
    Doorway_YOTT_House_2 = 54013
    Doorway_YOTT_House_3 = 54014

    # Daffodil Gardens - 56000
    Prop_DG_DaisyTable = 56000
    Prop_DG_Flowerbed_Pink = 56001
    Prop_DG_Flowerbed_Yellow = 56002
    Prop_DG_Gazebo = 56003
    Prop_DG_Fountain = 56004
    Prop_DG_Hydrant_Anim = 56005
    Prop_DG_Mailbox_Anim = 56006
    Prop_DG_Trashcan_Anim = 56007
    Prop_DG_Flowerbed_Round = 56008

    # Mezzo Melodyland - 58000
    Prop_Trampoline_MML = 58000
    Prop_MML_CrashedPiano = 58001
    Prop_MML_Drum = 58002
    Prop_MML_Planter = 58003
    Prop_MML_Hydrant_Anim = 58004
    Prop_MML_Mailbox = 58005
    Prop_MML_Mailbox_Anim = 58006
    Prop_MML_Trashcan = 58007
    Prop_MML_Trashcan_Anim = 58008
    Prop_MML_Streetlight_1 = 58009

    # Theater - 59000
    Prop_Theater_Lobby_Lamp = 59000
    Prop_Theater_Lobby_Sofa = 59001
    Prop_Theater_Lobby_Table = 59002
    Prop_Theater_Lobby_TicketCounter = 59003
    Ceiling_Theater_Lobby_Light = 59004

    Prop_Theater_Auditorium_StagePiece = 59050
    Wall_Theater_Auditorium_Light = 59051

    # The Brrrgh - 60000
    Prop_TB_Hydrant = 60000
    Prop_TB_Mailbox = 60001
    Prop_TB_Trashcan = 60002
    Prop_TB_Icecube = 60003
    Prop_TB_PotbellyStove = 60004
    Prop_TB_SnowPile = 60005
    Prop_TB_NorthPole = 60006
    Prop_TB_Hydrant_Anim = 60007
    Prop_TB_Mailbox_Anim = 60008
    Prop_TB_Trashcan_Anim = 60009

    # Pizzeria - 61000
    Prop_MozPizza_Lobby_CashRegister = 61000
    Prop_MozPizza_Lobby_Table_Square = 61001
    Prop_MozPizza_Lobby_Table_Round = 61002
    Prop_MozPizza_Lobby_Guestbook = 61003
    Prop_MozPizza_Lobby_PopsicleTray = 61004
    Wall_MozPizza_Lobby_FanUnit = 61005
    Prop_MozPizza_Lobby_Furnace_Frozen = 61006
    Ceiling_MozPizza_Lobby_Lamp = 61007
    Wall_MozPizza_Lobby_Lamp = 61008
    Prop_MozPizza_Lobby_Dispenser = 61009
    Prop_MozPizza_Lobby_CardboardBox = 61010
    Wall_MozPizza_Lobby_Dispenser_Cones = 61011
    Prop_MozPizza_Lobby_Machine_Cola = 61012
    Prop_MozPizza_Lobby_Machine_Popsicles = 61013
    Wall_MozPizza_Lobby_Pipe_End = 61014
    Prop_MozPizza_Lobby_Bag_Dough = 61015
    Prop_MozPizza_Lobby_Shelf_Rack = 61016
    Prop_MozPizza_Lobby_Booth_Seats = 61017
    Prop_MozPizza_Lobby_Gazebo_Entrance = 61018

    # Acorn Acres: 62000 - 64000
    Prop_AA_Hydrant = 62000
    Prop_AA_Mailbox = 62001
    Prop_AA_Trashcan = 62002
    Prop_AA_Lamp_1 = 62003
    Prop_AA_Lamp_2 = 62004

    # Drowsy Dreamland - 64000 - 66000
    Prop_DDL_Clouds_1 = 64000
    Prop_DDL_Hydrant = 64001
    Prop_DDL_Hydrant_Anim = 64002
    Prop_DDL_Mailbox = 64003
    Prop_DDL_Mailbox_Anim = 64004
    Prop_DDL_Trashcan = 64005
    Prop_DDL_Trashcan_Anim = 64006
    Prop_DDL_Tree_1 = 64007
    
    # Fassuite: 65000 - 65500
    Prop_Fassuite_Bell = 65000
    Prop_Fassuite_Bench_Wood = 65001
    Prop_Fassuite_Desk_Curved = 65002
    Wall_Fassuite_Speaker = 65003
    Prop_Fassuite_Speaker_Small = 65004
    Prop_Fassuite_Speaker_Tall = 65005
    Prop_Fassuite_Speaker_Skinny = 65006
    Prop_Fassuite_Speaker_Med = 65007
    Prop_Fassuite_Speaker_Amp = 65008
    Prop_Fassuite_Table_Round_Small = 65009
    Prop_Fassuite_Table_Round_Large = 65010
    Prop_Fassuite_Sofa_Curved_45 = 65011
    Prop_Fassuite_Sofa_Curved_180 = 65012
    Prop_Fassuite_Sign_PaceCorner = 65013
    Prop_Fassuite_Sign_Desk = 65014
    Prop_Fassuite_Weight_Barbell = 65015
    Prop_Fassuite_Weight_Circles = 65016
    Prop_Fassuite_Weight_Stand_Mini = 65017
    Prop_Fassuite_Ropes = 65018
    Wall_Fassuite_Sweatband = 65019
    Wall_Fassuite_Vinyl = 65020
    Prop_Fassuite_Lamp_Lava = 65021
    Ceiling_Fassuite_Lights_1 = 65022
    Ceiling_Fassuite_Lights_2 = 65023
    Wall_Fassuite_Lights_Neon_Circle = 65024
    Wall_Fassuite_Lights_Neon_Strip = 65025
    Prop_Fassuite_Fountain = 65026
    Ceiling_Fassuite_Spotlights_1 = 65027
    Wall_Fassuite_Lights_Neon_Strip_Desat = 65028


    # Minigame Area (GZ/RR): 66000 - 68000
    Prop_RR_Crate = 66500
    Prop_RR_BigTires = 66501
    Prop_RR_WrenchJack = 66502
    Prop_RR_Mailbox = 66503
    Prop_RR_Lamppost = 66504
    Prop_RR_Announcer = 66505
    Prop_RR_Cone = 66506
    Prop_RR_LeaderboardSign = 66507

    # Trolley Stuff - 67000
    Prop_MG_Cannon_Tower = 67000
    Ceiling_MG_Vine = 67001
    Prop_MG_Slingshot_Trampoline = 67002
    Prop_MG_Cannon_Hill = 67003

    # Sky Clan - 68000

    # 69000: Sellbot
    ## Sellbot HQ General: 69000 - 60200
    Prop_Sellbot_Crate_1 = 69000
    # 70000: Cashbot
    ## Cashbot HQ General: 70000 - 70200
    Prop_Cashbot_Safe_1 = 70000
    Prop_Cashbot_CashRegister_1 = 70001
    Prop_Cashbot_Crate_1 = 70002
    Prop_Cashbot_Crate_2 = 70003
    Prop_Cashbot_GoldBar_Single = 70004
    Prop_Cashbot_GoldBar_Stack = 70005
    Prop_Cashbot_MoneyBag_Single = 70006
    Prop_Cashbot_Money_Single = 70007
    Prop_Cashbot_Money_Stack = 70008
    Ceiling_Cashbot_TrainSignal = 70009
    Prop_Cashbot_Column_Vault = 70010

    # 72000: Lawbot
    ## Lawbot HQ General: 72000 - 72200
    Wall_Lawbot_Insignia = 72000
    Prop_Lawbot_Couch_1 = 72001
    Prop_Lawbot_Couch_2 = 72002
    Prop_Lawbot_Couch_3 = 72003
    Prop_Lawbot_Desk_1 = 72004  # unsued
    Prop_Lawbot_Desk_2 = 72005
    Prop_Lawbot_Desk_3 = 72006
    Prop_Lawbot_Plant_Fern = 72007
    Prop_Lawbot_Crate_1 = 72008
    Prop_Lawbot_Crate_2 = 72009
    Prop_Lawbot_Paper_Stack_1 = 72010
    Prop_Lawbot_Bookshelf_1 = 72011
    Prop_Lawbot_Bookshelf_2 = 72012
    Prop_Lawbot_Cabinet_1 = 72013
    Prop_Lawbot_Cabinet_2 = 72014
    Prop_Lawbot_Vacuum_Pipes = 72015
    Prop_Lawbot_Lamp_Tall_1 = 72016
    Prop_Lawbot_Lamp_Desk_1 = 72017
    Prop_Lawbot_Armchair_1 = 72018
    Prop_Lawbot_Armchair_2 = 72019  # reserved for og
    Prop_Lawbot_Armchair_3 = 72020

    # 84000: Bossbot

    # 86000: Boardbot <Or general cog stuff>

    # Uncategorized Props
    Prop_Cannon_Interactive = 90001
    Prop_Tree_Oak_Med_1 = 90003
    Prop_Tree_Oak_Med_2 = 90004
    Prop_Tree_Oak_Med_3 = 90005
    Prop_Tree_Oak_Dark_1 = 90006
    Prop_Tree_Oak_Light_1 = 90007
    Prop_Construction_Suit = 90009
    Prop_Construction_Toon = 90010
    Prop_PicnicTable = 90018
    Prop_ToonStatue = 90019
    Prop_Weather_Rain = 90020
    Prop_Weather_Snow = 90021
    Prop_Fireworks = 90022
    Prop_Pier_Fishing = 90024


@defineItemSubtypeEnum(ItemType.Estate_Style)
class EstateStyleItemType(IntEnum):
    """
    Item subtype enum for estate styles.
    """

    # 0 - 9999 = reserved for debug
    Debug_Test_Area_1 = 100
    Debug_Terrain_150x150_Flat = 200
    Debug_Terrain_150x150_Uneven = 201
    Debug_Terrain_300x300_Flat = 210
    Debug_Terrain_300x300_Uneven = 211

    Debug_TT_Flatgrass_1 = 1000
    Debug_Funny_Rural = 1001
    Debug_RuralTrack_1 = 1002
    Debug_RuralTrack_2 = 1003

    # 1100 - debug sellbot
    Debug_SellbotFactory = 1100
    # 1200 - cashbot
    # 1300 - debug lawbot
    Debug_CLOBossRoom = 1300
    Debug_OCLOLobby = 1301
    Debug_Lawfice = 1310
    Debug_Lawfice_Lobby = 1311
    # 1400 - debug bossbot
    Debug_BanquetInterior = 1400
    Debug_CEOLobby = 1401

    Debug_TrainStation = 1402

    # 1k = nonspecific generic
    Interior_Default = 10000
    Interior_Classic = 10001
    # 2k - specific generic (pg)
    Exterior_YOTT_Playground = 20000
    Exterior_AA_Playground = 20001
    Exterior_TB_Playground = 20002
    Exterior_DG_TagGame = 20003

    # 3k - drops
    Interior_FAASSuite_Lobby = 30001
    # 4k - special

    # 5k = nonspecific generic
    Exterior_Default = 50000
    Exterior_Classic = 50001
    Exterior_AA_Park = 50002


@defineItemSubtypeEnum(ItemType.Estate_Texture)
class EstateTextureItemType(IntEnum):
    """
    An item type for estate textures.
    """
    pass


@defineItemSubtypeEnum(ItemType.Estate_Ticket)
class EstateTicketItemType(IntEnum):
    """
    An item type for estate tickets.
    """
    Generic_Ticket = 1


"""Consumable Item Types"""


@defineItemSubtypeEnum(ItemType.Consumable_Boosters)
class BoosterItemType(IntEnum):
    """
    Item subtype enum for boosters.
    """
    Jellybeans_Global = 14
    Jellybeans_Bingo  = 24

    Gumballs_Global = 17

    Exp_Gags_Global  = 12
    Exp_Gags_Support = 50
    Exp_Gags_Power   = 51

    Exp_Activity_Global  = 11
    Exp_Activity_Racing  = 20
    Exp_Activity_Trolley = 21
    Exp_Activity_Golf    = 22
    Exp_Activity_Fishing = 23

    Fish_Rarity = 8

    Merit_Global   = 16
    Merit_Sellbot  = 3
    Merit_Cashbot  = 4
    Merit_Lawbot   = 5
    Merit_Bossbot  = 6
    Merit_Boardbot = 7

    Exp_Dept_Global   = 9
    Exp_Dept_Sellbot  = 30
    Exp_Dept_Cashbot  = 31
    Exp_Dept_Lawbot   = 32
    Exp_Dept_Bossbot  = 33
    Exp_Dept_Boardbot = 34

    Reward_Boss_Global   = 13
    Reward_Boss_Sellbot  = 40
    Reward_Boss_Cashbot  = 41
    Reward_Boss_Lawbot   = 42
    Reward_Boss_Bossbot  = 43
    Reward_Boss_Boardbot = 44

    AllStar = 60
    Random  = 70

    Reward_Boss_Sellbot_Double = 80


"""Misc Item Types"""


@defineItemSubtypeEnum(ItemType.Material)
class MaterialItemType(IntEnum):
    """
    Item subtype enum for currencies.
    """
    Jellybeans = 1
    Gumballs = 2
    Batcoin = 3

    Counterfeits = 11
    CeaseAndDesists = 12
    PinkSlips = 13


@defineItemSubtypeEnum(ItemType.IOU)
class IOUItemType(IntEnum):
    """
    Item subtype enum for IOUs.
    """
    # Toon-up
    ToonUpThreeStar = 1
    ToonUpFourStar  = 2
    ToonUpFiveStar  = 3
    # Trap
    TrapThreeStar = 11
    TrapFourStar  = 12
    TrapFiveStar  = 13
    # Lure
    LureThreeStar = 21
    LureFourStar  = 22
    LureFiveStar  = 23
    # Throw
    ThrowThreeStar              = 31
    ThrowFourStar               = 32
    ThrowFiveStar               = 33
    ThrowThreeStar_Unobtainable = 34
    # Squirt
    SquirtThreeStar = 41
    SquirtFourStar  = 42
    SquirtFiveStar  = 43
    # Zap
    ZapThreeStar = 51
    ZapFourStar  = 52
    ZapFiveStar  = 53
    # Sound
    SoundThreeStar = 61
    SoundFourStar  = 62
    SoundFiveStar  = 63
    # Drop
    DropThreeStar = 71
    DropFourStar  = 72
    DropFiveStar  = 73
    # Misc
    AllBoost = 81


@defineItemSubtypeEnum(ItemType.Unite)
class UniteItemType(IntEnum):
    """
    Item subtype enum for Unites.
    """
    ToonUpLow = 1
    ToonUpMid = 2
    ToonUpHigh = 3


@defineItemSubtypeEnum(ItemType.Music_Disc)
class MusicDiscItemType(IntEnum):
    """
    Item subtype enum for music discs.
    """
    # Instance mercs
    Merc_Prethinker_1 = 1
    Merc_Prethinker_2 = 2
    Merc_Rainmaker_1 = 3
    Merc_Rainmaker_2 = 4
    Merc_Rainmaker_3 = 5
    Merc_Rainmaker_4 = 6
    Merc_Rainmaker_5 = 7
    Merc_Rainmaker_6 = 8
    Merc_Rainmaker_7 = 9
    Merc_WitchHunter_1 = 10
    Merc_WitchHunter_2 = 11
    Merc_WitchHunter_3 = 12
    Merc_Multislacker_1 = 13
    Merc_Multislacker_2 = 14
    Merc_MajorPlayer_1 = 15
    Merc_MajorPlayer_2 = 16
    Merc_Plutocrat_1 = 17
    Merc_Plutocrat_2 = 18
    Merc_Plutocrat_3 = 19
    Merc_ChainsawConsultant_1 = 20
    Merc_ChainsawConsultant_2 = 21
    Merc_ChainsawConsultant_3 = 22
    Merc_Pacesetter_1 = 23
    Merc_Pacesetter_2 = 24

    Merc_Street_DuckShuffler = 25
    Merc_Street_DeepDiver = 26
    Merc_Street_Gatekeeper = 27
    Merc_Street_Bellringer = 28
    Merc_Street_Mouthpiece = 29
    Merc_Street_Firestarter = 30
    Merc_Street_Treekiller = 31
    Merc_Street_Featherbedder = 32
