from toontown.level.EntityTypes import *
from toontown.building import ElevatorConstants


class PersistentLevelMgr(LevelMgr):
    type = 'levelMgr'
    permanent = 1
    attribs = (
        ('musicKey', '', 'string'),
        ('battleMusicKey', '', 'string'),
        ('titleColor', 'ttc', 'string'),
        ('skyboxModel', '', 'string')
    )


class Crushable(Entity):
    """
    Crushable(Entity)
    """

    abstract = 1
    attribs = (
        ('pos', Point3(0, 0, 0), 'pos'),
        ('hpr', Vec3(0, 0, 0), 'hpr'),
        ('crushCellId', None, 'entId', {'type': 'crusherCell'}),
        ('gridId', None, 'entId', {'type': 'grid'})
    )


class Crate(Crushable):
    type = 'crate'
    blockAttribs = ('hpr',)
    attribs = (
        ('modelType', 0, 'int', {'min': 0, 'max': 1}),
        ('scale', 0.92, 'float'),
        ('pushable', 1, 'bool')
    )


class Grid(Nodepath):
    """
    Grid(Nodepath)
    """

    type = 'grid'

    blockAttribs = (
        'hpr',
    )

    attribs = (
        ('cellSize', 3, 'float'),
        ('numCol', 3, 'int'),
        ('numRow', 3, 'int')
    )


class Tunnel(Nodepath):
    """
    Tunnel(Nodepath)
    """

    type = 'tunnel'

    attribs = (
        ('destinationZone', -1, 'int'),
        ('tunnelId', -1, 'int'),
        ('destinationTunnelId', -1, 'int'),
        ('tunnelModelPath', 'phase_3.5/models/modules/cc_m_gen_prp_tunnel_st2sz', 'choice', {
            'choiceSet': ('playground', 'street', 'between-street'),
            'valueDict': {
                'playground': 'phase_3.5/models/modules/cc_m_gen_prp_tunnel_sz2st',
                'street': 'phase_3.5/models/modules/cc_m_gen_prp_tunnel_st2sz',
                'between-street': 'phase_5/models/modules/neighborhood_tunnel_TT',
            }
        }),
        # Determines if we are going to a legacy location or not
        # We will need to keep support for this for a while until all old streets are revamped
        ('legacyDestination', 0, 'bool'),
    )


class SuitPathCollection(Nodepath):
    """
    SuitPathCollection(Nodepath)
    """

    type = 'suitPathCollection'

    attribs = (
        ('spawnDataKey', 'test_spawn', 'string'),
        ('minSuits', 1, 'int'),
        ('maxSuits', 2, 'int'),
        ('battleCellIds', [], 'entIdList'),
        ('buildingIds', [], 'entIdList'),
        ('spawnDelay', 5.0, 'float'),
        ('enabled', 0, 'bool'),
    )


class SuitPathPoint(Nodepath):
    """
    SuitPathPoint(Nodepath)
    """

    type = 'suitPathPoint'

    attribs = (
        ('pointsTo', 0, 'entId', {'type': 'suitPathPoint'}),
    )


class SuitBattleCell(Nodepath):
    """
    SuitBattleCell(Nodepath)
    """

    type = 'suitBattleCell'


class BuildingEntity(Nodepath):
    """
    BuildingEntity(Nodepath)
    """
    type = 'building'

    attribs = (
        ('modelFilename', 'phase_6/models/modules/gagShop_OZ', 'const'),
        ('blockNumber', 0, 'int'),
        ('destZone', 0, 'int'),
        ('capturable', 1, 'bool'),
        ('enabled', 0, 'bool'),
        ('buildingName', 'Toon Building', 'string'),
    )


class BuildingMgr(Entity):
    """
    BuildingMgr(Entity)
    """

    type = 'buildingMgr'
    permanent = 1

    attribs = (
        ('name', 'BuildingMgr', 'const'),
        ('parentEntId', 0, 'const'),
        ('suitBuildingMin', 1, 'int'),
        ('suitBuildingMax', 3, 'int'),
    )


class TextNodeEntity(Nodepath):
    """
    TextNodeEntity(Nodepath)
    """

    type = 'textNode'

    attribs = (
        ('text', 'Hello World!', 'string'),
        ('color', Vec4(0, 0, 0, 1), 'color'),  # Client Only
        ('font', 'phase_3/fonts/Humanist.ttf', 'string'),
        ('smallCaps', 0, 'bool'),
        ('dropShadow', 0, 'bool'),
        ('stumble', 0.0, 'float'),
        ('stomp', 0.0, 'float'),
        ('wiggle', 0.0, 'float'),
        ('kern', 0.0, 'float'),
        ('height', 0.0, 'float'),
        ('width', 0.0, 'float'),
        ('indent', 0.0, 'float'),
    )


