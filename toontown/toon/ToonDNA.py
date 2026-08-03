from direct.directnotify.DirectNotifyGlobal import *
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from panda3d.core import *
from panda3d.direct import *
import ast, colorsys, hashlib, json, os, random
from otp.avatar import AvatarDNA

notify = directNotify.newCategory('ToonDNA')
mergeMATTailor = config.GetBool('want-mat-all-tailors', 0)
toonSpeciesTypes = ['d',    # Dog
                    'c',    # Cat
                    'h',    # Horse
                    'm',    # Mouse
                    'r',    # Rabbit
                    'f',    # Duck
                    'p',    # Monkey
                    'b',    # Bear
                    's',    # Pig (swine)
                    'x',    # Deer
                    'z',    # Beaver
                    'a',    # Alligator
                    'v',    # Fox
                    'n',    # Bat
                    't',
                    'g',  # Turkey
                    'e',  # Koala
                    'j',  # Kangaroo
                    'k',  # Kiwi
                    'l',
                    # Raccoon
                    ]
toonHeadTypes = [ "dls", "dss", "dsl", "dll",  # Dog
                  "cls", "css", "csl", "cll",  # Cat
                  "hls", "hss", "hsl", "hll",  # Horse
                  "mls", "mss", "msl", "mll",  # Mouse
                  "rls", "rss", "rsl", "rll",  # Rabbit
                  "fls", "fss", "fsl", "fll",  # Duck (Fowl)
                  "pls", "pss", "psl", "pll",  # Monkey (Primate)
                  "bls", "bss", "bsl", "bll",  # Bear
                  "sls", "sss", "ssl", "sll",  # Pig (swine)
                  "xls", "xss", "xsl", "xll",  # Deer
                  "zls", "zss", "zsl", "zll",  # Beaver
                  "als", "ass", "asl", "all",  # Alligator
                  "vls", "vss", "vsl", "vll",  # Fox
                  "nls", "nss", "nsl", "nll",  # Bat
                  "tls", "tss", "tsl", "tll",
                  "gls", "gss", "gsl", "gll",  # Turkey
                  "els", "ess", "esl", "ell",  # Koala
                  "jls", "jss", "jsl", "jll",  # Kangaroo
                  "kls", "kss", "ksl", "kll",  # Kiwi
                  "lls", "lss", "lsl", "lll",
                  # Raccoon
]

def getHeadList(species):
    headList = []
    for head in toonHeadTypes:
        if head[0] == species:
            headList.append(head)

    return headList


def getHeadStartIndex(species):
    for head in toonHeadTypes:
        if head[0] == species:
            return toonHeadTypes.index(head)


def getSpecies(head):
    for species in toonSpeciesTypes:
        if species == head[0]:
            return species


def getSpeciesName(head):
    species = getSpecies(head)
    if species == 'd':
        speciesName = 'dog'
    elif species == 'c':
        speciesName = 'cat'
    elif species == 'h':
        speciesName = 'horse'
    elif species == 'm':
        speciesName = 'mouse'
    elif species == 'r':
        speciesName = 'rabbit'
    elif species == 'f':
        speciesName = 'duck'
    elif species == 'p':
        speciesName = 'monkey'
    elif species == 'b':
        speciesName = 'bear'
    elif species == 's':
        speciesName = 'pig'
    elif species == 'x':
        speciesName = 'deer'
    elif species == 'z':
        speciesName = 'beaver'
    elif species == 'a':
        speciesName = 'alligator'
    elif species == 'v':
        speciesName = 'fox'
    elif species == 'n':
        speciesName = 'bat'
    elif species == 't':
        speciesName = 'raccoon'
    elif species == 'g':
        speciesName = 'turkey'
    elif species == 'e':
        speciesName = 'koala'
    elif species == 'j':
        speciesName = 'kangaroo'
    elif species == 'k':
        speciesName = 'kiwi'
    elif species == 'l':
        speciesName = 'armadillo'
    return speciesName


toonHeadAnimalIndices = [ 0, # start of dog heads
                          4, # start of cat heads
                          8, # start of horse heads
                          12, # start of mouse heads
                          16, # start of rabbit heads
                          20, # start of duck heads
                          24, # start of monkey heads
                          28, # start of bear heads
                          32, # start of pig heads
                          36, # start of deer heads
                          40, # start of beaver heads
                          44, # start of alligator heads
                          48, # start of fox heads
                          52, # start of bat heads
                          56,
                          60,  # start of turkey heads
                          64,  # start of koala heads
                          68,  # start of kangaroo heads
                          72,  # start of kiwi heads
                          76,
                          # start of raccoon heads
                          ]
toonHeadAnimalIndicesTrial = [0,
 4,
 12,
 14,
 18,
 30,
 34]
allToonHeadAnimalIndices = [ 0, 1, 2, 3,     # Dog
                             4, 5, 6, 7,     # Cat
                             8, 9, 10, 11,   # Horse
                             12, 13, 14, 15,   # Mouse
                             16, 17, 18, 19, # Rabbit
                             20, 21, 22, 23, # Duck
                             24, 25, 26, 27, # Monkey
                             28, 29, 30, 31, # Bear
                             32, 33, 34, 35, # Pig
                             36, 37, 38, 39, # Deer
                             40, 41, 42, 43,  # Beaver
                             44, 45, 46, 47, # Alligator
                             48, 49, 50, 51, # Fox
                             52, 53, 54, 55,  # Bat
                             56, 57, 58, 59,
                             60, 61, 62, 63,  # Turkey
                             64, 65, 66, 67,  # Koala
                             68, 69, 70, 71,  # Kangaroo
                             72, 73, 74, 75,  # Kiwi
                             76, 77, 78, 79
                             # Raccoon
                             ]
allToonHeadAnimalIndicesTrial = [0,
 1,
 2,
 3,
 4,
 5,
 6,
 7,
 12,
 13,
 14,
 15,
 16,
 17,
 18,
 19,
 20,
 21,
 30,
 31,
 32,
 33,
 34,
 35,
 36,
 37]
toonTorsoTypes = ['ss',
 'ms',
 'ls',
 'sd',
 'md',
 'ld',
 's',
 'm',
 'l']
toonLegTypes = ['s', 'm', 'l']
Shirts = ['phase_3/maps/desat_shirt_1.png',
 'phase_3/maps/desat_shirt_2.png',
 'phase_3/maps/desat_shirt_3.png',
 'phase_3/maps/desat_shirt_4.png',
 'phase_3/maps/desat_shirt_5.png',
 'phase_3/maps/desat_shirt_6.png',
 'phase_3/maps/desat_shirt_7.png',
 'phase_3/maps/desat_shirt_8.png',
 'phase_3/maps/desat_shirt_9.png',
 'phase_3/maps/desat_shirt_10.png',
 'phase_3/maps/desat_shirt_11.png',
 'phase_3/maps/desat_shirt_12.png',
 'phase_3/maps/desat_shirt_13.png',
 'phase_3/maps/desat_shirt_14.png',
 'phase_3/maps/desat_shirt_15.png',
 'phase_3/maps/desat_shirt_16.png',
 'phase_3/maps/desat_shirt_17.png',
 'phase_3/maps/desat_shirt_18.png',
 'phase_3/maps/desat_shirt_19.png',
 'phase_3/maps/desat_shirt_20.png',
 'phase_3/maps/desat_shirt_21.png',
 'phase_3/maps/desat_shirt_22.png',
 'phase_3/maps/desat_shirt_23.png',
 'phase_4/maps/female_shirt1b.png',
 'phase_4/maps/female_shirt2.png',
 'phase_4/maps/female_shirt3.png',
 'phase_4/maps/male_shirt1.png',
 'phase_4/maps/male_shirt2_palm.png',
 'phase_4/maps/male_shirt3c.png',
 'phase_4/maps/shirt_ghost.png',
 'phase_4/maps/shirt_pumkin.png',
 'phase_4/maps/holiday_shirt1.png',
 'phase_4/maps/holiday_shirt2b.png',
 'phase_4/maps/holidayShirt3b.png',
 'phase_4/maps/holidayShirt4.png',
 'phase_4/maps/female_shirt1b.png',
 'phase_4/maps/female_shirt5New.png',
 'phase_4/maps/shirtMale4B.png',
 'phase_4/maps/shirt6New.png',
 'phase_4/maps/shirtMaleNew7.png',
 'phase_4/maps/femaleShirtNew6.png',
 'phase_4/maps/Vday1Shirt5.png',
 'phase_4/maps/Vday1Shirt6SHD.png',
 'phase_4/maps/Vday1Shirt4.png',
 'phase_4/maps/Vday_shirt2c.png',
 'phase_4/maps/shirtTieDyeNew.png',
 'phase_4/maps/male_shirt1.png',
 'phase_4/maps/StPats_shirt1.png',
 'phase_4/maps/StPats_shirt2.png',
 'phase_4/maps/ContestfishingVestShirt2.png',
 'phase_4/maps/ContestFishtankShirt1.png',
 'phase_4/maps/ContestPawShirt1.png',
 'phase_4/maps/CowboyShirt1.png',
 'phase_4/maps/CowboyShirt2.png',
 'phase_4/maps/CowboyShirt3.png',
 'phase_4/maps/CowboyShirt4.png',
 'phase_4/maps/CowboyShirt5.png',
 'phase_4/maps/CowboyShirt6.png',
 'phase_4/maps/4thJulyShirt1.png',
 'phase_4/maps/4thJulyShirt2.png',
 'phase_4/maps/shirt_Cat7_01.png',
 'phase_4/maps/shirt_Cat7_02.png',
 'phase_4/maps/contest_backpack3.png',
 'phase_4/maps/contest_leder.png',
 'phase_4/maps/contest_mellon2.png',
 'phase_4/maps/contest_race2.png',
 'phase_4/maps/PJBlueBanana2.png',
 'phase_4/maps/PJRedHorn2.png',
 'phase_4/maps/PJGlasses2.png',
 'phase_4/maps/tt_t_chr_avt_shirt_valentine1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_valentine2.png',
 'phase_4/maps/tt_t_chr_avt_shirt_desat4.png',
 'phase_4/maps/tt_t_chr_avt_shirt_fishing1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_fishing2.png',
 'phase_4/maps/tt_t_chr_avt_shirt_gardening1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_gardening2.png',
 'phase_4/maps/tt_t_chr_avt_shirt_party1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_party2.png',
 'phase_4/maps/tt_t_chr_avt_shirt_racing1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_racing2.png',
 'phase_4/maps/tt_t_chr_avt_shirt_summer1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_summer2.png',
 'phase_4/maps/tt_t_chr_avt_shirt_golf1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_golf2.png',
 'phase_4/maps/tt_t_chr_avt_shirt_halloween1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_halloween2.png',
 'phase_4/maps/tt_t_chr_avt_shirt_marathon1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_saveBuilding1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_saveBuilding2.png',
 'phase_4/maps/tt_t_chr_avt_shirt_toonTask1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_toonTask2.png',
 'phase_4/maps/tt_t_chr_avt_shirt_trolley1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_trolley2.png',
 'phase_4/maps/tt_t_chr_avt_shirt_winter1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_halloween3.png',
 'phase_4/maps/tt_t_chr_avt_shirt_halloween4.png',
 'phase_4/maps/tt_t_chr_avt_shirt_valentine3.png',
 'phase_4/maps/tt_t_chr_shirt_scientistC.png',
 'phase_4/maps/tt_t_chr_shirt_scientistA.png',
 'phase_4/maps/tt_t_chr_shirt_scientistB.png',
 'phase_4/maps/tt_t_chr_avt_shirt_mailbox.png',
 'phase_4/maps/tt_t_chr_avt_shirt_trashcan.png',
 'phase_4/maps/tt_t_chr_avt_shirt_loonyLabs.png',
 'phase_4/maps/tt_t_chr_avt_shirt_hydrant.png',
 'phase_4/maps/tt_t_chr_avt_shirt_whistle.png',
 'phase_4/maps/tt_t_chr_avt_shirt_cogbuster.png',
 'phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated01.png',
 'phase_4/maps/tt_t_chr_avt_shirt_victoryParty01.png',
 'phase_4/maps/tt_t_chr_avt_shirt_victoryParty02.png',
 'phase_4/maps/tt_t_chr_avt_shirt_sellbotIcon.png',
 'phase_4/maps/tt_t_chr_avt_shirt_sellbotVPIcon.png',
 'phase_4/maps/tt_t_chr_avt_shirt_sellbotCrusher.png',
 'phase_4/maps/tt_t_chr_avt_shirt_jellyBeans.png',
 'phase_4/maps/tt_t_chr_avt_shirt_doodle.png',
 'phase_4/maps/tt_t_chr_avt_shirt_halloween5.png',
 'phase_4/maps/tt_t_chr_avt_shirt_halloweenTurtle.png',
 'phase_4/maps/tt_t_chr_avt_shirt_greentoon1.png',
 'phase_4/maps/tt_t_chr_avt_shirt_getConnectedMoverShaker.png',
 'phase_4/maps/tt_t_chr_avt_shirt_racingGrandPrix.png',
 'phase_4/maps/tt_t_chr_avt_shirt_bee.png',
 'phase_4/maps/tt_t_chr_avt_shirt_pirate.png',
 'phase_4/maps/tt_t_chr_avt_shirt_supertoon.png',
 'phase_4/maps/tt_t_chr_avt_shirt_vampire.png',
 'phase_4/maps/tt_t_chr_avt_shirt_dinosaur.png',
 'phase_4/maps/tt_t_chr_avt_shirt_fishing04.png',
 'phase_4/maps/tt_t_chr_avt_shirt_golf03.png',
 'phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated02.png',
 'phase_4/maps/tt_t_chr_avt_shirt_racing03.png',
 'phase_4/maps/tt_t_chr_avt_shirt_saveBuilding3.png',
 'phase_4/maps/tt_t_chr_avt_shirt_trolley03.png',
 'phase_4/maps/tt_t_chr_avt_shirt_fishing05.png',
 'phase_4/maps/tt_t_chr_avt_shirt_golf04.png',
 'phase_4/maps/tt_t_chr_avt_shirt_halloween06.png',
 'phase_4/maps/tt_t_chr_avt_shirt_winter03.png',
 'phase_4/maps/tt_t_chr_avt_shirt_halloween07.png',
 'phase_4/maps/tt_t_chr_avt_shirt_winter02.png',
 'phase_4/maps/tt_t_chr_avt_shirt_fishing06.png',
 'phase_4/maps/tt_t_chr_avt_shirt_fishing07.png',
 'phase_4/maps/tt_t_chr_avt_shirt_golf05.png',
 'phase_4/maps/tt_t_chr_avt_shirt_racing04.png',
 'phase_4/maps/tt_t_chr_avt_shirt_racing05.png',
 'phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated03.png',
 'phase_4/maps/tt_t_chr_avt_shirt_mostCogsDefeated04.png',
 'phase_4/maps/tt_t_chr_avt_shirt_trolley04.png',
 'phase_4/maps/tt_t_chr_avt_shirt_trolley05.png',
 'phase_4/maps/tt_t_chr_avt_shirt_saveBuilding4.png',
 'phase_4/maps/tt_t_chr_avt_shirt_saveBuilding05.png',
 'phase_4/maps/tt_t_chr_avt_shirt_anniversary.png',
 'phase_4/maps/i60_shirt.png',
 'phase_4/maps/tt_t_chr_avt_shirt_burger.png',
 'phase_4/maps/winter/2019_outfit/tt_t_chr_avt_shirt_2019_dress.png',
 'phase_4/maps/winter/2019_outfit/tt_t_chr_avt_shirt_2019_suit.png'
 'phase_4/maps/winter/2022_outfit/2022_top.png'
 'phase_4/maps/winter/2023_outfit/2023_top.png'
 'phase_4/maps/winter/2025_outfit/cc_t_clth_shirt_nye_25.png'
'phase_4/maps/social/gumball/tt_t_chr_avt_shirt_cardsF.png',
'phase_4/maps/social/gumball/tt_t_chr_avt_shirt_cards.png',
'phase_4/maps/social/gumball/tt_t_chr_avt_shirt_battlejacket.png',
'phase_4/maps/social/gumball/tt_t_chr_avt_shirt_funky.png',
'phase_13/maps/events/apriltoons/clothing/bored_top.png',
'phase_13/maps/events/apriltoons/clothing/triplerainbow_top.png',
'phase_4/maps/apriltoons/high_roller_outfit/cc_t_clth_shirt_suit_hroller_white.png',
'phase_4/maps/apriltoons/high_roller_outfit/cc_t_clth_shirt_suit_hroller_black.png',
          ]
BoyShirts = [(0, 0),
 (1, 1),
 (2, 2),
 (3, 3),
 (4, 4),
 (5, 5),
 (8, 8),
 (9, 9),
 (10, 0),
 (11, 0),
 (14, 10),
 (16, 0),
 (17, 0),
 (18, 12),
 (19, 13),
 (20, 0),
             (21, 0)
             ]
GirlShirts = [(0, 0),
 (1, 1),
 (2, 2),
 (3, 3),
 (5, 5),
 (6, 6),
 (7, 7),
 (9, 9),
 (12, 0),
 (13, 11),
 (15, 11),
 (16, 0),
 (20, 0),
 (21, 0),
 (22, 0),
 (23, 0),
              (24, 0)
              ]

def isValidBoyShirt(index):
    for pair in BoyShirts:
        if index == pair[0]:
            return 1

    return 0


def isValidGirlShirt(index):
    for pair in GirlShirts:
        if index == pair[0]:
            return 1

    return 0


Sleeves = ['phase_3/maps/desat_sleeve_1.png',
 'phase_3/maps/desat_sleeve_2.png',
 'phase_3/maps/desat_sleeve_3.png',
 'phase_3/maps/desat_sleeve_4.png',
 'phase_3/maps/desat_sleeve_5.png',
 'phase_3/maps/desat_sleeve_6.png',
 'phase_3/maps/desat_sleeve_7.png',
 'phase_3/maps/desat_sleeve_8.png',
 'phase_3/maps/desat_sleeve_9.png',
 'phase_3/maps/desat_sleeve_10.png',
 'phase_3/maps/desat_sleeve_15.png',
 'phase_3/maps/desat_sleeve_16.png',
 'phase_3/maps/desat_sleeve_19.png',
 'phase_3/maps/desat_sleeve_20.png',
 'phase_4/maps/female_sleeve1b.png',
 'phase_4/maps/female_sleeve2.png',
 'phase_4/maps/female_sleeve3.png',
 'phase_4/maps/male_sleeve1.png',
 'phase_4/maps/male_sleeve2_palm.png',
 'phase_4/maps/male_sleeve3c.png',
 'phase_4/maps/shirt_Sleeve_ghost.png',
 'phase_4/maps/shirt_Sleeve_pumkin.png',
 'phase_4/maps/holidaySleeve1.png',
 'phase_4/maps/holidaySleeve3.png',
 'phase_4/maps/female_sleeve1b.png',
 'phase_4/maps/female_sleeve5New.png',
 'phase_4/maps/male_sleeve4New.png',
 'phase_4/maps/sleeve6New.png',
 'phase_4/maps/SleeveMaleNew7.png',
 'phase_4/maps/female_sleeveNew6.png',
 'phase_4/maps/Vday5Sleeve.png',
 'phase_4/maps/Vda6Sleeve.png',
 'phase_4/maps/Vday_shirt4sleeve.png',
 'phase_4/maps/Vday2cSleeve.png',
 'phase_4/maps/sleeveTieDye.png',
 'phase_4/maps/male_sleeve1.png',
 'phase_4/maps/StPats_sleeve.png',
 'phase_4/maps/StPats_sleeve2.png',
 'phase_4/maps/ContestfishingVestSleeve1.png',
 'phase_4/maps/ContestFishtankSleeve1.png',
 'phase_4/maps/ContestPawSleeve1.png',
 'phase_4/maps/CowboySleeve1.png',
 'phase_4/maps/CowboySleeve2.png',
 'phase_4/maps/CowboySleeve3.png',
 'phase_4/maps/CowboySleeve4.png',
 'phase_4/maps/CowboySleeve5.png',
 'phase_4/maps/CowboySleeve6.png',
 'phase_4/maps/4thJulySleeve1.png',
 'phase_4/maps/4thJulySleeve2.png',
 'phase_4/maps/shirt_sleeveCat7_01.png',
 'phase_4/maps/shirt_sleeveCat7_02.png',
 'phase_4/maps/contest_backpack_sleeve.png',
 'phase_4/maps/Contest_leder_sleeve.png',
 'phase_4/maps/contest_mellon_sleeve2.png',
 'phase_4/maps/contest_race_sleeve.png',
 'phase_4/maps/PJSleeveBlue.png',
 'phase_4/maps/PJSleeveRed.png',
 'phase_4/maps/PJSleevePurple.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_valentine1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_valentine2.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_desat4.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing2.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_gardening1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_gardening2.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_party1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_party2.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing2.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_summer1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_summer2.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf2.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween2.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_marathon1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding2.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_toonTask1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_toonTask2.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley2.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_winter1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween3.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween4.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_valentine3.png',
 'phase_4/maps/tt_t_chr_shirtSleeve_scientist.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_mailbox.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_trashcan.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_loonyLabs.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_hydrant.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_whistle.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_cogbuster.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated01.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_victoryParty01.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_victoryParty02.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotIcon.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotVPIcon.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_sellbotCrusher.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_jellyBeans.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_doodle.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween5.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloweenTurtle.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_greentoon1.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_getConnectedMoverShaker.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_racingGrandPrix.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_bee.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_pirate.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_supertoon.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_vampire.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_dinosaur.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing04.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf03.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated02.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing03.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding3.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley03.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing05.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf04.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween06.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_winter03.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_halloween07.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_winter02.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing06.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_fishing07.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_golf05.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing04.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_racing05.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated03.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_mostCogsDefeated04.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley04.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_trolley05.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding4.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_saveBuilding05.png',
 'phase_4/maps/tt_t_chr_avt_shirtSleeve_anniversary.png',
 'phase_4/maps/i60_sleeves.png',
 'phase_4/maps/tt_t_chr_avt_sleeve_burger.png',
 'phase_4/maps/winter/2019_outfit/tt_t_chr_avt_sleeve_2019_suit.png',
 'phase_4/maps/winter/2019_outfit/tt_t_chr_avt_sleeve_2019_dress.png',
           'phase_4/maps/winter/2022_outfit/2022_sleeve.png',
           'phase_4/maps/winter/2023_outfit/2023_sleeve.png',
           'phase_4/maps/winter/2025_outfit/cc_t_clth_shirt_nye_25_sleeve.png',
'phase_4/maps/social/gumball/tt_t_chr_avt_sleeve_cardsF.png',
'phase_4/maps/social/gumball/tt_t_chr_avt_sleeve_cards.png',
'phase_4/maps/social/gumball/tt_t_chr_avt_sleeve_battlejacket.png',
'phase_4/maps/social/gumball/tt_t_chr_avt_sleeve_funky.png',
'phase_13/maps/events/apriltoons/clothing/bored_sleeve.png',
'phase_13/maps/events/apriltoons/clothing/triplerainbow_sleeve.png',
'phase_4/maps/apriltoons/high_roller_outfit/cc_t_clth_shirt_suit_hroller_black_sleeve.png',
'phase_4/maps/apriltoons/high_roller_outfit/cc_t_clth_shirt_suit_hroller_white_sleeve.png',
           ]
