from enum import IntEnum

"""
An enum containing one-time cutscenes that can be seen by the player.
Relevant objects will call the cutscenes, and mark on the toon
that it has been seen once it has been.

This is database stuff, do not use auto.
"""


class OneTimeCutscenes(IntEnum):
    KudosUnlock_TTC = 1
    KudosUnlock_BB = 2
    KudosUnlock_YOTT = 3
    KudosUnlock_DG = 4
    KudosUnlock_MML = 5
    KudosUnlock_TB = 6
    KudosUnlock_AA = 7
    KudosUnlock_DDL = 8

    KudosBookFlash = 9

    PizzeriaEasterEgg = 10
    HighRoller_TeleportTutorial = 11

    GagsolineGroupsTutorial = 12


AllKudosUnlocks = [
    OneTimeCutscenes.KudosUnlock_TTC,
    OneTimeCutscenes.KudosUnlock_BB,
    OneTimeCutscenes.KudosUnlock_YOTT,
    OneTimeCutscenes.KudosUnlock_DG,
    OneTimeCutscenes.KudosUnlock_MML,
    OneTimeCutscenes.KudosUnlock_TB,
    OneTimeCutscenes.KudosUnlock_AA,
    OneTimeCutscenes.KudosUnlock_DDL,
]
