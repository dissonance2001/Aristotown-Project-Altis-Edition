"""
Utility functions for the AI server.
"""
from typing import List
from toontown.toon.DistributedToonAI import DistributedToonAI


def avIds2Avs(avIds: List[int]) -> List[DistributedToonAI]:
    """Given a list of avIds, return all avs."""
    retList = []
    for avId in avIds:
        toon = simbase.air.doId2do.get(avId)
        if toon:
            retList.append(toon)
    return retList
