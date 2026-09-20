from toontown.chat.ui.speedchat.SCCustomMenu import SCCustomMenu
from toontown.chat.ui.speedchat.SCEmoteMenu import SCEmoteMenu
from toontown.chat.ui.speedchat.TTSCToontaskMenu import TTSCToontaskMenu
from toontown.toonbase import TTLocalizer

speedChatStructure = [
    [SCEmoteMenu, TTLocalizer.SCMenuEmotions],
    [SCCustomMenu, TTLocalizer.SCMenuCustom],
    [TTLocalizer.SCMenuHello, {100: 0}, {101: 0}, {102: 0}, {103: 0}, {104: 0}, {105: 0}, {106: 0}, 107, 108, 109, 110],
    [TTLocalizer.SCMenuBye, {200: 0}, {201: 0}, {202: 0}, 203, 204, 205, 206, 208, 209, 207],
    [TTLocalizer.SCMenuHappy, {300: 1}, {301: 1}, {302: 1}, 303, {304: 1}, 305, 316, 317, 306, 307, 308, 309, 310, 311, {312: 1}, {313: 1}, {314: 1}, 315, 318, 319],
    [TTLocalizer.SCMenuSad, {400: 2}, {401: 2}, {402: 2}, 403, 404, 405, 406, 407, 408, 411, 409, 410],
    [
        TTLocalizer.SCMenuFriendly,
        [TTLocalizer.SCMenuPronouns, 550, 551, 552, 553, 554, 558, 555, 556, 557],
        [TTLocalizer.SCMenuFriendlyYou, 600, 601, 602, 603],
        [TTLocalizer.SCMenuFriendlyILike, 700, 701, 702, 703, 704, 705, 706],
        505, 506, 507, 508, 509, 510, 515, 511, 512, 513, 514, 516
    ],
    [
        TTLocalizer.SCMenuReplies,
        [
            TTLocalizer.SCMenuEmoticons,
            450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462
        ],
        500, 501, 502, 503, 504, 1602, 5
    ],
    [
        TTLocalizer.SCMenuSorry,
        [
            TTLocalizer.SCMenuBugs,
            650, 30508
        ],
        800, 801, 802, 803, 804, 811, 814, 812, 813, 818, 805, 806, 807, 819, 816, 817, 808, 820, 810
    ],
    [TTLocalizer.SCMenuStinky, {900: 3}, {901: 3}, {902: 3}, {903: 3}, 904, {905: 3}, 907, 908, 909, 910],
    [
        TTLocalizer.SCMenuPlaces,
        [TTLocalizer.SCMenuPlacesPlayground, 1100, 1101, 1105, 1106, 1134, 1108, 1107, 1109, 1125, 1110, 1111, 1126, 1117],
        [
            TTLocalizer.SCMenuPlacesCogs,
            [TTLocalizer.SCMenuHQSellbot, 1114, 1115, 1116],
            [TTLocalizer.SCMenuHQCashbot, 1119, 1120, 1121],
            [TTLocalizer.SCMenuHQLawbot, 1122, 1123, 1135, 1124],
            [TTLocalizer.SCMenuHQBossbot, 1127, 1128, 1129],
            1102, 1103, 1104
        ],
        [TTLocalizer.SCMenuPlacesEstate, 1112, 1113, 1013, 1118],
        [TTLocalizer.SCMenuPlacesWait, 1015, 1007, 1008, 1010, 1011, 1014, 1017],
        1000, 1001, 1002, 1003, 1004, 1005, 1006, 1009, 1012
    ],
    [TTLocalizer.SCMenuGroups, 5000, 5001, 5002, 5003, 5004, 5005, 5006],
    [
        TTLocalizer.SCMenuClubs,
        [
            TTLocalizer.SCMenuToontasks,
            4900, 4901, 4902,
        ],
        4903, 4904, 4905,
    ],
    [
        TTLocalizer.SCMenuToontasks,
        [TTSCToontaskMenu, TTLocalizer.SCMenuToontasksMyTasks],
        [TTLocalizer.SCMenuToontasksINeedMore, 1206, 1210, 1211, 1212, 1213, 1207, 1214, 1215, 1216, 1217],
        1200, 1201, 1202, 1208, 1203, 1209, 1204, 1205
    ],
    [
        TTLocalizer.SCMenuBattle,
        [
            TTLocalizer.SCMenuBattleGags,
            [TTLocalizer.SCMenuBattleYouShould, 1300, 1301, 1302, 1306, 1304, 1305, 1303, 1307],
            [TTLocalizer.SCMenuBattleLetsUse, 1500, 1501, 1502, 1506, 1504, 1505, 1503, 1507],
            [TTLocalizer.SCMenuBattleImGoingTo, 1560, 1561, 1562, 1566, 1564, 1565, 1563, 1567],
            1401, 1402, 1600, 1413, 1417
        ],
        [
            TTLocalizer.SCMenuBattleStrategy,
            [TTLocalizer.SCMenuBattleActions, 1350, 1351, 1353, 1354, 1355, 1356, 1357, 1370, 1371, 1373, 1374, 1375],
            [TTLocalizer.SCMenuBattleLetsGoFor, 1530, 1531, 1532, 1533, 1534, 1535, 1536, 1537, 1538, 1539, 1540, 1541],
            1414, 1542, 1543, 1544, 1545, 1546, 1547,
        ],
        [TTLocalizer.SCMenuBattleTaunts, 1403, 1406, 1520, 1521, 1522, 1523, 1524, 1525, 1526, 1527, 1407, 1408],
        1400, 1416, 1404, 1405, 1409, 1410, 1411, 1412
    ],
    {1: 17}, {2: 18}, 3
]

