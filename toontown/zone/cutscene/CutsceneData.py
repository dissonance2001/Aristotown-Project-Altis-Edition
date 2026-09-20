from strenum import StrEnum
from typing import Dict, List, Union, Type
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class CutsceneBase:
    """
    The base cutscene object that is used via the CutsceneHandler.
    """

    # If the cutscene should lock down the Toon and take control over their camera
    # Only one of these types of cutscenes can be active at a time
    Blocking = False
    # If the cutscene should notify its objects that it has finished
    SendFinishCutsceneFunc = False

    def __init__(self, cutsceneHandler, objects: List, args: Union[Dict, None] = None) -> None:
        self.cutsceneHandler = cutsceneHandler
        self.objects: List = objects
        self.args: Dict = args if args else dict()
        self.seq: Union[Sequence, None] = None
        self.prevCamData: List = []

    def buildCutscene(self) -> MetaInterval:
        raise NotImplementedError(f"{self.__class__.__name__}.buildCutscene() is not defined.")

    def playCutscene(self) -> None:
        self.seq = self.cutsceneHandler.officializeCutscene(self)

        if self.seq:
            self.seq.start()

    def cutsceneFinished(self) -> None:
        if self.SendFinishCutsceneFunc:
            for obj in self.objects:
                if hasattr(obj, 'cutscene_onFinish'):
                    obj.cutscene_onFinish()

        # May want custom behavior here.
        self.cleanup()

    @property
    def isActive(self):
        return self.seq and self.seq.isPlaying()

    def cleanup(self) -> None:
        if self.seq:
            self.seq.finish()
            self.seq = None

        self.cutsceneHandler = None
        self.objects = []
        self.args = {}
        self.prevCamData = []

    # region Util Stuff

    def lockToon(self):
        place = base.cr.playGame.getPlace()
        place.setState('Stopped')

        self.prevCamData = [camera.getParent(), camera.getPos(), camera.getHpr()]

        base.localAvatar.cameraFSM.request('Off')
        base.camera.wrtReparentTo(render)

    def unlockToon(self):
        place = base.cr.playGame.getPlace()
        place.setState('walk')

        base.localAvatar.cameraFSM.request('Orbit')

    def setCamToPrevious(self):
        base.camera.reparentTo(self.prevCamData[0])
        base.camera.setPosHpr(*self.prevCamData[1], *self.prevCamData[2])

    # endregion

    # region Common Sequences

    def getIrisTrack(self, outTime=0.8, outFunc=None, waitDuration=1.0, inTime=0.8, inFunc=None):
        return Sequence(
            Func(base.transitions.fadeOut, outTime),
            Wait(outTime + 0.01),
            Func(outFunc) if outFunc else Sequence(),
            Wait(waitDuration),
            Func(base.transitions.fadeIn, inTime),
            Wait(inTime + 0.01),
            Func(inFunc) if inFunc else Sequence(),
        )

    def getPanTrack(self, pos, hpr, duration=2.0, other=None, blendType='noBlend'):
        return Sequence(
            LerpPosHprInterval(camera, duration, pos, hpr, other=other, blendType=blendType)
        )

    # endregion

    # region Generic getters

    @property
    def sfxToPlay(self):
        return self.args.get('sfx', '')

    @property
    def sfxVolume(self):
        return self.args.get('sfxVolume', 1.0)

    @property
    def animToPlay(self):
        return self.args.get('anim', '')

    @property
    def extraWaitTime(self):
        return self.args.get('extraWaitTime', 0.0)

    @property
    def specialAnim(self):
        return self.args.get('specialAnim', '')

    @property
    def specialState(self):
        return self.args.get('specialState', '')

    @property
    def camPosHpr(self):
        return self.args.get('camPosHpr', [7, 25, 12, 0, 0, 0])

    # endregion


class LevelCutsceneKey(StrEnum):
    # Basic hide/show
    Show = 'show'
    Hide = 'hide'
    # Basic anim
    PlayAnim = 'play_anim'
    # Set/play special stuff for SpecialQuestModel
    SpecialAnim = 'special_anim'
    SetSpecial = 'set_special'
    # Hide/show with an Iris
    IrisShow = 'iris_show'
    IrisHide = 'iris_hide'
    # Play an anim with an iris, and either hide after the anim is done or show before the anim starts
    IrisShowPlayAnim = 'iris_show_play_anim'
    IrisHidePlayAnim = 'iris_hide_play_anim'
    # Pan, then play a SpecialQuestModel animation.
    PanSpecialModelAnim = 'pan_special_model_anim'