BoyShorts = ['phase_3/maps/desat_shorts_1.png',
 'phase_3/maps/desat_shorts_2.png',
 'phase_3/maps/desat_shorts_4.png',
 'phase_3/maps/desat_shorts_6.png',
 'phase_3/maps/desat_shorts_7.png',
 'phase_3/maps/desat_shorts_8.png',
 'phase_3/maps/desat_shorts_9.png',
 'phase_3/maps/desat_shorts_10.png',
 'phase_4/maps/VdayShorts2.png',
 'phase_4/maps/shorts4.png',
 'phase_4/maps/shorts1.png',
 'phase_4/maps/shorts5.png',
 'phase_4/maps/CowboyShorts1.png',
 'phase_4/maps/CowboyShorts2.png',
 'phase_4/maps/4thJulyShorts1.png',
 'phase_4/maps/shortsCat7_01.png',
 'phase_4/maps/Blue_shorts_1.png',
 'phase_4/maps/Red_shorts_1.png',
 'phase_4/maps/Purple_shorts_1.png',
 'phase_4/maps/tt_t_chr_avt_shorts_winter1.png',
 'phase_4/maps/tt_t_chr_avt_shorts_winter2.png',
 'phase_4/maps/tt_t_chr_avt_shorts_winter3.png',
 'phase_4/maps/tt_t_chr_avt_shorts_winter4.png',
 'phase_4/maps/tt_t_chr_avt_shorts_valentine1.png',
 'phase_4/maps/tt_t_chr_avt_shorts_valentine2.png',
 'phase_4/maps/tt_t_chr_avt_shorts_fishing1.png',
 'phase_4/maps/tt_t_chr_avt_shorts_gardening1.png',
 'phase_4/maps/tt_t_chr_avt_shorts_party1.png',
 'phase_4/maps/tt_t_chr_avt_shorts_racing1.png',
 'phase_4/maps/tt_t_chr_avt_shorts_summer1.png',
 'phase_4/maps/tt_t_chr_avt_shorts_golf1.png',
 'phase_4/maps/tt_t_chr_avt_shorts_halloween1.png',
 'phase_4/maps/tt_t_chr_avt_shorts_halloween2.png',
 'phase_4/maps/tt_t_chr_avt_shorts_saveBuilding1.png',
 'phase_4/maps/tt_t_chr_avt_shorts_trolley1.png',
 'phase_4/maps/tt_t_chr_avt_shorts_halloween4.png',
 'phase_4/maps/tt_t_chr_avt_shorts_halloween3.png',
 'phase_4/maps/tt_t_chr_shorts_scientistA.png',
 'phase_4/maps/tt_t_chr_shorts_scientistB.png',
 'phase_4/maps/tt_t_chr_shorts_scientistC.png',
 'phase_4/maps/tt_t_chr_avt_shorts_cogbuster.png',
 'phase_4/maps/tt_t_chr_avt_shorts_sellbotCrusher.png',
 'phase_4/maps/tt_t_chr_avt_shorts_halloween5.png',
 'phase_4/maps/tt_t_chr_avt_shorts_halloweenTurtle.png',
 'phase_4/maps/tt_t_chr_avt_shorts_greentoon1.png',
 'phase_4/maps/tt_t_chr_avt_shorts_racingGrandPrix.png',
 'phase_4/maps/tt_t_chr_avt_shorts_bee.png',
 'phase_4/maps/tt_t_chr_avt_shorts_pirate.png',
 'phase_4/maps/tt_t_chr_avt_shorts_supertoon.png',
 'phase_4/maps/tt_t_chr_avt_shorts_vampire.png',
 'phase_4/maps/tt_t_chr_avt_shorts_dinosaur.png',
 'phase_4/maps/tt_t_chr_avt_shorts_golf03.png',
 'phase_4/maps/tt_t_chr_avt_shorts_racing03.png',
 'phase_4/maps/tt_t_chr_avt_shorts_golf04.png',
 'phase_4/maps/tt_t_chr_avt_shorts_golf05.png',
 'phase_4/maps/tt_t_chr_avt_shorts_racing04.png',
 'phase_4/maps/tt_t_chr_avt_shorts_racing05.png',
 'phase_4/maps/i60_shorts.png',
             'phase_4/maps/winter/2019_outfit/tt_t_chr_avt_shorts_2019_suit.png',
             'phase_4/maps/winter/2022_outfit/2022_bot.png',
'phase_4/maps/winter/2023_outfit/2023_bot.png',
'phase_4/maps/winter/2025_outfit/cc_t_clth_shorts_nye_25.png',
'phase_4/maps/social/gumball/tt_t_chr_avt_shorts_cards.png',
'phase_4/maps/social/gumball/tt_t_chr_avt_shorts_funky.png',
'phase_4/maps/events/apriltoons/clothing/triplerainbow_bot.png',
'phase_4/maps/apriltoons/high_roller_outfit/cc_t_clth_shorts_suit_hroller_black.png',
'phase_4/maps/apriltoons/high_roller_outfit/cc_t_clth_shorts_suit_hroller_white.png',
             ]
SHORTS = 0
SKIRT = 1
GirlBottoms = [('phase_3/maps/desat_skirt_1.png', SKIRT),
 ('phase_3/maps/desat_skirt_2.png', SKIRT),
 ('phase_3/maps/desat_skirt_3.png', SKIRT),
 ('phase_3/maps/desat_skirt_4.png', SKIRT),
 ('phase_3/maps/desat_skirt_5.png', SKIRT),
 ('phase_3/maps/desat_shorts_1.png', SHORTS),
 ('phase_3/maps/desat_shorts_5.png', SHORTS),
 ('phase_3/maps/desat_skirt_6.png', SKIRT),
 ('phase_3/maps/desat_skirt_7.png', SKIRT),
 ('phase_3/maps/desat_shorts_10.png', SHORTS),
 ('phase_4/maps/female_skirt1.png', SKIRT),
 ('phase_4/maps/female_skirt2.png', SKIRT),
 ('phase_4/maps/female_skirt3.png', SKIRT),
 ('phase_4/maps/VdaySkirt1.png', SKIRT),
 ('phase_4/maps/skirtNew5.png', SKIRT),
 ('phase_4/maps/shorts5.png', SHORTS),
 ('phase_4/maps/CowboySkirt1.png', SKIRT),
 ('phase_4/maps/CowboySkirt2.png', SKIRT),
 ('phase_4/maps/4thJulySkirt1.png', SKIRT),
 ('phase_4/maps/skirtCat7_01.png', SKIRT),
 ('phase_4/maps/Blue_shorts_1.png', SHORTS),
 ('phase_4/maps/Red_shorts_1.png', SHORTS),
 ('phase_4/maps/Purple_shorts_1.png', SHORTS),
 ('phase_4/maps/tt_t_chr_avt_skirt_winter1.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_winter2.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_winter3.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_winter4.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_valentine1.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_valentine2.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_fishing1.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_gardening1.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_party1.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_racing1.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_summer1.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_golf1.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_halloween1.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_halloween2.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_saveBuilding1.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_trolley1.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_halloween3.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_halloween4.png', SKIRT),
 ('phase_4/maps/tt_t_chr_shorts_scientistA.png', SHORTS),
 ('phase_4/maps/tt_t_chr_shorts_scientistB.png', SHORTS),
 ('phase_4/maps/tt_t_chr_shorts_scientistC.png', SHORTS),
 ('phase_4/maps/tt_t_chr_avt_shorts_cogbuster.png', SHORTS),
 ('phase_4/maps/tt_t_chr_avt_shorts_sellbotCrusher.png', SHORTS),
 ('phase_4/maps/tt_t_chr_avt_shorts_halloween5.png', SHORTS),
 ('phase_4/maps/tt_t_chr_avt_shorts_halloweenTurtle.png', SHORTS),
 ('phase_4/maps/tt_t_chr_avt_skirt_greentoon1.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_racingGrandPrix.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_shorts_bee.png', SHORTS),
 ('phase_4/maps/tt_t_chr_avt_shorts_pirate.png', SHORTS),
 ('phase_4/maps/tt_t_chr_avt_skirt_pirate.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_shorts_supertoon.png', SHORTS),
 ('phase_4/maps/tt_t_chr_avt_shorts_vampire.png', SHORTS),
 ('phase_4/maps/tt_t_chr_avt_shorts_dinosaur.png', SHORTS),
 ('phase_4/maps/tt_t_chr_avt_skirt_golf02.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_racing03.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_golf03.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_golf04.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_racing04.png', SKIRT),
 ('phase_4/maps/tt_t_chr_avt_skirt_racing05.png', SKIRT),
 ('phase_4/maps/i60_shorts.png', SHORTS),
               ('phase_4/maps/winter/2019_outfit/tt_t_chr_avt_skirt_2019_dress.png', SKIRT),
               ('phase_4/maps/winter/2022_outfit/2022_skirt.png', SKIRT),
               ('phase_4/maps/winter/2023_outfit/2023_skirt.png', SKIRT),
               ('phase_4/maps/winter/2025_outfit/cc_t_clth_skirt_nye_25.png', SKIRT),
               ('phase_4/maps/social/gumball/tt_t_chr_avt_skirt_cards.png', SKIRT),
               ('phase_4/maps/social/gumball/tt_t_chr_avt_shorts_funky.png', SHORTS),
               ('phase_13/maps/events/apriltoons/clothing/triplerainbow_skirt.png', SKIRT),
               ('phase_4/maps/apriltoons/high_roller_outfit/cc_t_clth_skirt_suit_hroller_white.png', SKIRT),
('phase_4/maps/apriltoons/high_roller_outfit/cc_t_clth_skirt_suit_hroller_black.png', SKIRT)
               ]

CUSTOM_CLOTHING_DIRECTORY = 'resources/phase_14/maps/clothing'
CUSTOM_CLOTHING_DIRECTORIES = (
    ('phase_14', CUSTOM_CLOTHING_DIRECTORY),
    ('phase_4', 'resources/phase_4/maps'),
)
CUSTOM_CLOTHING_REGISTRY = 'resources/phase_14/maps/clothing_registry.json'
CUSTOM_CLOTHING_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.rgb', '.rgba', '.tga')


def _getExistingPath(path):
    candidates = [path, os.path.join(os.getcwd(), path)]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return candidates[0]


def _getCustomClothingAssetPath(fullPath):
    normalized = fullPath.replace('\\', '/')
    resourcesToken = '/resources/'
    tokenIndex = normalized.lower().find(resourcesToken)
    if tokenIndex != -1:
        return normalized[tokenIndex + len(resourcesToken):]
    if normalized.lower().startswith('resources/'):
        return normalized[len('resources/'):]
    return normalized


def _normalizeClothingAssetPath(assetPath):
    return assetPath.replace('\\', '/').lower()


def _getKnownClothingPaths():
    knownPaths = {
        'shirt': set(),
        'sleeves': set(),
        'shorts': set(),
        'skirt': set(),
    }
    for assetPath in Shirts:
        if isinstance(assetPath, basestring):
            knownPaths['shirt'].add(_normalizeClothingAssetPath(assetPath))
    for assetPath in Sleeves:
        if isinstance(assetPath, basestring):
            knownPaths['sleeves'].add(_normalizeClothingAssetPath(assetPath))
    for assetPath in BoyShorts:
        if isinstance(assetPath, basestring):
            knownPaths['shorts'].add(_normalizeClothingAssetPath(assetPath))
    for bottomData in GirlBottoms:
        if isinstance(bottomData, tuple) and bottomData and isinstance(bottomData[0], basestring):
            if len(bottomData) > 1 and bottomData[1] == SKIRT:
                pieceName = 'skirt'
            else:
                pieceName = 'shorts'
            knownPaths[pieceName].add(_normalizeClothingAssetPath(bottomData[0]))
    return knownPaths


def _loadClothingRegistry(registryPath):
    if not os.path.isfile(registryPath):
        return {'version': 1, 'outfits': {}}
    try:
        registryFile = open(registryPath, 'r')
        try:
            registry = json.load(registryFile)
        finally:
            registryFile.close()
    except Exception:
        notify.warning('Could not read custom clothing registry. A new registry will be created.')
        return {'version': 1, 'outfits': {}}
    if not isinstance(registry, dict):
        registry = {}
    if not isinstance(registry.get('outfits'), dict):
        registry['outfits'] = {}
    registry['version'] = 1
    return registry


def _saveClothingRegistry(registryPath, registry):
    registryDirectory = os.path.dirname(registryPath)
    if registryDirectory and not os.path.isdir(registryDirectory):
        os.makedirs(registryDirectory)
    registryFile = open(registryPath, 'w')
    try:
        json.dump(registry, registryFile, indent=4, sort_keys=True)
        registryFile.write('\n')
    finally:
        registryFile.close()


def _getClothingPieceName(fileName):
    lowerName = fileName.lower()
    extension = os.path.splitext(lowerName)[1]
    if extension not in CUSTOM_CLOTHING_EXTENSIONS:
        return None
    fileStem = os.path.splitext(lowerName)[0]
    tokenName = fileStem.replace('-', '_').replace(' ', '_').replace('.', '_')
    nameTokens = [token for token in tokenName.split('_') if token]
    if 'sleeve' in lowerName:
        return 'sleeves'
    if 'shirt' in lowerName or 'top' in nameTokens:
        return 'shirt'
    if 'skirt' in lowerName or 'dress' in lowerName:
        return 'skirt'
    if ('short' in lowerName or 'bottom' in nameTokens or
            'bot' in nameTokens):
        return 'shorts'
    return None


def _findOutfitPieces(outfitDirectory):
    pieces = {}
    for fileName in sorted(os.listdir(outfitDirectory)):
        fullPath = os.path.join(outfitDirectory, fileName)
        if not os.path.isfile(fullPath):
            continue
        pieceName = _getClothingPieceName(fileName)
        if pieceName is not None:
            pieces[pieceName] = _getCustomClothingAssetPath(fullPath)
    return pieces


def _getPhase4OutfitKey(clothingRoot, fullPath):
    relativePath = os.path.relpath(fullPath, clothingRoot).replace('\\', '/')
    directoryName = os.path.dirname(relativePath).replace('\\', '/')
    fileStem = os.path.splitext(os.path.basename(relativePath))[0].lower()
    outfitStem = fileStem
    for token in ('shirtsleeve', 'sleeves', 'sleeve', 'shirt', 'shorts',
                  'short', 'skirt', 'bottom', 'dress'):
        outfitStem = outfitStem.replace(token, '_')
    tokenName = outfitStem.replace('-', '_').replace(' ', '_').replace('.', '_')
    outfitTokens = [token for token in tokenName.split('_')
                    if token and token not in ('top', 'bot')]
    outfitStem = '_'.join(outfitTokens)
    while '__' in outfitStem:
        outfitStem = outfitStem.replace('__', '_')
    outfitStem = outfitStem.strip('_-. ')
    if not outfitStem:
        outfitStem = fileStem
    if directoryName:
        return 'phase_4:%s/%s' % (directoryName.lower(), outfitStem)
    return 'phase_4:%s' % outfitStem


def _nextRegistryId(registry, idName, minimumId):
    usedIds = []
    for outfitData in registry['outfits'].values():
        if isinstance(outfitData, dict):
            value = outfitData.get(idName)
            if isinstance(value, int):
                usedIds.append(value)
    if not usedIds:
        return minimumId
    return max(max(usedIds) + 1, minimumId)


def _setListItemAtId(targetList, itemId, value, fallbackValue):
    while len(targetList) <= itemId:
        targetList.append(fallbackValue)
    targetList[itemId] = value


def _registerClothingPiece(registry, outfitData, pieceName, assetPath, minimumIds):
    registryChanged = False
    idName = pieceName + '_id'
    if outfitData.get(pieceName) != assetPath:
        outfitData[pieceName] = assetPath
        registryChanged = True
    if not isinstance(outfitData.get(idName), int):
        outfitData[idName] = _nextRegistryId(registry, idName, minimumIds[pieceName])
        registryChanged = True
    return registryChanged


def _scanPhase14Clothing(clothingRoot, registry, minimumIds):
    outfits = registry['outfits']
    registryChanged = False
    discoveredCount = 0
    for folderName in sorted(os.listdir(clothingRoot)):
        outfitDirectory = os.path.join(clothingRoot, folderName)
        if not os.path.isdir(outfitDirectory):
            continue
        pieces = _findOutfitPieces(outfitDirectory)
        if not pieces:
            continue
        discoveredCount += 1
        outfitData = outfits.get(folderName)
        if not isinstance(outfitData, dict):
            outfitData = {}
            outfits[folderName] = outfitData
            registryChanged = True
        if outfitData.get('folder') != folderName:
            outfitData['folder'] = folderName
            registryChanged = True
        if outfitData.get('source') != 'phase_14':
            outfitData['source'] = 'phase_14'
            registryChanged = True
        for pieceName in ('shirt', 'sleeves', 'shorts', 'skirt'):
            assetPath = pieces.get(pieceName)
            if assetPath is not None:
                if _registerClothingPiece(registry, outfitData, pieceName,
                                          assetPath, minimumIds):
                    registryChanged = True
    return registryChanged, discoveredCount


def _scanPhase4Clothing(clothingRoot, registry, minimumIds, knownPaths):
    outfits = registry['outfits']
    registryChanged = False
    discoveredCount = 0
    for directoryName, childDirectories, fileNames in os.walk(clothingRoot):
        childDirectories.sort()
        fileNames.sort()
        for fileName in fileNames:
            pieceName = _getClothingPieceName(fileName)
            if pieceName is None:
                continue
            fullPath = os.path.join(directoryName, fileName)
            assetPath = _getCustomClothingAssetPath(fullPath)
            normalizedPath = _normalizeClothingAssetPath(assetPath)
            if normalizedPath in knownPaths[pieceName]:
                continue
            registryKey = _getPhase4OutfitKey(clothingRoot, fullPath)
            outfitData = outfits.get(registryKey)
            if not isinstance(outfitData, dict):
                outfitData = {}
                outfits[registryKey] = outfitData
                registryChanged = True
            relativeDirectory = os.path.relpath(directoryName, clothingRoot).replace('\\', '/')
            if relativeDirectory == '.':
                relativeDirectory = ''
            if outfitData.get('folder') != relativeDirectory:
                outfitData['folder'] = relativeDirectory
                registryChanged = True
            if outfitData.get('source') != 'phase_4':
                outfitData['source'] = 'phase_4'
                registryChanged = True
            if _registerClothingPiece(registry, outfitData, pieceName,
                                      assetPath, minimumIds):
                registryChanged = True
            knownPaths[pieceName].add(normalizedPath)
            discoveredCount += 1
    return registryChanged, discoveredCount


def loadCustomClothing():
    registryPath = _getExistingPath(CUSTOM_CLOTHING_REGISTRY)
    registry = _loadClothingRegistry(registryPath)
    minimumIds = {
        'shirt': len(Shirts),
        'sleeves': len(Sleeves),
        'shorts': len(BoyShorts),
        'skirt': len(GirlBottoms),
    }
    knownPaths = _getKnownClothingPaths()
    registryChanged = False
    discoveredCount = 0
    foundClothingRoot = False
    for sourceName, clothingDirectory in CUSTOM_CLOTHING_DIRECTORIES:
        clothingRoot = _getExistingPath(clothingDirectory)
        if not os.path.isdir(clothingRoot):
            notify.info('Custom clothing directory not found: %s' % clothingDirectory)
            continue
        foundClothingRoot = True
        if sourceName == 'phase_14':
            sourceChanged, sourceCount = _scanPhase14Clothing(
                clothingRoot, registry, minimumIds)
        else:
            sourceChanged, sourceCount = _scanPhase4Clothing(
                clothingRoot, registry, minimumIds, knownPaths)
        if sourceChanged:
            registryChanged = True
        discoveredCount += sourceCount
    if not foundClothingRoot:
        return
    defaultShirt = Shirts[0]
    defaultSleeves = Sleeves[0]
    defaultShorts = BoyShorts[0]
    defaultGirlBottom = GirlBottoms[0]
    for folderName in sorted(registry['outfits'].keys()):
        outfitData = registry['outfits'][folderName]
        if not isinstance(outfitData, dict):
            continue
        shirtPath = outfitData.get('shirt')
        shirtId = outfitData.get('shirt_id')
        if isinstance(shirtPath, basestring) and isinstance(shirtId, int):
            _setListItemAtId(Shirts, shirtId, shirtPath, defaultShirt)
        sleevesPath = outfitData.get('sleeves')
        sleevesId = outfitData.get('sleeves_id')
        if isinstance(sleevesPath, basestring) and isinstance(sleevesId, int):
            _setListItemAtId(Sleeves, sleevesId, sleevesPath, defaultSleeves)
        shortsPath = outfitData.get('shorts')
        shortsId = outfitData.get('shorts_id')
        if isinstance(shortsPath, basestring) and isinstance(shortsId, int):
            _setListItemAtId(BoyShorts, shortsId, shortsPath, defaultShorts)
        skirtPath = outfitData.get('skirt')
        skirtId = outfitData.get('skirt_id')
        if isinstance(skirtPath, basestring) and isinstance(skirtId, int):
            _setListItemAtId(GirlBottoms, skirtId, (skirtPath, SKIRT), defaultGirlBottom)
    if registryChanged or not os.path.isfile(registryPath):
        _saveClothingRegistry(registryPath, registry)
    notify.info('Loaded %s custom clothing item(s) from the clothing registry.' % discoveredCount)



loadCustomClothing()



ClothesColors = [VBase4(1, 1, 1, 1.0),
 VBase4(0.863281, 0.40625, 0.417969, 1.0),
 VBase4(0.710938, 0.234375, 0.4375, 1.0),
 VBase4(0.992188, 0.480469, 0.167969, 1.0),
 VBase4(0.996094, 0.898438, 0.320312, 1.0),
 VBase4(0.550781, 0.824219, 0.324219, 1.0),
 VBase4(0.242188, 0.742188, 0.515625, 1.0),
 VBase4(0.433594, 0.90625, 0.835938, 1.0),
 VBase4(0.347656, 0.820312, 0.953125, 1.0),
 VBase4(0.191406, 0.5625, 0.773438, 1.0),
 VBase4(0.285156, 0.328125, 0.726562, 1.0),
 VBase4(0.460938, 0.378906, 0.824219, 1.0),
 VBase4(0.546875, 0.28125, 0.75, 1.0),
 VBase4(0.570312, 0.449219, 0.164062, 1.0),
 VBase4(0.640625, 0.355469, 0.269531, 1.0),
 VBase4(0.996094, 0.695312, 0.511719, 1.0),
 VBase4(0.832031, 0.5, 0.296875, 1.0),
 VBase4(0.992188, 0.480469, 0.167969, 1.0),
 VBase4(0.550781, 0.824219, 0.324219, 1.0),
 VBase4(0.433594, 0.90625, 0.835938, 1.0),
 VBase4(0.347656, 0.820312, 0.953125, 1.0),
 VBase4(0.96875, 0.691406, 0.699219, 1.0),
 VBase4(0.996094, 0.957031, 0.597656, 1.0),
 VBase4(0.855469, 0.933594, 0.492188, 1.0),
 VBase4(0.558594, 0.589844, 0.875, 1.0),
 VBase4(0.726562, 0.472656, 0.859375, 1.0),
 VBase4(0.898438, 0.617188, 0.90625, 1.0),
 VBase4(1.0, 1.0, 1.0, 1.0), #27
 VBase4(0.0, 0.2, 0.956862, 1.0),
 VBase4(0.972549, 0.094117, 0.094117, 1.0),
 VBase4(0.447058, 0.0, 0.90196, 1.0),
 VBase4(0.3, 0.3, 0.35, 1.0)]