class Mover(Nodepath):
    type = 'mover'
    attribs = (
        ('modelPath', 0, 'choice', {
            'choiceSet':
                ['square'],
            'valueDict':
                {'square': 0}
        }),
        ('pos', Point3(0, 0, 0), 'pos'),
        ('hpr', Vec3(0, 0, 0), 'hpr'),
        ('switchId', 0, 'entId', {'type': 'button'}),
        ('entity2Move', 0, 'entId'),
        ('moveTarget', 0, 'entId'),
        ('pos0Move', 2, 'float'), ('pos0Wait', 2, 'float'),
        ('pos1Move', 2, 'float'), ('pos1Wait', 2, 'float'),
        ('startOn', 0, 'bool'),
        ('cycleType', 'return', 'choice', {
            'choiceSet': [
                'return',
                'linear',
                'loop',
                'oneWay'
            ]
        })
    )


class Platform(Nodepath):
    type = 'platform'
    attribs = (
        ('modelPath', 'phase_9/models/cogHQ/platform1', 'bamfilename'),
        ('modelScale', Vec3(1, 1, 1), 'scale'),
        ('floorName', 'platformcollision', 'string'),
        ('offset', Point3(0, 0, 0), 'pos'),
        ('period', 2, 'float'),
        ('waitPercent', 0.1, 'float', {'min': 0, 'max': 1}),
        ('phaseShift', 0.0, 'float', {'min': 0, 'max': 1}),
        ('motion', 'noBlend', 'choice', {
            'choiceSet': [
                'noBlend',
                'easeInOut',
                'easeIn',
                'easeOut']
        })
    )


class QuickElevator(Nodepath):
    type = 'quickElevator'
    attribs = (
        ('exitElevator', 0, 'entId'),
        ('isLocked', 0, 'bool'),
        ('unlockEvent', 0, 'entId', {'output': 'bool'}),
        ('elevatorType', 0, 'choice', {
            'choiceSet': ('normal', 'mint', 'office', 'stage', 'dominium', 'vp'),
            'valueDict': {'normal': ElevatorConstants.ELEVATOR_NORMAL, 'mint': ElevatorConstants.ELEVATOR_MINT,
                          'office': ElevatorConstants.ELEVATOR_OFFICE, 'stage': ElevatorConstants.ELEVATOR_STAGE,
                          'dominium': ElevatorConstants.ELEVATOR_DERRICK_MAN, 'vp': ElevatorConstants.ELEVATOR_VP}
        }),
    )


class QuestEntity(Entity):
    abstract = 1
    type = 'questEntity'
    attribs = (
        ('wantedQuest', (0, 0, 0), 'questId'),
    )


class CutsceneQuestEntity(QuestEntity):
    abstract = 1
    type = 'cutsceneQuestEntity'
    attribs = (
        # Cutscene that plays when they receive the relevant quest
        ('ctsc_getQuest_key', '', 'str'),
        ('ctsc_getQuest_args', {}, 'dict'),
        # Cutscene that plays when they finish the relevant quest
        ('ctsc_finQuest_key', '', 'str'),
        ('ctsc_finQuest_args', {}, 'dict'),
    )


class QuestModel(CutsceneQuestEntity, Model):
    type = 'questModel'
    attribs = (
        ('hideCondition', 'None', 'choice', {
            'choiceSet': ['None', 'unfinishedQuest', 'finishedQuest'],
        }),
    )


class QuestAnimatedEntity(CutsceneQuestEntity, Nodepath):
    type = 'questAnimated'
    attribs = (
        ('modelPath', None, 'bamfilename'),
        ('animList', [], 'list'),
        # If the local avatar enters the area with their quest unfinished
        ('qst_unfinBehavior', 'None', 'choice', {
            'choiceSet': ['None', 'Pose', 'Loop', 'Hide', 'Special'],
        }),
        ('qst_unfinAnim', '', 'str'),
        ('qst_unfinArgs', [], 'list'),
        # If the local avatar enters the area with their quest finished
        ('qst_finBehavior', 'None', 'choice', {
            'choiceSet': ['None', 'Pose', 'Loop', 'Hide', 'Special'],
        }),
        ('qst_finAnim', '', 'str'),
        ('qst_finArgs', [], 'list'),
    )


class QuestInteractible(QuestAnimatedEntity):
    type = 'questInteractible'

    attribs = (
        ('interactibleType', 'test_crate', 'str'),
        # Interaction collision sphere
        ('sphereRadius', 5.0, 'float'),
        ('spherePos', (0.0, 0.0, 0.0), 'pos')
    )


class QuestCollectible(QuestAnimatedEntity):
    type = 'questCollectible'