mintMenuStructure = [42000, 42001, 42002, 40000, 40001]

cfoMenuStructure = [
    [TTLocalizer.SCMenuCFOBattleCranes, 2100, 2101, 2102, 2103, 2104, 2105, 2106, 2107, 2108, 2109, 2110],
    [TTLocalizer.SCMenuCFOBattleGoons, 2120, 2121, 2122, 2123, 2124, 2125, 2126],
    2130, 2131, 2132, 2133, 1410
]

cloMenuStructure = [
    [TTLocalizer.SCMenuCLOBattleSound, 2209, 2210, 2214, 2215],
    [TTLocalizer.SCMenuCLOBattleTraps, 2225, 2226, 2227, 2220, 2221, 2211, 2228, 2222, 2223, 2224],
    [TTLocalizer.SCMenuCLOBattleTreasures, 2131, 2132],
    [TTLocalizer.SCMenuCLOHardmodeSpecialists, 2230, 2231],
    2133, 2217, 2201, 2219
]

cloHardModeMenuStructure = [
    [TTLocalizer.SCMenuCLOBattleSound, 2209, 2210, 2214, 2215],
    [TTLocalizer.SCMenuCLOBattleTraps, 2225, 2226, 2227, 2220, 2221, 2211, 2228, 2222, 2223, 2224, 2229],
    [TTLocalizer.SCMenuCLOBattleTreasures, 2131, 2132],
    [TTLocalizer.SCMenuCLOHardmodeSpecialists, 2230, 2231, 2232, 2233],
    2133, 2217, 2201, 2219
]

cgcMenuStructure = [42000, 42001, 42002, 42003, 42004, 42005, 42006, 42007]
ceoMenuStructure = [
    [TTLocalizer.SCMenuCEOBattleDining, 2300, 2301, 2302, 2303, 2304, 2305, 2306, 2307, 2308, 2309, 2310, 2311],
    2312, 2313, 2314, 2315, 2316, 2317, 2318,
]
cooMenuStructure = [2400, 2401, 2402, 2403, 2404, 2405, 2406, 2407, 2408, 2409, 2410, 2411, 2412, 2413, 2414, 2415, 2416]
puzzleMenuStructure = [
    [TTLocalizer.SCMenuDABattle_TIAR, 41000, 41001, 41002, 41003, 41004],
    [TTLocalizer.SCMenuDABattle_M, 41010, 41011, 41012],
    [TTLocalizer.SCMenuDABattle_ATS, 41000, 41030],
    [TTLocalizer.SCMenuDABattle_SF, 41020, 41021, 41022, 41023, 41024],
    [TTLocalizer.SCMenuDABattle_CT, 41104, 41105, 41106, 41107, 41108, 41109],
    [TTLocalizer.SCMenuDABattle_T, 41110, 41111, 41112, 41113, 41114],
    41115, 41116
]