ShirtStyles = {'bss1': [0, 0, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (10, 10),
           (11, 11),
           (12, 12),
           (27, 27)]],
 'bss2': [1, 1, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (10, 10),
           (11, 11),
           (12, 12)]],
 'bss3': [2, 2, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (10, 10),
           (11, 11),
           (12, 12)]],
 'bss4': [3, 3, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (10, 10),
           (11, 11),
           (12, 12)]],
 'bss5': [4, 4, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (9, 9),
           (10, 10),
           (11, 11),
           (12, 12)]],
 'bss6': [5, 5, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (10, 10),
           (11, 11),
           (12, 12)]],
 'bss7': [8, 8, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (8, 8),
           (9, 9),
           (11, 11),
           (12, 12),
           (27, 27)]],
 'bss8': [9, 9, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (10, 10),
           (11, 11),
           (12, 12)]],
 'bss9': [10, 0, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (10, 10),
           (11, 11),
           (12, 12),
           (27, 27)]],
 'bss10': [11, 0, [(0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),
            (9, 9),
            (10, 10),
            (11, 11),
            (12, 12),
            (27, 27)]],
 'bss11': [14, 10, [(0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),
            (9, 9),
            (10, 10),
            (11, 11),
            (12, 12)]],
 'bss12': [16, 0, [(27, 27),
            (27, 4),
            (27, 5),
            (27, 6),
            (27, 7),
            (27, 8),
            (27, 9)]],
 'bss13': [17, 0, [(0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),
            (9, 9),
            (10, 10),
            (11, 11),
            (12, 12)]],
 'bss14': [18, 12, [(0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (8, 8),
            (9, 9),
            (11, 11),
            (12, 12),
            (27, 27)]],
 'bss15': [19, 13, [(0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),
            (9, 9),
            (10, 10),
            (11, 11),
            (12, 12),
            (27, 27)]],
 'gss1': [0, 0, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (11, 11),
           (12, 12),
           (21, 21),
           (22, 22),
           (23, 23),
           (24, 24),
           (25, 25),
           (26, 26),
           (27, 27)]],
 'gss2': [1, 1, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (11, 11),
           (12, 12),
           (21, 21),
           (22, 22),
           (23, 23),
           (24, 24),
           (25, 25),
           (26, 26)]],
 'gss3': [2, 2, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (11, 11),
           (12, 12),
           (21, 21),
           (22, 22),
           (23, 23),
           (24, 24),
           (25, 25),
           (26, 26)]],
 'gss4': [3, 3, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (11, 11),
           (12, 12),
           (21, 21),
           (22, 22),
           (23, 23),
           (24, 24),
           (25, 25),
           (26, 26)]],
 'gss5': [5, 5, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (11, 11),
           (12, 12),
           (21, 21),
           (22, 22),
           (23, 23),
           (24, 24),
           (25, 25),
           (26, 26)]],
 'gss6': [6, 6, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (11, 11),
           (12, 12),
           (21, 21),
           (22, 22),
           (23, 23),
           (24, 24),
           (25, 25),
           (26, 26)]],
 'gss7': [7, 7, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (11, 11),
           (12, 12),
           (21, 21),
           (22, 22),
           (23, 23),
           (24, 24),
           (25, 25),
           (26, 26)]],
 'gss8': [9, 9, [(0, 0),
           (1, 1),
           (2, 2),
           (3, 3),
           (4, 4),
           (5, 5),
           (6, 6),
           (7, 7),
           (8, 8),
           (9, 9),
           (11, 11),
           (12, 12),
           (21, 21),
           (22, 22),
           (23, 23),
           (24, 24),
           (25, 25),
           (26, 26)]],
 'gss9': [12, 0, [(27, 27)]],
 'gss10': [13, 11, [(0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),
            (9, 9),
            (10, 10),
            (11, 11),
            (12, 12),
            (21, 21),
            (22, 22),
            (23, 23),
            (24, 24),
            (25, 25),
            (26, 26)]],
 'gss11': [15, 11, [(0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),
            (9, 9),
            (10, 10),
            (11, 11),
            (12, 12),
            (21, 21),
            (22, 22),
            (23, 23),
            (24, 24),
            (25, 25),
            (26, 26)]],
 'gss12': [16, 0, [(27, 27),
            (27, 4),
            (27, 5),
            (27, 6),
            (27, 7),
            (27, 8),
            (27, 9)]],
 'gss13': [20, 0, [(0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),
            (9, 9),
            (10, 10),
            (11, 11),
            (12, 12),
            (21, 21),
            (22, 22),
            (23, 23),
            (24, 24),
            (25, 25),
            (26, 26)]],
 'gss14': [21, 0, [(0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),
            (9, 9),
            (10, 10),
            (11, 11),
            (12, 12),
            (21, 21),
            (22, 22),
            (23, 23),
            (24, 24),
            (25, 25),
            (26, 26)]],
 'gss15': [22, 0, [(0, 0),
            (1, 1),
            (2, 2),
            (3, 3),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7),
            (8, 8),
            (9, 9),
            (10, 10),
            (11, 11),
            (12, 12),
            (21, 21),
            (22, 22),
            (23, 23),
            (24, 24),
            (25, 25),
            (26, 26)]],
 'c_ss1': [25, 16, [(27, 27)]],
 'c_ss2': [27, 18, [(27, 27)]],
 'c_ss3': [38, 27, [(27, 27)]],
 'c_bss1': [26, 17, [(27, 27)]],
 'c_bss2': [28, 19, [(27, 27)]],
 'c_bss3': [37, 26, [(27, 27)]],
 'c_bss4': [39, 28, [(27, 27)]],
 'c_gss1': [23, 14, [(27, 27)]],
 'c_gss2': [24, 15, [(27, 27)]],
 'c_gss3': [35, 24, [(27, 27)]],
 'c_gss4': [36, 25, [(27, 27)]],
 'c_gss5': [40, 29, [(27, 27)]],
 'c_ss4': [45, 34, [(27, 27)]],
 'c_ss5': [46, 35, [(27, 27)]],
 'c_ss6': [52, 41, [(27, 27)]],
 'c_ss7': [53, 42, [(27, 27)]],
 'c_ss8': [54, 43, [(27, 27)]],
 'c_ss9': [55, 44, [(27, 27)]],
 'c_ss10': [56, 45, [(27, 27)]],
 'c_ss11': [57, 46, [(27, 27)]],
 'hw_ss1': [29, 20, [(27, 27)]],
 'hw_ss2': [30, 21, [(27, 27)]],
 'hw_ss3': [114, 101, [(27, 27)]],
 'hw_ss4': [115, 102, [(27, 27)]],
 'hw_ss5': [122, 109, [(27, 27)]],
 'hw_ss6': [123, 110, [(27, 27)]],
 'hw_ss7': [124, 111, [(27, 27)]],
 'hw_ss8': [125, 112, [(27, 27)]],
 'hw_ss9': [126, 113, [(27, 27)]],
 'wh_ss1': [31, 22, [(27, 27)]],
 'wh_ss2': [32, 22, [(27, 27)]],
 'wh_ss3': [33, 23, [(27, 27)]],
 'wh_ss4': [34, 23, [(27, 27)]],
 'vd_ss1': [41, 30, [(27, 27)]],
 'vd_ss2': [42, 31, [(27, 27)]],
 'vd_ss3': [43, 32, [(27, 27)]],
 'vd_ss4': [44, 33, [(27, 27)]],
 'vd_ss5': [69, 58, [(27, 27)]],
 'vd_ss6': [70, 59, [(27, 27)]],
 'vd_ss7': [96, 85, [(27, 27)]],
 'sd_ss1': [47, 36, [(27, 27)]],
 'sd_ss2': [48, 37, [(27, 27)]],
 'sd_ss3': [116, 103, [(27, 27)]],
 'tc_ss1': [49, 38, [(27, 27)]],
 'tc_ss2': [50, 39, [(27, 27)]],
 'tc_ss3': [51, 40, [(27, 27)]],
 'tc_ss4': [62, 51, [(27, 27)]],
 'tc_ss5': [63, 52, [(27, 27)]],
 'tc_ss6': [64, 53, [(27, 27)]],
 'tc_ss7': [65, 54, [(27, 27)]],
 'j4_ss1': [58, 47, [(27, 27)]],
 'j4_ss2': [59, 48, [(27, 27)]],
 'c_ss12': [60, 49, [(27, 27)]],
 'c_ss13': [61, 50, [(27, 27)]],
 'pj_ss1': [66, 55, [(27, 27)]],
 'pj_ss2': [67, 56, [(27, 27)]],
 'pj_ss3': [68, 57, [(27, 27)]],
 'sa_ss1': [71, 60, [(27, 27)]],
 'sa_ss2': [72, 61, [(27, 27)]],
 'sa_ss3': [73, 62, [(27, 27)]],
 'sa_ss4': [74, 63, [(27, 27)]],
 'sa_ss5': [75, 64, [(27, 27)]],
 'sa_ss6': [76, 65, [(27, 27)]],
 'sa_ss7': [77, 66, [(27, 27)]],
 'sa_ss8': [78, 67, [(27, 27)]],
 'sa_ss9': [79, 68, [(27, 27)]],
 'sa_ss10': [80, 69, [(27, 27)]],
 'sa_ss11': [81, 70, [(27, 27)]],
 'sa_ss12': [82, 71, [(27, 27)]],
 'sa_ss13': [83, 72, [(27, 27)]],
 'sa_ss14': [84, 73, [(27, 27)]],
 'sa_ss15': [85, 74, [(27, 27)]],
 'sa_ss16': [86, 75, [(27, 27)]],
 'sa_ss17': [87, 76, [(27, 27)]],
 'sa_ss18': [88, 77, [(27, 27)]],
 'sa_ss19': [89, 78, [(27, 27)]],
 'sa_ss20': [90, 79, [(27, 27)]],
 'sa_ss21': [91, 80, [(27, 27)]],
 'sa_ss22': [92, 81, [(27, 27)]],
 'sa_ss23': [93, 82, [(27, 27)]],
 'sa_ss24': [94, 83, [(27, 27)]],
 'sa_ss25': [95, 84, [(27, 27)]],
 'sa_ss26': [106, 93, [(27, 27)]],
 'sa_ss27': [110, 97, [(27, 27)]],
 'sa_ss28': [111, 98, [(27, 27)]],
 'sa_ss29': [120, 107, [(27, 27)]],
 'sa_ss30': [121, 108, [(27, 27)]],
 'sa_ss31': [118, 105, [(27, 27)]],
 'sa_ss32': [127, 114, [(27, 27)]],
 'sa_ss33': [128, 115, [(27, 27)]],
 'sa_ss34': [129, 116, [(27, 27)]],
 'sa_ss35': [130, 117, [(27, 27)]],
 'sa_ss36': [131, 118, [(27, 27)]],
 'sa_ss37': [132, 119, [(27, 27)]],
 'sa_ss38': [133, 120, [(27, 27)]],
 'sa_ss39': [134, 121, [(27, 27)]],
 'sa_ss40': [135, 122, [(27, 27)]],
 'sa_ss41': [136, 123, [(27, 27)]],
 'sa_ss42': [137, 124, [(27, 27)]],
 'sa_ss43': [138, 125, [(27, 27)]],
 'sa_ss44': [139, 126, [(27, 27)]],
 'sa_ss45': [140, 127, [(27, 27)]],
 'sa_ss46': [141, 128, [(27, 27)]],
 'sa_ss47': [142, 129, [(27, 27)]],
 'sa_ss48': [143, 130, [(27, 27)]],
 'sa_ss49': [144, 116, [(27, 27)]],
 'sa_ss50': [145, 131, [(27, 27)]],
 'sa_ss51': [146, 133, [(27, 27)]],
 'sa_ss52': [147, 134, [(27, 27)]],
 'sa_ss53': [148, 135, [(27, 27)]],
 'sa_ss54': [149, 136, [(27, 27)]],
 'sa_ss55': [150, 137, [(27, 27)]],
 'sc_1': [97, 86, [(27, 27)]],
 'sc_2': [98, 86, [(27, 27)]],
 'sc_3': [99, 86, [(27, 27)]],
 'sil_1': [100, 87, [(27, 27)]],
 'sil_2': [101, 88, [(27, 27)]],
 'sil_3': [102, 89, [(27, 27)]],
 'sil_4': [103, 90, [(27, 27)]],
 'sil_5': [104, 91, [(27, 27)]],
 'sil_6': [105, 92, [(27, 27)]],
 'sil_7': [107, 94, [(27, 27)]],
 'sil_8': [108, 95, [(27, 27)]],
 'emb_us1': [103, 90, [(27, 27)]],
 'emb_us2': [100, 87, [(27, 27)]],
 'emb_us3': [101, 88, [(27, 27)]],
 'sb_1': [109, 96, [(27, 27)]],
 'jb_1': [112, 99, [(27, 27)]],
 'jb_2': [113, 100, [(27, 27)]],
 'ugcms': [117, 104, [(27, 27)]],
 'lb_1': [119, 106, [(27, 27)]],
 'ins_sh1': [148, 135, [(27, 27)]]}
BottomStyles = {'bbs1': [0, [0,
           1,
           2,
           4,
           6,
           9,
           10,
           11,
           12,
           13,
           14,
           15,
           16,
           17,
           18,
           19,
           20]],
 'bbs2': [1, [0,
           1,
           2,
           4,
           6,
           9,
           10,
           11,
           12,
           13,
           14,
           15,
           16,
           17,
           18,
           19,
           20]],
 'bbs3': [2, [0,
           1,
           2,
           4,
           6,
           9,
           10,
           11,
           12,
           13,
           14,
           15,
           16,
           17,
           18,
           19,
           20]],
 'bbs4': [3, [0,
           1,
           2,
           4,
           6,
           8,
           9,
           11,
           12,
           13,
           15,
           16,
           17,
           18,
           19,
           20,
           27]],
 'bbs5': [4, [0,
           1,
           2,
           4,
           6,
           9,
           10,
           11,
           12,
           13,
           14,
           15,
           16,
           17,
           18,
           19,
           20]],
 'bbs6': [5, [0,
           1,
           2,
           4,
           6,
           9,
           10,
           11,
           12,
           14,
           15,
           16,
           17,
           18,
           19,
           20,
           27]],
 'bbs7': [6, [0,
           1,
           2,
           4,
           6,
           9,
           10,
           11,
           12,
           13,
           14,
           15,
           16,
           17,
           18,
           20,
           27]],
 'bbs8': [7, [0,
           1,
           2,
           4,
           6,
           9,
           10,
           11,
           12,
           13,
           14,
           15,
           16,
           17,
           18,
           19,
           20,
           27]],
 'vd_bs1': [8, [27]],
 'vd_bs2': [23, [27]],
 'vd_bs3': [24, [27]],
 'c_bs1': [9, [27]],
 'c_bs2': [10, [27]],
 'c_bs5': [15, [27]],
 'sd_bs1': [11, [27]],
 'sd_bs2': [44, [27]],
 'pj_bs1': [16, [27]],
 'pj_bs2': [17, [27]],
 'pj_bs3': [18, [27]],
 'wh_bs1': [19, [27]],
 'wh_bs2': [20, [27]],
 'wh_bs3': [21, [27]],
 'wh_bs4': [22, [27]],
 'hw_bs1': [47, [27]],
 'hw_bs2': [48, [27]],
 'hw_bs5': [49, [27]],
 'hw_bs6': [50, [27]],
 'hw_bs7': [51, [27]],
 'gsk1': [0, [0,
           1,
           2,
           3,
           4,
           5,
           6,
           7,
           8,
           9,
           11,
           12,
           21,
           22,
           23,
           24,
           25,
           26,
           27]],
 'gsk2': [1, [0,
           1,
           2,
           3,
           4,
           5,
           6,
           7,
           8,
           9,
           11,
           12,
           21,
           22,
           23,
           24,
           25,
           26]],
 'gsk3': [2, [0,
           1,
           2,
           3,
           4,
           5,
           6,
           7,
           8,
           9,
           11,
           12,
           21,
           22,
           23,
           24,
           25,
           26]],
 'gsk4': [3, [0,
           1,
           2,
           3,
           4,
           5,
           6,
           7,
           8,
           9,
           11,
           12,
           21,
           22,
           23,
           24,
           25,
           26]],
 'gsk5': [4, [0,
           1,
           2,
           3,
           4,
           5,
           6,
           7,
           8,
           9,
           11,
           12,
           21,
           22,
           23,
           24,
           25,
           26]],
 'gsk6': [7, [0,
           1,
           2,
           3,
           4,
           5,
           6,
           7,
           8,
           9,
           11,
           12,
           21,
           22,
           23,
           24,
           25,
           26,
           27]],
 'gsk7': [8, [0,
           1,
           2,
           3,
           4,
           5,
           6,
           7,
           8,
           9,
           11,
           12,
           21,
           22,
           23,
           24,
           25,
           26,
           27]],
 'gsh1': [5, [0,
           1,
           2,
           3,
           4,
           5,
           6,
           7,
           8,
           9,
           11,
           12,
           21,
           22,
           23,
           24,
           25,
           26,
           27]],
 'gsh2': [6, [0,
           1,
           2,
           3,
           4,
           5,
           6,
           7,
           8,
           9,
           11,
           12,
           21,
           22,
           23,
           24,
           25,
           26,
           27]],
 'gsh3': [9, [0,
           1,
           2,
           3,
           4,
           5,
           6,
           7,
           8,
           9,
           11,
           12,
           21,
           22,
           23,
           24,
           25,
           26,
           27]],
 'c_gsk1': [10, [27]],
 'c_gsk2': [11, [27]],
 'c_gsk3': [12, [27]],
 'vd_gs1': [13, [27]],
 'vd_gs2': [27, [27]],
 'vd_gs3': [28, [27]],
 'c_gsk4': [14, [27]],
 'sd_gs1': [15, [27]],
 'sd_gs2': [48, [27]],
 'c_gsk5': [16, [27]],
 'c_gsk6': [17, [27]],
 'c_bs3': [12, [27]],
 'c_bs4': [13, [27]],
 'j4_bs1': [14, [27]],
 'j4_gs1': [18, [27]],
 'c_gsk7': [19, [27]],
 'pj_gs1': [20, [27]],
 'pj_gs2': [21, [27]],
 'pj_gs3': [22, [27]],
 'wh_gsk1': [23, [27]],
 'wh_gsk2': [24, [27]],
 'wh_gsk3': [25, [27]],
 'wh_gsk4': [26, [27]],
 'sa_bs1': [25, [27]],
 'sa_bs2': [26, [27]],
 'sa_bs3': [27, [27]],
 'sa_bs4': [28, [27]],
 'sa_bs5': [29, [27]],
 'sa_bs6': [30, [27]],
 'sa_bs7': [31, [27]],
 'sa_bs8': [32, [27]],
 'sa_bs9': [33, [27]],
 'sa_bs10': [34, [27]],
 'sa_bs11': [35, [27]],
 'sa_bs12': [36, [27]],
 'sa_bs13': [41, [27]],
 'sa_bs14': [46, [27]],
 'sa_bs15': [45, [27]],
 'sa_bs16': [52, [27]],
 'sa_bs17': [53, [27]],
 'sa_bs18': [54, [27]],
 'sa_bs19': [55, [27]],
 'sa_bs20': [56, [27]],
 'sa_bs21': [57, [27]],
 'sa_gs1': [29, [27]],
 'sa_gs2': [30, [27]],
 'sa_gs3': [31, [27]],
 'sa_gs4': [32, [27]],
 'sa_gs5': [33, [27]],
 'sa_gs6': [34, [27]],
 'sa_gs7': [35, [27]],
 'sa_gs8': [36, [27]],
 'sa_gs9': [37, [27]],
 'sa_gs10': [38, [27]],
 'sa_gs11': [39, [27]],
 'sa_gs12': [40, [27]],
 'sa_gs13': [45, [27]],
 'sa_gs14': [50, [27]],
 'sa_gs15': [49, [27]],
 'sa_gs16': [57, [27]],
 'sa_gs17': [58, [27]],
 'sa_gs18': [59, [27]],
 'sa_gs19': [60, [27]],
 'sa_gs20': [61, [27]],
 'sa_gs21': [62, [27]],
 'sc_bs1': [37, [27]],
 'sc_bs2': [38, [27]],
 'sc_bs3': [39, [27]],
 'sc_gs1': [41, [27]],
 'sc_gs2': [42, [27]],
 'sc_gs3': [43, [27]],
 'sil_bs1': [40, [27]],
 'sil_gs1': [44, [27]],
 'hw_bs3': [42, [27]],
 'hw_gs3': [46, [27]],
 'hw_bs4': [43, [27]],
 'hw_gs4': [47, [27]],
 'hw_gs1': [51, [27]],
 'hw_gs2': [52, [27]],
 'hw_gs5': [54, [27]],
 'hw_gs6': [55, [27]],
 'hw_gs7': [56, [27]],
 'hw_gsk1': [53, [27]],
 'ins_bs1': [57, [27]],
 'ins_gs1': [62, [27]]}
MAKE_A_TOON = 1
TAMMY_TAILOR = 2004
LONGJOHN_LEROY = 1007
TAILOR_HARMONY = 4008
BONNIE_BLOSSOM = 5007
WARREN_BUNDLES = 3008
WORNOUT_WAYLON = 9010
TAILOR_TIM = 6010
TailorCollections = {MAKE_A_TOON: [['bss1', 'bss2'],
               ['gss1', 'gss2'],
               ['bbs1', 'bbs2'],
               ['gsk1', 'gsh1']],
 TAMMY_TAILOR: [['bss1', 'bss2'],
                ['gss1', 'gss2'],
                ['bbs1', 'bbs2'],
                ['gsk1', 'gsh1']],
 TAILOR_TIM: [['bss1', 'bss2'],
                ['gss1', 'gss2'],
                ['bbs1', 'bbs2'],
                ['gsk1', 'gsh1']],
 LONGJOHN_LEROY: [['bss3', 'bss14'],
                  ['gss3', 'gss14'],
                  ['bbs3', 'bbs4'],
                  ['gsk2', 'gsh2']],
 TAILOR_HARMONY: [['bss5', 'bss6', 'bss10'],
                  ['gss5', 'gss6', 'gss9'],
                  ['bbs5'],
                  ['gsk3', 'gsh3']],
 BONNIE_BLOSSOM: [['bss7', 'bss8', 'bss12'],
                  ['gss8', 'gss10', 'gss12'],
                  ['bbs6'],
                  ['gsk4', 'gsk5']],
 WARREN_BUNDLES: [['bss9', 'bss13'],
                  ['gss7', 'gss11'],
                  ['bbs7'],
                  ['gsk6']],
 WORNOUT_WAYLON: [['bss11', 'bss15'],
                  ['gss13', 'gss15'],
                  ['bbs8'],
                  ['gsk7']]}

BOY_SHIRTS = 0
GIRL_SHIRTS = 1
BOY_SHORTS = 2
GIRL_BOTTOMS = 3
HAT = 1
GLASSES = 2
BACKPACK = 4
SHOES = 8
MakeAToonBoyBottoms = []
MakeAToonBoyShirts = []
MakeAToonGirlBottoms = []
MakeAToonGirlShirts = []
MakeAToonGirlSkirts = []
MakeAToonGirlShorts = []

#Combine all tailors into MAKE_A_TOON tailor.
if mergeMATTailor:
    for tailors in TailorCollections:
        for girlBottoms in TailorCollections[tailors][GIRL_BOTTOMS]:
            if girlBottoms not in TailorCollections[MAKE_A_TOON][GIRL_BOTTOMS]:
                TailorCollections[MAKE_A_TOON][GIRL_BOTTOMS].append(girlBottoms)
        for boyShorts in TailorCollections[tailors][BOY_SHORTS]:
            if boyShorts not in TailorCollections[MAKE_A_TOON][BOY_SHORTS]:
                 TailorCollections[MAKE_A_TOON][BOY_SHORTS].append(boyShorts)
        for girlShirts in TailorCollections[tailors][GIRL_SHIRTS]:
            if girlShirts not in TailorCollections[MAKE_A_TOON][GIRL_SHIRTS]:
                 TailorCollections[MAKE_A_TOON][GIRL_SHIRTS].append(girlShirts)
        for boyShirts in TailorCollections[tailors][BOY_SHIRTS]:
            if boyShirts not in TailorCollections[MAKE_A_TOON][BOY_SHIRTS]:
                 TailorCollections[MAKE_A_TOON][BOY_SHIRTS].append(boyShirts)

for style in TailorCollections[MAKE_A_TOON][BOY_SHORTS]:
    index = BottomStyles[style][0]
    MakeAToonBoyBottoms.append(index)

for style in TailorCollections[MAKE_A_TOON][BOY_SHIRTS]:
    index = ShirtStyles[style][0]
    MakeAToonBoyShirts.append(index)

for style in TailorCollections[MAKE_A_TOON][GIRL_BOTTOMS]:
    index = BottomStyles[style][0]
    MakeAToonGirlBottoms.append(index)