LevelCutsceneRegistry: Dict[LevelCutsceneKey, Type[CutsceneBase]] = {}


@DirectNotifyCategory()
class LevelCutscene:
    """LevelCutscene: Decorator class used for the sole purpose of
    populating the LevelCutsceneRegistry global object with cutscene
    objects.

    :param cutsceneKey: The LevelCutsceneKey value which to attach the
    desired class to. This can also be a tuple of multiple
    LevelCutsceneKey values.
    """

    __slots__ = ("cutsceneKey",)

    def __init__(self, cutsceneKey: Union[LevelCutsceneKey, tuple]) -> None:
        # Ensure that this is a tuple.
        if not isinstance(cutsceneKey, tuple):
            cutsceneKey = (cutsceneKey,)

        self.cutsceneKey = cutsceneKey  # type: tuple[LevelCutsceneKey]

    def __call__(self, cls):
        self.notify.debug(f"Registering key: {repr(self.cutsceneKey)}")
        # Populate the repository with each type.
        for cutsceneKey in self.cutsceneKey:
            LevelCutsceneRegistry[cutsceneKey] = cls
        return cls


# region Cutscene Classes

@LevelCutscene(LevelCutsceneKey.Show)
class ShowCutscene(CutsceneBase):
    def buildCutscene(self) -> MetaInterval:
        if not len(self.objects):
            self.notify.warning('buildCutscene(): No objects to show!')
            return Sequence()
        return Sequence(*[Func(obj.unstash) for obj in self.objects])


@LevelCutscene(LevelCutsceneKey.Hide)
class HideCutscene(CutsceneBase):
    def buildCutscene(self) -> MetaInterval:
        if not len(self.objects):
            self.notify.warning('buildCutscene(): No objects to hide!')
            return Sequence()
        return Sequence(*[Func(obj.stash) for obj in self.objects])


@LevelCutscene(LevelCutsceneKey.PlayAnim)
class PlayAnimCutscene(CutsceneBase):
    def buildCutscene(self) -> MetaInterval:
        if not len(self.objects):
            self.notify.warning('buildCutscene(): No objects to play anims on!')
            return Sequence()
        return Sequence(Parallel(*[ActorInterval(self.objects[i], self.animToPlay) for i in range(len(self.objects))]))


@LevelCutscene(LevelCutsceneKey.SpecialAnim)
class SpecialAnimCutscene(CutsceneBase):
    def buildCutscene(self) -> MetaInterval:
        if not len(self.objects):
            self.notify.warning('buildCutscene(): No objects to play anims on!')
            return Sequence()
        return Sequence(
            Parallel(
                *[self.objects[i].getAnim(self.specialAnim) for i in range(len(self.objects))],
            ),
            Wait(self.extraWaitTime),
        )


@LevelCutscene(LevelCutsceneKey.SetSpecial)
class SetSpecialCutscene(CutsceneBase):
    def buildCutscene(self) -> MetaInterval:
        if not len(self.objects):
            self.notify.warning('buildCutscene(): No objects to play anims on!')
            return Sequence()
        return Sequence(
            Parallel(*[Func(self.objects[i].setSpecial, self.specialState) for i in range(len(self.objects))])
        )


class IrisCutsceneBase(CutsceneBase):
    Blocking = True

    def buildCutscene(self) -> MetaInterval:
        if not len(self.objects):
            self.notify.warning('buildCutscene(): No objects to show!')
            return Sequence()

        return Sequence(
            Func(self.lockToon),
            self.getIrisTrack(outFunc=self.positionCamera),
            Wait(0.25),
            Func(self.irisFunc),
            Wait(0.25 + self.extraWaitTime),
            self.getIrisTrack(outFunc=self.setCamToPrevious),
            Func(self.unlockToon),
        )

    def positionCamera(self):
        camPosHpr = [*[camPosVal / self.objects[0].getScale()[i] for i, camPosVal in enumerate(self.camPosHpr[:3])], *self.camPosHpr[3:]]
        base.camera.setPosHpr(self.objects[0], *camPosHpr)
        base.camera.lookAt(self.objects[0])

    def irisFunc(self) -> None:
        raise NotImplementedError(f"{self.__class__.__name__}.irisFunc() is not defined.")


