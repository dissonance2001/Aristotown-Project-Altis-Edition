'''
Contains a mapping of every attack enum to a respective environmental object.
'''

from toontown.battle.environmental.base.EnvironmentalEnum import EnvironmentalEnum


EnvironmentalRepository: dict[EnvironmentalEnum] = {}


def createEnvironmental(environmentalType: EnvironmentalEnum, battle, battleListener, **kwargs):
    '''
    Finds the environmental object attached to the environmental enum, then creates and returns that object, supplying any arguments.
    '''
    if environmentalType not in EnvironmentalRepository:
        raise NotImplementedError(
            f'No environmental object exists for environmental enum: {repr(environmentalType)}.')
    kwargs.update({
        'battle': battle,
        'battleListener': battleListener
    })
    return EnvironmentalRepository[environmentalType](**kwargs)


class EnvironmentalClass:
    '''
    EnvironmentalClass: Decorator class used for the sole purpose of
    populating the EnvironmentalRepository global object with environmental objects.
    '''

    __slots__ = ('environmentalType',)

    def __init__(self, *environmentalType: EnvironmentalEnum) -> None:
        '''
        Parameters:
            environmentalType: The EnvironmentalEnum value which to attach the desired class to. This can also be a tuple of multiple EnvironmentalEnum values.
        '''
        self.environmentalType = environmentalType

    def __call__(self, cls):
        for environmentalType in self.environmentalType:
            EnvironmentalRepository[environmentalType] = cls
        cls.environmentalType = self.environmentalType
        return cls