for style in TailorCollections[MAKE_A_TOON][GIRL_SHIRTS]:
    index = ShirtStyles[style][0]
    MakeAToonGirlShirts.append(index)

for index in MakeAToonGirlBottoms:
    flag = GirlBottoms[index][1]
    if flag == SKIRT:
        MakeAToonGirlSkirts.append(index)
    elif flag == SHORTS:
        MakeAToonGirlShorts.append(index)
    else:
        notify.error('Invalid flag')

def getRandomTop(gender, tailorId = MAKE_A_TOON, generator = None):
    if generator == None:
        generator = random
    collection = TailorCollections[tailorId]
    if gender == 'm':
        style = generator.choice(collection[BOY_SHIRTS])
    else:
        style = generator.choice(collection[GIRL_SHIRTS])
    styleList = ShirtStyles[style]
    colors = generator.choice(styleList[2])
    return (styleList[0],
     colors[0],
     styleList[1],
     colors[1])


def getRandomBottom(gender, tailorId = MAKE_A_TOON, generator = None, girlBottomType = None):
    if generator == None:
        generator = random
    collection = TailorCollections[tailorId]
    if gender == 'm':
        style = generator.choice(collection[BOY_SHORTS])
    elif girlBottomType is None:
        style = generator.choice(collection[GIRL_BOTTOMS])
    elif girlBottomType == SKIRT:
        skirtCollection = filter(lambda style: GirlBottoms[BottomStyles[style][0]][1] == SKIRT, collection[GIRL_BOTTOMS])
        style = generator.choice(skirtCollection)
    elif girlBottomType == SHORTS:
        shortsCollection = filter(lambda style: GirlBottoms[BottomStyles[style][0]][1] == SHORTS, collection[GIRL_BOTTOMS])
        style = generator.choice(shortsCollection)
    else:
        notify.error('Bad girlBottomType: %s' % girlBottomType)
    styleList = BottomStyles[style]
    color = generator.choice(styleList[1])
    return (styleList[0], color)


def getRandomGirlBottom(type):
    bottoms = []
    index = 0
    for bottom in GirlBottoms:
        if bottom[1] == type:
            bottoms.append(index)
        index += 1

    return random.choice(bottoms)


def getRandomGirlBottomAndColor(type):
    bottoms = []
    if type == SHORTS:
        typeStr = 'gsh'
    else:
        typeStr = 'gsk'
    for bottom in BottomStyles.keys():
        if bottom.find(typeStr) >= 0:
            bottoms.append(bottom)

    style = BottomStyles[random.choice(bottoms)]
    return (style[0], random.choice(style[1]))


def getRandomizedTops(gender, tailorId = MAKE_A_TOON, generator = None):
    if generator == None:
        generator = random
    collection = TailorCollections[tailorId]
    if gender == 'm':
        collection = collection[BOY_SHIRTS][:]
    else:
        collection = collection[GIRL_SHIRTS][:]
    tops = []
    random.shuffle(collection)
    for style in collection:
        colors = ShirtStyles[style][2][:]
        random.shuffle(colors)
        for color in colors:
            tops.append((ShirtStyles[style][0],
             color[0],
             ShirtStyles[style][1],
             color[1]))

    return tops


def getRandomizedBottoms(gender, tailorId = MAKE_A_TOON, generator = None):
    if generator == None:
        generator = random
    collection = TailorCollections[tailorId]
    if gender == 'm':
        collection = collection[BOY_SHORTS][:]
    else:
        collection = collection[GIRL_BOTTOMS][:]
    bottoms = []
    random.shuffle(collection)
    for style in collection:
        colors = BottomStyles[style][1][:]
        random.shuffle(colors)
        for color in colors:
            bottoms.append((BottomStyles[style][0], color))

    return bottoms


def getTops(gender, tailorId = MAKE_A_TOON):
    if gender == 'm':
        collection = TailorCollections[tailorId][BOY_SHIRTS]
    else:
        collection = TailorCollections[tailorId][GIRL_SHIRTS]
    tops = []
    for style in collection:
        for color in ShirtStyles[style][2]:
            tops.append((ShirtStyles[style][0],
             color[0],
             ShirtStyles[style][1],
             color[1]))

    return tops

def getTopColors(gender, top, tailorId = MAKE_A_TOON):
    if gender == 'm':
        collection = TailorCollections[tailorId][BOY_SHIRTS]
    else:
        collection = TailorCollections[tailorId][GIRL_SHIRTS]
    tops = getTopStyles(gender, tailorId)
    colors = []
    index = collection[tops.index(top)]
    for color in ShirtStyles[index][2]:
        colors.append((color[0], color[1]))
    return colors
 
def getTopStyles(gender, tailorId = MAKE_A_TOON):
    if gender == 'm':
        collection = TailorCollections[tailorId][BOY_SHIRTS]
    else:
        collection = TailorCollections[tailorId][GIRL_SHIRTS]
    tops = []
    for style in collection:
        tops.append((ShirtStyles[style][0], ShirtStyles[style][1]))
    return tops
 
def getAllTops(gender):
    tops = []
    for style in ShirtStyles.keys():
        if gender == 'm':
            if style[0] == 'g' or style[:3] == 'c_g':
                continue
        elif style[0] == 'b' or style[:3] == 'c_b':
            continue
        for color in ShirtStyles[style][2]:
            tops.append((ShirtStyles[style][0],
             color[0],
             ShirtStyles[style][1],
             color[1]))

    return tops


def getBottoms(gender, tailorId = MAKE_A_TOON):
    if gender == 'm':
        collection = TailorCollections[tailorId][BOY_SHORTS]
    else:
        collection = TailorCollections[tailorId][GIRL_BOTTOMS]
    bottoms = []
    for style in collection:
        for color in BottomStyles[style][1]:
            bottoms.append((BottomStyles[style][0], color))

    return bottoms

def getBottomStyles(gender, tailorId = MAKE_A_TOON):
    if gender == 'm':
        collection = TailorCollections[tailorId][BOY_SHORTS]
    else:
        collection = TailorCollections[tailorId][GIRL_BOTTOMS]
    bottoms = []
    for style in collection:
            bottoms.append(BottomStyles[style][0])
 
    return bottoms
 
def getBottomColors(gender, bottom, tailorId = MAKE_A_TOON):
    if gender == 'm':
        collection = TailorCollections[tailorId][BOY_SHORTS]
    else:
        collection = TailorCollections[tailorId][GIRL_BOTTOMS]
    bottoms = getBottomStyles(gender, tailorId)
    colors = []
    index = collection[bottoms.index(bottom)]
    for color in BottomStyles[index][1]:
        colors.append(color)
    return colors
 
def getAllBottoms(gender, output = 'both'):
    bottoms = []
    for style in BottomStyles.keys():
        if gender == 'm':
            if style[0] == 'g' or style[:3] == 'c_g' or style[:4] == 'vd_g' or style[:4] == 'sd_g' or style[:4] == 'j4_g' or style[:4] == 'pj_g' or style[:4] == 'wh_g' or style[:4] == 'sa_g' or style[:4] == 'sc_g' or style[:5] == 'sil_g' or style[:4] == 'hw_g':
                continue
        elif style[0] == 'b' or style[:3] == 'c_b' or style[:4] == 'vd_b' or style[:4] == 'sd_b' or style[:4] == 'j4_b' or style[:4] == 'pj_b' or style[:4] == 'wh_b' or style[:4] == 'sa_b' or style[:4] == 'sc_b' or style[:5] == 'sil_b' or style[:4] == 'hw_b':
            continue
        bottomIdx = BottomStyles[style][0]
        if gender == 'f':
            textureType = GirlBottoms[bottomIdx][1]
        else:
            textureType = SHORTS
        if output == 'both' or output == 'skirts' and textureType == SKIRT or output == 'shorts' and textureType == SHORTS:
            for color in BottomStyles[style][1]:
                bottoms.append((bottomIdx, color))

    return bottoms


allColorsList = [(1.0, 1.0, 1.0, 1.0),
 (0.96875, 0.691406, 0.699219, 1.0),
 (0.933594, 0.265625, 0.28125, 1.0),
 (0.863281, 0.40625, 0.417969, 1.0),
 (0.710938, 0.234375, 0.4375, 1.0),
 (0.570312, 0.449219, 0.164062, 1.0),
 (0.640625, 0.355469, 0.269531, 1.0),
 (0.996094, 0.695312, 0.511719, 1.0),
 (0.832031, 0.5, 0.296875, 1.0),
 (0.992188, 0.480469, 0.167969, 1.0),
 (0.996094, 0.898438, 0.320312, 1.0),
 (0.996094, 0.957031, 0.597656, 1.0),
 (0.855469, 0.933594, 0.492188, 1.0),
 (0.550781, 0.824219, 0.324219, 1.0),
 (0.242188, 0.742188, 0.515625, 1.0),
 (0.304688, 0.96875, 0.402344, 1.0),
 (0.433594, 0.90625, 0.835938, 1.0),
 (0.347656, 0.820312, 0.953125, 1.0),
 (0.191406, 0.5625, 0.773438, 1.0),
 (0.558594, 0.589844, 0.875, 1.0),
 (0.285156, 0.328125, 0.726562, 1.0),
 (0.460938, 0.378906, 0.824219, 1.0),
 (0.546875, 0.28125, 0.75, 1.0),
 (0.726562, 0.472656, 0.859375, 1.0),
 (0.898438, 0.617188, 0.90625, 1.0),
 (0.7, 0.7, 0.8, 1.0),
 (0.3, 0.3, 0.35, 1.0),
 (0.891, 0.439, 0.698, 1.0),
 (0.741, 0.873, 0.957, 1.0),
 (0.641, 0.857, 0.673, 1.0),
 (0.039, 0.862, 0.654, 1.0),
 (0.196, 0.725, 0.714, 1.0),
 (0.984, 0.537, 0.396, 1.0),
 (0.968, 0.749, 0.349, 1.0),
 (0.658, 0.175, 0.258, 1.0),
 (0.411, 0.644, 0.282, 1.0),
 (0.325, 0.407, 0.601, 1.0),
 (0.235, 0.573, 0.984, 1.0),
 (0.0, 0.635294, 0.258823, 1.0),
 (0.674509, 0.925490, 1.0, 1.0),
 (0.988235, 0.894117, 0.745098, 1.0),
 (0.749019, 1.0, 0.847058, 1.0),
 (0.470588, 0.443137, 0.447058, 1.0),
 (0.996078, 0.254901, 0.392156, 1.0),
 (0.811764, 0.709803, 0.231372, 1.0),
 (0.749019, 0.756862, 0.760784, 1.0),
 (1.0, 0.639215, 0.262745, 1.0),
 (0.0, 0.403921, 0.647058, 1.0),
 (0.862745, 0.078431, 0.235294, 1.0),
 (0.0, 0.635294, 0.513725, 1.0),
 (0.803921, 0.498039, 0.196078, 1.0),
 (0.70, 0.52, 0.75, 1.0),
 (1.0, 0, 1.0, 1.0),
 (0.5764, 0.4392, 0.8588, 1.0),
 (1.0, 1.0, 0.94117, 1.0),
 (0.9333, 0.8235, 0.9333, 1.0),
 (0.0, 1.0, 0.4980, 1.0),
 (0.8549, 0.6470, 0.1254, 1.0),
 (1.0, 0.59607, 0.0705, 1.0),
 (0.8039, 0.6862, 0.5843, 1.0),
 (0.2196, 0.5568, 0.5568, 1.0),
 (0.7764, 0.4431, 0.4431, 1.0),
 (0.8901, 0.8117, 0.3411, 1.0),
 (0.4117, 0.4117, 0.4117, 1.0),
 (1.0, 0.8431, 0.0, 1.0),
 (0.9333, 0.7882, 0.0, 1.0)]
defaultBoyColorList = [0,
 1,
 2,
 3,
 4,
 5,
 6,
 7,
 8,
 9,
 10,
 11,
 12,
 13,
 14,
 15,
 16,
 17,
 18,
 19,
 20,
 21,
 22,
 23,
 24,
 25,
 26,
 27,
 28,
 29,
 30,
 31,
 32,
 33,
 34,
 35,
 36, 
 37,
 38,
 39,
 40,
 41,
 42,
 43,
 44,
 45,
 46,
 47,
 48,
 49,
 50,
 51,
 52,
 53,
 54,
 55,
 56,
 57,
 58,
 59,
 60,
 61,
 62,
 63,
 64]
defaultGirlColorList = [0,
 1,
 2,
 3,
 4,
 5,
 6,
 7,
 8,
 9,
 10,
 11,
 12,
 13,
 14,
 15,
 16,
 17,
 18,
 19,
 20,
 21,
 22,
 23,
 24,
 25,
 26,
 27,
 28,
 29,
 30,
 31,
 32,
 33,
 34,
 35,
 36, 
 37,
 38,
 39,
 40,
 41,
 42,
 43,
 44,
 45,
 46,
 47,
 48,
 49,
 50,
 51,
 52,
 53,
 54,
 55,
 56,
 57,
 58,
 59,
 60,
 61,
 62,
 63,
 64]

