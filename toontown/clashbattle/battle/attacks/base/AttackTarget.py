from toontown.utils.AstronStruct import AstronStruct


class AttackTarget(AstronStruct):
    """
    AttackTarget: Dataclass for all information pertaining to
    what the attack did to the target.

    :param avId: The doId of the target.
    :param landed: If the target was inflicted by the attack.
    :param hpAdjust: How much to adjust the target's HP value by.
    (positive or negative change)
    :param died: If the attack killed the target.
    :param revived: If the attack forced the target to revive.
    :param hpBonus (toon attack specific): Combination damage bonus.
    :param kbBonus (toon attack specific): Knockback damage bonus.
    :param extraArgs: Extra arguments.
    """

    __slots__ = (
        "avId", "landed", "hpAdjust", "died", "revived", "hpBonus", "kbBonus",
        "extraArgs",
    )

    def __init__(self, avId: int, landed: bool=False, hpAdjust: int=0, 
                 died: bool=False, revived: bool=False, hpBonus: int=0, 
                 kbBonus: int=0, extraArgs: list=None) -> None:
        self.avId = avId
        self.landed = landed
        self.hpAdjust = hpAdjust
        self.died = died
        self.revived = revived
        self.hpBonus = hpBonus
        self.kbBonus = kbBonus
        self.extraArgs = extraArgs or []
    
    def __repr__(self) -> str:
        return f"AttackTarget({self.toStruct()})"
    
    def toStruct(self) -> list:
        return [
            self.avId, self.landed, self.hpAdjust, self.died, self.revived, 
            self.hpBonus, self.kbBonus, self.extraArgs,
        ]
