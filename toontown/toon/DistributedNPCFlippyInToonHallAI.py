from __future__ import absolute_import
from toontown.toon.DistributedNPCToonAI import *

class DistributedNPCFlippyInToonHallAI(DistributedNPCToonAI):

    def __init__(self, air, npcId, questCallback = None, hq = 0):
        DistributedNPCToonAI.__init__(self, air, npcId, questCallback)