defaultColorList = allColorsList
HatModels = [
    None,
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_baseball',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_safari',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_ribbon',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_heart',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_topHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_anvil',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_flowerPot',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_sandbag',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_weight',
    'phase_4/models/accessories/bosses/hat_chainsaw',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_golfHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_partyHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_pillBox',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_crown',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_cowboyHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_pirateHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_propellerHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_fishingHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_sombreroHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_strawHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_sunHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_antenna',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_beeHiveHairdo',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_bowler',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_chefsHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_detective',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_feathers',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_fedora',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_mickeysBandConductorHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_headband',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_pompadorHairdo',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_princess',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_robinHoodHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_romanHelmet',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_spiderAntennaThingy',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_tiara',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_vikingHelmet',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_witch',
    'phase_4/models/accessories/halloween/cc_m_acc_hat_wizard_enchanted',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_conquistadorHelmet',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_firefighterHelmet',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_foilPyramid',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_minersHardhatWithLight',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_napoleonHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_pilotsCap',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_policeHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_rainbowAfroWig',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_sailorHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_carmenMirandaFruitHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_bobbyHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_jugheadHat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_winter',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_bandana',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_dinosaur',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_band',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_birdNest',
    'phase_4/models/accessories/halloween/tt_t_chr_avt_acc_hat_space_helm',
    'phase_4/models/accessories/halloween/tt_m_chr_avt_acc_hat_batbow',
    'phase_4/models/accessories/halloween/tt_m_chr_avt_acc_hat_cauldronhat',
    'phase_4/models/accessories/halloween/tt_m_chr_avt_acc_hat_electricbolts',
    'phase_4/models/accessories/halloween/tt_m_chr_avt_acc_hat_pumpkinbucket',
    'phase_4/models/accessories/halloween/tt_m_chr_avt_acc_hat_scarecrow',
    'phase_4/models/accessories/halloween/tt_m_chr_avt_acc_hat_frank_head',
    'phase_4/models/accessories/halloween/tt_m_chr_avt_acc_hat_alchemistgoggles',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_bobblehat_blue',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_bobblehat_green',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_bobblehat_grey',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_bobblehat_pink',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_bobblehat_rainbow',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_bobblehat_red',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_santa_red',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_santa_rainbow',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_elf_green',
    'phase_4/models/accessories/winter/cc_m_acc_hat_elf',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_star',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_tin_humble',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_tin_regal',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_tin_tradi',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_ragdoll_humble',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_ragdoll_tradi',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_ragdoll_regal',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_hat_antlers',
    'phase_4/models/accessories/social/doe/tt_m_chr_avt_acc_hat_doe_beanie',
    'phase_4/models/accessories/social/webster/tt_m_chr_avt_acc_hat_webster_bookhat',
    'phase_4/models/accessories/apriltoons/tt_m_chr_avt_acc_hat_umbrella',
    'phase_4/models/accessories/apriltoons/tt_m_chr_avt_acc_hat_aviatorcap',
    'phase_4/models/accessories/anniversary/tt_m_chr_avt_acc_hat_cake',
    'phase_4/models/accessories/outback/slouchhat',
    'phase_4/models/accessories/outback/corkhat',
    'phase_4/models/accessories/outback/geckohat',
    'phase_13/models/events/btl/accessories/alien_hat',
    'phase_13/models/events/btl/accessories/angel_halo',
    'phase_13/models/events/btl/accessories/demon_horns',
    'phase_13/models/events/btl/accessories/ridinghood_hood',
    'phase_13/models/events/btl/accessories/robophones',
    'phase_13/models/events/btl/accessories/btl_spin_band',
    'phase_5/models/props/bowling_ball-mod',
    'phase_5/models/props/fruit-pie',
    'phase_4/models/accessories/winter/ragdoll_homemade_hat',
    'phase_4/models/accessories/winter/ski_helmet',
    'phase_4/models/accessories/winter/snowman_hat',
    'phase_4/models/accessories/winter/soldier_homemade_hat',
    'phase_3.5/models/props/tv',
    'phase_13/models/events/stpats/luckyhat',
    'phase_13/models/events/stpats/tartanhat',
    'phase_13/models/events/stpats/cloverband',
    'phase_13/models/events/stpats/cloverclip',
    'phase_13/models/events/apriltoons/rainbowphones',
    'phase_13/models/events/apriltoons/clown_hat',
    'phase_13/models/events/apriltoons/jester_hat',
    'phase_13/models/events/easter2020/easter_beanie',
    'phase_13/models/events/btl/accessories/atticushat',
    'phase_4/models/accessories/bosses/cc_m_acc_hat_diploma_bow',
    'phase_13/models/events/july4/grill',
    'phase_13/models/events/thanksgiving/leaf_hat',
    'phase_4/models/accessories/winter/past_candle',
    'phase_4/models/accessories/winter/present_holly',
    'phase_4/models/accessories/winter/future_hood',
    'phase_11/models/lawbotHQ/da_plant',
    'phase_4/models/accessories/social/newstoon-gray_bow',
    'phase_4/models/accessories/halloween/tt_m_chr_avt_acc_hat_gibus',  # redefined in GhostTophat.py
    'phase_4/models/accessories/apriltoons/hat-number1',
    'phase_4/models/accessories/tt_m_chr_avt_acc_hat_bandana2',
    'phase_4/models/accessories/social/bro/brovinci_hair',
    'phase_4/models/accessories/bosses/hat_icecube',
    'phase_4/models/accessories/bosses/hat_smartcap',
    'phase_4/models/accessories/social/ttcc_acc_clownbeanie',
    'phase_4/models/accessories/social/ttcc_acc_bananahat',
    'phase_4/models/accessories/social/ttcc_acc_wingsuit_helmet',
    'phase_4/models/accessories/social/ttcc_acc_engineer_cap',
    'phase_4/models/accessories/social/ttcc_acc_donuthat',
    'phase_4/models/accessories/social/ttcc_acc_crullerberet',
    'phase_4/models/accessories/social/ttcc_acc_flowercrown',
    'phase_4/models/accessories/social/ttcc_acc_rosecrown',
    'phase_4/models/accessories/bosses/hat_chainsaw',
    'phase_4/models/accessories/bosses/hat_multislacker',
    'phase_4/models/accessories/bosses/hat_treekiller',
    'phase_4/models/accessories/bosses/hat_unibrow',
    'phase_4/models/accessories/social/ttcc_acc_nightcap',
    'phase_4/models/accessories/social/ttcc_acc_blackberet',
    'phase_4/models/accessories/social/ttcc_acc_gumballhat',
    'phase_4/models/accessories/social/ttcc_acc_cardCrown',
    'phase_4/models/accessories/social/ttcc_acc_cardTopHat',
    'phase_4/models/accessories/social/ttcc_acc_butter',
    'phase_4/models/accessories/bosses/hat_rainmaker',
    'phase_4/models/accessories/social/ttcc_acc_hairbow',
    'phase_4/models/accessories/bosses/hat_firestarter',
    'phase_4/models/accessories/social/ttcc_acc_painter_beret',
    'phase_4/models/accessories/bosses/hat_witchhunter',
    'phase_4/models/accessories/apriltoons/cc_m_acc_hat_goon_patrol',
    'phase_4/models/accessories/apriltoons/cc_m_acc_hat_goon_security',
    'phase_4/models/accessories/apriltoons/cc_m_acc_hat_cog_bucket',
    'phase_4/models/accessories/apriltoons/cc_m_acc_hat_low_baller',
    'phase_4/models/accessories/apriltoons/cc_m_acc_hat_high_roller',
    'phase_4/models/accessories/social/cyberpunk/cc_m_acc_hat_cyberpunk',
    'phase_4/models/accessories/halloween/cc_m_acc_hat_headphones_spy',
    'phase_4/models/accessories/halloween/cc_m_acc_hat_pirate_ghost',
]
HatTextures = [
    None,
    # we omit ribbonPink since that is the default ribbon texture
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonRed.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonPurple.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_heartYellow.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_topHatBlue.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_safariBrown.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_safariGreen.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_baseballBlue.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_baseballOrange.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonYellow.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonChecker.png',  # 10
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonLtRed.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonRainbow.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_baseballYellow.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_baseballRed.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_baseballTeal.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonPinkDots.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_baseballPurple.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonCheckerGreen.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_partyToon.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_tiaraBlue.png',  # 20
    'phase_4/maps/halloween/accessories_textures/cc_t_acc_hat_wizard_enchanted_stars_purple.png',
    'phase_4/maps/halloween/accessories_textures/cc_t_acc_hat_wizard_enchanted_stars_blue.png',
    'phase_4/maps/halloween/accessories_textures/cc_t_acc_hat_wizard_enchanted_stars_black.png',
    'phase_4/maps/halloween/accessories_textures/cc_t_acc_hat_wizard_enchanted_stars_green.png',
    'phase_4/maps/halloween/accessories_textures/cc_t_acc_hat_wizard_enchanted_stars_red.png',
    'phase_4/maps/halloween/accessories_textures/cc_t_acc_hat_wizard_enchanted_stars_pink.png',
    'phase_4/maps/halloween/accessories_textures/tt_t_chr_avt_acc_hat_space_helm.png',
    'phase_4/maps/halloween/accessories_textures/tt_t_chr_avt_acc_hat_ribbonBLACK.png',
    'phase_13/maps/events/btl/accessories/angel-demon-blue.png',
    'phase_13/maps/events/btl/accessories/angel-demon-green.png',   # 30
    'phase_13/maps/events/btl/accessories/angel-demon-orange.png',
    'phase_13/maps/events/btl/accessories/angel-demon-purple.png',
    'phase_13/maps/events/btl/accessories/angel-demon-red.png',
    'phase_13/maps/events/btl/accessories/tt_t_chr_avt_acc_hat_NurseHat.png',
    'phase_13/maps/events/btl/accessories/btl_spincjtie.png',
    'phase_13/maps/events/halloween/tt_t_chr_avt_acc_hat_ribbon_candyCorn.png',
    'phase_13/maps/events/btl/accessories/angel-demon-yellow.png',
    'phase_4/maps/winter/ski_helmet/ski_helmet_blue.png',
    'phase_4/maps/winter/ski_helmet/ski_helmet_green.png',
    'phase_4/maps/winter/ski_helmet/ski_helmet_grey.png',   # 40
    'phase_4/maps/winter/ski_helmet/ski_helmet_pink.png',
    'phase_4/maps/winter/ski_helmet/ski_helmet_rainbow.png',
    'phase_4/maps/winter/ski_helmet/ski_helmet_red.png',
    'phase_13/maps/events/btl/accessories/seven_fedora.png',
    'phase_13/maps/events/apriltoons/accessories/jester_hat.png',
    'phase_13/maps/events/apriltoons/accessories/jesterblack_hat.png',
    'phase_13/maps/events/btl/accessories/atticushat.png',
    'phase_13/maps/events/july4/accessories/grill.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonBlue.png',
    'phase_4/maps/social/gumball/ttcc_acc_donutblue.png',   # 50
    'phase_4/maps/social/gumball/ttcc_acc_donutchocolate.png',
    'phase_4/maps/social/gumball/ttcc_acc_donutlemon.png',
    'phase_4/maps/social/gumball/ttcc_acc_donutvanilla.png',
    'phase_4/maps/social/gumball/ttcc_acc_flowercrown_blue.png',
    'phase_4/maps/social/gumball/ttcc_acc_flowercrown_cyan.png',
    'phase_4/maps/social/gumball/ttcc_acc_flowercrown_cyanpurple.png',
    'phase_4/maps/social/gumball/ttcc_acc_flowercrown_green.png',
    'phase_4/maps/social/gumball/ttcc_acc_flowercrown_orange.png',
    'phase_4/maps/social/gumball/ttcc_acc_flowercrown_orangepink.png',
    'phase_4/maps/social/gumball/ttcc_acc_flowercrown_pink.png',    # 60
    'phase_4/maps/social/gumball/ttcc_acc_flowercrown_pinkblue.png',
    'phase_4/maps/social/gumball/ttcc_acc_flowercrown_purple.png',
    'phase_4/maps/social/gumball/ttcc_acc_flowercrown_red.png',
    'phase_4/maps/social/gumball/ttcc_acc_flowercrown_redyellow.png',
    'phase_4/maps/social/gumball/ttcc_acc_flowercrown_yellow.png',
    'phase_4/maps/social/gumball/ttcc_acc_rosecrown_blue.png',
    'phase_4/maps/social/gumball/ttcc_acc_rosecrown_cyan.png',
    'phase_4/maps/social/gumball/ttcc_acc_rosecrown_green.png',
    'phase_4/maps/social/gumball/ttcc_acc_rosecrown_orange.png',
    'phase_4/maps/social/gumball/ttcc_acc_rosecrown_pink.png',  # 70
    'phase_4/maps/social/gumball/ttcc_acc_rosecrown_purple.png',
    'phase_4/maps/social/gumball/ttcc_acc_rosecrown_red.png',
    'phase_4/maps/social/gumball/ttcc_acc_rosecrown_yellow.png',
    'phase_4/maps/social/gumball/ttcc_acc_hairbow_B.png',
    'phase_4/maps/social/gumball/ttcc_acc_hairbow_BR.png',
    'phase_4/maps/social/gumball/ttcc_acc_hairbow_G.png',
    'phase_4/maps/social/gumball/ttcc_acc_hairbow_OR.png',
    'phase_4/maps/social/gumball/ttcc_acc_hairbow_P.png',
    'phase_4/maps/social/gumball/ttcc_acc_hairbow_PU.png',
    'phase_4/maps/social/gumball/ttcc_acc_hairbow_RB.png',  # 80
    'phase_4/maps/apriltoons/accessories/cc_t_acc_hat_goon_patrol_orange.png',
    'phase_4/maps/apriltoons/accessories/cc_t_acc_hat_goon_patrol_red.png',
    'phase_4/maps/apriltoons/accessories/cc_t_acc_hat_goon_patrol_purple.png',
    'phase_4/maps/apriltoons/accessories/cc_t_acc_hat_foreman.png',

    # gumball bowties, hat edition
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_black.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_blackwhite.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_blue.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_gray.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_green.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_orange.png',   # 90
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_pink.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_pinkblack.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_polkadot.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_purple.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_purpleorange.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_red.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_yellow.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_yellowblack.png',

    # pride 2023 bowties
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_ace.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_aro.png',   # 100
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_bi.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_gay.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_genderfluid.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_lesbian.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_lgbt.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_nb.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_pan.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_trans.png',

    'phase_4/maps/halloween/accessories_textures/cc_t_acc_hat_wizard_enchanted_traffic_orange.png',
    'phase_4/maps/halloween/accessories_textures/cc_t_acc_hat_headphones_spy_1.png',  # 110
    'phase_4/maps/winter/accessories_textures/cc_t_acc_hat_elf_whiteRed.png',
]
GlassesModels = [
    None,
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_roundGlasses',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_miniblinds',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_narrowGlasses',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_starGlasses',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_squareRims',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_3dGlasses',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_aviator',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_catEyeGlasses',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_dorkGlasses',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_jackieOShades',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_scubaMask',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_goggles',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_grouchoMarxEyebrow',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_heartGlasses',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_insectEyeGlasses',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_masqueradeTypeMask',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_masqueradeTypeMask3',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_monocle',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_mouthGlasses',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_eyepatch',
    'phase_4/models/accessories/tt_m_chr_avt_acc_msk_alienGlasses',
    'phase_4/models/accessories/halloween/tt_m_chr_avt_acc_msk_spiderglasses',
    'phase_4/models/accessories/halloween/tt_m_chr_avt_acc_msk_hypno',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_msk_snow_goggles_blue',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_msk_snow_goggles_green',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_msk_snow_goggles_grey',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_msk_snow_goggles_pink',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_msk_snow_goggles_rainbow',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_msk_snow_goggles_red',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_msk_snow_goggles_vintage',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_msk_2019_glasses',
    'phase_4/models/accessories/apriltoons/tt_m_chr_avt_acc_msk_flunky_glasses',
    'phase_4/models/accessories/apriltoons/tt_m_chr_avt_acc_msk_eye_spring',
    'phase_4/models/accessories/apriltoons/tt_m_chr_avt_acc_msk_flight_goggles',
    'phase_4/models/accessories/outback/sunnyglasses',
    'phase_13/models/events/btl/accessories/x_glasses',
    'phase_4/models/accessories/winter/giftglasses',
    'phase_4/models/accessories/winter/2020_glasses',
    'phase_13/models/events/btl/accessories/mustache',
    'phase_4/models/accessories/social/discord/cc_m_acc_gl_promo_chairman',
    'phase_4/models/accessories/winter/ornament_glasses',
    'phase_4/models/accessories/halloween/tt_t_chr_avt_acc_hat_hwtown_mask',
    'phase_4/models/accessories/halloween/tt_m_chr_avt_acc_msk_countmask',
    'phase_4/models/accessories/winter/2022_glasses',
    'phase_4/models/accessories/apriltoons/scifi_visor',
    'phase_4/models/accessories/social/bro/brovinci_glasses',
    'phase_4/models/accessories/bosses/glasses_mouthpiece',
    'phase_4/models/accessories/social/ttcc_acc_funkyglasses',
    'phase_4/models/accessories/social/ttcc_acc_sleepingmask',
    'phase_4/models/accessories/bosses/glasses_pacesetter',
    'phase_4/models/accessories/social/ttcc_acc_cardGlassesBlack',
    'phase_4/models/accessories/social/ttcc_acc_cardGlassesRed',
    'phase_6/models/miniboss/majorplayer_rose',
    'phase_4/models/accessories/social/ttcc_acc_painter_paintbrush',
    'phase_4/models/accessories/social/ttcc_acc_cookieglasses',
    'phase_4/models/accessories/apriltoons/cc_m_acc_msk_low_baller',
    'phase_4/models/accessories/social/cyberpunk/cc_m_acc_msk_cyberpunk',
    'phase_4/models/accessories/halloween/cc_m_acc_face_msk_pirate_ghost',
    'phase_4/models/accessories/halloween/cc_m_acc_face_gl_goggles_spy',
]
GlassesTextures = [
    None,
    'phase_4/maps/tt_t_chr_avt_acc_msk_masqueradeTypeMask2.png',
    'phase_4/maps/tt_t_chr_avt_acc_msk_masqueradeTypeMask4.png',
    'phase_4/maps/tt_t_chr_avt_acc_msk_masqueradeTypeMask5.png',
    'phase_4/maps/tt_t_chr_avt_acc_msk_eyepatchGems.png',
    'phase_4/maps/tt_t_chr_avt_acc_msk_eyepatchSkull.png',
    'phase_4/maps/halloween/accessories_textures/tt_t_chr_avt_acc_hallowen_hypno_2019.png',
    'phase_13/maps/events/btl/accessories/x_glasses.png',
    'phase_13/maps/events/btl/accessories/x_glasses_GOLD.png',
    'phase_13/maps/events/btl/accessories/x_glasses_GREEN.png',
    'phase_13/maps/events/btl/accessories/x_glasses_RAINBOW.png',
    'phase_13/maps/events/btl/accessories/x_glasses_RED.png',
    'phase_4/maps/winter/gift_glasses/giftglasses_blue.png',
    'phase_4/maps/winter/gift_glasses/giftglasses_cyan.png',
    'phase_4/maps/winter/gift_glasses/giftglasses_green.png',
    'phase_4/maps/winter/gift_glasses/giftglasses_orange.png',
    'phase_4/maps/winter/gift_glasses/giftglasses_pink.png',
    'phase_4/maps/winter/gift_glasses/giftglasses_purple.png',
    'phase_4/maps/winter/gift_glasses/giftglasses_red.png',
    'phase_4/maps/winter/gift_glasses/giftglasses_yellow.png',
    'phase_13/maps/events/btl/accessories/seven_hypno.png',
    'phase_13/maps/events/btl/accessories/mustache.png',
    # note: this is here because the model itself did not have a texture, so a setTexture was applied with the below
    # however, the model's texture has now been fixed, meaning, this texture entry is not needed anymore
    # (but will be difficult to remove at ease)
    'phase_4/maps/social/discord/cc_t_acc_gl_promo_chairman.png',
    'phase_13/maps/events/halloween/hypno_blue.png',
    'phase_13/maps/events/halloween/hypno_lightblue.png',
    'phase_13/maps/events/halloween/hypno_orange.png',
    'phase_13/maps/events/halloween/hypno_pink.png',
    'phase_13/maps/events/halloween/hypno_yellow.png',
    'phase_13/maps/events/halloween/hypno_purple.png',
    'phase_13/maps/events/halloween/hypno_darkpurple.png',
    'phase_13/maps/events/halloween/hypno_rainbow.png',

    'phase_4/maps/winter/ornament_glasses/orn_glasses_black.png',
    'phase_4/maps/winter/ornament_glasses/orn_glasses_blue.png',
    'phase_4/maps/winter/ornament_glasses/orn_glasses_cyan.png',
    'phase_4/maps/winter/ornament_glasses/orn_glasses_green.png',
    'phase_4/maps/winter/ornament_glasses/orn_glasses_orange.png',
    'phase_4/maps/winter/ornament_glasses/orn_glasses_pink.png',
    'phase_4/maps/winter/ornament_glasses/orn_glasses_purple.png',
    'phase_4/maps/winter/ornament_glasses/orn_glasses_rainbow.png',
    'phase_4/maps/winter/ornament_glasses/orn_glasses_red.png',
    'phase_4/maps/winter/ornament_glasses/orn_glasses_white.png',
    'phase_4/maps/winter/ornament_glasses/orn_glasses_yellow.png',
]
BackpackModels = [
    None,
    'phase_4/models/accessories/bosses/backpack_pacesetter',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_batWings',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_beeWings',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_dragonFlyWings',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_scubaTank',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_sharkFin',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_angelWings',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_backpackWithToys',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_butterflyWings',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_dragonWing',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_jetPack',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_spiderLegs',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_stuffedAnimalBackpackA',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_birdWings',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_stuffedAnimalBackpackCat',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_stuffedAnimalBackpackDog',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_airplane',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_woodenSword',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_supertoonCape',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_vampireCape',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_dinosaurTail',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_band',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_gags',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_flunky',
    'phase_4/models/accessories/halloween/tt_t_chr_avt_acc_pac_space_back',
    'phase_4/models/accessories/halloween/tt_t_chr_avt_acc_pac_witchbroom_back',
    'phase_4/models/accessories/halloween/tt_t_chr_avt_acc_pac_reapercape_back',
    'phase_4/models/accessories/halloween/tt_t_chr_avt_acc_pac_draculacape_back',
    'phase_4/models/accessories/halloween/tt_t_chr_avt_acc_pac_trickortreat_back',
    'phase_4/models/accessories/halloween/tt_t_chr_avt_acc_pac_potions_back',
    'phase_4/models/accessories/winter/tt_t_chr_avt_acc_pac_tin_tradi',
    'phase_4/models/accessories/winter/tt_t_chr_avt_acc_pac_tin_humble',
    'phase_4/models/accessories/winter/tt_t_chr_avt_acc_pac_tin_regal',
    'phase_4/models/accessories/winter/tt_t_chr_avt_acc_pac_ragdoll_humble',
    'phase_4/models/accessories/winter/tt_t_chr_avt_acc_pac_ragdoll_regal',
    'phase_4/models/accessories/winter/tt_t_chr_avt_acc_pac_ragdoll_tradi',
    'phase_4/models/accessories/winter/cc_m_acc_bp_bag_presents',
    'phase_4/models/accessories/winter/cc_m_acc_bp_snowboard',
    'phase_4/models/accessories/winter/cc_m_acc_bp_candycane',
    'phase_4/models/accessories/winter/tt_m_chr_avt_acc_pac_2019_scarf',
    'phase_4/models/accessories/2019valentoon/tt_m_chr_avt_acc_pac_cupidbow',
    'phase_4/models/accessories/2019valentoon/tt_m_chr_avt_acc_pac_cupidbow_quiver',
    'phase_4/models/accessories/social/doe/tt_m_chr_avt_acc_pac_doe_bandana',
    'phase_4/models/accessories/apriltoons/tt_t_chr_avt_acc_pac_prop_pack',
    'phase_4/models/accessories/apriltoons/tt_t_chr_avt_acc_pac_kite',
    'phase_4/models/accessories/apriltoons/tt_t_chr_avt_acc_pac_hangglider',
    'phase_4/models/accessories/apriltoons/tt_t_chr_avt_acc_pac_aviatorscarf',
    'phase_4/models/accessories/apriltoons/tt_t_chr_avt_acc_pac_telescope',
    'phase_4/models/accessories/apriltoons/tt_m_chr_avt_acc_pac_pinwheel_bowtie',
    'phase_4/models/accessories/outback/outback_backpack',
    'phase_4/models/accessories/outback/bandana',
    'phase_4/models/accessories/outback/boomerang',
    'phase_4/models/accessories/outback/didgeridoo',
    'phase_13/models/events/btl/accessories/alien_backpack',
    'phase_13/models/events/btl/accessories/angel_wings',
    'phase_13/models/events/btl/accessories/demon_wings',
    'phase_13/models/events/btl/accessories/ridinghood_cloak',
    'phase_13/models/events/btl/accessories/btl_blood_lollipop',
    'phase_13/models/events/btl/accessories/btl_cjtie',
    'phase_13/models/events/btl/accessories/sailor_collar',
    'phase_13/models/events/btl/accessories/sailor_collar_bow',
    'phase_13/models/events/btl/accessories/btl_backstab',
    'phase_13/models/events/btl/accessories/btl_gavel_back',
    'phase_13/models/events/btl/accessories/spellbook_back',
    'phase_13/models/events/btl/accessories/gravestone_backpack',
    'phase_5/models/props/tnt-mod',
    'phase_4/models/accessories/winter/retroscarf',
    'phase_3.5/models/props/bottle',
    'phase_3.5/models/props/squirting-flower',
    'phase_5/models/props/magnet',
    'phase_3.5/models/props/joybuzz',
    'phase_13/models/events/apriltoons/fusionpack',
    'phase_13/models/events/apriltoons/clown_bowtie',
    'phase_4/models/accessories/social/discord/cc_m_acc_bp_promo_chairpack',
    'phase_13/models/events/apriltoons/jester_collar',
    'phase_13/models/events/easter2020/bunny_backpack',
    'phase_13/models/events/july4/spatula',
    'phase_13/models/events/july4/firework',
    'phase_13/models/events/halloween/pumpkin_candy',
    'phase_13/models/events/thanksgiving/plate_pack',
    'phase_4/models/accessories/winter/cc_m_acc_bp_extinguisher',
    'phase_4/models/accessories/winter/cc_m_acc_bp_cornucopia',
    'phase_4/models/accessories/winter/cc_m_acc_bp_cloak_future_wings',
    'phase_4/models/accessories/winter/cc_m_acc_bp_cloak_future_cape',
    'phase_4/models/accessories/winter/cc_m_acc_bp_cloak_future_combo',
    'phase_13/models/events/apriltoons/ottoman_tie',
    'phase_4/models/accessories/halloween/tt_t_chr_avt_acc_pac_hwtown_cape_back',
    'phase_4/models/accessories/halloween/tt_t_chr_avt_acc_pac_skeleton_back',
    'phase_4/models/accessories/halloween/tt_t_chr_avt_acc_pac_eyebow_back',
    'phase_4/models/accessories/halloween/tt_t_chr_avt_acc_pac_mystery_bowtie_back',
    'phase_4/models/accessories/social/newstoon_suitcase',
    'phase_4/models/accessories/social/newstoon_camera',
    'phase_4/models/accessories/tt_m_chr_avt_acc_pac_ribbon',
    'phase_4/models/accessories/pride/prideCape',
    'phase_4/models/accessories/social/doodle_pack',
    'phase_4/models/accessories/social/bro/brovinci_necklace',
    'phase_4/models/accessories/bosses/backpack_moneybag',
    'phase_4/models/accessories/bosses/backpack_pitchfork',
    'phase_4/models/accessories/social/ttcc_acc_wingsuit_wings',
    'phase_4/models/accessories/social/ttcc_acc_pillowpack',
    'phase_4/models/accessories/bosses/backpack_bellringer',
    'phase_4/models/accessories/bosses/backpack_majorplayer',
    'phase_4/models/accessories/bosses/backpack_firestarter',
    'phase_4/models/accessories/bosses/backpack_gatekeeper',
    'phase_4/models/accessories/social/ttcc_acc_fruitbasket',
    'phase_4/models/accessories/social/ttcc_acc_retrobag',
    'phase_4/models/accessories/social/ttcc_acc_breadbag',
    'phase_4/models/accessories/social/ttcc_acc_chefscarf',
    'phase_4/models/accessories/social/ttcc_acc_paddle',
    'phase_4/models/accessories/social/ttcc_acc_painter_palette',
    'phase_4/models/accessories/bosses/backpack_pacesetter',
    'phase_9/models/cogHQ/FactoryGearB',
    'phase_4/models/accessories/social/cyberpunk/cc_m_acc_pac_cyberpunk',
    'phase_4/models/accessories/halloween/cc_m_acc_bp_pirate_ghost',
    'phase_4/models/accessories/winter/cc_m_acc_nec_bowtie_elf',
]
BackpackTextures = [
    None,
    'phase_4/maps/tt_t_chr_avt_acc_pac_backpackOrange.png',
    'phase_4/maps/tt_t_chr_avt_acc_pac_backpackPurple.png',
    'phase_4/maps/tt_t_chr_avt_acc_pac_backpackPolkaDotRed.png',
    'phase_4/maps/tt_t_chr_avt_acc_pac_backpackPolkaDotYellow.png',
    'phase_4/maps/tt_t_chr_avt_acc_pac_angelWingsMultiColor.png',
    'phase_4/maps/tt_t_chr_avt_acc_pac_butterflyWingsStyle2.png',
    'phase_13/maps/events/btl/accessories/angel-demon-blue.png',
    'phase_13/maps/events/btl/accessories/angel-demon-green.png',
    'phase_13/maps/events/btl/accessories/angel-demon-orange.png',
    'phase_13/maps/events/btl/accessories/angel-demon-purple.png',  # 10
    'phase_13/maps/events/btl/accessories/angel-demon-red.png',
    'phase_13/maps/events/btl/accessories/btl_blood_lollipop.png',
    'phase_13/maps/events/btl/accessories/btl_spincjtie.png',
    'phase_13/maps/events/btl/accessories/angel-demon-yellow.png',

    'phase_13/maps/events/btl/accessories/sailor_collar_blue.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_cyan.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_green.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_orange.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_pink.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_purple.png',  # 20
    'phase_13/maps/events/btl/accessories/sailor_collar_red.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_black.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_yellow.png',

    'phase_13/maps/events/btl/accessories/sailor_collar_bow_blue.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_bow_cyan.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_bow_green.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_bow_orange.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_bow_pink.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_bow_purple.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_bow_red.png',  # 30
    'phase_13/maps/events/btl/accessories/sailor_collar_bow_black.png',
    'phase_13/maps/events/btl/accessories/sailor_collar_bow_yellow.png',
    'phase_13/maps/events/btl/accessories/btl_gavel_back.png',
    'phase_13/maps/events/btl/accessories/btl_backstab.png',
    'phase_4/maps/bosses/cc_t_acc_bp_book_clo.png',
    'phase_13/maps/events/btl/accessories/gravestone_backpack.png',
    'phase_4/maps/winter/homemade_ragdoll/ragdoll_homemade_bow.png',
    'phase_4/maps/winter/homemade_tin_soldier/soldier_homemade_key.png',
    'phase_4/maps/winter/2020_outfit/newyears_scarf20.png',
    'phase_5/maps/gag_palette_3.png',  # 40
    'phase_4/maps/social/discord/cc_t_acc_bp_promo_chairpack.png',
    'phase_13/maps/events/apriltoons/accessories/jester_collar.png',
    'phase_13/maps/events/btl/accessories/lawbot_bowtie.png',
    'phase_13/maps/events/july4/accessories/spatula.png',
    'phase_13/maps/events/july4/accessories/firework.png',
    'phase_13/maps/events/halloween/spellbook.png',
    'phase_13/maps/events/halloween/hw_gravestone.png',
    'phase_4/maps/winter/2021_outfit/scarf.png',
    'phase_4/maps/social/newstoon_blue/newstoon-blue_bowtie.png',
    'phase_4/maps/winter/2022_outfit/2022_scarf.png',  # 50

    # Bowtie Support
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonRed.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonPurple.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonYellow.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonChecker.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonLtRed.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonRainbow.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonPinkDots.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonCheckerGreen.png',
    'phase_4/maps/tt_t_chr_avt_acc_hat_ribbonBlue.png',
    'phase_13/maps/events/halloween/tt_t_chr_avt_acc_hat_ribbon_candyCorn.png',  # 60
    'phase_4/maps/halloween/accessories_textures/tt_t_chr_avt_acc_hat_ribbonBLACK.png',

    # pride capes
    'phase_4/maps/pride/ttcc_acc_bp_capePride_2.png',
    'phase_4/maps/pride/ttcc_acc_bp_capePride_3.png',
    'phase_4/maps/pride/ttcc_acc_bp_capePride_4.png',
    'phase_4/maps/pride/ttcc_acc_bp_capePride_5.png',
    'phase_4/maps/pride/ttcc_acc_bp_capePride_6.png',
    'phase_4/maps/pride/ttcc_acc_bp_capePride_7.png',
    'phase_4/maps/pride/ttcc_acc_bp_capePride_8.png',
    'phase_4/maps/pride/ttcc_acc_bp_capePride_9.png',

    'phase_4/maps/social/doctor_toon/doctor_doodle_pack.png',  # 70
    'phase_4/maps/social/gumball/ttcc_acc_engineer_bandana.png',

    'phase_4/maps/social/gumball/ttcc_acc_bowtie_black.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_blackwhite.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_blue.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_gray.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_green.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_orange.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_pink.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_pinkblack.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_polkadot.png',  # 80
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_purple.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_purpleorange.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_red.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_yellow.png',
    'phase_4/maps/social/gumball/ttcc_acc_bowtie_yellowblack.png',
    'phase_4/maps/winter/2023_outfit/2023_scarf.png',

    # pride 2023 bowties + cape
    'phase_4/maps/pride/cc_t_acc_bp_cape_pride_gay.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_ace.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_aro.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_bi.png',    # 90
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_gay.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_genderfluid.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_lesbian.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_lgbt.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_nb.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_pan.png',
    'phase_4/maps/pride/cc_t_acc_bowtie_pride_trans.png',

    'phase_4/maps/winter/accessories_textures/cc_t_acc_nec_scarf_nye_24.png',

]
ShoesModels = [
    'feet',
    'shoes',
    'boots_short',
    'boots_long'
]
ShoesTextures = [
    'phase_3/maps/tt_t_chr_avt_acc_sho_athleticGreen.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_athleticRed.png',
    'phase_3/maps/tt_t_chr_avt_acc_sho_docMartinBootsGreen.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_converseStyleGreen.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_wingtips.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_maryJaneShoes.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_deckShoes.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_athleticYellow.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_converseStyleBlack.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_converseStyleWhite.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_converseStylePink.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_cowboyBoots.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_fashionBootsPurple.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_hiTopSneakers.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_maryJaneShoesBrown.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_maryJaneShoesRed.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_superToonRedBoots.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_tennisShoesGreen.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_tennisShoesPink.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_converseStyleRed.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_docMartinBootsAqua.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_docMartinBootsBrown.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_docMartinBootsYellow.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_fashionBootsBlueSquares.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_fashionBootsGreenHearts.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_fashionBootsGreyDots.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_fashionBootsOrangeStars.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_fashionBootsPinkStars.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_loafers.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_maryJaneShoesPurple.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_motorcycleBoots.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_oxfords.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_rainBootsPink.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_santaBoots.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_winterBootsBeige.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_winterBootsPink.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_workBoots.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_converseStyleYellow.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_docMartinBootsPink.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_hiTopSneakersPink.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_rainBootsRedDots.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_tennisShoesPurple.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_tennisShoesViolet.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_tennisShoesYellow.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_rainBootsBlue.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_rainBootsYellow.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_athleticBlack.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_pirate.png',
    'phase_4/maps/tt_t_chr_avt_acc_sho_dinosaur.png',
    'phase_4/maps/halloween/accessories_textures/tt_t_chr_avt_acc_sho_space_boots.png',
    'phase_4/maps/halloween/accessories_textures/tt_t_chr_avt_acc_sho_witch.png',
    'phase_4/maps/halloween/accessories_textures/tt_t_chr_avt_acc_sho_skeleton.png',
    'phase_4/maps/halloween/accessories_textures/tt_t_chr_avt_acc_sho_alchemist.png',
    'phase_4/maps/winter/accessories_textures/humble-ragdoll-shoes.png',
    'phase_4/maps/winter/accessories_textures/regal-ragdoll-shoes.png',
    'phase_4/maps/winter/accessories_textures/tradi-ragdoll-shoes.png',
    'phase_4/maps/winter/accessories_textures/humble-tinsoldier-shoes.png',
    'phase_4/maps/winter/accessories_textures/regal-tinsoldier-shoes.png',
    'phase_4/maps/winter/accessories_textures/tradi-tinsoldier-shoes.png',
    'phase_4/maps/winter/vintage_snow_outfit/tt_t_chr_avt_acc_sho_vintage_snow.png',
    'phase_4/maps/apriltoons/aviator_outfit/aviator_boots.png',
    'phase_4/maps/apriltoons/wingsuit_outfit/wingsuit_boots.png',
    'phase_4/maps/outback/outback_shoes.png',
    'phase_13/maps/events/btl/accessories/pumpkin_shoes.png',
    'phase_4/maps/halloween/lazy_bones_outfit/lazy_bones_shoes.png',
    'phase_4/maps/winter/homemade_ragdoll/ragdoll_homemade_boots.png',
    'phase_4/maps/winter/homemade_tin_soldier/soldier_homemade_boots.png',
    'phase_4/maps/winter/retro_winterwear/wintersuit_shoes.png',
    'phase_4/maps/winter/retro_winterwear/winterdress_shoes.png',
    'phase_13/maps/events/apriltoons/accessories/btl_lbhq_shoes.png',
    'phase_13/maps/events/apriltoons/accessories/triplerainbow_shoes.png',
    'phase_4/maps/social/discord/cc_t_acc_sho_promo_chairman.png',
    'phase_13/maps/events/halloween/phantoon_boots.png',
    'phase_4/maps/tumbles/tumbles_shoes.png',
    'phase_4/maps/halloween/halloweentown_outfit/hwtown_boots.png',
    'phase_4/maps/bosses/shoes_diver.png',
    'phase_4/maps/social/gumball/ttcc_acc_engineer_shoes.png',
    'phase_4/maps/social/gumball/ttcc_acc_fruitpieshoes.png',
    'phase_4/maps/social/gumball/ttcc_acc_cardBoots_red.png',
    'phase_4/maps/social/gumball/ttcc_acc_cardBoots_black.png',
    'phase_4/maps/social/gumball/ttcc_acc_gator_shoes.png',
    'phase_4/maps/social/gumball/ttcc_acc_painter_shoes.png',
    'phase_4/maps/bosses/ttcc_acc_armored_boots.png',
    'phase_4/maps/social/cyberpunk/cc_t_acc_shoes_cyberpunk.png',
    'phase_4/maps/halloween/accessories_textures/cc_t_acc_sho_md_pirate_ghost_green.png',
    'phase_4/maps/halloween/accessories_textures/cc_t_acc_sho_md_spy_purple.png',
]
HatStyles = {
    'none': [0, 0, 0],
    'hbb1': [1, 0, 0],  # Green Baseball Cap
    'hsf1': [2, 0, 0],
    'hsf2': [2, 5, 0],
    'hsf3': [2, 6, 0],
    'hht1': [4, 0, 0],  # Pink Heart
    'hht2': [4, 3, 0],  # Yellow Heart
    'htp1': [5, 0, 0],
    'htp2': [5, 4, 0],
    'hav1': [6, 0, 0],
    'hfp1': [7, 0, 0],
    'hsg1': [8, 0, 0],
    'hwt1': [9, 0, 0],
    'hfz1': [10, 0, 0],
    'hgf1': [11, 0, 0],
    'hpt1': [12, 0, 0],
    'hpt2': [12, 19, 0],
    'hpb1': [13, 0, 0],
    'hcr1': [14, 0, 0],
    'hbb2': [1, 7, 0],
    'hbb3': [1, 8, 0],
    'hcw1': [15, 0, 0],
    'hpr1': [16, 0, 0],
    'hpp1': [17, 0, 0],
    'hfs1': [18, 0, 0],
    'hsb1': [19, 0, 0],
    'hst1': [20, 0, 0],
    'hat1': [22, 0, 0],
    'hhd1': [23, 0, 0],
    'hbw1': [24, 0, 0],
    'hch1': [25, 0, 0],
    'hdt1': [26, 0, 0],
    'hft1': [27, 0, 0],
    'hfd1': [28, 0, 0],
    'hmk1': [29, 0, 0],
    'hft2': [30, 0, 0],
    'hhd2': [31, 0, 0],
    'hrh1': [33, 0, 0],
    'hhm1': [34, 0, 0],
    'hat2': [35, 0, 0],
    'htr1': [36, 0, 0],
    'hhm2': [37, 0, 0],
    'hwz1': [38, 0, 0],
    'hwz2': [39, 0, 0],
    'hhm3': [40, 0, 0],
    'hhm4': [41, 0, 0],
    'hfp2': [42, 0, 0],
    'hhm5': [43, 0, 0],
    'hnp1': [44, 0, 0],
    'hpc2': [45, 0, 0],
    'hph1': [46, 0, 0],
    'hwg1': [47, 0, 0],
    'hbb4': [1, 13, 0],
    'hbb5': [1, 14, 0],
    'hbb6': [1, 15, 0],
    'hsl1': [48, 0, 0],
    'hfr1': [49, 0, 0],
    'hby1': [50, 0, 0],
    'hjh1': [51, 0, 0],
    'hbb7': [1, 17, 0],
    'hwt2': [52, 0, 0],
    'hhw2': [54, 0, 0],
    'hob1': [55, 0, 0],
    'hbn1': [56, 0, 0],
    'hrb1': [3, 0, 0],  # Pink Bow
    'hrb2': [3, 1, 0],  # Red Bow
    'hrb3': [3, 2, 0],  # Purple Bow
    'hsu1': [21, 0, 0],
    'hrb4': [3, 9, 0],  # Yellow Bow
    'hrb5': [3, 10, 0],  # Checker Bow
    'hrb6': [3, 11, 0],  # Light Red Bow
    'hrb7': [3, 12, 0],  # Rainbow Bow
    'hpc1': [32, 0, 0],
    'hrb8': [3, 16, 0],  # Pink Dots Bow
    'hrb9': [3, 18, 0],  # Green Checker Bow
    'hhw1': [53, 0, 0],
    'space_helm': [57, 0, 0],
    'bat_bow': [58, 0, 0],
    'cauldron_hat': [59, 0, 0],
    'electric_bolts': [60, 0, 0],
    'pumpkin_bucket': [61, 0, 0],
    'scarecrow_hat': [62, 0, 0],
    'wizard_black': [39, 23, 0],
    'wizard_pink': [39, 26, 0],
    'wizard_red': [39, 25, 0],
    'wizard_green': [39, 24, 0],
    'wizard_blue': [39, 22, 0],
    'frank_head': [63, 0, 0],
    'alchemist_goggles': [64, 0, 0],
    'tiw_bow': [3, 28, 0],  # Toons in wonderland (Black bow)
    'bobble_blue': [65, 0, 0],
    'bobble_green': [66, 0, 0],
    'bobble_grey': [67, 0, 0],
    'bobble_pink': [68, 0, 0],
    'bobble_rainbow': [69, 0, 0],
    'bobble_red': [70, 0, 0],
    'santa_red': [71, 0, 0],
    'santa_rainbow': [72, 0, 0],
    'elf_green': [73, 0, 0],  # OLD green elf hat --> green santa hat
    'elf_red': [74, 0, 0],  # Red santa hat
    'star_hat': [75, 0, 0],
    'tin_humble': [76, 0, 0],
    'tin_regal': [77, 0, 0],
    'tin_tradi': [78, 0, 0],
    'ragdoll_humble': [79, 0, 0],
    'ragdoll_tradi': [80, 0, 0],
    'ragdoll_regal': [81, 0, 0],
    'antlers': [82, 0, 0],
    'doe_beanie': [83, 0, 0],
    'webster_bookhat': [84, 0, 0],
    'umbrella': [85, 0, 0],
    'aviator_hat': [86, 0, 0],
    'cake_hat': [87, 0, 0],
    'outback_hat': [88, 0, 0],
    'outback_corkhat': [89, 0, 0],
    'outback_geckohat': [90, 0, 0],
    'alien_hat': [91, 0, 0],
    'angel_halo': [92, 0, 0],
    'angel_halo_blue': [92, 29, 0],
    'angel_halo_green': [92, 30, 0],
    'angel_halo_orange': [92, 31, 0],
    'angel_halo_purple': [92, 32, 0],
    'angel_halo_red': [92, 33, 0],
    'demon_horns': [93, 0, 0],
    'demon_horns_blue': [93, 29, 0],
    'demon_horns_green': [93, 30, 0],
    'demon_horns_orange': [93, 31, 0],
    'demon_horns_purple': [93, 32, 0],
    'demon_horns_red': [93, 33, 0],
    'ridinghood_hood': [94, 0, 0],
    'robophones': [95, 0, 0],
    'nurse_hat': [48, 34, 0],
    'spin_doctor_band': [96, 35, 0],
    'candycorn_bow': [3, 36, 0],
    'angel_halo_yellow': [92, 37, 0],
    'demon_horns_yellow': [93, 37, 0],
    'bowling_ball': [97, 0, 0],
    'fruit_pie': [98, 0, 0],
    'ragdoll_hat': [99, 0, 0],
    'ski_helmet': [100, 0, 0],
    'ski_helmet_blue': [100, 38, 0],
    'ski_helmet_green': [100, 39, 0],
    'ski_helmet_gray': [100, 40, 0],
    'ski_helmet_pink': [100, 41, 0],
    'ski_helmet_rainbow': [100, 42, 0],
    'ski_helmet_red': [100, 43, 0],
    'snowman_hat': [101, 0, 0],
    'soldier_hat': [102, 0, 0],
    'tv_hat': [103, 0, 0],
    'seven_fedora': [28, 44, 0],
    'stpats_top_lucky': [104, 0, 0],
    'stpats_top_tart': [105, 0, 0],
    'stpats_band': [106, 0, 0],
    'stpats_clip': [107, 0, 0],
    'rainbow_phones': [108, 0, 0],
    'clown_hat': [109, 0, 0],
    'jester_hat': [110, 45, 0],
    'jester_b_hat': [110, 46, 0],
    'easter_beanie': [111, 0, 0],
    'atticus_hat': [112, 47, 0],
    'diploma': [113, 0, 0],
    'grill': [114, 48, 0],
    'leaf_hat': [115, 0, 0],
    'candle_hat': [116, 0, 0],
    'present_band': [117, 0, 0],
    'future_hood': [118, 0, 0],
    'plant_hat': [119, 0, 0],
    'newstoon_gray_bow': [120, 0, 0],
    'hw_gibus': [121, 0, 0],
    'hat-number1': [122, 0, 0],
    'ribbon_blue': [3, 49, 0],
    'bandana-deluxe': [123, 0, 0],
    'brovinci_hair': [124, 0, 0],
    'hat_icecube': [125, 0, 0],
    'hat_smartcap': [126, 0, 0],
    'hat_clownbeanie': [127, 0, 0],
    'hat_bananahat': [128, 0, 0],
    'hat_wingsuit_helmet': [129, 0, 0],
    'hat_engineer_cap': [130, 0, 0],
    'donuthat_pink': [131, 0, 0],
    'donuthat_blue': [131, 50, 0],
    'donuthat_chocolate': [131, 51, 0],
    'donuthat_lemon': [131, 52, 0],
    'donuthat_vanilla': [131, 53, 0],
    'cruller_beret': [132, 0, 0],
    'flowercrown_white': [133, 0, 0],
    'flowercrown_blue': [133, 54, 0],
    'flowercrown_cyan': [133, 55, 0],
    'flowercrown_cyanpurple': [133, 56, 0],
    'flowercrown_green': [133, 57, 0],
    'flowercrown_orange': [133, 58, 0],
    'flowercrown_orangepink': [133, 59, 0],
    'flowercrown_pink': [133, 60, 0],
    'flowercrown_pinkblue': [133, 61, 0],
    'flowercrown_purple': [133, 62, 0],
    'flowercrown_red': [133, 63, 0],
    'flowercrown_redyellow': [133, 64, 0],
    'flowercrown_yellow': [133, 65, 0],
    'rosecrown_white': [134, 0, 0],
    'rosecrown_blue': [134, 66, 0],
    'rosecrown_cyan': [134, 67, 0],
    'rosecrown_green': [134, 68, 0],
    'rosecrown_orange': [134, 69, 0],
    'rosecrown_pink': [134, 70, 0],
    'rosecrown_purple': [134, 71, 0],
    'rosecrown_red': [134, 72, 0],
    'rosecrown_yellow': [134, 73, 0],
    'hat_chainsaw': [135, 0, 0],
    'hat_multislacker': [136, 0, 0],
    'hat_treekiller': [137, 0, 0],
    'hat_featherbedder': [138, 0, 0],
    'hat_nightcap': [139, 0, 0],
    'hat_blackberet': [140, 0, 0],
    'hat_gumballhat': [141, 0, 0],
    'hat_cardCrown': [142, 0, 0],
    'hat_cardTopHat': [143, 0, 0],
    'hat_butter': [144, 0, 0],
    'hat_rainmaker_depression': [145, 0, 0],
    'hat_gumball_hairbow': [146, 0, 0],
    'hat_firestarter': [147, 0, 0],
    'painter_beret': [148, 0, 0],
    'hat_gumball_hairbow_b': [146, 74, 0],
    'hat_gumball_hairbow_br': [146, 75, 0],
    'hat_gumball_hairbow_g': [146, 76, 0],
    'hat_gumball_hairbow_or': [146, 77, 0],
    'hat_gumball_hairbow_p': [146, 78, 0],
    'hat_gumball_hairbow_pu': [146, 79, 0],
    'hat_gumball_hairbow_rb': [146, 80, 0],
    'hat_witchhunter': [149, 0, 0],
    'hat_goon_patrol_yellow': [150, 0, 0],
    'hat_goon_patrol_orange': [150, 81, 0],
    'hat_goon_patrol_red': [150, 82, 0],
    'hat_goon_patrol_purple': [150, 83, 0],
    'hat_goon_security': [151, 0, 0],
    'hat_foreman': [112, 84, 0],
    'hat_cog_bucket': [152, 0, 0],
    'hat_low_baller': [153, 0, 0],
    'hat_high_roller': [154, 0, 0],
    'gb_hairbow_black': [120, 85, 0],
    'gb_hairbow_blackwhite': [120, 86, 0],
    'gb_hairbow_blue': [120, 87, 0],
    'gb_hairbow_gray': [120, 88, 0],
    'gb_hairbow_green': [120, 89, 0],
    'gb_hairbow_orange': [120, 90, 0],
    'gb_hairbow_pink': [120, 91, 0],
    'gb_hairbow_pinkblack': [120, 92, 0],
    'gb_hairbow_polkadot': [120, 93, 0],
    'gb_hairbow_purple': [120, 94, 0],
    'gb_hairbow_purpleorange': [120, 95, 0],
    'gb_hairbow_red': [120, 96, 0],
    'gb_hairbow_yellow': [120, 97, 0],
    'gb_hairbow_yellowblack': [120, 98, 0],
    'pride_hairbow_ace': [120, 99, 0],
    'pride_hairbow_aro': [120, 100, 0],
    'pride_hairbow_bi': [120, 101, 0],
    'pride_hairbow_gay': [120, 102, 0],
    'pride_hairbow_genderfluid': [120, 103, 0],
    'pride_hairbow_lesbian': [120, 104, 0],
    'pride_hairbow_lgbt': [120, 105, 0],
    'pride_hairbow_nb': [120, 106, 0],
    'pride_hairbow_pan': [120, 107, 0],
    'pride_hairbow_trans': [120, 108, 0],
    'hat_cyberpunk': [155, 0, 0],
    'wizard_traffic_orange': [39, 109, 0],
    'headset_spy': [156, 0, 0],
    'hat_pirate_ghost': [157, 0, 0],
    'elf_jolly_green': [74, 111, 0],  # Jolly green elf hat
 }
