from toontown.utils.AstronStruct import AstronStruct


class AttackTarget(AstronStruct):
    '''
    AttackTarget: Dataclass for all information pertaining to
    what the attack did to the target.
    '''

    __slots__ = ('avId', 'landed', 'hpAdjust', 'died', 'revived', 'hpBonus', 'kbBonus', 'extraArgs')

    def __init__(self, avId: int, landed: bool = False, hpAdjust: int = 0, died: bool = False, revived: bool = False, hpBonus: int = 0, kbBonus: int = 0, extraArgs: list = []) -> None:
        '''
        Parameters:
            avId (int): The doId of the target.
            landed (bool): If the target was inflicted by the attack.
            hpAdjust (int): How much to adjust the target's HP value by.
             (positive or negative change)
            died (bool): If the attack killed the target.
            revived (bool): If the attack forced the target to revive.
            hpBonus (int): Combination damage bonus. (toon attack specific)
            kbBonus (int): Knockback damage bonus. (toon attack specific)
            extraArgs (list): Extra arguments.
        '''
        self.avId: int = avId
        self.landed: bool = landed
        self.hpAdjust: int = hpAdjust
        self.died: bool = died
        self.revived: bool = revived
        self.hpBonus: int = hpBonus
        self.kbBonus: int = kbBonus
        self.extraArgs: list = extraArgs


    def __repr__(self) -> str:
        return f'AttackTarget({self.toStruct()})'


    def toStruct(self) -> list:
        return [self.avId, self.landed, self.hpAdjust, self.died, self.revived, self.hpBonus, self.kbBonus, self.extraArgs]
