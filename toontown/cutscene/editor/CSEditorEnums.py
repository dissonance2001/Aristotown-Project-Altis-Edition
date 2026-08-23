# Python 2 compatibility enums for the Clash cutscene runtime.

class _EnumValue(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self is other


class _NameMap(object):
    def __init__(self, names):
        self._values = {}
        for name in names:
            value = _EnumValue(name)
            self._values[name] = value
            setattr(self, name, value)

    def __getitem__(self, name):
        return self._values[name]

    def __contains__(self, name):
        return name in self._values

    def names(self):
        return list(self._values.keys())

EventDefinitionEnum = _NameMap(['moveToonsInBlock', 'turnToonsToNode', 'turnToonsToPoint', 'moveSingleToon', 'turnSingleToonToNode', 'turnSingleToonToPoint', 'turnSingleToonToHpr', 'turnToonsToHpr', 'tpToonsToElevator', 'hideSuits', 'showSuits', 'moveCameraPosHpr', 'moveCameraPos', 'moveCameraHpr', 'changeCameraFov', 'reparentCamera', 'reparentNode', 'cameraToElevator', 'actorDialogue', 'actorDialogueIt', 'showNametag', 'hideNametag', 'actorChat', 'timeSleep', 'turnActor', 'moveActor', 'particleSystemRun', 'moveParticleSystemPos', 'moveParticleSystemHpr', 'nodePosHprScale', 'hideSuit', 'showSuit', 'doSuitAnim', 'doSuitBlendAnim', 'doSuitHeadAnim', 'doSuitPingpong', 'suitApplyVisualEffect', 'suitUnapplyVisualEffect', 'moveToonsToBattlePos', 'heavyDropKill', 'summonSuitErfit', 'animateSingleToon', 'animateAllToons', 'pingpongSingleToon', 'pingpongAllToons', 'duckShufflerRoll', 'duckShufflerEyePos', 'actorShutUp', 'showNode', 'hideNode', 'scaleNode', 'scaleNodeList', 'moveNode', 'posRelativeToOther', 'rotateNode', 'animateAllSuits', 'pingpongAllSuits', 'disguiseAllToons', 'undisguiseAllToons', 'setAllAnimStates', 'setOneAnimState', 'clearAllSuitChat', 'dyeParticleSystem', 'toonFireFromCannon', 'hideToons', 'showToons', 'hideToon', 'showToon', 'colorScaleNode', 'alphaScaleNode', 'setAllEmote', 'setOneEmote', 'suitSupaFly', 'suitLockPropeller', 'suitProjectileFly', 'turnSuitsToNode', 'turnSuitsToPoint', 'turnSingleSuitToNode', 'turnSingleSuitToPoint', 'turnSingleSuitToHpr', 'turnSuitsToHpr', 'suitFireFromCannon', 'chainsawSetHeadGlitch', 'prethinkerDoBrainBlast', 'playSoundEffect', 'stopSoundEffect', 'playMusic', 'stopMusic', 'functionCall', 'functionLerp', 'openElev', 'closeElev', 'laaTrapdoor', 'showTimescaleChange', 'applyStagelight', 'setClearColorScale', 'dustcloudNode', 'doScreenFade', 'showBoss', 'hideBoss', 'showBosses', 'hideBosses', 'doBossAnimation', 'bossRollToPoint', 'turnAndMoveToon', 'createFog', 'destroyFog', 'setFogColor', 'setFogDensity', 'setToonExpression', 'setToonSpecies', 'suitColorScale', 'createExplosion', 'setToonEyes', 'basicLabel', 'colorNode', 'fakeCannonControl', 'squishToon', 'jiggleNode', 'highRollerDropTelevisionSet', 'highRollerSetTelevisionDice', 'highRollerSpawnWheel', 'highRollerSpawnPodiums'])

SubEventArgumentType = _NameMap(['slider_xyz', 'slider_hpr', 'slider_min_zero', 'slider_min_almost_zero', 'slider_float', 'slider_xyz_camera', 'slider_hpr_camera', 'slider_fov', 'textbox_str', 'textbox_float', 'dropdown_messages', 'dropdown_actors', 'dropdown_toons', 'dropdown_suits', 'dropdown_toon_anims', 'dropdown_suit_anims', 'dropdown_suit_head_anims', 'dropdown_node', 'dropdown_function', 'dropdown_elevators', 'dropdown_blendType', 'dropdown_blockShape', 'dropdown_particles', 'dropdown_visual_effects', 'dropdown_targetGroup', 'dropdown_suitFlyChoice', 'dropdown_suitFlyPosChoice', 'dropdown_sound_effects', 'dropdown_music', 'dropdown_fogType', 'dropdown_toonExpression', 'dropdown_toonSpecies', 'dropdown_toonEyes', 'boolean', 'slider_xyz_scale', 'slider_xyz_node', 'slider_hpr_node', 'dropdown_toon_anim_states', 'dropdown_arguments', 'slider_rgb', 'dropdown_toon_emote', 'slider_hpr_toon', 'slider_hpr_suit', 'slider_hpr_cannon', 'dropdown_bosses', 'dropdown_boss_anims'])

EventSequenceMode = _NameMap(['Sequence', 'Parallel'])

PauseFlags = _NameMap(['ChangingTime', 'TimelineState', 'PauseButton'])

ToonBlockShape = _NameMap(['Elevator', 'BigElevator', 'SingleFile', 'DoubleFile', 'FourWide', 'EightWide', 'Line', 'Circle'])

ToonSubEventTargetGroup = _NameMap(['All', 'Players', 'NPCs'])