# bow texture ids (for hats):
# 1, 2, 9, 10, 11, 12, 16, 18, 28, 36, 51

GlassesStyles = {
    'none': [0, 0, 0],
    'grd1': [1, 0, 0],
    'gmb1': [2, 0, 0],
    'gnr1': [3, 0, 0],
    'gst1': [4, 0, 0],
    'g3d1': [5, 0, 0],
    'gav1': [6, 0, 0],
    'gjo1': [9, 0, 0],
    'gsb1': [10, 0, 0],
    'ggl1': [11, 0, 0],
    'ggm1': [12, 0, 0],
    'ghg1': [13, 0, 0],
    'gie1': [14, 0, 0],
    'gmt1': [15, 0, 0],
    'gmt2': [15, 1, 0],
    'gmt3': [16, 0, 0],
    'gmt4': [16, 2, 0],
    'gmt5': [16, 3, 0],
    'gmn1': [17, 0, 0],
    'gmo1': [18, 0, 0],
    'gsr1': [19, 0, 0],
    'gce1': [7, 0, 0],
    'gdk1': [8, 0, 0],
    'gag1': [21, 0, 0],
    'ghw1': [20, 0, 0],
    'ghw2': [20, 4, 0],
    'ghw3': [20, 5, 0],
    'spider_glasses': [22, 0, 0],
    'hypno': [23, 0, 0],
    'snow_goggles_blue': [24, 0, 0],
    'snow_goggles_green': [25, 0, 0],
    'snow_goggles_grey': [26, 0, 0],
    'snow_goggles_pink': [27, 0, 0],
    'snow_goggles_rainbow': [28, 0, 0],
    'snow_goggles_red': [29, 0, 0],
    'snow_goggles_vintage': [30, 0, 0],
    '2019_glasses': [31, 0, 0],
    'flunky_glasses': [32, 0, 0],
    'eye_spring': [33, 0, 0],
    'flight_goggles': [34, 0, 0],
    'outback_sunnyglasses': [35, 0, 0],
    'hypno_2019': [23, 6, 0],
    'x_glasses_b': [36, 7, 0],
    'x_glasses_go': [36, 8, 0],
    'x_glasses_gr': [36, 9, 0],
    'x_glasses_ra': [36, 10, 0],
    'x_glasses_red': [36, 11, 0],
    'gift_glasses': [37, 0, 0],
    'gift_glasses_blue': [37, 12, 0],
    'gift_glasses_cyan': [37, 13, 0],
    'gift_glasses_green': [37, 14, 0],
    'gift_glasses_orange': [37, 15, 0],
    'gift_glasses_pink': [37, 16, 0],
    'gift_glasses_purple': [37, 17, 0],
    'gift_glasses_red': [37, 18, 0],
    'gift_glasses_yellow': [37, 19, 0],
    '2020_glasses': [38, 0, 0],
    'seven_glasses': [23, 20, 0],
    'vinny_stache': [39, 21, 0],
    'chair_glasses': [40, 22, 0],
    'hypno_blue': [23, 23, 0],
    'hypno_lightblue': [23, 24, 0],
    'hypno_orange': [23, 25, 0],
    'hypno_pink': [23, 26, 0],
    'hypno_yellow': [23, 27, 0],
    'hypno_purple': [23, 28, 0],
    'hypno_darkpurple': [23, 29, 0],
    'hypno_rainbow': [23, 30, 0],
    'orn_glasses_black': [41, 31, 0],
    'orn_glasses_blue': [41, 32, 0],
    'orn_glasses_cyan': [41, 33, 0],
    'orn_glasses_green': [41, 34, 0],
    'orn_glasses_orange': [41, 35, 0],
    'orn_glasses_pink': [41, 36, 0],
    'orn_glasses_purple': [41, 37, 0],
    'orn_glasses_rainbow': [41, 38, 0],
    'orn_glasses_red': [41, 39, 0],
    'orn_glasses_white': [41, 40, 0],
    'orn_glasses_yellow': [41, 41, 0],
    'hwtown_mask': [42, 0, 0],
    'count_mask': [43, 0, 0],
    '2022_glasses': [44, 0, 0],
    'scifi_visor': [45, 0, 0],
    'brovinci_glasses': [46, 0, 0],
    'glasses_mouthpiece': [47, 0, 0],
    'glasses_funky': [48, 0, 0],
    'ddl_sleepingmask': [49, 0, 0],
    'glasses_pacesetter': [50, 0, 0],
    'glasses_cardBlack': [51, 0, 0],
    'glasses_cardRed': [52, 0, 0],
    'muzzle_rose': [53, 0, 0],
    'painter_brush': [54, 0, 0],
    'cookie_glasses': [55, 0, 0],
    'glasses_low_baller': [56, 0, 0],
    'glasses_cyberpunk': [57, 0, 0],
    'glasses_pirate_mask': [58, 0, 0],
    'glasses_goggles_spy': [59, 0, 0],
}
BackpackStyles = {
    'none': [0, 0, 0],
    'backpack_pacesetter': [111, 0, 0],
    'bpb2': [1, 1, 0],
    'bpb3': [1, 2, 0],
    'bpd1': [1, 3, 0],
    'bpd2': [1, 4, 0],
    'bwg1': [2, 0, 0],
    'bwg2': [3, 0, 0],
    'bwg3': [4, 0, 0],
    'bst1': [5, 0, 0],
    'bfn1': [6, 0, 0],
    'baw1': [7, 0, 0],
    'baw2': [7, 5, 0],
    'bwt1': [8, 0, 0],
    'bwg4': [9, 0, 0],
    'bwg5': [9, 6, 0],
    'bwg6': [10, 0, 0],
    'bjp1': [11, 0, 0],
    'blg1': [12, 0, 0],
    'bsa1': [13, 0, 0],
    'bwg7': [14, 0, 0],
    'bsa2': [15, 0, 0],
    'bsa3': [16, 0, 0],
    'bap1': [17, 0, 0],
    'bhw1': [18, 0, 0],
    'bhw2': [19, 0, 0],
    'bhw3': [20, 0, 0],
    'bhw4': [21, 0, 0],
    'bob1': [22, 0, 0],
    'bfg1': [23, 0, 0],
    'bfl1': [24, 0, 0],
    'space_back': [25, 0, 0],
    'witch_broom': [26, 0, 0],
    'reaper_cape': [27, 0, 0],
    'dracula_cape': [28, 0, 0],
    'trickortreat_back': [29, 0, 0],
    'potion_back': [30, 0, 0],
    'tin_tradi': [31, 0, 0],
    'tin_humble': [32, 0, 0],
    'tin_regal': [33, 0, 0],
    'ragdoll_humble': [34, 0, 0],
    'ragdoll_regal': [35, 0, 0],
    'ragdoll_tradi': [36, 0, 0],
    'presents_sack': [37, 0, 0],
    'snowboard': [38, 0, 0],
    'candy_cane': [39, 0, 0],
    '2019_scarf': [40, 0, 0],
    'cupid_bow': [41, 0, 0],
    'cupid_bow_quiver': [42, 0, 0],
    'doe_bandana': [43, 0, 0],
    'prop_pack': [44, 0, 0],
    'kite': [45, 0, 0],
    'hangglider': [46, 0, 0],
    'aviator_scarf': [47, 0, 0],
    'telescope': [48, 0, 0],
    'pinwheel_bowtie': [49, 0, 0],
    'outback_backpack': [50, 0, 0],
    'outback_bandana': [51, 0, 0],
    'outback_boomerang': [52, 0, 0],
    'outback_didgeridoo': [53, 0, 0],
    'alien_backpack': [54, 0, 0],
    'angel_wings': [55, 0, 0],
    'angel_wings_blue': [55, 7, 0],
    'angel_wings_green': [55, 8, 0],
    'angel_wings_orange': [55, 9, 0],
    'angel_wings_purple': [55, 10, 0],
    'angel_wings_red': [55, 11, 0],
    'demon_wings': [56, 0, 0],
    'demon_wings_blue': [56, 7, 0],
    'demon_wings_green': [56, 8, 0],
    'demon_wings_orange': [56, 9, 0],
    'demon_wings_purple': [56, 10, 0],
    'demon_wings_red': [56, 11, 0],
    'ridinghood_cloak': [57, 0, 0],
    'bloodsucker_lollipop': [58, 12, 0],
    'cj_tie': [59, 13, 0],
    'angel_wings_yellow': [55, 14, 0],
    'demon_wings_yellow': [56, 14, 0],
    'sailor_collar_white': [60, 0, 0],
    'sailor_collar_blue': [60, 15, 0],
    'sailor_collar_cyan': [60, 16, 0],
    'sailor_collar_green': [60, 17, 0],
    'sailor_collar_orange': [60, 18, 0],
    'sailor_collar_pink': [60, 19, 0],
    'sailor_collar_purple': [60, 20, 0],
    'sailor_collar_red': [60, 21, 0],
    'sailor_collar_black': [60, 22, 0],
    'sailor_collar_yellow': [60, 23, 0],
    'sailor_bow_white': [61, 0, 0],
    'sailor_bow_blue': [61, 24, 0],
    'sailor_bow_cyan': [61, 25, 0],
    'sailor_bow_green': [61, 26, 0],
    'sailor_bow_orange': [61, 27, 0],
    'sailor_bow_pink': [61, 28, 0],
    'sailor_bow_purple': [61, 29, 0],
    'sailor_bow_red': [61, 30, 0],
    'sailor_bow_black': [61, 31, 0],
    'sailor_bow_yellow': [61, 32, 0],
    'stab_pack': [62, 34, 0],
    'gavel_pack': [63, 33, 0],
    'cj_pack': [64, 35, 0],
    'stone_pack': [65, 36, 0],
    'tnt_pack': [66, 0, 0],
    'retro_scarf': [67, 0, 0],
    'ragdoll_homemade_bow': [34, 37, 0],
    'soldier_homemade_key': [31, 38, 0],
    '2020_scarf': [40, 39, 0],
    'seltzer_pack': [68, 0, 0],
    'flower_tie': [69, 0, 0],
    'mini_mag': [70, 40, 0],
    'taser': [71, 0, 0],
    'fusion_pack': [72, 0, 0],
    'clown_bowtie': [73, 0, 0],
    'chair_pack': [74, 41, 0],
    'jester_collar': [75, 42, 0],
    'bunny_backpack': [76, 0, 0],
    'law_bowtie': [73, 43, 0],
    'spatula': [77, 44, 0],
    'firework': [78, 45, 0],
    'spellbook': [64, 46, 0],
    'tombstone': [65, 47, 0],
    'candy_pumpkin': [79, 0, 0],
    'plate_pack': [80, 0, 0],
    'extinguisher': [81, 0, 0],
    'present_corn': [82, 0, 0],
    'future_wing': [83, 0, 0],
    'future_cloak': [84, 0, 0],
    'future_wing_cloak': [85, 0, 0],
    '2021_scarf': [40, 48, 0],
    'ottoman_tie': [86, 0, 0],
    'hwtown_cape': [87, 0, 0],
    'skelecog_pack': [88, 0, 0],
    'eye_bowtie': [89, 0, 0],
    'mystery_bowtie': [90, 0, 0],
    'newstoon_suitcase': [91, 0, 0],
    'newstoon_blue_bowtie': [73, 49, 0],
    'newstoon_camera': [92, 0, 0],
    'ribbon_bowtie': [93, 0, 0],
    '2022_scarf': [40, 50, 0],
    'ribbon_bowtie_redPolka': [93, 51, 0],  # Red Polka Dot Bow
    'ribbon_bowtie_purple': [93, 52, 0],   # Purple Bow
    'ribbon_bowtie_yellow': [93, 53, 0],# Yellow Bow
    'ribbon_bowtie_blueChecker': [93, 54, 0], # Blue Checker Bow
    'ribbon_bowtie_red': [93, 55, 0],  # Red Bow
    'ribbon_bowtie_rainbow': [93, 56, 0],  # Rainbow Bow
    'ribbon_bowtie_pinkDots': [93, 57, 0],  # Pink Dots Bow
    'ribbon_bowtie_greenChecker': [93, 58, 0],  # Yellow/Green Checker Bow
    'ribbpn_bowtie_blue': [93, 59, 0],  # Blue Bow
    'ribbon_bowtie_candycorn': [93, 60, 0],  # Candy Corn Bow
    'ribbon_bowtie_black': [93, 61, 0],  # Black Bow
    'pride_cape_lgbt': [94, 0, 0],
    'pride_cape_trans': [94, 62, 0],
    'pride_cape_lesbian': [94, 63, 0],
    'pride_cape_pan': [94, 64, 0],
    'pride_cape_bi': [94, 65, 0],
    'pride_cape_nb': [94, 66, 0],
    'pride_cape_ace': [94, 67, 0],
    'pride_cape_fluid': [94, 68, 0],
    'pride_cape_aro': [94, 69, 0],
    'pride_cape_gay': [94, 87, 0],
    'doodle_pack': [95, 0, 0],
    'brovinci_necklace': [96, 0, 0],
    'backpack_moneybag': [97, 0, 0],
    'backpack_pitchfork': [98, 0, 0],
    'backpack_wingsuit_wings': [99, 0, 0],
    'bandana_engineer': [51, 71, 0],
    'backpack_pillow': [100, 0, 0],
    'backpack_bellringer': [101, 0, 0],
    'backpack_majorplayer': [102, 0, 0],
    'backpack_firestarter': [103, 0, 0],
    'backpack_gatekeeper': [104, 0, 0],
    'backpack_fruitbasket': [105, 0, 0],
    'backpack_retrobag': [106, 0, 0],
    'gb_bowtie_black': [73, 72, 0],
    'gb_bowtie_blackwhite': [73, 73, 0],
    'gb_bowtie_blue': [73, 74, 0],
    'gb_bowtie_gray': [73, 75, 0],
    'gb_bowtie_green': [73, 76, 0],
    'gb_bowtie_orange': [73, 77, 0],
    'gb_bowtie_pink': [73, 78, 0],
    'gb_bowtie_pinkblack': [73, 79, 0],
    'gb_bowtie_polkadot': [73, 80, 0],
    'gb_bowtie_purple': [73, 81, 0],
    'gb_bowtie_purpleorange': [73, 82, 0],
    'gb_bowtie_red': [73, 83, 0],
    'gb_bowtie_yellow': [73, 84, 0],
    'gb_bowtie_yellowblack': [73, 85, 0],
    'ee_breadbag': [107, 0, 0],
    'ee_chefscarf': [108, 0, 0],
    'ee_paddle': [109, 0, 0],
    'painter_palette': [110, 0, 0],
    '2023_scarf': [40, 86, 0],
    'backpack_pacesetter': [111, 0, 0],
    'backpack_factory_gear': [112, 0, 0],
    'pride_bowtie_ace': [73, 88, 0],
    'pride_bowtie_aro': [73, 89, 0],
    'pride_bowtie_bi': [73, 90, 0],
    'pride_bowtie_gay': [73, 91, 0],
    'pride_bowtie_genderfluid': [73, 92, 0],
    'pride_bowtie_lesbian': [73, 93, 0],
    'pride_bowtie_lgbt': [73, 94, 0],
    'pride_bowtie_nb': [73, 95, 0],
    'pride_bowtie_pan': [73, 96, 0],
    'pride_bowtie_trans': [73, 97, 0],
    'backpack_cyberpunk': [113, 0, 0],
    'backpack_pirate_ghost': [114, 0, 0],
    'bowtie_elf_jolly': [115, 0, 0],

    '2024_scarf': [40, 98, 0],

}
ShoesStyles = {
    'none': [0, 0, 0],
    'sat1': [1, 0, 0],
    'sat2': [1, 1, 0],
    'smb1': [3, 2, 0],
    'scs1': [2, 3, 0],
    'sdk1': [1, 6, 0],
    'sat3': [1, 7, 0],
    'scs2': [2, 8, 0],
    'scs3': [2, 9, 0],
    'scs4': [2, 10, 0],
    'scb1': [3, 11, 0],
    'sht1': [2, 13, 0],
    'ssb1': [3, 16, 0],
    'sts1': [1, 17, 0],
    'sts2': [1, 18, 0],
    'scs5': [2, 19, 0],
    'smb2': [3, 20, 0],
    'smb3': [3, 21, 0],
    'smb4': [3, 22, 0],
    'slf1': [1, 28, 0],
    'smt1': [3, 30, 0],
    'sox1': [1, 31, 0],
    'srb1': [3, 32, 0],
    'sst1': [3, 33, 0],
    'swb1': [3, 34, 0],
    'swb2': [3, 35, 0],
    'swk1': [2, 36, 0],
    'scs6': [2, 37, 0],
    'smb5': [3, 38, 0],
    'sht2': [2, 39, 0],
    'srb2': [3, 40, 0],
    'sts3': [1, 41, 0],
    'sts4': [1, 42, 0],
    'sts5': [1, 43, 0],
    'srb3': [3, 44, 0],
    'srb4': [3, 45, 0],
    'sat4': [1, 46, 0],
    'shw1': [3, 47, 0],
    'shw2': [3, 48, 0],
    'swt1': [1, 4, 0],
    'smj1': [2, 5, 0],
    'sfb1': [3, 12, 0],
    'smj2': [2, 14, 0],
    'smj3': [2, 15, 0],
    'sfb2': [3, 23, 0],
    'sfb3': [3, 24, 0],
    'sfb4': [3, 25, 0],
    'sfb5': [3, 26, 0],
    'sfb6': [3, 27, 0],
    'smj4': [2, 29, 0],
    'space_boots': [2, 49, 0],
    'witch_shoes': [3, 50, 0],
    'skeleton_shoes': [2, 51, 0],
    'alchemist_shoes': [3, 52, 0],
    'ragdoll_humble': [3, 53, 0],
    'ragdoll_regal': [3, 54, 0],
    'ragdoll_traditional': [3, 55, 0],
    'tin_humble': [3, 56, 0],
    'tin_regal': [3, 57, 0],
    'tin_traditional': [3, 58, 0],
    'vintage_snow_outfit': [3, 59, 0],
    'aviator_boots': [3, 60, 0],
    'wingsuit_boots': [3, 61, 0],
    'outback_shoes': [2, 62, 0],
    'pumpkin_shoes': [2, 63, 0],
    'lazy_bones_shoes': [1, 64, 0],
    'homemade_ragdoll_boots': [3, 65, 0],
    'homemade_soldier_boots': [3, 66, 0],
    'retro_wintersuit_shoes': [2, 67, 0],
    'retro_winterdress_shoes': [2, 68, 0],
    'law_shoes': [2, 69, 0],
    'rainbow_shoes': [2, 70, 0],
    'chair_shoes': [1, 71, 0],
    'phantom_shoes': [2, 72, 0],
    'tumbles_shoes': [2, 73, 0],
    'hwtown_boots': [3, 74, 0],
    'shoes_diver': [3, 75, 0],
    'shoes_engineer': [2, 76, 0],
    'shoes_fruitpie': [2, 77, 0],
    'shoes_cardRed': [3, 78, 0],
    'shoes_cardBlack': [3, 79, 0],
    'shoes_gator': [3, 80, 0],
    'shoes_painter': [2, 81, 0],
    'shoes_gatekeeper': [2, 82, 0],
    'shoes_cyberpunk': [2, 83, 0],
    'shoes_pirate_ghost': [2, 84, 0],
    'shoes_spy': [2, 85, 0],
 }

