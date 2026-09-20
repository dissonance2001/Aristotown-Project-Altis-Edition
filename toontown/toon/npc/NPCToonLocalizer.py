"""
Strings and constants related to Toon NPC names.
"""

from toontown.toon.npc.NPCToonConstants import NPCToonID
from toontown.toon.npc.NPCToonRegistry import NPCToonDict

Flippy = 'Flippy'
lHQOfficer = 'HQ Officer'
NPCToonNames = {npcId: npcToon.name for npcId, npcToon in NPCToonDict.items()}
NPCName2Id = {v: k for k, v in list(NPCToonNames.items())}
