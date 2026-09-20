"""Contains a mapping of every attack enum to a respective attack object."""
from typing import Dict, Union


from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.client.Attack import Attack


AttackRepository = {}  # type: Dict[AttackEnum, Attack]


class AttackClass:
    """AttackClass: Decorator class used for the sole purpose of
    populating the AttackRepository global object with attack
    movie objects.

    :param attackType: The AttackEnum value which to attach the
    desired class to. This can also be a tuple of multiple
    AttackEnum values.
    """

    __slots__ = ("attackType",)

    def __init__(self, attackType: Union[AttackEnum, tuple]):
        # Ensure that this is a tuple.
        if not isinstance(attackType, tuple):
            attackType = (attackType,)

        self.attackType = attackType  # type: tuple[AttackEnum]

    def __call__(self, cls):
        # Populate the repository with each type.
        for attackType in self.attackType:
            AttackRepository[attackType] = cls
        return cls
