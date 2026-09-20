from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from panda3d.core import *
from typing import Dict, List, Union, Type
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class SpecialQuestModelBase(DirectObject):
    """
    A generic SpecialQuestModel.
    These classes allow standard NodePaths to have custom functionality
    in lieu of needing to make absolutely everything an actor.
    """

    def __init__(self, modelPath) -> None:
        self.modelPath = modelPath
        self.model = self.loadModel()

    def loadModel(self) -> NodePath:
        return loader.loadModel(self.modelPath)

    def cleanup(self) -> None:
        if self.model:
            self.model.removeNode()
            self.model = None

    def reparentTo(self, *args, **kwargs):
        if self.model:
            self.model.reparentTo(*args, **kwargs)

    def wrtReparentTo(self, *args, **kwargs):
        if self.model:
            self.model.wrtReparentTo(*args, **kwargs)

    # Actor interface filler

    def play(self, *args, **kwargs):
        return

    def loop(self, *args, **kwargs):
        return

    def pose(self, *args, **kwargs):
        return

    def stop(self, *args, **kwargs):
        return

    # Custom stuff for special models

    def getAnim(self, *args) -> MetaInterval:
        # The actual thing that will be used if a special anim is to play
        return Sequence()

    def setSpecial(self, *args) -> None:
        # The actual thing that will be used if a special mode is to be set
        return


SpecialModelRegistry: Dict[str, Type[SpecialQuestModelBase]] = {}


@DirectNotifyCategory()
class SpecialModel:
    """SpecialModel: Decorator class used for the sole purpose of
    populating the SpecialModelRegistry global object with model
    objects.

    :param specialKey: The str value which to attach the
    desired class to. This can also be a tuple of multiple
    str values.
    """

    __slots__ = ("specialKey",)

    def __init__(self, specialKey: Union[str, tuple]) -> None:
        # Ensure that this is a tuple.
        if not isinstance(specialKey, tuple):
            specialKey = (specialKey,)

        self.specialKey = specialKey  # type: tuple[str]

    def __call__(self, cls):
        self.notify.debug(f"Registering key: {repr(self.specialKey)}")
        # Populate the repository with each type.
        for specialKey in self.specialKey:
            SpecialModelRegistry[specialKey] = cls
        return cls


@SpecialModel('phase_9/models/cogHQ/woodCrateB.bam')
class SpecialQuestModel(SpecialQuestModelBase):
    """
    Generic, has nothing special but used to define models that should work w/ animated quest entities.
    """
    pass


@SpecialModel('phase_6/models/modules/ttcc_bb_street_gatePier')
class RainmakerGateModel(SpecialQuestModelBase):
    def __init__(self, modelPath) -> None:
        super().__init__(modelPath)
        self.leftGate = self.model.find('**/gate_door_left')
        self.rightGate = self.model.find('**/gate_door_right')
        self.leftShadow = self.model.find('**/gate_shadow_left')
        self.rightShadow = self.model.find('**/gate_shadow_right')
        self.doorSfx = loader.loadSfx('phase_11/audio/sfx/LB_door_moves.ogg')

    def getAnim(self, *args) -> MetaInterval:
        if args[0] == 'open':
            seq = Sequence(Parallel(
                Func(base.playSfx, self.doorSfx, node=self.rightGate),
                LerpHprInterval(self.leftGate, 3.0, (92, 0, 0), blendType='easeInOut'),
                LerpHprInterval(self.rightGate, 3.0, (-92, 0, 0), blendType='easeInOut'),
                LerpHprInterval(self.leftShadow, 3.0, (92, 0, 0), blendType='easeInOut'),
                LerpHprInterval(self.rightShadow, 3.0, (-92, 0, 0), blendType='easeInOut'),
            ))
            return seq
        elif args[0] == 'close':
            seq = Sequence(Parallel(
                Sequence(
                    Wait(0.5),
                    Func(base.playSfx, self.doorSfx, node=self.rightGate),
                ),
                LerpHprInterval(self.leftGate, 3.0, (0, 0, 0), blendType='easeInOut'),
                LerpHprInterval(self.rightGate, 3.0, (0, 0, 0), blendType='easeInOut'),
                LerpHprInterval(self.leftShadow, 3.0, (0, 0, 0), blendType='easeInOut'),
                LerpHprInterval(self.rightShadow, 3.0, (0, 0, 0), blendType='easeInOut'),
            ))
            return seq
        else:
            return Sequence()

    def setSpecial(self, *args) -> None:
        if args[0] == 'open':
            [obj.setHpr(92, 0, 0) for obj in (self.leftGate, self.leftShadow)]
            [obj.setHpr(-92, 0, 0) for obj in (self.rightGate, self.rightShadow)]
        elif args[0] == 'close':
            [obj.setHpr(0, 0, 0) for obj in (self.leftGate, self.rightGate, self.leftShadow, self.rightShadow)]

    def cleanup(self) -> None:
        super().cleanup()
        self.leftGate = None
        self.rightGate = None
        self.leftShadow = None
        self.rightShadow = None
        self.doorSfx.stop()
        self.doorSfx = None
