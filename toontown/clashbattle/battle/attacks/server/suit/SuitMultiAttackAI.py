from toontown.clashbattle.battle.attacks.server.suit.SuitSingleAttackAI import SuitSingleAttackAI


class SuitMultiAttackAI(SuitSingleAttackAI):
    """SuitMultiAttackAI: Extends SuitSingleAttackAI with functionality
    for multi (not completely group) attacks.
    """
    RequestedTargetNum = 1

    def chooseRandomToon(self, amount: int = 1, biased: bool = True) -> list:
        return super().chooseRandomToon(amount=self.RequestedTargetNum, biased=biased)


class SuitDoubleAttackAI(SuitMultiAttackAI):
    """
    SuitMultiAttack that attacks 2 toons
    """
    RequestedTargetNum = 2


class SuitTripleAttackAI(SuitMultiAttackAI):
    """
    SuitMultiAttack that attacks 3 toons
    """
    RequestedTargetNum = 3
