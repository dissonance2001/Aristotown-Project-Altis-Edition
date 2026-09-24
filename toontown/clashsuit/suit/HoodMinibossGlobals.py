from toontown.toonbase.ToontownGlobals import *

SPAWN_WEIGHTS = 0   # Weights of streets to spawn boss on
SPAWN_TIME = 1      # Time between spawns, in seconds.
SPAWN_LIMITED = 2   # Is boss limited to 1 per pg?

BossSpawnDict = {
 ToontownCentral: {'duckshfl':
                   ((25, 25, 25, 25),
                    180,
                    1)},
 DonaldsDock: {'ddiver':
                   ((25, 25, 25, 25),
                    180,
                    1)},
 YeOlde: {'gatekeep':
                   ((33, 34, 33),
                    180,
                    1)},
 DaisyGardens: {'bellring':
                   ((25, 25, 25, 25),
                    180,
                    1)},
 MinniesMelodyland: {'mouthp':
                   ((25, 25, 25, 25),
                    180,
                    1)},
 TheBrrrgh: {'fires':
                   ((25, 25, 25, 25),
                    180,
                    1)},
 OutdoorZone: {'treek':
                   ((25, 25, 25, 25),
                    180,
                    1)},
 DonaldsDreamland: {'fbed':
                   ((33, 34, 33),
                    180,
                    1)}
}
