"""Contains a mapping of every attack enum to a respective attack object."""

from typing import Dict, Union
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.attacks.server.AttackAI import AttackAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


AttackRepository = {}  # type: Dict[AttackEnum, AttackAI]


def createAttack(attackType: AttackEnum, *args, **kwargs):
    """Finds the attack object attached to the attack enum,
    then creates and returns that object, supplying any arguments.
    """
    if attackType not in AttackRepository:
        raise NotImplementedError(f"No attack object exists for attack enum: {repr(attackType)}.")
    
    return AttackRepository[attackType](attackType, *args, **kwargs)


@DirectNotifyCategory()
class AttackClassAI:
    """AttackClassAI: Decorator class used for the sole purpose of
    populating the AttackRepository global object with attack
    movie objects.

    :param attackType: The AttackEnum value which to attach the
    desired class to. This can also be a tuple of multiple
    AttackEnum values.
    """

    __slots__ = ("attackType",)

    def __init__(self, attackType: Union[AttackEnum, tuple]) -> None:
        # Ensure that this is a tuple.
        if not isinstance(attackType, tuple):
            attackType = (attackType,)

        self.attackType = attackType # type: tuple[AttackEnum]

    def __call__(self, cls):
        self.notify.debug(f"Registering type: {repr(self.attackType)}")
        # Populate the repository with each type.
        for attackType in self.attackType:
            AttackRepository[attackType] = cls
        return cls
