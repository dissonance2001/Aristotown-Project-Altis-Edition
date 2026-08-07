# Major Player Place is designed to host more than one temporary miniboss
# room. Shared instance identifiers live in InstanceGlobals so other entrances
# can route through the same global InstanceZoneManagerAI.

from toontown.instances import InstanceGlobals

HIGH_ROLLER = InstanceGlobals.HIGH_ROLLER
BOSS_BATTLE_STATE = 'majorPlayerBossBattle'
INSTANCE_LOADER = 'townLoader'