@LevelCutscene(LevelCutsceneKey.IrisShow)
class IrisShowCutscene(IrisCutsceneBase):
    def irisFunc(self):
        [obj.unstash() for obj in self.objects]


@LevelCutscene(LevelCutsceneKey.IrisHide)
class IrisHideCutscene(IrisCutsceneBase):
    def irisFunc(self):
        [obj.stash() for obj in self.objects]


@LevelCutscene(LevelCutsceneKey.IrisShowPlayAnim)
class IrisShowPlayAnimCutscene(IrisCutsceneBase):
    SendFinishCutsceneFunc = True

    def irisFunc(self):
        [self.objects[i].play(self.animToPlay) for i in range(len(self.objects))]
        [obj.unstash() for obj in self.objects]
        if self.sfxToPlay:
            base.playSfx(loader.loadSfx(self.sfxToPlay), volume=self.sfxVolume)


@LevelCutscene(LevelCutsceneKey.IrisHidePlayAnim)
class IrisHidePlayAnimCutscene(IrisCutsceneBase):
    SendFinishCutsceneFunc = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.irisSeq = None

    def irisFunc(self):
        if self.sfxToPlay:
            sfxFunc = Func(base.playSfx, loader.loadSfx(self.sfxToPlay), volume=self.sfxVolume)
        else:
            sfxFunc = Sequence()

        self.irisSeq = Parallel(
            *[Sequence(
                Func(self.objects[i].play, self.animToPlay),
                sfxFunc,
                Wait(self.objects[i].getDuration(self.animToPlay)),
                Func(self.objects[i].stash)
            ) for i in range(len(self.objects))]
        )
        self.irisSeq.start()

    def cleanup(self) -> None:
        if self.irisSeq:
            self.irisSeq.finish()
            self.irisSeq = None
        super().cleanup()


class PanCutsceneBase(CutsceneBase):
    Blocking = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__panBackSeq = None

    @property
    def panDuration(self):
        return self.args.get('panDuration', 2.0)

    def buildCutscene(self) -> MetaInterval:
        if not len(self.objects):
            self.notify.warning('buildCutscene(): No objects to show!')
            return Sequence()

        finalCamPosHpr = self.getFinalCamPosHpr()

        def panBack():
            self.__panBackSeq = self.getPanTrack(Point3(*self.prevCamData[1]), Point3(*self.prevCamData[2]), duration=self.panDuration, other=self.prevCamData[0], blendType='easeInOut')
            self.__panBackSeq.start()

        return Sequence(
            Func(self.lockToon),
            self.getPanTrack(Point3(*finalCamPosHpr[:3]), Point3(*finalCamPosHpr[3:]), duration=self.panDuration, other=self.objects[0], blendType='easeInOut'),
            Wait(0.25),
            Func(self.panFunc),
            Wait(0.25 + self.extraWaitTime),
            Func(panBack),
            Wait(self.panDuration),
            Func(self.unlockToon),
        )

    def getFinalCamPosHpr(self):
        camPosHpr = [*[camPosVal / self.objects[0].getScale()[i] for i, camPosVal in enumerate(self.camPosHpr[:3])], *self.camPosHpr[3:]]
        return camPosHpr

    def panFunc(self) -> None:
        raise NotImplementedError(f"{self.__class__.__name__}.panFunc() is not defined.")

    def cleanup(self) -> None:
        if self.__panBackSeq:
            self.__panBackSeq.finish()
            self.__panBackSeq = None
        super().cleanup()


@LevelCutscene(LevelCutsceneKey.PanSpecialModelAnim)
class PanSpecialModelAnimCutscene(PanCutsceneBase):
    SendFinishCutsceneFunc = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.panSeq = None

    def panFunc(self):
        self.panSeq = self.objects[0].getAnim(self.specialAnim)
        self.panSeq.start()

    def cleanup(self) -> None:
        if self.panSeq:
            self.panSeq.finish()
            self.panSeq = None
        super().cleanup()

# endregion
