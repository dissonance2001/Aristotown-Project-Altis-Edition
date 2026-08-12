GROUP_MIN_SIZE = 2
GROUP_MAX_SIZE = 8
GROUP_HEARTBEAT_SECONDS = 15.0
GROUP_TIMEOUT_SECONDS = 50
GROUP_INVITE_TIMEOUT_SECONDS = 90

NOTIFY_INFO = 0
NOTIFY_SUCCESS = 1
NOTIFY_ERROR = 2

ACTIVITIES = (
    ('VP', 8),
    ('CFO', 8),
    ('CJ', 8),
    ('CEO', 8),
    ('Cog Building', 4),
    ('Sellbot Factory', 4),
    ('Cashbot Mint', 4),
    ('Lawbot DA Office', 4),
    ('Bossbot Country Club', 4),
    ('Racing', 4),
    ('Golfing', 4),
    ('Trolley', 4),
    ('Fishing', 4),
    ('High Roller', 4),
    ('Pacesetter', 4),
    ('Chainsaw Consultant', 4),
    ('Other', 4),
)

ACTIVITY_NAMES = tuple(entry[0] for entry in ACTIVITIES)
ACTIVITY_SIZES = dict(ACTIVITIES)
