"""
A list of the passive effects a given suit can have associated with it.
"""

LURE_RESISTANCE = 'LURE_RESISTANCE'                 # Use lure immune enum for no lure, 0 for lured this round, 1+ for actual round caps
COMBO_EFFECTIVENESS = 'COMBO_EFFECTIVENESS'         # Mult 0 to 1
KNOCKBACK_EFFECTIVENESS = 'KNOCKBACK_EFFECTIVENESS' # Mult 0 to 1
FORCED_DEFENSE = 'FORCED_DEFENSE'                   # Flat number of defense that will be set on the suit no matter what
HP_BOOST = 'HP_BOOST'                               # Flat number hp boost per suit, after all other calculations are done
HP_MULT = 'HP_MULT'                                 # Hp multiplier done after all other calculations are done (hpBoost comes after this)
DEFENSE_BOOST = 'DEFENSE_BOOST'                     # Flat defense boost per suit
STATUS_EFFECTS = 'STATUS_EFFECTS'                   # Defines what status effects they spawn with
ATTACKS_FIRST = 'ATTACKS_FIRST'                     # Whether or not this Suit should attack before Toons do.
