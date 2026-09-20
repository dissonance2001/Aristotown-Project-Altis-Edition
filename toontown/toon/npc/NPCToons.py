import os
import random
from collections import OrderedDict

from panda3d.core import ConfigVariableList
from toontown.nametag import NametagGroup

from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.hood import ZoneUtil
from toontown.toon import ToonDNA
from toontown.toon.npc import NPCToonRegistry
from toontown.toon.npc.NPCToonConstants import NPCToonEnum as NPC
from toontown.toonbase import TTLocalizer, RealmGlobals
from toontown.toonbase import ToontownGlobals


names = TTLocalizer.NPCToonNames
NPCToon = NPCToonRegistry.NPCToon
NPCToonDict = NPCToonRegistry.NPCToonDict


def createNPC(air, npcId, npcToon: NPCToon, posIndex = 0, *args, **kwargs):
    # These imports need to be here (circular dependency)
    from .NPCToonClassesAI import createNPC
    npc = createNPC(npcToon.npcType, air, npcId, *args, **kwargs)
    npcToon.createNPC(npc, posIndex)
    return npc


def createNpcsInZone(air, zoneId):
    output = []
    # Would use set here to ensure no duplicates, but order is important
    for cnt, npcId in enumerate(list(OrderedDict.fromkeys(zone2NpcDict.get(ZoneUtil.getCanonicalZoneId(zoneId), [])))):
        npcToon: NPCToon = NPCToonDict.get(npcId)
        if npcToon.npcType == NPC.PARTYPERSON:
            continue

        # Temporarily disable QA Toons from spawning.
        if npcToon.npcType == NPC.QA:
            continue

        if npcToon.npcType == NPC.QA and not RealmGlobals.getCurrentRealm().isPrivateRealm():
            continue
        output.append(createNPC(air, npcId, npcToon, cnt))
    return output


def createLocalNPC(npcId, toonClass=None, extraArgs=None):
    npc: NPCToon = NPCToonDict.get(npcId)
    if not npc:
        return None
    return npc.createNPCLocal(toonClass=toonClass, extraArgs=extraArgs)


def createRandomLocalNPC(toonClass=None, extraArgs=None, extraCallables=None):
    npc: NPCToon = random.choice(list(NPCToonDict.values()))
    return npc.createNPCLocal(toonClass=toonClass, extraArgs=extraArgs, extraCallables=extraCallables)


# Figure out what Holiday IDs we want for the batcoin and material crew
elphabatHolidayIds = [ToontownGlobals.HALLOWEEN, ToontownGlobals.HALLOWEEN_MIX_WINTER_HOLIDAY]
if ConfigVariableString('current-seasonal-holiday', 'None').getValue() == 'april-fools' and ConfigVariableBool('want-halloween-with-april-fools').getValue():
    elphabatHolidayIds.append(ToontownGlobals.APRIL_FOOLS)


# currently needed for getNPCNameID, can't delete it yet
# del names
zone2NpcDict = {}


def generateZone2NpcDict():
    for npcId, npcToon in NPCToonDict.items():
        if npcToon.npcType == NPC.RESTORATION:
            # don't generate these NPC's; they're created by a DO on the client side, for client side only things
            continue
        if npcToon.zoneId in zone2NpcDict:
            zone2NpcDict[npcToon.zoneId].append(npcId)
        else:
            zone2NpcDict[npcToon.zoneId] = [npcId]


def getNPCName(npc_id):
    npc = NPCToonDict.get(npc_id)
    if npc:
        return npc.name
    else:
        return None


def getNPCNameID(nameId):
    """
    :return: the number in names[x]
    """
    return list(names.keys())[list(names.values()).index(nameId)]


def getNPCZone(npc_id):
    npc = NPCToonDict.get(npc_id)
    if npc:
        return npc.zoneId
    else:
        return None


def getNPCType(npc_id):
    npc = NPCToonDict.get(npc_id)
    if npc:
        return npc.npcType
    else:
        return None


