from toontown.clashbattle.battle.attacks.server.suit.SuitSingleAttackAI import SuitSingleAttackAI


class SuitGroupAttackAI(SuitSingleAttackAI):
    """SuitGroupAttackAI: Extends SuitSingleAttackAI with functionality
    for group target suit attacks.
    """

    def setTargetList(self) -> None:
        if not self.targets or len(self.targets) < len(self.toons):
            self.targets = self.getToons()
