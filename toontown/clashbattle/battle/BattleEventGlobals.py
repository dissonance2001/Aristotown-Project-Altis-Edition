"""
Used to contain enums and other helpful things that relate to BattleEventDefinitions and suit passives.

When adding new events, be sure to add the corresponding enum here!
"""

from enum import IntEnum, auto


class BattleEventEnum(IntEnum):
    """
    BEGIN GENERAL EVENTS
    """

    EVENT_SET_PARTICIPANTS        = auto()  # args [toons, suits]
    EVENT_BEGIN_FIRST_ROUND       = auto()  # no args
    EVENT_BEGIN_ROUND             = auto()  # no args
    EVENT_END_ROUND               = auto()  # no args
    EVENT_BATTLE_END              = auto()  # no args
    EVENT_BATTLE_STATE            = auto()  # args [state: str]

    # NOTE: THE BATTLECALC'S ATTACK ORDER WILL GET OVERWRITTEN
    # AFTER THESE TWO EVENTS. IF YOU WANT TO ADD AN ATTACK BASED
    # ON EXISTING ATTACK ORDER, USE EVENT_ATTACK_ORDER
    EVENT_TOON_ATTACK_ORDER       = auto()  # args [attackOrder]

    # This event doesn't indicate something happening,
    # but is more like a request sent to all listening suits
    # to create their attacks and insert them into the attack
    # order.
    EVENT_SUIT_ATTACK_ORDER       = auto()  # no args
    EVENT_ATTACK_ORDER            = auto()  # args [attackOrder]
    EVENT_NORMAL_ATTACKS_OVER     = auto()  # no args

    # Called at the end of calculation for each
    # toon attack track
    EVENT_END_TOON_TRACK          = auto()  # args [attackTrack, attackList]
    # Called when all toons have used their gags, and it goes
    # on to the suit portion of the round
    EVENT_BEGIN_SUIT_ATTACKS      = auto()  # no args

    EVENT_TOON_USED_GAG          = auto()  # args [attack]

    EVENT_TOON_DAMAGE            = auto()  # args [suit, toon, damageAmount, attackTrack, attackIndex, attackLevel]
    EVENT_TOON_KNOCKBACK_DAMAGE  = auto()  # args [suit, toon, knockbackAmount, attackTrack]
    EVENT_TOON_COMBO_DAMAGE      = auto()  # args [suit, toon, comboAmount, attackTrack, attackIndex]

    EVENT_SUIT_DAMAGE            = auto()  # args [toon, suit, damageAmount, attackType, attackIndex]

    EVENT_GENERAL_DAMAGE         = auto()  # args [target, invoker, damageAmount, attackType, attackIndex]

    EVENT_HEALED                 = auto()  # args [toonHealed, healAmount]

    EVENT_STATUS_EFFECT_CREATED  = auto()  # args [avatar, statusEffect, effectId]
    EVENT_STATUS_EFFECT_COMBINED = auto()  # args [avatar, statusEffect, effectId]
    EVENT_STATUS_EFFECT_EXPIRED  = auto()  # args [avatar, effectId]

    EVENT_LURED_SUIT             = auto()  # args [suit, toon, roundsLured, lureEffect, attackIndex, attackLevel]
    EVENT_RELURED_SUIT           = auto()  # args [suit, toon, roundsLured, lureEffect, attackIndex, attackLevel]
    EVENT_SOAKED_SUIT            = auto()  # args [suit, toon, roundsSoaked, soakEffect, squirtAttack]
    EVENT_RESOAKED_SUIT          = auto()  # args [suit, toon, roundsSoaked, soakEffect, squirtAttack]

    EVENT_FIRED_SUIT             = auto()  # args [suit, toon]
    EVENT_SUED_SUIT              = auto()  # args [suit, toon]

    EVENT_PLACED_TRAP            = auto()  # args [suit, toon, trapDamage, trapLevel, attackIndex]
    EVENT_FAILED_TRAP            = auto()  # args [suit, toon, trapDamage, trapLevel]
    EVENT_TRIGGERED_TRAP         = auto()  # args [suit, toon, trapDamage, trapLevel]

    EVENT_SUIT_REVIVED           = auto()  # args [suit, revivesLeft, toon]
    EVENT_SUIT_DIED              = auto()  # args [suit, toon, attackType]

    # Called when a toon "dies".
    # If you wish to listen for a toon truly leaving the battle,
    # use EVENT_TOON_LEFT instead.
    EVENT_TOON_DIED              = auto()  # args [toon, suit, attackType]

    # Called when server adjusts everything
    # after battle movie finishes
    EVENT_MOVIE_DONE             = auto()  # no args

    # Called in DistributedBattleBaseAI
    EVENT_TOON_ADDED_TO_BATTLE   = auto()  # args [toon]
    EVENT_SUIT_ADDED_TO_BATTLE   = auto()  # args [suit]

    EVENT_TOONS_DAMAGE_UP        = auto()  # args [toon, rounds]
    EVENT_MARKED_SUIT            = auto()  # args [suit, toon, roundsMarked]

    # Visual Effect events

    EVENT_VISUAL_EFFECT_CREATED  = auto()  # args [avatar, visualEffect, effectId]
    EVENT_VISUAL_EFFECT_COMBINED = auto()  # args [avatar, visualEffect, effectId]
    EVENT_VISUAL_EFFECT_EXPIRED  = auto()  # args [avatar, effectId]

    EVENT_NEXT_ATTACK            = auto()  # no args

    # Move this to the proper category once this is an IntEnum class
    EVENT_SUIT_HEALED_TOON       = auto()  # args [suit, toon, healAmount, attackType]

    # Called when a toon leaves the battle.
    EVENT_TOON_LEFT              = auto()  # args [toon]
    EVENT_SUIT_LEFT              = auto()  # args [suit]

    # Called when a toon unlures a suit.
    EVENT_TOON_UNLURED_SUIT      = auto()  # args [toon, lureEffectUniqueId]

    # Events for creating inserting attacks into the attack order.
    EVENT_CREATE_INSERT_ATTACK   = auto()  # args

    # Called to make Toon attacks change their targeting in the middle of the round.
    # targetOverrideDict = {oldTargetId: newTargetId, ...}
    EVENT_TOON_TARGETING_OVERRIDE = auto()  # args [targetOverrideDict]

    EVENT_CREATE_ENVIRONMENTAL   = auto()  # args [environmentalEnum]
    EVENT_DESTROY_ENVIRONMENTAL  = auto()  # args [environmentalEnum]

    # Updates a toon with an adaptive laff modifier to have new laff when the battle movie ends.
    EVENT_ADAPTIVE_LAFF          = auto()  # args [toon, amount, modifyType]
    """
    END GENERAL EVENTS
    """

    """
    BEGIN MINIBOSS-SPECIFIC EVENTS
    """

    # Lawfice.
    EVENT_HA_LAWFICE_OBJECTION                  = auto()  # args [comboDamage]

    # Litigation team, hardmode CLO.
    EVENT_LT_SPAWN_NATURAL_COGS                 = auto()  # no args
    EVENT_LT_LGATOR_BAYOU_BASH                  = auto()  # no args
    EVENT_LT_LGATOR_BAYOU_BELLOW                = auto()  # no args
    EVENT_LT_STENOG_TRIGGER_COURT_RECORD_DAMAGE = auto()  # args [attack]
    EVENT_LT_STENOG_USE_COURT_RECORD            = auto()  # no args
    EVENT_LT_STENOG_NORMAL_SANCTION             = auto()  # no args
    EVENT_LT_SGOAT_RAGE_ENTER                   = auto()  # no args
    EVENT_LT_SGOAT_RAGE_EXIT                    = auto()  # no args
    EVENT_LT_CASEMAN_BINDINGS_EXPIRED           = auto()  # args [toon]

    # Erfit
    EVENT_ERFIT_GAINS_FROM_THE_SCRAP            = auto()  # no args

    # Rainmaker
    EVENT_RAINMAKE_PRE_TRANSITION               = auto()  # no args
    EVENT_RAINMAKE_WEATHER                      = auto()  # args [weather enum]
    EVENT_RAINMAKE_DEATH_PREVENTED              = auto()  # no args

    # Bellringer
    EVENT_BELLRING_EXPLOSION_HAPPENED           = auto()  # no args
    EVENT_BELLRING_FODDER_IGNORE_PREVENT_DEATH  = auto()  # args [suit]

    # Major Player
    EVENT_MPLAYER_RHYTHM                        = auto()  # args [notesPlayed, totalNotes]
    EVENT_MPLAYER_HWA                           = auto()  # no args
    EVENT_MPLAYER_ADD_STAR_BONUS                = auto()  # args [bonusValue]

    # Plutocrat
    EVENT_PCRAT_WEATHER                         = auto()  # args [weather enum]

    # Pacesetter
    EVENT_PACESETTER_BAD_LEVEL_USED             = auto()  # args [attack]
    EVENT_PACESETTER_RANDOMIZE_LEVELS           = auto()  # args [track, level]
    EVENT_PACESETTER_RANDOMIZE_GAG_ORDER        = auto()  # no args
    EVENT_PACESETTER_FAILED                     = auto()  # no args

    EVENT_FTF_RUSHJOB_TRACKER_CREATED           = auto()  # no args

    EVENT_HROLL_QUESTION_WRONG                  = auto()  # args [toon]
    EVENT_HROLL_KILL_CLONE                      = auto()  # args [cloneId]
    EVENT_HROLL_ACTIVATE_CLONE                  = auto()  # args [callback, attackOrder]
    EVENT_HROLL_FORCE_MAX_LAFF_MOVIE            = auto()  # no args

    """
    END MINIBOSS-SPECIFIC EVENTS
    """


# Handy dandy alias
BEG = BattleEventEnum
