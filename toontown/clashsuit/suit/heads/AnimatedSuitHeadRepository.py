"""Contains a mapping of suit names to a respective animated suit head class."""
from typing import Dict, Union
from toontown.clashsuit.suit.heads.AnimatedSuitHead import AnimatedSuitHead

AnimatedSuitHeadRepository = {}  # type: Dict[str, AnimatedSuitHead]


def getAnimatedSuitHead(suitName: str):
    """Finds the head object attached to the suit name,
    then creates and returns that object.
    """
    if suitName not in AnimatedSuitHeadRepository:
        return AnimatedSuitHead

    return AnimatedSuitHeadRepository[suitName]


class AnimatedSuitHeadClass:
    """AnimatedSuitHeadClass: Decorator class used to register custom AnimatedSuitHeads.

    :param suitName: The suit name which to attach the
    desired class to. This can also be a tuple of multiple
    suit names.
    """

    __slots__ = ("suitName",)

    def __init__(self, suitName: Union[str, tuple]):
        # Ensure that this is a tuple.
        if not isinstance(suitName, tuple):
            suitName = (suitName,)

        self.suitName = suitName  # type: tuple[str]

    def __call__(self, cls):
        # Populate the repository with each type.
        for suitName in self.suitName:
            AnimatedSuitHeadRepository[suitName] = cls
        return cls