# Manually register only the requested queer/ADHD pride accessory textures.
# This intentionally avoids the broad automatic texture scanner so existing
# accessory texture IDs are never cleared or renumbered.
MANUAL_PRIDE_TEXTURE_DIRECTORY = 'resources/phase_4/maps/pride'
MANUAL_PRIDE_TEXTURE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.rgb', '.rgba', '.tga')


def _appendManualAccessoryTexture(textureList, texturePath):
    normalizedPath = texturePath.replace('\\', '/').lower()

    for textureId, existingPath in enumerate(textureList):
        if (isinstance(existingPath, basestring) and
                existingPath.replace('\\', '/').lower() == normalizedPath):
            return textureId

    if len(textureList) >= 256:
        notify.warning(
            'Cannot manually register accessory texture %s because texture IDs are limited to 255.' %
            texturePath
        )
        return None

    textureList.append(texturePath)
    return len(textureList) - 1


def _registerManualAccessoryStyle(styleDict, styleName, modelId, textureId):
    if textureId is None:
        return
    styleDict[styleName] = [modelId, textureId, 0]


def registerManualPrideAccessoryTextures():
    prideDirectory = _getExistingPath(MANUAL_PRIDE_TEXTURE_DIRECTORY)
    if not os.path.isdir(prideDirectory):
        notify.info('Manual pride texture directory not found: %s' % MANUAL_PRIDE_TEXTURE_DIRECTORY)
        return

    registeredCount = 0

    try:
        fileNames = sorted(os.listdir(prideDirectory))
    except Exception:
        notify.warning('Could not read manual pride texture directory: %s' % prideDirectory)
        return

    for fileName in fileNames:
        fullPath = os.path.join(prideDirectory, fileName)
        if not os.path.isfile(fullPath):
            continue

        lowerName = fileName.lower()
        if os.path.splitext(lowerName)[1] not in MANUAL_PRIDE_TEXTURE_EXTENSIONS:
            continue

        if 'queer' in lowerName:
            variantName = 'queer'
        elif 'adhd' in lowerName:
            variantName = 'adhd'
        else:
            continue

        texturePath = _getCustomClothingAssetPath(fullPath).replace('\\', '/')

        if 'bowtie' in lowerName:
            # The same bowtie is available in both Head Accessories and
            # Body Accessories, so add the texture to both independent lists.
            hatTextureId = _appendManualAccessoryTexture(HatTextures, texturePath)
            backpackTextureId = _appendManualAccessoryTexture(BackpackTextures, texturePath)

            _registerManualAccessoryStyle(
                HatStyles,
                'manual_pride_bowtie_%s_hat' % variantName,
                120,
                hatTextureId
            )
            _registerManualAccessoryStyle(
                BackpackStyles,
                'manual_pride_bowtie_%s_body' % variantName,
                73,
                backpackTextureId
            )
            registeredCount += 1

        elif 'cape' in lowerName:
            textureId = _appendManualAccessoryTexture(BackpackTextures, texturePath)
            _registerManualAccessoryStyle(
                BackpackStyles,
                'manual_pride_cape_%s' % variantName,
                94,
                textureId
            )
            registeredCount += 1

        elif 'scarf' in lowerName:
            textureId = _appendManualAccessoryTexture(BackpackTextures, texturePath)
            _registerManualAccessoryStyle(
                BackpackStyles,
                'manual_pride_scarf_%s' % variantName,
                40,
                textureId
            )
            registeredCount += 1

    notify.info('Manually registered %d queer/ADHD pride accessory texture file(s).' % registeredCount)


registerManualPrideAccessoryTextures()




CUSTOM_ACCESSORY_DIRECTORY = 'resources/phase_14/accessories'
CUSTOM_ACCESSORY_REGISTRY = 'resources/phase_14/accessories/accessories_registry.json'
CUSTOM_ACCESSORY_EXTENSIONS = ('.bam',)
CUSTOM_ACCESSORY_REGISTRY_VERSION = 3
CUSTOM_ACCESSORY_MAX_ID = 255

# Capture the first free native IDs before any custom BAMs are appended to the
# model tables. Using len(HatModels), etc. inside every rescan made the minimum
# increase after each call, so every search in the placement editor assigned a
# fresh set of IDs.
_CUSTOM_ACCESSORY_NATIVE_MINIMUM_IDS = {
    'hat': len(HatModels),
    'glasses': len(GlassesModels),
    'backpack': len(BackpackModels),
    'shoes': len(ShoesModels)
}


def _clearRegisteredCustomAccessoryStyles():
    for accessoryType in ('hat', 'glasses', 'backpack', 'shoes'):
        unusedModels, styleDict, prefix = _getNativeAccessoryTables(
            accessoryType
        )
        if styleDict is None:
            continue

        for styleName in list(styleDict.keys()):
            if styleName.startswith(prefix):
                del styleDict[styleName]


def _findCustomAccessoryRoot():
    relativePath = CUSTOM_ACCESSORY_DIRECTORY.replace('/', os.sep)
    searchRoots = []

    currentDirectory = os.path.abspath(os.getcwd())
    while True:
        if currentDirectory not in searchRoots:
            searchRoots.append(currentDirectory)
        parentDirectory = os.path.dirname(currentDirectory)
        if parentDirectory == currentDirectory:
            break
        currentDirectory = parentDirectory

    try:
        currentDirectory = os.path.dirname(os.path.abspath(__file__))
        while True:
            if currentDirectory not in searchRoots:
                searchRoots.append(currentDirectory)
            parentDirectory = os.path.dirname(currentDirectory)
            if parentDirectory == currentDirectory:
                break
            currentDirectory = parentDirectory
    except Exception:
        pass

    for root in searchRoots:
        candidate = os.path.join(root, relativePath)
        if os.path.isdir(candidate):
            return candidate

    return os.path.join(os.getcwd(), relativePath)


def _loadNativeAccessoryRegistry(registryPath):
    if not os.path.isfile(registryPath):
        return {
            'version': CUSTOM_ACCESSORY_REGISTRY_VERSION,
            'accessories': {}
        }

    try:
        registryFile = open(registryPath, 'r')
        try:
            registry = json.load(registryFile)
        finally:
            registryFile.close()
    except Exception:
        notify.warning('Could not read accessory registry. A new registry will be created.')
        return {
            'version': CUSTOM_ACCESSORY_REGISTRY_VERSION,
            'accessories': {}
        }

    if not isinstance(registry, dict):
        registry = {}

    if not isinstance(registry.get('accessories'), dict):
        registry['accessories'] = {}

    registry['version'] = CUSTOM_ACCESSORY_REGISTRY_VERSION
    return registry


def _saveNativeAccessoryRegistry(registryPath, registry):
    registryDirectory = os.path.dirname(registryPath)
    if registryDirectory and not os.path.isdir(registryDirectory):
        os.makedirs(registryDirectory)

    registryFile = open(registryPath, 'w')
    try:
        json.dump(registry, registryFile, indent=4, sort_keys=True)
        registryFile.write('\n')
    finally:
        registryFile.close()


def _getAccessoryTypeFromName(fileName):
    lowerName = fileName.lower()

    if 'glasses' in lowerName or 'glass' in lowerName:
        return 'glasses'
    if 'shoes' in lowerName or 'shoe' in lowerName or '_sho_' in lowerName:
        return 'shoes'
    if 'hat' in lowerName:
        return 'hat'
    if ('backpack' in lowerName or 'pack' in lowerName or
            'cape' in lowerName or 'scarf' in lowerName or
            'bowtie' in lowerName or 'neck' in lowerName or
            '_nec_' in lowerName):
        return 'backpack'

    return None


def _getNativeAccessoryTables(accessoryType):
    if accessoryType == 'hat':
        return HatModels, HatStyles, 'custom_hat_'
    if accessoryType == 'glasses':
        return GlassesModels, GlassesStyles, 'custom_glasses_'
    if accessoryType == 'backpack':
        return BackpackModels, BackpackStyles, 'custom_backpack_'
    if accessoryType == 'shoes':
        return ShoesModels, ShoesStyles, 'custom_shoes_'

    return None, None, None


def _setAccessoryModelAtId(modelList, accessoryId, modelPath):
    while len(modelList) <= accessoryId:
        modelList.append(None)

    modelList[accessoryId] = modelPath


def _nextNativeAccessoryId(minimumId, usedIds):
    accessoryId = minimumId

    while accessoryId in usedIds:
        accessoryId += 1

    return accessoryId


def _makeDefaultAccessoryDisplayName(fileName, accessoryType):
    baseName = os.path.splitext(os.path.basename(fileName))[0]
    words = [word for word in baseName.replace('-', '_').split('_') if word]

    typeWords = {
        'hat': ('hat',),
        'glasses': ('glasses', 'glass'),
        'backpack': ('backpack', 'pack'),
        'shoes': ('shoes', 'shoe')
    }.get(accessoryType, ())

    filteredWords = []
    for word in words:
        if word.lower() not in typeWords:
            filteredWords.append(word)

    if filteredWords:
        prettyName = ' '.join(filteredWords).title()
    else:
        prettyName = baseName.replace('_', ' ').replace('-', ' ').title()

    suffixes = {
        'hat': 'Hat',
        'glasses': 'Glasses',
        'backpack': 'Backpack',
        'shoes': 'Shoes'
    }

    suffix = suffixes.get(accessoryType)
    if suffix:
        prettyName = '%s %s' % (prettyName, suffix)

    return prettyName.strip()


def _makeCustomAccessoryKey(accessoryType, accessoryId, registryKey):
    safeName = registryKey.lower()
    safeName = safeName.replace('\\', '_').replace('/', '_')
    safeName = safeName.replace('.bam', '')
    safeName = ''.join(
        character if character.isalnum() else '_'
        for character in safeName
    )

    return 'custom_%s_%d_%s' % (
        accessoryType,
        accessoryId,
        safeName
    )


def _getCustomAccessoryFingerprint(fullPath):
    try:
        digest = hashlib.sha1()
        accessoryFile = open(fullPath, 'rb')
        try:
            while True:
                chunk = accessoryFile.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
        finally:
            accessoryFile.close()
        return digest.hexdigest()
    except Exception:
        notify.warning('Could not fingerprint custom accessory: %s' % fullPath)
        return None


def _getCustomAccessoryCandidateSortKey(candidate):
    registryKey = candidate['registry_key']
    # If the same BAM exists loose and inside a named folder, keep the folder copy.
    inSubfolder = '/' in registryKey
    return (
        0 if inSubfolder else 1,
        registryKey.count('/'),
        len(registryKey),
        registryKey.lower()
    )