def getNPCTypeValue(index):
    npcTypes = {
        NPC.REGULAR: "NPC.REGULAR",
        NPC.CLERK: "NPC.CLERK",
        NPC.TAILOR: "NPC.TAILOR",
        NPC.HQ: "NPC.HQ",
        NPC.FISHERMAN: "NPC.FISHERMAN",
        NPC.PETCLERK: "NPC.PETCLERK",
        NPC.KARTCLERK: "NPC.KARTCLERK",
        NPC.PARTYPERSON: "NPC.PARTYPERSON",
        NPC.FLIPPYTOONHALL: "NPC.FLIPPYTOONHALL",
        NPC.RODCLERK: "NPC.RODCLERK",
        NPC.TRASHCAT: "NPC.TRASHCAT",
        NPC.HQRANGER: "NPC.HQRANGER",
        NPC.SNOWMAN: "NPC.SNOWMAN",
        NPC.ELF: "NPC.ELF",
        NPC.WEBSTER: "NPC.WEBSTER",
        NPC.VALENTINES: "NPC.VALENTINES",
        NPC.FIREWORK: "NPC.FIREWORK",
        NPC.SECRETARY: "NPC.SECRETARY",
        NPC.ELPHABAT: "NPC.ELPHABAT",
        NPC.EASTER: "NPC.EASTER",
        NPC.RESTORATION: "NPC.RESTORATION",
        NPC.GHASTLY: "NPC.GHASTLY",
        NPC.TURNKEY: "NPC.TURNKEY",
        NPC.SPIRITS: "NPC.SPIRITS",
        NPC.PLANT: "NPC.PLANT",
        NPC.QA: "NPC.QA",
        NPC.TUMBLES: "NPC.TUMBLES",
        NPC.BUBBY: "NPC.BUBBY",
        NPC.HALLOWEEN_PASS: "NPC.HALLOWEEN_PASS",
        NPC.GNG_CLERK: "NPC.GNG_CLERK",
        NPC.RED_NOSE: "NPC.RED_NOSE",
        NPC.CLUB_CREATION: "NPC.CLUB_CREATION",
        NPC.CLUB_SHOP: "NPC.CLUB_SHOP",
        NPC.TUTORIAL: "NPC.TUTORIAL",
        NPC.HQ_INTERN: "NPC.HQ_INTERN",
        NPC.ITEM_SELLER: "NPC.ITEM_SELLER",
    }
    return npcTypes[index]


def getBuildingArticle(zoneId):
    article = TTLocalizer.zone2TitleDict.get(zoneId)
    if not article:
        zoneId = ZoneUtil.getBranchZone(zoneId)
        whereName = ZoneUtil.getWhereName(zoneId, True)
        if whereName == 'playground':
            article = TTLocalizer.QuestsLocationPlaygroundArticle
        else:
            article = ''
    else:
        article = article[1]
    return article


def getBuildingTitle(zoneId):
    title = TTLocalizer.zone2TitleDict.get(zoneId)
    if not title:
        zoneId = ZoneUtil.getBranchZone(zoneId)
        title = TTLocalizer.GlobalStreetNames.get(zoneId, "Unknown Location")[2]
    else:
        title = title[0]
    return title


def getNPCByNPCType(npcType: NPC) -> list:
    return [npcId for npcId, npc in NPCToonDict.items() if npc.npcType == npcType]


def filterForNPCs(
    npcTypes: list = None,
    safezoneIds: list = None,
    getIds: bool = False
        ) -> list:
    # Start searching.
    validNPCs = []
    for npcId, npc in NPCToonDict.items():
        # Filter by NPC types.
        if npcTypes is not None:
            if npc.npcType not in npcTypes:
                continue
        # Filter by hood ID.
        if safezoneIds is not None:
            if ZoneUtil.getSafeZoneId(npc.zoneId) not in safezoneIds:
                continue
        # This NPC is valid.
        validNPCs.append(npcId if getIds else npc)
    # Return valid NPCs.
    return validNPCs
