#safe-ty supervisor cheats
'SafetyHighPressure': ('falling-knife', ATK_TGT_GROUP),
'SafetyHeatWave': ('magic3-alt', ATK_TGT_GROUP),
'SafetyHeatWaveCalculation': ('soak', ATK_TGT_SINGLE),
'SafetyViolation': ('snap', ATK_TGT_GROUP),
'SafetyPromotion': ('mob-mentality', ATK_TGT_SINGLE),
#union buster cheats
'UnionBusterUnionDues': ('magic3', ATK_TGT_GROUP),
'UnionBusterUnionCalculator': ('calculator', ATK_TGT_SINGLE),
'UnionBusterUnionBust': ('quick-jump', ATK_TGT_SINGLE),
'UnionBusterUnionBuster': ('summon', ATK_TGT_SINGLE),
'UnionBusterUnionBusterDamage': ('nothing', ATK_TGT_GROUP),
'UnionBusterUnionWages': ('calculating-costs', ATK_TGT_SINGLE),
'UnionBusterBreachOfContract': ('sanction', ATK_TGT_SINGLE),
'UnionBusterBreachOfContract2': ('sanction', ATK_TGT_GROUP),
'UnionBusterBreachOfContract3': ('sanction', ATK_TGT_GROUP),
'UnionBusterBreachOfContract4': ('sanction', ATK_TGT_GROUP),
'UnionBusterContractEnforcement': ('throw-paper', ATK_TGT_SINGLE),
#racketeer cheats
'RacketeerProfiteering': ('come-on', ATK_TGT_SINGLE),
'RacketeerExtortion': ('magic3', ATK_TGT_GROUP),
'RacketeerExtortion2': ('magic3', ATK_TGT_GROUP),
'RacketeerCompensation': ('rush-job', ATK_TGT_SINGLE),
'RacketeerHustling': ('come-on', ATK_TGT_GROUP),
'RacketeerRacketeering': ('objection', ATK_TGT_SINGLE),
'RacketeerPeckingOrderRetaliation': ('throw-object', ATK_TGT_GROUP),
#radiographer cheats
'RadiographerRadioInfrequency': ('nothing', ATK_TGT_GROUP),
'RadiographerHotTake': ('sanction', ATK_TGT_SINGLE),
'RadiographerHotTakeRetaliation': ('sanction', ATK_TGT_SINGLE),
'RadiographerOvermodulated': ('sanction', ATK_TGT_SINGLE),
#safe-ty supervisor cheats
SAFETY_HIGH_PRESSURE = SuitAttacks.keys().index('SafetyHighPressure')
SAFETY_HEAT_WAVE = SuitAttacks.keys().index('SafetyHeatWave')
SAFETY_HEAT_WAVE_CALCULATION = SuitAttacks.keys().index('SafetyHeatWaveCalculation')
SAFETY_VIOLATION = SuitAttacks.keys().index('SafetyViolation')
SAFETY_PROMOTION = SuitAttacks.keys().index('SafetyPromotion')
#union buster cheats
UNION_BUSTER_UNION_DUES = SuitAttacks.keys().index('UnionBusterUnionDues')
UNION_BUSTER_UNION_CALCULATOR = SuitAttacks.keys().index('UnionBusterUnionCalculator')
UNION_BUSTER_UNION_BUST = SuitAttacks.keys().index('UnionBusterUnionBust')
UNION_BUSTER_UNION_BUSTER = SuitAttacks.keys().index('UnionBusterUnionBuster')
UNION_BUSTER_UNION_BUSTER_DAMAGE = SuitAttacks.keys().index('UnionBusterUnionBusterDamage')
UNION_BUSTER_UNION_WAGES = SuitAttacks.keys().index('UnionBusterUnionWages')
UNION_BUSTER_BREACH_OF_CONTRACT = SuitAttacks.keys().index('UnionBusterBreachOfContract')
UNION_BUSTER_BREACH_OF_CONTRACT_2 = SuitAttacks.keys().index('UnionBusterBreachOfContract2')
UNION_BUSTER_BREACH_OF_CONTRACT_3 = SuitAttacks.keys().index('UnionBusterBreachOfContract3')
UNION_BUSTER_BREACH_OF_CONTRACT_4 = SuitAttacks.keys().index('UnionBusterBreachOfContract4')
UNION_BUSTER_CONTRACT_ENFORCEMENT = SuitAttacks.keys().index('UnionBusterContractEnforcement')
#racketeer cheats
RACKETEER_PROFITEERING = SuitAttacks.keys().index('RacketeerProfiteering')
RACKETEER_EXTORTION = SuitAttacks.keys().index('RacketeerExtortion')
RACKETEER_COMPENSATION = SuitAttacks.keys().index('RacketeerCompensation')
RACKETEER_HUSTLING = SuitAttacks.keys().index('RacketeerHustling')
RACKETEER_EXTORTION_2 = SuitAttacks.keys().index('RacketeerExtortion2')
RACKETEER_RACKETEERING = SuitAttacks.keys().index('RacketeerRacketeering')
RACKETEER_PECKING_ORDER_RETALIATION = SuitAttacks.keys().index('RacketeerPeckingOrderRetaliation')
#radiographer cheats
RADIOGRAPHER_RADIO_INFREQUENCY = SuitAttacks.keys().index('RadiographerRadioInfrequency')
RADIOGRAPHER_HOT_TAKE = SuitAttacks.keys().index('RadiographerHotTake')
RADIOGRAPHER_HOT_TAKE_RETALIATION = SuitAttacks.keys().index('RadiographerHotTakeRetaliation')
RADIOGRAPHER_OVERMODULATED = SuitAttacks.keys().index('RadiographerOvermodulated')

for t in self.battle.activeToons:
    if t in do.involvedToons:
        if len(self.battle.activeSuits) < 6:
            boss.appendSuitsToBattle(boss.battleNumber, 'lit')