def _getRegistryCandidateIds(oldAccessories, group, minimumId):
    candidateIds = []
    groupKeys = set(candidate['registry_key'] for candidate in group['candidates'])
    groupNames = set(
        os.path.splitext(os.path.basename(candidate['registry_key']))[0].lower()
        for candidate in group['candidates']
    )

    for registryKey, accessoryData in oldAccessories.items():
        if not isinstance(accessoryData, dict):
            continue
        if accessoryData.get('type') != group['type']:
            continue

        matches = registryKey in groupKeys
        if not matches and group['fingerprint'] is not None:
            matches = accessoryData.get('fingerprint') == group['fingerprint']
        if not matches:
            oldName = accessoryData.get('name')
            if isinstance(oldName, basestring):
                matches = oldName.lower() in groupNames
        if not matches:
            oldBaseName = os.path.splitext(os.path.basename(registryKey))[0].lower()
            matches = oldBaseName in groupNames

        if matches:
            nativeId = accessoryData.get('native_id')
            if (isinstance(nativeId, int) and nativeId >= minimumId and
                    nativeId <= CUSTOM_ACCESSORY_MAX_ID):
                candidateIds.append(nativeId)

    return sorted(set(candidateIds))


def _getPreservedAccessoryDisplayName(oldAccessories, group):
    groupKeys = set(candidate['registry_key'] for candidate in group['candidates'])

    for registryKey, accessoryData in oldAccessories.items():
        if not isinstance(accessoryData, dict):
            continue
        if accessoryData.get('type') != group['type']:
            continue

        matches = registryKey in groupKeys
        if not matches and group['fingerprint'] is not None:
            matches = accessoryData.get('fingerprint') == group['fingerprint']

        if matches:
            displayName = accessoryData.get('display_name')
            if isinstance(displayName, basestring) and displayName.strip():
                return displayName.strip()

    return None


def registerCustomAccessoriesAsNative():
    accessoryRoot = _findCustomAccessoryRoot()

    if not os.path.isdir(accessoryRoot):
        try:
            os.makedirs(accessoryRoot)
        except Exception:
            notify.warning('Could not create accessory directory: %s' % accessoryRoot)
            return

    registryPath = os.path.join(accessoryRoot, 'accessories_registry.json')
    registry = _loadNativeAccessoryRegistry(registryPath)
    oldAccessories = registry['accessories']

    # Remove generated style aliases from an earlier registration pass before
    # rebuilding the clean registry-backed set. The model lists may remain
    # extended in memory, but no stale alias points at those abandoned slots.
    _clearRegisteredCustomAccessoryStyles()

    minimumIdsByType = dict(_CUSTOM_ACCESSORY_NATIVE_MINIMUM_IDS)

    groupsByFingerprint = {}
    discoveredFileCount = 0

    for currentRoot, directoryNames, fileNames in os.walk(accessoryRoot):
        directoryNames.sort()

        for fileName in sorted(fileNames):
            extension = os.path.splitext(fileName)[1].lower()
            if extension not in CUSTOM_ACCESSORY_EXTENSIONS:
                continue

            accessoryType = _getAccessoryTypeFromName(fileName)
            if accessoryType is None:
                continue

            fullPath = os.path.join(currentRoot, fileName)
            registryKey = os.path.relpath(
                fullPath,
                accessoryRoot
            ).replace('\\', '/')
            fingerprint = _getCustomAccessoryFingerprint(fullPath)

            if fingerprint is None:
                groupIdentity = (
                    accessoryType,
                    'path:%s' % registryKey.lower()
                )
            else:
                groupIdentity = (accessoryType, fingerprint)

            group = groupsByFingerprint.get(groupIdentity)
            if group is None:
                group = {
                    'type': accessoryType,
                    'fingerprint': fingerprint,
                    'candidates': []
                }
                groupsByFingerprint[groupIdentity] = group

            group['candidates'].append({
                'registry_key': registryKey,
                'full_path': fullPath
            })
            discoveredFileCount += 1

    groups = list(groupsByFingerprint.values())
    for group in groups:
        group['candidates'].sort(key=_getCustomAccessoryCandidateSortKey)
        group['canonical'] = group['candidates'][0]

    groups.sort(key=lambda group: (
        group['type'],
        group['canonical']['registry_key'].lower()
    ))

    usedIdsByType = {
        'hat': set(),
        'glasses': set(),
        'backpack': set(),
        'shoes': set()
    }
    cleanAccessories = {}
    registeredCount = 0

    for group in groups:
        accessoryType = group['type']
        canonical = group['canonical']
        registryKey = canonical['registry_key']
        fullPath = canonical['full_path']
        minimumId = minimumIdsByType[accessoryType]

        nativeId = None
        for candidateId in _getRegistryCandidateIds(
                oldAccessories, group, minimumId):
            if candidateId not in usedIdsByType[accessoryType]:
                nativeId = candidateId
                break

        if nativeId is None:
            nativeId = _nextNativeAccessoryId(
                minimumId,
                usedIdsByType[accessoryType]
            )

        if nativeId > CUSTOM_ACCESSORY_MAX_ID:
            notify.warning(
                'Cannot register %s because native accessory IDs are limited to 255.' %
                registryKey
            )
            continue

        usedIdsByType[accessoryType].add(nativeId)

        modelList, styleDict, unusedPrefix = _getNativeAccessoryTables(
            accessoryType
        )
        if modelList is None:
            continue

        assetPath = _getCustomClothingAssetPath(fullPath)
        if assetPath.lower().endswith('.bam'):
            assetPath = assetPath[:-4]
        assetPath = assetPath.replace('\\', '/')

        internalName = os.path.splitext(os.path.basename(fullPath))[0]
        displayName = _getPreservedAccessoryDisplayName(
            oldAccessories,
            group
        )
        if not displayName:
            displayName = _makeDefaultAccessoryDisplayName(
                fullPath,
                accessoryType
            )

        styleKey = _makeCustomAccessoryKey(
            accessoryType,
            nativeId,
            registryKey
        )

        accessoryData = {
            'type': accessoryType,
            'native_id': nativeId,
            'id': nativeId,
            'model': assetPath,
            'name': internalName,
            'display_name': displayName,
            'style': styleKey
        }
        if group['fingerprint'] is not None:
            accessoryData['fingerprint'] = group['fingerprint']

        cleanAccessories[registryKey] = accessoryData
        _setAccessoryModelAtId(modelList, nativeId, assetPath)
        styleDict[styleKey] = [nativeId, 0, 0]
        registeredCount += 1

    duplicateFileCount = discoveredFileCount - len(groups)
    removedRegistryCount = max(len(oldAccessories) - len(cleanAccessories), 0)

    registry['version'] = CUSTOM_ACCESSORY_REGISTRY_VERSION
    registry['accessories'] = cleanAccessories
    if (oldAccessories != cleanAccessories or
            not os.path.isfile(registryPath)):
        _saveNativeAccessoryRegistry(registryPath, registry)

    notify.info(
        'Registered %d unique custom accessory model(s); cleaned %d duplicate file(s) and %d stale registry entry/entries.' %
        (registeredCount, duplicateFileCount, removedRegistryCount)
    )


registerCustomAccessoriesAsNative()


def isValidHat(itemIdx, textureIdx, colorIdx):
    for style in HatStyles.values():
        if itemIdx == style[0] and textureIdx == style[1] and colorIdx == style[2]:
            return True

    return False


def isValidGlasses(itemIdx, textureIdx, colorIdx):
    for style in GlassesStyles.values():
        if itemIdx == style[0] and textureIdx == style[1] and colorIdx == style[2]:
            return True

    return False


def isValidBackpack(itemIdx, textureIdx, colorIdx):
    for style in BackpackStyles.values():
        if itemIdx == style[0] and textureIdx == style[1] and colorIdx == style[2]:
            return True

    return False


def isValidShoes(itemIdx, textureIdx, colorIdx):
    for style in ShoesStyles.values():
        if itemIdx == style[0] and textureIdx == style[1] and colorIdx == style[2]:
            return True

    return False


def isValidAccessory(itemIdx, textureIdx, colorIdx, which):
    if which == HAT:
        return isValidHat(itemIdx, textureIdx, colorIdx)
    elif which == GLASSES:
        return isValidGlasses(itemIdx, textureIdx, colorIdx)
    elif which == BACKPACK:
        return isValidBackpack(itemIdx, textureIdx, colorIdx)
    elif which == SHOES:
        return isValidShoes(itemIdx, textureIdx, colorIdx)
    else:
        return False


class ToonDNA(AvatarDNA.AvatarDNA):

    def __init__(self, str = None, type = None, dna = None, r = None, b = None, g = None):
        if str != None:
            self.makeFromNetString(str)
        elif type != None:
            if type == 't':
                if dna == None:
                    self.newToonRandom(r, g, b)
                else:
                    self.newToonFromProperties(*dna.asTuple())
        else:
            self.type = 'u'
        
        self.cache = ()

    def __str__(self):
        string = 'type = toon\n'
        string = string + 'gender = %s\n' % self.gender
        string = string + 'head = %s, torso = %s, legs = %s\n' % (self.head, self.torso, self.legs)
        string = string + 'arm color = %s\n' % (self.armColor,)
        string = string + 'glove color = %s\n' % (self.gloveColor,)
        string = string + 'leg color = %s\n' % (self.legColor,)
        string = string + 'head color = %s\n' % (self.headColor,)
        string = string + 'top texture = %d\n' % self.topTex
        string = string + 'top texture color = %d\n' % self.topTexColor
        string = string + 'sleeve texture = %d\n' % self.sleeveTex
        string = string + 'sleeve texture color = %d\n' % self.sleeveTexColor
        string = string + 'bottom texture = %d\n' % self.botTex
        string = string + 'bottom texture color = %d\n' % self.botTexColor
        return string

    def clone(self):
        d = ToonDNA()
        d.makeFromNetString(self.makeNetString())
        return d

    def makeNetString(self):
        dg = PyDatagram()
        dg.addFixedString(self.type, 1)
        if self.type == 't':
            headIndex = toonHeadTypes.index(self.head)
            torsoIndex = toonTorsoTypes.index(self.torso)
            legsIndex = toonLegTypes.index(self.legs)
            dg.addUint8(headIndex)
            dg.addUint8(torsoIndex)
            dg.addUint8(legsIndex)
            if self.gender == 'm':
                dg.addUint8(1)
            else:
                dg.addUint8(0)
            dg.addUint8(self.topTex)
            dg.addUint8(self.topTexColor)
            dg.addUint8(self.sleeveTex)
            dg.addUint8(self.sleeveTexColor)
            dg.addUint8(self.botTex)
            dg.addUint8(self.botTexColor)
            self.armColor = self.checkIsDefaultColor(self.armColor)
            self.gloveColor = self.checkIsDefaultColor(self.gloveColor)
            self.legColor = self.checkIsDefaultColor(self.legColor)
            self.headColor = self.checkIsDefaultColor(self.headColor)
            for colors in (self.armColor, self.gloveColor, self.legColor, self.headColor):
                for color in colors[:-1]:
                    dg.addFloat64(color)
        elif self.type == 'u':
            notify.error('undefined avatar')
        else:
            notify.error('unknown avatar type: ', self.type)
        return dg.getMessage()

    def isValidNetString(self, string):
        dg = PyDatagram(string)
        dgi = PyDatagramIterator(dg)
        type = dgi.getFixedString(1)
        if type not in ('t',):
            return False
        headIndex = dgi.getUint8()
        torsoIndex = dgi.getUint8()
        legsIndex = dgi.getUint8()
        if headIndex >= len(toonHeadTypes):
            return False
        if torsoIndex >= len(toonTorsoTypes):
            return False
        if legsIndex >= len(toonLegTypes):
            return False
        gender = dgi.getUint8()
        if gender == 1:
            gender = 'm'
        else:
            gender = 'f'
        topTex = dgi.getUint8()
        topTexColor = dgi.getUint8()
        sleeveTex = dgi.getUint8()
        sleeveTexColor = dgi.getUint8()
        botTex = dgi.getUint8()
        botTexColor = dgi.getUint8()
        armColor = (dgi.getFloat64(), dgi.getFloat64(), dgi.getFloat64(), 1.0)
        gloveColor = (dgi.getFloat64(), dgi.getFloat64(), dgi.getFloat64(), 1.0)
        legColor = (dgi.getFloat64(), dgi.getFloat64(), dgi.getFloat64(), 1.0)
        headColor = (dgi.getFloat64(), dgi.getFloat64(), dgi.getFloat64(), 1.0)
        if topTex >= len(Shirts):
            return False
        if topTexColor >= len(ClothesColors):
            return False
        if sleeveTex >= len(Sleeves):
            return False
        if sleeveTexColor >= len(ClothesColors):
            return False
        if gender == 'm':
            if botTex >= len(BoyShorts):
                return False
        else:
            if botTex >= len(GirlBottoms):
                return False
        if botTexColor >= len(ClothesColors):
            return False
        if not self.checkColor(armColor):
            return False
        if not self.checkColor(gloveColor):
            return False
        if not self.checkColor(legColor):
            return False
        if not self.checkColor(headColor):
            return False
        return True

    def checkColor(self, color):
        if color in allColorsList: # Color is a default one
            return True
        
        hsv = colorsys.rgb_to_hsv(color[0], color[1], color[2])
        return 0.1 <= hsv[1] <= 0.9 and 0.2 <= hsv[2] <= 0.9

    def makeFromNetString(self, string):
        dg = PyDatagram(string)
        dgi = PyDatagramIterator(dg)
        self.type = dgi.getFixedString(1)
        if self.type == 't':
            headIndex = dgi.getUint8()
            torsoIndex = dgi.getUint8()
            legsIndex = dgi.getUint8()
            self.head = toonHeadTypes[headIndex]
            self.torso = toonTorsoTypes[torsoIndex]
            self.legs = toonLegTypes[legsIndex]
            gender = dgi.getUint8()
            if gender == 1:
                self.gender = 'm'
            else:
                self.gender = 'f'
            self.topTex = dgi.getUint8()
            self.topTexColor = dgi.getUint8()
            self.sleeveTex = dgi.getUint8()
            self.sleeveTexColor = dgi.getUint8()
            self.botTex = dgi.getUint8()
            self.botTexColor = dgi.getUint8()
            try:
                self.armColor = (dgi.getFloat64(), dgi.getFloat64(), dgi.getFloat64(), 1.0)
                self.gloveColor = (dgi.getFloat64(), dgi.getFloat64(), dgi.getFloat64(), 1.0)
                self.legColor = (dgi.getFloat64(), dgi.getFloat64(), dgi.getFloat64(), 1.0)
                self.headColor = (dgi.getFloat64(), dgi.getFloat64(), dgi.getFloat64(), 1.0)
            except:
                # Outdated toon color, will need to convert to new format
                self.notify.info("Outdated Toon color format! Converting to new format...")
                self.armColor = dgi.getUint8()
                self.gloveColor = dgi.getUint8()
                self.legColor = dgi.getUint8()
                self.headColor = dgi.getUint8()
                self.armColor = allColorsList[self.armColor]
                self.gloveColor = allColorsList[self.gloveColor]
                self.legColor = allColorsList[self.legColor]
                self.headColor = allColorsList[self.headColor]
                
        else:
            notify.error('unknown avatar type: ', self.type)
        return None

    def defaultColor(self):
        return 25

    def __defaultColors(self):
        color = self.defaultColor()
        self.armColor = color
        self.gloveColor = 0
        self.legColor = color
        self.headColor = color

    def newToon(self, dna, color = None):
        if len(dna) == 4:
            self.type = 't'
            self.head = dna[0]
            self.torso = dna[1]
            self.legs = dna[2]
            self.gender = dna[3]
            self.topTex = 0
            self.topTexColor = 0
            self.sleeveTex = 0
            self.sleeveTexColor = 0
            self.botTex = 0
            self.botTexColor = 0
            if color == None:
                color = 1 # If for some reason there is no color, gg, and set it to 1
            color = self.checkIsDefaultColor(color)
            self.armColor = color
            self.legColor = color
            self.headColor = color
            self.gloveColor = 0
        else:
            notify.error("tuple must be in format ('%s', '%s', '%s', '%s')")
            
    def checkIsDefaultColor(self, color):
        if isinstance(color, int):
            return defaultColorList[color]
        else:
            return color

    def newToonFromProperties(self, head, torso, legs, gender, armColor, gloveColor, legColor, headColor, topTexture, topTextureColor, sleeveTexture, sleeveTextureColor, bottomTexture, bottomTextureColor):
        self.type = 't'
        self.head = head
        self.torso = torso
        self.legs = legs
        self.gender = gender
        self.armColor = self.checkIsDefaultColor(armColor)
        self.gloveColor = self.checkIsDefaultColor(gloveColor)
        self.legColor = self.checkIsDefaultColor(legColor)
        self.headColor = self.checkIsDefaultColor(headColor)
        self.topTex = topTexture
        self.topTexColor = topTextureColor
        self.sleeveTex = sleeveTexture
        self.sleeveTexColor = sleeveTextureColor
        self.botTex = bottomTexture
        self.botTexColor = bottomTextureColor

    def updateToonProperties(self, head = None, torso = None, legs = None, gender = None, armColor = None, gloveColor = None, legColor = None, headColor = None, topTexture = None, topTextureColor = None, sleeveTexture = None, sleeveTextureColor = None, bottomTexture = None, bottomTextureColor = None, shirt = None, bottom = None):
        if head:
            self.head = head
        if torso:
            self.torso = torso
        if legs:
            self.legs = legs
        if gender:
            self.gender = gender
        if armColor:
            self.armColor = self.checkIsDefaultColor(armColor)
        if gloveColor:
            self.gloveColor = self.checkIsDefaultColor(gloveColor)
        if legColor:
            self.legColor = self.checkIsDefaultColor(legColor)
        if headColor:
            self.headColor = self.checkIsDefaultColor(headColor)
        if topTexture:
            self.topTex = topTexture
        if topTextureColor:
            self.topTexColor = topTextureColor
        if sleeveTexture:
            self.sleeveTex = sleeveTexture
        if sleeveTextureColor:
            self.sleeveTexColor = sleeveTextureColor
        if bottomTexture:
            self.botTex = bottomTexture
        if bottomTextureColor:
            self.botTexColor = bottomTextureColor
        if shirt:
            str, colorIndex = shirt
            defn = ShirtStyles[str]
            self.topTex = defn[0]
            self.topTexColor = defn[2][colorIndex][0]
            self.sleeveTex = defn[1]
            self.sleeveTexColor = defn[2][colorIndex][1]
        if bottom:
            str, colorIndex = bottom
            defn = BottomStyles[str]
            self.botTex = defn[0]
            self.botTexColor = defn[1][colorIndex]

    def newToonRandom(self, seed = None, gender = 'm', npc = 0, stage = None):
        if seed:
            generator = random.Random()
            generator.seed(seed)
        else:
            generator = random
        self.type = 't'
        self.legs = generator.choice(toonLegTypes + ['m',
         'l',
         'l',
         'l'])
        self.gender = gender
        if not npc:
            if stage == MAKE_A_TOON:
                animalIndicesToUse = allToonHeadAnimalIndicesTrial
                animal = generator.choice(animalIndicesToUse)
                self.head = toonHeadTypes[animal]
            else:
                self.head = generator.choice(toonHeadTypes)
        else:
            self.head = generator.choice(toonHeadTypes[:22])
        top, topColor, sleeve, sleeveColor = getRandomTop(gender, generator=generator)
        bottom, bottomColor = getRandomBottom(gender, generator=generator)
        if gender == 'm':
            self.torso = generator.choice(toonTorsoTypes[:3])
            self.topTex = top
            self.topTexColor = topColor
            self.sleeveTex = sleeve
            self.sleeveTexColor = sleeveColor
            self.botTex = bottom
            self.botTexColor = bottomColor
            color = generator.choice(defaultColorList)
            self.armColor = color
            self.legColor = color
            self.headColor = color
        else:
            self.torso = generator.choice(toonTorsoTypes[:6])
            self.topTex = top
            self.topTexColor = topColor
            self.sleeveTex = sleeve
            self.sleeveTexColor = sleeveColor
            if self.torso[1] == 'd':
                bottom, bottomColor = getRandomBottom(gender, generator=generator, girlBottomType=SKIRT)
            else:
                bottom, bottomColor = getRandomBottom(gender, generator=generator, girlBottomType=SHORTS)
            self.botTex = bottom
            self.botTexColor = bottomColor
            color = generator.choice(defaultColorList)
            self.armColor = color
            self.legColor = color
            self.headColor = color
        self.gloveColor = self.checkIsDefaultColor(0)

    def asTuple(self):
        return (self.head,
         self.torso,
         self.legs,
         self.gender,
         self.armColor,
         self.gloveColor,
         self.legColor,
         self.headColor,
         self.topTex,
         self.topTexColor,
         self.sleeveTex,
         self.sleeveTexColor,
         self.botTex,
         self.botTexColor)

    def getType(self):

        if self.type == 't':
            type = self.getAnimal()
        else:
            notify.error('Invalid DNA type: ', self.type)
        return type

    def getAnimal(self):
        if not hasattr(self, 'head'):
            self.head = ['d']
        if self.head[0] == 'd':
            return 'dog'
        elif self.head[0] == 'c':
            return 'cat'
        elif self.head[0] == 'm':
            return 'mouse'
        elif self.head[0] == 'h':
            return 'horse'
        elif self.head[0] == 'r':
            return 'rabbit'
        elif self.head[0] == 'f':
            return 'duck'
        elif self.head[0] == 'p':
            return 'monkey'
        elif self.head[0] == 'b':
            return 'bear'
        elif self.head[0] == 's':
            return 'pig'
        elif self.head[0] == 'x':
            return 'deer'
        elif self.head[0] == 'z':
            return 'beaver'
        elif self.head[0] == 'a':
            return 'alligator'
        elif self.head[0] == 'v':
            return 'fox'
        elif self.head[0] == 'n':
            return 'bat'
        elif self.head[0] == 't':
            return 'raccoon'
        elif self.head[0] == 'g':
            return 'turkey'
        elif self.head[0] == 'e':
            return 'koala'
        elif self.head[0] == 'j':
            return 'kangaroo'
        elif self.head[0] == 'k':
            return 'kiwi'
        elif self.head[0] == 'l':
            return 'armadillo'
        else:
            notify.error('unknown headStyle: ', self.head[0])

    def getHeadSize(self):
        if self.head[1] == 'l':
            return 'long'
        elif self.head[1] == 's':
            return 'short'
        else:
            notify.error('unknown head size: ', self.head[1])

    def getMuzzleSize(self):
        if self.head[2] == 'l':
            return 'long'
        elif self.head[2] == 's':
            return 'short'
        else:
            notify.error('unknown muzzle size: ', self.head[2])

    def getTorsoSize(self):
        if self.torso[0] == 'l':
            return 'long'
        elif self.torso[0] == 'm':
            return 'medium'
        elif self.torso[0] == 's':
            return 'short'
        else:
            notify.error('unknown torso size: ', self.torso[0])

    def getLegSize(self):
        if self.legs == 'l':
            return 'long'
        elif self.legs == 'm':
            return 'medium'
        elif self.legs == 's':
            return 'short'
        else:
            notify.error('unknown leg size: ', self.legs)

    def getGender(self):
        return self.gender

    def getClothes(self):
        if len(self.torso) == 1:
            return 'naked'
        elif self.torso[1] == 's':
            return 'shorts'
        elif self.torso[1] == 'd':
            return 'dress'
        else:
            notify.error('unknown clothing type: ', self.torso[1])

    def getArmColor(self):
        return self.armColor
    
    def getLegColor(self):
        return self.legColor

    def getHeadColor(self):
        return self.headColor

    def getGloveColor(self):
        return self.gloveColor

    def getBlackColor(self):
        try:
            return allColorsList[26]
        except:
            return allColorsList[0]

    def getWhiteColor(self):
        return allColorsList[0]

    def setTemporary(self, newHead, newArmColor, newLegColor, newHeadColor):
        if not self.cache and self.getArmColor != newArmColor:
            self.cache = (self.head,
             self.armColor,
             self.legColor,
             self.headColor)
            self.updateToonProperties(head=newHead, armColor=newArmColor, legColor=newLegColor, headColor=newHeadColor)

    def restoreTemporary(self, oldStyle):
        cache = ()
        if oldStyle:
            cache = oldStyle.cache
        if cache:
            self.updateToonProperties(head=cache[0], armColor=cache[1], legColor=cache[2], headColor=cache[3])
            if oldStyle:
                oldStyle.cache = ()
