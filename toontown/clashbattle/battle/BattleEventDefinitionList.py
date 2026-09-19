from toontown.battle.BattleEventGlobals import BEG
from toontown.battle.BattleEventDefinitionClasses import *
from toontown.battle.BattleGlobals import BattleStateEnum
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from .environmental.base.EnvironmentalEnum import ENV_ENUM
from toontown.battle.statuses.StatusEffectEnums import SEE


EventDefs = BattleEventDefinitions({
    ### Battle Debug Event Definitions ###

    # Contains events that can be listened to for debugging purposes.
    # These events are not added to listeners in any production code.

    DebugGagAccuracyEventDefinition("BattleCalculatorAI"): (
        BattleEvent(
            "update_accuracy_gui",
            listensTo=BEG.EVENT_TOON_ATTACK_ORDER,
            callback=SelfCallback('updateAccuracyGUI', EventArg.ZERO)
        ),
        BattleEvent(
            "delete_single_accuracy_gui",
            listensTo=BEG.EVENT_TOON_LEFT,
            callback=SelfCallback('removeAccuracyGUI', EventArg.ZERO)
        ),
        BattleEvent(
            "delete_all_accuracy_guis",
            listensTo=BEG.EVENT_BATTLE_END,
            callback=SelfCallback('cleanupAllAccuracyGUIs')
        )
    ),

    ### Battle Calculator Event Definitions ###

    # Contains general events which can occur
    # in any battle and don't rely on any status effect's existence.
    # This allows for better usage of the battle listener
    # as a medium between the battle calculator and all other
    # battle objects.

    BattleCalculatorEventDefinition("BattleCalculatorAI"): (
        BattleEvent(
            "create_insert_attack",
            listensTo=BEG.EVENT_CREATE_INSERT_ATTACK,
            callback=SelfCallback(
                "createAndInsertAttack",
                attackType=EventArg.ZERO,
                attackKwargs=EventArg.ONE,
                insertKwargs=EventArg.TWO
            )
        ),
        BattleEvent(
            "create_environmental",
            listensTo=BEG.EVENT_CREATE_ENVIRONMENTAL,
            callback=SelfCallback(
                'createEnvironmental',
                environmentalType=EventArg.ZERO,
            )
        ),
        BattleEvent(
            'remove_environmental',
            listensTo=BEG.EVENT_DESTROY_ENVIRONMENTAL,
            callback=SelfCallback('removeEnvironmental', EventArg.ZERO),
        )
    ),


    ### Attack Event Definitions ###

    # Event to force toon attacks to change targets away from one suit to another
    AttackEventDefinition("ToonAttackAI"): (
        BattleEvent(
            "update_target",
            listensTo=BEG.EVENT_TOON_TARGETING_OVERRIDE,
            callback=SelfCallback('attemptTargetingOverride', EventArg.ZERO)
        )
    ),


    ### Suit Event Definitions ###

    ## TTC'S DERRICKMAN ##
    # The Derrickman's cheat is fairly simple.
    # - At the start of the event attack order, the Derrickman will call
    #   his Refinement cheat, if any suit is hurt,
    #   while on a fairly lengthy round cycle.
    SuitEventDefinition('derrman'): BattleEventCreateAndInsertAttack(
        attackType=AttackEnum.REFINEMENT,
        conditional=WantAllConditionalGroup(
            ConditionalSomeSuitIsHurt(healthCap=1.1),
            ConditionalRoundCycle(3, 1),
        ),
        attackKwargs=dict(invoker=EventArg.SELF, unlure=True),
        insertKwargs=dict(mode="beginning"),
    ),

    # BB'S LAND ACQ ##
    # Land Acq listens for the attack order created event.
    # - When this attack order is created, he'll go ahead and sneak an Ink Drain in.
    #   This will only happen on a fairly lengthy round cycle.
    SuitEventDefinition('dlao'): BattleEventCreateAndInsertAttack(
        attackType=AttackEnum.INK_DRAIN,
        conditional=ConditionalRoundCycle(4, 2),
        attackKwargs=dict(invoker=EventArg.SELF, unlure=True),
        insertKwargs=dict(mode="beginning"),
    ),

    ### THE DIRECTORS ###
    # region

    ## DERRICKHAND ##
    # Derrickhand has an improved healing cheat over the Derrickman.
    # - When the attack order is created, he'll sneak in an improved Refinement,
    #   given that there is some suit that isn't at 1.25x overheal.
    SuitEventDefinition('derrhand'): BattleEventCreateAndInsertAttack(
        attackType=AttackEnum.REFINEMENT_DIRECTORS,
        conditional=WantAllConditionalGroup(
            ConditionalSomeSuitIsHurt(healthCap=1.25),
            ConditionalRoundCycle(4, 0),
        ),
        attackKwargs=dict(invoker=EventArg.SELF, unlure=True),
        insertKwargs=dict(mode="beginning"),
    ),

    ## DIRECTOR OF LAND DEVELOPMENT ##
    # The DOLD has a fairly similar ink drain status effect like
    # the DLAO.
    # - When this attack order is created, he'll go ahead and sneak an Ink Drain in.
    #   This will only happen on a fairly lengthy round cycle.
    SuitEventDefinition('dold'): BattleEventCreateAndInsertAttack(
        attackType=AttackEnum.INK_DRAIN_DIRECTORS,
        conditional=ConditionalRoundCycle(4, 2),
        attackKwargs=dict(invoker=EventArg.SELF, unlure=True),
        insertKwargs=dict(mode="beginning"),
    ),

    ## DIRECTOR OF PUBLIC AFFAIRS ##
    # The DOPA builds up speed for several hours.
    # - At the very start of the battle, the DOPA will inflict overwhelming authority at
    #   the absolute start of the turn.
    # - At the start of the suit attack order on a conditional round cycle, he'll
    #   call for Disruptive Advertisement.
    #   This effect applies a HitAvatarStatusEffect to his suit profile.
    SuitEventDefinition('dopa'): (
        BattleEventCreateAndInsertAttack(
            "dopa_disruptive_advertisement",
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            attackType=AttackEnum.DISRUPTIVE_ADVERTISEMENT,
            conditional=ConditionalRoundCycle(4, 1),
            attackKwargs=dict(invoker=EventArg.SELF, unlure=True),
            insertKwargs=dict(mode="end"),
        ),
        BattleEventCreateAndInsertAttack(
            "dopa_overwhelming_authority",
            attackType=AttackEnum.OVERWHELMING_AUTHORITY,
            conditional=ConditionalRoundCheck(1),
            attackKwargs=dict(invoker=EventArg.SELF, unlure=True),
            insertKwargs=dict(mode="beginning"),
        ),
    ),
    # endregion

    ### FACILITY MINIBOSSES ###
    # region

    ## FACTORY FOREMAN ##
    # The Foreman has Workers Comp, which generously applies after a suit Is Murdered.
    # - At the start of the event attack order, he'll insert a worker's comp attack
    #   if a suit hath died during the turn.
    #   From there, the attack will heal him and boost his damage x1.15 for each suit killed.
    SuitEventDefinition('foreman'): BattleEventCreateAndInsertAttack(
        attackType=AttackEnum.WORKERS_COMP,
        listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
        conditional=ConditionalEventWasSent(BEG.EVENT_SUIT_DIED),
        attackKwargs=dict(invoker=EventArg.SELF, unlure=True),
        insertKwargs=dict(adjust=False),
    ),
    ## MINT SUPERVISOR ##
    # Mint Supervisor doesn't need an event definition, as it is handled by the SUPERVISOR_INSURED status effect.

    ## HEAD ATTORNEY ##
    # The Head Attorney rejects the existence of combo damage.
    # - When a toon deals combo damage to the Head Attorney, the HA will object,
    #   and call an Objection attack, while calling the next event.
    # - The objection will be sustained under an 85% chance,
    #   otherwise will be overruled for a 15% chance,
    #   in which he will be very disappointed and be sad.
    SuitEventDefinition('clerk'): (
        BattleEvent(
            listensTo=BEG.EVENT_TOON_COMBO_DAMAGE,
            callback=(
                BattleCalculatorCallback(
                    'createAndInsertAttack',
                    attackType=AttackEnum.OBJECTION,
                    attackKwargs=dict(invoker=EventArg.SELF, unlure=True),
                    insertKwargs=dict(respectPreviousAdditions=True),
                ),
                BattleListenerCallback(
                    funcName="sendEvent",
                    eventId=BEG.EVENT_HA_LAWFICE_OBJECTION,
                    eventArgs=[EventArg.TWO, EventArg.SELF],
                )
            ),
            conditional=ConditionalReferenceEquality(EventArg.SELF, EventArg.ZERO)
        ),
        BattleEventCreateAndInsertAttack(
            attackType=AttackEnum.OBJECTION_SUSTAINED,
            listensTo=BEG.EVENT_HA_LAWFICE_OBJECTION,
            attackKwargs=dict(invoker=EventArg.SELF, unlure=True, extraArgs=[EventArg.ZERO]),
            insertKwargs=dict(respectPreviousAdditions=True),
            conditional=ConditionalRandomRoll(0.85),
            failureCallback=BattleCalculatorCallback(
                "createAndInsertAttack",
                attackType=AttackEnum.OBJECTION_OVERRULED,
                attackKwargs=dict(invoker=EventArg.SELF, unlure=True),
                insertKwargs=dict(respectPreviousAdditions=True),
            ),
        )
    ),

    ## CLUB PRESIDENT ##
    # The Club President has tips to give out.
    # - At the start of the suit attacks, he'll do an Extra Tip attack if there is a lured autocaddie.
    SuitEventDefinition('clubpres'): BattleEventCreateAndInsertAttack(
        attackType=AttackEnum.EXTRA_TIP,
        listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
        conditional=ConditionalSuitTypeLured(
            BattleCalculatorCallback("allSuitsExceptMe", exceptSuit=EventArg.SELF),
        ),
        attackKwargs=dict(invoker=EventArg.SELF, unlure=True, extraArgs=[0.20, False, 1.1]),
        insertKwargs=dict(adjust=False),
    ),
    # endregion

    ### STREET MINIBOSSES ###
    # region

    ## BELLRINGER ##
    # At the end of each turn, Bellringer uses Healing Bell.
    # If there are any Suits in battle with negative status conditions, those status conditions are healed
    # If there are other Suits in battle but they don't have negative status effects, they're healed by 33% of their max HP instead (up to 33% overheal)
    # If there aren't other Suits in battle, Bellringer will heal himself by 20% of his max HP and remove his negative status effects.
    SuitEventDefinition('bellring'): BattleEventCreateAndInsertAttack(
        'bellringer_healing_bell',
        attackType=AttackEnum.HEALING_BELL,
        listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
        attackKwargs=dict(invoker=EventArg.SELF, extraArgs=[0]),
        insertKwargs=dict(mode="end"),
    ),

    ## FIRESTARTER ##
    # The Firestarter spams high-damage attacks because it's funny.
    # - At the end of every turn, he'll give all other cogs the Backburner status effect.
    # - Every few turns, he'll use a strong general attack that deals 20 damage to everything.
    SuitEventDefinition('fires'): (
        BattleEventCreateAndInsertAttack(
            'firestarter_raise_barnburner',
            attackType=AttackEnum.BARNBURNER,
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            conditional=WantAllConditionalGroup(
                ConditionalRoundCycle(3, 0),
                ConditionalSelfIsAlive(),
            ),
            attackKwargs=dict(invoker=EventArg.SELF, extraArgs=[16])  # The extraArgs here is Barnburner's damage before exe bonus
        ),
    ),

    ## TREEKILLER ##
    SuitEventDefinition('treek'): (
        BattleEventCreateAndInsertAttack(
            'treek_peeling_the_bark',
            attackType=AttackEnum.PEELING_THE_BARK,
            conditional=ConditionalRoundCycle(2, 1),
            attackKwargs=dict(invoker=EventArg.SELF, unlure=True),
            insertKwargs=dict(mode="beginning"),
        ),
        BattleEventCreateAndInsertAttack(
            'treek_woodchipper',
            attackType=AttackEnum.WOODCHIPPER,
            conditional=ConditionalRoundCycle(2, 0),
            attackKwargs=dict(invoker=EventArg.SELF, unlure=True),
            insertKwargs=dict(mode="beginning"),
        ),
    ),
    # endregion
    
    ### TUTORIAL EVENTS ###
    # region
    ## Desk Jockey ##
    #   Lights On Initiative
    # - Does a cheat to spawn cogs on certain rounds (for extraArgs: [amount, level]).
    SuitEventDefinition('djockey'): (
        BattleEventCreateAndInsertAttack(
            attackType=AttackEnum.LIGHTS_ON,
            conditional=ConditionalRoundCheck(2),
            attackKwargs=dict(invoker=EventArg.SELF, unlure=False, extraArgs=[1, 1]),
            insertKwargs=dict(mode="end"),
        ),
        BattleEventCreateAndInsertAttack(
            attackType=AttackEnum.LIGHTS_ON,
            conditional=ConditionalRoundCheck(6),
            attackKwargs=dict(invoker=EventArg.SELF, unlure=False, extraArgs=[3, 2]),
            insertKwargs=dict(mode="end"),
        ),
    ),
    # endregion

    ### Generic Status Effect Definitions ###

    ## BASE STATUS EFFECT ##
    # The generic status effect all status effects inherit from.
    # - Listen for the end of the round, then decrement the timer.
    StatusEffectEventDefinition(SEE.EFFECT_BASE): BaseStatusEffectEvents,

    # A generic status effect which each suit uses by default.
    # This effect has the generic functionality that any suit in the game
    # needs: creating and inserting a randomly generated suit attack into
    # the attack order, but this can be easily overriden by inheritors.
    # This effect also handles some extra field-setting that is required
    # when suits revive to properly show updated HP values.
    StatusEffectEventDefinition(SEE.EFFECT_SUIT): (
        BattleEvent(
            "suit_generate_suit_attack",
            listensTo=BEG.EVENT_SUIT_ATTACK_ORDER,
            callback=SelfCallback('generateAttack'),
            conditional=ConditionalValueEquality(SelfCallback('getAvatarBattleState'), BattleStateEnum.ACTIVE)
        ),
        BattleEvent(
            'suit_handle_suit_revived',
            listensTo=BEG.EVENT_SUIT_REVIVED,
            callback=SelfCallback('handleSuitRevived', EventArg.ZERO),
        ),
        BattleEvent(
            'suit_handle_track_over',
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=SelfCallback('handleReviveDamageInfo'),
        )
    ),

    ### Generic Environmental Definitions ###

    # The generic environmental which all other environmentals inherit from.
    EnvironmentalEventDefinition(ENV_ENUM.BASE): BaseEnvironmentalEvents,
    EnvironmentalEventDefinition(ENV_ENUM.HECK_YOUR_GAG_ORDER): [
        BattleEventEndRound(
            "gag_order_hecked",
            callback=SelfCallback("handleTurnEnd"),
        ),
        BattleEvent(
            "gag_order_reset",
            listensTo=BEG.EVENT_BATTLE_END,
            callback=SelfCallback('handleBattleEnd'),
        ),
    ],

    ## TIMERS ##
    # A timer status effect, which minibosses can inherit from to calculate abilities.
    # - Listen for the beginning of the round to increment our timer.
    # - At the end of the round, reset our rounds list.
    StatusEffectEventDefinition(SEE.DEFINITION_ROUND_TIMER): (
        BattleEventBeginRound(
            "round_timer_increment",
            callback=SelfCallback("incrementRoundTimer", amount=1),
        ),
        BattleEventEndRound(
            "round_timer_reset_rounds_list",
            callback=SelfCallback("resetRoundsList"),
        ),
    ),

    # A multi-timer status effect, for handling several round-based timers at once.
    # More complicated minibosses can use this. (Litigator's status effect is one.)
    # - Listen for the beginning of the round to increment our timers.
    # - At the end of the round, reset our rounds lists.
    StatusEffectEventDefinition(SEE.DEFINITION_MULTI_TIMER): (
        BattleEventBeginRound(
            "round_timer_increment",
            callback=SelfCallback("incrementRoundTimers", amount=1),
        ),
        BattleEventEndRound(
            "round_timer_reset_rounds_list",
            callback=SelfCallback("resetRounds"),
        ),
    ),

    ## DAMAGE LISTENER ##
    # Listens to all damage dealt in a battle.
    # - Listen for any damage dealt. Then, increment the damage dealt against that avatar.
    # - At the end of the round, reset our damage dicts.
    StatusEffectEventDefinition(SEE.DEFINITION_DAMAGE_LISTENER): (
        BattleEvent(
            callback = SelfCallback('addDamage', EventArg.ZERO, EventArg.TWO),
            listensTo = (BEG.EVENT_TOON_DAMAGE,
                         BEG.EVENT_TOON_KNOCKBACK_DAMAGE,
                         BEG.EVENT_TOON_COMBO_DAMAGE),
        ),
        BattleEvent(
            callback = SelfCallback('addDamage', EventArg.ONE, EventArg.TWO),
            listensTo = BEG.EVENT_SUIT_DAMAGE,
        ),
        BattleEventEndRound(
            callback = SelfCallback('resetDamage'),
        ),
    ),

    # An HP-Gatekeeper definition. Keeps and handles the HP Gates.
    # A Status Effect that has this definition inherited will be able to
    # have specific methods defined that fire when the Suit hits different
    # levels of HP.
    StatusEffectEventDefinition(SEE.DEFINITION_HP_GATEKEEPER): BattleEvent(
        "hp_gatekeeper_check_gates",
        listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
        callback=SelfCallback("fireGates"),
    ),

    # Damage Absorb status effect.
    # - Listen for when a Toon deals damage.
    # - Listen for when a Suit deals damage.
    # - Listen for when the Toons are done attacking.
    # - Listen for the beginning of the round.
    # Note: toon_dealt_damage calls incrementSuitDamageDealt, as the Suit is the one taking the damage.
    # The same applies for suit_dealt_damage and incrementToonDamageDealt
    StatusEffectEventDefinition(SEE.DEFINITION_DAMAGE_ABSORB): (
        BattleEvent(
            "damage_absorb_toon_dealt_damage",
            listensTo=(BEG.EVENT_TOON_DAMAGE, BEG.EVENT_TOON_COMBO_DAMAGE),
            callback=SelfCallback(
                "incrementSuitDamageDealt", amount=EventArg.TWO, suit=EventArg.ZERO, track=EventArg.THREE
            )
        ),
        BattleEvent(
            "damage_absorb_suit_dealt_damage",
            listensTo=BEG.EVENT_SUIT_DAMAGE,
            callback=SelfCallback("incrementToonDamageDealt", amount=EventArg.TWO, toon=EventArg.ONE),
        ),
        BattleEvent(
            "damage_absorb_end_track",
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=SelfCallback("handleTrackOver"),
        ),
        BattleEvent(
            "damage_absorb_begin_round",
            listensTo=BEG.EVENT_BEGIN_ROUND,
            callback=SelfCallback("handleBeginRound"),
        ),
    ),

    StatusEffectEventDefinition(SEE.DEFINITION_ROUNDS_MODIFIER): (
        BattleEvent(
            "rounds_modifier_handle_effect_rounds",
            listensTo=(BEG.EVENT_STATUS_EFFECT_CREATED, BEG.EVENT_STATUS_EFFECT_COMBINED),
            callback=SelfCallback('handleEffectRounds', effect=EventArg.ONE, avatar=EventArg.ZERO),
        ),
        BattleEvent(
            "rounds_modifier_handle_suit_lured",
            listensTo=(BEG.EVENT_LURED_SUIT, BEG.EVENT_RELURED_SUIT),
            callback=SelfCallback("handleSuitLured", target=EventArg.ZERO, lureEffect=EventArg.THREE),
        ),
        BattleEvent(
            "rounds_modifier_handle_suit_soaked",
            listensTo=(BEG.EVENT_SOAKED_SUIT, BEG.EVENT_RESOAKED_SUIT),
            callback=SelfCallback(
                "handleSuitSoaked", target=EventArg.ZERO, soakEffect=EventArg.THREE, squirtAttack=EventArg.FOUR
            ),
        ),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_GENERIC_EXTRA_ATTACKS): (
        BattleEventNormalAttacksOver(
            "generic_extra_attacks",
            callback=SelfCallback("addAllExtraAttacks"),
        ),
    ),
    # endregion

    ## TOON STATUS EFFECTS ###
    #region
    # A section dedicated to all status effects that get applied to toons.

    # Toon unite cooldown.
    # Decrement is set to movie done, which is called at the very end of the current round,
    # When all battle movies are finished.
    StatusEffectEventDefinition(SEE.EFFECT_UNITE_COOLDOWN): BattleEvent(
        "status_effect_decrement",
        listensTo=BEG.EVENT_MOVIE_DONE,
        callback=DecrementCallback(),
    ),

    # Deep Freeze, which moves some
    # Toon's attack to the end of the turn.
    StatusEffectEventDefinition(SEE.EFFECT_DEEP_FREEZE): (
        BattleEventEndRound(
            "deep_freeze_reset",
            callback=SelfCallback("reset"),
        ),
        BattleEvent(
            "deep_freeze_shift",
            listensTo=BEG.EVENT_ATTACK_ORDER,
            callback=SelfCallback('shiftAllToonMoves', attackOrder=EventArg.ZERO),
        ),
        BattleEvent(
            "deep_freeze_on_movie_done",
            listensTo=BEG.EVENT_MOVIE_DONE,
            callback=SelfCallback('onMovieDone')
        )
    ),
    
    # Toon damage up effect
    StatusEffectEventDefinition(SEE.EFFECT_TOON_DAMAGE_UP): (
        BattleEvent(
            'toon_damage_boost_send_event',
            listensTo=BEG.EVENT_TOON_USED_GAG,
            callback=SelfCallback('checkSendEvent', EventArg.ZERO),
        ),
    ),
    #endregion

    ### SUIT STATUS EFFECTS ###
    # region
    # A section dedicated to all status effects that get applies to suits.

    # A simple effect to apply HoT on suits.
    # - After normal attacks are over, apply healing to the suit.
    StatusEffectEventDefinition(SEE.DEFINITION_SUIT_HEAL_OVER_TIME): BattleEventNormalAttacksOver(
        "suit_heal_over_time_apply_heal",
        callback=SelfCallback("applyHeal"),
    ),

    # Lure status effect, created by the lure gag track.
    # - Decrements the Lure round counter by 1 when the suits start attacking.
    #   This is so that:
    #   - Toons will be able to attack and deal combo damage the turn that lure ends.
    #   - A cog can unlure and attack on the turn that lure ends.
    # - Listens for the end of the toon track, and then check to know if
    #   we need to delete ourselves if it was used by a different track this round.
    StatusEffectEventDefinition(SEE.EFFECT_SUIT_LURED): (
        BattleEvent(
            "lure_decrement",
            listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
            callback=DecrementCallback(),
        ),
        BattleEvent(
            "lure_check_used",
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=SelfCallback("delete"),
            conditional=CustomConditional(SelfCallback, "getUsed"),
        ),
        BattleEvent(
            "lure_set_fresh",
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=SelfCallback("setFresh", fresh=False),
        ),
        BattleEvent(
            "lure_clear_invoker",
            listensTo=BEG.EVENT_TOON_LEFT,
            callback=SelfCallback("removeInvoker", toon=EventArg.ZERO),
        ),
        BattleEvent(
            "lure_attempt_clear_invoker",
            listensTo=BEG.EVENT_TOON_UNLURED_SUIT,
            callback=SelfCallback("removeInvoker", toon=EventArg.ZERO),
            conditional=ConditionalValueEquality(
                SelfCallback("getUniqueId"), EventArg.ONE
            ),
        ),
    ),

    # Trap status effect, created by the trap gag track.
    StatusEffectEventDefinition(SEE.EFFECT_SUIT_TRAPPED): (
        BattleEvent(
            "trap_clear_invoker",
            listensTo=BEG.EVENT_TOON_LEFT,
            callback=SelfCallback("setInvokerId", toonId=0),
            conditional=ConditionalValueEquality(
                SelfCallback("getInvoker"), EventArg.ZERO
            ),
        ),
        BattleEvent(
            "trap_check_used",
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=SelfCallback("delete"),
            conditional=CustomConditional(SelfCallback, "getUsed"),
        ),
    ),

    # Sued status effect, created by the cease and desist ability.
    # - Listen for a Toon to deal damage to specifically this suit, and then refresh our round counter.
    StatusEffectEventDefinition(SEE.EFFECT_SUIT_SUED): BattleEvent(
        "sue_refresh_rounds",
        BEG.EVENT_TOON_DAMAGE,
        callback=SelfCallback("incrementRounds"),
        conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
    ),

    # The Overcharged status effect, given to a Suit that can receive the Overcharge effect.
    # - Check the avatar's HP after every single attack.
    StatusEffectEventDefinition(SEE.EFFECT_OVERCHARGED): BattleEvent(
        "overcharge_check_hp",
        listensTo=BEG.EVENT_NEXT_ATTACK,
        callback=SelfCallback("checkAvHp"),
    ),

    # NERVOUS PACING
    # Causes the Suit to change its position priority given certain conditions.
    StatusEffectEventDefinition(SEE.EFFECT_NERVOUS_PACING): BattleEventEndRound(
        "nervous_pacing_default_behavior",
        callback=SelfCallback("pacing_onRoundEnd")
    ),
    # endregion

    ### TASKLINE MINIBOSS STATUS EFFECTS ###
    # region
    # This section is for all defined status effects for the different
    # taskline minibosses. Most of the listeners here are not tied to
    # any status effects, but rather to the suits themselves.

    ## THE DOPR ##
    # Ambush marketing, used by DOPR.
    # - Listen for the end of the normal round to add an extra attack.
    # - Listen for the end of the round to set the attacks completed to 0.
    StatusEffectEventDefinition(SEE.EFFECT_AMBUSH_MARKETING): (
        BattleEventEndRound(
            "ambush_marketing_clear_attacks",
            callback=SelfCallback("setAttacksCompleted", 0)
        ),
    ),

    ## THE DOPA ##
    # Disruptive advertisement, used by DOPA in the directors fight.
    # - Listens to toon dealing damage, make sure we're the suit that got hit, and then
    #   set our own flag that we got hit.
    # - Override the base status effect decrement to use the normal attacks over event,
    #   so that we can properly add extra attacks to ourselves at the end of the normal round.
    StatusEffectEventDefinition(SEE.EFFECT_DISRUPTIVE_ADVERTISEMENT): (
        BattleEvent(
            "disruptive_advertisement_toon_success",
            listensTo=BEG.EVENT_TOON_DAMAGE,
            callback=SelfCallback("setAvatarHit", 1),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO)
        ),
        BattleEventNormalAttacksOver(
            "disruptive_advertisement_decrement",
            callback=DecrementCallback(),
        ),
    ),

    # Multi level marketing, also used by the DOPA in the directors fight.
    # - Listens for normal attacks to be over, so that we can append all
    #   of our glower powers at the end of the normal turn.
    # - Checks for when the status effect is created or combined, and use that to
    #   again add new attacks. Also make sure that THIS is the status effect that
    #   was created/was combined.
    # - At the end of the round, reset our attacks completed flag to 0,
    #   to ensure we can properly add all extra attacks in weird circumstances.
    StatusEffectEventDefinition(SEE.EFFECT_MULTI_LEVEL_MARKETING): (
        BattleEvent(
            "multi_level_marketing_status_extra_attacks",
            listensTo=(BEG.EVENT_STATUS_EFFECT_CREATED, BEG.EVENT_STATUS_EFFECT_COMBINED),
            callback=SelfCallback("addAllExtraAttacks"),
            conditional=ConditionalReferenceEquality(EventArg.SELF, EventArg.ONE),
        ),
        BattleEventEndRound(
            "multi_level_marketing_clear_attacks",
            callback=SelfCallback("setAttacksCompleted", 0)
        ),
    ),
    # endregion

    ### LITIGATION TEAM STATUS EFFECTS ###
    # region
    # The following status effects are used by specifically the Litigation Team.
    # Each member has several special abilities, with several of them having synergies.

    ## Superclass Status Effect ##
    # This is the parent status effect for all Litigation Team status effects.
    # All of the Litigation Team effects inherit these features.
    # - At the beginning of the round, or after a suit dies, update our litigation members.
    # - After normal attacks are over, check the lure queue.
    # - After normal attacks are over, check our lure resistance.
    StatusEffectEventDefinition(SEE.DEFINITION_LITIGATION_TEAM_MANAGER): (
        BattleEvent(
            'litigation_team_manager_update_lt_members',
            listensTo=(BEG.EVENT_BEGIN_ROUND, BEG.EVENT_SUIT_DIED),
            callback=SelfCallback('updateLitigationMembers'),
        ),
        BattleEventNormalAttacksOver(
            'litigation_team_manager_lure_queue_check',
            callback=SelfCallback('checkLureQueue'),
        ),
        BattleEventNormalAttacksOver(
            'litigation_team_manager_lure_resistance_check',
            callback=SelfCallback('checkApplyLureResistance'),
        ),
    ),

    ## Litigator ##
    # The Litigator's status effect; his primary focus is to apply damage vulnerability,
    # spawn several waves of cogs, and overall be excessively punishing.
    # - Listens for specific damage dealt from a specific toon targeting anybody.
    # - Listens for total damage taken from all toons, and confirm it was dealt to the Suit.
    # - Listen for a round cycle, and use Snap every 3 rounds.
    # - Check if we got soaked, and then apply a weak Snap accordingly.
    # - Wait for normal attacks to end, then after a round cycle apply Bayou Bash.
    # - Listen for Scapegoat to exit rage, and use that to create another Bayou Bash.
    StatusEffectEventDefinition(SEE.EFFECT_LITIGATOR_MANAGER): (
        BattleEvent(
            'litigator_manager_update_toons_damage_dealt',
            listensTo=BEG.EVENT_TOON_DAMAGE,
            callback=SelfCallback('increaseToonsDamageDealt', EventArg.ONE, EventArg.TWO),
        ),
        BattleEvent(
            'litigator_manager_inc_damage_dealt',
            listensTo=(BEG.EVENT_TOON_DAMAGE, BEG.EVENT_TOON_COMBO_DAMAGE, BEG.EVENT_TOON_KNOCKBACK_DAMAGE),
            callback=SelfCallback('increaseDamageTaken', EventArg.TWO),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),
        BattleEvent(
            'litigator_use_bayou_bash_synergy',
            listensTo=BEG.EVENT_LT_SGOAT_RAGE_EXIT,
            callback=SelfCallback('createBayouBashAttack'),
        ),
        BattleEventNormalAttacksOver(
            'litigator_use_snap',
            callback=SelfCallback('createSnapAttack'),
            conditional=ConditionalValueEquality(SelfCallback('doRoundCycleCheck', 0, 3, 0), True),
        ),
        BattleEventNormalAttacksOver(
            'litigator_use_bayou_bash',
            callback=SelfCallback('createBayouBashAttack'),
            conditional=ConditionalValueEquality(SelfCallback('doRoundCycleCheck', 1, 4, 1), True),
        ),
        BattleEvent(
            'litigator_use_weak_snap',
            listensTo=BEG.EVENT_SOAKED_SUIT,
            callback=SelfCallback('createSnapAttack', True, EventArg.ONE),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),
    ),

    ## Stenographer
    # The Stenographer's status effect; her primary focus being to apply several
    # really annoying effects that makes it a pain in the ass to use gags.
    # And a group attack too, to spite ubers.
    # - Listens for a court record damage event, and Murders that toon.
    # - Listen for when a toon deals damage, and increment that internally.
    # - Create a Sanction on a round cycle after normal attacks end.
    # - Same as above, but create court costs.
    # - Listen for legal bindings to expire, and then create a Court Sanction.
    # - Establish Court Record every round after normal attacks end.
    # - Spawn cogs naturally.
    StatusEffectEventDefinition(SEE.EFFECT_STENOGRAPHER_MANAGER): (
        BattleEvent(
            'stenographer_manager_triggered_court_record_damage',
            listensTo=BEG.EVENT_LT_STENOG_TRIGGER_COURT_RECORD_DAMAGE,
            callback=SelfCallback('triggeredCourtRecordDamage', EventArg.ZERO),
        ),
        BattleEvent(
            'stenographer_manager_update_toons_damage_dealt',
            listensTo=BEG.EVENT_TOON_DAMAGE,
            callback=SelfCallback('increaseToonsDamageDealt', EventArg.ONE, EventArg.TWO),
        ),
        BattleEvent(
            'stenographer_use_court_sanction_retaliate',
            listensTo=BEG.EVENT_LT_CASEMAN_BINDINGS_EXPIRED,
            callback=SelfCallback('createCourtSanctionAttack', True, EventArg.ZERO),
        ),
        BattleEventNormalAttacksOver(
            'stenographer_use_court_sanction',
            callback=SelfCallback('createCourtSanctionAttack'),
            conditional=ConditionalValueEquality(SelfCallback('doRoundCycleCheck', 3, 0), True),
        ),
        BattleEventNormalAttacksOver(
            'stenographer_use_court_costs',
            callback=SelfCallback('createCourtCostsAttack'),
            conditional=ConditionalValueEquality(SelfCallback('doRoundCycleCheck', 3, 2), True),
        ),
        BattleEventNormalAttacksOver(
            'stenographer_use_calculating_costs',
            callback=SelfCallback('createCalculatingCostsAttack'),
            conditional=ConditionalValueEquality(SelfCallback('doRoundCycleCheck', 3, 1), True),
        ),
        BattleEventNormalAttacksOver(
            'stenographer_use_court_record',
            callback=SelfCallback('createCourtRecordAttack'),
        ),
        BattleEventEndRound(
            'stenographer_natural_spawn_cogs',
            callback=SelfCallback('checkSpawnNaturalCogs'),
            conditional=ConditionalRoundCycle(2, 1),
        ),
    ),

    # Stenographer court record.
    # Status effect uses base definition as first listener
    # Second listener waits for when a toon uses a gag. When a toon uses a gag of the right level, it will send
    # The given event back to the battle listener.
    # Third listener will delete the status effect when the stenographer dies.
    StatusEffectEventDefinition(SEE.EFFECT_COURT_RECORD): (
        BattleEvent(
            'court_record_send_event',
            listensTo=BEG.EVENT_TOON_USED_GAG,
            callback=SelfCallback('checkSendEvent', EventArg.ZERO),
        ),
        BattleEventSuitDied('court_record_delete', 'stenog'),
    ),

    ## Case Manager ##
    # The Case Manager's status effect; applies Insurance on other cogs,
    # and Legal Bindings onto Toons in general.
    # - Listens for normal attacks to end, and uses Insurance Plan every other round.
    # - Listen for normal attacks to end, and then uses Legal Bindings every few rounds.
    # - Uses Legal Bindings when Stenographer sanctions.
    # - Uses Legal Bindings when Scapegoat exits Rage.
    # - Uses Legal Bindings when Scapegoat enters Rage.
    # - Spawns cogs naturally.
    StatusEffectEventDefinition(SEE.EFFECT_CASE_MANAGER_MANAGER): (
        BattleEvent(
            'caseman_use_legal_bindings_stenog',
            listensTo=BEG.EVENT_LT_STENOG_NORMAL_SANCTION,
            callback=SelfCallback('createLegalBindingsAttack'),
        ),
        BattleEvent(
            'caseman_use_insurance_plan_sgoat',
            listensTo=BEG.EVENT_LT_SGOAT_RAGE_EXIT,
            callback=SelfCallback('createInsurancePlanAttack'),
        ),
        BattleEvent(
            'caseman_use_legal_bindings_sgoat',
            listensTo=BEG.EVENT_LT_SGOAT_RAGE_ENTER,
            callback=SelfCallback('createLegalBindingsAttack')
        ),
        BattleEventNormalAttacksOver(
            'caseman_use_insurance_plan',
            callback=SelfCallback('createInsurancePlanAttack'),
            conditional=ConditionalValueEquality(SelfCallback('doRoundCycleCheck', 2, 1), True),
        ),
        BattleEventNormalAttacksOver(
            'caseman_use_legal_bindings',
            callback=SelfCallback('createLegalBindingsAttack'),
            conditional=ConditionalValueEquality(SelfCallback('doRoundCycleCheck', 3, 2), True)
        ),
        BattleEventEndRound(
            'case_manager_natural_spawn_cogs',
            callback=SelfCallback('checkSpawnNaturalCogs'),
            conditional=ConditionalRoundCycle(2, 1),
        ),
    ),

    # Case manager damage over time (to toon).
    # status effect decrements as normal
    # At the end of normal attacks, the effect will apply its damage to the toon and create a general attack
    # to display it.
    StatusEffectEventDefinition(SEE.EFFECT_CASE_MANAGER_DOT): BattleEventNormalAttacksOver(
        'case_manager_dot_apply_damage',
        callback=SelfCallback('applyDamage'),
    ),

    ## Scapegoat ##
    # Scapegoat's invisible status effect; very angry goat boy,
    # tanky and big damage dealer.
    # Most of Scapegoat's functionality comes in his rage status effect, which is visible.
    StatusEffectEventDefinition(SEE.EFFECT_SCAPEGOAT_MANAGER): BattleEventEndRound(
        'scapegoat_natural_spawn_cogs',
        callback=SelfCallback('checkSpawnNaturalCogs'),
        conditional=ConditionalRoundCycle(2, 1),
    ),

    # Scapegoat's rage status effect.
    # - Listen for when a Toon deals damage.
    # - Listen for general attack damage.
    # - Listen for when we're lured.
    # - Listen for when we're soaked.
    # - Listen for when someone gets sued.
    # - - All of the above is to increase rage.
    # - Listen for when the Toons are done attacking.
    # - Listen for when the round is all over.
    # - Listen for the beginning of the round.
    StatusEffectEventDefinition(SEE.EFFECT_SCAPEGOAT_RAGE): (
        BattleEvent(
            'scapegoat_rage_toon_dealt_damage',
            listensTo=(BEG.EVENT_TOON_DAMAGE, BEG.EVENT_TOON_COMBO_DAMAGE, BEG.EVENT_TOON_KNOCKBACK_DAMAGE),
            callback=SelfCallback('incrementDamageDealt', EventArg.TWO, EventArg.ZERO, EventArg.THREE),
        ),
        BattleEvent(
            'scapegoat_rage_general_attack_damage',
            listensTo=BEG.EVENT_GENERAL_DAMAGE,
            callback=SelfCallback('receiveGeneralAttackDamage', EventArg.TWO),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),
        BattleEvent(
            'scapegoat_rage_suit_lured',
            listensTo=BEG.EVENT_LURED_SUIT,
            callback=SelfCallback('gotLured'),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),
        BattleEvent(
            'scapegoat_rage_suit_sued',
            listensTo=BEG.EVENT_SUED_SUIT,
            callback=SelfCallback('gotSued'),
        ),
        BattleEvent(
            'scapegoat_end_track',
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=SelfCallback('handleTrackOver'),
        ),
        BattleEventNormalAttacksOver(
            'scapegoat_normal_attacks_over',
            callback=SelfCallback('handleRoundOver'),
        ),
        BattleEventBeginRound(
            'scapegoat_begin_round',
            callback=SelfCallback('handleBeginRound'),
        ),
        BattleEvent(
            'scapegoat_rage_suit_soaked',
            listensTo=BEG.EVENT_SOAKED_SUIT,
            callback=SelfCallback('gotSoaked'),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),
    ),

    # Scapegoat's damage down status effect.
    # - Listen for when Scapegoat dies, then cleanup.
    StatusEffectEventDefinition(SEE.EFFECT_SCAPEGOAT_DAMAGE_TAKEN_DOWN): \
        BattleEventSuitDied('scapegoat_damage_taken_down_delete', 'sgoat'),
    # endregion

    ### EVENT STATUS EFFECTS ###
    # region
    # Count Erclaim's listening events.
    # - Check for damage Count's done, and increment laff steal damage.
    # - Try a Scope Creep.
    # - See if we can revive or sacrifice.
    # - Listen for when we skelecogify.
    # - Begin round and cleanup variables.
    # - Listen for calls which force a revive.
    StatusEffectEventDefinition(SEE.EFFECT_COUNT_ERCLAIM): (
        BattleEvent(
            'erclaim_increase_laffsteal_damage',
            listensTo=BEG.EVENT_SUIT_DAMAGE,
            callback=SelfCallback('createLaffStealAttack', EventArg.TWO, EventArg.ONE),
        ),
        BattleEvent(
            'erclaim_scope_creep',
            listensTo=BEG.EVENT_ATTACK_ORDER,
            callback=SelfCallback('attemptScopeCreep'),
            conditional=ConditionalRoundCycle(3, 1),
        ),
        BattleEvent(
            'erclaim_cheat_checks',
            listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
            callback=(
                SelfCallback('checkForRevive'),
                SelfCallback('checkForSacrifice'),
            ),
        ),
        BattleEvent(
            'erclaim_turn_into_skelecog',
            listensTo=BEG.EVENT_SUIT_REVIVED,
            callback=SelfCallback('enterRevive', EventArg.ZERO),
        ),
        BattleEvent(
            'erclaim_force_revive',
            listensTo=(BEG.EVENT_FIRED_SUIT),
            callback=SelfCallback('forceRevive'),
        ),
        BattleEventBeginRound(
            'erclaim_reset_check_variables',
            callback=SelfCallback('beginRound'),
        ),
    ),

    # Count Erfit's listening events.
    # - Every three rounds, commit Hydration Check.
    #   - Water a toon for funsies
    # - When damaging a toon, use Pro-Toon Shake.
    #   - Heals another cog using Erfit's own health.
    # - At the start of the suit attacks, try to initiate some attacks.
    # - On revive, do a special revive.
    StatusEffectEventDefinition(SEE.EFFECT_COUNT_ERFIT): (
        # Unique Revive
        BattleEvent(
            'erfit_special_revive',
            listensTo=BEG.EVENT_SUIT_REVIVED,
            callback=SelfCallback('doSpecialRevive'),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),

        # Hydration Check
        BattleEvent(
            'erfit_use_hydration_check',
            listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
            callback=SelfCallback('createHydrationCheckAttack'),
            conditional=ConditionalRoundCycle(3, 0),
        ),

        # Pro-Toon Shake
        BattleEvent(
            'erfit_increase_shake_damage',
            listensTo=BEG.EVENT_SUIT_DAMAGE,
            callback=SelfCallback('createProToonShake', EventArg.TWO, EventArg.ONE),
        ),

        # Post-Toon Attack Checks
        BattleEvent(
            'erfit_do_cheats',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('doCheats'),
        ),

        # Round Reset
        BattleEventBeginRound(
            'erfit_reset_check_variables',
            callback=SelfCallback('beginRound'),
        ),
    ),

    # Overclocked Foreman status effect.
    StatusEffectEventDefinition(SEE.EFFECT_OVERCLOCKED_FOREMAN): (
        # Attack Order Listener
        BattleEvent(
            'overclocked_foreman_attack_order',
            listensTo=BEG.EVENT_ATTACK_ORDER,
            callback=SelfCallback('onAttackOrder', EventArg.ZERO),
        ),

        # Sound punisher
        BattleEvent(
            'overclocked_foreman_on_end_toon_track',
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=SelfCallback('onEndToonTrack', EventArg.ZERO, EventArg.ONE),
        ),

        # Round start listener
        BattleEventBeginRound(
            'overclocked_foreman_round_start',
            callback=SelfCallback('onRoundStart')
        ),
    ),

    # region Overclocked Find The Family effects
    ## FACTORY FOREMAN ##
    # The Foreman has Workers Comp, which generously applies after a suit Is Murdered.
    # - At the start of the event attack order, he'll insert a worker's comp attack
    #   if a suit hath died during the turn.
    #   From there, the attack will heal him and boost his damage x1.15 for each suit killed.
    StatusEffectEventDefinition(SEE.DEFINITION_OC_FAMILY_S): BattleEventCreateAndInsertAttack(
        attackType=AttackEnum.WORKERS_COMP,
        listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
        conditional=WantAllConditionalGroup(
            ConditionalEventWasSent(BEG.EVENT_SUIT_DIED),
        ),
        attackKwargs=dict(invoker=AvatarGetterCallback(), unlure=True, extraArgs=[-1, 11]),
    ),
    ## MINT SUPERVISOR ##
    # Mint Supervisor doesn't need an event definition, as it is handled by the FTF_SUPERVISOR_INSURED status effect.

    ## HEAD ATTORNEY ##
    # The Head Attorney rejects the existence of combo damage.
    # - When a toon deals combo damage to the Head Attorney, the HA will object,
    #   and call an Objection attack, while calling the next event.
    # - The objection will be sustained under an 85% chance,
    #   otherwise will be overruled for a 15% chance,
    #   in which he will be very disappointed and be sad.
    StatusEffectEventDefinition(SEE.DEFINITION_OC_FAMILY_L): (
        BattleEvent(
            listensTo=BEG.EVENT_TOON_COMBO_DAMAGE,
            callback=(
                BattleCalculatorCallback(
                    'createAndInsertAttack',
                    attackType=AttackEnum.OBJECTION,
                    attackKwargs=dict(invoker=AvatarGetterCallback(), unlure=True),
                    insertKwargs=dict(respectPreviousAdditions=True),
                ),
                BattleListenerCallback(
                    funcName="sendEvent",
                    eventId=BEG.EVENT_HA_LAWFICE_OBJECTION,
                    eventArgs=[EventArg.TWO, AvatarGetterCallback()],
                )
            ),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO)
        ),
        BattleEventCreateAndInsertAttack(
            attackType=AttackEnum.OBJECTION_SUSTAINED,
            listensTo=BEG.EVENT_HA_LAWFICE_OBJECTION,
            attackKwargs=dict(invoker=AvatarGetterCallback(), unlure=True, extraArgs=[EventArg.ZERO]),
            insertKwargs=dict(respectPreviousAdditions=True),
            conditional=WantAllConditionalGroup(
                ConditionalRandomRoll(0.85),
                ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ONE)
            ),
            failureCallback=SelfCallback('handleObjectionFailure', EventArg.ONE),
        )
    ),

    ## CLUB PRESIDENT ##
    # The Club President has tips to give out.
    # - At the start of the suit attacks, he'll do an Extra Tip attack if there is a lured cog.
    StatusEffectEventDefinition(SEE.DEFINITION_OC_FAMILY_C): BattleEventCreateAndInsertAttack(
        'ftf_president_general_extra_tip',
        attackType=AttackEnum.FTF_PRESIDENT_EXTRA_TIP,
        listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
        conditional=ConditionalSuitTypeLured(
            BattleCalculatorCallback("allSuitsExceptMe", exceptSuit=AvatarGetterCallback()),
        ),
        attackKwargs=dict(invoker=AvatarGetterCallback(), unlure=True, extraArgs=[225, True, 10.0]),
        insertKwargs=dict(respectPreviousAdditions=True, priority=-100),
    ),

    ### NUCLEAR ###
    StatusEffectEventDefinition(SEE.EFFECT_FTF_NUCLEAR): (
        BattleEvent(
            'ftf_nuclear_transformation',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('handleNuclearTransformation'),
        ),
        BattleEvent(
            'ftf_nuclear_movieDone',
            listensTo=BEG.EVENT_MOVIE_DONE,
            callback=SelfCallback('handleMovieDone'),
        ),
    ),

    ### Specific FTF manager effects ###
    StatusEffectEventDefinition(SEE.EFFECT_FTF_FOREMAN_CONTRACTOR): BattleEventNormalAttacksOver(
        "ftf_foreman_contractor_attacks_over",
        callback=SelfCallback("handleNormalAttacksOver"),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_FOREMAN_SNIPER): (
        BattleEvent(
            'ftf_foreman_sniper_inflict_snipe',
            listensTo=BEG.EVENT_SUIT_DAMAGE,
            callback=SelfCallback('applySnipe', EventArg.ZERO, EventArg.TWO, EventArg.THREE),
        ),
        BattleEvent(
            'ftf_foreman_sniper_snipe_attack',
            listensTo=BEG.EVENT_NEXT_ATTACK,
            callback=SelfCallback('addSnipeAttack'),
        ),
        BattleEventEndRound('ftf_foreman_sniper_reset', callback=SelfCallback('resetHits'))
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_FOREMAN_EXPLOSIVE): BattleEvent(
        'ftf_foreman_explosive_decrement',
        listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
        callback=DecrementCallback(),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_FOREMAN_BURNING_SMOKED): BattleEventNormalAttacksOver(
        'ftf_foreman_burning_smoked_dot_apply_damage',
        callback=SelfCallback('applyDamage'),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_FTF_SUPERVISOR_FRAUD): BattleEvent(
            'ftf_supervisor_fraud_damage',
            listensTo=BEG.EVENT_SUIT_DAMAGE,
            callback=SelfCallback('suitDealtDamage', EventArg.ONE, EventArg.TWO),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_SUPERVISOR_ABACUS): (
        BattleEventNormalAttacksOver(
            'ftf_supervisor_abacus_normalAttacksOver',
            callback=SelfCallback('handleNormalAttacksOver'),
        ),
        BattleEvent(
            'ftf_supervisor_abacus_hit_cog',
            listensTo=BEG.EVENT_TOON_DAMAGE,
            callback=SelfCallback('handleGagLanded', EventArg.ZERO, EventArg.FIVE),
        ),
        BattleEvent(
            'ftf_supervisor_abacus_lured_cog',
            listensTo=(BEG.EVENT_LURED_SUIT, BEG.EVENT_RELURED_SUIT),
            callback=SelfCallback('handleGagLanded', EventArg.ZERO, EventArg.FIVE),
        ),
        BattleEvent(
            'ftf_supervisor_abacus_trapped_cog',
            listensTo=BEG.EVENT_TRIGGERED_TRAP,
            callback=SelfCallback('handleGagLanded', EventArg.ZERO, EventArg.THREE),
        ),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_SUPERVISOR_CONFUSED): BattleEventNormalAttacksOver(
        'ftf_supervisor_confused_normalAttacksOver',
        callback=SelfCallback('doCheats'),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_SUPERVISOR_ACCOUNTANT): (
        BattleEventNormalAttacksOver(
            'ftf_supervisor_accountant_normalAttacksOver',
            callback=SelfCallback('handleNormalAttacksOver'),
        ),
        BattleEvent(
            'ftf_supervisor_accountant_hit_cog',
            listensTo=BEG.EVENT_TOON_DAMAGE,
            callback=SelfCallback('handleGagLanded', EventArg.ZERO),
        ),
        BattleEvent(
            'ftf_supervisor_accountant_lured_cog',
            listensTo=(BEG.EVENT_LURED_SUIT, BEG.EVENT_RELURED_SUIT),
            callback=SelfCallback('handleGagLanded', EventArg.ZERO),
        ),
        BattleEvent(
            'ftf_supervisor_accountant_trapped_cog',
            listensTo=BEG.EVENT_TRIGGERED_TRAP,
            callback=SelfCallback('handleGagLanded', EventArg.ZERO),
        ),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_FTF_ATTORNEY_SNEAKY): BattleEvent(
        'ftf_attorney_sneaky_attackOrder',
        listensTo=BEG.EVENT_ATTACK_ORDER,
        callback=SelfCallback('doCheats'),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_ATTORNEY_CHRONO): BattleEventNormalAttacksOver(
        'ftf_attorney_chrono_doCheats',
        callback=SelfCallback('doCheats'),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_ATTORNEY_RUSHJOB): BattleEventNormalAttacksOver(
        'ftf_attorney_rushjob_doCheats',
        callback=SelfCallback('doCheats'),
    ),
    EnvironmentalEventDefinition(ENV_ENUM.FTF_GENERAL_RUSHJOB_TRACKER): BattleEvent(
        'ftf_attorney_rushjob_fail',
        listensTo=BEG.EVENT_PACESETTER_FAILED,
        callback=SelfCallback('handleRushJobFail'),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_ATTORNEY_MONOLITH): BattleEventNormalAttacksOver(
        'ftf_attorney_monolith_doCheats',
        callback=SelfCallback('doCheats'),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_ATTORNEY_OMNIPOTENT): BattleEventNormalAttacksOver(
        'ftf_attorney_omnipotent_doCheats',
        callback=SelfCallback('doCheats'),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_FTF_PRESIDENT_MULLIGAN): BattleEventNormalAttacksOver(
        'ftf_president_mulligan_normalAttacksOver',
        callback=SelfCallback('doCheats'),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_PRESIDENT_CHIPFAN): (
        BattleEvent(
            'ftf_president_chipfan_doCheats',
            listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
            callback=SelfCallback('doCheats'),
        ),
        BattleEvent(
            'ftf_president_chipfan_hit_cog',
            listensTo=BEG.EVENT_TOON_DAMAGE,
            callback=SelfCallback('handleGagLanded', EventArg.ZERO, EventArg.THREE),
        ),
        BattleEvent(
            'ftf_president_chipfan_trapped_cog',
            listensTo=BEG.EVENT_TRIGGERED_TRAP,
            callback=SelfCallback('handleGagLanded', EventArg.ZERO, AttackEnum.TOON_TRAP),
        ),
        BattleEvent(
            "ftf_president_chipfan_end_track",
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=SelfCallback("handleTrackOver"),
        ),
        BattleEvent(
            'ftf_president_chipfan_dealt_damage',
            listensTo=BEG.EVENT_SUIT_DAMAGE,
            callback=SelfCallback('suitDealtDamage', EventArg.TWO),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ONE)
        ),
        BattleEventEndRound('ftf_president_chipfan_reset', callback=SelfCallback('resetHits')),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_PRESIDENT_PUZZLING): BattleEvent(
        'ftf_president_puzzling_confuseToon',
        listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
        callback=SelfCallback('confuseToon'),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_PRESIDENT_PUZZLING_CONFUSED): BattleEvent(
        'ftf_president_puzzling_confused_attackOrder',
        listensTo=BEG.EVENT_ATTACK_ORDER,
        callback=SelfCallback('handleRandomization', EventArg.ZERO),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_FTF_PRESIDENT_SHIVERING): (
        BattleEventNormalAttacksOver(
            'ftf_president_shivering_doCheats',
            callback=SelfCallback('doCheats'),
        ),
        BattleEvent(
            'ftf_president_shivering_hit_cog',
            listensTo=BEG.EVENT_TOON_DAMAGE,
            callback=SelfCallback('handleGagLanded', EventArg.ZERO, EventArg.THREE),
        ),
        BattleEvent(
            'ftf_president_shivering_trapped_cog',
            listensTo=BEG.EVENT_TRIGGERED_TRAP,
            callback=SelfCallback('handleGagLanded', EventArg.ZERO, AttackEnum.TOON_TRAP),
        ),
        BattleEvent(
            'ftf_president_shivering_freeze_suits',
            listensTo=BEG.EVENT_STATUS_EFFECT_CREATED,
            callback=SelfCallback('freezeSuit', EventArg.ONE),
            conditional=WantAllConditionalGroup(
                ConditionalMultipleValueEquality(EventArg.TWO, [SEE.EFFECT_SUIT_SOAKED, SEE.EFFECT_SUIT_DRENCHED]),
                ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO)
            )
        ),
        # Shatter cogs are handled by the FTFPresidentShivering environmental
        BattleEventEndRound('ftf_president_shivering_reset', callback=SelfCallback('resetHits')),
    ),
    EnvironmentalEventDefinition(ENV_ENUM.FTF_PRESIDENT_SHIVERING): BattleEvent(
        'ftf_president_shivering_env_suit_died',
        listensTo=BEG.EVENT_SUIT_DIED,
        callback=SelfCallback('attemptShatter', EventArg.ZERO, EventArg.TWO),
        conditional=ConditionalValueEquality(SelfCallback('suitIsUs', EventArg.ZERO), True),
    ),
    EnvironmentalEventDefinition(ENV_ENUM.FTF_PRESIDENT_HIGHSTAKES): (
        BattleEvent(
            'ftf_highstakes_env_attack_order',
            listensTo=BEG.EVENT_ATTACK_ORDER,
            callback=SelfCallback('onAttackOrder', EventArg.ZERO),
        ),
        BattleEvent(
            'ftf_highstakes_env_end_round',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('onRoundEnd'),
        ),
    ),

    # endregion

    # High Roller's status effect.
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_HIGH_ROLLER): (
        BattleEvent(
            name='highroller_suit_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('handleSuitDied', EventArg.ZERO, EventArg.ONE, EventArg.TWO)
        ),
        BattleEvent(
            name='highroller_leveldamage',
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=SelfCallback('handleLevelDamage'),
        ),
        BattleEvent(
            name='highroller_randomgame',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('handleRandomGame'),
            conditional=ConditionalRoundCycle(3, 1),
        ),
        BattleEvent(
            name='highroller_game_finish',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('handleGameFinish'),
            conditional=ConditionalRoundCycle(3, 2),
        ),
        BattleEvent(
            name='highroller_game_wrong',
            listensTo=BEG.EVENT_HROLL_QUESTION_WRONG,
            callback=SelfCallback('handleGameWrong', EventArg.ZERO),
        ),
        BattleEvent(
            name='highroller_clone_spawn',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('handlePhaseTwo')
        ),
        BattleEventEndRound(
            'instance_merc_natural_spawn_cogs',
            callback=SelfCallback('instanceNaturalSpawns'),
        ),

        # point counter shit
        BattleEvent(
            name='highroller_pointcounter_addstatus',
            listensTo=BEG.EVENT_TOON_ADDED_TO_BATTLE,
            callback=SelfCallback('handleToonAdded', EventArg.ZERO)
        ),
        BattleEvent(
            name='highroller_pointcounter_spendpoints',
            listensTo=BEG.EVENT_ATTACK_ORDER,
            callback=SelfCallback('spendPointsOnGags', EventArg.ZERO)
        ),
        BattleEvent(
            name='highroller_pointcounter_roundpoints',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('roundStartPoints'),
            conditional=ConditionalRoundCycle(1, 0)
        ),
    ),

    # Question Cogs base status effect.
    StatusEffectEventDefinition(SEE.EFFECT_QUESTION): (
        BattleEvent(
            name='highroller_question_expire',
            listensTo=BEG.EVENT_TOON_ATTACK_ORDER,
            callback=SelfCallback('checkAnswer', EventArg.ZERO),
        ),
    ),

    # Dice Choice manager.
    DistributedDiceChoiceDefinition('DistributedDiceChoiceAI'): (
        BattleEvent(
            name='dicechoice_enter_battle_state',
            listensTo=BEG.EVENT_BATTLE_STATE,
            callback=SelfCallback('enterBattleState', EventArg.ZERO),
        ),
    ),

    EnvironmentalEventDefinition(ENV_ENUM.ADAPTIVE_LAFF): (
        BattleEvent(
            'highroller_adaptivelaff_request',
            listensTo=BEG.EVENT_ADAPTIVE_LAFF,
            callback=SelfCallback('requestAdaptiveLaff', EventArg.ZERO, EventArg.ONE, EventArg.TWO),
        ),

        BattleEvent(
            'highroller_adaptivelaff_increase',
            listensTo=BEG.EVENT_MOVIE_DONE,
            callback=SelfCallback('updateAdaptiveLaff'),
        ),
    ),

    # Hollywood Star effect for High Roller phase 2.
    StatusEffectEventDefinition(SEE.EFFECT_HOLLYWOOD_STAR): (
        BattleEventEndRound(callback=SelfCallback('onRoundEnd')),
    ),

    # Clone environmental
    EnvironmentalEventDefinition(ENV_ENUM.HIGH_ROLLER_CLONE_HANDLER):  (
        BattleEvent(
            'highroller_env_suit_died',
            listensTo=BEG.EVENT_HROLL_KILL_CLONE,
            callback=SelfCallback('killClone', EventArg.ZERO),
        ),

        # Round-based status effect refreshes
        BattleEvent(
            'highroller_env_clones_join',
            listensTo=BEG.EVENT_SUIT_ADDED_TO_BATTLE,
            callback=SelfCallback('onClonesJoin'),
        ),
        BattleEvent(
            'highroller_env_end_round',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('onRoundEnd'),
        ),

        # Squirt and toonup punisher
        BattleEvent(
            'highroller_env_on_end_toon_track',
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=SelfCallback('onEndToonTrack', EventArg.ZERO, EventArg.ONE),
        ),

        # Attack Order Listener
        BattleEvent(
            'highroller_env_attack_order',
            listensTo=BEG.EVENT_ATTACK_ORDER,
            callback=SelfCallback('onAttackOrder', EventArg.ZERO),
        ),

        # Attack Order Listener
        BattleEvent(
            'highroller_env_on_begin_suit_attacks',
            listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
            callback=SelfCallback('onBeginSuitAttacks'),
        ),
    ),
    # endregion

    ### STREET MERC STATUS EFFECTS ###
    # region
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_DUCK_SHUFFLER): (
        BattleEventNormalAttacksOver(
            'duck_shuffler_roll_slots',
            callback=SelfCallback('rollSlots'),
        ),
        BattleEvent(
            'duck_shuffler_shuffler_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('weDied'),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),
    ),

    ## DEEP DIVER ##
    # Deep Diver alternates between diving and doing a group attack.
    # Deep Diver is untouchable while diving, due to the dive status effect.
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_DEEP_DIVER): (
        BattleEvent(
            'deep_diver_begin_round',
            listensTo=BEG.EVENT_BEGIN_ROUND,
            callback=SelfCallback('handleBeginRound')
        ),
        BattleEvent(
            'deep_diver_handle_abilities',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('handleAbilities')
        ),
        BattleEvent(
            'deep_diver_suit_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('handleSuitDied', EventArg.ZERO)
        ),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_FIRESTARTER): (
        BattleEventNormalAttacksOver(
            'firestarter_apply_backburners',
            callback=(SelfCallback("handleBackburner"), SelfCallback("handleRequestPyromaniac")),
        ),
        BattleEvent(
            'firestarter_suit_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('handleSuitDied', EventArg.ZERO)
        ),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_BACKBURNER): BattleEventNormalAttacksOver(
        'backburner_dot_apply_damage', callback=SelfCallback('applyDamage'),
    ),

    # Treekiller's Damage
    StatusEffectEventDefinition(SEE.EFFECT_WOODCHIPPER): BattleEventNormalAttacksOver(
        'woodchipper_dot_apply_damage', callback=SelfCallback('applyDamage'),
    ),

    # Front Line listening events.
    # - Listen for any updates to suits joining the battle, or the end of the round.
    #   Use this to call an updateReduction check.
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_GATEKEEPER): (
        BattleEvent(
            'front_line_update',
            listensTo=(BEG.EVENT_SUIT_ADDED_TO_BATTLE, BEG.EVENT_END_ROUND, BEG.EVENT_END_TOON_TRACK),
            callback=SelfCallback('addEffectToSuits'),
        ),
        BattleEvent(
            'front_line_normal_attacks_over',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('normalAttacksOver'),
        ),
        BattleEvent(
            'front_line_suit_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('handleSuitDied', EventArg.ZERO)
        ),
    ),

    # Gatekeeper fodder stuff
    StatusEffectEventDefinition(SEE.EFFECT_GATEKEEPER_FODDER_BONUS): (
        BattleEventEndRound(callback=SelfCallback('onRoundEnd')),
    ),

    # Bellringer
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_BELLRINGER): (
        BattleEvent(
            'bellringer_update',
            listensTo=(BEG.EVENT_SUIT_ADDED_TO_BATTLE, BEG.EVENT_END_ROUND, BEG.EVENT_END_TOON_TRACK),
            callback=SelfCallback('addEffectToSuits'),
        ),
        BattleEventBeginRound(callback=SelfCallback('onRoundBegin')),
        BattleEvent(
            'bellringer_explosion_happened',
            listensTo=BEG.EVENT_BELLRING_EXPLOSION_HAPPENED,
            callback=SelfCallback('explosionHappened'),
        ),
    ),
    # Bellringer fodder
    StatusEffectEventDefinition(SEE.EFFECT_BELLRINGER_FODDER_EXPLOSION): (
        BattleEventBeginRound(callback=SelfCallback('onRoundBegin')),
        BattleEvent(
            'bellringer_fodder_explosion_ignore_prevent_death',
            listensTo=BEG.EVENT_BELLRING_FODDER_IGNORE_PREVENT_DEATH,
            callback=SelfCallback('setIgnorePreventDeath', True),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO)  # Cog is us
        ),
    ),

    # Mouthpiece
    # - Listen for any updates to suits joining the battle, or the end of the round.
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_MOUTHPIECE): (
        BattleEvent(
            'mouthpiece_bakery',
            listensTo=(BEG.EVENT_SUIT_ADDED_TO_BATTLE),
            callback=SelfCallback('bakeCookies', EventArg.ZERO)
        ),
        BattleEvent(
            'mouthpiece_suit_died',
            listensTo=(BEG.EVENT_SUIT_DIED),
            callback=SelfCallback('handleSuitDied', EventArg.ZERO)
        ),
        BattleEvent(
            'mpiece_extraAttacks',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('extraAttacks'),
        ),
        BattleEvent(
            'mouthpiece_heartbroken',
            listensTo=(BEG.EVENT_END_TOON_TRACK, BEG.EVENT_NORMAL_ATTACKS_OVER),
            callback=SelfCallback('handleHeartbroken')
        ),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_RED_THREAD): (
        BattleEvent(
            'redthread_damage_listener',
            listensTo=(BEG.EVENT_GENERAL_DAMAGE, BEG.EVENT_TOON_DAMAGE, BEG.EVENT_SUIT_DAMAGE),
            callback=SelfCallback('heardDamage', EventArg.TWO, EventArg.ZERO, EventArg.THREE),
            conditional=ConditionalReferenceInequality(AvatarGetterCallback(), EventArg.ZERO)
        ),
    ),

    # Featherbedder
    # - Listen for any updates to suits joining the battle, or the end of the round.
    #   Use this to also add the silly funny Sleepy Boy effect to the suit.
    # - Listen for any sleepy suits which have taken Sound damage.
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_FEATHERBEDDER): (
        BattleEvent(
            'featherbedder_update',
            listensTo=(BEG.EVENT_SUIT_ADDED_TO_BATTLE, BEG.EVENT_END_ROUND),
            callback=SelfCallback('updateReduction'),
        ),
        BattleEvent(
            'featherbedder_sleepy_hurt',
            listensTo=BEG.EVENT_TOON_DAMAGE,
            callback=SelfCallback('heyFeatherbedderIReallyHateSoundCanYouMakeThemShutUp', EventArg.ZERO),
            conditional=ConditionalValueEquality(EventArg.THREE, AttackEnum.TOON_SOUND)
        ),
        BattleEvent(
            'featherbedder_suit_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('checkSuitDied', EventArg.ZERO),
        ),
        BattleEvent(
            'featherbedder_check_power_nap_boost',
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=SelfCallback('checkPowerNapBoost')
        ),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_PEACEFUL_SLUMBER): BattleEvent(
        "peaceful_slumber_adjust_defense",
        listensTo=BEG.EVENT_END_ROUND,
        callback=SelfCallback('adjustDefense'),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_POWER_NAP): BattleEvent(
        "power_nap_decrement",
        listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
        callback=DecrementCallback(),
    ),
    # endregion

    ### INSTANCE MERC STATUS EFFECTS ###
    # region
    # General Instance Mercs
    # - Some instance mercs will end the fight immediately when they die by killing all other suits in the fight.
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_MERC): (
        BattleEvent(
            'instance_merc_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('attemptEndFight'),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),
    ),

    # Copy of above definition for general use.
    StatusEffectEventDefinition(SEE.EFFECT_END_BATTLE_ON_DEATH): (
        BattleEvent(
            'important_suit_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('attemptEndFight'),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),
    ),

    # The Prethinker.
    # - Constantly listening for various attacks.
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_PRETHINKER): (
        BattleEvent(
            'prethinker_cheats',
            listensTo=BEG.EVENT_ATTACK_ORDER,
            callback=SelfCallback('doCheats', EventArg.ZERO),
        ),
        BattleEvent(
            'prethinker_begin_suit_attacks',
            listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
            callback=(
                SelfCallback('attemptLightsOn'),
                SelfCallback('fireGates')
            ),
        ),
        BattleEvent(
            'prethinker_sound_ended',
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=(
                SelfCallback('checkSoundOver', EventArg.ZERO)
            ),
        ),
        BattleEventEndRound(
            'instance_merc_natural_spawn_cogs',
            callback=SelfCallback('instanceNaturalSpawns'),
            conditional=ConditionalRoundCycle(2, 0),
        ),
        BattleEvent(
            'prethinker_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('weDied'),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),
    ),

    # The Chainsaw Consultant.
    # - Has the status effect handle his cheats after normal attacks.
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_CHAINSAW_CONSULTANT): (
        BattleEvent(
            'chainsaw_cheats',
            listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
            callback=SelfCallback('handleBeginSuitAttacks'),
        ),
        BattleEventEndRound(
            'instance_chainsaw_natural_spawn_cogs',
            callback=(SelfCallback('instanceNaturalSpawns'), SelfCallback('handleEndRound')),
        ),
        BattleEvent(
            'chainsaw_was_hit',
            listensTo=BEG.EVENT_TOON_DAMAGE,
            callback=SelfCallback('handleChainsawHit', EventArg.ONE),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),
        BattleEvent(
            'chainsaw_toon_damage_dealt',
            listensTo=(BEG.EVENT_TOON_DAMAGE, BEG.EVENT_TOON_COMBO_DAMAGE, BEG.EVENT_TOON_KNOCKBACK_DAMAGE),
            callback=SelfCallback('registerToonDamageDealt', EventArg.ZERO, EventArg.TWO, EventArg.THREE),
        ),
        BattleEvent(
            'chainsaw_suit_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('suitDied', EventArg.ZERO, EventArg.TWO),
            conditional=ConditionalReferenceInequality(AvatarGetterCallback(), EventArg.ZERO),
        ),
        BattleEventNormalAttacksOver(
            'chainsaw_normal_attacks_over',
            callback=(SelfCallback('fireGates'), SelfCallback('handleAbilities'), SelfCallback('handleNormalAttacksOver')),
        ),
        BattleEvent(
            'chainsaw_hit_cog',
            listensTo=BEG.EVENT_TOON_DAMAGE,
            callback=SelfCallback('handleGagLanded', EventArg.ZERO, EventArg.ONE, EventArg.THREE),
        ),
        BattleEvent(
            'chainsaw_lured_cog',
            listensTo=(BEG.EVENT_LURED_SUIT, BEG.EVENT_RELURED_SUIT),
            callback=SelfCallback('handleGagLanded', EventArg.ZERO, EventArg.ONE, AttackEnum.TOON_LURE),
        ),
        BattleEvent(
            'chainsaw_trapped_cog',
            listensTo=BEG.EVENT_TRIGGERED_TRAP,
            callback=SelfCallback('handleGagLanded', EventArg.ZERO, EventArg.ONE, AttackEnum.TOON_TRAP),
        ),
        BattleEvent(
            'chainsaw_unlure',
            listensTo=BEG.EVENT_TOON_UNLURED_SUIT,
            callback=SelfCallback('handleChainsawUnlured'),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.TWO)
        ),
        BattleEvent(
            'chainsaw_toon_used_gag',
            listensTo=BEG.EVENT_TOON_USED_GAG,
            callback=SelfCallback('handleToonUsedGag', EventArg.ZERO),
        ),
    ),

    # Spark plug DOT
    StatusEffectEventDefinition(SEE.EFFECT_SPARK_PLUG): BattleEventNormalAttacksOver(
        'spark_plug_apply_damage',
        callback=SelfCallback('applyDamage'),
    ),

    # Chain linked effect
    StatusEffectEventDefinition(SEE.EFFECT_CHAIN_LINKED): BattleEvent(
        'chain_linked_update',
        listensTo=(BEG.EVENT_SUIT_ADDED_TO_BATTLE, BEG.EVENT_END_ROUND, BEG.EVENT_END_TOON_TRACK),
        callback=SelfCallback('updateMultiplier'),
    ),

    # The Pacesetter.
    # - Once the Suit Attack order begins, fire the HP gates.
    #   This gate fire call also ties into generating Pacesetter's various attacks.
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_PACESETTER): (
        BattleEventNormalAttacksOver(
            'pacesetter_change_speed',
            callback=SelfCallback('changeSpeed'),
        ),
        BattleEventEndRound(
            'instance_merc_natural_spawn_cogs',
            callback=SelfCallback('instanceNaturalSpawns'),
        ),
        BattleEvent(
            'pacesetter_rush_job_fail',
            listensTo=BEG.EVENT_PACESETTER_FAILED,
            callback=SelfCallback('handleRushJobFail'),
        ),
        BattleEvent(
            'pacesetter_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('weDied'),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),
        BattleEvent(
            'pacesetter_movie_end',
            listensTo=BEG.EVENT_MOVIE_DONE,
            callback=SelfCallback('onMovieEnd'),
        ),
        BattleEventNormalAttacksOver(
            'pacesetter_randomize_gag_levels',
            callback=SelfCallback('randomizeGagLevels'),
        ),
        BattleEvent(
            'pacesetter_bad_level_used',
            listensTo=BEG.EVENT_PACESETTER_BAD_LEVEL_USED,
            callback=SelfCallback('badGagLevelUsed', EventArg.ZERO)
        ),
        BattleEventNormalAttacksOver(
            'pacesetter_attempt_sync',
            callback=SelfCallback('callContentSync'),
            conditional=ConditionalRoundCycle(4, 1),
        ),
        BattleEventEndRound(
            'pacesetter_end_round',
            callback=SelfCallback('handleEndRound')
        ),
        BattleEvent(
            'pacesetter_toon_attacks',
            listensTo=BEG.EVENT_TOON_ATTACK_ORDER,
            callback=SelfCallback('handleToonAttackOrder', EventArg.ZERO)
        )
    ),

    StatusEffectEventDefinition(SEE.EFFECT_RUSH_JOB): (
        BattleEvent(
            'pacesetter_rush_job',
            listensTo=BEG.EVENT_TOON_DAMAGE,
            callback=SelfCallback('handleDamageTaken', EventArg.FOUR),
            conditional=WantAllConditionalGroup(
                ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
                ConditionalValueEquality(EventArg.THREE, SelfCallback('getTrack')),
            ),
        ),
        BattleEvent(
            'pacesetter_rush_job_trap',
            listensTo=BEG.EVENT_PLACED_TRAP,
            callback=SelfCallback('handleDamageTaken', EventArg.FOUR),
            conditional=WantAllConditionalGroup(
                ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
                ConditionalValueEquality(AttackEnum.TOON_TRAP, SelfCallback('getTrack')),
            ),
        ),
        BattleEvent(
            'pacesetter_rush_job_lure',
            listensTo=BEG.EVENT_LURED_SUIT,
            callback=SelfCallback('handleDamageTaken', EventArg.FOUR),
            conditional=WantAllConditionalGroup(
                ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
                ConditionalValueEquality(AttackEnum.TOON_LURE, SelfCallback('getTrack')),
            ),
        ),
        BattleEvent(
            'status_effect_decrement',
            listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
            callback=DecrementCallback(),
        ),
    ),

    # Pacesetter moving goalposts.
    # Status effect uses base definition as first listener
    # Second listener waits for when a toon uses a gag. When a toon uses a gag of the right track/level, it will send
    # The given event back to the battle listener.
    # Third listener will delete the status effect when the pacesetter dies.
    StatusEffectEventDefinition(SEE.EFFECT_MOVING_GOALPOSTS): (
        BattleEvent(
            'moving_goalposts_send_event',
            listensTo=BEG.EVENT_TOON_USED_GAG,
            callback=SelfCallback('checkSendEvent', EventArg.ZERO),
        ),
        BattleEventSuitDied('moving_goalposts_delete', 'psetter'),
    ),

    EnvironmentalEventDefinition(ENV_ENUM.PACESETTER_GAG_ORDER): BattleEvent(
        'pacesetter_gag_order_update',
        listensTo=BEG.EVENT_PACESETTER_RANDOMIZE_GAG_ORDER,
        callback=SelfCallback('randomizeOrder'),
    ),

    # Multislacker
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_MULTISLACKER): (
        BattleEvent(
            'multislacker_begin_suit_attacks',
            listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
            callback=(
                SelfCallback('checkAvatarHits'),
                SelfCallback('fireGates'),
                SelfCallback('checkOutForLunch'),
            ),
        ),
        BattleEvent(
            'multislacker_suit_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('checkOutForLunch'),
        ),
        BattleEvent(
            'multislacker_avatar_hits',
            listensTo=BEG.EVENT_TOON_DAMAGE,
            callback=SelfCallback('incrementAvatarHits', EventArg.ONE),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),
        BattleEvent(
            'multislacker_reset_lonely',
            listensTo=BEG.EVENT_SUIT_ADDED_TO_BATTLE,
            callback=SelfCallback('resetLoneliness'),
            conditional=ConditionalReferenceInequality(AvatarGetterCallback(), EventArg.ZERO),
        ),
        BattleEventBeginRound(
            'multislacker_begin_round',
            callback=(
                SelfCallback('resetAvatarHits'),
                SelfCallback('resetRoundStartHp')
            )
        ),
        BattleEventNormalAttacksOver(
            'multislacker_attempt_get_friends',
            callback=SelfCallback('attemptSummonFriends')
        ),
    ),

    # Multislacker summons his own version of the Factory Foreman.
    # This is the Worker's Compensation cheat event def for that guy.
    SuitEventDefinition('msfore'): BattleEventCreateAndInsertAttack(
        attackType=AttackEnum.WORKERS_COMP,
        listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
        conditional=WantAllConditionalGroup(
            ConditionalEventWasSent(BEG.EVENT_SUIT_DIED),
            ConditionalValueEquality(SelfCallback('hasStatusEffectOfId', SEE.EFFECT_UNION_BUST), False),
        ),
        attackKwargs=dict(invoker=EventArg.SELF, unlure=True, extraArgs=[-1, 9]),
        insertKwargs=dict(adjust=False),
    ),

    # Focused Defense Status Effect (one of the Multislacker Foreman effects)
    # Takes less damage from the first gag track that hit it each round.
    StatusEffectEventDefinition(SEE.EFFECT_FOCUSED_DEFENSE): (
        BattleEventBeginRound(
            'focused_defense_begin_round',
            callback=SelfCallback('handleBeginRound'),
        ),
        BattleEvent(
            'focused_defense_toon_dealt_damage',
            listensTo=BEG.EVENT_TOON_DAMAGE,
            callback=SelfCallback('checkForDamageDealt', EventArg.ZERO),
        ),
        BattleEvent(
            'focused_defense_end_track',
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=SelfCallback('handleTrackOver'),
        ),
    ),

    # Worker Management Status Effect (one of the Multislacker Foreman effects)
    # Removes certain negative effects from nearby suits at the end of each round.
    StatusEffectEventDefinition(SEE.EFFECT_WORKER_MANAGEMENT): (
        BattleEvent(
            'worker_management_remove_effects',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('cleanseNearbySuits'),
        ),
    ),

    # Union bust Status Effect (one of the Multislacker Foreman effects)
    # Kills all other cogs in the battle at the end of the first round,
    # Giving him a ton of compensation.
    StatusEffectEventDefinition(SEE.EFFECT_UNION_BUST): (
        BattleEvent(
            'union_bust_decrement',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=DecrementCallback(),
        ),
    ),

    # Rainmaker
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_RAINMAKER): (
        BattleEvent(
            'rainmaker_fire_gates',
            listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
            callback=(
                SelfCallback('fireGates'),
            ),
        ),
        BattleEvent(
            'rainmaker_weather_control',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=(
                SelfCallback('weatherControl'),
            ),
        ),
        BattleEventEndRound(
            'instance_merc_natural_spawn_cogs',
            callback=SelfCallback('instanceNaturalSpawns'),
        ),
        BattleEvent(
            'rainmaker_check_final_cooldown',
            listensTo=BEG.EVENT_MOVIE_DONE,
            callback=SelfCallback('checkApplyFinalRewardCooldown')
        ),
    ),
    EnvironmentalEventDefinition(ENV_ENUM.RAINMAKER_WEATHER): (
        BattleEvent(
            'rainmaker_env_weather_control',
            listensTo=BEG.EVENT_RAINMAKE_WEATHER,
            callback=SelfCallback('setWeather', EventArg.ZERO),
        ),
        BattleEvent(
            'rainmaker_env_drenched_expire',
            listensTo=BEG.EVENT_STATUS_EFFECT_EXPIRED,
            callback=SelfCallback('handleDrenchedExpire', EventArg.ZERO),
            conditional=ConditionalValueEquality(EventArg.ONE, SEE.EFFECT_SUIT_DRENCHED),
        ),
        BattleEvent(
            'rainmaker_env_check_toon_monsoon',
            listensTo=BEG.EVENT_MOVIE_DONE,
            callback=SelfCallback('checkToonMonsoonEffect'),
        ),
    ),

    # Monsoon status effect
    # - Listen for suit attack order; attacks will be shuffled only when we're in overclocked.
    StatusEffectEventDefinition(SEE.EFFECT_OIL_RAIN_HOT): (
        BattleEvent(
            'rainmaker_oil_rain_hot',
            BEG.EVENT_RAINMAKE_PRE_TRANSITION,
            callback=SelfCallback('applyHeal'),
        ),
        BattleEvent(
            'rainmaker_oil_rain_hot_death_prevented',
            BEG.EVENT_RAINMAKE_DEATH_PREVENTED,
            callback=SelfCallback('rainmakerDeathPrevented')
        ),
    ),
    StatusEffectEventDefinition(SEE.EFFECT_OIL_RAIN_DOT): (
        BattleEvent(
            'rainmaker_oil_rain_dot_end',
            BEG.EVENT_RAINMAKE_PRE_TRANSITION,
            callback=SelfCallback('applyDamage'),
        ),
        BattleEventNormalAttacksOver(
            'rainmaker_oil_rain_dot',
            callback=SelfCallback('applyDamage'),
        ),
        BattleEvent(
            'rainmaker_oil_rain_dot_death_prevented',
            BEG.EVENT_RAINMAKE_DEATH_PREVENTED,
            callback=SelfCallback('rainmakerDeathPrevented')
        ),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_STORM_CELL): BattleEvent(
        'rainmaker_storm_cell_reduce_rounds',
        BEG.EVENT_TOON_DAMAGE,
        callback=DecrementCallback(),
        conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
    ),

    # Major Player
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_MAJOR_PLAYER): (
        BattleEvent(
            name='majorplayer_staroftheshow',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('handleStarOfTheShow'),
            conditional=ConditionalRoundCycle(2, 0),
        ),
        BattleEvent(
            name='majorplayer_revivestaroftheshow',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('handleRevivedStarOfTheShow'),
        ),
        BattleEvent(
            name='majorplayer_dancepartners',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('handleDancePartners'),
            conditional=ConditionalRoundCycle(5, 1),
        ),
        BattleEvent(
            name='majorplayer_guestverse',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('handleGuestVerse'),
            conditional=ConditionalRoundCycle(2, 1),
        ),
        BattleEvent(
            name='majorplayer_reservebuffs',
            listensTo=BEG.EVENT_END_ROUND,
            callback=SelfCallback('applyBuffs'),
        ),
        BattleEvent(
            name='majorplayer_round_begin',
            listensTo=BEG.EVENT_BEGIN_ROUND,
            callback=SelfCallback('handleBeginRound'),
        ),
        BattleEvent(
            name="majorplayer_suit_died",
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('suitDied', EventArg.ZERO),
        ),
        BattleEvent(
            name='majorplayer_add_star_toon_buff',
            listensTo=BEG.EVENT_MPLAYER_ADD_STAR_BONUS,
            callback=SelfCallback('addToonStarBonus', EventArg.ZERO)
        ),
        BattleEvent(
            name='majorplayer_show_star_toon_buff',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('checkToonStarBonus')
        ),
        BattleEvent(
            'majorplayer_rhythm_ended',
            listensTo=BEG.EVENT_MPLAYER_RHYTHM,
            callback=SelfCallback('handleRhythm', EventArg.ZERO, EventArg.ONE),
        ),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_STAR_OF_THE_SHOW): (
        BattleEventEndRound(callback=SelfCallback('onRoundEnd')),
        BattleEvent(
            'sots_suit_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('weDied'),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO)
        )
    ),

    StatusEffectEventDefinition(SEE.EFFECT_LAST_TAP): (
        BattleEventEndRound(callback=SelfCallback('onRoundEnd')),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_GUEST_VERSE): (
        BattleEvent(
            'guestverse_toon_hit',
            listensTo=BEG.EVENT_SUIT_DAMAGE,
            callback=SelfCallback('suitHit', EventArg.ZERO, EventArg.ONE),
        ),
        BattleEvent(
            'guestverse_followup_attack',
            listensTo=BEG.EVENT_NEXT_ATTACK,
            callback=SelfCallback('timeForVirus'),
        )
    ),

    StatusEffectEventDefinition(SEE.EFFECT_DANCE_PARTNER): (
        BattleEvent(
            name='dancepartner_onAvRemove',
            listensTo=(BEG.EVENT_TOON_LEFT, BEG.EVENT_SUIT_LEFT, BEG.EVENT_SUIT_DIED),
            callback=SelfCallback('handleAvatarDied', EventArg.ZERO),
        ),
    ),

    EnvironmentalEventDefinition(ENV_ENUM.MAJOR_PLAYER_SHUFFLE_HANDLER): (
        BattleEventEndRound(callback=SelfCallback('handleRevivedDancePartners')),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_SIPHON): (
        BattleEvent(
            name='siphon_heal',
            listensTo=BEG.EVENT_SUIT_DAMAGE,
            callback=SelfCallback('onSuitAttack', EventArg.ONE, EventArg.TWO),
        ),
    ),

    # Witch Hunter
    # - Every 2 rounds, starting on the first round, bewitch a random Toon.
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_WITCH_HUNTER): (
        BattleEvent(
            'witch_hunter_cheat_handler',
            listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
            callback=(
                SelfCallback('fireGates'),
                SelfCallback('handleCheats'),
            )
        ),
        BattleEvent(
            'witch_hunter_bewitchment',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('handleBewitchment'),
            conditional=ConditionalRoundCycle(2, 1),
        ),
        BattleEvent(
            'witch_hunter_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('weDied'),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO),
        ),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_WILL_OF_THE_PEOPLE): (
        BattleEvent(
            'will_of_the_people_decrease',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('handleSuitDied')
        ),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_TRIAL_BY_FIRE): (
        BattleEventNormalAttacksOver(
            'trial_by_fire_dot', callback=SelfCallback('applyDamage'),
        ),
        BattleEvent(
            'trial_by_fire_soaked',
            listensTo=(BEG.EVENT_SOAKED_SUIT, BEG.EVENT_RESOAKED_SUIT),
            callback=SelfCallback('handleSoaked'),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO)
        ),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_HIVEMIND): (
        BattleEvent(
            'hivemind_attacks',
            listensTo=(BEG.EVENT_BEGIN_SUIT_ATTACKS, BEG.EVENT_TOON_DIED),
            callback=SelfCallback('retargetSuitAttacks'),
        ),
    ),

    # Plutocrat
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_PLUTOCRAT): (
        BattleEvent(
            'plutocrat_test_hp_gates',
            listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
            callback=SelfCallback('fireGates'),
        ),
        BattleEvent(
            'plutocrat_slush_fund',
            listensTo=BEG.EVENT_ATTACK_ORDER,
            callback=(SelfCallback('handleSlushFund'), SelfCallback('handleSnowSquall')),
            conditional=ConditionalRoundCycle(3, 1),
        ),
        BattleEventEndRound(
            'instance_merc_natural_spawn_cogs',
            callback=SelfCallback('instanceNaturalSpawns'),
            conditional=ConditionalRoundCycle(2, 1),
        ),
        BattleEvent(
            'plutocrat_take_damage',
            listensTo=(BEG.EVENT_TOON_DAMAGE, BEG.EVENT_GENERAL_DAMAGE),
            callback=SelfCallback('handleReceivedDamage', EventArg.THREE),
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO)
        ),
        BattleEventEndRound('plutocrat_end_round', callback=SelfCallback('handleRoundEnded'))
    ),

    # Environmental module for plutocrat that handles when
    # he uses snow squall.
    EnvironmentalEventDefinition(ENV_ENUM.PLUTOCRAT_WEATHER): (
        BattleEvent(
            'plutocrat_env_weather_control',
            listensTo=BEG.EVENT_PCRAT_WEATHER,
            callback=SelfCallback('setWeather', EventArg.ZERO),
        ),
        BattleEvent(
            'plutocrat_env_hurt_toons',
            listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER,
            callback=SelfCallback('hurtToons'),
        ),
        BattleEvent(
            'plutocrat_freeze_suits',
            listensTo=BEG.EVENT_STATUS_EFFECT_CREATED,
            callback=SelfCallback('freezeSuit', EventArg.ZERO, EventArg.ONE),
            conditional=ConditionalMultipleValueEquality(
                EventArg.TWO, [SEE.EFFECT_SUIT_SOAKED, SEE.EFFECT_SUIT_DRENCHED]
            )
        ),
        BattleEvent(
            'plutocrat_env_suit_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('attemptShatter', EventArg.ZERO, EventArg.TWO),
        )
    ),

    # Battle calc module definition for plutocrat that handles investors dying,
    # allowing him to say phrases when they die and hes not technically
    # in the battle yet.
    BattleObjectEventDefinition("DistributedBattlePlutocratAI"): (
        BattleEvent(
            "plutocrat_bc_suit_died",
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('suitDied', EventArg.ZERO),
        ),
        BattleEvent(
            "plutocrat_bc_track_over",
            listensTo=BEG.EVENT_END_TOON_TRACK,
            callback=SelfCallback('trackOver')
        ),
        BattleEvent(
            "plutocrat_bc_round_over",
            listensTo=BEG.EVENT_END_ROUND,
            callback=SelfCallback('clearSuitsDied')
        )
    ),

    # Battle object definition for major player which handles when 
    # the rhythm game occurs.
    BattleObjectEventDefinition("DistributedBattleMajorPlayerAI"): (
        BattleEvent(
            'major_player_trigger_rhythm',
            listensTo=BEG.EVENT_MPLAYER_HWA,
            callback=SelfCallback('queueRhythmGame'),
        )
    ),

    BattleObjectEventDefinition("DistributedBattleChainsawAI"): (
        BattleEvent(
            "chainsaw_remove_toon",
            listensTo=BEG.EVENT_TOON_LEFT,
            callback=SelfCallback("toonLeftBattle", EventArg.ZERO),
        ),
    ),

    StatusEffectEventDefinition(SEE.EFFECT_SATELLITE_INVESTOR_MANAGER): (
        BattleEvent(
            'satellite_investors_manager_update_st_members',
            listensTo=(BEG.EVENT_BEGIN_ROUND, BEG.EVENT_SUIT_DIED),
            callback=SelfCallback('updateInvestorMembers'),
        ),
        BattleEvent(
            'satellite_investors_manager_suit_died',
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=SelfCallback('suitDied', EventArg.ZERO),
            conditional=ConditionalReferenceInequality(AvatarGetterCallback(), EventArg.ZERO),
        ),
    ),

    # Charon
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_CHARON): BattleEvent(
        'charon_begin_round',
        listensTo=BEG.EVENT_ATTACK_ORDER,
        callback=SelfCallback('handleBeginRound'),
    ),

    # Nix
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_NIX): BattleEvent(
        'nix_begin_round',
        listensTo=BEG.EVENT_ATTACK_ORDER,
        callback=SelfCallback('handleBeginRound'),
    ),

    # Hydra
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_HYDRA): BattleEvent(
        'hydra_kick_up',
        listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
        callback=SelfCallback('handleKickUp'),
    ),

    # Styx
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_STYX): (
        BattleEventNormalAttacksOver(
            'styx_sitdown',
            callback=SelfCallback('handleSitdown'),
            conditional=ConditionalRoundCycle(4, 1),
        ),
        BattleEventNormalAttacksOver(
            'styx_usury',
            callback=SelfCallback('handleUsury')
        ),
    ),

    # Kerberos
    StatusEffectEventDefinition(SEE.EFFECT_MANAGER_KERBEROS): BattleEvent(
        'kerberos_tribute',
        listensTo=BEG.EVENT_BEGIN_SUIT_ATTACKS,
        callback=SelfCallback('handleTribute'),
        conditional=ConditionalRoundCycle(2, 1),
    ),
})
