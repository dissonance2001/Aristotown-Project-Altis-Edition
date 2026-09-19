from enum import IntEnum


class InvasionType(IntEnum):
    NORMAL = 0
    MEGA = 1


# Flags:
IFSkelecog = 1 << 0
IFWaiter = 1 << 1
IFV2 = 1 << 2
IFExe = 1 << 3

# Special case when sending a dept. invasion from UD -> AI (SuitInvasionManager)
UnmarkedDeptInvasion = 'unmarkedDeptInvasion'
