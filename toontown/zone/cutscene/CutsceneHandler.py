from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import Sequence, Func
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from typing import List, Union
from toontown.zone.cutscene.CutsceneData import CutsceneBase, LevelCutsceneKey, LevelCutsceneRegistry


@DirectNotifyCategory(debug=True)
class CutsceneHandler(DirectObject):
    """
    A container that handles cutscenes that need to play, and plays them in order.
    """
    CheckTaskName = 'CutsceneHandler-cutsceneTask'

    def __init__(self) -> None:
        self.__cutsceneQueue: List[CutsceneBase] = []
        self.__cutsceneTaskActive = False

    @property
    def inactiveCutsceneQueue(self) -> List[CutsceneBase]:
        return [cutscene for cutscene in self.__cutsceneQueue if not cutscene.isActive]

    @property
    def blockingCutsceneActive(self) -> bool:
        for cutscene in self.__cutsceneQueue:
            if cutscene.Blocking and cutscene.isActive:
                return True

        return False

    def addCutscene(self, cutsceneKey: LevelCutsceneKey, objects: Union[List, None] = None, args: Union[List, None] = None) -> None:
        self.notify.debug(f'addCutscene(): cutsceneKey {cutsceneKey}, objects {objects}, args {args}')
        if cutsceneKey not in LevelCutsceneRegistry:
            self.notify.warning(f'addCutscene(): Ignoring invalid cutscene key ({cutsceneKey})')
            return

        objects = objects or []
        args = args or []
        cutsceneObj = LevelCutsceneRegistry[cutsceneKey](cutsceneHandler=self, objects=objects, args=args)
        self.__cutsceneQueue.append(cutsceneObj)

        if not self.__cutsceneTaskActive:
            self.__cutsceneTaskActive = True
            self.addTask(self.__cutsceneTask, name=self.CheckTaskName)

    def __removeCutscene(self, cutscene: CutsceneBase):
        if cutscene in self.__cutsceneQueue:
            self.__cutsceneQueue.remove(cutscene)

        if not len(self.__cutsceneQueue):
            # We're out of cutscenes, we can stop the task checking for them.
            self.__cutsceneTaskActive = False
            self.removeTask(self.CheckTaskName)

    def __cutsceneTask(self, task=None):
        task.delayTime = 0.1

        for cutscene in self.inactiveCutsceneQueue:
            if cutscene.Blocking:
                if self.blockingCutsceneActive:
                    # Ignore blocking cutscenes if we already have a blocker active
                    continue

                # Do a series of checks for blocking cutscenes, as they will control the game environment.
                if not base.localAvatar:
                    continue
                place = base.localAvatar.getPlace()
                if not place:
                    continue
                state = place.getState()
                if state != 'walk':
                    continue

            # Play the cutscene
            # Once it is done, it'll automatically remove itself from the queue.
            cutscene.playCutscene()

        return task.again

    def officializeCutscene(self, cutscene: CutsceneBase):
        return Sequence(
            cutscene.buildCutscene(),
            Func(self.__removeCutscene, cutscene),
            Func(cutscene.cutsceneFinished),
        )

    def cleanup(self):
        for cutscene in self.__cutsceneQueue:
            cutscene.cleanup()
        self.__cutsceneQueue = []
        self.removeAllTasks()
        self.ignoreAll()

    def __str__(self):
        return f'{self.__class__.__name__}: Queue({self.__cutsceneQueue})'
