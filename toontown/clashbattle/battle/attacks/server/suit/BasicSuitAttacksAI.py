import random

from toontown.battle.BattleEventGlobals import BEG
from toontown.battle.BattleAvatar import BattleAvatar
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.attacks.server.AttackAI import AttackAI
from toontown.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.battle.attacks.server.suit.SuitGroupAttackAI import SuitGroupAttackAI
from toontown.battle.statuses.StatusEffectEnums import SEE
from toontown.battle.statuses import StatusEffectGlobals as SEG


@AttackClassAI(attackType=AttackEnum.AFTERSHOCK)
class AftershockAI(SuitGroupAttackAI):
    DAMAGE_RANGE = (0.7, 1.3)
