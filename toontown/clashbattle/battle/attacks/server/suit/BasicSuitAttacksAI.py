import random

from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.server.AttackAI import AttackAI
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.clashbattle.battle.attacks.server.suit.SuitGroupAttackAI import SuitGroupAttackAI
from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG


@AttackClassAI(attackType=AttackEnum.AFTERSHOCK)
class AftershockAI(SuitGroupAttackAI):
    DAMAGE_RANGE = (0.7, 1.3)
